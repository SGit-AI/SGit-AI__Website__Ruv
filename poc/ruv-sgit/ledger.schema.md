# data/vaults.json: the ruv.sgit vault ledger (one entry per run; every number measured by poc/ruv-sgit/ruvsgit.py)

```
{ "updated": "ISO time", "sample": false,
  "server": "what served the vaults (local SG/Send vault server, version, storage mode)",
  "published_on": { "server": "https://dev.send.sgraph.ai", "viewer": "https://dev.vault.sgraph.ai/en-gb/", "note": "where sealed example vaults live" },
  "vaults": [ {
    "run": "r2-motion", "purpose": "one line", "feedback": "the request this run answered",
    "vault_id": "id on the local server (the key is never recorded)",
    "created_at": "ISO", "closed_at": "ISO", "deleted_at": "ISO or null",
    "hive":  { "queen": "queen-…", "workers": 5, "tasks": 5, "ruflo_calls": 20, "ruflo_ms": 9000 },
    "branches": [ { "name": "w-motion", "role": "developer", "commits": 1, "files": 3, "bytes": 40000,
                    "write_ms": 900, "merge_ms": 700 } ],
    "commits": 9, "files": 14, "bytes_plain": 160000,          // everything in the vault at close, the brief included
    "files_delivered": 12, "bytes_delivered": 150000,        // what the workers delivered (sum of branches)
    "delete_check": { "store_paths_left": 0, "clone_after_delete": "failed" },   // checked before the key is destroyed
    "sealed_at": "ISO or absent",                             // public example runs only (ruvsgit.py seal); client runs are deleted, never sealed
    "published": { "server": "https://dev.send.sgraph.ai", "vault_id": "…", "read_key": "sgit_public_read_<hex>:<vault id>",
                   "viewer_url": "https://dev.vault.sgraph.ai/en-gb/#<read key>", "clone": "sgit clone <read key>",
                   "sealed_at": "ISO", "files": 3, "bytes": 2708 },   // only the reference: the vault's files are on the server, never in the repository
    "seal_check": { "server": "…", "push_ms": 4413,
                    "clone_published": { "ms": 2232, "files": 3, "identical": true, "store_objects": 21, "store_identical": true, "named_branch_refs": 2 },
                    "write_with_read_key": "refused (commit and push)",
                    "vault_ui": { "opened": true, "shows": ["brief", "workers"], "title": "…", "screenshot": "evidence/ruv-sgit/<run>-vault-ui.png" },
                    "local_server_clone_after_delete": "failed", "vault_key_left": false },
    "superseded_by": "run or absent",                         // example-01-hello and r14-examples: sealed as static folders (removed 17 Oct), republished by newer runs
    "server_store": { "files": 120, "bytes": 190000, "plaintext_hits": 0, "probe": "what was searched for" },
    "clone": { "ms": 1500, "files": 14, "identical": true },
    "ops": [ { "op": "init", "ms": 800 }, { "op": "push", "ms": 600 } ],
    "history": [ { "id": "3bf90dd8d00a", "message": "…", "branch": "w-motion" } ],
    "workers": [ { "id": "motion", "role": "developer", "tokens": 90000, "tool_uses": 15, "wall_s": 420 } ]
  } ] }
```
