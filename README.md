# Zed Shortcuts

Static shortcut references generated from Zed's upstream keymaps.

## Build

```powershell
python build_cheatsheet.py
python build_essentials.py
python build_pdfs.py
```

`build_cheatsheet.py` builds the full searchable references for every supported platform:

- `zed-cheatsheet-macos.html`
- `zed-cheatsheet-windows.html`
- `zed-cheatsheet-linux.html`

`build_essentials.py` builds the curated essentials references for every supported platform:

- `zed-essentials-macos.html`
- `zed-essentials-windows.html`
- `zed-essentials-linux.html`

To rebuild one platform:

```powershell
python build_cheatsheet.py --platform windows
python build_essentials.py --platform windows
```

To rebuild one PDF:

```powershell
python build_pdfs.py --only essentials-windows
```

PDF generation requires Chrome, Chromium, or Edge.

## Keymap Sources

Default platform keymaps live under `keymaps/`:

- `default-macos.json`
- `default-windows.json`
- `default-linux.json`
- `vim.json`, shared across platforms

The default keymaps are copied from `zed-industries/zed` under `assets/keymaps/`.

## Expansion Notes

The full cheatsheet path is platform-ready: add or update the platform entry in `build_cheatsheet.py`, place the matching default keymap in `keymaps/`, and rebuild.

The essentials path keeps macOS as the canonical curated list, with explicit Windows and Linux overrides for shortcuts where Zed's platform defaults differ.
