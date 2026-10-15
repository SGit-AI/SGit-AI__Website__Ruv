# ruv.sgit, a business plan for somebody else to run: task runs, dedicated compute, a maintained repository and expert time

*Source: <https://ruv.sgit.ai/articles/ruv-sgit-business-model.html> · article v1.0.0 · generated from the same source as the page, so the two cannot drift.*

By Dinis Cruz · 2026-10-15

**Abstract.** ruv.sgit is a Ruflo hive, sgit vaults and Agent Behaviour Policies put together to do agent work under a written mandate, with one vault per run as the record. This is the business built on it, written for somebody else to run: four offers that mix and match (task runs from £10, dedicated compute from £21 per 8-hour block, a maintained repository from £149 a month, expert time from £500), the architecture behind them, the workflow from an emailed order to a vault handed over, the unit cost and margin of every price, a calculator, a Wardley map per offer, who should run it, the first ninety days, the risks and what it does not claim. Every number is a starting hypothesis, and the arithmetic is published so you can change it. No payment is taken anywhere yet: orders go by email to agent@riskmandate.ai.

---
## In short

- **Status: starting hypotheses.** Every price, every hour and every margin here is a first guess for a UK operator in October 2026. The arithmetic behind each one is in `poc/ruv-sgit/market/economics.md` and runs as `poc/ruv-sgit/market/model.py`. The first paid orders are the test.
- **Four things, priced three ways each.** Task runs (£10, £20, £50 a run), dedicated compute (£21, £23, £36 per 8-hour block), a maintained repository (£149, £499, £1,500 a month) and expert time (£500, £1,500, £5,000). They mix and match: ten runs and two hours of help is one order.
- **The person's time is the cost, not the tokens.** At our assumptions a small run costs £1.01 in tokens and £5.00 in operator time. That is why the entry price is £10 and not £5, and why automation is the first thing to build.
- **No payment yet.** The [shop](../shop/index.html) builds an order and emails it to agent@riskmandate.ai; we reply with a quote. A person on our side starts, watches and hands over every run.
- **The demonstration is the sales process.** This site was built by the runs it sells, and its [ledger](../ruv-sgit/index.html) shows each one.
- **Written to be copied.** Anybody who runs this business runs sgit vaults and Agent Behaviour Policies, which is the reason it is published.

## The business on one page

Six things to know.

| Thing | What to know |
|---|---|
| **The business** | Agent work done under a written policy, with a record the customer keeps. A queen and a team of agent workers do one task; their messages, deliveries and decisions go into an sgit vault; the vault is what the customer receives. |
| **Why now** | Multi-agent hives are available as open source (Ruflo, by rUv / ruvnet, MIT), model tokens are bought by the million, and machines by the hour. What is scarce is a run somebody can check afterwards: what the agents were allowed to do, and proof of what they did. |
| **The stack** | Ruflo's hive-mind (a queen, workers, tasks, a policy engine with legacy, observe and enforce modes that writes a decision receipt for each action), sgit vaults (encrypted, versioned, the server holds ciphertext only) and Agent Behaviour Policies (what each agent may do, and the barrier when it may not). |
| **What you sell** | Four offers: task runs on shared infrastructure, dedicated compute per task, a maintained repository you run yourself, and expert time. Three sizes each, published prices, mixed and matched in one order. |
| **The numbers** | Target margin 40%, floor 35%, at the base assumptions. Run margins 39% / 47% / 50%; compute 38% / 38% / 43%; repository 43% / 42% / 47%; expert time 55% / 52% / 46%. The biggest sensitivity is operator minutes per run. |
| **Who runs it** | An independent consultant, a company adding it to what it already sells, or an internal team providing it to the rest of its organisation. One operator can start it; the calculator says when a second is needed. |

## What you sell

The catalogue is `site/data/offers.json`. These are its prices; the [shop](../shop/index.html) reads the same file. All prices are in GBP, excluding VAT.

### Task runs (shared infrastructure)

A Ruflo queen and a team of agent workers do one task on our shared runner, inside an sgit vault, under an Agent Behaviour Policy with no network access. You upload the materials; you get the vault back.

