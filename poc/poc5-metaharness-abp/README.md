# POC5: MetaHarness <-> ABP (P5)
Verified CLI surface (metaharness 0.4.17 `--help`): `npx metaharness <name> [--template <id>] [--host claude-code|codex|...] [--target <path>] [--no-darwin]`, `npx metaharness score <repo> [--json]`, `analyze <repo>`, `genome <repo>`; templates include `vertical:agentics`, `vertical:crm`, `vertical:coding`; hosts include claude-code, rvm, github-actions.

Steps
1. `npx metaharness rm-agentics --template vertical:agentics --host claude-code --no-darwin --target out/poc5/harness`
2. Find the governance policy + per-host settings it generated (`grep -ri -E "deny|permission|policy|audit" out/poc5/harness`). Its README states defaults: no network, no shell, no file-write, approve-dangerous, 30 s timeout, 8 calls/turn, audit on.
3. Write `harness-to-abp.mjs`: each setting -> an ABP row (e.g. "no network" -> `send.endpoint.world` reach=true mandate=no barrier="MetaHarness host setting"). Output `out/poc5/harness.abp.json`.
4. Diff against `abp/examples/ruflo-sparc-swarm.abp.json` role `coder`: rows in one and not the other = gaps both ways -> `out/poc5/diff.md`.
5. `npx metaharness score . --json > out/poc5/score.json` on THIS repo (a safety/cost scorecard of our own POC repo; nice demo moment).
Acceptance: harness.abp.json + diff.md committed to the public vault. If the scaffold needs network/API keys, stop and note it.
