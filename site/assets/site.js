// ruv.sgit.ai: nav, theme, Mermaid, markdown includes, POC data tables. No build step needed for these.
(() => {
  const PAGES = [['index.html','Home'],['ruv-stack.html',"rUv's stack"],['use-cases.html','Use cases'],['architecture.html','Architecture'],['pocs.html','The POCs'],['replicate.html','Replicate'],['demo.html','Demo'],['app/index.html','Live app']];
  const here = location.pathname.split('/').pop() || 'index.html';
  const root = document.body.dataset.root ?? '';
  const nav = document.querySelector('nav.main');
  if (nav) nav.innerHTML = PAGES.map(([h, t]) => `<a href="${root}${h}"${h === here ? ' aria-current="page"' : ''}>${t}</a>`).join('');
  // theme
  const saved = (() => { try { return localStorage.getItem('theme'); } catch { return null; } })();
  if (saved) document.documentElement.dataset.theme = saved;
  const btn = document.querySelector('.theme');
  const isDark = () => (document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')) === 'dark';
  const label = () => { if (btn) btn.textContent = isDark() ? '☀ light' : '☾ dark'; };
  label();
  if (btn) btn.addEventListener('click', () => { const t = isDark() ? 'light' : 'dark'; document.documentElement.dataset.theme = t; try { localStorage.setItem('theme', t); } catch {} label(); location.reload(); });
  // mermaid
  if (window.mermaid) mermaid.initialize({ startOnLoad: true, theme: isDark() ? 'dark' : 'neutral', securityLevel: 'loose', flowchart: { curve: 'basis', htmlLabels: true }, themeVariables: isDark() ? { primaryColor: '#163e3a', primaryTextColor: '#efeae0', lineColor: '#a39d90' } : { primaryColor: '#d9f1ee', primaryTextColor: '#1a1917', lineColor: '#6b675f' } });
  // copy buttons
  document.querySelectorAll('pre:not(.mermaid)').forEach(pre => { const b = document.createElement('button'); b.className = 'copy'; b.textContent = 'copy'; b.onclick = () => { navigator.clipboard?.writeText(pre.innerText.replace(/copy$/, '').trim()); b.textContent = 'copied'; setTimeout(() => b.textContent = 'copy', 1200); }; pre.appendChild(b); });
  // markdown includes: <div class="md" data-md="data/x.md">
  document.querySelectorAll('[data-md]').forEach(async el => { try { const t = await (await fetch(el.dataset.md)).text(); el.innerHTML = window.marked ? marked.parse(t) : `<pre>${t.replace(/</g, '&lt;')}</pre>`; } catch (e) { el.textContent = 'could not load ' + el.dataset.md; } });
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
