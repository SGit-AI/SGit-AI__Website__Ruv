# Getting started with ruv.sgit: a ladder of examples, and run vaults that end sealed and published

*Source: <https://ruv.sgit.ai/articles/getting-started.html> · article v0.1.0 (DRAFT) · generated from the same source as the page, so the two cannot drift.*

By Dinis Cruz · 2026-10-16

**Abstract.** DRAFT for Dinis to check. This is the brief for the ruv.sgit team and an article for anyone who wants to try ruv.sgit. It proposes two things. First, a new end for every run: once a run has been measured, the vault key is deleted, so the vault can no longer change, because it represents a run that has ended; then the vault is either published with its read key, handed over privately, or deleted. Second, a ladder of seven examples, from a one-file hello world to the killer workflow (an explainer animation made from a brief by a Ruflo hive) and a meta example (the run that wrote this article), each on a standard page with its brief, its output, its sealed vault and its ledger entry. The thirteen run vaults made so far were deleted by design, so the examples will be re-runs. Four runs, r15 to r18, build it; nine open questions have proposed answers.

---
*Written by Claude (Claude Code), worker "writer" in run r14-examples, from Dinis Cruz's voice memo of 16 October 2026, this site's runner, run specs and ledger, the sgit 0.21.0 command help, and the way [sgit.ai](https://sgit.ai/demos/vaults/index.html) and the [newsroom](https://newsroom.sgit.ai/vault/index.html) publish vaults. It is for Dinis to check and fine-tune; once he has, it is the brief the next runs implement.*

> **DRAFT v0.1.0.** Every command, path and page below is a proposal until Dinis signs it off. Commands marked *to be confirmed* are waiting for the first real run of the new ending, which another worker in this run (the "mechanic") is building now. Edit the source (`site/articles/src/getting-started.md`) and the implementation follows the edited version.

## In short

- **Examples, for three kinds of people.** Consultants who will deliver ruv.sgit and need to learn and test it; anyone who wants to try it; and us, developing the technology. In Dinis's words, the aim is examples that are "super easy to use", "from very very simple hello world examples to more complex ones that leverage vaults".
- **A new end for every run: seal.** Today a run ends with its vault deleted. From now on the last step of every run is deleting the *vault key*. Without it nobody can add a commit, so the vault is immutable: it represents a run, and the run has ended.
- **Then one of three things.** Publish the vault with its read key (examples and open work), hand the read key over privately (client work, private first), or delete the vault (scratch runs). The spec of each run says which; the default is private.
- **A ladder of seven examples.** Hello world; two workers and a merge; a mandate; memory across runs; the killer workflow, an explainer animation made from a brief; a talk built as a timeline; and the meta example, this run itself.
- **One page format for every example.** The brief, the output, the vault (open it, clone it, what is inside, its history drawn), the ledger entry, and "try it yourself". The model is sgit.ai's [published demo vaults](https://sgit.ai/demos/vaults/index.html).
- **An honest gap.** The thirteen run vaults in the ledger were deleted on purpose, so none of them can be published. Their briefs, outputs and measurements still exist; the examples will be re-runs of the important ones.
- **Four runs to build it** (r15 to r18), each with acceptance checks, and **nine open questions** with proposed answers.

## Why examples, and for whom

ruv.sgit is a Ruflo hive (Ruflo is MIT, by rUv / ruvnet) whose shared memory and output is one sgit vault per run, with each role bounded by an Agent Behaviour Policy (ABP). The site already proves that the pieces work: thirteen runs in the [ledger](../ruv-sgit/ledger/index.html), 74 vault commits, 48 worker branches, no plaintext found in what the server stored (0 of 483 probed text fragments), and every fresh clone identical to what the workers delivered (13 of 13). What it does not yet have is a way in. A reader can see that runs happened; they cannot easily make one.

Dinis named who the examples are for: "not only consultants that are going to be providing these services can learn and test, but also people can try it out". So the ladder serves three readers:

| Reader | What they need from an example |
|---|---|
| A consultant who will deliver ruv.sgit | A safe place to learn each moving part, one at a time, and a known-good result to compare their own run with |
| Anyone trying it | Something that runs on a laptop in minutes, with nothing to sign up for, and an obvious "it worked" at the end |
| Us, developing it | A fixed set of runs to repeat after every change to the runner, sgit or Ruflo: a regression suite that is also documentation |

The third use matters as much as the first two. If example 01 still produces the same ledger shape after an upgrade, the upgrade did not break the basics.

## The new end of a run: seal, then publish, hand over or delete

### Today

The runner, [`poc/ruv-sgit/ruvsgit.py`](https://github.com/SGit-AI/SGit-AI__Website__Ruv/blob/dev/poc/ruv-sgit/ruvsgit.py), does four things:

1. **open**: a fresh Ruflo hive (one specialist per role, one task per deliverable) and a new vault on a local SG/Send vault server, with the brief committed;
2. **deliver**: each worker's output committed on its own branch (`w-<worker>`), pushed, and merged into `current`;
3. **close**: measure the vault (history, files, bytes, what the server stored, a plaintext probe, a fresh clone compared with the working copy) and write the ledger entry;
4. **delete**: remove the vault's objects from the server store, check that a clone with the key now fails, and destroy the key and the working copy.

The runs were ephemeral by design: the point was to show that a vault can carry a run and then be gone. It worked (12 of the 12 runs with a delete check left no store paths behind, and a clone afterwards failed), and it means there is nothing left to publish.

### The lifecycle from now on

*(Figure: see the HTML version.)*

1. **open**, **deliver**, **close**: as today.
2. **Decide, from the spec.** Each spec gains one field, `"visibility"`, with three values: `"public"`, `"private"` (the default) or `"delete"`.
3. **Prepare the way in.** For `public`, `sgit publish --visibility public` writes a static folder that includes the read key; it is pushed to the sgraph vault server and only the reference (server, vault id, read key, viewer URL, clone command) goes into the site. *(Decided 17 Oct: first built as a static folder under `site/vaults/<run>/`, then moved to the server; see the update below.)* For `private`, the read key is written to a 0600 file outside the repository for handing over. For `delete`, today's delete step runs.
4. **Seal: delete the vault key.** Always the last step. The key file in `~/.ruv-sgit/runs/<run>/`, the working copy (whose `.sg_vault` folder also holds the key) and every temporary clone are removed. The ledger records `sealed_at`.

Dinis put the principle plainly: "the last step of the vault is always the deletion of the vault key, because the vault should not be modified anymore, because the vault represents a run, and the run has ended". The order inside step 3 and 4 matters: publishing needs the key, so the read surface is prepared first and the key is destroyed straight after, in the same step of the runner.

### Dinis's four questions, answered

| Question | Proposed answer |
|---|---|
| Is the data in the vault confidential or not? | A decision per run, written in the spec as `"visibility"` before the run starts, not after. The default is `private`. Client work is always private first, as the [next-phase brief](next-phase.html) already decided. |
| Can we publish the vault? | Only when its content is meant to be public: examples, the site's own runs, open work. Publishing the read key is irreversible (CLAUDE.md, rule 1): anyone who has it can read the vault for as long as a copy exists. So a public run is checked before it is sealed: no keys, no tokens, no personal data, nothing a client owns, the same audit sgit.ai's demo pages describe ("Audited before publishing"). |
| Who accesses it? | Anyone with the read key. For a public vault that is anyone who opens its page on ruv.sgit.ai; for a private one, the people the read key was handed to. Nobody can write to it, including us, because the vault key no longer exists. |
| How is it passed to the next round? | The next run clones it read-only as an input, with the read key: from the published folder for a public vault, from the server for a private one. The new run has its own vault; the old one is never changed. That is example 04. |

### How a sealed vault is published (to be confirmed by the mechanic's run)

> **Update, 17 Oct (run r15-publish).** Dinis decided the vaults live on the sgraph vault server, not in the repository. `seal` now pushes the run's vault (every branch, full history) to `https://dev.send.sgraph.ai`, checks a fresh read-only clone and the vault UI at `https://dev.vault.sgraph.ai`, deletes the local copy, then destroys the vault key. The site keeps only the reference, and lists the published vaults, each open in the vault UI, on [the examples page](../examples/index.html). The static folders under `site/vaults/` are removed; `example-01-hello` and `r14-examples` are superseded by `example-01-hello-v2` and `example-07-meta`. The sketch below is the first version, kept as written.

The intended mechanism follows how sgit.ai publishes its [demo vaults](https://sgit.ai/demos/vaults/blackhat-eu-2025/index.html), where each page shows the read key, a link that opens the vault read-only in the official web UI, and a one-line clone command:

```
# inside the run's working copy, after close, before the key is deleted (to be confirmed)
sgit publish --visibility public --yes        # writes the static folder: cover.json, index.html, manifest.json, the read key file
# copied by the runner to site/vaults/<run>/

# a reader, afterwards (to be confirmed)
sgit clone <read-key>:<vault-id> --base-url https://ruv.sgit.ai/vaults/<run> --transport static my-copy
```

What is already known, from `sgit publish --help` (sgit-ai 0.21.0) and from publishing this site's POC vault on 14 October (see `evidence/notes.md` and [the published POC vault](../vault/index.html)):

- `--visibility public` puts the READ KEY in the folder; the help itself says "irreversible". `bare` (the default) publishes no key.
- `--bundles` also writes a head snapshot and per-commit delta zips; `--api-spec` writes a description of the folder.
- `sgit clone` has a `static` transport ("any GET host, read-only") and accepts `<read-key-hex>:<vault-id>`, which it detects as read-only.
- In the POC vault, the published folder *referenced* the store objects rather than copying them, so the static host served the loader only and the contents came from the vault server. Our run vaults live on a local server that stops after the run. So the mechanic has to confirm that the folder under `site/vaults/<run>/` carries the encrypted objects too (copied, or as `--bundles`), and that a clone from it works with no server running. Example 01 is the proof.

## The example ladder

Seven rungs. Each one adds one idea to the one before. The times are measured where a past run did the same thing, and marked *estimate* where none did.

### 01 Hello world

- **What it shows**: the whole lifecycle with nothing else in the way: open, deliver, close, seal, publish.
- **The brief**: one worker, `hello`, role `writer`, task "write hello.md: one line saying which run this is and when", `"visibility": "public"`.
- **Workers**: one, scripted (no model).
- **What you get**: a vault with 3 commits (init, brief, the delivery), the brief and one file, sealed and published on the sgraph vault server (now `example-01-hello-v2`, open in the vault UI from [the examples page](../examples/index.html)), and a ledger entry.
- **How long**: about half a minute. The first run on this site, `smoke-1`, did the same with one 72-byte file: 23 seconds from open to close.
- **What you learn**: what a run, a branch, a ledger entry, a read key and a seal are.
- **Reverse-engineers**: `smoke-1` in the [ledger](../ruv-sgit/ledger/index.html). Being built now by the mechanic.

### 02 Two workers, two branches, a merge

- **What it shows**: parallel workers that cannot overwrite each other: each delivers on its own branch, and both are merged into `current`.
- **The brief**: two scripted workers, `left` and `right`, each writing one file; then a third, `editor`, that writes `summary.md` naming both.
- **What you get**: a vault with three `w-*` branches merged, and the vault's history drawn as a graph on the example page.
- **How long**: under a minute (*estimate*).
- **What you learn**: branches per worker, merges, and how to read a vault's history (`sgit history log --json`).
- **Reverse-engineers**: the branch pattern every run since `r2-materials` used, and the [history slide](../talk/slides/history/index.html) from the talk, which draws a real run's commits.

### 03 A mandate

- **What it shows**: an Agent Behaviour Policy. Two workers ask to do the same things; one is allowed, one is denied, and each decision leaves a receipt.
- **The brief**: an ABP with two roles: `writer` may write files in its lane; `tester` may not write files and may not reach the network. The worker actions go through Ruflo's own policy engine in enforce mode, with the ABP compiled into its rules, exactly as [POC1](../pocs.html#poc1) does through the engine's library API (no faked terminal, no weakened control).
- **What you get**: the decisions table (allowed, denied, approval required, each with the ABP row that decided it), the engine's ledger check, and both in the sealed vault.
- **How long**: about a minute (*estimate*; POC1 runs in seconds).
- **What you learn**: what a mandate is, how a row becomes a rule, and what a receipt looks like.
- **Reverse-engineers**: POC1 and the [ABP slide](../talk/slides/abp/index.html). Note: the thirteen runs so far were not policy-gated; this would be the first run that is.

### 04 Memory across runs

- **What it shows**: run B reads what run A left, without being able to change it.
- **The brief**: run A is example 01. Run B's spec names it as an input: `"inputs": [{"run": "example-01-hello", "read": "vaults/example-01-hello/"}]`. Run B clones it read-only into `inputs/`, and its worker writes `reply.md` quoting A's file and A's head commit.
- **What you get**: two sealed vaults; B's brief and output point at A's head commit, so the chain can be checked.
- **How long**: about a minute (*estimate*).
- **What you learn**: how a sealed vault becomes the next run's memory, and why read-only matters: B cannot rewrite A's history, and neither can anyone else.
- **Reverse-engineers**: [POC2](../pocs.html#poc2) (agent memory kept in a vault) and the talk's line about memory you can trust (the [claim slide](../talk/slides/claim/index.html)).

### 05 The killer workflow: an explainer animation from a brief

Dinis: "the creation of those animations to explain stuff is the killer one".

- **What it shows**: a Ruflo hive with three roles turning a one-paragraph brief into a live, controllable explainer animation.
- **The brief**: a subject (for the first one: "what a sealed vault is"), an audience, a length in seconds, and the slide contract.
- **Workers**: `researcher` (collects the facts and numbers, each with its source, into `facts.json`), `animator` (builds the page), `editor` (checks it against the brief and the contract, and against the facts, and writes the review).
- **The slide contract**, as used for the talk ([the talk player](the-talk-player.html) lists it): a standalone page on a fixed 1280×600 canvas scaled to fit; colours only from the theme tokens; [`clock.js`](../assets/clock.js) loaded first and one timeline on `requestAnimationFrame`, so it can be paused, sped up, stepped and sought; `?review` shows the final frame, `?once` plays once and holds, `?ruvt=` starts part-way; numbers read from data files, never typed in.
- **What you get**: the animation, running live on the example page; the facts with their sources; the editor's review; all of it in the sealed vault.
- **How long**: about 7 to 9 minutes. Run `r8-explain` made two such slides in 7 minutes 15 seconds from open to close, with its two animators using about 90,500 and 118,400 tokens; `r7-claim` took 8 minutes 47 seconds for two.
- **What you learn**: how a brief becomes a moving explanation, and how the vault shows how it was made.
- **Reverse-engineers**: the talk's slides made by runs: [what an sgit vault is](../talk/slides/sgit/index.html) and [what an ABP is](../talk/slides/abp/index.html) (`r8-explain`, spec [`r8-explain.spec.json`](https://github.com/SGit-AI/SGit-AI__Website__Ruv/blob/dev/poc/ruv-sgit/runs/r8-explain.spec.json)); [the claim](../talk/slides/claim/index.html) (`r7-claim`); the definition animations, [equation](../ruv-sgit/define/equation/index.html), [layers](../ruv-sgit/define/layers/index.html) and [journey](../ruv-sgit/define/journey/index.html) (`r3-define`); and [the studio](the-studio.html), whose seven versions are the same idea pushed further.

### 06 A talk built as a timeline

- **What it shows**: several explainer animations put in order, with words and timings, played by the talk player.
- **The brief**: a three-beat talk of about a minute: example 05's animation, example 02's history, and a closing statement. Workers: `writer` (the beats and the words), `timer` (the timings, checked so the beats add up), `editor`.
- **What you get**: a `talk-example.json` the [player](../talk/player.html?talk=talk-10.json) plays, live slides included, and an offline build.
- **How long**: about 5 minutes (*estimate*), if example 05 is reused.
- **What you learn**: a presentation as data: a file of beats, each with a start, a duration, a slide and the words.
- **Reverse-engineers**: `talk-10.json` and `talk-5.json`, the timelines of 15 October, and the articles [the talk player](the-talk-player.html) and [the talk, live](the-talk-live.html).

### 07 The meta example: the run that made the examples

- **What it shows**: a real run of real work, published: the brief that asked for this article and the examples page, the two workers' deliveries, and the measurements.
- **The brief**: [`r14-examples.spec.json`](https://github.com/SGit-AI/SGit-AI__Website__Ruv/blob/dev/poc/ruv-sgit/runs/r14-examples.spec.json): the `mechanic` (the runner's new ending and example 01) and the `writer` (this article).
- **What you get**: this article and the runner change, inside a sealed, published vault, with the voice memo's summary as the brief's feedback.
- **How long**: the length of the run; the ledger will say.
- **What you learn**: that the examples are not staged: the same lifecycle carried the work that defined them.
- **Note**: if run r14 is closed with the new ending, its own vault becomes example 07. If not, r18 re-runs it.

## The example page: the standard way

Dinis asked for "a standard way", listing for each example "the original briefs, the output, and the vault". Each example gets one page, `site/examples/<id>/index.html`, with five parts in this order:

| Part | What it shows | Where it comes from |
|---|---|---|
| (a) The brief | The spec rendered: purpose, feedback, each worker's id, role, task and output path, and the visibility | `brief/spec.json` in the vault, the same as `poc/ruv-sgit/runs/<run>.spec.json` |
| (b) The output | The deliverable, rendered. An animation runs live in a frame, with play, pause and review (it follows the slide contract) | The delivered files, from the site |
| (c) The vault | **Open it**: a link to the official read-only web UI with the read key, as on sgit.ai. **Clone it**: the one-line command with the read key. **What is inside**: the file tree from `manifest.json`. **Its history, drawn**: the commits and `w-*` branches as a graph, reusing the history slide's drawing | `site/vaults/<run>/` and the ledger entry |
| (d) The ledger entry | Commits, files, bytes, branches with write and merge times, the plaintext probe, the clone check, `sealed_at`, and whether the key file is gone | `data/vaults.json` |
| (e) Try it yourself | The exact commands, copyable: `bash scripts/offline.sh setup` once, then the example's run, then `./run-website-locally.sh` to see it | The repository |

The "history, drawn" part answers Dinis's request for runs "where we actually use the visualisation of the vaults": every example page shows its own vault, not a diagram of one.

An index page, `site/examples/index.html`, lists the ladder: number, name, one line, how long, and a link; the menu gets an "Examples" entry. Like every page on this site, it reads its numbers from the data files when it loads.

## The plan

Four runs, in order, each after the one before is reviewed. Run numbers continue from r14; the runs proposed in the [next-phase brief](next-phase.html) take the numbers after these, or run in between, as Dinis prefers.

| Run | Purpose | Workers |
|---|---|---|
| **r15-seal** | Seal and publish in the runner, proven by example 01 (if the mechanic's work in r14 is not finished, this completes it) | mechanic (`ruvsgit.py`: `seal` and `publish`, the `visibility` field, `sealed_at`), checker (the acceptance checks as a script), page (the first example page) |
| **r16-ladder** | Examples 02 to 04 | three scripted example workers, one per example; page (their pages); editor |
| **r17-explainer** | Examples 05 and 06 | researcher, animator, editor (example 05, a hive); writer, timer (example 06); page |
| **r18-meta** | Example 07, the examples index and the menu entry | archivist (r14's vault published, or r14 re-run), page (the index), indexer (`llms.txt`, the README, the version history), editor |

### Acceptance checks

**r15-seal**

- Example 01 runs end to end from `scripts/offline.sh` with no network.
- After the run: the key file is gone, the working copy is gone, and a search of `~/.ruv-sgit` finds no vault key for the run.
- A clone from `site/vaults/example-01-hello/`, with the read key and no vault server running, gets back files identical to what the worker delivered.
- A commit attempted on that read-only clone is refused.
- The ledger entry has `sealed_at` and `visibility`; `validate.py` passes (its secret check still finds no vault key or token anywhere in `site/`; the published read key is the one string it allows on purpose).
- A run with `"visibility": "private"` writes nothing under `site/vaults/`.

**r16-ladder**

- Example 02's page draws three merged branches that match `sgit history log --json` for its vault.
- Example 03's decisions table matches the engine's output, with at least one allowed and one denied action, and the engine's ledger check is valid.
- Example 04's output names example 01's head commit, and that commit is in example 01's published manifest.

**r17-explainer**

- Example 05's animation passes the slide contract: `?review`, `?once` and `?ruvt=` work, it pauses with the player, and every number on it is read from a file with a source.
- Example 06's beats add up to the talk's length (the player's own check and `validate.py`).
- Both pages are checked in a browser at 1366 and at 390 wide.

**r18-meta**

- Example 07's page shows r14's brief, the outputs and the vault, or the re-run's, and says which.
- The examples index lists seven examples, each page loads, and the menu has the entry.
- `validate.py` passes; every new page is in `llms.txt`.

## Open questions for Dinis

Each has a proposed answer. A "yes" accepts it.

1. **Where do published vaults live?** *Decided 17 Oct:* on the sgraph vault server (dev.send.sgraph.ai), shown in its vault UI; the site keeps only the reference. *First proposal:* on this site, under `ruv.sgit.ai/vaults/<run>/`, next to their example pages, and listed in sgit.ai's catalogue with a link here, rather than moved to sgit.ai.
2. **Keep a server copy after sealing?** *Proposed:* for public vaults, also push the sealed vault to the hosted sgit server, so the official web UI link works as it does for sgit.ai's demos; the static folder stays the copy we control. For private vaults, keep the server copy until the client has their own, then delete it.
3. **Naming.** *Proposed:* `example-01-hello` to `example-07-meta` for the example runs; a re-run of an old run keeps its old name with `-rerun` (`r8-explain-rerun`).
4. **Model or scripted workers?** *Proposed:* scripted for 01 to 04, so anyone can run them with no API key and get the same result each time; a model for 05 and 06, where the work needs one; 07 is whatever r14 was (Claude Code workers).
5. **Size limit for a published vault.** *Proposed:* 5 MB per vault for the examples. The largest run so far, `r10-articles`, held about 6.9 MB of plaintext; examples should be small enough to clone in seconds.
6. **The seal is permanent; is that what we want for the examples?** *Proposed:* yes. A fixed example is re-run as a new vault with a new name, never edited, so its page always points at what it says.
7. **Which past runs are re-run as examples?** *Proposed:* `r8-explain` (the clearest explainer) inside example 05, and nothing else for now; the rest stay as ledger entries.
8. **A check before publishing.** *Proposed:* the runner refuses to publish if the secret check finds anything shaped like a key or token in the delivered files, and the spec must say `"visibility": "public"` explicitly; no flag on the command line can override either.
9. **Licence of published example content.** *Proposed:* the same as the site: code Apache-2.0, text CC BY 4.0 (as decided for the next phase), rUv's projects credited as MIT, by rUv / ruvnet.

## What this does not claim

- **Nothing here is built yet**, except what the mechanic is building in this run. The examples, their pages and the index do not exist until runs r15 to r18 make them.
- **The thirteen past run vaults cannot be published.** They were deleted by design; only their specs, outputs and ledger entries remain. Every example is a new run.
- **The publish and clone commands are not confirmed.** They follow `sgit publish --help` and sgit.ai's demo pages; the exact form waits for example 01.
- **"Immutable" means no new commits can be made.** It does not stop anyone holding a copy from deleting their copy, and the static folder is ordinary files in this site's git history, where any change would show.
- **A published read key cannot be taken back.** Removing the folder later does not remove copies already made.
- **The times are estimates** where no past run did the same thing; they say so.
- **The past runs were not policy-gated.** Example 03 would be the first run that is.
- **Not rUv's offer.** This builds on his open-source projects (MIT, by rUv / ruvnet); it is not his service and does not speak for him.

## Where this comes from

Dinis Cruz's voice memo of 16 October 2026 (quoted where his words are used) and the run spec [`r14-examples.spec.json`](https://github.com/SGit-AI/SGit-AI__Website__Ruv/blob/dev/poc/ruv-sgit/runs/r14-examples.spec.json); the runner [`ruvsgit.py`](https://github.com/SGit-AI/SGit-AI__Website__Ruv/blob/dev/poc/ruv-sgit/ruvsgit.py); the ledger [`data/vaults.json`](../data/vaults.json) (13 runs; the totals and times above are computed from it); `docs/01-sgit-cheatsheet.md` and `sgit publish --help` / `sgit clone --help` (sgit-ai 0.21.0, run on 16 October); `evidence/notes.md` (publishing the POC vault, 14 October); sgit.ai's [published vaults](https://sgit.ai/demos/vaults/index.html) and [Black Hat Europe 2025 demo page](https://sgit.ai/demos/vaults/blackhat-eu-2025/index.html) and the newsroom's [vault page](https://newsroom.sgit.ai/vault/index.html), read on 16 October; and the articles [the studio](the-studio.html), [the talk player](the-talk-player.html) and [from the talk to the service](next-phase.html).

## Changes

- **v0.1.0 (DRAFT), 16 October 2026.** First draft, for Dinis to review (run r14-examples, worker writer).
