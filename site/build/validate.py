#!/usr/bin/env python3
"""Site gate: every internal link and image resolves, every page has the shared chrome, and nothing shaped like a secret is in the tree.
Exit 1 on any failure. Usage: python3 site/build/validate.py"""
import re, sys, json, pathlib
SITE = pathlib.Path(__file__).resolve().parents[1]
SECRET = re.compile(r'(sgit_private_vault_[A-Za-z0-9_]{8,}|sgit_private_read_[0-9a-f]{16,}|sk-or-v1-[0-9a-f]{20,}|ghp_[A-Za-z0-9]{20,})')  # a READ key declared public (sgit_public_read_…) is published on purpose; a vault key or a private read key never is
fails = []
pages = sorted(SITE.glob('*.html')) + [SITE / 'talk' / 'index.html', SITE / 'studio' / 'index.html', SITE / 'admin' / 'versions.html', SITE / 'ruv-sgit' / 'index.html'] + sorted((SITE / 'business').glob('*.html')) + [SITE / 'shop' / 'index.html', SITE / 'examples' / 'index.html'] + sorted((SITE / 'articles').glob('*.html'))
# the v0.2 areas (next-phase brief): checked as soon as each exists, so a new page gets the same gate as the old ones
pages += [f for d in ('learn', 'proof', 'clients', 'providers', 'rules', 'how-it-works', 'join') for f in sorted((SITE / d).glob('*.html'))]
REFRESH = re.compile(r'<meta\s+http-equiv="refresh"\s+content="[^"]*?url=([^"]+)"', re.I)
CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
def resolve(base, t):
    """An internal URL as a file under site/ (None if external); anchors and queries dropped, a folder means its index.html."""
    t = t.strip().split('#')[0].split('?')[0]
    if t.startswith('https://ruv.sgit.ai/'): f = SITE / t[len('https://ruv.sgit.ai/'):]
    elif t.startswith('/'): f = SITE / t.lstrip('/')
    elif t.startswith(('http://', 'https://', 'mailto:', 'data:')): return None
    else: f = base / t
    f = pathlib.Path(__import__('os').path.normpath(f))
    return f / 'index.html' if f.is_dir() or t.endswith('/') or t == '' else f
for p in pages:
    html = p.read_text(encoding='utf-8'); name = p.relative_to(SITE).as_posix()
    stub = REFRESH.search(html)  # a redirect stub keeps the chrome, but its canonical names the new page (checked below), not itself
    for need in ['<nav class="main">', 'assets/site.js', 'assets/site.css'] + ([] if stub else ['<link rel="canonical" href="https://ruv.sgit.ai/' + name + '">']):
        if need not in html: fails.append(f'{name}: missing {need}')
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
        t = m.group(1)
        if t.startswith(('http://', 'https://', 'mailto:', 'data:')) or '${' in t: continue
        if not (p.parent / t).exists(): fails.append(f'{name}: broken link {t}')
        elif (p.parent / t).is_dir() and not (p.parent / t / 'index.html').exists(): fails.append(f'{name}: broken link {t} (a folder with no index.html)')
# redirect stubs (next-phase brief, "URL changes"): GitHub Pages has no server redirects, so a retired URL keeps a file whose
# refresh, canonical and visible link all reach the same existing page. Every HTML file under site/ is scanned, listed above or not.
for p in sorted(SITE.rglob('*.html')):
    if 'vendor' in p.parts: continue
    html = p.read_text(encoding='utf-8', errors='ignore'); name = p.relative_to(SITE).as_posix()
    m = REFRESH.search(html)
    if not m: continue
    target = resolve(p.parent, m.group(1))
    if target is None: fails.append(f'{name}: stub refresh leaves the site ({m.group(1).strip()})'); continue
    if not target.is_file(): fails.append(f'{name}: stub refresh target {m.group(1).strip()} does not exist'); continue
    c = CANON.search(html)
    if not c: fails.append(f'{name}: stub has no <link rel="canonical">')
    elif resolve(p.parent, c.group(1)) != target: fails.append(f'{name}: stub canonical {c.group(1)} is not its refresh target {m.group(1).strip()}')
    body = html.split('<body', 1)[-1]
    if not any(resolve(p.parent, a) == target for a in re.findall(r'<a\s[^>]*?href="([^"]+)"', body)): fails.append(f'{name}: stub has no visible <a href> to {m.group(1).strip()}')
# the menu and footer links live in site.js, not in any page: they must resolve too
_js = (SITE / 'assets' / 'site.js').read_text(encoding='utf-8')
for t in sorted(set(re.findall(r"\[\s*'([^']+)'\s*,\s*['\"]", _js) + re.findall(r'\$\{root\}([^"`$\s]+)', _js))):
    f = resolve(SITE, t)
    if f is not None and not f.is_file(): fails.append(f'assets/site.js: menu/footer link {t} does not exist')
# old URLs keep working (next-phase brief): every page and menu link in the 16 October inventory still exists, as a page or a stub
_inv = json.loads((SITE / 'data' / 'site-map-2026-10-16.json').read_text(encoding='utf-8'))
for t in sorted({pg['path'] for pg in _inv['pages']} | {h for items in _inv['menu'].values() for h, _ in items}):
    f = resolve(SITE, t)
    if f is not None and not f.is_file(): fails.append(f'site-map-2026-10-16.json: {t} no longer exists (keep it, or leave a redirect stub)')
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
# no vault files in the repository (Dinis, 17 Oct): sealed example vaults live on the sgraph vault server (dev.send.sgraph.ai)
# and the site keeps only the reference (server, vault id, read key, viewer URL, clone command) in data/vaults.json.
if (SITE / 'vaults').exists(): fails.append('site/vaults/ exists: vault files do not belong in the repository; seal pushes them to the vault server')
for f in SITE.rglob('*'):
    if f.is_dir() and f.name in {'.sg_vault', 'bare'} and 'vendor' not in f.parts: fails.append(f'{f.relative_to(SITE)}: a vault store has no place in the site')
for v in json.loads((SITE / 'data' / 'vaults.json').read_text())['vaults']:
    pub = v.get('published')
    if not pub: continue
    if 'path' in pub: fails.append(f"vaults.json {v['run']}: published.path points into the repository")
    if v.get('superseded_by'): continue
    for k in ('server', 'vault_id', 'read_key', 'viewer_url', 'clone'):
        if not pub.get(k): fails.append(f"vaults.json {v['run']}: published.{k} missing")
    if not re.fullmatch(r'sgit_public_read_[0-9a-f]{64}:' + re.escape(str(pub.get('vault_id'))), str(pub.get('read_key'))): fails.append(f"vaults.json {v['run']}: read_key is not sgit_public_read_<hex>:<vault id>")
print(f'{len(pages)} pages checked')
for x in fails: print('FAIL', x)
sys.exit(1 if fails else 0)
