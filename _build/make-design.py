"""
Builds receipts-design.html, the design-system variant of the app, from receipts.html. Same logic, same data,
restyled to the neutral visual system (one type family, 12/14/16/20/24 scale, two weights, three text colours,
neutrals plus one accent, 4/8 spacing, radius 8/12, borders not shadows, dark mode, visible focus, reduced motion).
Re-run after any change to receipts.html: python _build/make-design.py
"""
import os, re
base = os.path.join(os.path.dirname(__file__), '..')
src = open(os.path.join(base, 'receipts.html'), encoding='utf-8').read()
s = src

def rep(a, b, count=1):
    global s
    assert a in s, a[:70]; s = s.replace(a, b, count)

STYLE = """  <style>
    /* Design system: neutral visual system, house default. Tokens first, nothing improvised below. */
    :root {
      color-scheme: light dark;
      --surface: #FFFFFF; --surface-2: #F7F7F8; --surface-3: #EFEFF1;
      --text: #1A1A1F; --text-2: #5C5C66; --text-3: #8A8A94;
      --border: #E4E4E8; --border-strong: #D4D4DA;
      --accent: #2563EB; --accent-tint: #EAF0FD; --accent-text: #1D4ED8; --on-accent: #FFFFFF;
      --red: #DC2626; --red-tint: #FDECEC; --green: #16A34A; --green-tint: #E9F7EE; --amber: #B45309; --amber-tint: #FDF3E1;
      --r-control: 8px; --r-card: 12px; --r-pill: 999px;
      --shadow-float: 0 4px 12px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
      --ease-out: cubic-bezier(0.2, 0, 0, 1); --dur: 200ms;
      /* names the logic still uses */
      --bg: var(--surface-2); --card: var(--surface); --ink: var(--text); --muted: var(--text-2); --line: var(--border);
      --navy: var(--accent); --navy-soft: var(--accent-tint); --amber-soft: var(--amber-tint); --green-soft: var(--green-tint); --radius: var(--r-card);
      --safe-b: env(safe-area-inset-bottom, 0px); --safe-t: env(safe-area-inset-top, 0px);
    }
    :root[data-theme="light"] { color-scheme: light; }
    :root[data-theme="dark"], :root:not([data-theme="light"]) .dark-tokens { color-scheme: dark; }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) {
        --surface: #1C1C21; --surface-2: #121215; --surface-3: #26262C;
        --text: #F2F2F4; --text-2: #A9A9B1; --text-3: #7C7C86;
        --border: rgba(255,255,255,0.10); --border-strong: rgba(255,255,255,0.18);
        --accent: #6B96F5; --accent-tint: #1C2A48; --accent-text: #9DB8FA; --on-accent: #0B1220;
        --red: #F87171; --red-tint: #3A1D1D; --green: #4ADE80; --green-tint: #17301F; --amber: #FBBF24; --amber-tint: #3A2E12;
        --shadow-float: 0 4px 16px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4);
      }
    }
    :root[data-theme="dark"] {
      --surface: #1C1C21; --surface-2: #121215; --surface-3: #26262C;
      --text: #F2F2F4; --text-2: #A9A9B1; --text-3: #7C7C86;
      --border: rgba(255,255,255,0.10); --border-strong: rgba(255,255,255,0.18);
      --accent: #6B96F5; --accent-tint: #1C2A48; --accent-text: #9DB8FA; --on-accent: #0B1220;
      --red: #F87171; --red-tint: #3A1D1D; --green: #4ADE80; --green-tint: #17301F; --amber: #FBBF24; --amber-tint: #3A2E12;
      --shadow-float: 0 4px 16px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4);
    }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: -apple-system, "Segoe UI", Roboto, Inter, sans-serif; font-size: 16px; line-height: 1.5; }
    body { min-height: 100vh; }
    button { font: inherit; color: inherit; cursor: pointer; }
    input, select, textarea { font: inherit; color: inherit; }
    :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
    .app { min-height: 100vh; padding-bottom: calc(96px + var(--safe-b)); max-width: 640px; margin: 0 auto; }
    .sheet > * { max-width: 640px; margin-left: auto; margin-right: auto; }
    .topbar { position: sticky; top: 0; z-index: 20; background: var(--bg); padding: calc(12px + var(--safe-t)) 16px 8px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .topbar h1 { font-size: 24px; margin: 0; font-weight: 600; letter-spacing: -0.02em; line-height: 1.2; }
    .fab { position: fixed; right: 16px; bottom: calc(24px + var(--safe-b)); z-index: 31; width: 56px; height: 56px; border-radius: var(--r-pill); background: var(--accent); color: var(--on-accent); border: none; box-shadow: var(--shadow-float); display: flex; align-items: center; justify-content: center; transition: transform var(--dur) var(--ease-out); }
    .fab:active { transform: scale(0.96); }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: var(--r-card); padding: 12px 16px; margin: 0 16px 8px; }
    .row { display: flex; align-items: center; gap: 8px; }
    .grow { flex: 1; min-width: 0; }
    .muted { color: var(--text-2); }
    .small { font-size: 14px; }
    .amt { font-variant-numeric: tabular-nums; font-weight: 600; }
    .chip { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: var(--r-pill); font-size: 12px; line-height: 20px; background: var(--surface-2); color: var(--text-2); border: 1px solid var(--border); white-space: nowrap; }
    .chip .dot { width: 8px; height: 8px; border-radius: 4px; flex-shrink: 0; }
    .chip.tag { background: var(--surface); color: var(--text-2); }
    .chip.warn { background: var(--amber-tint); color: var(--amber); border-color: transparent; }
    .chip.btn { background: var(--surface); border-color: var(--border); color: var(--text); min-height: 32px; padding: 4px 12px; transition: background var(--dur) var(--ease-out); }
    .chip.btn.on { background: var(--accent-tint); color: var(--accent-text); border-color: var(--accent); }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .thumb { width: 48px; height: 64px; object-fit: cover; border-radius: var(--r-control); background: var(--surface-3); border: 1px solid var(--border); flex-shrink: 0; }
    .btn { border: 1px solid var(--border-strong); background: var(--surface); border-radius: var(--r-control); padding: 10px 16px; min-height: 44px; font-weight: 600; font-size: 16px; transition: background var(--dur) var(--ease-out), opacity var(--dur) var(--ease-out); }
    .btn:active { background: var(--surface-2); }
    .btn.primary { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
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
    .section-h { padding: 16px 16px 8px; font-size: 12px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.06em; display: flex; justify-content: space-between; align-items: center; }
    .empty { text-align: center; color: var(--text-2); padding: 64px 24px; font-size: 16px; }
    .search { width: 100%; padding: 10px 12px; min-height: 44px; border-radius: var(--r-control); border: 1px solid var(--border-strong); background: var(--surface); font-size: 16px; }
    .filters { display: flex; gap: 8px; overflow-x: auto; padding: 4px 16px 8px; scrollbar-width: none; }
    .filters::-webkit-scrollbar { display: none; }
    .flabel { font-size: 12px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.06em; align-self: center; min-width: 64px; flex-shrink: 0; }
    .sheet { position: fixed; inset: 0; z-index: 40; background: var(--bg); overflow-y: auto; padding-bottom: calc(24px + var(--safe-b)); }
    .sheet .topbar { background: var(--bg); }
    .pages { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0; }
    .pages img { height: 120px; border-radius: var(--r-control); border: 1px solid var(--border); }
    .pages .add { height: 120px; width: 88px; border-radius: var(--r-control); border: 1px dashed var(--border-strong); background: none; color: var(--text-2); font-size: 14px; }
    .banner { margin: 0 16px 8px; padding: 12px 16px; border-radius: var(--r-card); font-size: 14px; line-height: 1.5; }
    .banner.err { background: var(--red-tint); color: var(--red); }
    .banner.ok { background: var(--green-tint); color: var(--green); }
    .banner.info { background: var(--accent-tint); color: var(--accent-text); }
    .spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
    .spinner.dark { border-color: var(--border-strong); border-top-color: var(--accent); }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes focusPulse { 0% { transform: scale(1.3); opacity: 0; } 30% { opacity: 1; } 100% { transform: scale(1); opacity: 0; } }
    .kv { display: grid; grid-template-columns: 112px 1fr; gap: 8px 12px; font-size: 14px; }
    .kv .k { color: var(--text-2); }
    .total-line { display: flex; justify-content: space-between; align-items: center; padding: 8px 16px; font-size: 14px; color: var(--text-2); }
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

rep("const HAS_DARK = false;", "const HAS_DARK = true;")
# identity of the copy
rep('<title>Receipts</title>', '<title>Receipts design</title>')
rep("<meta name=\"theme-color\" content=\"#1F3A5F\">", "<meta name=\"theme-color\" content=\"#F7F7F8\">")
s = re.sub(r"const BUILD_VERSION = '([^']+)';", lambda m: "const BUILD_VERSION = '%s-design';" % m.group(1), s, count=1)

# type scale: 12 / 14 / 16 / 20 / 24. Map every inline size onto it.
size_map = {'10': '12', '11': '12', '13': '14', '15': '16', '18': '20', '22': '24', '28': '24'}
s = re.sub(r'fontSize: (\d+)\b', lambda m: 'fontSize: ' + size_map.get(m.group(1), m.group(1)), s)
# two weights only
s = s.replace('fontWeight: 700', 'fontWeight: 600').replace('fontWeight: 500', 'fontWeight: 400')
# hard-coded colours to tokens
s = s.replace("'#B23A3A'", "'var(--red)'").replace("#B23A3A", "var(--red)").replace("'#eee'", "'var(--surface-3)'").replace("'#555'", "'var(--text-2)'")
s = s.replace("background: 'rgba(0,0,0,0.5)', color: '#fff', borderRadius: 14", "background: 'rgba(0,0,0,0.5)', color: '#fff', borderRadius: 999")
# category chips: colour as a small dot, not a tinted pill (colour carries meaning, not decoration)
s = s.replace("""<span className="chip" style={{ background: col + '22', color: col }}>{r.category}</span>""", """<span className="chip"><span className="dot" style={{ background: col }} />{r.category}</span>""")
s = s.replace("""<span className="chip" style={{ background: col + '22', color: col }}>{receipt.category}</span>""", """<span className="chip"><span className="dot" style={{ background: col }} />{receipt.category}</span>""")
s = s.replace("""<span className="chip" style={{ background: catColour(c, settings.categories) + '22', color: catColour(c, settings.categories) }}>{c}</span>""", """<span className="chip"><span className="dot" style={{ background: catColour(c, settings.categories) }} />{c}</span>""")
s = re.sub(r"const CATEGORY_COLOURS = \[[^\]]*\];", "const CATEGORY_COLOURS = ['#2563EB', '#16A34A', '#D97706', '#7C3AED', '#DC2626', '#0891B2', '#A16207', '#64748B'];", s, count=1)
# icons: one monochrome set (Lucide outlines), replaces the emoji gear and the text plus
rep("""<button className="btn" style={{ padding: '8px 12px' }} onClick={() => setShowSettings(true)} aria-label="Settings">⚙️</button>""",
    """<button className="btn" style={{ padding: '0 12px', minWidth: 44 }} onClick={() => setShowSettings(true)} aria-label="Settings"><svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></button>""")
rep("""<button className="fab" onClick={() => setCapturing(true)} aria-label="Add receipt">+</button>""",
    """<button className="fab" onClick={() => setCapturing(true)} aria-label="Add receipt"><svg className="icon" style={{ width: 24, height: 24, strokeWidth: 2 }} viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button>""")
rep("""<button type="button" className="btn" style={{ padding: '10px 12px' }} onClick={openPicker} aria-label="Pick a date">📅</button>""",
    """<button type="button" className="btn" style={{ padding: '0 12px', minWidth: 44 }} onClick={openPicker} aria-label="Pick a date"><svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg></button>""")
# a quiet marker so the two builds are told apart at a glance
rep("""<div className="topbar"><h1>Receipts</h1>""", """<div className="topbar"><h1>Receipts <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-3)', letterSpacing: 0, verticalAlign: 'middle' }}>design</span></h1>""")
# list row: 16px title, 14px secondary
s = s.replace("""<div style={{ fontWeight: 600, lineHeight: 1.25 }}>{r.items || r.merchant || 'Receipt'}</div>""", """<div style={{ fontWeight: 600, fontSize: 16, lineHeight: 1.3 }}>{r.items || r.merchant || 'Receipt'}</div>""")
# select-mode bar and inline surfaces
s = s.replace("background: 'var(--card)', borderTop: '1px solid var(--line)', padding: '10px 12px calc(10px + var(--safe-b))'", "background: 'var(--surface)', borderTop: '1px solid var(--border)', padding: '12px 16px calc(12px + var(--safe-b))', boxShadow: 'var(--shadow-float)'")
s = s.replace("style={{ height: 6, background: 'var(--line)', borderRadius: 3 }}", "style={{ height: 6, background: 'var(--surface-3)', borderRadius: 3 }}")
# paddings that were 12 at the edge become 16 (edge padding rule)
s = s.replace("padding: '0 12px'", "padding: '0 16px'").replace("padding: '0 12px 12px'", "padding: '0 16px 12px'").replace("padding: '0 12px 20px'", "padding: '0 16px 20px'").replace("padding: '0 12px 8px'", "padding: '0 16px 8px'").replace("padding: '0 12px 6px'", "padding: '0 16px 6px'").replace("padding: '8px 12px'", "padding: '8px 16px'")

# secondary line on the detail card at 14, placeholder thumb text at 12
s = s.replace("""<div className="muted" style={{ marginTop: 2 }}>{[receipt.items""", """<div className="muted" style={{ marginTop: 2, fontSize: 14 }}>{[receipt.items""")
s = s.replace("""<div className="thumb" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, color: 'var(--muted)' }}>no image</div>""", """<div className="thumb" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, color: 'var(--text-3)' }}>none</div>""")
open(os.path.join(base, 'receipts-design.html'), 'w', encoding='utf-8').write(s)
print('wrote receipts-design.html')
