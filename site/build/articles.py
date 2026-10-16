#!/usr/bin/env python3
"""Build the articles section: site/articles/src/<slug>.md  ->  site/articles/<slug>.html + its .md twin, and site/articles/index.html.
Same shape as the sgit newsroom: abstract, byline with version, the article, and a .md twin generated from the same source so the two cannot drift.
A small Markdown subset, no dependencies: headings, paragraphs, lists, tables, fenced code, blockquotes, links, bold, italic, inline code; raw HTML blocks pass through.
Usage: python3 site/build/articles.py"""
import html, json, pathlib, re
SITE = pathlib.Path(__file__).resolve().parents[1]
ART = SITE / 'articles'
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://ruv.sgit.ai/articles/{file}">
<link rel="alternate" type="text/markdown" href="{md}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%230f766e%27/%3E%3Ctext x=%2716%27 y=%2722%27 font-size=%2718%27 text-anchor=%27middle%27 fill=%27white%27 font-family=%27Georgia%27%3Er%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/theme.js"></script>
<style>.article{{max-width:780px}}.article p,.article li{{max-width:none}}.article h2{{margin-top:1.6em}}.abstract{{font-size:18px;border-left:4px solid var(--t);padding:4px 0 4px 16px;margin:18px 0}}.byline{{color:var(--m);font-size:14px}}.article figure{{margin:24px 0}}.article figure img,.article figure svg{{width:100%;height:auto;border-radius:12px;border:1px solid var(--line);background:var(--card)}}.article figcaption{{color:var(--m);font-size:13px;margin-top:6px}}.article blockquote{{margin:16px 0;padding:8px 16px;border-left:4px solid var(--a);background:var(--a2);border-radius:0 10px 10px 0}}.tags span{{display:inline-block;margin-bottom:4px;font-size:12px;padding:2px 8px;border:1px solid var(--line);border-radius:999px;margin-right:6px;color:var(--m)}}</style>
</head>
<body data-root="../">
<header class="top"><div class="wrap"><a class="brand" href="../index.html">ruv.sgit.ai<small>rUv + sgit</small></a><nav class="main"></nav><button class="theme" aria-label="toggle theme">theme</button></div></header>
'''
FOOT = '''<footer><div class="wrap"><span>ruv.sgit.ai · articles</span><a href="https://github.com/SGit-AI/SGit-AI__Website__Ruv">source on GitHub</a><a href="https://newsroom.sgit.ai">newsroom.sgit.ai</a><a href="https://github.com/ruvnet">github.com/ruvnet</a><span>code Apache-2.0 · rUv's projects MIT · "per its README" means we read, not ran, unless a POC says so</span><a href="../llms.txt">llms.txt</a></div></footer>
<script src="../assets/site.js"></script>
</body>
</html>
'''

def inline(s):
    links = []   # a link whose text is a code span, [`x`](url): kept whole, or the code split breaks it
    def keep(m): links.append(f'<a href="{m.group(2)}"><code>{html.escape(m.group(1))}</code></a>'); return f'\x00{len(links) - 1}\x00'
    s = re.sub(r'\[`([^`]+)`\]\(([^)\s]+)\)', keep, s)
    out, parts = [], re.split(r'(`[^`]+`)', s)
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p) > 1: out.append('<code>' + html.escape(p[1:-1]) + '</code>'); continue
        p = html.escape(p, quote=False)
        p = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', p)
        p = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', p)
        p = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', p)
        out.append(p)
    return re.sub(r'\x00(\d+)\x00', lambda m: links[int(m.group(1))], ''.join(out))

def md_to_html(md):
    lines, out, i = md.split('\n'), [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('```'):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith('```'): buf.append(lines[j]); j += 1
            out.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>'); i = j + 1; continue
        if l.startswith('<'):    # raw HTML block, up to a blank line
            buf = []
            while i < len(lines) and lines[i].strip(): buf.append(lines[i]); i += 1
            out.append('\n'.join(buf)); continue
        m = re.match(r'(#{2,4}) (.+)', l)
        if m:
            n = len(m.group(1)); slug = re.sub(r'[^a-z0-9]+', '-', m.group(2).lower()).strip('-')
            out.append(f'<h{n} id="{slug}">{inline(m.group(2))}</h{n}>'); i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'): rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            head, body = rows[0], [r for r in rows[1:] if not re.match(r'^:?-+:?$', r[0] or '-')]
            out.append('<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>' +
                       ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table></div>'); continue
        if l.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('> '): buf.append(lines[i][2:]); i += 1
            out.append('<blockquote><p>' + inline(' '.join(buf)) + '</p></blockquote>'); continue
        if re.match(r'(- |\d+\. )', l):
            tag = 'ol' if l[0].isdigit() else 'ul'; items = []
            while i < len(lines) and re.match(r'(- |\d+\. |  )', lines[i]) and lines[i].strip():
                if lines[i].startswith('  '): items[-1] += ' ' + lines[i].strip()
                else: items.append(re.sub(r'^(- |\d+\. )', '', lines[i]))
                i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'(#{2,4} |```|\||> |- |\d+\. |<)', lines[i]): buf.append(lines[i].strip()); i += 1
        out.append('<p>' + inline(' '.join(buf)) + '</p>')
    return '\n'.join(out)

def front(src):
    m = re.match(r'---\n(.*?)\n---\n', src, re.S); meta = json.loads(m.group(1)); return meta, src[m.end():]

def strip_html_blocks(body):   # the .md twin keeps the text; figures become a link to the page
    return re.sub(r'\n<figure.*?</figure>\n', lambda m: '\n*(Figure: see the HTML version.)*\n', body, flags=re.S)

arts = []
for src in sorted((ART / 'src').glob('*.md')):
    meta, body = front(src.read_text(encoding='utf-8')); slug = src.stem; meta['slug'] = slug; arts.append(meta)
    page = HEAD.format(title=html.escape(meta['title']), desc=html.escape(meta['abstract'][:300], quote=True), file=f'{slug}.html', md=f'{slug}.md')
    page += f'''<section class="hero"><div class="wrap article">
