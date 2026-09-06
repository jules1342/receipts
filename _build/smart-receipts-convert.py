"""
One-off converter: Smart Receipts "report with images" zip  ->  a zip this app can Import.

Usage (from any folder):
    set ANTHROPIC_API_KEY=sk-ant-...        (PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-...")
    python smart-receipts-convert.py "C:\\path\\to\\report_images.zip" "C:\\path\\to\\output-folder"

Without a key it still runs, matching images to table rows by name and order, and leaves merchant blank.
With a key it reads every image with Claude (claude-opus-5), which fixes the ambiguous matches (Fuel, Gas, Water...)
by date and total, fills merchant and a concise item name, and prefers the invoice's own date and total when the
hand-typed row disagrees. Reads are cached in <output>/reads.json so a re-run costs nothing.

Output: <output>/smart-receipts-import.zip  (receipts.json + images/ in this app's format), plus report.md.
"""
import sys, os, re, json, zipfile, io, base64, time, collections, urllib.request, random, string
from datetime import datetime

try:
    import pypdf
except ImportError:
    sys.exit("pip install pypdf")
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

# ---- mapping agreed 2026-09-06 ----
CATEGORY_MAP = {
    'Electronics': ('Electronics', []),
    'Bills': ('Bills', []),
    'Vehicle': ('Vehicle', []),
    'Entertainment': ('Food and entertainment', []),
    'WorkExpenses': ('Work', ['Reimbursable']),
    'ProfessionalExpenses': ('Work', ['Reimbursable']),
    'OtherPurchasedItems': ('Other', []),
    'InvestmentHouse': ('Investment house', []),
    'Warranty': (None, ['Warranty']),   # category decided from the item, see guess_category
}
CATEGORIES = ['Electronics', 'Bills', 'Vehicle', 'Food and entertainment', 'Work', 'Other', 'Investment house']
TAGS = ['Warranty', 'Reimbursable']

MODEL = 'claude-opus-5'
API = 'https://api.anthropic.com/v1/messages'

def uid():
    return format(int(time.time() * 1000), 'x')[-8:] + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

def key(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def safe_name(t):
    return re.sub(r'\s+', ' ', re.sub(r'[\\/:*?"<>|\r\n]+', ' ', str(t or ''))).strip()[:40]

def page_file_name(r, idx, pid):
    parts = [r.get('date') or 'undated', safe_name(r.get('items')), safe_name(r.get('merchant'))]
    if r.get('total') not in (None, ''):
        parts.append('%.2f' % float(r['total']))
    return ' '.join(p for p in parts if p) + ' p%d [%s].jpg' % (idx + 1, pid)

# ---- 1. table rows from the PDF ----
def parse_rows(pdf_bytes):
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text = '\n'.join(p.extract_text() for p in reader.pages)
    lines = [l for l in text.split('\n') if l.strip()]
    pat = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.*)$')
    skip = ('Createdwith', 'Upgradeto', 'Date Name', 'SMARTRECEIPTS', 'Report', 'From:', 'Total', 'Grand')
    raw, buf = [], None
    for l in lines:
        m = pat.match(l)
        if m:
            if buf: raw.append(buf)
            buf = {'date': m.group(1), 'rest': m.group(2)}
        elif buf and not l.startswith(skip):
            buf['rest'] += ' ' + l
    if buf: raw.append(buf)
    rows = []
    for i, b in enumerate(raw):
        m = re.match(r'^(.*?)\s+(-?[\d,]+\.\d{2})\s+(-?[\d,]+\.\d{2})\s+([A-Z]{3})\s+(.*)$', b['rest'])
        if not m:
            print('UNPARSED ROW', b); continue
        cat = re.sub(r'[^A-Za-z]', '', m.group(5))
        cat = next((k for k in CATEGORY_MAP if cat.startswith(k)), cat)
        mm, dd, yy = b['date'].split('/')
        rows.append({'i': i, 'date': '%s-%s-%s' % (yy, mm, dd), 'name': m.group(1).strip(), 'price': float(m.group(2).replace(',', '')),
                     'tax': float(m.group(3).replace(',', '')), 'cur': m.group(4), 'cat': cat, 'key': key(m.group(1))})
    return rows

