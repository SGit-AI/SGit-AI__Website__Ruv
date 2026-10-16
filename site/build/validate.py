#!/usr/bin/env python3
"""Site gate: every internal link and image resolves, every page has the shared chrome, and nothing shaped like a secret is in the tree.
Exit 1 on any failure. Usage: python3 site/build/validate.py"""
import re, sys, pathlib
SITE = pathlib.Path(__file__).resolve().parents[1]
SECRET = re.compile(r'(sgit_private_vault_[A-Za-z0-9_]{8,}|sgit_private_read_[0-9a-f]{16,}|sk-or-v1-[0-9a-f]{20,}|ghp_[A-Za-z0-9]{20,})')  # a READ key declared public (sgit_public_read_…) is published on purpose; a vault key or a private read key never is
fails = []
pages = sorted(SITE.glob('*.html')) + [SITE / 'talk' / 'index.html', SITE / 'studio' / 'index.html', SITE / 'admin' / 'versions.html', SITE / 'ruv-sgit' / 'index.html'] + sorted((SITE / 'business').glob('*.html')) + [SITE / 'shop' / 'index.html'] + sorted((SITE / 'articles').glob('*.html'))
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
    for b in beats + talk.get('extras', []):
        for k in ('src', 'fallback'):
            v = b['slide'].get(k)
            if v and not (tj.parent / v.split('?')[0]).exists(): fails.append(f'{tj.name}: beat {b["id"]} {k} {v} missing')
    for k, v in talk.get('data', {}).items():
        if not (tj.parent / v).exists(): fails.append(f'{tj.name}: data {k} {v} missing')
for f in SITE.rglob('*'):
    if f.is_file() and f.suffix in {'.html', '.js', '.css', '.json', '.md', '.txt', '.sh', '.py', '.yml'}:
        txt = f.read_text(encoding='utf-8', errors='ignore')
        for m in SECRET.finditer(txt): fails.append(f'{f.relative_to(SITE)}: secret-shaped string {m.group(0)[:12]}…')
# site/vaults/<run>/: sealed example vaults, public on purpose. Each folder may hold only the publish surface
# (index.html, manifest.json, cover.json, its sgit_public_read_ key file) and the ciphertext objects its manifest lists,
# at api/vault/read/<vault id>/bare/…; never a working copy's .sg_vault/local (vault key, token, PEM) or anything else.
import hashlib
VKEY = re.compile(rb'sgit_private_vault_[A-Za-z0-9]')
for vf in sorted(f for f in (SITE / 'vaults').rglob('*') if f.is_file()) if (SITE / 'vaults').exists() else []:
    rel = vf.relative_to(SITE).as_posix()
    if VKEY.search(vf.read_bytes()): fails.append(f'{rel}: holds a vault key (sgit_private_vault_…)')
    if {'local', '.sg_vault'} & set(vf.parts) or vf.name in {'vault_key', 'token', 'base_url'} or vf.suffix in {'.pem', '.key'}:
        fails.append(f'{rel}: a working-copy key file has no place in a published vault')
for vd in sorted(d for d in (SITE / 'vaults').iterdir() if d.is_dir()) if (SITE / 'vaults').exists() else []:
    rel = vd.relative_to(SITE).as_posix()
    try: man = json.loads((vd / 'manifest.json').read_text())
    except Exception as e: fails.append(f'{rel}: no readable manifest.json ({e.__class__.__name__})'); continue
    if man.get('visibility') != 'public': fails.append(f'{rel}: manifest visibility is {man.get("visibility")!r}, not public')
    allowed = {'index.html', 'manifest.json', 'cover.json'} | {x['path'] for x in man.get('plaintext_surface', []) if x['path'].startswith('sgit_public_read_')}
    root = vd / 'api' / 'vault' / 'read' / str(man.get('vault_id'))
    want = {(root / o['file_id']): o['sha256'] for o in man.get('objects', [])}
    for f, h in want.items():
        if not f.exists(): fails.append(f'{rel}: object {f.relative_to(vd)} missing')
        elif hashlib.sha256(f.read_bytes()).hexdigest() != h: fails.append(f'{rel}: object {f.relative_to(vd)} does not match its manifest hash')
    for f in vd.rglob('*'):
        if f.is_file() and f not in want and f.relative_to(vd).as_posix() not in allowed: fails.append(f'{rel}: unexpected file {f.relative_to(vd)}')
print(f'{len(pages)} pages checked')
for x in fails: print('FAIL', x)
sys.exit(1 if fails else 0)
