// ABP (JSON) -> Ruflo AgenticPolicyEngine rules. Usage: node compile.mjs <abp.json> > rules.json
import fs from 'node:fs';
const here = new URL('.', import.meta.url).pathname;
const map = JSON.parse(fs.readFileSync(here + '../../abp/mapping.json', 'utf8'));
export function compile(abp) {
  const rules = []; const gaps = [];
  for (const role of abp.roles) for (const row of role.rows) {
    const m = map.primitives[row.capability];
    if (!m) { gaps.push({ role: role.id, capability: row.capability, gap: 'unknown-primitive' }); continue; }
    const effect = map.mandate_to_effect[row.mandate];
    if (row.reach && row.mandate !== 'yes' && !row.barrier) gaps.push({ role: role.id, capability: row.capability, gap: 'reach-without-mandate-and-no-barrier' });
    rules.push({
      id: `abp:${role.id}:${row.capability}`, effect, actions: m.ruflo, principals: [role.id],
      ...(row.instances && effect === 'allow' && !row.capability.startsWith('write.budget') ? { resources: row.instances } : {}),
      // budgets (write.budget.*) are enforced with engine.setBudget(), not resources: see run.mjs
      priority: effect === 'deny' ? 100 : effect === 'require_approval' ? 90 : 10,
      description: `${row.mandate === 'yes' ? 'mandate' : 'barrier'}: ${row.why}${row.barrier ? ' | ' + row.barrier : ''}`,
    });
  }
  return { rules, gaps };
}
if (process.argv[1] && process.argv[1].endsWith('compile.mjs')) {
  const abp = JSON.parse(fs.readFileSync(process.argv[2] ?? here + '../../abp/examples/ruflo-sparc-swarm.abp.json', 'utf8'));
  console.log(JSON.stringify(compile(abp), null, 2));
}