| Tier | Price | Workers | Token budget | Wall clock | Materials | Bring your own key |
|---|---|---|---|---|---|---|
| Small run | **£10** a run | 1 queen + up to 5 | 1M Sonnet 5.5, or 0.5M Opus 5.5, or 10M Haiku 5.5 | stops at 15 min | up to 50 MB | £9 |
| Team run | **£20** a run | 1 queen + up to 10 | 3M Sonnet, or 1.5M Opus, or 30M Haiku | stops at 25 min | up to 100 MB | £17 |
| Large run | **£50** a run | 1 queen + up to 20 | 10M Sonnet, or 5M Opus, or 100M Haiku | stops at 45 min | up to 100 MB | £40 |

Every run: no network access (the run's behaviour policy allows no egress); the vault delivered as a zip, or published with a read key if you choose (publishing cannot be undone); if a cap is reached the run stops and the vault holds everything done until then.

### Dedicated compute (an instance per task)

An AWS EC2 instance in London (eu-west-2) started for your task and stopped after it. The vault is created inside that machine, so nothing is shared with other customers. Tokens are bought separately, as a task run. **Not built yet:** this offer is designed and priced, but SG Compute (sgraph's ephemeral EC2 tooling) is not connected to ruv.sgit runs.

| Size | Price | Instance | Price arithmetic |
|---|---|---|---|
| Small | **£21** per 8-hour block | t3.medium: 2 vCPU, 4 GiB | £20 platform fee + twice the EC2 cost ($0.0472 an hour) |
| Medium | **£23** per 8-hour block | m7i.xlarge: 4 vCPU, 16 GiB | £20 + twice the EC2 cost ($0.2331 an hour) |
| GPU | **£36** per 8-hour block | g5.xlarge: 4 vCPU, 16 GiB, 1 NVIDIA A10G | £20 + twice the EC2 cost ($1.277 an hour) |

The EC2 prices come from third-party aggregators and must be confirmed on AWS's own price list before the first sale.

### Maintained repository (monthly)

The full ruv.sgit setup in a private repository of the customer's own, kept up to date. It runs on Claude Code, on AWS or anywhere else they run agents. Model tokens and cloud costs are on their own accounts.

| Tier | Price | What is in it | Our time included |
|---|---|---|---|
| Individual | **£149** a month | one private repository, new versions as released, setup help by email | up to 1 hour a month |
| Team | **£499** a month | everything in Individual, custom branding and the latest UI, a setup call, help running it on Claude Code or AWS | up to 3.5 hours a month |
| White-label ready | **£1,500** a month | everything in Team, your name and domain, priority on versions and fixes; rUv's projects stay attributed as their licences require (MIT, by rUv / ruvnet) | up to 10 hours a month |

Time beyond the cap is sold as expert time. The cap is written into each tier because doubling the hours turns every tier's margin negative (section 6 of the economics).

### Expert time

Time with the people who built ruv.sgit: scope a task, write its behaviour policy, steer runs, read the vaults.

| Item | Price | What it is |
|---|---|---|
| A couple of hours | **£500** a session | about 2 hours, remote: scope a task, steer a few runs, review what came back |
| A day | **£1,500** a day | a working day: design a run pipeline, a behaviour policy or a pilot |
| Several days | **£5,000** an engagement | four working days: set ruv.sgit up in your environment, with your policies and your first runs, and hand it over |

### Mix and match

One order can hold any of the above. Some combinations that make sense:

- **Ten runs and two hours:** ten Team runs (£200) and a couple of hours (£500) to shape the briefs and read the vaults: £700.
- **A pilot:** twenty Small runs (£200) and a day (£1,500) to write the policy and run them with you: £1,700.
- **A big job on its own machine:** a GPU block (£36) and a Large run for the tokens (£50): £86.
- **Run it yourself:** a Team repository (£499 a month) and several days (£5,000) to set it up in your environment.

## How a run works

*(Figure: see the HTML version.)*

**The hive.** A Ruflo queen plans the task and spawns one worker per role; each worker gets a task. In every run so far the workers have been Claude Code subagents. Ruflo is by rUv / ruvnet, MIT licensed, and pinned at 3.56.10 here.

**The mandate.** Each run has a written Agent Behaviour Policy: what the agents may do, and the barrier when they may not. For a shared run it allows no network egress at all: the materials are uploaded with the order, up to 50 MB for a Small run and 100 MB for the others. POC1 on this site shows the mechanism: the same 11 actions through Ruflo's policy engine, 6 stopped in enforce mode with ABP rules (4 denied, 2 sent for approval), and both of Ruflo's hash-chained receipt ledgers valid.

**The vault.** One ephemeral sgit vault per run: created when the work starts, a branch per worker, every delivery committed and merged, measured when the run closes. For a customer the vault is the deliverable, as a zip by default or published with a read key if they ask (publishing gives away the read key and cannot be undone, so it is a choice per run). For this site's own runs it was then deleted, and what stays is the ledger entry.

**Three places a run can happen.**

| Where | Offer | What is shared | Who holds the keys |
|---|---|---|---|
| Our shared runner | Task runs | the machine (one runner shared by 4 runs in the cost model) and the sgit server, which holds ciphertext only | we create the vault and hand it over |
| A dedicated instance | Dedicated compute | nothing: one EC2 per task, stopped after it | the vault is born inside the instance |
| The customer's own environment | Maintained repository | nothing of ours at run time | the customer, on their models and their cloud |

What is measured so far (`evidence/ruv-sgit/`, `site/data/vaults.json`): three working runs on 15 October 2026, r2-materials (6 workers, 5 with a token count), r3-define (4, all with a count) and r4-hero (5, 3 with a count), with vaults open 17.5 to 20.7 minutes and 324,813 to 540,688 workers' tokens each; in every run the server held no plaintext from the sampled delivered text, and a fresh clone matched what the workers delivered. Studio run 1 used 629,857 tokens across 7 builders.

## The workflow

1. **An order by email.** The customer builds an order in the [shop](../shop/index.html) or writes directly; it goes to agent@riskmandate.ai. No payment is taken on the site.
2. **A person on our side.** They read the order, check the task fits the tier, agree the materials and the policy, and reply with a quote.
3. **The run.** The operator opens the run (`python3 poc/ruv-sgit/ruvsgit.py open`), the hive works, each worker delivers into the vault, the operator watches the caps.
4. **The vault handed over.** The run closes, is measured, and the vault goes to the customer as a zip, or is published with a read key if they chose that.
5. **The ledger.** The run's numbers join the ledger: workers, tokens, time, what the server held, whether the clone matched.

**Honestly: this is not automated end to end yet.** A person starts, watches and hands over every run. The materials sandbox for customer uploads is designed, not built; dedicated compute is designed, not built, and SG Compute is not connected to ruv.sgit runs; and delivery of the vault per order is a manual step today. The prices include that person's time at an assumed £75 an hour.

## The numbers

All of this is from `poc/ruv-sgit/market/economics.md`. The inputs that matter: Anthropic first-party model prices cached on 6 October 2026, a token mix of 75% cache reads / 20% fresh input / 5% output (which blends to $1.05 per million tokens on Sonnet 5.5), 1.30 USD per GBP, +25% on workers' tokens for the queen and host session, £75 an hour for the person, and 4 / 6 / 12 operator minutes per Small / Team / Large run. The token mix, the overhead and the operator minutes are assumptions; the economics say so and say why.

### Unit cost and margin

| Offer | Cost per unit | Price | Margin |
|---|---|---|---|
| Small run | £1.01 tokens + £5.00 operator + £0.06 infra = **£6.07** | £10 | 39% |
| Team run | £3.03 + £7.50 + £0.07 = **£10.60** | £20 | 47% |
| Large run | £10.10 + £15.00 + £0.08 = **£25.18** | £50 | 50% |
| Compute, small / medium / GPU | £13.04 / £14.18 / £20.61 (EC2 + 10 operator minutes + disk) | £21 / £23 / £36 | 38% / 38% / 43% |
| Repository, Individual / Team / White-label | £85.00 / £287.50 / £800.00 (capped hours + tooling) | £149 / £499 / £1,500 | 43% / 42% / 47% |
| Expert, hours / day / days | £225 / £712.50 / £2,700 (delivered + prep hours) | £500 / £1,500 / £5,000 | 55% / 52% / 46% |

With the customer's own key the runs are £9 / £17 / £40, at margins of 44% / 55% / 62%. The Small run sits one point under the 40% target and above the 35% floor: it is the entry price, and the person's time is most of its cost.

### Where it breaks

| Stress | Small £10 | Team £20 | Large £50 |
|---|---|---|---|
| base | 39% | 47% | 50% |
| worst token mix, no caching ($2.80 per M) | 22% | 22% | 16% |
| FX 1.20 | 38% | 46% | 48% |
| host overhead 50% | 37% | 44% | 46% |
| **operator time x2** | **-11%** | 10% | 20% |
| automated (no operator) | 89% | 85% | 80% |

Tokens are not the risk; the person's time is. Every run tier stays positive with no caching at all, and at any plausible exchange rate. Doubling the operator's minutes makes the Small run lose money. That is the first number to measure on the first paid runs.

### Why £5 runs wait for automation

The starting idea was a queen and 10 to 20 agents, about a million tokens, about five minutes, for £5 to £10. The evidence moves it: our workers used 75,829 to 151,370 tokens each, so 1M tokens is a 5-to-10-worker run, and no measured run took five minutes (vaults stayed open 17.5 to 20.7 minutes). A 1M-token, five-minute run costs £1.01 in tokens, £5.00 in operator time and £0.05 in infrastructure: £6.06. At £5 that loses 21%. Without the person it would cost £1.06, and £5 would earn 79%. So £5 is the price after automation, and £10 is the entry price now.

### A calculator, because the numbers are yours to change

Volumes per month by offer; the unit prices, costs and hours are the ones above. The default volumes are an example, not a forecast. Nothing runs anywhere: it is arithmetic in the page.

*(Figure: see the HTML version.)*

## The maps

One Wardley map per offer and one for the whole. Positions are judgements, not measurements: left is genesis and custom, right is product and commodity; higher is closer to the customer. Colours and shapes mark whose component it is: ours, rUv's tools, cloud, models, people.

### The whole

*(Figure: see the HTML version.)*

Commoditised: everything heavy underneath is bought or borrowed, model tokens and AWS by the unit, Ruflo and AgentDB / RuVector as rUv's open-source products, and sgit vaults as a product of our own. Custom: the thing the customer sees, governed agent work, is still assembled by hand per order, and the arrows on the map are the work of turning it into a catalogue.

### Task runs

*(Figure: see the HTML version.)*

Commoditised: the hive (rUv's Ruflo), the workers and the tokens are bought, and the shared runner is a machine by the hour. Custom: the run itself, because a person drives each one and the order-to-run path and the materials sandbox are not built yet; this is the offer to productise first.

### Dedicated compute

*(Figure: see the HTML version.)*

Commoditised: EC2 instances by the hour, with GPUs as a scarcer product, passed through at a stated multiple. Custom: the launcher that makes one machine per task and the vault born inside it, which is small, ours, and not built yet: SG Compute is not connected to runs.

### Maintained repository

*(Figure: see the HTML version.)*

Commoditised: the customer's own models, cloud and GitHub, and the sgit and Ruflo packages, pinned. Custom: the setup on each customer's infrastructure and their branding; the subscription productises the upkeep, tested version bumps and the UI.

### Expert time

*(Figure: see the HTML version.)*

Commoditised: the wrapper, fixed-price blocks instead of a day rate, and the method itself, published in articles, maps and specs anyone can copy. Custom, and kept there on purpose: judgement about what to run, what to allow and what a run proved, which is the scarcest component and carries the highest margin.

## Who runs it

The plan is written for three kinds of operator. No person or company that inspired it is named here.

- **[Independent consultants](../business/consultants.html).** Sell runs and expert time under your own name, from the White-label repository tier or a custom setup. Your clients get a vault per job; you keep the method.
- **[Companies adding it to their offering](../business/companies.html).** A services firm that already sells reviews, builds or research adds governed agent runs to the catalogue, with the vault as the deliverable and the policy as the control.
- **[Internal teams](../business/teams.html).** A platform or security team provides runs to the rest of its organisation from the maintained repository, on its own models and cloud, with its own policies.

The [business overview](../business/index.html) has the three side by side. Whoever runs it needs one person who can write a behaviour policy and read a vault, and the calculator above to see when that person runs out of hours.

## Go to market

**The demonstration is the sales process.** This site was made by the runs it sells: the [ruv.sgit page and its ledger](../ruv-sgit/index.html) list every run with its workers, tokens, time and clone check; [the studio](../studio/index.html) shows a hive animating its own explanation; [the talk](../talk/index.html) walks through both. Showing a run, then the vault it produced, then the ledger entry, is the whole pitch.

**The prices are published.** The [shop](../shop/index.html) lists every item from the same catalogue as this article, builds a mixed order and emails it. Publishing the prices is part of the offer.

**The first ninety days.**

| Days | What | Done means |
|---|---|---|
| 1 to 30 | Take orders by email; run them by hand; record operator minutes per run against the 4 / 6 / 12 assumed | ten paid runs in the ledger, each with measured operator time and tokens |
| 31 to 60 | Re-run `model.py` with the measured minutes and host tokens; re-price any tier under the 35% floor; confirm EC2 prices on AWS's list | a catalogue backed by measured inputs, not assumed ones |
| 61 to 90 | Automate the order-to-run path and the materials upload; wire dedicated compute; sign the first repository subscription | a run that starts without a person, and the £5 tier back on the table |

## Risks

| Risk | What it does | What we do about it |
|---|---|---|
| **Operator time** | Doubling the minutes per run takes the Small run to -11% | measure minutes on every paid run; automation is the first thing built; hours are capped in every repository tier |
| **Token and cloud prices** | With no caching at all, run margins fall to 16% to 22% | every run tier stays positive at the worst mix; bring-your-own-key moves token risk to the customer; re-price triggers in `model.py` |
| **Model refusals** | A worker declines a task or part of it, and the run delivers less | the vault shows what each worker delivered, so a gap is visible rather than hidden; expert time to reshape the brief |
| **Abuse** | Somebody uses a run for something harmful, or to reach systems they should not | the mandate allows no network, materials are uploaded and size-capped, workers, tokens and time are capped, and a person reads every order today |
| **Dependence on rUv's open-source tools** | The hive, the policy engine and AgentDB / RuVector are rUv's projects (MIT, by rUv / ruvnet); a change upstream changes us | versions pinned (Ruflo 3.56.10, sgit-ai 0.21.0) and moved only when tested; credit and licence kept as required |

## Why we publish it

We are creating the demand: the talk, the site, the runs in the ledger. We want somebody to run with it. So the business model is published, in enough detail to copy, on the same terms as the code. Anybody who implements this implements sgit vaults and Agent Behaviour Policies, which is the outcome we want either way. If you take it, tell us what broke: agent@riskmandate.ai.

## What this does not claim

- **No paid run yet.** The prices, margins and volumes are hypotheses; the measured numbers are from this site's own runs on 15 October 2026.
- **Not automated end to end.** A person starts, watches and hands over every run; the materials sandbox and dedicated compute are designed, not built, and SG Compute is not connected to runs.
- **Some inputs are assumptions.** The token mix, the +25% queen and host overhead, the operator minutes and the £75 an hour are assumed, and the EC2 prices come from aggregators, to be confirmed on AWS's list.
- **No customer vault has been delivered.** This site's run vaults were measured and then deleted; delivery as a zip or published is how sgit works, not yet a step we have done for a customer.
- **The maps are judgements**, not measurements.
- **Nothing here is rUv's offer.** Ruflo, AgentDB, RuVector, MetaHarness and RVM are rUv's projects, MIT licensed, by rUv / ruvnet; this business builds on them, does not sell or own them, and is not endorsed by him.

## Where this comes from

Dinis Cruz's feedback on 15 October 2026 (run r5-market, `poc/ruv-sgit/runs/r5-market.spec.json`): four offers that mix and match, no payment yet, every contact to agent@riskmandate.ai, and a business model published so somebody else can copy it. The catalogue is `site/data/offers.json`; the unit economics are `poc/ruv-sgit/market/economics.md` and `model.py`; the maps are `site/data/maps.json`; the measured runs are in `evidence/ruv-sgit/` and `site/data/vaults.json`. The shape follows the business plans published on [sgit.ai](https://sgit.ai/startups/business-plans.html): one page first, then everything behind it, the numbers as starting hypotheses, a calculator, and the audit, honestly. Code Apache-2.0; rUv's projects MIT.
