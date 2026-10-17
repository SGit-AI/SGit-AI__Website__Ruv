# Technical brief: sgit vaults + ABPs inside rUv's stack (six POCs, one night)

## 0. Goal and audience
Tomorrow, 5 minutes in front of rUv and the Agentics London community. The demo must show, live, that:
1. A Ruflo swarm with a **written mandate (ABP)** behaves differently from one without: same actions, `legacy-default-allow` vs allow/deny/approval with signed receipts.
2. Agent memory (Ruflo/RuVector) kept in an **sgit vault** gains what RuVector's own docs say it lacks: encryption (server holds ciphertext), versioned history, branch/merge across agents, clone anywhere.
3. It all runs **in CI**, **in a browser** (RuVector WASM + a vault-served page) and **in a Claude session** (Claude Code with Ruflo as MCP/plugin).

## 1. Architecture
```
            ABP (JSON, abp/examples/*.abp.json, grammar verb.object.reach, 23 primitives)
              │ compile                         │ compile                    │ render
              ▼                                 ▼                            ▼
   Ruflo AgenticPolicyEngine          RVM capability rights           browser ABP viewer
   (rules + envelope, enforce)        (READ/WRITE/EXECUTE/GRANT...)   (RuVector WASM search)
              │ receipts (hash-chained)          │ gap report                 ▲
              ▼                                 ▼                            │ published read key
   ┌──────────────────────── sgit vaults (client-side AES-256-GCM, server = ciphertext) ───────────┐
   │ ruv-pocs-public  : ABPs, compiled policies, receipts, reports, browser app  (publish public)  │
   │ ruv-pocs-memory  : agent memory snapshots (ruflo memory export / ruvector export), private,   │
   │                    one branch per agent role, merged; history = what the swarm learned, when  │
   └───────────────────────────────────────────────────────────────────────────────────────────────┘
              ▲ sgit write --push (CI job, secrets)           ▲ Claude Code session (hooks post-task)
```

## 2. The POCs (priority order; each has acceptance criteria)

### POC1 (P1, ~1h): ABP → Ruflo policy engine, enforced, with receipts in a vault
- Input: `abp/examples/ruflo-sparc-swarm.abp.json` (queens + 8 worker roles).
- `poc/poc1-abp-to-ruflo-policy/compile.mjs`: ABP rows → `PolicyRule[]` (`effect` allow | deny | require_approval; `actions`; `principals`; `constraints`) + one `CapabilityEnvelope` per role. Mapping table: `docs/02-abp-format.md`.
- `poc/poc1-abp-to-ruflo-policy/trace.json`: a scripted action trace a SPARC swarm would emit (file.write, test.run, network.fetch, email.send, deploy, repo.push, credential.read...).
- `run.mjs`: evaluate the trace twice: (a) `legacy` mode, no ABP (what Ruflo does by default today), (b) `enforce` mode with the compiled ABP. Output `report.json` + `report.md` (side by side) + the receipt ledger (`exportState()`), `verifyLedger()` must be `{valid:true}`.
- Acceptance: report shows ≥1 action allowed in legacy and denied under the ABP (e.g. `email.send`), ≥1 `approval_required`, ≥1 `default-deny`; ledger valid; outputs committed to `ruv-pocs-public` at `poc1/<run-id>/`.
- Already runs (see `evidence/poc1-run.txt`).

