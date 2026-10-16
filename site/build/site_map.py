#!/usr/bin/env python3
"""The site map, as a dated record: version, menu and every page of ruv.sgit.ai, so the site can be diffed before and
after a change. Reads site/assets/site.js (VERSION, NAV) and every .html under site/ (site/vendor excluded).
Usage: python3 site/build/site_map.py [YYYY-MM-DD]   -> site/data/site-map-<date>.json  (default date: today)
Diff two runs:  diff <(jq -S . site/data/site-map-A.json) <(jq -S . site/data/site-map-B.json)"""
import datetime, html, json, pathlib, re, sys
from collections import Counter

SITE = pathlib.Path(__file__).resolve().parents[1]
JS = (SITE / 'assets/site.js').read_text(encoding='utf-8')


def version():
    m = re.search(r"const VERSION = '([^']*)';", JS)
    assert m, 'site.js has no VERSION constant'
    return m.group(1)


def menu():
    """The NAV constant is a JS array of [label, [[href, text], ...]]; its strings are '...' or "...", so it becomes
    JSON by turning single-quoted strings into double-quoted ones and dropping trailing commas."""
    m = re.search(r'const NAV = (\[.*?\n  \]);', JS, re.S)
    assert m, 'site.js has no NAV constant'
    def lit(s):   # one JS string literal, either quote style, as a JSON string
        if s.group(1) is not None: return s.group(0)
        return json.dumps(s.group(2).replace("\\'", "'"))
    src = re.sub(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'', lit, m.group(1))
    src = re.sub(r',\s*([\]}])', r'\1', src)
    return {label: [[h, t] for h, t in items] for label, items in json.loads(src)}


def text(fragment):
    fragment = re.sub(r'<small\b.*?</small>', '', fragment, flags=re.S | re.I)   # subtitles inside h1
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


def kind(path):
    if path.startswith('admin/'): return 'admin'
    if path.startswith('articles/'): return 'page' if path == 'articles/index.html' else 'article'
    if path.startswith('talk/slides/'): return 'slide'
    if path.startswith('talk/'): return 'talk'
    if re.match(r'studio/v\d+/', path) or path.startswith(('ruv-sgit/motion/', 'ruv-sgit/define/')): return 'animation'
    if path.startswith(('ruv-sgit/ledger/', 'ruv-sgit/case/', 'vault/')): return 'data'
    return 'page'


def group_of(path, nav):
    """The menu group that links to this page: an exact href first, then one with a ?query or #anchor stripped."""
    for exact in (True, False):
        for label, items in nav.items():
            for h, _ in items:
                if (h == path) if exact else (re.split(r'[?#]', h)[0] == path): return label
    return None


def pages(nav):
    out = []
    for f in sorted(SITE.rglob('*.html')):
        rel = f.relative_to(SITE).as_posix()
        if rel.startswith('vendor/'): continue
        src = f.read_text(encoding='utf-8')
        body = re.sub(r'<script\b.*?</script>', '', src, flags=re.S | re.I)   # template h1s inside scripts are not the page's
        t = re.search(r'<title>(.*?)</title>', src, re.S | re.I)
        h = re.search(r'<h1\b[^>]*>(.*?)</h1>', body, re.S | re.I)
        out.append({'path': rel, 'title': text(t.group(1)) if t else None, 'h1': text(h.group(1)) if h else None,
                    'group': group_of(rel, nav), 'kind': kind(rel)})
    return out


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    nav = menu(); ps = pages(nav)
    doc = {'version': version(), 'date': date, 'menu': nav, 'pages': ps,
           'counts': dict(sorted(Counter(p['kind'] for p in ps).items())) | {'total': len(ps)}}
    out = SITE / f'data/site-map-{date}.json'
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{out.relative_to(SITE.parent)}: {doc["version"]}, {len(ps)} pages, {doc["counts"]}')


if __name__ == '__main__':
    main()
