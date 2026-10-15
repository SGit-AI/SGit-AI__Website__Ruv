// POC5: MetaHarness scaffold -> ABP, and diff against our ABP for the same role.
// Usage: node harness-to-abp.mjs <harness-dir> <abp.json> <role> <outdir>
// Reads what the scaffold actually generated (.claude/settings.json permissions, CLAUDE.md rules,
// .harness/manifest.json) and renders every setting as an ABP row (verb.object.reach grammar).
import fs from 'node:fs';
import path from 'node:path';
const [harness = 'out/poc5/harness', abpPath = 'abp/examples/ruflo-sparc-swarm.abp.json', roleId = 'coder', out = 'out/poc5'] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const read = p => fs.existsSync(path.join(harness, p)) ? fs.readFileSync(path.join(harness, p), 'utf8') : '';
const settings = JSON.parse(read('.claude/settings.json') || '{}');
const manifest = JSON.parse(read('.harness/manifest.json') || '{}');
const claudeMd = read('CLAUDE.md');
const rows = [];
const src = (what, where) => `${what} (${where})`;
// 1. permissions.allow -> reach + mandate yes
for (const a of settings.permissions?.allow ?? []) {
  if (a.startsWith('Bash(')) rows.push({ capability: 'execute.process.self', reach: true, mandate: 'yes', instances: [a], why: src('allow-listed command', '.claude/settings.json permissions.allow') });
  else if (a.startsWith('mcp__')) rows.push({ capability: 'execute.process.self', reach: true, mandate: 'yes', instances: [a], why: src('allow-listed MCP tool', '.claude/settings.json permissions.allow') });
}
// 2. permissions.deny -> reach + mandate no + barrier = the host setting
for (const d of settings.permissions?.deny ?? []) {
  if (d.startsWith('Read(')) rows.push({ capability: 'read.credential.host', reach: true, mandate: 'no', instances: [d], barrier: 'Claude Code permissions.deny (host-enforced)', why: src('secrets file denied', '.claude/settings.json permissions.deny') });
}
// 3. MCP servers the harness starts -> network + process reach the agent gets
for (const [name, s] of Object.entries(settings.mcpServers ?? {})) rows.push({ capability: 'execute.process.host', reach: true, mandate: 'yes', instances: [`${name}: ${s.command} ${(s.args ?? []).join(' ')}`], why: src('MCP server launched by the host', '.claude/settings.json mcpServers') });
// 4. CLAUDE.md behavioural rules -> prose rules; destructive ops deferred = approval
if (/defer destructive operations to the user/i.test(claudeMd)) rows.push({ capability: 'delete.file.host', reach: true, mandate: 'approval', barrier: 'CLAUDE.md rule only (prose, not enforced)', why: src('"Defer destructive operations to the user"', 'CLAUDE.md') });
// merge duplicate rows (same capability + mandate): instances and sources accumulate
const merged = [];
for (const r of rows) { const k = merged.find(x => x.capability === r.capability && x.mandate === r.mandate); if (k) { k.instances = [...(k.instances ?? []), ...(r.instances ?? [])]; if (!k.why.includes(r.why)) k.why += '; ' + r.why; } else merged.push({ ...r }); }
rows.length = 0; rows.push(...merged);
// 5. What the scaffold does NOT state: everything else in our vocabulary is reach=unknown. We list the rows our ABP has and the harness is silent on.
const abp = JSON.parse(fs.readFileSync(abpPath, 'utf8'));
const ours = abp.roles.find(r => r.id === roleId)?.rows ?? [];
const harnessAbp = { abp_version: '0.1-poc', deployment: `MetaHarness ${manifest.generator ?? '?'} scaffold: template ${manifest.template ?? '?'}, host ${manifest.vars?.host ?? '?'} (generated ${manifest.generated_at ?? '?'})`, owner: 'unsigned (generated, no named owner)', valid_until: null, roles: [{ id: manifest.vars?.name ?? 'harness', purpose: manifest.vars?.description ?? '', rows }] };
fs.writeFileSync(`${out}/harness.abp.json`, JSON.stringify(harnessAbp, null, 2));
const caps = r => new Set(r.map(x => x.capability));
const h = caps(rows), o = caps(ours);
const onlyHarness = rows.filter(r => !o.has(r.capability));
const onlyOurs = ours.filter(r => !h.has(r.capability));
const both = ours.filter(r => h.has(r.capability)).map(r => ({ ours: r, harness: rows.filter(x => x.capability === r.capability) }));
const md = [`# POC5: MetaHarness scaffold vs our ABP (role \`${roleId}\`)`, '',
  `Scaffold: \`npx metaharness rm-agentics --template vertical:agentics --host claude-code --no-darwin\` (metaharness 0.4.17, manifest generator ${manifest.generator}, ${Object.keys(manifest.files ?? {}).length} files).`, '',
  '## What the harness actually says about permissions', '',
  '| source | setting |', '|---|---|',
  ...(settings.permissions?.allow ?? []).map(a => `| settings.json allow | \`${a}\` |`),
  ...(settings.permissions?.deny ?? []).map(a => `| settings.json deny | \`${a}\` |`),
  ...Object.keys(settings.mcpServers ?? {}).map(a => `| settings.json mcpServers | \`${a}\` |`),
  `| CLAUDE.md | ${/defer destructive/i.test(claudeMd) ? '"Defer destructive operations to the user" (prose)' : 'no destructive-ops rule found'} |`, '',
  `Not found in the generated files: a governance policy document, deny-by-default statement, network/shell/file-write switches, timeouts, call limits or an audit flag (the README of the metaharness package describes those; this scaffold, with this template and host, did not emit them). Noted in evidence/notes.md.`, '',
  '## Rendered as an ABP', '', `${rows.length} rows -> \`harness.abp.json\``, '',
  '| capability | reach | mandate | barrier | from |', '|---|---|---|---|---|',
  ...rows.map(r => `| ${r.capability} | ${r.reach} | ${r.mandate} | ${r.barrier ?? ''} | ${r.why} |`), '',
  '## Diff both ways', '',
  `### In the harness, not in our ABP (${onlyHarness.length})`, '', ...(onlyHarness.length ? onlyHarness.map(r => `- \`${r.capability}\`: ${r.why}`) : ['- none']), '',
  `### In our ABP, harness silent (${onlyOurs.length}): reach the agent has with no setting either way`, '', ...onlyOurs.map(r => `- \`${r.capability}\` mandate **${r.mandate}**${r.barrier ? ` (our barrier: ${r.barrier})` : ''}`), '',
  `### In both (${both.length})`, '', ...(both.length ? both.map(b => `- \`${b.ours.capability}\`: ours mandate **${b.ours.mandate}**; harness ${b.harness.map(x => x.mandate).join('/')}`) : ['- none']), '',
  '## Reading', '', 'The scaffold ships a host permission list (what the tool runner lets through) and prose rules. An ABP adds the three things a permission list cannot say: whether the reach is mandated, who signed it, and until when. The harness file is a good barrier; the ABP is the mandate it should be generated from.'].join('\n');
fs.writeFileSync(`${out}/diff.md`, md); console.log(md);
