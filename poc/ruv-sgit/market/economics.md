# Unit economics behind site/data/offers.json (r5-market, economist)

Every price in the catalogue is checked here against what it costs us. Every number is either an **input** (cited in section 1) or **computed** from inputs (arithmetic shown). The model is runnable and editable: `python3 out/ruv-sgit/r5-market/economist/model.py` (change the INPUTS block, re-run, and the margins below update). All money in GBP excluding VAT unless marked $.

## 1. Inputs

| Input | Value | Source |
|---|---|---|
| Fable 5.1 | $10 in / $50 out / $0.25 cache read, per M tokens | Anthropic first-party, cached 6 Oct 2026 |
| Opus 5.5 | $4 / $20 / $0.20 | same |
| Sonnet 5.5 | $2 / $10 / $0.20 | same |
| Haiku 5.5 | $0.10 / $0.50 (prompts up to 100K); cache read not listed | same; **assumed $0.01** cache read |
| EC2 eu-west-2 on-demand | t3.medium $0.0472/h; m7i.xlarge $0.2331/h; g5.xlarge $1.277/h | doit.com / devzero.io aggregators; **to confirm on AWS's price list** |
| FX | **1.30 USD per GBP** | assumption, editable |
| Token mix | **75% cache reads / 20% fresh input / 5% output** | assumption, editable (see 2) |
| Queen + host overhead | **+25%** on workers' tokens | assumption: the host session's tokens were not measured |
| Person on our side | **£75 an hour**, loaded | assumption, editable |
| Operator minutes per run | **4 (small) / 6 (team) / 12 (large)** hands-on | assumption: start, check, hand over; watching overlaps with other work |
| Shared runner | one m7i.xlarge shared by **4** runs, charged for the full wall-clock cap | assumption |
| Storage + delivery | **£0.05 per run** (sgit server, zip) | assumption: no measured cost |
| Compute block | 8 hours; **10 operator minutes** per block; **£0.25** disk allowance | assumption |

Measured (evidence/ruv-sgit/r2-materials.json, r3-define.json, r4-hero.json; site/data/vaults.json; site/studio/run.json):

| Run | Workers (with tokens) | Workers' tokens | Vault open (min) | Slowest worker |
|---|---|---|---|---|
| r2-materials | 6 (5) | 540,688 | 20.7 | 769 s |
| r3-define | 4 (4) | 524,733 | 20.6 | 777 s |
| r4-hero | 5 (3) | 324,813 | 17.5 | 302 s |
| studio run 1 | 7 builders | 629,857 | n/a | n/a |

Per worker (12 workers with a token count): min 75,829, max 151,370, mean 115,853. Studio: 629,857 / 7 = 89,980 per builder. Claude Code subagents report one total per worker, not an input/output split, and the host session was not measured: that is why the mix and the +25% overhead are assumptions.

## 2. Token mix: blended $ per million tokens

Blended = cache share x cache price + fresh-input share x input price + output share x output price.

| Mix (cache / input / output) | Sonnet 5.5 | Opus 5.5 | Haiku 5.5 | Fable 5.1 |
|---|---|---|---|---|
| **base 75 / 20 / 5** | 0.75x0.20 + 0.20x2 + 0.05x10 = **$1.05** | **$1.95** | **$0.0525** | **$4.69** |
| conservative 50 / 40 / 10 | $1.90 | $3.70 | $0.095 | $9.13 |
| worst 0 / 90 / 10 (no caching) | $2.80 | $5.60 | $0.14 | $14.00 |

Agent work is mostly reading: each turn resends the conversation, most of it from cache. Cache writes are counted as fresh input (Anthropic bills them at a premium over input; at a 20% share that is inside the conservative row).

