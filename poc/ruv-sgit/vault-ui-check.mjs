// Open a published vault in the official SG/Vault UI and screenshot it (used by `ruvsgit.py seal`).
// usage: node poc/ruv-sgit/vault-ui-check.mjs <viewer-url> <screenshot.png> <name shown in the vault>...
// prints one JSON line: {ok, found, missing, title, errors}
// playwright-core is loaded from RUVSGIT_PLAYWRIGHT_DIR (a folder with node_modules/playwright-core) or this repo;
// Chromium from RUVSGIT_CHROMIUM (default /opt/pw-browsers/chromium); HTTPS_PROXY is honoured, TLS checks stay on.
import { createRequire } from 'node:module';
import path from 'node:path';
const base = process.env.RUVSGIT_PLAYWRIGHT_DIR || path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const { chromium } = createRequire(path.join(base, 'package.json'))('playwright-core');
const [url, shot, ...want] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: process.env.RUVSGIT_CHROMIUM || '/opt/pw-browsers/chromium',
  proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
const p = await (await b.newContext({ viewport: { width: 1280, height: 860 } })).newPage();
const errors = [];
p.on('pageerror', e => errors.push(String(e).slice(0, 200)));
p.on('response', r => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url().split('#')[0].slice(0, 160)); });
await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
let found = [];
for (let i = 0; i < 45 && found.length < want.length; i++) {
  await p.waitForTimeout(1000);
  const text = await p.evaluate(() => {   // the UI renders inside shadow roots: read them too; a navigation inside the UI rejects this, retried next tick
    let t = document.body ? document.body.innerText : '';
    const walk = (root) => { for (const el of root.querySelectorAll('*')) if (el.shadowRoot) { t += '\n' + el.shadowRoot.textContent; walk(el.shadowRoot); } };
    walk(document); return t;
  }).catch(() => '');
  found = want.filter(w => text.includes(w));
}
await p.waitForTimeout(1500);
await p.screenshot({ path: shot });
console.log(JSON.stringify({ ok: found.length === want.length, found, missing: want.filter(w => !found.includes(w)), title: await p.title(), errors: errors.slice(0, 10) }));
await b.close();
