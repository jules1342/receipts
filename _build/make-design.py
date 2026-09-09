"""
Builds receipts-design.html, the "ledger" design-system variant, from receipts.html. Same logic, same data, restyled:
paper surfaces, a serif for titles and amounts, hairline rows instead of cards, a month summary strip, one ink-green
accent, 12/14/16/20/24 type, two weights, 4/8 spacing, radius 6/8, borders not shadows, light and dark, visible focus,
reduced motion, bound labels, alt text, single-column forms, inline toasts instead of alerts.
Re-run after any change to receipts.html: python _build/make-design.py
"""
import os, re
base = os.path.join(os.path.dirname(__file__), '..')
src = open(os.path.join(base, 'receipts.html'), encoding='utf-8').read()
s = src

def rep(a, b, count=1):
    global s
    assert a in s, a[:70]; s = s.replace(a, b, count)

DARK = """      --surface: #1D1B17; --surface-2: #14130F; --surface-3: #29261F;
      --text: #F1ECE1; --text-2: #B3AC9E; --text-3: #948C7D;
      --border: rgba(255,250,240,0.12); --border-strong: rgba(255,250,240,0.24);
      --accent: #6FBF95; --accent-tint: #1C3428; --accent-text: #9BD7B7; --on-accent: #0E1A13;
      --red: #F08A80; --red-tint: #3A1F1C; --green: #6FBF95; --green-tint: #1C3428; --amber: #E8B85C; --amber-tint: #3A2F14;
      --shadow-float: 0 4px 16px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4);"""

