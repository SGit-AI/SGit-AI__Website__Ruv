#!/usr/bin/env python3
"""The site version, as sgit.ai does it: one release history (site/admin/versions.json), shown in the nav of every page
and linked to site/admin/versions.html (+ its .md twin). Writes the current version into site/assets/site.js.
Usage: python3 site/build/versions.py   (bump: add a release at the top of versions.json)"""
import html, json, pathlib, re
SITE = pathlib.Path(__file__).resolve().parents[1]
V = json.loads((SITE / 'admin/versions.json').read_text(encoding='utf-8'))
cur = V['releases'][0]['version']
js = SITE / 'assets/site.js'; s = js.read_text(encoding='utf-8')
s2 = re.sub(r"const VERSION = '[^']*';", f"const VERSION = '{cur}';", s)
assert s2 != s or f"const VERSION = '{cur}';" in s, 'site.js has no VERSION constant'
js.write_text(s2, encoding='utf-8')
def link(r):
    if r['commit']: return f'<a href="{V["repo"]}/commit/{r["commit"]}">git {r["commit"]}</a>'
    return f'<a href="{V["repo"]}/commits/{V["branch"]}">this release</a>'
def pages(r):   # no backslashes inside f-string expressions: CI runs Python 3.11
    links = ', '.join('<a href="../%s">%s</a>' % (p, p) for p in r['pages'])
    return '<br><span class="k">Pages: ' + links + '</span>' if r['pages'] else ''
rows = ''.join(f'<tr><td><b>{r["version"]}</b></td><td>{r["date"]}</td><td>{link(r)}</td><td><b>{html.escape(r["title"])}.</b> {html.escape(r["changes"])}{pages(r)}</td></tr>' for r in V['releases'])
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Release history</title>
<meta name="description" content="Every release of ruv.sgit.ai: version, date, commit and changes. The version increments on every push.">
<link rel="canonical" href="https://ruv.sgit.ai/admin/versions.html">
<link rel="alternate" type="text/markdown" href="versions.md">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%230f766e%27/%3E%3Ctext x=%2716%27 y=%2722%27 font-size=%2718%27 text-anchor=%27middle%27 fill=%27white%27 font-family=%27Georgia%27%3Er%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/theme.js"></script>
</head>
<body data-root="../">
<header class="top"><div class="wrap"><a class="brand" href="../index.html">ruv.sgit.ai<small>rUv + sgit</small></a><nav class="main"></nav><button class="theme" aria-label="toggle theme">theme</button></div></header>
<section class="hero"><div class="wrap">
<p class="k"><a href="../index.html">Home</a> / Release history · <a href="versions.md">.md twin</a> · <a href="versions.json">versions.json</a></p>
<h1>Release history</h1>
<p class="lead">The site version (<b>{cur}</b>, shown in the nav of every page) increments on every release, and each release is one push to the <code>{V["branch"]}</code> branch of <a href="{V["repo"]}">SGit-AI/SGit-AI__Website__Ruv</a>. The git log is the authoritative audit trail; this page is the human-readable index of it. The same convention as <a href="https://sgit.ai/admin/versions.html">sgit.ai</a> and <a href="https://newsroom.sgit.ai/admin/versions.html">newsroom.sgit.ai</a>.</p>
</div></section>
<section><div class="wrap"><div class="tbl"><table><thead><tr><th>Version</th><th>Date</th><th>Commit</th><th>Changes</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<footer><div class="wrap"><span>ruv.sgit.ai · {cur}</span><a href="{V["repo"]}">source on GitHub</a><a href="https://sgit.ai">sgit.ai</a><a href="../llms.txt">llms.txt</a></div></footer>
<script src="../assets/site.js"></script>
</body>
</html>
'''
(SITE / 'admin/versions.html').write_text(page, encoding='utf-8')
md = f'# Release history, ruv.sgit.ai\n\n*Source: <https://ruv.sgit.ai/admin/versions.html> · site {cur} · generated from the same file as the page (versions.json), so the two cannot drift.*\n\n{V["note"]}\n\n| Version | Date | Commit | Changes |\n|---|---|---|---|\n'
md += ''.join(f'| {r["version"]} | {r["date"]} | {r["commit"] or "this release"} | **{r["title"]}.** {r["changes"]} |\n' for r in V['releases'])
(SITE / 'admin/versions.md').write_text(md, encoding='utf-8')
print('site version', cur, '·', len(V['releases']), 'releases · admin/versions.html + .md')