### POC2 (P2, ~1.5h): agent memory with history: Ruflo/RuVector memory in an sgit vault
- Use Ruflo's own memory (`ruflo memory init|store|search|export`, sql.js WASM, no native deps) and, if the native binary works on the runner, `ruvector create|insert|search|export`.
- Per run: one vault branch per agent role (`sgit branch new coder` ...), each writes its memory export (`sgit write memory/<role>/<ts>.json --file ... --push`), then merge into `main`.
- Show: `sgit history log --json --file memory/coder/...` (what was learned, when, by whom); a second CI job clones the vault (`sgit clone` with the key from secrets) on a fresh runner, re-imports the memory (`ruflo memory import`), and answers the same query: memory survived the ephemeral runner.
- Acceptance: two runners, same answer; vault history has ≥2 commits per role; the server never sees plaintext (state it; `sgit` encrypts client-side, AES-256-GCM).
- Why it matters (cite RuVector's README): no encryption at rest/in transit; no document versioning; replication on "simulated transport"; "collections and metadata filters ... are not a complete authorization boundary".

### POC3 (P4, ~30m): ABP → RVM capability rights (and the gap report)
- `poc/poc3-abp-to-rvm-caps/abp_to_rvm.py`: map each primitive to RVM rights {READ, WRITE, EXECUTE, GRANT, REVOKE, PROVE, GRANT_ONCE}; print the token set per role and the **gap list** (reach granted with no mandate, or mandate with no barrier).
- Acceptance: a markdown table per role + gaps; committed to the public vault. No RVM build needed tonight (RVM is bare-metal Rust).

### POC4 (P3, ~1h): the browser: ABP + memory search in a page served from a vault
- `poc/poc4-browser/index.html`: loads `@ruvector/wasm` (verified: `init()`, `new VectorDB(dim,'cosine',true)`, `insert(vec,id,meta)`, `search(vec,k)`), indexes ABP rows and POC1 receipts, lets the audience ask "can the coder send email?" (embed with a tiny deterministic bag-of-words hash vector, no model, so it runs offline), shows the matching ABP row, the ruflo decision and the receipt hash.
- Serve it from the vault: put it under `app/` in `ruv-pocs-public`, `sgit publish --visibility public --yes`, then `sgit vault serve --open` locally; GitHub Pages as a fallback.
- Acceptance: works offline after load; numbers/hashes on screen come from POC1 outputs.

### POC5 (P5, ~45m): MetaHarness ↔ ABP
- `npx metaharness@0.4.17 rm-demo --template vertical:agentics --host claude-code --no-darwin --target ./poc/poc5-metaharness-abp/harness` (check `--help` first).
- Read its generated governance policy and per-host settings (deny-by-default, "no network, no shell, no file-write, approve-dangerous, 30s timeout, 8 calls/turn, audit on" per its README); render as an ABP; diff against the ABP for the same role: gaps both ways.
- Acceptance: `harness.abp.json` + `diff.md` in the public vault.

### POC6 (P6, stretch): a real Ruflo session in Claude Code, recorded in a vault
- Dedicated repo + Claude Code. Add Ruflo as MCP: `claude mcp add ruflo -- npx -y @claude-flow/cli@3.56.10 mcp start` (verify the exact `mcp` subcommand with `npx ruflo mcp --help`), or the plugin route (`/plugin install ruflo-core@ruflo`).
- Run a tiny SPARC task under `ruflo policy` in **observe** mode (interactive admin: Dinis types it in his terminal; do not automate around the TTY check), then `ruflo hooks session-end`, export memory, `sgit write` the session record.
- Acceptance: one recorded session in `ruv-pocs-memory` with its policy receipts. Cowork alternative: same steps with the vault cloned in a Cowork session (no plugin install there).

## 3. CI (`.github/workflows/pocs.yml`)
Jobs: `setup` (Node 20, Python 3.11, `pip install sgit-ai==0.21.0`, `npm ci`) → `poc1` (+ `abp-gate`: fail the build if any ABP row has reach without mandate and no barrier: the ABP as a test) → `poc3` → `poc4-build` → `vault-commit` (secrets; writes outputs to `ruv-pocs-public` under `runs/<github.run_id>/`, publishes) → `poc2-roundtrip` (needs two jobs on separate runners). Artefacts uploaded per job. Secrets: `SGIT_TOKEN`, `SGIT_VAULT_KEY_PUBLIC`, `SGIT_VAULT_KEY_MEMORY` (never echoed; `::add-mask::`).

## 4. Timeline for tonight
| Time | Do |
|---|---|
| 0:00-0:20 | New repo; copy this pack; `npm i` pinned; create the two vaults (`sgit create`); add secrets |
| 0:20-1:20 | POC1 end to end, incl. vault commit |
| 1:20-2:50 | POC2 roundtrip in CI |
| 2:50-3:50 | POC4 page served from the vault |
| 3:50-4:20 | POC3 |
| then | POC5, POC6 if time; rehearse `docs/07-demo-script.md` |

## 5. Definition of done for the demo
A public vault URL (read key published on purpose) whose page shows: the ABP, the legacy-vs-ABP decision table with receipt hashes, the memory history across two runners, and the RVM gap table; plus the repo link with green CI.

## Public example vaults (16 Oct 2026, Dinis)
Dinis asked on 16 Oct for the example runs' vaults to be published: an ephemeral vault represents a run; once the run has ended it must not change, so the last step of a run is deleting its vault key (the seal, which makes the vault immutable), then publishing the vault with its read key on ruv.sgit.ai, as sgit.ai and the newsroom do.
- The example vaults under `site/vaults/<run>/` are **public on purpose**: their READ key (`sgit_public_read_…`) is published in the folder and in `site/data/vaults.json`. That is irreversible (the bytes stay in git history and on every copy), so it is done only for runs made to be examples, with `python3 poc/ruv-sgit/ruvsgit.py seal <run>`.
- **17 Oct, Dinis: the vaults live on the sgraph vault server, not in the repository.** `seal` now pushes the run's vault (every branch, full history) to https://dev.send.sgraph.ai, publishes its READ key in `site/data/vaults.json` (the reference only: server, vault id, read key, viewer URL, clone command), checks a fresh read-only clone and the vault UI (https://dev.vault.sgraph.ai), then destroys the vault key. `site/vaults/` is removed and `site/build/validate.py` fails if it comes back. Published: `example-01-hello-v2` and `example-07-meta` (which republishes r14-examples' deliveries), listed on `site/examples/index.html`. The SG/Send access token for the server is a secret like the others (`$RUVSGIT_HOME/publish.token` or `RUVSGIT_PUBLISH_TOKEN`), never in the repository.
- **Client vaults are never published.** Client work stays private first and ends with `ruvsgit.py delete <run>` (objects removed from the server, key destroyed), never `seal`.
- A vault key (`sgit_private_vault_…`), a private read key or a working copy's `.sg_vault/local/` never goes into the site; `site/build/validate.py` fails the build if one does.
