---
{"no": 2, "title": "Set it up: a brief any agent can follow to run a Ruflo hive with sgit vaults as its bus and its evidence", "author": "Dinis Cruz", "date": "2026-10-15", "version": "1.0.0", "tags": ["brief", "setup", "ruflo", "hive-mind", "sgit", "abp", "agents", "observability"], "abstract": "Point an agent at this page and say: set this up. It is written for any host that can run a shell: Claude Code, Claude on the web, ChatGPT, Lovable, a CI runner. It installs pinned versions of Ruflo and sgit, creates two vaults (a message bus with a lane per role, and one vault per run that keeps everything), starts a Ruflo hive with a queen and eight roles, runs the work under a written mandate, times every call and commit, and ends with one vault that is the evidence of the whole run. Each step has a check, and the rules about keys are not optional."}
---
## How to use this page

Give an agent this page (or its [.md twin](studio-setup-brief.md)) and one sentence: "Set this up and do run 1 with the objective below." The steps are in order; each has a check. If a command differs from what is written here, trust the tool's `--help`, and write the difference in the run's notes. The plan and the architecture behind it are in [The studio](the-studio.html).

## What you will have at the end

- A Ruflo hive: a queen, eight role workers, a task per deliverable.
- A bus vault (`studio-bus`): every message between agents, one lane per role, encrypted on the client.
- A run vault (`studio-run-<id>`): the brief, the mandate, every artefact, the trace, the hive's status. This vault is the evidence.
- A trace: every Ruflo call and every vault write, timed.

## 0. The rules (read first)

1. **Keys are secrets.** A vault key is shown once by `sgit create` and there is no reset. Keep it in the host's secret store or an environment variable. Never print it, log it, commit it, or pass it on a command line: pass it on stdin (`printf '%s' "$VAULT_KEY" | sgit clone - dir`).
2. **Publishing is a human's call.** `sgit publish --visibility public` publishes the vault's read key, for ever. Only for the run vault, and only when a named person says so.
3. **Do not work around a safety check.** Ruflo's policy admin asks for an interactive terminal; if your host has none, use the library engine or skip it. Do not fake a TTY.
4. **Record, do not invent.** Every number you report comes from the trace or the vault history.
5. **Pin versions.** Do not upgrade mid-run.

## 1. Install (pinned)

```
node --version        # 20 or later
python3 --version     # 3.11 or later
npm install ruflo@3.56.10
pip install sgit-ai==0.21.0
npx ruflo --version   # ruflo v3.56.10
sgit --version        # 0.21.0
```

Check: both version lines print. Ruflo is MIT, by rUv (ruvnet); it auto-starts a background daemon on some commands, so end every session with `npx ruflo daemon stop`.

## 2. Create the two vaults

You need an SG/Send access token (`SGIT_TOKEN`) from the person you work for.

```
sgit --token "$SGIT_TOKEN" create studio-bus          # prints the vault key ONCE: store it as SGIT_VAULT_KEY_BUS
sgit --token "$SGIT_TOKEN" create studio-run-001      # store as SGIT_VAULT_KEY_RUN
```

Seed each with a README commit and push before any script clones it (a vault with no commits cannot be cloned). Then clone the bus:

```
printf '%s' "$SGIT_VAULT_KEY_BUS" | sgit --token "$SGIT_TOKEN" clone - .vault-bus
```

Check: `cd .vault-bus && sgit history log --oneline` shows the README commit. sgit calls its default branch `current`.

## 3. Write the mandate

Copy the ABP format from this site ([data/abp.json](../data/abp.json), grammar `verb.object.reach`) and write one row set per role. The minimum for the studio:

| Role | Capability | Mandate | Barrier |
|---|---|---|---|
| every role | `write.file.project` | yes: its own lane and folder | the lane convention; review by the editor |
| every role | `send.endpoint.world` | no | default-deny egress; libraries from a pinned CDN only |
| every role | `read.credential.host` | no | keys only via the host's secret store |
| developer | `execute.process.self` | yes: a headless browser to check its work | sandbox |
| conductor | `create.record.world` | approval | a named human publishes the run vault |

Put it at `brief/abp.json` in the run folder.

## 4. Start the hive

Use the script from this repository (it times every call into `trace.jsonl`): `bash poc/poc7-studio/hive.sh out/run-001`. Or by hand:

```
npx ruflo hive-mind init -t hierarchical-mesh -c byzantine -m 12
npx ruflo hive-mind spawn -n 1 -t conductor -r specialist -p conductor   # once per role:
#   conductor librarian architect designer developer editor historian observer
npx ruflo hive-mind task -d "v1: <deliverable>" -p high                  # once per deliverable
npx ruflo hive-mind broadcast -m "<the brief in one line>" -f conductor
npx ruflo hive-mind memory -a set -k studio/spec -v "brief/spec.json"   # in 3.56.10 this did not persist across calls: use broadcast for anything you need back
npx ruflo hive-mind status
```

Check: `hive-mind status` lists the queen, eight workers and the tasks queued. Use a new, empty folder for every run: Ruflo anchors each project's policy ledger in `~/.config/ruflo/policy-trust/`, and a folder deleted and recreated at the same path is refused with `policy-anchor-log-missing` (its tamper check; never delete the anchor to get past it).

## 5. The run loop

For each task, the conductor assigns a worker; the worker reads only the brief and its inbox, does the work, and answers on its own lane.

```
lanes/<from-role>/<seq>-to-<to-role>.json    # one writer per lane: append, never edit
```

Write a message with `bash poc/poc7-studio/lane.sh <from> <to> msg.json trace.jsonl` (it calls `sgit write <path> --file msg.json --push --json` and times it). Each role works on its own branch (`sgit branch new <role>`); the conductor merges into `current` at milestones (`sgit branch switch current && sgit branch merge <role>`).

Who does the work depends on the host. In Claude Code, a subagent per task (run 1). Ruflo can also launch Claude Code itself (`npx ruflo hive-mind work`, `spawn --claude`); both skip permission prompts by default, so only use them in a sandbox you are allowed to run unattended. In ChatGPT, Claude on the web or Lovable, the host is the worker: do the tasks in turn and write each answer to its lane.

The editor checks every number in every artefact against the data before the task is closed. The librarian keeps `brief/spec.json` current and labels anything proposed as proposed.

## 6. Observe

| Measure | How |
|---|---|
| Ruflo calls | `trace.jsonl`: seq, actor, command, exit code, start, milliseconds |
| Messages | One vault commit per message: `sgit history log --json` gives author, time, message |
| Network | `sgit --debug <command>` shows traffic with timing; `sgit dev profile` profiles one operation |
| Deliverables | Wall clock from task to checked file; file size; sha256 recorded in hive memory |
| Tokens | From the host (per worker), written into the run notes |

## 7. Close the run: one vault is the evidence

```
bash poc/poc7-studio/close.sh out/run-001     # broadcasts each deliverable's sha256 to the hive, reads it back, packs out/run-001/run/
VAULT_KEY="$SGIT_VAULT_KEY_RUN" SGIT_TOKEN="$SGIT_TOKEN" scripts/vault_write.sh out/run-001/run runs/001 "studio run 001"
npx ruflo daemon stop
```

Check: a fresh clone of the run vault on another machine has `brief/`, `versions/`, `trace/`, and `sgit history log` shows the run. Only if a named person approves: `sgit publish --visibility public --yes` in the run vault, and share the read key.

## 8. Report

Write five lines and no more: what was made (links), how long it took (from the trace), what it cost (from the host), what failed and why, and the run vault's id. Numbers only from the trace and the vault.

## A prompt to paste into any agent

```
Read https://ruv.sgit.ai/articles/studio-setup-brief.md and follow it step by step.
Objective for run 1: make <N> versions of an animation that explains <subject>,
from a simple diagram to a full 3D scene, each one self-contained HTML that reads its numbers from <data URLs>.
Use the roles conductor, librarian, architect, designer, developer, editor, historian, observer.
Rules: keys only from my secret store, never printed; do not publish anything without asking me;
every number you report comes from your trace or the vault history. Stop and ask if blocked for more than 20 minutes.
```

## What this does not claim

- **Steps 2, 5 and 7 have not run against a server from this repository yet.** Run 1 had no sgit credentials; the commands are checked against `--help` of sgit-ai 0.21.0, not executed.
- **The hosts differ.** Some cannot run a shell or hold secrets; there, a person runs the vault steps.
- **Ruflo's `hive-mind work` was not used in run 1.**

## Where this comes from

This repository's POCs (POC1 for the ABP and Ruflo's policy engine, POC2 for memory per role in a vault, branch per role, merged), the sgit cheatsheet in `docs/01-sgit-cheatsheet.md`, `ruflo hive-mind --help` (3.56.10) and `sgit write --help` (0.21.0), run on 15 October 2026. The plan is in [The studio](the-studio.html).