STYLE = """  <style>
    /* Ledger design system. Tokens first; nothing below is improvised. */
    :root {
      color-scheme: light;
      --sans: -apple-system, "Segoe UI", Roboto, Inter, sans-serif;
      --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
      --surface: #FFFDF9; --surface-2: #F4EFE4; --surface-3: #EBE5D8;
      --text: #211D17; --text-2: #5F5849; --text-3: #6F6859;
      --border: rgba(33,29,23,0.14); --border-strong: rgba(33,29,23,0.28);
      --accent: #1F6B4A; --accent-tint: #E3EFE7; --accent-text: #185A3E; --on-accent: #FFFFFF;
      --red: #B42318; --red-tint: #FCEBE9; --green: #1F6B4A; --green-tint: #E3EFE7; --amber: #8A5200; --amber-tint: #FBF0DC;
      --r-control: 6px; --r-card: 8px; --r-pill: 999px;
      --shadow-float: 0 4px 12px rgba(33,29,23,0.12), 0 1px 2px rgba(33,29,23,0.08);
      --ease-out: cubic-bezier(0.2, 0, 0, 1); --dur: 200ms;
      --bg: var(--surface-2); --card: var(--surface); --ink: var(--text); --muted: var(--text-2); --line: var(--border);
      --navy: var(--accent); --navy-soft: var(--accent-tint); --amber-soft: var(--amber-tint); --green-soft: var(--green-tint); --radius: var(--r-card);
      --safe-b: env(safe-area-inset-bottom, 0px); --safe-t: env(safe-area-inset-top, 0px);
    }
    @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark;
""" + DARK + """
    } }
    :root[data-theme="dark"] { color-scheme: dark;
""" + DARK + """
    }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: var(--sans); font-size: 16px; line-height: 1.5; }
    body { min-height: 100vh; }
    button { font: inherit; color: inherit; cursor: pointer; }
    input, select, textarea { font: inherit; color: inherit; }
    :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
    .app { min-height: 100vh; padding-bottom: calc(96px + var(--safe-b)); max-width: 640px; margin: 0 auto; }
    .sheet > * { max-width: 640px; margin-left: auto; margin-right: auto; }
    .topbar { position: sticky; top: 0; z-index: 20; background: var(--bg); padding: calc(12px + var(--safe-t)) 16px 8px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .topbar h1 { font-family: var(--serif); font-size: 24px; margin: 0; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; }
    .serif { font-family: var(--serif); }
    .fab { position: fixed; right: 16px; bottom: calc(24px + var(--safe-b)); z-index: 31; width: 56px; height: 56px; border-radius: var(--r-pill); background: var(--accent); color: var(--on-accent); border: none; box-shadow: var(--shadow-float); display: flex; align-items: center; justify-content: center; transition: transform var(--dur) var(--ease-out); }
    .fab:active { transform: scale(0.96); }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: var(--r-card); padding: 12px; margin: 0 16px 16px; }
    .row { display: flex; align-items: center; gap: 8px; }
    .grow { flex: 1; min-width: 0; }
    .muted { color: var(--text-2); }
    .small { font-size: 14px; }
    .amt { font-family: var(--serif); font-variant-numeric: tabular-nums; font-weight: 600; letter-spacing: -0.01em; }
    .chip { display: inline-flex; align-items: center; gap: 6px; padding: 0 8px; min-height: 24px; border-radius: var(--r-pill); font-size: 12px; line-height: 1; background: transparent; color: var(--text-2); border: 1px solid var(--border); white-space: nowrap; }
    .chip .dot { width: 8px; height: 8px; border-radius: 4px; flex-shrink: 0; }
    .chip.tag { color: var(--text-2); }
    .chip.warn { background: var(--amber-tint); color: var(--amber); border-color: transparent; }
    .chip.btn { background: var(--surface); border-color: var(--border-strong); color: var(--text); min-height: 44px; padding: 0 14px; font-size: 14px; transition: background var(--dur) var(--ease-out); }
    .chip.btn.on { background: var(--accent-tint); color: var(--accent-text); border-color: var(--accent); }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .thumb { width: 44px; height: 56px; object-fit: cover; border-radius: 4px; background: var(--surface-3); border: 1px solid var(--border); flex-shrink: 0; }
    .btn { border: 1px solid var(--border-strong); background: var(--surface); border-radius: var(--r-control); padding: 10px 16px; min-height: 44px; font-weight: 600; font-size: 16px; transition: background var(--dur) var(--ease-out), opacity var(--dur) var(--ease-out); }
    .btn:active { background: var(--surface-2); }
    .btn.primary { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
    .btn.quiet { background: transparent; border-color: transparent; color: var(--accent-text); padding: 10px 12px; }
    .btn.danger { color: var(--red); border-color: var(--border-strong); }
    .btn.danger.armed { background: var(--red); color: #fff; border-color: var(--red); }
    .btn.wide { width: 100%; }
    .btn:disabled { opacity: 0.4; cursor: default; }
    .field { margin-bottom: 16px; }
    .field label { display: block; font-size: 14px; color: var(--text-2); margin-bottom: 6px; font-weight: 600; }
    .field label.row { display: flex; align-items: center; min-height: 44px; margin: 0; }
    input[type="checkbox"] { width: 22px; height: 22px; accent-color: var(--accent); }
    .field input, .field select, .field textarea { width: 100%; padding: 10px 12px; min-height: 44px; border: 1px solid var(--border-strong); border-radius: var(--r-control); background: var(--surface); font-size: 16px; }
    .field textarea { min-height: 88px; resize: vertical; }
    .field.unsure input, .field.unsure select { border-color: var(--amber); }
    .field.unsure { background: var(--amber-tint); margin-left: -8px; margin-right: -8px; padding: 8px 8px 4px; border-radius: var(--r-control); }
    .unsure-note { font-size: 14px; color: var(--amber); margin-top: 4px; }
    .section-h { padding: 24px 16px 8px; font-size: 12px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.08em; display: flex; justify-content: space-between; align-items: center; }
    .section-h .amt { font-size: 14px; color: var(--text-2); }
    .empty { text-align: center; color: var(--text-2); padding: 64px 24px; font-size: 16px; }
    .search { width: 100%; padding: 10px 12px; min-height: 44px; border-radius: var(--r-control); border: 1px solid var(--border-strong); background: var(--surface); font-size: 16px; }
    .filters { display: flex; gap: 8px; overflow-x: auto; padding: 4px 16px 8px; scrollbar-width: none; }
    .filters::-webkit-scrollbar { display: none; }
    .flabel { font-size: 12px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.08em; align-self: center; min-width: 64px; flex-shrink: 0; }
    .sheet { position: fixed; inset: 0; z-index: 40; background: var(--bg); overflow-y: auto; padding-bottom: calc(24px + var(--safe-b)); }
    .sheet .topbar { background: var(--bg); }
    .pages { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0; }
    .pages img { height: 120px; border-radius: 4px; border: 1px solid var(--border); }
    .pages .add { height: 120px; width: 88px; border-radius: var(--r-control); border: 1px dashed var(--border-strong); background: none; color: var(--text-2); font-size: 14px; }
    .banner { margin: 0 16px 16px; padding: 12px; border-radius: var(--r-card); font-size: 14px; line-height: 1.5; }
    .banner.err { background: var(--red-tint); color: var(--red); }
    .banner.ok { background: var(--green-tint); color: var(--green); }
    .banner.info { background: var(--accent-tint); color: var(--accent-text); }
    .spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
    .spinner.dark { border-color: var(--border-strong); border-top-color: var(--accent); }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes focusPulse { 0% { transform: scale(1.3); opacity: 0; } 30% { opacity: 1; } 100% { transform: scale(1); opacity: 0; } }
    .facts { display: flex; flex-direction: column; gap: 4px; font-size: 14px; color: var(--text-2); margin-top: 12px; }
    .facts .mono { font-variant-numeric: tabular-nums; color: var(--text); }
    .total-line { display: flex; justify-content: space-between; align-items: center; padding: 8px 16px; font-size: 14px; color: var(--text-2); }
    .ledger { margin: 0 16px; border-top: 1px solid var(--border); }
    .lrow { display: flex; gap: 12px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid var(--border); cursor: pointer; }
    .lrow.sel { background: var(--accent-tint); margin: 0 -16px; padding: 12px 16px; }
    .lrow .title { font-size: 16px; font-weight: 600; line-height: 1.3; }
    .lrow .sub { font-size: 14px; color: var(--text-2); margin-top: 2px; }
    .lrow .amt { font-size: 20px; white-space: nowrap; }
    .month { display: flex; justify-content: space-between; align-items: baseline; padding: 24px 16px 8px; }
    .month .name { font-family: var(--serif); font-size: 20px; font-weight: 600; }
    .month .sum { font-size: 14px; color: var(--text-2); }
    .summary { margin: 8px 16px 16px; padding: 16px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-card); }
    .summary .label { font-size: 12px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.08em; }
    .summary .big { font-family: var(--serif); font-size: 24px; font-weight: 600; line-height: 1.2; margin-top: 4px; font-variant-numeric: tabular-nums; }
    .summary .meta { font-size: 14px; color: var(--text-2); margin-top: 4px; }
    .toast { position: fixed; left: 16px; right: 16px; bottom: calc(96px + var(--safe-b)); z-index: 80; background: var(--text); color: var(--surface); padding: 12px 16px; border-radius: var(--r-card); font-size: 14px; box-shadow: var(--shadow-float); max-width: 608px; margin: 0 auto; }
    .crop-wrap { position: relative; touch-action: none; user-select: none; }
    .crop-wrap img { display: block; width: 100%; height: auto; }
    .handle { position: absolute; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 22px; background: rgba(255,255,255,0.15); border: 2px solid #fff; box-shadow: 0 0 0 2px rgba(0,0,0,0.4); }
    .handle::after { content: ''; position: absolute; left: 50%; top: 50%; width: 10px; height: 10px; margin: -5px 0 0 -5px; border-radius: 5px; background: #fff; }
    .handle { transform-origin: center; touch-action: none; }
    .handle.edge { width: 36px; height: 36px; margin: -18px 0 0 -18px; border-radius: 8px; background: rgba(255,255,255,0.1); }
    .handle.edge::after { width: 14px; height: 4px; margin: -2px 0 0 -7px; border-radius: 2px; }
    .seg { display: flex; border: 1px solid var(--border-strong); border-radius: var(--r-control); overflow: hidden; }
    .seg button { flex: 1; border: none; background: var(--surface); padding: 10px; min-height: 44px; font-size: 14px; }
    .seg button.on { background: var(--accent); color: var(--on-accent); }
    .sync-dot { width: 8px; height: 8px; border-radius: 4px; display: inline-block; }
    .icon { width: 20px; height: 20px; stroke: currentColor; fill: none; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; display: block; }
  </style>"""
