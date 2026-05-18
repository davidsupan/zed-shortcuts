#!/usr/bin/env python3
"""Generate a single-file Zed shortcuts cheatsheet from Zed's default keymaps."""
import json, re, datetime, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEYMAPS = HERE / 'keymaps'
SOURCES = [
    ('default', KEYMAPS / 'default-macos.json'),
    ('vim', KEYMAPS / 'vim.json'),
]
OUT = HERE / 'zed-cheatsheet.html'

def strip_comments(s):
    out = []
    i = 0
    in_str = False
    esc = False
    while i < len(s):
        c = s[i]
        if in_str:
            out.append(c)
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
            i += 1
        else:
            if c == '"':
                in_str = True; out.append(c); i += 1
            elif c == '/' and i+1 < len(s) and s[i+1] == '/':
                while i < len(s) and s[i] != '\n': i += 1
            elif c == '/' and i+1 < len(s) and s[i+1] == '*':
                i += 2
                while i+1 < len(s) and not (s[i] == '*' and s[i+1] == '/'): i += 1
                i += 2
            else:
                out.append(c); i += 1
    return ''.join(out)

bindings = []
for source, path in SOURCES:
    raw = open(str(path)).read()
    cleaned = strip_comments(raw)
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    data = json.loads(cleaned)
    for section in data:
        ctx = section.get('context', '')
        for keys, action in section.get('bindings', {}).items():
            if isinstance(action, list):
                action_name = action[0]
                args = action[1] if len(action) > 1 else None
            else:
                action_name = action
                args = None
            if action_name is None:
                continue  # null = unbind
            bindings.append({
                'keys': keys,
                'action': action_name,
                'args': args,
                'context': ctx,
                'source': source,
            })

payload = json.dumps(bindings, separators=(',', ':'))
generated = datetime.datetime.utcnow().strftime('%Y-%m-%d')

