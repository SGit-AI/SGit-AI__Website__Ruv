# Demo (5 minutes)
1. (30 s) "rUv's stack lets agents go to town. Autonomy needs two more things: a written mandate per agent, and memory with history the host can't read."
2. (60 s) Terminal: `npx ruflo policy evaluate '{"identity":{"id":"coder-1","type":"agent"},"action":{"type":"email.send"}}'` -> `allowed`, `legacy-default-allow`. "That's the default today."
3. (90 s) Browser (the vault page): the ABP for a SPARC swarm; type "can the coder send email?" (answer: no, barrier, owner); scroll to the table: same 11 actions, Ruflo default vs with the ABP; receipt ledger valid. "Your engine enforces it; the ABP is the mandate it enforces."
4. (60 s) Memory: CI run, two runners: coder and tester wrote memory, a fresh runner restored it from the vault; `sgit history log`: who learned what, when. "RuVector's docs list no encryption at rest, no versioning: this is that layer, encrypted client-side."
5. (60 s) RVM table: rights compiled from the mandate, plus the withheld list. Ask: "Pick one: Ruflo policy profiles generated from ABPs, or vault-backed memory for RuVector. Build it together, show it back here."