i = s.index('  <style>'); j = s.index('  </style>') + len('  </style>')
s = s[:i] + STYLE + s[j:]

# ---- identity ----
rep('<title>Receipts</title>', '<title>Receipts ledger</title>')
rep('<meta name="theme-color" content="#1F3A5F">', '<meta name="theme-color" content="#F4EFE4">')
s = re.sub(r"const BUILD_VERSION = '([^']+)';", lambda m: "const BUILD_VERSION = '%s-ledger';" % m.group(1), s, count=1)
rep("const HAS_DARK = false;", "const HAS_DARK = true;")

# ---- type scale 12/14/16/20/24, two weights, token colours ----
size_map = {'10': '12', '11': '12', '13': '14', '15': '16', '18': '20', '22': '24', '28': '24'}
s = re.sub(r'fontSize: (\d+)\b', lambda m: 'fontSize: ' + size_map.get(m.group(1), m.group(1)), s)
s = s.replace('fontWeight: 700', 'fontWeight: 600').replace('fontWeight: 500', 'fontWeight: 400')
s = s.replace("'#B23A3A'", "'var(--red)'").replace("#B23A3A", "var(--red)").replace("'#eee'", "'var(--surface-3)'").replace("'#555'", "'var(--text-2)'")
s = re.sub(r"const CATEGORY_COLOURS = \[[^\]]*\];", "const CATEGORY_COLOURS = ['#1F6B4A', '#2F5FA8', '#B86A00', '#7A3E9D', '#B42318', '#0F7A8A', '#8A6D2B', '#5B6470'];", s, count=1)