html_doc = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Zed Shortcuts Cheatsheet</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {
    --bg: #1b1d23;
    --panel: #232730;
    --panel-2: #2a2f3a;
    --text: #e6e8ee;
    --muted: #8b93a7;
    --accent: #7aa2f7;
    --accent-2: #bb9af7;
    --key-bg: #3a4150;
    --key-border: #4a5366;
    --border: #353a47;
    --hi: #f7c873;
  }
  @media (prefers-color-scheme: light) {
    :root {
      --bg: #f6f7fa;
      --panel: #ffffff;
      --panel-2: #eef0f5;
      --text: #1a1d24;
      --muted: #5a6378;
      --accent: #3a5fcd;
      --accent-2: #7a4fcf;
      --key-bg: #e9ecf2;
      --key-border: #c8cdd9;
      --border: #d8dce5;
      --hi: #b07c1a;
    }
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; }
  header { position: sticky; top: 0; z-index: 10; background: var(--bg); border-bottom: 1px solid var(--border); padding: 14px 20px 10px; }
  h1 { margin: 0 0 8px; font-size: 16px; font-weight: 600; letter-spacing: 0.2px; }
  h1 small { color: var(--muted); font-weight: 400; margin-left: 8px; font-size: 12px; }
  .controls { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .search-wrap { position: relative; flex: 1 1 320px; min-width: 220px; }
  #q, #capture-display {
    width: 100%; padding: 9px 12px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--panel); color: var(--text); font-size: 14px; outline: none;
    font-family: inherit;
  }
  #q:focus, #capture-display.active { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(122,162,247,0.15); }
  #capture-display { display: none; min-height: 38px; cursor: text; user-select: none; line-height: 1.4; }
  #capture-display.active { display: block; }
  #capture-display .placeholder { color: var(--muted); }
  .btn {
    padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--panel); color: var(--text); cursor: pointer; font-size: 13px;
    white-space: nowrap;
  }
  .btn:hover { background: var(--panel-2); }
  .btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }
  .btn.ghost { background: transparent; }
  select.btn { appearance: none; padding-right: 24px; background-image: linear-gradient(45deg, transparent 50%, var(--muted) 50%), linear-gradient(135deg, var(--muted) 50%, transparent 50%); background-position: calc(100% - 14px) 50%, calc(100% - 9px) 50%; background-size: 5px 5px; background-repeat: no-repeat; }
  .meta { color: var(--muted); font-size: 12px; padding: 6px 20px 0; }
  .hint { color: var(--muted); font-size: 12px; margin-top: 6px; }
  main { padding: 8px 20px 60px; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    text-align: left; font-weight: 600; font-size: 11px; letter-spacing: 0.6px;
    text-transform: uppercase; color: var(--muted); padding: 10px 10px;
    border-bottom: 1px solid var(--border); position: sticky; top: 96px; background: var(--bg);
  }
  tbody td { padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
  tbody tr:hover { background: var(--panel-2); }
  .keys { white-space: nowrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .keys .seq + .seq::before { content: " "; display: inline-block; width: 6px; }
  .kbd {
    display: inline-block; padding: 2px 7px; margin: 1px 1px; border-radius: 6px;
    background: var(--key-bg); border: 1px solid var(--key-border); border-bottom-width: 2px;
    font-size: 12px; min-width: 18px; text-align: center; color: var(--text);
  }
  .kbd.mod { color: var(--accent-2); }
  .action { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
  .action-pretty { color: var(--text); }
  .action-raw { color: var(--muted); font-size: 11.5px; }
  .ctx { color: var(--muted); font-size: 12px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .global { color: var(--accent); font-style: italic; }
  mark { background: rgba(247, 200, 115, 0.35); color: inherit; border-radius: 3px; padding: 0 1px; }
  .empty { padding: 40px; text-align: center; color: var(--muted); }
  .count { color: var(--muted); font-size: 12px; padding: 6px 20px; }
  .args { color: var(--hi); font-size: 11.5px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .badge { display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 10px; margin-left: 6px; vertical-align: middle; letter-spacing: 0.4px; text-transform: uppercase; }
  .badge.vim { background: rgba(187, 154, 247, 0.18); color: var(--accent-2); border: 1px solid rgba(187, 154, 247, 0.4); }
  footer { color: var(--muted); font-size: 11.5px; padding: 18px 20px 30px; text-align: center; }
  footer a { color: var(--muted); }
  kbd.live {
    display: inline-block; padding: 3px 8px; margin: 1px 2px; border-radius: 6px;
    background: var(--accent); color: #fff; border: 1px solid var(--accent);
    font: 12px ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  .chord-sep { color: var(--muted); margin: 0 4px; }
</style>
</head>
<body>
<header>
  <h1>Zed Shortcuts <small>macOS · default + vim · __COUNT__ bindings · synced __DATE__</small></h1>
  <div class="controls">
    <div class="search-wrap">
      <input id="q" type="text" placeholder="Search by action, key, or context (e.g. 'duplicate line', 'cmd-p', 'editor')" autocomplete="off" autofocus>
      <div id="capture-display" tabindex="0"><span class="placeholder">Press a shortcut… (Esc to clear)</span></div>
    </div>
    <button id="capture-btn" class="btn" title="Toggle key-capture mode">⌨︎ Capture keys</button>
    <select id="src-filter" class="btn" title="Filter by keymap source">
      <option value="">All keymaps</option>
      <option value="default">Default only</option>
      <option value="vim">Vim only</option>
      <option value="no-vim">Hide vim mode</option>
    </select>
    <select id="ctx-filter" class="btn" title="Filter by context">
      <option value="">All contexts</option>
    </select>
    <button id="clear-btn" class="btn ghost" title="Reset filters">Reset</button>
  </div>
  <div class="hint" id="hint">Tip: type to search. Click <b>Capture keys</b> then press a shortcut to look it up.</div>
</header>
<div class="count" id="count"></div>
<main>
  <table>
    <thead>
      <tr><th style="width: 22%">Shortcut</th><th style="width: 38%">Action</th><th style="width: 40%">Context</th></tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>
  <div id="empty" class="empty" hidden>No bindings match.</div>
</main>
<footer>
  Data from <a href="https://github.com/zed-industries/zed/blob/main/assets/keymaps/default-macos.json" target="_blank" rel="noopener">zed/assets/keymaps/default-macos.json</a>.
</footer>

<script id="data" type="application/json">__PAYLOAD__</script>
<script>
(() => {
  const RAW = JSON.parse(document.getElementById('data').textContent);

  // ---------- Key formatting ----------
  const MOD_SYMS = { cmd: '⌘', shift: '⇧', alt: '⌥', ctrl: '⌃', fn: 'fn' };
  const KEY_SYMS = {
    enter: '↩', tab: '⇥', backspace: '⌫', delete: '⌦', escape: '⎋',
    up: '↑', down: '↓', left: '←', right: '→',
    pageup: '⇞', pagedown: '⇟', home: '↖', end: '↘',
    space: '␣',
  };
  const MOD_ORDER = ['ctrl', 'alt', 'shift', 'cmd', 'fn'];

  function parseChord(chord) {
    // returns { mods: Set, key: string }
    const parts = chord.split('-');
    const mods = new Set();
    let key = '';
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      if (i < parts.length - 1 && MOD_SYMS[p]) {
        mods.add(p);
      } else {
        // Handle case where '-' is itself the key: e.g. "cmd--" => parts = ['cmd','','']
        // join the rest as the key (preserving '-' chars)
        key = parts.slice(i).join('-');
        break;
      }
    }
    return { mods, key };
  }

  function chordToHTML(chord) {
    const { mods, key } = parseChord(chord);
    let html = '';
    for (const m of MOD_ORDER) {
      if (mods.has(m)) html += `<span class="kbd mod" title="${m}">${MOD_SYMS[m]}</span>`;
    }
    const keyLabel = KEY_SYMS[key.toLowerCase()] || keyDisplay(key);
    html += `<span class="kbd">${escapeHTML(keyLabel)}</span>`;
    return html;
  }

  function keyDisplay(k) {
    if (k.length === 1) return k.toUpperCase();
    if (/^f\d+$/i.test(k)) return k.toUpperCase();
    return k;
  }

  function keysToHTML(keys) {
    // Multi-chord sequences are space-separated, e.g. "cmd-k cmd-q"
    const chords = keys.split(/\s+/);
    return chords.map(c => `<span class="seq">${chordToHTML(c)}</span>`).join('');
  }

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // ---------- Action humanization ----------
  function humanizeAction(action) {
    const [ns, name] = action.includes('::') ? action.split('::') : ['', action];
    const pretty = (name || '')
      .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
      .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2');
    const nsPretty = ns.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    return nsPretty ? `${nsPretty}: ${pretty}` : pretty;
  }

  // ---------- Build enriched dataset ----------
  const DATA = RAW.map((b, i) => {
    const pretty = humanizeAction(b.action);
    const argsStr = b.args ? JSON.stringify(b.args) : '';
    return {
      ...b,
      id: i,
      pretty,
      argsStr,
      searchBlob: [
        b.keys, b.keys.replace(/-/g, ' '), b.keys.replace(/-/g, ''),
        b.action, pretty, b.context, argsStr, b.source,
      ].join(' ').toLowerCase(),
    };
  });

  // ---------- Populate context filter ----------
  const ctxSel = document.getElementById('ctx-filter');
  const ctxs = [...new Set(DATA.map(d => d.context))].sort((a, b) => {
    if (a === '') return -1; if (b === '') return 1; return a.localeCompare(b);
  });
  for (const c of ctxs) {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c === '' ? '⟨global⟩' : c;
    ctxSel.appendChild(opt);
  }

  // ---------- Rendering ----------
  const rowsEl = document.getElementById('rows');
  const emptyEl = document.getElementById('empty');
  const countEl = document.getElementById('count');

  function highlight(text, terms) {
    if (!terms.length) return escapeHTML(text);
    const safe = escapeHTML(text);
    let out = safe;
    for (const t of terms) {
      if (!t) continue;
      const re = new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig');
      out = out.replace(re, '<mark>$1</mark>');
    }
    return out;
  }

  function render(rows, terms = []) {
    countEl.textContent = `${rows.length} of ${DATA.length} bindings`;
    if (!rows.length) {
      rowsEl.innerHTML = '';
      emptyEl.hidden = false;
      return;
    }
    emptyEl.hidden = true;
    const max = 600; // cap for performance
    const shown = rows.slice(0, max);
    const html = shown.map(r => {
      const ctxHTML = r.context === ''
        ? '<span class="global">⟨global⟩</span>'
        : `<span class="ctx">${highlight(r.context, terms)}</span>`;
      const argsHTML = r.argsStr ? ` <span class="args">${escapeHTML(r.argsStr)}</span>` : '';
      const badgeHTML = r.source === 'vim' ? ' <span class="badge vim">vim</span>' : '';
      return `<tr>
        <td class="keys">${keysToHTML(r.keys)}</td>
        <td class="action">
          <div class="action-pretty">${highlight(r.pretty, terms)}${badgeHTML}${argsHTML}</div>
          <div class="action-raw">${highlight(r.action, terms)}</div>
        </td>
        <td>${ctxHTML}</td>
      </tr>`;
    }).join('');
    rowsEl.innerHTML = html + (rows.length > max ? `<tr><td colspan="3" class="empty">Showing first ${max}. Refine your search to see the rest.</td></tr>` : '');
  }

  // ---------- Filter ----------
  let captureMode = false;
  let capturedKeys = ''; // space-separated chord string, e.g. "cmd-k cmd-q"

  function filter() {
    const q = document.getElementById('q').value.trim().toLowerCase();
    const ctxFilter = ctxSel.value;
    let rows = DATA;
    const terms = [];

    if (captureMode && capturedKeys) {
      const cap = capturedKeys.toLowerCase();
      // Match bindings whose keys *start with* the captured sequence (so partial chords match too)
      rows = rows.filter(d => d.keys.toLowerCase() === cap || d.keys.toLowerCase().startsWith(cap + ' '));
      terms.push(cap);
    } else if (q) {
      const tokens = q.split(/\s+/).filter(Boolean);
      rows = rows.filter(d => tokens.every(t => d.searchBlob.includes(t)));
      terms.push(...tokens);
    }

    if (ctxFilter !== '') {
      rows = rows.filter(d => d.context === ctxFilter);
    } else if (ctxSel.selectedIndex === 0 && ctxFilter === '' && document.getElementById('q').value === '' && !captureMode) {
      // no-op (showing everything)
    }
    render(rows, terms);
  }

  const srcSel = document.getElementById('src-filter');
  function applySrcFilter(rows) {
    const v = srcSel.value;
    if (v === '') return rows;
    if (v === 'no-vim') return rows.filter(d => d.source !== 'vim');
    return rows.filter(d => d.source === v);
  }

  document.getElementById('q').addEventListener('input', () => filter());
  ctxSel.addEventListener('change', () => filter());
  srcSel.addEventListener('change', () => filter());
  document.getElementById('clear-btn').addEventListener('click', () => {
    document.getElementById('q').value = '';
    ctxSel.selectedIndex = 0;
    srcSel.selectedIndex = 0;
    setCaptureMode(false);
    capturedKeys = '';
    filter();
  });

  // ---------- Capture mode ----------
  const captureBtn = document.getElementById('capture-btn');
  const captureDisp = document.getElementById('capture-display');
  const qEl = document.getElementById('q');
  const hintEl = document.getElementById('hint');

  function setCaptureMode(on) {
    captureMode = on;
    captureBtn.classList.toggle('active', on);
    if (on) {
      qEl.style.display = 'none';
      captureDisp.classList.add('active');
      captureDisp.focus();
      hintEl.innerHTML = 'Capture mode: press any shortcut to look it up. Multi-chord (e.g. ⌘K ⌘Q) auto-chains within 1.2s. Esc to clear, click button again to exit.';
      renderCapture();
    } else {
      qEl.style.display = '';
      captureDisp.classList.remove('active');
      hintEl.innerHTML = 'Tip: type to search. Click <b>Capture keys</b> then press a shortcut to look it up.';
      qEl.focus();
    }
    filter();
  }

  captureBtn.addEventListener('click', () => setCaptureMode(!captureMode));

  function renderCapture() {
    if (!capturedKeys) {
      captureDisp.innerHTML = '<span class="placeholder">Press a shortcut…</span>';
      return;
    }
    const chords = capturedKeys.split(/\s+/);
    captureDisp.innerHTML = chords.map((c, i) => {
      const span = `<span>${chordToHTML(c)}</span>`;
      return i === 0 ? span : `<span class="chord-sep">then</span>${span}`;
    }).join('');
  }

  // Map JS KeyboardEvent → Zed key token
  const JS_KEY_MAP = {
    'Escape': 'escape', 'Enter': 'enter', 'Tab': 'tab', 'Backspace': 'backspace',
    'Delete': 'delete', ' ': 'space',
    'ArrowUp': 'up', 'ArrowDown': 'down', 'ArrowLeft': 'left', 'ArrowRight': 'right',
    'PageUp': 'pageup', 'PageDown': 'pagedown', 'Home': 'home', 'End': 'end',
  };

  function eventToChord(e) {
    // Modifiers
    const mods = [];
    if (e.ctrlKey) mods.push('ctrl');
    if (e.altKey) mods.push('alt');
    if (e.shiftKey) mods.push('shift');
    if (e.metaKey) mods.push('cmd');
    // Key
    let k = JS_KEY_MAP[e.key];
    if (!k) {
      if (/^F\d{1,2}$/.test(e.key)) k = e.key.toLowerCase();
      else if (e.key.length === 1) k = e.key.toLowerCase();
      else k = e.key.toLowerCase();
    }
    // If only-modifier press, ignore
    if (['control','shift','alt','meta','capslock'].includes(k)) return null;
    // Order: ctrl-alt-shift-cmd-key  (matches Zed's canonical-ish order; we'll match on both orders below)
    return [...mods, k].join('-');
  }

  // Normalize a chord to a canonical form for comparison (alphabetize mods, keep key last)
  function canonicalChord(chord) {
    const parts = chord.split('-');
    // last token (or last empty due to literal '-') = key; rest = mods
    // handle "cmd--" => key is "-"
    let modSet = new Set();
    let i = 0;
    while (i < parts.length - 1 && MOD_SYMS[parts[i]]) {
      modSet.add(parts[i]); i++;
    }
    const key = parts.slice(i).join('-') || '-';
    const sortedMods = MOD_ORDER.filter(m => modSet.has(m));
    return [...sortedMods, key.toLowerCase()].join('-');
  }
  function canonicalSeq(seq) {
    return seq.split(/\s+/).map(canonicalChord).join(' ');
  }

  // Override `filter` to use canonical match in capture mode
  const origFilter = filter;
  filter = function() {
    const ctxFilter = ctxSel.value;
    let rows = DATA;
    const terms = [];

    if (captureMode && capturedKeys) {
      const cap = canonicalSeq(capturedKeys);
      rows = rows.filter(d => {
        const cd = canonicalSeq(d.keys);
        return cd === cap || cd.startsWith(cap + ' ');
      });
      terms.push(...capturedKeys.split(/\s+/));
    } else {
      const q = qEl.value.trim().toLowerCase();
      if (q) {
        const tokens = q.split(/\s+/).filter(Boolean);
        rows = rows.filter(d => tokens.every(t => d.searchBlob.includes(t)));
        terms.push(...tokens);
      }
    }
    if (ctxFilter !== '') rows = rows.filter(d => d.context === ctxFilter);
    rows = applySrcFilter(rows);
    render(rows, terms);
  };

  let chordTimer = null;
  function recordChord(chord) {
    if (chordTimer) clearTimeout(chordTimer);
    if (!capturedKeys) {
      capturedKeys = chord;
    } else {
      capturedKeys = capturedKeys + ' ' + chord;
    }
    renderCapture();
    filter();
    // After 1.2s, finalize: next key press starts fresh
    chordTimer = setTimeout(() => { chordTimer = null; }, 1200);
  }

  function captureKeydown(e) {
    if (!captureMode) return;
    // Allow tabbing out
    if (e.key === 'Tab' && !e.ctrlKey && !e.metaKey && !e.altKey) return;
    // Esc clears
    if (e.key === 'Escape' && !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey) {
      e.preventDefault();
      capturedKeys = '';
      if (chordTimer) { clearTimeout(chordTimer); chordTimer = null; }
      renderCapture();
      filter();
      return;
    }
    const chord = eventToChord(e);
    if (!chord) return;
    e.preventDefault();
    // If the previous chord finalized (timer expired), start fresh
    if (!chordTimer && capturedKeys) capturedKeys = '';
    recordChord(chord);
  }

  document.addEventListener('keydown', captureKeydown, true);

  // Clicking capture display re-focuses it
  captureDisp.addEventListener('click', () => captureDisp.focus());

  // Initial render
  filter();
})();
</script>
</body>
</html>
"""

html_doc = html_doc.replace('__COUNT__', str(len(bindings)))
html_doc = html_doc.replace('__DATE__', generated)
html_doc = html_doc.replace('__PAYLOAD__', payload)

OUT.write_text(html_doc)
print(f"Wrote {OUT} ({len(html_doc):,} bytes, {len(bindings)} bindings)")
