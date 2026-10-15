# POC6 (stretch): a real Ruflo swarm session in Claude Code, recorded in a vault
Claude Code, dedicated repo (this one):
1. MCP route (verified subcommands: `ruflo mcp start|status|tools|exec`): `claude mcp add ruflo -- npx -y ruflo@3.56.10 mcp start` then `claude mcp list`. Plugin route (from public guides, verify): `/plugin install ruflo-core@ruflo`.
2. Policy: Dinis, in his own terminal (interactive admin is required by design): `npx ruflo policy init --mode observe` then add rules from `out/poc1/rules.json` by hand for 2-3 key rows (`npx ruflo policy rule ...`, check `npx ruflo policy --help`). Observe mode records receipts without blocking.
3. Task: a tiny SPARC run on this repo, e.g. "add a unit test for compile.mjs" (`npx ruflo swarm start -o "..." -s development` or via the MCP tools from Claude Code).
4. Record: `npx ruflo hooks session-end`; copy `.claude-flow/policy/state.json` (receipts) + memory DB files; `scripts/vault_write.sh` into `ruv-pocs-memory` under `sessions/<date>/`.
5. `npx ruflo daemon stop`.
Cowork variant: Cowork sessions cannot install Claude Code plugins; clone the vault there (`sgit clone`) and use Cowork to READ the recorded session and the ABP, and draft the write-up. Agents draft; Dinis sends.
Acceptance: one session folder in the memory vault with receipts; `npx ruflo policy verify` (or `status`) shows a valid ledger.
