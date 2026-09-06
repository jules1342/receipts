"""
Correction pass for the first Smart Receipts import (2026-09-06). Builds a small delta zip that the app imports on top
of what is already there: it re-attaches the bill images to the right entries by invoice date and total, attaches the
three mislabelled images, and removes the 19 image-only stubs. Every receipt id comes from the first import file, so the
app updates in place. Reads below were done by eye from the invoice images.

    python smart-receipts-delta.py <original smart receipts zip> <first import zip> <output folder>
"""
import sys, os, re, io, json, zipfile, collections
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location('conv', os.path.join(os.path.dirname(__file__), 'smart-receipts-convert.py'))
conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

# source image -> (type, invoice issue date, amount paid, note)
READS = {
 '019d9e29-fb87-70b8-b083-9361805f81ad.jpg': ('water', '2025-07-14', 174.10, ''),
 '019d9e2b-0949-75fa-a970-2bf2e3b54a41.jpg': ('gas', '2025-10-14', 152.92, ''),
 '019d9e2c-6553-7307-91dd-f5ec91f5cb5d.jpg': ('electricity', '2025-09-23', 496.40, 'Bill $571.40 less $75 credit'),
 '019d9e2e-064a-7669-9473-3a9d6ff3f000.jpg': ('water', '2026-01-15', 157.35, ''),
 '019d9e2e-d1ed-76d6-a066-72b28fdb7b95.jpg': ('electricity', '2026-02-24', 101.36, ''),
 '019d9e30-0b86-7a0d-94c9-fc17e2bff18c.jpg': ('gas', '2026-02-16', 166.97, ''),
 '019d9e31-3789-746c-bf90-4895e0159547.jpg': ('electricity', '2025-12-23', 327.43, ''),
 '019d9e32-053a-70f3-b1e7-f0eb5745d2f5.jpg': ('gas', '2025-12-16', 143.89, ''),
 '019d9e33-c7f7-7efd-b3fc-cfc56419a89d.jpg': ('rates', '2026-01-21', 401.45, 'Instalment 3, 2025-26'),
 '019d9e34-b66e-7eb3-ba85-af92d90057bf.jpg': ('rates', '2026-04-10', 401.50, 'Instalment 4, 2025-26'),
 '01a06fc0-c100-7cbb-a17a-cf9111bc5092.jpg': ('jbhifi', '2025-06-19', 625.00, 'Samsung Jet 95 stick vac, JB Hi-Fi Brighton'),
 '1d99e233-77ca-4362-bd34-2ae0e564aeb2.jpg': ('gas', '2025-06-16', 150.00, ''),
 '29c85f90-9c5a-4862-a56e-ed894d66732e.jpg': ('gas', '2025-08-13', 141.92, ''),
 '3a9bc9c6-ab2a-48ef-80c2-3e9468f86bf5.jpg': ('water', '2025-10-13', 173.75, ''),
 'e919f723-3965-435d-a711-801eb2f758d9.jpg': ('electricity', '2025-06-25', 348.06, 'Bill $423.06 less $75 credit'),
 'f5d01dc2-0733-4309-89e3-0506dbe82a58.jpg': ('rates', '2025-08-01', 802.90, 'Rate notice 2025-26, total $1,605.85; instalments 1 and 2 paid ($401.45 each)'),
 '1c2058dc-5ed8-4805-ac39-5e01d090060a_gas.jpg': ('gas', '2024-10-15', 115.32, ''),
 'c5508168-2b3a-4f6b-ae58-c510e4b94d6f_gas.jpg': ('gas', '2025-02-17', 132.64, ''),
 '424f967e-560c-42db-bd5a-5289d49cff8b_gas.jpg': ('gas', '2024-12-17', 176.77, 'Debited 8 Jan 2025'),
 '3f01cde0-d417-4110-a222-3f2a0a645069_water.jpg': ('water', '2025-01-15', 175.05, ''),
 '1c8c70cc-19ae-40e0-a2a0-b26d45d38a93_water.jpg': ('water', '2025-04-14', 173.15, ''),
 '4b471b0e-9f36-49b6-a76d-32dd6d056ae9_electricity.jpg': ('electricity', '2024-12-30', 370.22, ''),
 'a0cc99ae-9236-4c23-be40-48284e940698_Electricity.jpg': ('electricity', '2025-03-27', 396.11, 'Bill $471.11 less $75 credit'),
 '799b3832-f568-4d65-b7ee-b155c4fa324f_Rates 2.jpg': ('rates', '2024-10-11', 378.60, 'Instalment 2, 2024-25'),
 '26ddf940-bf62-404d-bdd6-573fc50ba23d_Rates 4.jpg': ('rates', '2025-05-05', 378.70, 'Instalment 4, 2024-25'),
 '37b65a9c-6dc6-4d90-8de5-c8b02b97a1c1_Rates 3.jpg': ('rates', '2025-01-22', 378.60, 'Instalment 3, 2024-25'),
 '206_rates..jpg': ('rates', '2024-08-20', 378.60, 'Rate notice 2024-25, total $1,514.50; instalment 1'),
 '205_electricity..jpg': ('electricity', '2024-09-30', 234.08, 'Bill $309.08 less $75 credit'),
 '204_water..jpg': ('water', '2024-10-14', 175.45, ''),
 '207_gas..jpg': ('gas', '2024-08-13', 137.49, ''),
 '11_Gas.jpg': ('gas', '2023-10-17', 224.18, ''),
 '17_Gas.jpg': ('gas', '2023-12-11', 131.39, ''),
 '18_Gas.jpg': ('gas', '2024-02-13', 139.37, ''),
 '21_Gas.jpg': ('gas', '2024-04-12', 109.37, ''),
 '23_Gas.jpg': ('gas', '2024-06-12', 125.70, 'Debited 1 Jul 2024'),
 '1_Water.jpg': ('water', '2023-04-17', 116.00, ''),
 '10_Water.jpg': ('water', '2023-10-12', 172.85, ''),
 '15_Water.jpg': ('water', '2024-01-16', 159.45, ''),
 '19_Water.jpg': ('water', '2024-04-15', 170.30, ''),
 '26_Water.jpg': ('water', '2024-07-12', 168.55, ''),
 '12_Electricity.jpg': ('electricity', '2023-10-09', 255.24, ''),
 '16_Electricity.jpg': ('electricity', '2024-01-03', 298.41, ''),
 '20_Electricity.jpg': ('electricity', '2024-04-03', 264.89, ''),
 '24_Electricity.jpg': ('electricity', '2024-07-02', 399.04, ''),
 '13_Rates.jpg': ('rates', '2023-10-18', 338.45, 'Instalment 2, 2023-24'),
 '14_Rates installment 3.jpg': ('rates', '2024-01-12', 338.45, 'Instalment 3, 2023-24'),
 '22_Rates 4.jpg': ('rates', '2024-04-17', 338.60, 'Instalment 4, 2023-24'),
}
# non-bill fixes: image-only stub label -> row (date, name)
LABEL_FIX = {'Couch Part 1': ('2020-06-01', 'Couch'), 'May - PC': ('2019-01-05', 'Msy-PC'), 'Vegan pie': ('2022-05-04', 'Muffinbreak')}
MERCHANT = {'gas': 'AGL', 'electricity': 'AGL', 'water': 'South East Water', 'rates': 'Glen Eira City Council', 'jbhifi': 'JB Hi-Fi'}
ITEM = {'gas': 'Gas', 'electricity': 'Electricity', 'water': 'Water', 'rates': 'Rates', 'jbhifi': 'Samsung Jet 95 stick vac'}

