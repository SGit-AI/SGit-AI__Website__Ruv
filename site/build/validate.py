#!/usr/bin/env python3
"""Site gate: every internal link and image resolves, every page has the shared chrome, and nothing shaped like a secret is in the tree.
Exit 1 on any failure. Usage: python3 site/build/validate.py"""
import re, sys, pathlib
SITE = pathlib.Path(__file__).resolve().parents[1]
SECRET = re.compile(r'(sgit_private_vault_[A-Za-z0-9_]{8,}|sk-or-v1-[0-9a-f]{20,}|ghp_[A-Za-z0-9]{20,})')  # the public vault's READ key (sgit_private_read_…) is published on purpose
fails = []
pages = sorted(SITE.glob('*.html'))
for p in pages:
    html = p.read_text(encoding='utf-8')
    for need in ['<nav class="main">', 'assets/site.js', 'assets/site.css', '<link rel="canonical" href="https://ruv.sgit.ai/' + p.name + '">']:
        if need not in html: fails.append(f'{p.name}: missing {need}')
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
        t = m.group(1)
        if t.startswith(('http://', 'https://', 'mailto:', 'data:')) or '${' in t: continue
        if not (SITE / t).exists(): fails.append(f'{p.name}: broken link {t}')
for f in SITE.rglob('*'):
    if f.is_file() and f.suffix in {'.html', '.js', '.css', '.json', '.md', '.txt', '.sh', '.py', '.yml'}:
        txt = f.read_text(encoding='utf-8', errors='ignore')
        for m in SECRET.finditer(txt): fails.append(f'{f.relative_to(SITE)}: secret-shaped string {m.group(0)[:12]}…')
print(f'{len(pages)} pages checked')
for x in fails: print('FAIL', x)
sys.exit(1 if fails else 0)