# ---- toasts instead of browser alerts ----
rep("""    class ErrorBoundary extends React.Component {""",
"""    const showToast = (msg) => { try { let el = document.getElementById('toast'); if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; el.setAttribute('role', 'status'); document.body.appendChild(el); } el.textContent = String(msg); el.hidden = false; clearTimeout(el._t); el._t = setTimeout(() => { el.hidden = true; }, 5000); } catch (_) { window.alert(msg); } };
    class ErrorBoundary extends React.Component {""")
s = re.sub(r'(?<![\w.])alert\(', 'showToast(', s)

# ---- bound labels ----
rep("""    try { applyTheme((loadSettings().theme) || 'system'); } catch (_) {}""",
"""    try { applyTheme((loadSettings().theme) || 'system'); } catch (_) {}
    (function bindLabels() {
      let n = 0;
      const run = () => { document.querySelectorAll('.field > label').forEach(l => { if (l.htmlFor || l.querySelector('input')) return; const input = l.parentElement.querySelector('input, select, textarea'); if (!input) return; if (!input.id) input.id = 'f' + (++n); l.htmlFor = input.id; }); };
      new MutationObserver(run).observe(document.getElementById('root'), { childList: true, subtree: true }); run();
    })();""")

# ---- alt text ----
s = s.replace('<img src={p.url} />', '<img src={p.url} alt="Receipt page" />')
s = s.replace('<img key={p.id} src={p.url} onClick={() => setViewer(i)}', '<img key={p.id} src={p.url} alt={`Receipt page ${i + 1}`} onClick={() => setViewer(i)}')
s = s.replace('<img src={urls[i]} draggable={false}', '<img src={urls[i]} alt={`Receipt page ${i + 1}`} draggable={false}')
s = s.replace("<img src={r.thumb} style={{ width: '100%', maxHeight: 160", "<img src={r.thumb} alt=\"\" style={{ width: '100%', maxHeight: 160")
s = s.replace('<img src={item.before.thumb} className="thumb"', '<img src={item.before.thumb} alt="" className="thumb"')
s = s.replace('<img src={enhance ? result.enhancedUrl : result.colourUrl} draggable={false}', '<img src={enhance ? result.enhancedUrl : result.colourUrl} alt="Cleaned page" draggable={false}')
s = s.replace('<img ref={imgRef} src={preview} draggable={false}', '<img ref={imgRef} src={preview} alt="Photo to crop" draggable={false}')

