#!/usr/bin/env python3
"""Site gate: every internal link and image resolves, every page has the shared chrome, and nothing shaped like a secret is in the tree.
Exit 1 on any failure. Usage: python3 site/build/validate.py"""
import re, sys, pathlib
SITE = pathlib.Path(__file__).resolve().parents[1]
SECRET = re.compile(r'(sgit_private_vault_[A-Za-z0-9_]{8,}|sk-or-v1-[0-9a-f]{20,}|ghp_[A-Za-z0-9]{20,})')  # the public vault's READ key (sgit_private_read_…) is published on purpose
fails = []
pages = sorted(SITE.glob('*.html')) + [SITE / 'talk' / 'index.html', SITE / 'studio' / 'index.html', SITE / 'admin' / 'versions.html'] + sorted((SITE / 'articles').glob('*.html'))
for p in pages:
    html = p.read_text(encoding='utf-8'); name = p.relative_to(SITE).as_posix()
    for need in ['<nav class="main">', 'assets/site.js', 'assets/site.css', '<link rel="canonical" href="https://ruv.sgit.ai/' + name + '">']:
        if need not in html: fails.append(f'{name}: missing {need}')
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
        t = m.group(1)
        if t.startswith(('http://', 'https://', 'mailto:', 'data:')) or '${' in t: continue
        if not (p.parent / t).exists(): fails.append(f'{name}: broken link {t}')
# the version in the nav is the newest release in the history
import json as _j
_cur = _j.loads((SITE / 'admin' / 'versions.json').read_text())['releases'][0]['version']
if f"const VERSION = '{_cur}';" not in (SITE / 'assets' / 'site.js').read_text(): fails.append(f'site.js VERSION is not {_cur} (run site/build/versions.py)')
# the talk timelines: beats tile the talk, and every file they point at exists
import json
for tj in sorted((SITE / 'talk').glob('talk-*.json')):
    talk = json.loads(tj.read_text(encoding='utf-8')); beats = talk['beats']
    for i, b in enumerate(beats):
        end = beats[i + 1]['at'] if i + 1 < len(beats) else talk['duration_s']
        if b['at'] + b['dur'] != end: fails.append(f'{tj.name}: beat {b["id"]} {b["at"]}+{b["dur"]} != {end}')
        for k in ('src', 'fallback'):
            v = b['slide'].get(k)
            if v and not (tj.parent / v).exists(): fails.append(f'{tj.name}: beat {b["id"]} {k} {v} missing')
    for k, v in talk.get('data', {}).items():
        if not (tj.parent / v).exists(): fails.append(f'{tj.name}: data {k} {v} missing')
for f in SITE.rglob('*'):
    if f.is_file() and f.suffix in {'.html', '.js', '.css', '.json', '.md', '.txt', '.sh', '.py', '.yml'}:
        txt = f.read_text(encoding='utf-8', errors='ignore')
        for m in SECRET.finditer(txt): fails.append(f'{f.relative_to(SITE)}: secret-shaped string {m.group(0)[:12]}…')
print(f'{len(pages)} pages checked')
for x in fails: print('FAIL', x)
sys.exit(1 if fails else 0)