# ---- 2. Claude read of one image ----
READ_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'merchant': {'type': ['string', 'null']},
        'date': {'type': ['string', 'null'], 'description': 'YYYY-MM-DD, Australian receipts print day first'},
        'total': {'type': ['number', 'null']},
        'gst': {'type': ['number', 'null']},
        'item': {'type': 'string', 'description': 'Concise name for the purchase, 1 to 4 words'},
        'category': {'type': ['string', 'null']},
        'readable': {'type': 'boolean', 'description': 'false if the image is not a receipt or is unreadable'},
        'confidence': {'type': 'object', 'additionalProperties': False,
                       'properties': {'merchant': {'type': 'string', 'enum': ['high', 'low']}, 'date': {'type': 'string', 'enum': ['high', 'low']}, 'total': {'type': 'string', 'enum': ['high', 'low']}},
                       'required': ['merchant', 'date', 'total']}
    },
    'required': ['merchant', 'date', 'total', 'gst', 'item', 'category', 'readable', 'confidence']
}
STYLE = ("Name the purchase the way this person names things: short and plain, the thing itself, with the model when it is a durable good. "
         "Examples of their names: Fuel, Gas, Water, Electricity, Rates, Food, Stationary, Dog sitter, Car service, Tyres, Postage, "
         "Tab S6 lite, Phone - S22+, Laptop - Lenovo, Hisense split system, MX Keys keyboard, Kindle Paperwhite, Bag - Osprey, Couch, Work chair. "
         "One to four words. Do not list every line item.")

def read_image(api_key, jpg_bytes, hint):
    if Image is not None:
        im = Image.open(io.BytesIO(jpg_bytes)); im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((1568, 1568)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=85); jpg_bytes = buf.getvalue()
    body = {
        'model': MODEL, 'max_tokens': 2000,
        'output_config': {'effort': 'low', 'format': {'type': 'json_schema', 'schema': READ_SCHEMA}},
        'messages': [{'role': 'user', 'content': [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': base64.b64encode(jpg_bytes).decode()}},
            {'type': 'text', 'text': 'Read this receipt or invoice photographed in Australia. ' + STYLE +
             (' The owner labelled it "%s".' % hint if hint else '') +
             ' Allowed categories: ' + ', '.join(CATEGORIES) + '. Mark a field low confidence when faint, cut off or guessed; null when absent.'}
        ]}]
    }
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        'Content-Type': 'application/json', 'x-api-key': api_key, 'anthropic-version': '2023-06-01'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                j = json.load(r)
            text = ''.join(c.get('text', '') for c in j.get('content', []) if c.get('type') == 'text')
            return json.loads(text)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 529) and attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            raise RuntimeError('HTTP %s %s' % (e.code, msg))
    return None

