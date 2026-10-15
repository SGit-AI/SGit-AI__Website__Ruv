# rUv (Reuven Cohen) x sgit and ABPs: debrief, synergy map and POCs for Thursday 15 Oct

By @CRM for Dinis, 14 Oct 2026, from public sources (listed at the end). Star counts are third-party snapshots; nothing here was run.

## The meeting
Agentic Engineering Live: rUv in London. Thu 15 Oct 2026, 18:00-21:00 BST, hybrid, run by the London chapter of the Agentics Foundation (registration lu.ma/agentics). Format: an intro to the Agentics ecosystem, then "more than a conventional talk": members show projects and pair on demos, prototypes and code. That is the slot for Dinis's mini presentation.

## Who he is
Reuven Cohen (rUv): founder and Chief AI Officer, Cognitum One; creator of the Agentics Foundation; earlier founded Enomaly, Chief Cloud Advocate at Citrix, architect of EY.ai; credited with coining "Agentic Engineer". Oakville, Ontario. 62,758 LinkedIn followers; first-degree connection of Dinis (462 mutuals). Positioning: "Sovereign agentic AI, cloud to edge"; "I build AI systems that perceive, think, coordinate, act, and evolve."

## His stack, in one table (most popular first)
| Project | What it is | Size (snapshot) |
|---|---|---|
| RuView | Camera-free WiFi sensing: presence, pose, vital signs (research) | ~92.7k stars (7 Sep) |
| Ruflo (formerly Claude Flow) | Hive-mind orchestration for Claude Code and other models: queens (strategic, tactical, adaptive) and 8 worker types; consensus (Raft, BFT, Gossip, CRDT, Quorum); daemon and scheduled unattended runs; SPARC workflow; HNSW memory, knowledge graph, ReasoningBank (reusable solution patterns), SONA learning loop, AgentDB; signed releases, security plugins (prompt injection, path traversal, PII), anti-drift spec pinning | ~71.4k stars; ~711k npm downloads (May) |
| RuVector | Rust memory substrate for agents: vector + graph/hypergraph + temporal memory, HNSW, GNN rerank, self-learning (SONA MicroLoRA), WASM and edge builds, MCP server with allow/deny tool policy, hash-linked witness logs, copy-on-write branches, snapshots | ~4.5k stars |
| MetaHarness | Factory for agent harnesses: agents, skills, commands, MCP tools, memory namespace and a governance policy (deny by default, audit on), across 10 hosts incl. Claude Code, Codex, GitHub Actions; evaluates on SWE-bench etc.; "Darwin mode" evolves its own config | v0.1.x beta |
| RVM | Bare-metal Rust VMM for agents: capabilities with 7 rights (read, write, grant, revoke, execute, prove, grant-once), no ambient authority, proof-gated mutations, hash-chained signed witness log with deterministic replay | early (Apr 2026) |
| Also | agentic-flow, sparc, ruv-FANN, open-claude-code, and 14 new repos in Aug-Sep alone | |

Fair note (Dinis's point): some of this is superseded by Claude Code itself (subagents, plugins, hooks), and Ruflo now plugs into Claude Code as a plugin or MCP server. The innovation rate is the point.

## The two halves (Dinis's framing)
- rUv: let the agents go to town: swarms, consensus, self-learning, speed, autonomy, many agents.
- Dinis: determinism and memory: what the agent is allowed to do (ABP), and what it did and knew, kept encrypted, versioned and reviewable (sgit), read through a graph.
Autonomy needs both: the more the swarm learns and evolves, the more you need a written mandate and a history you can trust.

## Where his own docs leave the gaps we fill
- RuVector, in its own words: no encryption at rest or in transit ("witnesses do not encrypt memory content"; embeddings are sensitive); no document versioning; replication with "simulated transport", "not a complete production network replication plane"; "collections and metadata filters ... are not a complete authorization boundary"; deletes do not reach snapshots, branches or replicas. => sgit: encrypted client-side, server sees ciphertext, full history, branch/merge, clone anywhere.
- Ruflo: anti-drift pins the spec; deviations become votes. No permissions model, RBAC or audit log described. => ABP: the spec becomes a mandate per queen and worker: reach, mandate, gap, barriers, owner.
- MetaHarness: ships "a governance policy" per harness. => ABP is that policy as a document the CISO and insurer read; MetaHarness can be one of its enforcers.
- RVM: capabilities and witness logs enforce reach. => ABP says why each right was granted; RVM tokens are the compiled form.
- Learning loops (SONA, ReasoningBank, Darwin mode): behaviour changes over time. => versioned ABPs and sgit history show what changed, when, and let you roll back a learned pattern.

## Synergy map
| His piece | Our piece | Together |
|---|---|---|
| Ruflo swarm (queens, 8 workers) | ABP per role | A swarm whose every role has a written mandate; anti-drift votes check against it |
| RuVector memory | sgit vault | Agent memory that is encrypted, versioned and shareable without trusting the host |
| RVF witness logs, RVM witness chain | sgit commits | Witness logs committed per session: tamper-evident and private and replayable |
| MetaHarness governance policy | ABP | Policy as code (his) plus policy as document (ours), generated from each other |
| RVM capabilities (7 rights) | ABP rows | ABP row -> capability tokens; every token traceable to a mandate |
| Ruflo knowledge graph, RuVector hypergraph | Fractal semantic graphs | Business context fed in as a graph, not as prompts |
| Shared Brain (hosted cross-agent memory) | Vaults + lanes | Cross-agent memory where the host holds only ciphertext |

## POCs and MVPs (smallest first)
1. ABP for a Ruflo SPARC swarm: read a ruflo.toml + plugin list, write one ABP per queen and worker (reach, mandate, gap, barriers). Output: a public vault. Days.
2. RuVector memory in an sgit vault: after each session, commit RuVector snapshots and witness logs to a vault; show history, diff, encryption, clone on another machine. Days.
3. ABP -> RVM capabilities: map ABP rows to RVM's seven rights; show a capability that has no mandate (the gap). A table first, code later.
4. MetaHarness <-> ABP: export a harness's governance policy as an ABP, and generate the policy from an ABP.
5. Learning with a history: version ReasoningBank / SONA outputs in sgit so a learned route can be reviewed and reverted.

## Mini presentation (5 minutes, 5 slides)
1. Who: sgit (git for encrypted vaults) and RiskMandate (Agent Behaviour Policies). One line each.
2. Two halves: autonomy (Agentics, Ruflo) and determinism plus memory (ABPs, sgit). Same goal.
3. The synergy table above (the 7 rows).
4. One live thing: a vault (e.g. the Licence to Operate or Risk Mandate demo vault), or POC 1 if built tonight.
5. The ask: pick one POC to build together; a talk or write-up at a future Agentics London meetup.

## Open
- Should anything be built tonight for the demo (POC 1 or 2)? That is @DevTeam's call and needs Dinis's yes.
- Verify current star counts and the venue on the day.

## Sources
https://ruv.io/ · https://github.com/ruvnet · https://github.com/ruvnet/ruvector · https://github.com/ruvnet/rvm · https://github.com/ruvnet/metaharness · https://sublimecoding.com/blog/ruflo-claude-flow-multi-agent-deep-dive · https://createwith.com/event/london-agentic-engineering-live-reuven-cohen-ruv-in-london-oct-2026 · LinkedIn profile screenshot from Dinis (14 Oct)
