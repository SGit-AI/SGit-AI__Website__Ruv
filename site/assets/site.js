// ruv.sgit.ai: nav, theme, Mermaid, markdown includes, POC data tables. No build step needed for these.
(() => {
  const VERSION = 'v0.1.39';   // written by site/build/versions.py from admin/versions.json
  // six groups by audience (the brief: articles/next-phase.html, "The new menu"); same shape as sgit.ai: brand, version, grouped menus, a Menu button on phones
  // an item's third field, 1, marks a cross-link: it is listed here too, but its page "belongs" to another group, so it does not highlight this one
  const NAV = [
    ['For clients', [['clients/index.html', 'Overview'], ['shop/index.html', 'The shop'], ['clients/index.html#offers', 'The offers and prices'], ['clients/index.html#companies', 'For companies'], ['clients/index.html#teams', 'For internal teams'], ['articles/ruv-sgit-business-model.html', 'The business plan', 1]]],
    ['For providers', [['providers/index.html', 'Overview'], ['providers/index.html#providers', 'The providers'], ['providers/dinis-cruz.html', 'Dinis Cruz'], ['providers/mondweep-chakravorty.html', 'Mondweep Chakravorty'], ['rules/index.html', 'Rules of engagement'], ['join/index.html#provider', 'Apply to join', 1]]],
    ['How it works', [['how-it-works/index.html', 'The engagement path'], ['ruv-sgit/index.html', 'One run, six steps', 1], ['rules/index.html', 'Rules of engagement', 1], ['architecture.html', 'Architecture']]],
    ['Proof', [['proof/index.html', 'Overview'], ['ruv-sgit/index.html', 'ruv.sgit runs'], ['ruv-sgit/ledger/index.html', 'The vault ledger'], ['pocs.html', 'The six POCs'], ['app/index.html', 'Live app'], ['examples/index.html', 'Published run vaults'], ['talk/index.html', 'The talk, 15 October 2026'], ['talk/player.html?talk=talk-10.json', 'Play the talk'], ['talk/narration.html', 'The talk, narrated'], ['articles/the-talk-live.html', 'The talk, live', 1]]],
    ['Learn', [['learn/index.html', 'Overview'], ['learn/overview.html', 'What ruv.sgit is'], ['articles/index.html', 'All articles'], ['ruv-stack.html', "rUv's stack"], ['use-cases.html', 'Use cases'], ['studio/index.html', 'The studio'], ['replicate.html', 'Replicate'], ['replicate.html#offline', 'Run it offline'], ['articles/studio-setup-brief.html', 'Set it up: the brief', 1]]],
    ['Join', [['join/index.html#provider', 'Apply as a provider'], ['join/index.html#updates', 'Keep me posted'], ['mailto:agent@riskmandate.ai', 'Contact: agent@riskmandate.ai']]],
  ];
  const root = document.body.dataset.root ?? '';
  const segs = location.pathname.split('/'), file = segs.pop() || 'index.html';
  const depth = (root.match(/\.\.\//g) || []).length;   // pages in a subfolder (talk/, ruv-sgit/ledger/) set data-root="../" or "../../"
  const here = [...segs.slice(segs.length - depth), file].join('/');
  const path = h => h.split(/[?#]/)[0];
  const nav = document.querySelector('nav.main'), brand = document.querySelector('header.top .brand');
  if (brand && !document.querySelector('header.top .ver')) brand.insertAdjacentHTML('afterend', `<a class="ver" href="${root}admin/versions.html" title="Site release history">${VERSION}</a><button class="menu-btn" type="button" aria-expanded="false">Menu</button>`);
  if (nav) {
    // the group that holds this page: an item for it (not a cross-link); otherwise a group with its folder's index (articles/*, talk/*, studio/v1 ...)
    const owns = (items, h) => items.some(([u, , x]) => !x && path(u) === h);
    let ci = NAV.findIndex(([, items]) => owns(items, here));
    if (ci < 0 && here.includes('/')) ci = NAV.findIndex(([, items]) => owns(items, here.split('/')[0] + '/index.html'));
    nav.innerHTML = NAV.map(([label, items], gi) => {
      const at = items.map(([h]) => path(h) === here ? (h.includes('#') ? 1 : 2) : 0), best = Math.max(...at), mark = best ? at.indexOf(best) : -1;   // one item per group: the page itself before its sections
      return `<div class="ni${gi === ci ? ' cur' : ''}"><button class="nl" type="button" aria-expanded="false">${label}<span class="caret">▾</span></button><div class="sub"${gi >= NAV.length - 2 ? ' style="left:auto;right:0"' : ''}>${items.map(([h, t], i) => `<a href="${/^[a-z]+:/.test(h) ? '' : root}${h}"${i === mark ? ' aria-current="page"' : ''}>${t}</a>`).join('')}</div></div>`;
    }).join('');
    const close = except => nav.querySelectorAll('.ni.open').forEach(n => { if (n !== except) { n.classList.remove('open'); n.querySelector('.nl').setAttribute('aria-expanded', 'false'); } });
    nav.querySelectorAll('.nl').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); const ni = b.parentElement; close(ni); const o = ni.classList.toggle('open'); b.setAttribute('aria-expanded', o); }));
    document.addEventListener('click', () => close());
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    const mb = document.querySelector('.menu-btn');
    if (mb) mb.addEventListener('click', () => { const o = document.body.classList.toggle('nav-open'); mb.setAttribute('aria-expanded', o); mb.textContent = o ? 'Close' : 'Menu'; });
  }
  // the source, in the top banner of every page
  const gh = 'https://github.com/SGit-AI/SGit-AI__Website__Ruv';
  const tb = document.querySelector('header.top .theme');
  if (tb && !document.querySelector('header.top .gh')) tb.insertAdjacentHTML('beforebegin', `<a class="gh" href="${gh}" title="The source on GitHub: ${gh.slice(8)}" aria-label="source on GitHub"><svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38v-1.33c-2.23.48-2.7-1.07-2.7-1.07-.36-.92-.89-1.17-.89-1.17-.73-.5.06-.49.06-.49.8.06 1.23.83 1.23.83.72 1.22 1.88.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.65-.89-3.65-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48v2.2c0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg><span>GitHub</span></a>`);
  // contact, on every page: one address, a live agent that answers and a person who follows up
  const foot = document.querySelector('footer .wrap');
  if (foot && !foot.querySelector('.contact')) foot.insertAdjacentHTML('afterbegin', `<span class="contact">Contact: <a href="mailto:agent@riskmandate.ai">agent@riskmandate.ai</a> (a live agent answers; a person follows up) · <a href="${root}clients/index.html">work with us</a> · <a href="${root}join/index.html#provider">join as a provider</a></span>`);
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
