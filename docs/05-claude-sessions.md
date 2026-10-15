# Claude Code (dedicated repo) and Cowork
Claude Code (recommended for the build):
1. New GitHub repo `ruv-x-sgit-pocs`; unzip this pack; `npm ci`; open Claude Code in the repo; it reads `CLAUDE.md` (its ABP).
2. Ruflo inside Claude Code: MCP `claude mcp add ruflo -- npx -y ruflo@3.56.10 mcp start` (subcommands verified: start/status/tools/exec); or plugin (`/plugin install ruflo-core@ruflo`, from public guides, verify). RuVector MCP: `RUVECTOR_MCP_PROFILE=readonly npx ruvector mcp start` (check `npx ruvector --help`; the CLI lists `hooks` for Claude Code).
3. Ruflo hooks for learning (`ruflo hooks pre-task|post-task|session-end`) can write session state; POC6 copies it into the memory vault.
Cowork: no plugin installs; use it to clone the public vault (`sgit clone --read-key ...`), read the ABP, the reports and the memory history, and draft the write-up. Agents draft; Dinis sends.
