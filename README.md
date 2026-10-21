<img src="site/assets/brand/ruv-sgit-logo.svg" alt="ruv.sgit" width="420">

# ruv.sgit.ai: sgit vaults + Agent Behaviour Policies inside rUv's agentic stack

[![built with ruv.sgit](site/assets/brand/ruv-sgit-badge.svg)](https://ruv.sgit.ai/ruv-sgit/index.html)

Website: **https://ruv.sgit.ai** (GitHub Pages, deployed by `.github/workflows/deploy-pages.yml` from `site/`).

Built on 14 Oct 2026 for *Agentic Engineering Live: rUv in London* (Agentics Foundation London, 15 Oct). The one-sentence story:
rUv's stack (Ruflo, RuVector, RVM, MetaHarness) gives agents swarms, consensus, self-learning and speed, with its own policy engine and memory. Ours adds two things:
**a written mandate per agent (ABP)**, compiled into Ruflo's own policy engine, and **a memory with history, encrypted before it leaves the agent (sgit vaults)**. Six proofs of concept show both running *inside* his tools, in CI, in a browser and in a Claude Code session.

Since 21 Oct 2026 (v0.2.0) the site is no longer only about the talk: it offers **the ruv.sgit service**, agent work done by a Ruflo hive under a written mandate per role, with an sgit vault per job that the client keeps, delivered by people through a small marketplace of providers. It starts with two founding providers, Dinis Cruz and Mondweep Chakravorty (Agentics Foundation London), who take enquiries to book: an enquiry is an email to agent@riskmandate.ai and a person replies with dates and a quote. There is no payment on the site and no automation; matching is by hand. The plan, its decisions and what was built are in [Article No. 9](https://ruv.sgit.ai/articles/next-phase.html).

The site speaks to three audiences, with the proof behind all three:

| Audience | Pages |
|---|---|
| **Clients**, who want the work done | [Home](https://ruv.sgit.ai/) (three doors, the path, the providers, the proof, the rules in brief) · [For clients](https://ruv.sgit.ai/clients/index.html) (the engagement path, the four offers and prices, the project types, what stays yours, sections for companies and internal teams) · [the shop](https://ruv.sgit.ai/shop/index.html) (an emailed order, with an optional preferred provider) |
| **Providers**, consultants and service companies who want to deliver it | [For providers](https://ruv.sgit.ai/providers/index.html) · the founding providers' pages, [Dinis Cruz](https://ruv.sgit.ai/providers/dinis-cruz.html) and [Mondweep Chakravorty](https://ruv.sgit.ai/providers/mondweep-chakravorty.html) (bios drafted from public pages, for each to approve; photos to come) · [Rules of engagement](https://ruv.sgit.ai/rules/index.html) · [How it works](https://ruv.sgit.ai/how-it-works/index.html) · [Join](https://ruv.sgit.ai/join/index.html) |
| **Learners**, who want to understand it | [Learn](https://ruv.sgit.ai/learn/index.html): what ruv.sgit is, rUv's stack, use cases, architecture, the studio, replicate, the articles |
| **Proof** | [Proof](https://ruv.sgit.ai/proof/index.html): the ruv.sgit runs and their vault ledger, the published run vaults, the POCs, the live app, the talk of 15 Oct 2026 |

**Rules of engagement, in brief:** everything is open (our code Apache-2.0, our materials CC BY 4.0, rUv's projects MIT) and anybody can do this without us; code made in engagements through us is open, but the client's own code and data stay the client's; changes are committed back; revenue is split equally between the parties after direct costs; whoever has the client bills; custom arrangements are agreed in writing. **To join as a provider:** apply on [the join page](https://ruv.sgit.ai/join/index.html#provider); the form builds an email to agent@riskmandate.ai (no backend), applications go on a waiting list, and they never go into this repository. Approved providers, with consented fields only, are listed in `site/data/providers.json`.

The menu is For clients · For providers · How it works · Proof · Learn · Join. The old business pages (`site/business/*.html`) are redirects to For clients and For providers, so their URLs, including the talk's "ruv.sgit.ai/business", keep working.

| Where | What |
|---|---|
| `site/` | The website: the service home, `clients/`, `providers/` (one page per founding provider), `rules/`, `how-it-works/`, `join/`, the `learn/` and `proof/` hubs (the old home's content is `learn/overview.html`), rUv's stack by use case, use cases, architecture, the POCs with live outputs, replicate, the shop, the demo script (historical), and the browser app under `site/app/`; `site/business/` holds the redirects |
| `site/articles/` | Articles (newsroom shape, each with a `.md` twin) built from `site/articles/src/*.md` by `site/build/articles.py`: among them the studio plan, the setup brief any agent can follow, the business plan, the talk's write-ups, and Article No. 9, the brief for the service site |
| `site/studio/`, `poc/poc7-studio/` | POC7, the studio: a Ruflo hive-mind (queen + 8 roles) whose run made seven animations (`site/studio/v1..v7`, MP4s in `video/`); `hive.sh` / `close.sh` time every Ruflo call; `lane.sh` is the sgit bus protocol (not yet run against a server) |
| `site/talk/` | The talk of 15 Oct 2026 as a timeline: `talk-10.json` / `talk-5.json`, the player (`player.html`, presenter + synced audience window), offline single-file builds (`site/build/talk_offline.py`), rehearsal check (`site/build/rehearsal_check.py`) |
| `BRIEF.md`, `CLAUDE.md`, `docs/` | The technical brief, the builder agent's own mandate, and the facts and commands the build followed |
| `abp/` | ABP schema, vocabulary (23 primitives, `verb.object.reach`), mapping to Ruflo actions and RVM rights, two example ABPs |
| `poc/ruv-sgit/` | The ruv.sgit runner (`ruvsgit.py`) and every run's spec in `runs/` (feedback and one task per worker); the ledger is `site/data/vaults.json` |
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
