// ruv.sgit.ai: nav, theme, Mermaid, markdown includes, POC data tables. No build step needed for these.
(() => {
  const VERSION = 'v0.1.10';   // written by site/build/versions.py from admin/versions.json
  // four groups instead of eleven links (the same shape as sgit.ai: brand, version, grouped menus, a Menu button on phones)
  const NAV = [
    ['Tonight', [['talk/index.html', "Tonight's talk"], ['talk/player.html?talk=talk-10.json', 'Present (10 min)'], ['demo.html', 'The five-minute demo script']]],
    ['The idea', [['index.html', 'Overview'], ['ruv-stack.html', "rUv's stack"], ['use-cases.html', 'Use cases'], ['architecture.html', 'Architecture']]],
    ['Proofs', [['ruv-sgit/index.html', 'ruv.sgit runs and vaults'], ['pocs.html', 'The six POCs'], ['app/index.html', 'Live app'], ['studio/index.html', 'The studio'], ['replicate.html', 'Replicate']]],
    ['Work with us', [['business/index.html', 'Overview'], ['business/consultants.html', 'For consultants'], ['business/companies.html', 'For companies'], ['business/teams.html', 'For internal teams'], ['shop/index.html', 'The shop'], ['articles/ruv-sgit-business-model.html', 'The business model'], ['mailto:agent@riskmandate.ai', 'Contact: agent@riskmandate.ai']]],
    ['Articles', [['articles/index.html', 'All articles'], ['articles/the-studio.html', 'The studio: plan'], ['articles/studio-setup-brief.html', 'Set it up: the brief']]],
  ];
  const root = document.body.dataset.root ?? '';
  const segs = location.pathname.split('/'), file = segs.pop() || 'index.html';
  const here = root ? `${segs.pop()}/${file}` : file;   // pages in a subfolder (talk/) set data-root="../"
  const nav = document.querySelector('nav.main'), brand = document.querySelector('header.top .brand');
  if (brand && !document.querySelector('header.top .ver')) brand.insertAdjacentHTML('afterend', `<a class="ver" href="${root}admin/versions.html" title="Site release history">${VERSION}</a><button class="menu-btn" type="button" aria-expanded="false">Menu</button>`);
  if (nav) {
    nav.innerHTML = NAV.map(([label, items]) => {
      const cur = items.some(([h]) => h.split('?')[0] === here);
      return `<div class="ni${cur ? ' cur' : ''}"><button class="nl" type="button" aria-expanded="false">${label}<span class="caret">▾</span></button><div class="sub">${items.map(([h, t]) => `<a href="${/^[a-z]+:/.test(h) ? '' : root}${h}"${h.split('?')[0] === here ? ' aria-current="page"' : ''}>${t}</a>`).join('')}</div></div>`;
    }).join('');
    const close = except => nav.querySelectorAll('.ni.open').forEach(n => { if (n !== except) { n.classList.remove('open'); n.querySelector('.nl').setAttribute('aria-expanded', 'false'); } });
    nav.querySelectorAll('.nl').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); const ni = b.parentElement; close(ni); const o = ni.classList.toggle('open'); b.setAttribute('aria-expanded', o); }));
    document.addEventListener('click', () => close());
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    const mb = document.querySelector('.menu-btn');
    if (mb) mb.addEventListener('click', () => { const o = document.body.classList.toggle('nav-open'); mb.setAttribute('aria-expanded', o); mb.textContent = o ? 'Close' : 'Menu'; });
  }
  // contact, on every page: one address, a live agent that answers and a person who follows up
  const foot = document.querySelector('footer .wrap');
  if (foot && !foot.querySelector('.contact')) foot.insertAdjacentHTML('afterbegin', `<span class="contact">Contact: <a href="mailto:agent@riskmandate.ai">agent@riskmandate.ai</a> (a live agent answers; a person follows up) · <a href="${root}business/index.html">work with us</a></span>`);
  // theme: the five newsroom themes (assets/themes.css), applied before paint by assets/theme.js; the picker replaces the old toggle
  const btn = document.querySelector('header.top .theme');
  const isDark = () => window.RuvTheme ? RuvTheme.isDark() : matchMedia('(prefers-color-scheme: dark)').matches;
  if (btn && window.RuvTheme) RuvTheme.picker(btn);
  if (document.querySelector('.mermaid')) window.addEventListener('ruv-theme', () => location.reload());   // diagrams are drawn in the theme's colours
  // mermaid
  if (window.mermaid) mermaid.initialize({ startOnLoad: true, theme: isDark() ? 'dark' : 'neutral', securityLevel: 'loose', flowchart: { curve: 'basis', htmlLabels: true }, themeVariables: (() => { const v = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim(); return { primaryColor: v('--tint-solid'), primaryTextColor: v('--head'), primaryBorderColor: v('--accent'), lineColor: v('--dim'), background: v('--panel'), mainBkg: v('--tint-solid'), secondaryColor: v('--panel2'), tertiaryColor: v('--panel'), textColor: v('--fg'), fontFamily: 'ui-sans-serif,system-ui,sans-serif' }; })() });
  // copy buttons
  document.querySelectorAll('pre:not(.mermaid)').forEach(pre => { const b = document.createElement('button'); b.className = 'copy'; b.textContent = 'copy'; b.onclick = () => { navigator.clipboard?.writeText(pre.innerText.replace(/copy$/, '').trim()); b.textContent = 'copied'; setTimeout(() => b.textContent = 'copy', 1200); }; pre.appendChild(b); });
  // markdown includes: <div class="md" data-md="data/x.md">
  document.querySelectorAll('[data-md]').forEach(async el => { try { const t = await (await fetch(el.dataset.md)).text(); el.innerHTML = window.marked ? marked.parse(t) : `<pre>${t.replace(/</g, '&lt;')}</pre>`; el.querySelectorAll('h1,h2,h3').forEach(h => { const n = document.createElement('h' + (+h.tagName[1] + 1)); n.innerHTML = h.innerHTML; h.replaceWith(n) }); el.querySelectorAll('table').forEach(t => { if (!t.parentElement.classList.contains('tbl')) { const w = document.createElement('div'); w.className = 'tbl'; t.replaceWith(w); w.appendChild(t) } }); } catch (e) { el.textContent = 'could not load ' + el.dataset.md; } });
  // POC1 report table: <div data-poc1="data/report.json">
  document.querySelectorAll('[data-poc1]').forEach(async el => { try {
    const rep = await (await fetch(el.dataset.poc1)).json();
    const cls = s => s.startsWith('allowed') ? 'ok' : s.startsWith('approval') ? 'ap' : 'no';
    el.innerHTML = `<div class="tbl"><table><thead><tr><th>agent</th><th>action</th><th>resource</th><th>Ruflo default (legacy)</th><th>with the ABP (enforce)</th></tr></thead><tbody>${rep.rows.map(r => `<tr><td>${r.who}</td><td><code>${r.action}</code></td><td class="k">${r.resource || ''}</td><td class="${cls(r.legacy)}">${r.legacy}</td><td class="${cls(r.abp)}">${r.abp}</td></tr>`).join('')}</tbody></table></div>
      <p class="k">Deployment: ${rep.deployment} · owner ${rep.owner} · ABP gaps: ${rep.gaps.length} · ledger (ABP): valid=${rep.ledger.abp.valid}, ${rep.ledger.abp.length} receipts · ledger (legacy): valid=${rep.ledger.legacy.valid}</p>`;
  } catch (e) { el.textContent = 'report not built yet (run npm run poc1)'; } });
  // receipts: <div data-receipts="data/state-abp.json">
  document.querySelectorAll('[data-receipts]').forEach(async el => { try {
    const st = await (await fetch(el.dataset.receipts)).json();
    const rs = st.receipts || st.ledger || [];
    el.innerHTML = `<div class="tbl"><table><thead><tr><th>#</th><th>principal</th><th>action</th><th>outcome</th><th>receipt id</th><th>previous</th></tr></thead><tbody>${rs.slice(0, 11).map((r, i) => `<tr><td>${i + 1}</td><td>${r.identity?.id ?? r.principal ?? ''}</td><td><code>${r.action?.type ?? r.actionType ?? ''}</code></td><td class="${(r.outcome || '').startsWith('allowed') ? 'ok' : (r.outcome || '').startsWith('approval') ? 'ap' : 'no'}">${r.outcome ?? ''}</td><td><code>${String(r.receiptId ?? r.id ?? '').slice(0, 26)}…</code></td><td><code>${String(r.previousReceiptId ?? r.prev ?? r.previousHash ?? '').slice(0, 18)}…</code></td></tr>`).join('')}</tbody></table></div>`;
  } catch (e) { el.textContent = 'ledger not built yet'; } });
  // ABP rows: <div data-abp="data/abp.json">
  document.querySelectorAll('[data-abp]').forEach(async el => { try {
    const abp = await (await fetch(el.dataset.abp)).json();
    el.innerHTML = abp.roles.map(role => `<details${role.id === 'coder' ? ' open' : ''}><summary>${role.id} <span class="pill">${role.rows.length} rows</span> <span class="k">${role.purpose}</span></summary><div class="tbl"><table><thead><tr><th>capability</th><th>reach</th><th>mandate</th><th>why</th><th>barrier</th><th>instances</th></tr></thead><tbody>${role.rows.map(r => `<tr><td><code>${r.capability}</code></td><td>${r.reach ? 'yes' : 'no'}</td><td class="${r.mandate === 'yes' ? 'ok' : r.mandate === 'approval' ? 'ap' : 'no'}">${r.mandate}</td><td>${r.why}</td><td class="k">${r.barrier ?? ''}</td><td class="k">${(r.instances ?? []).join(', ')}</td></tr>`).join('')}</tbody></table></div></details>`).join('') + `<p class="k">owner ${abp.owner} · valid until ${abp.valid_until} · ${abp.deployment}</p>`;
  } catch (e) { el.textContent = 'ABP not found'; } });
})();