**Model conversion (budgets are Sonnet-equivalent, base mix).** 1M Sonnet costs $1.05. The same money buys 1.05/1.95 = 0.54M Opus (we offer **0.5M**), 1.05/0.0525 = 20M Haiku (we offer **10M**, half, because Haiku's cache price is our assumption and at full input price for cache reads 10M Haiku costs 10 x (0.75x0.10 + 0.20x0.10 + 0.05x0.50) = $1.20, close to the Sonnet budget), and 1.05/4.69 = 0.22M Fable (on request only).

## 3. Testing Dinis's starting idea

"1 queen + 10-20 agents + ~1M tokens in ~5 minutes for £5-10":
- **Tokens:** our workers used 75k-151k each, so 10-20 workers would use about 1.2M-2.3M (mean 115,853 x 10 or x 20), not 1M. 1M tokens is a 5-to-10-worker run.
- **Time:** no measured run took 5 minutes: vaults stayed open 17.5-20.7 min, and single workers took up to 777 s (13 min). Caps are set from the evidence: 15 / 25 / 45 minutes.
- **£5:** cost of a 1M-token, 5-minute run = tokens 1 x 1.05 x 1.25 / 1.30 = £1.01, + operator 4/60 x 75 = £5.00, + infra £0.05 = **£6.06. At £5 we lose 21%.** Without the person (automated) it would cost £1.06 and £5 would earn 79%. So **£5 waits for automation**; the entry tier is £10 now.

## 4. Task runs

Cost per run = tokens (M x blended x 1.25 / FX) + operator (minutes / 60 x 75) + infra (cap / 60 x $0.2331 / 4 / FX + £0.05).

| Tier | Caps | Tokens | Operator | Infra | **Cost** | **Price** | **Margin** |
|---|---|---|---|---|---|---|---|
| Small run-s | 1+5 workers, 1M Sonnet, 15 min, 50 MB | 1x1.05x1.25/1.3 = £1.01 | 4 min = £5.00 | £0.061 | **£6.07** | **£10** | **39%** |
| Team run-m | 1+10 workers, 3M Sonnet, 25 min, 100 MB | £3.03 | 6 min = £7.50 | £0.069 | **£10.60** | **£20** | **47%** |
| Large run-l | 1+20 workers, 10M Sonnet, 45 min, 100 MB | £10.10 | 12 min = £15.00 | £0.084 | **£25.18** | **£50** | **50%** |

**Bring your own key** removes our token cost; the delta passes it on rounded down (we keep a little for the higher support load of other people's keys):

| Tier | BYOK delta | BYOK price | Cost (no tokens) | Margin |
|---|---|---|---|---|
| run-s | -£1 | £9 | £5.06 | 44% |
| run-m | -£3 | £17 | £7.57 | 55% |
| run-l | -£10 | £40 | £15.08 | 62% |

The small run sits 1 point under the 40% target and above the 35% floor: it is the entry price, and the person's time is most of its cost.

## 5. Dedicated compute (SG Compute)

Price per 8-hour block = £20 platform fee + 2 x EC2 cost for 8 hours (100% markup on EC2 covers idle start-up time, disk and AWS price drift), rounded up to the pound. Cost = EC2 + 10 operator minutes (£12.50) + £0.25 disk. Tokens are bought separately as a run (section 4).

| Size | EC2 8h | Price arithmetic | **Price** | Cost | **Margin** | EC2 price +20% |
|---|---|---|---|---|---|---|
| small t3.medium | 8 x 0.0472 / 1.3 = £0.29 | 20 + 0.58 = 20.58 | **£21** | £13.04 | **38%** | 38% |
| medium m7i.xlarge | 8 x 0.2331 / 1.3 = £1.43 | 20 + 2.87 = 22.87 | **£23** | £14.18 | **38%** | 37% |
| GPU g5.xlarge | 8 x 1.277 / 1.3 = £7.86 | 20 + 15.72 = 35.72 | **£36** | £20.61 | **43%** | 38% |

The EC2 prices come from aggregators and must be confirmed on AWS's price list before the first sale; a 20% error still leaves every size at or above 37%.

## 6. Maintained repository (per month)

Cost = our hours x £75 + tooling (CI, sgit server, domain allowance). The hours are a stated cap in the offer; anything beyond is expert time. Model tokens and cloud costs are the customer's.

| Tier | Our time cap | Tooling | Cost | **Price** | **Margin** | if time doubled |
|---|---|---|---|---|---|---|
| Individual | 1 h | £10 | £85.00 | **£149** | **43%** | -7% |
| Team | 3.5 h | £25 | £287.50 | **£499** | **42%** | -10% |
| White-label ready | 10 h | £50 | £800.00 | **£1,500** | **47%** | -3% |

The "if time doubled" column is why the hours cap is written into each tier.

## 7. Expert time

Cost = (hours delivered + prep/admin hours) x £75.

| Item | Hours | Cost | **Price** | **Margin** | £ per delivered hour |
|---|---|---|---|---|---|
| A couple of hours | 2 + 1 | £225 | **£500** | **55%** | £250 |
| A day | 7.5 + 2 | £712.50 | **£1,500** | **52%** | £200 |
| Several days (4) | 30 + 6 | £2,700 | **£5,000** | **46%** | £167 |

Runs are not automated end to end yet: a person on our side starts, watches and hands over each run. The catalogue says so on every expert item and in its notes.

## 8. Sensitivity (task runs)

| Stress | run-s £10 | run-m £20 | run-l £50 |
|---|---|---|---|
| base | 39% | 47% | 50% |
| conservative mix (1.90 $/M) | 31% | 35% | 33% |
| worst mix, no caching (2.80 $/M) | 22% | 22% | 16% |
| FX 1.20 | 38% | 46% | 48% |
| FX 1.40 | 40% | 48% | 51% |
| host overhead 50% | 37% | 44% | 46% |
| operator time x2 | **-11%** | 10% | 20% |
| automated (no operator) | 89% | 85% | 80% |

Reading: tokens are not the risk; **the person's time is**. Every tier stays positive under the worst token mix (no caching at all) and any plausible FX. Doubling operator minutes makes the small run lose money; that is the first thing to watch in the evidence of the first paid runs, and the first thing automation removes.

## 9. How we protect ourselves

1. **Hard caps on every run:** workers (5 / 10 / 20), tokens (1M / 3M / 10M Sonnet-equivalent), wall clock (15 / 25 / 45 min), materials (50 / 100 / 100 MB). Token budgets already include the +25% queen/host allowance in our cost.
2. **On overrun the run stops at the cap.** The vault holds what was done up to then and is delivered as normal. No extra charge, no refund for a stopped run. Honest status: today the wall-clock cap is enforced by the runner and the operator, and tokens are metered per worker after the fact; the 25% overhead and the base-vs-worst-mix headroom (section 8) are what absorb a run that overshoots before it is stopped.
3. **No network.** The run's Agent Behaviour Policy allows no egress; materials are uploaded. That removes the cost and risk of agents fetching from the internet.
4. **A minimum price that covers the person.** No tier is priced below its operator cost plus tokens; £5 is not offered until runs are automated (section 3).
5. **Margin target 40%, floor 35% at the base mix**, and every run tier positive at the worst token mix. Compute meets the floor with EC2 20% dearer than quoted.
6. **Capped hours** on repository subscriptions; more time is sold as expert time.
7. **BYOK** moves the token risk to the customer's own account for anyone who wants larger or longer work.
8. **Published vaults:** publishing gives away the read key and cannot be undone, so it is an explicit choice per run (default: zip).
9. **Re-price triggers:** change any input in `model.py` (model prices, FX, EC2 confirmed on AWS's price list, measured operator minutes, measured host tokens) and re-run; if any tier falls under the 35% floor, its price or caps change before the next sale.