def rowtype(r):
    k = r['key']
    for t in ('gas', 'water', 'electricity'):
        if k == t: return t
    if k.startswith('rates'): return 'rates'
    if k == 'jbhifi': return 'jbhifi'
    return None

def main(src_zip, first_zip, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    z = zipfile.ZipFile(src_zip)
    rows = conv.parse_rows(z.read(next(n for n in z.namelist() if n.lower().endswith('.pdf'))))
    prev = json.loads(zipfile.ZipFile(first_zip).read('receipts.json'))['receipts']
    # previous receipt for a row: same date and price, item equals the row name or an image label (first pass used the label)
    def prev_for_row(r):
        c = [p for p in prev if p['date'] == r['date'] and p['total'] is not None and abs(float(p['total']) - r['price']) < 0.005 and 'No table row' not in (p['comments'] or '')]
        if len(c) > 1:
            c2 = [p for p in c if conv.key(p['items']) == r['key'] or ('Smart Receipts name: ' + r['name']) in (p['comments'] or '')]
            if c2: c = c2
        return c
    bill_rows = [r for r in rows if rowtype(r)]
    used_rows, updates, deletes, notes = set(), [], [], []
    # 1. bill images -> rows by (type, total) then nearest date; leftovers by date within 45 days
    imgs = list(READS.items())
    pairs = []
    for f, (t, d, amt, note) in imgs:
        cands = [r for r in bill_rows if rowtype(r) == t and r['i'] not in used_rows and abs(r['price'] - amt) < 0.005]
        if not cands:
            cands = [r for r in bill_rows if rowtype(r) == t and r['i'] not in used_rows and abs((datetime.fromisoformat(r['date']) - datetime.fromisoformat(d)).days) <= 45]
            how = 'date' if cands else None
        else: how = 'total'
        if not cands: pairs.append((f, None, None)); continue
        cands.sort(key=lambda r: abs((datetime.fromisoformat(r['date']) - datetime.fromisoformat(d)).days))
        used_rows.add(cands[0]['i']); pairs.append((f, cands[0], how))
    stubs = [p for p in prev if 'No table row' in (p['comments'] or '')]
    out_images = []
    for f, r, how in pairs:
        t, d, amt, note = READS[f]
        if r is None:
            notes.append('NO ROW for %s (%s %s %.2f): left as an image-only receipt' % (f, t, d, amt)); continue
        pr = prev_for_row(r)
        if len(pr) != 1:
            notes.append('AMBIGUOUS previous receipt for row %s %s %.2f: %d candidates' % (r['date'], r['name'], r['price'], len(pr))); continue
        p = dict(pr[0]); pid = conv.uid()
        comments = [c for c in (p['comments'] or '').split('\n') if c and 'matched to this entry by order' not in c]
        if note: comments.append(note)
        if d != r['date']: comments.append('Smart Receipts date was %s; invoice issued %s' % (conv.__dict__['datetime'].fromisoformat(r['date']).strftime('%d/%m/%Y'), datetime.fromisoformat(d).strftime('%d/%m/%Y')))
        if abs(amt - r['price']) >= 0.005: comments.append('Smart Receipts total was %.2f; invoice shows %.2f' % (r['price'], amt))
        p.update({'date': d, 'total': amt, 'items': ITEM[t] if t != 'rates' else (ITEM[t] + (' ' + note.split(',')[0].replace('Instalment ', 'instalment ') if note.startswith('Instalment') else '')), 'merchant': MERCHANT[t],
                  'pages': [pid], 'comments': '\n'.join(comments), 'unsure': [], 'needsReview': how == 'date',
                  'updatedAt': datetime.utcnow().isoformat() + 'Z'})
        p.pop('thumb', None)
        updates.append(p); out_images.append((f, p, pid))
    # 2. mislabelled stubs -> rows
    for label, (d, name) in LABEL_FIX.items():
        st = [p for p in stubs if p['items'] == label]; r = [x for x in rows if x['date'] == d and x['name'] == name]
        if len(st) != 1 or len(r) != 1: notes.append('LABEL FIX failed for %s' % label); continue
        pr = prev_for_row(r[0])
        if len(pr) != 1: notes.append('LABEL FIX ambiguous for %s' % label); continue
        p = dict(pr[0]); p.update({'pages': st[0]['pages'], 'updatedAt': datetime.utcnow().isoformat() + 'Z', 'needsReview': label == 'Vegan pie', 'unsure': ['merchant'] if label == 'Vegan pie' else []})
        p['comments'] = ((p['comments'] or '') + '\nImage came from Smart Receipts entry "%s"' % label).strip(); p.pop('thumb', None)
        updates.append(p); deletes.append(st[0]['id'])
    # 3. delete every other stub whose image is now attached elsewhere (the 16 unnamed + labelled uuid ones that were stubs)
    for st in stubs:
        if st['id'] in deletes: continue
        if st['items'] in LABEL_FIX: continue
        deletes.append(st['id'])
    # 4. rows the Smart Receipts table listed twice: keep the receipt that has an image, remove the other copy
    seen = collections.defaultdict(list)
    for p in prev:
        if 'No table row' in (p['comments'] or ''): continue
        seen[(p['date'], round(float(p['total']), 2) if p['total'] is not None else None, conv.key(p['items']))].append(p)
    dup_removed = 0
    for k, group in seen.items():
        if len(group) < 2: continue
        upd_ids = {u['id'] for u in updates}
        group.sort(key=lambda p: (0 if (p['pages'] or p['id'] in upd_ids) else 1, p['createdAt']))
        for extra in group[1:]:
            if extra['id'] in upd_ids: continue
            deletes.append(extra['id']); dup_removed += 1
            notes.append('Duplicate table row removed: %s %s %.2f' % (extra['date'], extra['items'], float(extra['total'])))
    # 5. the June 2024 gas bill was entered twice, once on the issue date and once on the debit date
    for p in prev:
        if p['date'] == '2024-07-01' and conv.key(p['items']) == 'gas' and abs(float(p['total']) - 125.70) < 0.005 and not p['pages']:
            deletes.append(p['id']); notes.append('Removed 2024-07-01 Gas 125.70: same bill as 12 Jun 2024 (debit date 1 Jul)')
    # write
    out_zip = os.path.join(out_dir, 'smart-receipts-fix.zip')
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_STORED) as oz:
        oz.writestr('receipts.json', json.dumps({'app': 'Receipts', 'exportedAt': datetime.utcnow().isoformat() + 'Z', 'categories': conv.CATEGORIES, 'tags': conv.TAGS, 'notDuplicates': [], 'deleted': deletes, 'receipts': updates}, indent=1))
        for f, p, pid in out_images:
            data = z.read(f)
            if Image is not None:
                imx = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
                if max(imx.size) > 2800: imx.thumbnail((2800, 2800), Image.LANCZOS)
                buf = io.BytesIO(); imx.save(buf, 'JPEG', quality=88, optimize=True, subsampling=0)
                if buf.tell() < len(data) * 0.85: data = buf.getvalue()
            oz.writestr('images/' + conv.page_file_name(p, 0, pid), data)
    # coverage report: every row, does it now have an image?
    have = set()
    for p in prev:
        if p['pages'] and 'No table row' not in (p['comments'] or ''): have.add(p['id'])
    for p in updates: have.add(p['id'])
    missing = []
    delset = set(deletes)
    for r in rows:
        pr = [x for x in prev_for_row(r) if x['id'] not in delset]
        if len(pr) >= 1 and not any(x['id'] in have for x in pr): missing.append(r)
        elif not pr: notes.append('coverage check could not find receipt for row %s %s %.2f' % (r['date'], r['name'], r['price']))
    rep = ['# Correction pass', '', 'Updated receipts: %d. Removed: %d (19 image-only stubs, %d duplicate rows, 1 double-entered bill). Images re-attached: %d.' % (len(updates), len(deletes), dup_removed, len(out_images)), '',
           '## Bill image -> entry', *['- %s -> %s %s %.2f (%s)' % (f, r['date'], r['name'], r['price'], how) for f, r, how in pairs if r], '',
           '## Rows still without an image', *['- %s %s %.2f (%s)' % (r['date'], r['name'], r['price'], r['cat']) for r in missing], '',
           '## Notes', *['- ' + n for n in notes]]
    open(os.path.join(out_dir, 'fix-report.md'), 'w', encoding='utf-8').write('\n'.join(rep))
    print('\n'.join(rep)); print('wrote', out_zip)

if __name__ == '__main__':
    main(*sys.argv[1:4])
