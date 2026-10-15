# Demo (5 minutes)
The scripted, timed version (10 and 5 minutes) is `site/talk/` (https://ruv.sgit.ai/talk/index.html); its timeline files are the source of truth for the words.

1. (30 s) "rUv's stack lets agents go to town. Autonomy needs two more things: a written mandate per agent, and memory with history the host can't read."
2. (60 s) Terminal: `npx ruflo policy evaluate '{"identity":{"id":"coder-1","type":"agent"},"action":{"type":"email.send"}}'` -> `allowed`, `legacy-default-allow`. "That's the default today."
3. (90 s) Browser (the vault page): the ABP for a SPARC swarm; type "can the coder send email?" (answer: no, barrier, owner); scroll to the table: same 11 actions, Ruflo default vs with the ABP: 6 stopped (4 denied: email, pastebin, the tester's edit, the researcher's credential read; 2 need approval: push, deploy), 5 allowed; receipt ledger valid. "Your engine enforces it; the ABP is the mandate it enforces."
4. (60 s) Memory (POC2 roundtrip, run locally; the CI jobs are wired and need the secrets): coder and tester wrote memory on their own branches, a fresh clone restored it from the vault; `sgit history log`: who learned what, when. "RuVector's docs list no encryption at rest, no versioning: this is that layer, encrypted client-side."
5. (60 s) RVM table: rights compiled from the mandate, plus the withheld list. Ask: "Pick one: Ruflo policy profiles generated from ABPs, or vault-backed memory for RuVector. Build it together, show it back here."
