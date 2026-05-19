#!/usr/bin/env python3
"""Generate PDFs from the built Zed shortcut HTML files."""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

PDF_TARGETS = {
    'cheatsheet-macos': ('zed-cheatsheet-macos.html', 'zed-cheatsheet-macos.pdf'),
    'cheatsheet-windows': ('zed-cheatsheet-windows.html', 'zed-cheatsheet-windows.pdf'),
    'cheatsheet-linux': ('zed-cheatsheet-linux.html', 'zed-cheatsheet-linux.pdf'),
    'essentials-macos': ('zed-essentials-macos.html', 'zed-essentials-macos.pdf'),
    'essentials-windows': ('zed-essentials-windows.html', 'zed-essentials-windows.pdf'),
    'essentials-linux': ('zed-essentials-linux.html', 'zed-essentials-linux.pdf'),
}

BROWSER_COMMANDS = [
    'chrome',
    'google-chrome',
    'google-chrome-stable',
    'chromium',
    'chromium-browser',
    'msedge',
    'microsoft-edge',
]

WINDOWS_BROWSER_PATHS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
]

MACOS_BROWSER_PATHS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
]


def find_browser(explicit=None):
    if explicit:
        browser = Path(explicit)
        if browser.exists():
            return str(browser)
        resolved = shutil.which(explicit)
        if resolved:
            return resolved
        raise SystemExit(f'Browser not found: {explicit}')

    for command in BROWSER_COMMANDS:
        resolved = shutil.which(command)
        if resolved:
            return resolved

    for path in WINDOWS_BROWSER_PATHS + MACOS_BROWSER_PATHS:
        if Path(path).exists():
            return path

    raise SystemExit(
        'No Chrome-compatible browser found. Install Chrome, Chromium, or Edge, '
        'or pass --browser /path/to/browser.'
    )


def build_pdf(browser, source, output):
    source_path = HERE / source
    output_path = HERE / output
    if not source_path.exists():
        raise SystemExit(f'Missing HTML source: {source_path}')

    with tempfile.TemporaryDirectory(prefix='zed-shortcuts-pdf-') as user_data_dir:
        command = [
            browser,
            '--headless=new',
            '--disable-gpu',
            '--disable-extensions',
            '--no-first-run',
            '--no-default-browser-check',
            f'--user-data-dir={user_data_dir}',
            f'--print-to-pdf={output_path}',
            '--no-pdf-header-footer',
            source_path.as_uri(),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            fallback = command.copy()
            fallback[fallback.index('--headless=new')] = '--headless'
            result = subprocess.run(fallback, capture_output=True, text=True)
        if result.returncode != 0:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
            raise SystemExit(result.returncode)

    size = output_path.stat().st_size
    print(f'Wrote {output_path} ({size:,} bytes)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--browser',
        help='Chrome, Chromium, or Edge executable to use for PDF printing.',
    )
    parser.add_argument(
        '--only',
        choices=[*PDF_TARGETS.keys(), 'all'],
        default='all',
        help='PDF target to build. Defaults to all.',
    )
    args = parser.parse_args()

    browser = find_browser(args.browser)
    selected = PDF_TARGETS.items()
    if args.only != 'all':
        selected = [(args.only, PDF_TARGETS[args.only])]

    for _, (source, output) in selected:
        build_pdf(browser, source, output)


if __name__ == '__main__':
    main()
