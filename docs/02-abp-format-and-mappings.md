# ABP format, and how it compiles into rUv's enforcement points
An Agent Behaviour Policy describes, per agent role in one deployment: what it can **reach** (technically, today), what it is **mandated** to do, the **gap** between the two, and the **barrier** that actually stops the rest, signed by a named **owner**, valid until a date (licence to operate).
- Grammar: `verb.object.reach`, 23 primitives with an undo class: `abp/vocabulary/capabilities.json` (RiskMandate's published vocabulary).
- POC profile schema: `abp/schema/abp.schema.json`. Examples: `abp/examples/ruflo-sparc-swarm.abp.json` (6 roles), `abp/examples/builder-agent.abp.json` (the agent building this repo).
- A row with `reach: true`, `mandate != yes` and no `barrier` is a **gap**; `npm run abp:gate` fails CI on gaps.

## Compile targets
| Target | rUv surface (verified 14 Oct) | Our mapping |
|---|---|---|
| Ruflo policy engine | `@claude-flow/security` `AgenticPolicyEngine` (modes legacy/observe/enforce; `PolicyRule {id, effect: allow\|deny\|require_approval, actions[], principals[], resources[], priority, constraints}`; `setBudget`; hash-chained receipts; `verifyLedger()`); CLI `ruflo policy status\|evaluate` (admin needs an interactive TTY) | mandate yes -> allow; no -> deny; approval -> require_approval; `write.budget.*` -> `setBudget`; primitives -> action strings via `abp/mapping.json` |
| Ruflo claims | `ruflo claims list\|check\|grant\|revoke\|roles\|policies` | roles = ABP roles; claims = allowed primitives (next step) |
| Ruflo guidance | `ruflo guidance compile` (CLAUDE.md -> policy bundle), `gates` | CLAUDE.md here is the builder's ABP in prose: compile it and compare (nice demo) |
| RVM | 7 rights READ, WRITE, GRANT, REVOKE, EXECUTE, PROVE, GRANT_ONCE; no ambient authority; witness log | `abp/mapping.json` -> per-role token rights + withheld list (POC3). Rights are coarser than primitives: the ABP keeps the distinction |
| MetaHarness | per-harness governance policy, deny-by-default host settings, audit on | harness settings -> ABP rows; diff both ways (POC5) |
| RuVector MCP | `RUVECTOR_MCP_PROFILE=readonly`, `RUVECTOR_MCP_ALLOW` / `_DENY` tool lists | ABP rows on memory tools -> allow/deny lists |