# ---- category chips: colour as a dot, text stays neutral ----
s = s.replace("""<span className="chip" style={{ background: col + '22', color: col }}>{receipt.category}</span>""", """<span className="chip"><span className="dot" style={{ background: col }} />{receipt.category}</span>""")
s = s.replace("""<span className="chip" style={{ background: col + '22', color: col }}>{r.category}</span>""", """<span className="chip"><span className="dot" style={{ background: col }} />{r.category}</span>""")
s = s.replace("""<span className="chip" style={{ background: catColour(c, settings.categories) + '22', color: catColour(c, settings.categories) }}>{c}</span>""", """<span className="chip"><span className="dot" style={{ background: catColour(c, settings.categories) }} />{c}</span>""")
# ---- icons ----
GEAR = '<svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>'
rep("""<button className="btn" style={{ padding: '8px 12px' }} onClick={() => setShowSettings(true)} aria-label="Settings">⚙️</button>""",
    """<button className="btn quiet" style={{ minWidth: 44 }} onClick={() => setShowSettings(true)} aria-label="Settings">""" + GEAR + """</button>""")
rep("""<button className="fab" onClick={() => setCapturing(true)} aria-label="Add receipt">+</button>""",
    """<button className="fab" onClick={() => setCapturing(true)} aria-label="Add receipt"><svg className="icon" style={{ width: 24, height: 24, strokeWidth: 2 }} viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button>""")
rep("""<button type="button" className="btn" style={{ padding: '10px 12px' }} onClick={openPicker} aria-label="Pick a date">📅</button>""",
    """<button type="button" className="btn" style={{ padding: '0 12px', minWidth: 44 }} onClick={openPicker} aria-label="Pick a date"><svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg></button>""")

# ---- one primary action on the list ----
rep("""<div className="topbar"><h1>Receipts</h1><div className="row"><span className="small muted">{receipts.length} total</span>{!selecting && <button className="btn" style={{ padding: '8px 12px' }} onClick={() => setSelecting(true)}>Select</button>}""",
    """<div className="topbar"><h1>Receipts <span style={{ fontFamily: 'var(--sans)', fontSize: 12, fontWeight: 400, color: 'var(--text-3)', letterSpacing: '0.08em', textTransform: 'uppercase', verticalAlign: 'middle' }}>ledger</span></h1><div className="row" style={{ gap: 0 }}>{!selecting && <button className="btn quiet" onClick={() => setSelecting(true)}>Select</button>}""")
rep("""<button className={'btn' + (n || panel ? ' primary' : '')} style={{ whiteSpace: 'nowrap', padding: '10px 14px' }} onClick={() => setPanel(p => !p)}>Filter{n ? ` (${n})` : ''}</button>""",
    """<button className="btn quiet" style={{ whiteSpace: 'nowrap', background: n || panel ? 'var(--accent-tint)' : undefined }} onClick={() => setPanel(p => !p)}>Filter{n ? ` (${n})` : ''}</button>""")

