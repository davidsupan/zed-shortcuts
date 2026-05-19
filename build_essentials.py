#!/usr/bin/env python3
"""Build curated Zed essentials cheatsheets for each supported platform."""
import argparse
import datetime
import html as html_lib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLATFORMS = {
    'macos': {
        'label': 'macOS',
        'output': 'zed-essentials-macos.html',
        'cheatsheet': 'zed-cheatsheet-macos.html',
        'mod_symbols': {'cmd': '⌘', 'shift': '⇧', 'alt': '⌥', 'ctrl': '⌃', 'fn': 'fn'},
    },
    'windows': {
        'label': 'Windows',
        'output': 'zed-essentials-windows.html',
        'cheatsheet': 'zed-cheatsheet-windows.html',
        'mod_symbols': {'cmd': 'Win', 'shift': 'Shift', 'alt': 'Alt', 'ctrl': 'Ctrl', 'fn': 'Fn'},
    },
    'linux': {
        'label': 'Linux',
        'output': 'zed-essentials-linux.html',
        'cheatsheet': 'zed-cheatsheet-linux.html',
        'mod_symbols': {'cmd': 'Super', 'shift': 'Shift', 'alt': 'Alt', 'ctrl': 'Ctrl', 'fn': 'Fn'},
    },
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '--platform',
    choices=[*PLATFORMS.keys(), 'all'],
    default='all',
    help='Platform to build. Defaults to all essentials sheets.',
)
args = parser.parse_args()
if args.platform == 'all':
    for platform_id in PLATFORMS:
        subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), '--platform', platform_id],
            check=True,
        )
    raise SystemExit(0)

PLATFORM_ID = args.platform
PLATFORM = PLATFORMS[PLATFORM_ID]
OUT = HERE / PLATFORM['output']

# Each entry: (keys, label, note_or_empty)
# 'keys' uses the same Zed token format so the renderer formats it consistently.
SECTIONS = [
    ("Files & Workspace", [
        ("cmd-p",        "Open file (fuzzy file finder)", ""),
        ("cmd-shift-p",  "Command palette", "your universal escape hatch — fuzzy search every action"),
        ("cmd-n",        "New file", ""),
        ("cmd-o",        "Open file/folder", ""),
        ("alt-cmd-o",    "Open recent project", ""),
        ("cmd-s",        "Save", ""),
        ("cmd-alt-s",    "Save all", ""),
        ("cmd-w",        "Close tab", ""),
        ("cmd-shift-t",  "Reopen closed tab", ""),
        ("ctrl-tab",     "Next tab (tab switcher)", ""),
        ("ctrl-shift-tab","Previous tab", ""),
        ("cmd-,",        "Open settings", ""),
        ("cmd-k cmd-s",  "Open keymap", ""),
    ]),
    ("Panels & Splits", [
        ("cmd-b",        "Toggle left dock (project panel)", ""),
        ("cmd-r",        "Toggle right dock", ""),
        ("cmd-j",        "Toggle bottom dock (terminal)", ""),
        ("cmd-shift-e",  "Focus project panel", ""),
        ("cmd-shift-b",  "Focus outline panel", ""),
        ("ctrl-`",       "New terminal", "(literal: ctrl-~ in keymap)"),
        ("cmd-\\",        "Split editor right", ""),
        ("cmd-k cmd-left", "Focus pane left", ""),
        ("cmd-k cmd-right","Focus pane right", ""),
        ("ctrl-shift-pageup",   "Swap tab left", ""),
        ("ctrl-shift-pagedown", "Swap tab right", ""),
        ("shift-escape", "Toggle editor zoom (maximize pane)", ""),
    ]),
    ("Code Navigation (LSP)", [
        ("f12",          "Go to definition", ""),
        ("shift-f12",    "Go to implementation", ""),
        ("alt-shift-f12","Find all references", ""),
        ("ctrl--",       "Go back (navigation history)", ""),
        ("ctrl-_",       "Go forward", ""),
        ("cmd-shift-o",  "Go to symbol in file (outline)", ""),
        ("ctrl-g",       "Go to line", ""),
        ("cmd-k cmd-i",  "Hover (show symbol info)", ""),
        ("cmd-i",        "Signature help (in editor)", ""),
    ]),
    ("Editing", [
        ("f2",           "Rename symbol", ""),
        ("cmd-.",        "Code actions / quick fix", ""),
        ("cmd-shift-i",  "Format document", ""),
        ("cmd-/",        "Toggle line comment", ""),
        ("alt-up",       "Move line up", ""),
        ("alt-down",     "Move line down", ""),
        ("alt-shift-down","Duplicate line down", ""),
        ("alt-tab",      "Accept edit prediction (Zeta) / show next", "yes, Alt+Tab — overrides OS app switcher in editor"),
        ("ctrl-cmd-right","Accept next word of prediction", ""),
        ("ctrl-cmd-down","Accept next line of prediction", ""),
    ]),
    ("Multi-cursor & Selection", [
        ("cmd-d",        "Select next occurrence of word", "press repeatedly to add cursors"),
        ("cmd-shift-l",  "Select all occurrences", ""),
        ("cmd-alt-up",   "Add cursor above", ""),
        ("cmd-alt-down", "Add cursor below", ""),
        ("ctrl-shift-right","Expand selection to larger syntax node", "tree-sitter aware — grows by AST"),
        ("ctrl-shift-left", "Shrink selection to smaller syntax node", ""),
    ]),
    ("Find & Search", [
        ("cmd-f",        "Find in current buffer", ""),
        ("cmd-shift-f",  "Find in project", ""),
        ("cmd-alt-shift-f","New search in folder (from project panel)", ""),
    ]),
    ("Git", [
        ("cmd-f8",       "Go to next hunk", ""),
        ("cmd-shift-f8", "Go to previous hunk", ""),
        ("cmd-shift-backspace", "Go to previous change", ""),
        ("cmd-k cmd-b",  "Show git blame for line (hover)", ""),
        ("cmd-ctrl-b",   "Open recent branches", ""),
    ]),
    ("AI / Agent", [
        ("cmd-?",        "Toggle agent panel", ""),
        ("ctrl-enter",   "Inline assist (rewrite/explain selection)", ""),
        ("cmd->",        "Add selection to agent thread", ""),
        ("cmd-n",        "New thread (when in agent panel)", ""),
    ]),
]

