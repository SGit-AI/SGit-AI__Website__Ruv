# ruv.sgit.ai: sgit vaults + Agent Behaviour Policies inside rUv's agentic stack

Website: **https://ruv.sgit.ai** (GitHub Pages, deployed by `.github/workflows/deploy-pages.yml` from `site/`).

Built on 14 Oct 2026 for *Agentic Engineering Live: rUv in London* (Agentics Foundation London, 15 Oct). The one-sentence story:
rUv's stack (Ruflo, RuVector, RVM, MetaHarness) lets agents go to town. Ours adds the two things autonomy needs to be trusted:
**a written mandate per agent (ABP)** and **memory with history that the host cannot read (sgit vaults)**. Six proofs of concept show both running *inside* his tools, in CI, in a browser and in a Claude Code session.

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