# ---- 3. matching ----
def main(zip_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    z = zipfile.ZipFile(zip_path)
    pdf = next(n for n in z.namelist() if n.lower().endswith('.pdf'))
    rows = parse_rows(z.read(pdf))
    images = []
    for n in z.namelist():
        if not n.lower().endswith('.jpg'): continue
        m = re.match(r'^(\d+)_(.*)\.jpg$', n, re.I)
        u = re.match(r'^([0-9a-f-]{36})(?:_(.*))?\.jpg$', n, re.I)
        label = m.group(2) if m else (u.group(2) or '') if u else n[:-4]
        images.append({'file': n, 'idx': int(m.group(1)) if m else 10 ** 6, 'label': label, 'key': key(label)})
    print('rows', len(rows), 'images', len(images))

    # Claude pass, cached
    cache_path = os.path.join(out_dir, 'reads.json')
    reads = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        todo = [im for im in images if im['file'] not in reads]
        print('reading %d images with Claude (%d cached)' % (len(todo), len(images) - len(todo)))
        for k, im in enumerate(todo):
            try:
                reads[im['file']] = read_image(api_key, z.read(im['file']), im['label'])
            except Exception as e:
                print('  read failed', im['file'], e); reads[im['file']] = {'error': str(e)}
            json.dump(reads, open(cache_path, 'w'), indent=1)
            print('  %d/%d %s -> %s' % (k + 1, len(todo), im['file'], json.dumps(reads[im['file']])[:120]))
    else:
        print('ANTHROPIC_API_KEY not set: skipping the Claude pass, matching by name and order only')

    # match images to rows: unique keys first, then by read date/total, then by order
    by_key = collections.defaultdict(list)
    for r in rows: by_key[r['key']].append(r)
    used = set(); pairs = []; unmatched_imgs = []
    def read_of(im):
        rd = reads.get(im['file']) or {}
        return rd if rd.get('readable', True) and not rd.get('error') else {}
    # pass 1: unique name
    for im in images:
        cands = [r for r in by_key.get(im['key'], []) if r['i'] not in used]
        if im['key'] and len(by_key.get(im['key'], [])) == 1 and cands:
            used.add(cands[0]['i']); pairs.append((im, cands[0], 'name'))
    done = {p[0]['file'] for p in pairs}
    # pass 2: repeated names, choose by read date then total; also unnamed uuid images by date+total across all rows
    for im in images:
        if im['file'] in done: continue
        rd = read_of(im)
        pool = [r for r in by_key.get(im['key'], []) if r['i'] not in used] if im['key'] else [r for r in rows if r['i'] not in used]
        pick, how = None, None
        if rd.get('date') or rd.get('total') is not None:
            scored = []
            for r in pool:
                sc = 0
                if rd.get('date') == r['date']: sc += 2
                elif rd.get('date') and abs((datetime.fromisoformat(rd['date']) - datetime.fromisoformat(r['date'])).days) <= 3: sc += 1
                if rd.get('total') is not None and abs(float(rd['total']) - r['price']) < 0.01: sc += 2
                if sc: scored.append((sc, r))
            if scored:
                scored.sort(key=lambda x: -x[0]); pick, how = scored[0][1], 'read'
        if pick is None and im['key'] and pool:
            # order guess: images with the same name sorted by their index, rows by date
            pool_imgs = sorted([x for x in images if x['key'] == im['key'] and x['file'] not in done], key=lambda x: x['idx'])
            pos = pool_imgs.index(im)
            pool_rows = sorted(pool, key=lambda r: r['date'])
            if pos < len(pool_rows): pick, how = pool_rows[pos], 'order'
        if pick is not None:
            used.add(pick['i']); done.add(im['file']); pairs.append((im, pick, how))
        else:
            unmatched_imgs.append(im)
    unmatched_rows = [r for r in rows if r['i'] not in used]

    # ---- 4. build receipts ----
    receipts, out_images, notes = [], [], []
    def guess_category(cat_key, item, rd):
        mapped = CATEGORY_MAP.get(cat_key, ('Other', []))
        if mapped[0]: return mapped[0], mapped[1]
        c = rd.get('category') if rd else None
        return (c if c in CATEGORIES else 'Electronics'), mapped[1]
    def make_receipt(row, im, how, rd):
        pid = uid()
        label_name = im['label'] if im else ''
        item = (rd.get('item') if rd else None) or label_name or (row['name'] if row else '')
        cat, tags = guess_category(row['cat'] if row else '', item, rd)
        date = row['date'] if row else (rd.get('date') if rd else None)
        total = row['price'] if row else (rd.get('total') if rd else None)
        comments, unsure = [], []
        if row and rd:
            if rd.get('date') and rd['date'] != row['date'] and rd['confidence']['date'] == 'high':
                comments.append('Smart Receipts date was %s; invoice shows %s' % (row['date'], rd['date'])); date = rd['date']
            if rd.get('total') is not None and abs(float(rd['total']) - row['price']) >= 0.01 and rd['confidence']['total'] == 'high':
                comments.append('Smart Receipts total was %.2f; invoice shows %.2f' % (row['price'], float(rd['total']))); total = float(rd['total'])
        if row and label_name and key(label_name) != row['key']:
            comments.append('Smart Receipts name: %s' % row['name'])
        if how == 'order':
            comments.append('Image matched to this entry by order only; check it is the right one'); unsure.append('date')
        if row is None: comments.append('No table row for this image; details read from the image'); unsure += ['date', 'total']
        if rd and rd.get('confidence', {}).get('merchant') == 'low': unsure.append('merchant')
        merchant = (rd.get('merchant') if rd else '') or ''
        return {
            'id': uid(), 'items': item, 'merchant': merchant, 'date': date, 'total': total,
            'gstIncluded': bool(rd and rd.get('gst')), 'currency': (row['cur'] if row else 'AUD'), 'category': cat, 'tags': tags,
            'comments': '\n'.join(comments), 'pages': [pid] if im else [], 'unsure': sorted(set(unsure)), 'needsReview': bool(unsure),
            'createdAt': (date or '2026-01-01') + 'T00:00:00.000Z', 'updatedAt': datetime.utcnow().isoformat() + 'Z', 'source': 'smart-receipts'
        }, pid
    for im, row, how in pairs:
        r, pid = make_receipt(row, im, how, read_of(im)); receipts.append(r); out_images.append((im, r, pid))
    for im in unmatched_imgs:
        r, pid = make_receipt(None, im, 'none', read_of(im)); receipts.append(r); out_images.append((im, r, pid))
    for row in unmatched_rows:
        r, _ = make_receipt(row, None, 'none', {}); r['comments'] = 'No image in the export for this entry'; receipts.append(r)

    # ---- 5. write the import zip ----
    out_zip = os.path.join(out_dir, 'smart-receipts-import.zip')
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_STORED) as oz:
        oz.writestr('receipts.json', json.dumps({'app': 'Receipts', 'exportedAt': datetime.utcnow().isoformat() + 'Z', 'categories': CATEGORIES, 'tags': TAGS, 'notDuplicates': [], 'receipts': receipts}, indent=1))
        saved = 0
        for im, r, pid in out_images:
            data = z.read(im['file'])
            # Same limits the app uses for its own captures: long side 2800 px, JPEG quality 88. Only replace the
            # original when that is clearly smaller; a receipt is never upscaled and never quality-reduced twice.
            if Image is not None:
                try:
                    imx = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
                    if max(imx.size) > 2800: imx.thumbnail((2800, 2800), Image.LANCZOS)
                    buf = io.BytesIO(); imx.save(buf, 'JPEG', quality=88, optimize=True, subsampling=0)
                    if buf.tell() < len(data) * 0.85: saved += len(data) - buf.tell(); data = buf.getvalue()
                except Exception as e:
                    print('  keep original', im['file'], e)
            oz.writestr('images/' + page_file_name(r, 0, pid), data)
        print('images compressed, saved %.1f MB' % (saved / 1048576))
    hows = collections.Counter(h for _, _, h in pairs)
    rep = ['# Smart Receipts conversion', '', 'Rows in table: %d. Images: %d.' % (len(rows), len(images)),
           'Matched by unique name: %d. By invoice date/total: %d. By order only (check these): %d.' % (hows['name'], hows['read'], hows['order']),
           'Images with no row: %d. Rows with no image: %d.' % (len(unmatched_imgs), len(unmatched_rows)), '',
           '## Rows with no image', *['- %s %s %.2f (%s)' % (r['date'], r['name'], r['price'], r['cat']) for r in unmatched_rows], '',
           '## Images with no row', *['- %s' % im['file'] for im in unmatched_imgs], '',
           '## Matched by order only', *['- %s -> %s %s %.2f' % (im['file'], row['date'], row['name'], row['price']) for im, row, how in pairs if how == 'order'], '',
           '## Invoice disagreed with the table', *['- %s: %s' % (r['items'], r['comments'].split('\n')[0]) for r in receipts if 'invoice shows' in r['comments']]]
    open(os.path.join(out_dir, 'report.md'), 'w', encoding='utf-8').write('\n'.join(rep))
    print('\n'.join(rep[:6])); print('wrote', out_zip)

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
