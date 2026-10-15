<img src="site/assets/brand/ruv-sgit-logo.svg" alt="ruv.sgit" width="420">

# ruv.sgit.ai: sgit vaults + Agent Behaviour Policies inside rUv's agentic stack

[![built with ruv.sgit](site/assets/brand/ruv-sgit-badge.svg)](https://ruv.sgit.ai/ruv-sgit/index.html)

Website: **https://ruv.sgit.ai** (GitHub Pages, deployed by `.github/workflows/deploy-pages.yml` from `site/`).

Built on 14 Oct 2026 for *Agentic Engineering Live: rUv in London* (Agentics Foundation London, 15 Oct). The one-sentence story:
rUv's stack (Ruflo, RuVector, RVM, MetaHarness) gives agents swarms, consensus, self-learning and speed, with its own policy engine and memory. Ours adds two things:
**a written mandate per agent (ABP)**, compiled into Ruflo's own policy engine, and **a memory with history, encrypted before it leaves the agent (sgit vaults)**. Six proofs of concept show both running *inside* his tools, in CI, in a browser and in a Claude Code session.

| Where | What |
|---|---|
| `site/` | The website: home, rUv's stack by use case, use cases, architecture, the POCs with live outputs, replicate, demo script, and the browser app under `site/app/` |
| `site/articles/` | Articles (newsroom shape, each with a `.md` twin) built from `site/articles/src/*.md` by `site/build/articles.py`: the studio plan, and the setup brief any agent can follow |
| `site/studio/`, `poc/poc7-studio/` | POC7, the studio: a Ruflo hive-mind (queen + 8 roles) whose run made seven animations (`site/studio/v1..v7`, MP4s in `video/`); `hive.sh` / `close.sh` time every Ruflo call; `lane.sh` is the sgit bus protocol (not yet run against a server) |
| `site/talk/` | Tonight's talk as a timeline: `talk-10.json` / `talk-5.json`, the player (`player.html`, presenter + synced audience window), offline single-file builds (`site/build/talk_offline.py`), rehearsal check (`site/build/rehearsal_check.py`) |
| `BRIEF.md`, `CLAUDE.md`, `docs/` | The technical brief, the builder agent's own mandate, and the facts and commands the build followed |
| `abp/` | ABP schema, vocabulary (23 primitives, `verb.object.reach`), mapping to Ruflo actions and RVM rights, two example ABPs |
| `poc/` | POC1 ABP → Ruflo policy engine with receipts · POC2 agent memory in a vault across runners · POC3 ABP → RVM rights · POC4 browser app (RuVector WASM) · POC5 MetaHarness ↔ ABP · POC6 Claude Code session runbook |
| `evidence/` | Recorded outputs of every run (no invented numbers) |
| `.github/workflows/pocs.yml` | CI: build → ABP gate → POC1 → POC3 → POC4 → POC5 → human-approved publish to the public vault; POC2 write ×2 then read on a fresh runner |

## Releases
The site version (in the nav of every page) increments on every push, as on sgit.ai: add a release at the top of `site/admin/versions.json`, then `python3 site/build/versions.py` writes it into `site/assets/site.js` and regenerates `site/admin/versions.html` + `.md`. `validate.py` fails if the two disagree.

## Run the website locally

```bash
./run-website-locally.sh        # http://localhost:8080 (no setup, no network; Python 3 only); opens tonight's talk
```

## Run it offline, on a laptop

```bash
git clone https://github.com/SGit-AI/SGit-AI__Website__Ruv && cd SGit-AI__Website__Ruv
bash scripts/offline.sh setup    # once, online: npm ci (pinned) + .venv with sgit-ai 0.21.0 and the SG/Send vault server 0.34.0
bash scripts/offline.sh all      # no network from here: doctor, POC1/3/4/5, sync + validate the site,
                                 # one ruv.sgit run (Ruflo hive + ephemeral vault on a local server: open, deliver, close, delete),
                                 # then serve the site at http://localhost:8080
```
Steps one at a time: `doctor`, `pocs`, `run`, `serve`. The laptop run's workers are the POC scripts (no model calls), so it needs nothing outside the machine; its ledger and evidence go to `out/offline/` (not the public ledger), its keys to `~/.ruv-sgit-offline` (0600), and its vault server listens on 127.0.0.1:8091. Pages load mermaid, three.js and marked from `site/vendor/` (MIT), so the site works with no network too; the talk also runs from the single file `site/talk/offline-10.html`. Needs Node 20+ and Python 3.11+. `pocs` rewrites a few generated files with fresh timestamps (`git checkout site/data` puts them back).

## Run it

```bash
npm ci && pip install sgit-ai==0.21.0
npm run abp:gate && npm run poc1 && npm run poc3 && npm run poc4:build && npm run poc5 && npm run cleanup
bash site/build/sync.sh && python3 site/build/validate.py && npm run site:serve     # http://localhost:8080
```

Vault steps (keys and token from the environment only) and CI secrets: see https://ruv.sgit.ai/replicate.html.

## Pinned versions (npm, checked 14 Oct 2026)
ruflo 3.56.10 (= claude-flow, @claude-flow/cli) · @ruvector/wasm 0.2.1 · ruvector 0.3.3 · metaharness 0.4.17 · sgit-ai 0.21.0 (PyPI)

## Licences
Our code: Apache-2.0 (`LICENSE`). rUv's projects: MIT, by rUv / ruvnet, used as pinned npm packages and cited "per its README".
