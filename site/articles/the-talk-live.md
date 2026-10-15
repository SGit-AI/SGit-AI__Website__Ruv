# The talk, live: thirteen of its animations, each with its own controls

*Source: <https://ruv.sgit.ai/articles/the-talk-live.html> · article v1.0.0 · generated from the same source as the page, so the two cannot drift.*

By Dinis Cruz · 2026-10-15

**Abstract.** The talk "Autonomy with a mandate and a memory" (Agentic Engineering Live, London, 15 October 2026) was 26 slides and 11 minutes 38 seconds, most of them live web pages rather than pictures. This article puts thirteen of those live pages on one page, in talk order, each in its own frame with play, pause, restart and step controls, and with the context the talk had no time for: what each one shows, which ruv.sgit run or studio run made it, and which data file its numbers are read from. The frames are the real pages, not recordings: they read the same ledger and POC files the site does, and they are driven by the same virtual clock as the talk player. It is the short companion to the long read, which walks every step with screenshots.

---
*Written by Claude (Claude Code) from the session that built the talk, its commits and its run records; reviewed by Dinis Cruz.*

## In short

- **The talk ran itself.** It is a timeline (`site/talk/talk-10.json`) played by the [talk player](../talk/player.html?talk=talk-10.json). Afterwards Dinis wrote: "I actually let it run in autopilot, and he actually did a great job, and I just spoke over it."
- **Most slides are live pages.** Each one fetches its numbers from the site's data files (the vault ledger, the POC1 report, the offers) when it loads, so what you see below is computed now, from the same files, not pasted in.
- **Each frame has its own controls.** ▶ plays, ❚❚ pauses, ↺ restarts, ‹ and › move between the *ends* of the page's steps (each stop is a finished picture), and "open full size" opens the page on its own.
- **Light on purpose.** A frame loads only when it scrolls near the screen, starts paused at the end of its first step, and pauses again if you scroll away.
- **Where to go next.** The [long read](the-talk-long-read.html) tells the whole talk step by step with screenshots; the [player](../talk/player.html?talk=talk-10.json) plays it as it was given.

## How to use this page

