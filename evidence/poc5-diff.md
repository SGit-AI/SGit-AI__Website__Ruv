# POC5: MetaHarness scaffold vs our ABP (role `coder`)

Scaffold: `npx metaharness rm-agentics --template vertical:agentics --host claude-code --no-darwin` (metaharness 0.4.17, manifest generator 0.1.0, 18 files).

## What the harness actually says about permissions

| source | setting |
|---|---|
| settings.json allow | `Bash(npx rm-agentics*)` |
| settings.json allow | `mcp__rm-agentics__*` |
| settings.json allow | `mcp__swarm_bus__*` |
| settings.json deny | `Read(./.env)` |
| settings.json deny | `Read(./.env.*)` |
| settings.json mcpServers | `rm-agentics` |
| settings.json mcpServers | `swarm_bus` |
| CLAUDE.md | "Defer destructive operations to the user" (prose) |

Not found in the generated files: a governance policy document, deny-by-default statement, network/shell/file-write switches, timeouts, call limits or an audit flag (the README of the metaharness package describes those; this scaffold, with this template and host, did not emit them). Noted in evidence/notes.md.

## Rendered as an ABP

4 rows -> `harness.abp.json`

| capability | reach | mandate | barrier | from |
|---|---|---|---|---|
| execute.process.self | true | yes |  | allow-listed command (.claude/settings.json permissions.allow); allow-listed MCP tool (.claude/settings.json permissions.allow) |
| read.credential.host | true | no | Claude Code permissions.deny (host-enforced) | secrets file denied (.claude/settings.json permissions.deny) |
| execute.process.host | true | yes |  | MCP server launched by the host (.claude/settings.json mcpServers) |
| delete.file.host | true | approval | CLAUDE.md rule only (prose, not enforced) | "Defer destructive operations to the user" (CLAUDE.md) |

## Diff both ways

### In the harness, not in our ABP (2)

- `execute.process.host`: MCP server launched by the host (.claude/settings.json mcpServers)
- `delete.file.host`: "Defer destructive operations to the user" (CLAUDE.md)

### In our ABP, harness silent (8): reach the agent has with no setting either way

- `read.file.project` mandate **yes**
- `write.file.project` mandate **yes**
- `write.repository.project` mandate **yes**
- `write.repository.tenant` mandate **approval** (our barrier: require_approval; branch protection)
- `send.endpoint.allowed` mandate **yes**
- `send.endpoint.world` mandate **no** (our barrier: default-deny egress)
- `send.message.world` mandate **no** (our barrier: policy deny + no mail credential in the sandbox)
- `create.record.world` mandate **approval** (our barrier: require_approval rule + CI protected environment)

### In both (2)

- `execute.process.self`: ours mandate **yes**; harness yes
- `read.credential.host`: ours mandate **no**; harness no

## Reading

The scaffold ships a host permission list (what the tool runner lets through) and prose rules. An ABP adds the three things a permission list cannot say: whether the reach is mandated, who owns it, and until when. The harness file is a good barrier; the ABP is the mandate it should be generated from.