# ---- ledger rows and month headers ----
row_start = s.index("    function ReceiptRow({ r, cats, onOpen, selectable, selected }) {")
row_end = s.index("    function ReceiptList({")
s = s[:row_start] + """    function ReceiptRow({ r, cats, onOpen, selectable, selected }) {
      const col = catColour(r.category, cats);
      const sub = [r.items ? (r.merchant || 'Unknown merchant') : '', fmtDate(r.date)].filter(Boolean).join(' · ');
      return (
        <div className={'lrow' + (selected ? ' sel' : '')} onClick={onOpen} role="button" tabIndex={0} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(); } }}>
          {selectable && <div aria-hidden="true" style={{ width: 24, height: 24, marginTop: 16, borderRadius: 12, border: '2px solid ' + (selected ? 'var(--accent)' : 'var(--border-strong)'), background: selected ? 'var(--accent)' : 'transparent', color: 'var(--on-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0 }}>{selected ? '✓' : ''}</div>}
          {r.thumb ? <img className="thumb" src={r.thumb} alt="" /> : <div className="thumb" aria-hidden="true" />}
          <div className="grow">
            <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
              <div className="title">{r.items || r.merchant || 'Receipt'}</div>
              <div className="amt">{fmtMoney(r.total, r.currency)}</div>
            </div>
            <div className="sub">{sub}</div>
            <div className="chips" style={{ marginTop: 6 }}>
              {r.category && <span className="chip"><span className="dot" style={{ background: col }} />{r.category}</span>}
              {(r.tags || []).map(t => <span key={t} className="chip tag">#{t}</span>)}
              {r.needsReview && <span className="chip warn">Check</span>}
              {(r.pages || []).length > 1 && <span className="chip">{r.pages.length} pages</span>}
            </div>
          </div>
        </div>
      );
    }
""" + s[row_end:]
rep("""          {groups.map(g => (
            <div key={g.key}>
              {g.label && <div className="section-h"><span>{g.label}</span><span className="amt">{fmtMoney(g.sum, settings.currency)}</span></div>}
              {g.items.map(r => <ReceiptRow key={r.id} r={r} cats={settings.categories} onOpen={() => onOpen(r)} selectable={selecting} selected={selecting && selected.has(r.id)} />)}
            </div>
          ))}""",
"""          {groups.map(g => (
            <div key={g.key}>
              {g.label && <div className="month"><span className="name">{g.label}</span><span className="sum amt" style={{ fontSize: 14 }}>{fmtMoney(g.sum, settings.currency)}</span></div>}
              <div className="ledger">{g.items.map(r => <ReceiptRow key={r.id} r={r} cats={settings.categories} onOpen={() => onOpen(r)} selectable={selecting} selected={selecting && selected.has(r.id)} />)}</div>
            </div>
          ))}""")
rep("""          <div className="row" style={{ padding: '0 12px 8px', gap: 8 }}>
            <input className="search grow\"""",
"""          {!panel && !n && !q && groups.length > 0 && groups[0].label && (
            <div className="summary">
              <div className="label">{groups[0].label}</div>
              <div className="big">{fmtMoney(groups[0].sum, settings.currency)}</div>
              <div className="meta">{groups[0].items.length} receipt{groups[0].items.length === 1 ? '' : 's'}{receipts.filter(r => r.needsReview).length ? ` · ${receipts.filter(r => r.needsReview).length} to check` : ''}</div>
            </div>
          )}
          <div className="row" style={{ padding: '0 12px 8px', gap: 8 }}>
            <input className="search grow\"""")
rep("""          <div className="total-line"><span>{shown.length} receipt{shown.length === 1 ? '' : 's'} · {sortLabel}""", """          <div className="total-line"><span>{shown.length} receipt{shown.length === 1 ? '' : 's'}, {sortLabel.toLowerCase()}""")

# ---- detail ----
rep("""                <div style={{ fontSize: 20, fontWeight: 600, lineHeight: 1.25 }}>{receipt.items || receipt.merchant || 'Receipt'}</div>""",
    """                <div className="serif" style={{ fontSize: 24, fontWeight: 600, lineHeight: 1.2 }}>{receipt.items || receipt.merchant || 'Receipt'}</div>""")
