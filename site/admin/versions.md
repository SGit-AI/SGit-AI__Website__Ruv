# Release history, ruv.sgit.ai

*Source: <https://ruv.sgit.ai/admin/versions.html> · site v0.1.5 · generated from the same file as the page (versions.json), so the two cannot drift.*

The site version, shown in the nav of every page, increments on every release; each release is one push to dev. The git log is the authoritative audit trail; this file is the human-readable index of it. Newest first. The newest release links to the branch until its commit exists.

| Version | Date | Commit | Changes |
|---|---|---|---|
| v0.1.5 | 2026-10-15 | this release | **Navigation, version and name.** The navigation is consolidated into four groups (Tonight, The idea, Proofs, Articles) with dropdowns, and a Menu button on phones; the site version is shown in the nav of every page and links here; this release history is new, with a .md twin; the collaboration is written rUv + sgit instead of rUv x sgit. The studio article and the setup brief are corrected on append lanes: sgit.ai documents a write-only append mode, which the bus protocol now maps onto. |
| v0.1.4 | 2026-10-15 | e2070cf | **The talk works on an iPad.** Touch controls, swipe between beats, notes under the slide in portrait, a swipeable reader of the script, and the evening from the organisers' welcome deck (agenda, the 7:00 pm slot, who is in the room). Removed a regex lookbehind that older iPad Safari rejects. |
| v0.1.3 | 2026-10-15 | b4276b3 | **The studio and the articles.** POC7: a Ruflo hive-mind (queen and eight roles) whose run made seven animations, from a diagram to a 3D city of vaults, with MP4s, the timed trace and the builders' token use. A new articles section in the newsroom's shape: the studio's plan and architecture, and a setup brief any agent can follow. |
| v0.1.2 | 2026-10-15 | 0924c5e | **Tonight's talk as a timeline, and the review fixes.** A scripted ten-minute talk (and a five-minute cut) that plays on a clock, with a presenter view, a synced audience window, rehearsals and offline files. Fixes from an external review: the count of stopped actions (6 of 11: 4 denied, 2 approval), no sideways scrolling on phones, one h1 per page, WebP images. |
| v0.1.1 | 2026-10-15 | 37e9ee5 | **Build scripts in CI.** site/build un-ignored: the Python .gitignore template's build/ rule hid the sync and validate scripts from CI. |
| v0.1.0 | 2026-10-15 | 1b33ef1 | **First release.** Six proofs of concept of sgit vaults and Agent Behaviour Policies inside rUv's stack, and the website that explains them: home, rUv's stack, use cases, architecture, the POCs, replicate, the demo script and the live app. |
