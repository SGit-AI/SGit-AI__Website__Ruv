# sgit cheatsheet (sgit-ai 0.21.0, flags checked with --help on 14 Oct 2026)
Install: `pip install sgit-ai==0.21.0` (Python >= 3.11). Docs: https://sgit.ai/docs/quickstart.html · https://sgit.ai/docs/installation.html · agents: https://sgit.ai/llms.txt
What it is: git for encrypted vaults. Files are encrypted client-side (AES-256-GCM) before they leave the machine; the server stores ciphertext only. The vault key (`{passphrase}:{vault_id}`) is the one secret; there is no reset.

| Need | Command |
|---|---|
| New vault (prints the vault key and a read key ONCE) | `sgit create <name> [--token T]` |
| Clone with the key from stdin (keeps it out of argv/history) | `printf '%s' "$VAULT_KEY" \| sgit clone [--token T] - <dir>` |
| Read-only clone | `sgit clone --read-key <hex> <vault_id> <dir>` |
| Status / commit / pull / push | `sgit status` · `sgit commit -m "msg"` · `sgit pull` · `sgit push [--token T]` (commit before pull) |
| Write one file atomically (agent-friendly) | `sgit write <vault/path> --file local.json --message "msg" [--also p:file] --push [--json]` |
| History for agents | `sgit history log --json -n 20` · `--file <path>` · `--grep <re>` · `--since 2026-10-14` · `--patch` |
| Branch per agent, then merge | `sgit branch new <name>` · `sgit branch switch main` · `sgit branch merge <name>` |
| Conflicts | `sgit resolve --all --ours\|--theirs` |
| Publish a static, browsable folder | `sgit publish [--visibility bare\|named\|public] [--bundles] [--api-spec] --yes` (public = READ KEY published, irreversible) |
| Serve it locally (browser) | `sgit vault serve [--port 8420] [--open]` |
| Inspect | `sgit vault info` · `sgit ls` · `sgit cat <path>` · `sgit doctor` |
Notes from use: big shared vaults can report "diverged N ahead, N behind" after another client migrates history; the fix that worked was a fresh clone. Keep POC vaults small and single-purpose.
Vaults for tonight: `ruv-pocs-public` (published, read key public on purpose: ABPs, reports, the browser app) and `ruv-pocs-memory` (private: agent memory, sessions). Create both, store keys as repo secrets `SGIT_VAULT_KEY_PUBLIC`, `SGIT_VAULT_KEY_MEMORY`, plus `SGIT_TOKEN`.