Each section below is one slide. Read the paragraph, then press ▶, or press › to jump to the end of the next step. The label under the frame says which step you are on, its name (the page's own, from `window.RUV_STEPS` where it has one), and how far into the page you are. The times in the headings are where the slide sat in the 11:38 talk.

The pages were designed for a 16:9 slide, so each is drawn at 1280×720 (960×540 on a phone) and scaled to fit the column; on a phone it is small, and "open full size" is the better way to read it. Every frame wears the theme you have chosen for this site (the theme button at the top); change it, and the frames change with it. The one exception is the city of vaults, a 3D scene that is always dark.

## 1. The equation (0:00, slide 1)

The talk opened on its own definition: many hands (a Ruflo hive) plus a memory (sgit vaults) plus a mandate (Agent Behaviour Policies) equals ruv.sgit. Each term is drawn from a recorded run: the hive and the vault from the ledger entry of run r2-materials, the mandate from POC1's report (`data/vaults.json`, `data/report.json`, `data/abp.json`).

It was made by ruv.sgit run r3-define, whose brief was Dinis's line "in fact it needs its own animations". That run gave the definition three takes in parallel (the equation, the layers, a journey) plus an editor; the equation came from the designer's branch, `w-equation`, with a second take on `w-equation-r2`. The run then measured its vault (9 commits, 0 plaintext fragments found on the server) and deleted it.

*(Figure: see the HTML version.)*

## 2. The claim (0:30, slide 2)

Dinis's feedback on the second slide was short: "use ruv.sgit to create a better view and animation for this. Today it is four lines of text." Run r7-claim turned the four lines into one picture. A worker learns something; the item is encrypted before it leaves the agent (the server holds ciphertext only: zero plaintext found across every run in the ledger); it is versioned (who learned what, and when); it is scoped to one run (the vault is measured, then deleted); and the agent has a written mandate (POC1: six of eleven actions stopped).

The counts are read from `data/vaults.json` and `data/report.json` when the page loads, so the "every run" figure grows as runs are added.

*(Figure: see the HTML version.)*

## 3. rUv's stack, one picture (1:01, slide 4)

Slide 3 was an image model's infographic of rUv's stack; slide 4 is the same stack drawn as a live page by the same run as the claim (r7-claim, branch `w-stack`). Bottom up: RVM, the capability VM; RuVector, the memory; Ruflo, the orchestrator with queens and workers; MetaHarness, which assembles a harness for a host; and the hosts on top. All of it is MIT, by rUv (ruvnet).

The column to the right is where sgit plugs in, and it plugs in at three places only: a vault around the memory, one vault per hive run, and an ABP compiled into Ruflo's own policy engine. Nothing in rUv's stack is replaced.

*(Figure: see the HTML version.)*

## 4. RuVector, in its own words (1:23, slide 5)

This slide matters most for accuracy. Earlier in the day the site had said RuVector has "no encryption at rest" and "no versioning". The researcher in run r4-hero read RuVector's README and found that neither phrase is in it, and the site was corrected everywhere to quote it exactly. Dinis then asked for the slide to show "RuVector's README itself, highlighted, and say what RuVector secures and where sgit adds (not 'where it stops')".

Run r6-talk's researcher (branch `w-ruvector`) built it: the README's security and governance section on screen, what RuVector secures (tamper-evident witness logs, snapshots, copy-on-write branches), the README's own statements that its witness logs do not encrypt memory content and that a delete does not automatically reach every snapshot, branch or copy, and then the three places where sgit adds around the files: client-side encryption (AES-256-GCM), a history you can clone anywhere, and a vault deleted with the run, with the delete checked.

*(Figure: see the HTML version.)*

## 5. What an sgit vault is (2:01, slide 6)

After a run-through, Dinis said the RuVector and layers slides were "brilliant" but that a ruv.sgit-made explanation of sgit, then of ABPs, was missing between them, and asked for shorter slides because he speaks fast. Run r8-explain made both, one worker each.

This one has three panels. Encrypted on the client: a folder whose files are encrypted (AES-256-GCM) before anything leaves the machine, so the server stores ciphertext and whoever has the vault key has the memory. Works like git: commit, branch, merge, push, clone, each around a second against our local vault server (the timings are the ledger's own `ops`). Why agents: a shared, versioned memory that a fresh clone anywhere brings back, or an ephemeral one, one vault per run, deleted and checked.

*(Figure: see the HTML version.)*

## 6. What an Agent Behaviour Policy is (2:29, slide 7)

The second r8-explain slide. An ABP is a written mandate per role that a person can read: one row per capability, in a small grammar of verb, object and reach; each row says yes, no or ask a human, why, and the barrier; and the whole policy has an owner and an end date (here Dinis Cruz, valid until 31 October 2026, from `data/abp.json`).

We did not build a new enforcer. The policy compiles into Ruflo's own policy engine, rUv's, in enforce mode: the 36 rows across six roles become its rules (`data/rules.json`). Then POC1's eleven real actions hit it: 4 denied, 2 sent to a human, 5 allowed, every decision a hash-chained receipt, and the chain valid (`data/report.json`).

*(Figure: see the HTML version.)*

## 7. ruv.sgit, in layers (2:57, slide 8)

The definition again, as three layers that build and then lie flat: the hive on top (a queen and workers, in parallel), the mandate in the middle (POC1's roles and gates; the panel says plainly that this was a separate run and that no ABP was compiled into the vault run), and the vault below (run r2-materials: its branches, its commits, measured, then deleted).

It came from the same run as the equation, r3-define, branch `w-layers`. Dinis used it as the quality bar for the rest of the talk: run r6-talk's brief asked for "every slide at the quality of the layers animation, no loops, with steps the player can move through".

*(Figure: see the HTML version.)*

## 8. One run's vault, commit by commit (4:07, slide 10)

"Slide 7 (history) needs more meat and the flows mapped" was Dinis's note; run r6-talk's animator (branch `w-history`) rebuilt it around a real vault: run r5-market's, from that afternoon. The brief lands on `current`; each of six workers gets its own branch, commits what it delivered and merges back, with how long each sgit step took in milliseconds; then the flow, mapped; then the measurements: 8 commits, 0 of 40 text fragments found in the server's store, a fresh clone identical, the vault deleted.

The last step is POC2, run locally: a coder and a tester each wrote their Ruflo memory to a vault, the folder was deleted, a fresh clone restored it, and Ruflo gave the same answers (`data/poc2-history.json`, `data/poc2-run.txt`).

*(Figure: see the HTML version.)*

## 9. ruv.sgit in motion (6:28, slide 16)

This page draws one run from its ledger entry alone: the hive starts, the vault is created and the brief committed, the workers work in parallel, each delivery lands on its own branch and merges into `current`, the vault is closed, measured and cloned fresh, and then deleted. The timings on screen are the run's own: every sgit call's milliseconds, scaled to fit.

In the talk it showed the newest run in the ledger. Here it is pinned to run r6-talk (`?run=r6-talk`), the run that made five of the slides on this page, so you can watch its six branches (five workers and the conductor's) land one at a time. The page itself was made earlier, by run r2-materials (branch `w-motion`), and later fixed by the conductor so its tiles no longer overlapped its footer at slide size.

*(Figure: see the HTML version.)*

## 10. How to read the ledger (7:08, slide 17)

Every ruv.sgit run leaves one row in a ledger (`data/vaults.json`). The slide reads one row cell by cell: the run and what it was for; the workers, each on its own branch; the commits; what was delivered and what the server held (all ciphertext); the probe (fragments of the delivered files, searched for in every byte the server stored); a fresh clone with the key; then the delete and its check (no store paths left, and a clone with the key fails). Then every run, and the totals.

When this was written the ledger held nine runs (smoke-1 to r9-ask): 57 commits, 0 plaintext fragments found, every fresh clone identical, every vault deleted. The page reads the file live, so it will show more rows as later runs close. It was made by run r6-talk's animator on branch `w-ledger`.

*(Figure: see the HTML version.)*

## 11. The city of vaults (7:42, slide 18)

This one is older than ruv.sgit, and it is the reason ruv.sgit exists. In studio run 1, a Ruflo hive-mind (a queen and eight specialists, 31 calls, none failed) coordinated seven Claude Code subagents that built seven animations in parallel, about 630,000 tokens in all (629,857 by the host's usage report, `studio/run.json`). This was version 7: 102,599 tokens, 560 seconds. But the hive's shared memory said OK on a set and "key not found" on the very next get, so results travelled as broadcasts. That run had no vault; a vault added alongside the hive is what ruv.sgit brings.

The picture: each role's branch is a street, each commit a floor, and the mandate is a wall with gates. The first floors are POC2's real vault history; the streets are illustrative; then POC1's eleven actions drive out twice, once under Ruflo's default and once against the ABP.

*(Figure: see the HTML version.)*

## 12. Four ways to work with us (8:32, slide 20)

Run r5-market wrote the business model, and run r6-talk's strategist (branch `w-services`) explained it visually, one act per service: a task run on our infrastructure (a Ruflo queen and workers inside an ephemeral sgit vault, each role under its own ABP, no internet; £10, £20 or £50 a run); dedicated compute (a machine started for the task, the vault created inside it); a maintained private repository of the whole setup (from £149 a month); and expert time. They mix and match.

The prices are read from `data/offers.json`, the same file the shop uses, so the slide and the shop cannot disagree.

*(Figure: see the HTML version.)*

## 13. The shop (9:18, slide 21)

A guided tour of [the shop](../shop/index.html), built from screenshots of the real shop page: twelve items in four groups; an option changes a price (a Team run with your own model key drops from £20 to £17); add a Team repository subscription (£499) and a day of expert time (£1,500) and the cart says £2,016; check out with who you are and what you want done; and then no card form. The order is written into an email to agent@riskmandate.ai, sent from your own email app, and a person follows up. No payment is taken online.

It was made by run r6-talk's builder (branch `w-shop`, 20 files, most of them the screenshots); the element positions it highlights were recorded by a Playwright check of the shop.

*(Figure: see the HTML version.)*

## How the frames are driven

Every live page in the talk loads `assets/clock.js` first. It replaces the page's sense of time (`performance.now`, `Date.now`, `requestAnimationFrame`, timers, CSS and Web Animations) with one virtual clock, so a page can be paused, sped up and moved to any second without being rewritten. It was added to the player after Dinis's note that the animations did not stop when the talk did.

This article uses the same clock through each frame's `contentWindow.RuvClock` (same origin, so no messages needed): `pause()`, `play()`, `seek(t)` and `elapsed()`. Each frame loads with `?once` (play once and hold, rather than loop) and `?ruvpaused`, waits until the page has its data and its steps, and then jumps to the end of the first step. The steps come from the page's own `window.RUV_STEPS` where it publishes one; for the four older pages that do not (the equation, the layers, motion and the city), the article lists them, taken from the page's timeline or measured by sampling its captions.

The controls stop at the *end* of each step, one second before the next step starts. That is the player's rule too, and it came from Dinis, on the day of the talk, shortly before it: "for each step you need to have two moments, the begining of the step and the end of the step, so that I can move forward and see the end of that section". On a live page the start of a step is often a blank frame, so only the ends are worth stopping at. Moving forwards fast-forwards the page in 100 ms frames; moving backwards reloads it paused and fast-forwards to the earlier point, because an animation cannot run in reverse.

All of it is one file with no dependencies, [`assets/live-frames.js`](../assets/live-frames.js).

## What this does not claim

- **It is not the whole talk.** Thirteen of 26 slides are here: the ones that stand on their own. The image slide, the vault-lanes and studio slides, the table, the ask, the closing slides and the extras are in the [long read](the-talk-long-read.html) and the [player](../talk/player.html?talk=talk-10.json).
- **The frames show today's data.** The pages read the ledger and the POC files when they load. The ledger grows as runs close, so the "every run" totals in the claim, the ledger and the sgit slides can be higher than they were on stage; the per-run numbers quoted above are for runs that are closed and do not change.
- **The steps of four pages are ours, not theirs.** Where a page publishes no step list, the steps above were read from its code or measured; they are a convenience for reading, not part of the page.
- **Some slides were finished by hand.** The runs delivered the pages; the conductor (the main Claude Code session) then fixed some of them between runs, for example the motion page's layout at slide size. The commits say which.
- **Seconds are page seconds.** In the talk some pages ran faster than real time to fit their slot (motion at 1.2×); here they run at 1×.

## Where this comes from

- The talk timeline: `site/talk/talk-10.json` (slide order, times, the words said over each slide).
- The run records: `site/data/vaults.json` and `evidence/ruv-sgit/<run>.json` (branches per run, commits, probes, clones, deletes); each run's brief: `poc/ruv-sgit/runs/<run>.spec.json`.
- Studio run 1: `site/studio/run.json`.
- Dinis's notes, quoted from his messages during the session, 14 and 15 October 2026.
- The commits: `git log` of [the repository](https://github.com/SGit-AI/SGit-AI__Website__Ruv).

rUv's projects (Ruflo, RuVector, AgentDB, MetaHarness, RVM) are MIT, by rUv / ruvnet. Our code is Apache-2.0. Questions: agent@riskmandate.ai.
