# RVM capabilities compiled from the ABP: Ruflo SPARC swarm (ruflo 3.56.10) on a POC repo, run by Claude Code

Owner: Dinis Cruz · valid until 2026-10-31

## queen-strategic: plan the objective, choose topology, assign roles

Capability token rights: `EXECUTE, READ` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## coder: implement the change, on a branch

Capability token rights: `EXECUTE, READ, WRITE` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| write.repository.tenant | approval | require_approval; branch protection |
| send.endpoint.world | no | default-deny egress |
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## tester: run tests, report

Capability token rights: `EXECUTE, READ` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| write.file.project | no | deny rule |
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## reviewer: review diffs against the mandate

Capability token rights: `READ` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## researcher: fetch public sources

Capability token rights: `EXECUTE, WRITE` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## documenter: write docs

Capability token rights: `READ, WRITE` (GRANT never delegated unless a row says so)

| reachable but not mandated | mandate | barrier |
|---|---|---|
| send.message.world | no | policy deny + no mail credential in the sandbox |
| create.record.world | approval | require_approval rule + CI protected environment |
| read.credential.host | no | deny rule; secrets only via the supervisor |

## Gaps

0 rows have reach, no mandate and no barrier.

Note: RVM rights are coarser than ABP primitives (EXECUTE covers both a sandboxed test run and an email send). The ABP keeps the distinction; the token alone cannot. That is the argument for compiling tokens FROM a mandate.