rep("""              <div style={{ fontSize: 24, fontWeight: 600, whiteSpace: 'nowrap' }} className="amt">{fmtMoney(receipt.total, receipt.currency) || 'No total'}</div>""",
    """              <div style={{ fontSize: 24, whiteSpace: 'nowrap' }} className="amt">{fmtMoney(receipt.total, receipt.currency) || 'No total'}</div>""")
rep("""            <div className="kv" style={{ marginTop: 12 }}>
              <span className="k">GST</span><span>{receipt.gstIncluded ? `Included, ${fmtMoney(gstOf(receipt.total), receipt.currency)}` : 'Not included'}</span>
              {receipt.receiptNo && <><span className="k">Receipt no.</span><span style={{ fontFamily: 'monospace' }}>{receipt.receiptNo}</span></>}
              {receipt.accountNo && <><span className="k">Account no.</span><span style={{ fontFamily: 'monospace' }}>{receipt.accountNo}</span></>}
              {receipt.comments && <><span className="k">Comments</span><span style={{ whiteSpace: 'pre-wrap' }}>{receipt.comments}</span></>}
              <span className="k">Added</span><span>{fmtDate((receipt.createdAt || '').slice(0, 10))}</span>
            </div>""",
"""            <div className="facts">
              <div>{receipt.gstIncluded ? `Includes ${fmtMoney(gstOf(receipt.total), receipt.currency)} GST` : 'No GST'}</div>
              {receipt.receiptNo && <div>Receipt no. <span className="mono">{receipt.receiptNo}</span></div>}
              {receipt.accountNo && <div>Account <span className="mono">{receipt.accountNo}</span></div>}
              {receipt.comments && <div style={{ whiteSpace: 'pre-wrap', color: 'var(--text)' }}>{receipt.comments}</div>}
              <div>Added {fmtDate((receipt.createdAt || '').slice(0, 10))}</div>
            </div>""")

# ---- forms single column ----
rep("""            <div className="row" style={{ alignItems: 'flex-start' }}>
              <div className={'field grow' + (unsure('date') ? ' unsure' : '')}><label>Date</label><DateField value={r.date} onChange={v => set('date', v)} /><Note k="date" /></div>
              <div className={'field' + (unsure('total') ? ' unsure' : '')} style={{ width: 130 }}>""",
"""            <div>
              <div className={'field' + (unsure('date') ? ' unsure' : '')}><label>Date</label><DateField value={r.date} onChange={v => set('date', v)} /><Note k="date" /></div>
              <div className={'field' + (unsure('total') ? ' unsure' : '')}>""")
rep("""            <div className="row">
              <div className="field grow"><label>Receipt or invoice no.</label>""", """            <div>
              <div className="field"><label>Receipt or invoice no.</label>""")

# ---- spacing ----
s = s.replace("padding: '0 12px'", "padding: '0 16px'").replace("padding: '0 12px 12px'", "padding: '0 16px 16px'").replace("padding: '0 12px 20px'", "padding: '0 16px 24px'").replace("padding: '0 12px 8px'", "padding: '0 16px 8px'").replace("padding: '0 12px 6px'", "padding: '0 16px 8px'").replace("padding: '8px 12px'", "padding: '8px 16px'")
s = s.replace("background: 'var(--card)', borderTop: '1px solid var(--line)', padding: '10px 12px calc(10px + var(--safe-b))'", "background: 'var(--surface)', borderTop: '1px solid var(--border)', padding: '12px 16px calc(12px + var(--safe-b))', boxShadow: 'var(--shadow-float)'")
s = s.replace("style={{ height: 6, background: 'var(--line)', borderRadius: 3 }}", "style={{ height: 6, background: 'var(--surface-3)', borderRadius: 3 }}")

open(os.path.join(base, 'receipts-design.html'), 'w', encoding='utf-8').write(s)
print('wrote receipts-design.html')