PLATFORM_KEY_OVERRIDES = {
    'windows': {
        "Open file/folder": "ctrl-k ctrl-o",
        "Open recent project": "ctrl-r",
        "Save all": "ctrl-k s",
        "Toggle right dock": "ctrl-alt-b",
        "Go to implementation": "ctrl-f12",
        "Go forward": "alt-right",
        "Format document": "shift-alt-f",
        "Accept edit prediction (Zeta) / show next": "alt-]",
        "Accept next word of prediction": "alt-k",
        "Accept next line of prediction": "alt-j",
        "Expand selection to larger syntax node": "shift-alt-right",
        "Shrink selection to smaller syntax node": "shift-alt-left",
        "New search in folder (from project panel)": "ctrl-k ctrl-shift-f",
        "Open recent branches": "shift-alt-b",
        "Toggle agent panel": "ctrl-shift-/",
        "Add selection to agent thread": "ctrl-shift-.",
    },
    'linux': {
        "Open file/folder": "ctrl-k ctrl-o",
        "Open recent project": "ctrl-r",
        "Toggle right dock": "ctrl-alt-b",
        "Go forward": "ctrl-alt-_",
        "Accept edit prediction (Zeta) / show next": "alt-]",
        "Accept next word of prediction": "alt-k",
        "Accept next line of prediction": "alt-j",
        "Add cursor above": "shift-alt-up",
        "Add cursor below": "shift-alt-down",
        "Expand selection to larger syntax node": "alt-shift-right",
        "Shrink selection to smaller syntax node": "alt-shift-left",
        "Open recent branches": "alt-ctrl-shift-b",
    },
}

PLATFORM_NOTE_OVERRIDES = {
    'windows': {
        "Accept edit prediction (Zeta) / show next": "uses Alt+] on Windows to avoid the OS app switcher",
    },
    'linux': {
        "Accept edit prediction (Zeta) / show next": "uses Alt+] on Linux to avoid common window manager shortcuts",
    },
}

