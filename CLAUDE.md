# CLAUDE.md: rules for the agent building this repo (its Agent Behaviour Policy)

You are building proofs of concept tonight for a live demo tomorrow. Speed matters; trust matters more.

## Mandate (what you are asked to do)
- Build the POCs in `BRIEF.md`, in order of priority, inside this repo.
- Run them locally and in CI; record real outputs under `evidence/` (never invented numbers).
- Commit POC outputs to sgit vaults as described; publish only what `BRIEF.md` says is public.

## Reach you will have, and the barriers
| Capability (ABP grammar) | Allowed? | Barrier / rule |
|---|---|---|
| write.file.project | yes | this repo only |
| execute.process.self | yes | npm/pip/node/python inside the repo or the CI runner |
| send.endpoint.allowed | yes | npm registry, PyPI, GitHub, the sgit server, rUv's public repos. No other hosts |
| write.repository.project | yes | feature branches + PRs; never force-push `main` |
| authenticate-as.credential.tenant | limited | only via repo secrets (`SGIT_TOKEN`, `SGIT_VAULT_KEY_*`, optional `ANTHROPIC_API_KEY`) |
| send.message.world | **no** | no emails, posts, issues or comments on rUv's repos. Dinis talks to rUv |
| read.credential.host | **no** | never print, log, commit or echo a vault key or token. `git diff` before every commit |

## Hard rules
1. **Vault keys are secrets.** Read them from env/secrets only. A vault published with `--visibility public` publishes its READ key on purpose: that is irreversible, so only for vaults marked public in BRIEF.md.
2. **Verify before you claim.** Every number in a demo page or README comes from a run in `evidence/`. If a third-party command differs from the docs here, trust the tool's `--help`, note it in `evidence/notes.md`.
3. **Pin versions** (see README). Do not upgrade mid-build.
4. **Never weaken a security control to make a demo work** (e.g. do not fake a TTY to get past Ruflo's interactive policy admin; use the engine API as POC1 does, which is its documented library surface).
5. Attribute rUv's projects correctly (MIT, by rUv / ruvnet). Our code: Apache-2.0.
6. If blocked > 20 minutes on one POC, mark it "not tonight" in `evidence/notes.md` and move on.
