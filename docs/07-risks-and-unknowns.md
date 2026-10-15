# Risks and unknowns (read before you start)
- Third-party versions move fast (Ruflo: 14 new rUv repos in Aug-Sep alone; npm `ruflo` 3.56.10 vs the 3.6.x in May articles). Pin, and trust `--help` over any doc.
- Ruflo memory export/import were unreliable on a fresh project in our run (export count 0; import `policy-anchor-log-missing`); copying the DB files worked. If time is short, POC2 can vault Ruflo's `memory list` output plus the DB files only.
- Ruflo auto-starts a background daemon; stop it (`npx ruflo daemon stop`) in every script and CI job.
- Ruflo policy administration requires an interactive TTY by design. Do not bypass; use the library engine (POC1) or Dinis's own terminal (POC6).
- `ruvector` native CLI needs platform binaries; not tested on the CI runner. POC4 uses WASM, which is verified.
- MetaHarness scaffolding may want network or API keys; it is P5 for that reason.
- Vault keys: never in argv, logs, commits or the browser app. Only `ruv-pocs-public` is published with its read key.
- Claims about rUv's projects in the demo: say "per its README" and link; star counts are snapshots.
