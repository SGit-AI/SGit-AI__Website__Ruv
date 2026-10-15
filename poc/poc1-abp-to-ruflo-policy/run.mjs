// Evaluate the same swarm trace twice: Ruflo default (legacy, no ABP) vs ABP compiled + enforce.
// Usage: node run.mjs [abp.json] [trace.json] [outdir]
import fs from 'node:fs';
import { AgenticPolicyEngine } from '@claude-flow/security/policy/index';
import { compile } from './compile.mjs';
const here = new URL('.', import.meta.url).pathname;
const abp = JSON.parse(fs.readFileSync(process.argv[2] ?? here + '../../abp/examples/ruflo-sparc-swarm.abp.json', 'utf8'));
const trace = JSON.parse(fs.readFileSync(process.argv[3] ?? here + 'trace.json', 'utf8'));
const out = process.argv[4] ?? here + 'out'; fs.mkdirSync(out, { recursive: true });
const { rules, gaps } = compile(abp);
const legacy = new AgenticPolicyEngine({ mode: 'legacy' });
const enforce = new AgenticPolicyEngine({ mode: 'enforce' });
for (const r of rules) enforce.upsertRule(r);
// ABP rows on write.budget.* with an instance like 'daily-model <= $10' become a budget ceiling
for (const role of abp.roles) for (const row of role.rows) if (row.capability.startsWith('write.budget') && row.mandate === 'yes') {
  const m = /<=\s*\$?(\d+(?:\.\d+)?)/.exec((row.instances ?? []).join(' '));
  if (m) enforce.setBudget({ id: `abp:${role.id}:budget`, principal: role.id, action: 'model.call', maxCostUsd: Number(m[1]), periodMs: 86400000 });
}
const rows = trace.map(t => {
  const req = { identity: { id: t.who, type: 'agent' }, action: t.action };
  const a = legacy.evaluate(req), b = enforce.evaluate(req);
  return { who: t.who, action: t.action.type, resource: t.action.resource ?? '', legacy: `${a.outcome} (${a.reason})`, abp: `${b.outcome} (${b.reason})` };
});
const ledger = { legacy: legacy.verifyLedger(), abp: enforce.verifyLedger() };
fs.writeFileSync(`${out}/report.json`, JSON.stringify({ deployment: abp.deployment, owner: abp.owner, rows, gaps, ledger }, null, 2));
fs.writeFileSync(`${out}/rules.json`, JSON.stringify(rules, null, 2));
fs.writeFileSync(`${out}/state-abp.json`, JSON.stringify(enforce.exportState(), null, 2));
const md = ['| agent | action | resource | Ruflo default (legacy) | with ABP (enforce) |', '|---|---|---|---|---|', ...rows.map(r => `| ${r.who} | ${r.action} | ${r.resource} | ${r.legacy} | ${r.abp} |`), '', `ABP gaps: ${gaps.length}`, `Ledger: legacy ${JSON.stringify(ledger.legacy)} · abp ${JSON.stringify(ledger.abp)}`].join('\n');
fs.writeFileSync(`${out}/report.md`, md); console.log(md);
const changed = rows.filter(r => r.legacy.startsWith('allowed') && !r.abp.startsWith('allowed')).length;
if (!ledger.abp.valid || changed === 0) { console.error('POC1 acceptance failed'); process.exit(1); }