# Vim section: most useful default-vim bindings. These are part of Zed's vim mode and
# only fire when vim mode is enabled.
VIM_SECTIONS = [
    ("Vim · Movement (normal mode)", [
        ("h j k l",      "Left / Down / Up / Right", ""),
        ("w",            "Next word start", ""),
        ("b",            "Previous word start", ""),
        ("e",            "Next word end", ""),
        ("0",            "Beginning of line", ""),
        ("^",            "First non-whitespace of line", ""),
        ("$",            "End of line", ""),
        ("g g",          "Top of file", ""),
        ("shift-g",      "Bottom of file (G)", ""),
        ("{",            "Previous paragraph", ""),
        ("}",            "Next paragraph", ""),
        ("%",            "Matching bracket", ""),
        ("ctrl-d",       "Half page down", ""),
        ("ctrl-u",       "Half page up", ""),
        ("z z",          "Center cursor on screen", ""),
    ]),
    ("Vim · Modes", [
        ("i",            "Insert before cursor", ""),
        ("a",            "Insert after cursor (append)", ""),
        ("shift-i",      "Insert at start of line (I)", ""),
        ("shift-a",      "Insert at end of line (A)", ""),
        ("o",            "Open new line below", ""),
        ("shift-o",      "Open new line above (O)", ""),
        ("v",            "Visual (character) mode", ""),
        ("shift-v",      "Visual line mode (V)", ""),
        ("ctrl-v",       "Visual block mode", ""),
        ("escape",       "Back to normal mode", ""),
        (":",            "Command palette (in vim normal)", "Zed maps : to the command palette"),
    ]),
    ("Vim · Editing", [
        ("x",            "Delete character under cursor", ""),
        ("d d",          "Delete (cut) line", ""),
        ("d w",          "Delete to next word", ""),
        ("c c",          "Change line (delete + insert)", ""),
        ("c w",          "Change to next word", ""),
        ("y y",          "Yank (copy) line", ""),
        ("p",            "Paste after cursor", ""),
        ("shift-p",      "Paste before cursor (P)", ""),
        ("u",            "Undo", ""),
        ("ctrl-r",       "Redo", ""),
        (".",            "Repeat last change", ""),
        (">",            "Indent (in visual) — operator in normal", ""),
        ("<",            "Outdent", ""),
        ("g u u",        "Lowercase line", ""),
        ("g shift-u shift-u", "Uppercase line", ""),
    ]),
    ("Vim · Search & Replace", [
        ("/",            "Search forward", ""),
        ("?",            "Search backward", ""),
        ("n",            "Next match", ""),
        ("shift-n",      "Previous match (N)", ""),
        ("*",            "Search word under cursor (forward)", ""),
        ("#",            "Search word under cursor (backward)", ""),
    ]),
    ("Vim · LSP & Code Intelligence", [
        ("g d",          "Go to definition", ""),
        ("g r r",        "Find all references", "Zed's grr — references"),
        ("g r n",        "Rename symbol", "grn — rename"),
        ("g r a",        "Code actions", "gra — actions"),
        ("g r i",        "Go to implementation", "gri — implementation"),
        ("g s",          "Symbol outline", ""),
        ("g a",          "Select all matches of word", ""),
        ("shift-k",      "Hover (show symbol info)", ""),
        ("[ c",          "Previous hunk", ""),
        ("] c",          "Next hunk", ""),
        ("[ d",          "Previous diagnostic", ""),
        ("] d",          "Next diagnostic", ""),
        ("ctrl-o",       "Jump back (navigation)", ""),
        ("ctrl-i",       "Jump forward", ""),
    ]),
    ("Vim · Windows / Panes", [
        ("ctrl-w v",     "Split right (vertical split)", ""),
        ("ctrl-w s",     "Split down (horizontal split)", ""),
        ("ctrl-w h",     "Focus pane left", ""),
        ("ctrl-w l",     "Focus pane right", ""),
        ("ctrl-w j",     "Focus pane below", ""),
        ("ctrl-w k",     "Focus pane above", ""),
        ("ctrl-w o",     "Close other panes (only this one)", ""),
        ("shift-z shift-z", "Save & close (ZZ)", ""),
        ("shift-z shift-q", "Close without saving (ZQ)", ""),
    ]),
]

def fallback_platform_keys(keys):
    if PLATFORM_ID == 'macos':
        return keys
    tokens = []
    for chord in keys.split():
        parts = ['ctrl' if part == 'cmd' else part for part in chord.split('-')]
        deduped = []
        for part in parts:
            if part not in deduped:
                deduped.append(part)
        tokens.append('-'.join(deduped))
    return ' '.join(tokens)