<p class="k"><a href="index.html">Articles</a> · No. {meta['no']}</p>
<h1>{html.escape(meta['title'])}</h1>
<p class="byline">By {meta['author']} · {meta['date']} · article v{meta['version']} · <a href="{slug}.md">.md twin</a></p>
<p class="tags">{' '.join(f'<span>{html.escape(t)}</span>' for t in meta['tags'])}</p>
<p class="abstract"><b>Abstract.</b> {inline(meta['abstract'])}</p>
</div></section>
<section><div class="wrap article">
{md_to_html(body)}
</div></section>
''' + FOOT
    (ART / f'{slug}.html').write_text(page, encoding='utf-8')
    twin = f"# {meta['title']}\n\n*Source: <https://ruv.sgit.ai/articles/{slug}.html> · article v{meta['version']} · generated from the same source as the page, so the two cannot drift.*\n\nBy {meta['author']} · {meta['date']}\n\n**Abstract.** {meta['abstract']}\n\n---\n" + strip_html_blocks(body)
    (ART / f'{slug}.md').write_text(twin, encoding='utf-8')
    print('articles/' + slug, '.html + .md')

arts.sort(key=lambda a: -a['no'])
idx = HEAD.format(title='Articles', desc='Articles from ruv.sgit.ai: plans, briefs and write-ups about sgit vaults and Agent Behaviour Policies inside rUv\'s stack.', file='index.html', md='index.md')
idx += '<section class="hero"><div class="wrap"><h1>Articles</h1><p class="lead">Plans, briefs and write-ups from this site, in the same shape as the <a href="https://newsroom.sgit.ai">sgit newsroom</a>: every article has a <code>.md</code> twin an agent can read.</p></div></section>\n<section><div class="wrap"><div class="cards">'
idx += ''.join(f'<div class="card"><span class="n">No. {a["no"]} · {a["date"]}</span><h3><a href="{a["slug"]}.html">{html.escape(a["title"])}</a></h3><p>{inline(a["abstract"][:260])}…</p><p class="k"><a href="{a["slug"]}.html">Read</a> · <a href="{a["slug"]}.md">.md</a></p></div>' for a in arts)
idx += '</div></div></section>\n' + FOOT
(ART / 'index.html').write_text(idx, encoding='utf-8')
(ART / 'index.md').write_text('# Articles (ruv.sgit.ai)\n\n' + ''.join(f'- [{a["title"]}]({a["slug"]}.md) · No. {a["no"]} · {a["date"]}\n' for a in arts), encoding='utf-8')
print('articles/index.html,', len(arts), 'articles')