def platform_sections(sections):
    key_overrides = PLATFORM_KEY_OVERRIDES.get(PLATFORM_ID, {})
    note_overrides = PLATFORM_NOTE_OVERRIDES.get(PLATFORM_ID, {})
    translated = []
    for title, rows in sections:
        translated_rows = []
        for keys, label, note in rows:
            platform_keys = key_overrides.get(label, fallback_platform_keys(keys))
            platform_note = note_overrides.get(label, note)
            translated_rows.append((platform_keys, label, platform_note))
        translated.append((title, translated_rows))
    return translated


PLATFORM_SECTIONS = platform_sections(SECTIONS)
ALL = PLATFORM_SECTIONS + VIM_SECTIONS

# --- Renderer ---
MOD_SYMS = PLATFORM['mod_symbols']
KEY_SYMS = {
    'enter':'↩','tab':'⇥','backspace':'⌫','delete':'⌦','escape':'⎋',
    'up':'↑','down':'↓','left':'←','right':'→',
    'pageup':'⇞','pagedown':'⇟','home':'↖','end':'↘','space':'␣',
}
MOD_ORDER = ['ctrl','alt','shift','cmd','fn']

def parse_chord(chord):
    parts = chord.split('-')
    mods = []
    i = 0
    while i < len(parts) - 1 and parts[i] in MOD_SYMS:
        mods.append(parts[i]); i += 1
    key = '-'.join(parts[i:]) or '-'
    return mods, key

def chord_html(chord):
    mods, key = parse_chord(chord)
    out = []
    for m in MOD_ORDER:
        if m in mods:
            out.append(f'<span class="kbd mod" title="{m}">{MOD_SYMS[m]}</span>')
    if key.lower() in KEY_SYMS:
        label = KEY_SYMS[key.lower()]
    elif len(key) == 1:
        label = key.upper()
    elif key.lower().startswith('f') and key[1:].isdigit():
        label = key.upper()
    else:
        label = key
    out.append(f'<span class="kbd">{html_lib.escape(label)}</span>')
    return ''.join(out)

def keys_html(keys):
    chords = keys.split()
    return '<span class="chord-group">' + ''.join(
        (f'<span class="seq">{chord_html(c)}</span>' if i==0
         else f'<span class="seq-sep">then</span><span class="seq">{chord_html(c)}</span>')
        for i, c in enumerate(chords)
    ) + '</span>'

def section_html(title, rows, is_vim=False):
    lis = []
    for keys, label, note in rows:
        note_html = f'<span class="note">{html_lib.escape(note)}</span>' if note else ''
        lis.append(f'''
        <div class="row">
          <div class="kcell">{keys_html(keys)}</div>
          <div class="dcell"><span class="label">{html_lib.escape(label)}</span>{note_html}</div>
        </div>''')
    cls = 'section vim' if is_vim else 'section'
    return f'''<section class="{cls}">
      <h2>{html_lib.escape(title)}</h2>
      <div class="rows">{''.join(lis)}</div>
    </section>'''

generated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')

body_sections = ''.join(section_html(t, r, is_vim=False) for t, r in PLATFORM_SECTIONS)
body_sections += '<div class="vim-divider"><span>Vim mode</span></div>'
body_sections += ''.join(section_html(t, r, is_vim=True) for t, r in VIM_SECTIONS)

total = sum(len(r) for _, r in ALL)

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Zed Essentials — Shortcuts to Remember</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{
    --bg: #1b1d23;
    --panel: #232730;
    --text: #e6e8ee;
    --muted: #8b93a7;
    --accent: #7aa2f7;
    --accent-2: #bb9af7;
    --key-bg: #3a4150;
    --key-border: #4a5366;
    --border: #353a47;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #fafbfd;
      --panel: #ffffff;
      --text: #1a1d24;
      --muted: #5a6378;
      --accent: #3a5fcd;
      --accent-2: #7a4fcf;
      --key-bg: #eef0f5;
      --key-border: #c8cdd9;
      --border: #e1e4eb;
    }}
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text);
    font: 13.5px/1.5 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; }}
  header {{ padding: 20px 28px 4px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; font-weight: 700; }}
  header p {{ color: var(--muted); margin: 0 0 4px; font-size: 12.5px; }}
  header a {{ color: var(--muted); }}
  main {{
    padding: 12px 24px 30px;
    columns: 360px 3;
    column-gap: 22px;
  }}
  .section {{
    break-inside: avoid;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px 10px;
    margin: 0 0 14px;
  }}
  .section.vim {{ border-left: 3px solid var(--accent-2); }}
  .section h2 {{
    margin: 0 0 8px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--accent);
    font-weight: 700;
  }}
  .section.vim h2 {{ color: var(--accent-2); }}
  .row {{ display: flex; gap: 10px; padding: 4px 0; align-items: baseline; border-top: 1px dashed transparent; }}
  .row + .row {{ border-top-color: var(--border); }}
  .kcell {{ flex: 0 0 auto; min-width: 110px; white-space: nowrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .dcell {{ flex: 1 1 auto; }}
  .label {{ color: var(--text); }}
  .note {{ display: block; color: var(--muted); font-size: 11.5px; margin-top: 1px; line-height: 1.35; }}
  .kbd {{
    display: inline-block; padding: 1px 6px; margin: 1px 1px; border-radius: 5px;
    background: var(--key-bg); border: 1px solid var(--key-border); border-bottom-width: 2px;
    font: 11.5px ui-monospace, SFMono-Regular, Menlo, monospace;
    min-width: 16px; text-align: center;
  }}
  .kbd.mod {{ color: var(--accent-2); }}
  .seq + .seq-sep {{ color: var(--muted); font-size: 10.5px; margin: 0 4px; }}
  .seq-sep + .seq {{ }}
  .vim-divider {{
    column-span: all;
    text-align: center;
    margin: 6px 0 14px;
    color: var(--accent-2);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
  }}
  .vim-divider span {{
    display: inline-block;
    padding: 0 14px;
    position: relative;
  }}
  .vim-divider span::before, .vim-divider span::after {{
    content: '';
    position: absolute;
    top: 50%;
    width: 80px;
    height: 1px;
    background: var(--border);
  }}
  .vim-divider span::before {{ right: 100%; }}
  .vim-divider span::after {{ left: 100%; }}
  footer {{ padding: 6px 28px 28px; color: var(--muted); font-size: 11.5px; text-align: center; }}
  @media print {{
    @page {{ size: Letter landscape; margin: 0.35in 0.35in 0.3in; }}
    html, body {{ background: #fff; color: #000; font-size: 9.5px; line-height: 1.32; }}
    header {{ padding: 0 0 4px; }}
    header h1 {{ font-size: 14px; margin: 0; }}
    header p {{ font-size: 9px; margin: 0; }}
    header p:nth-of-type(2) {{ display: none; }}
    main {{ columns: 3; column-gap: 12px; padding: 0; }}
    .section {{
      break-inside: avoid;
      border: 1px solid #bcbcbc;
      border-radius: 6px;
      padding: 5px 8px 4px;
      margin: 0 0 6px;
      background: #fff;
    }}
    .section.vim {{ border-left: 2px solid #555; }}
    .section h2 {{ font-size: 9px; margin: 0 0 3px; color: #000; letter-spacing: 0.5px; }}
    .section.vim h2 {{ color: #000; }}
    .row {{ padding: 1px 0; gap: 6px; }}
    .row + .row {{ border-top-color: #e0e0e0; }}
    .kcell {{ min-width: 78px; }}
    .note {{ font-size: 8.5px; margin-top: 0; line-height: 1.25; color: #555; }}
    .label {{ color: #000; }}
    .kbd {{
      background: #f3f3f3; border-color: #888; color: #000;
      font-size: 9px; padding: 0 4px; border-bottom-width: 1px;
      min-width: 12px; margin: 0 0.5px;
    }}
    .kbd.mod {{ color: #000; }}
    .seq + .seq-sep {{ font-size: 8px; margin: 0 2px; color: #777; }}
    .vim-divider {{
      break-before: page;
      column-span: all;
      margin: 0 0 6px;
      color: #000;
      font-size: 9px;
    }}
    .vim-divider span {{ padding: 0 8px; }}
    .vim-divider span::before, .vim-divider span::after {{
      width: 60px; background: #999;
    }}
    footer {{ display: none; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Zed Essentials</h1>
  <p>Curated shortcuts worth memorizing · {PLATFORM['label']} · {total} entries · synced {generated}</p>
  <p>Full searchable reference: <a href="{PLATFORM['cheatsheet']}">{PLATFORM['cheatsheet']}</a></p>
</header>
<main>
{body_sections}
</main>
<footer>Source: <a href="https://github.com/zed-industries/zed/tree/main/assets/keymaps">zed-industries/zed · assets/keymaps</a></footer>
</body>
</html>
"""

OUT.write_text(doc, encoding='utf-8')
print(f"Wrote {OUT} ({len(doc):,} bytes, {total} entries)")
