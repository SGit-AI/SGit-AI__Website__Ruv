# r16-narration: writer brief (shared by the ceo, cto and dev workers)

You are one worker in ruv.sgit run r16-narration. Write ONE file: site/talk/narration/<persona>.json. Do not edit any
other file, do not commit, do not run poc/ruv-sgit/ruvsgit.py, do not touch vault keys or tokens.

## What it is for
Dinis Cruz gave the talk "Autonomy with a mandate and a memory" on 15 Oct 2026 (Agentic Engineering Live, Agentics
Foundation London). The deck is a timed player (site/talk/player.html + site/talk/talk-10.json, 26 beats, 698 s). We
want a text narration of that deck, to be shown under the deck as synchronised captions (watch it with no sound,
press play, it runs beginning to end) and later read by a text-to-speech voice for a video. Three versions, one per
persona; you write one.

## Inputs (read them)
- site/talk/narration/beats.json: every beat: id, at, dur (seconds), title, heading, sub, caption, builds, the speaker's line
  ("say"), the speaker's note ("cue"), the live page's steps ({t, label}, seconds local to the beat, already scaled by
  speed) and the page's visible text (page_text).
- site/talk/talk-10.json (the timeline itself; the "table" beat has its rows there), the slide pages under
  site/talk/slides/*/index.html and the pages the beats embed (site/studio/v*/, site/ruv-sgit/...), site/data/
  (report.json, vaults.json), the articles in site/articles/src/ (the-talk-long-read.md, the-talk-live.md,
  how-it-was-made.md are the best context), BRIEF.md, README.md.
- Look at slides in a browser if it helps: the site is served at http://127.0.0.1:8099/ (e.g.
  http://127.0.0.1:8099/talk/player.html?t=30). Playwright: playwright-core in
  /tmp/claude-0/-home-user-SGit-AI--Website--Ruv/145b1e7d-e432-5eb5-a1ab-c9670dcca9f3/scratchpad/pw, executablePath
  /opt/pw-browsers/chromium. Optional.

## Format
{
 "persona": "<ceo|cto|dev>", "label": "<CEO|CTO|Developer>",
 "voice": "<one line: who this is for and how it speaks>",
 "words_per_minute": 150,
 "beats": [
  {"id": "open", "paras": [
    {"at": 0, "text": "<what the narrator says, plain text, 1-3 sentences>",
     "notes": {"screen": "<what is on screen at this moment>",
               "from": "<what in the talk this paragraph is written from: the speaker's line, a cue, a slide label>",
               "sources": ["<file for every number or claim, e.g. site/data/vaults.json>"]}}
  ]}
 ]
}
- Every beat, in the timeline's order, each with 1+ paragraphs. "at" is seconds from the start of the beat; start a
  paragraph where its step starts on screen (use the steps' t), increasing within the beat.
- Timing is a hard rule: a paragraph read aloud at 150 words per minute (2.5 words a second) must end before the next
  paragraph's "at" (or the end of the beat). Short beats (8 s, 15 s) get one short paragraph. Leave a little air.
- Run `python3 site/build/narration_check.py site/talk/narration/<persona>.json` and fix until it says ok.
- The text is spoken: no markdown, no bullet lists, no URLs read out letter by letter (say "ruv dot sgit dot ai"
  only if needed; the screen shows URLs), numbers as the speaker would say them. Write it to be read by a narrator
  to the viewer ("you"); "we" is Dinis and the sgit / ruv.sgit team; call the speaker Dinis when needed.

## Accuracy (hard rules; the site is 100% accurate)
- Every number and factual claim must come from the inputs above; put its file in "sources". No invented numbers,
  customers, prices, results or quotes. If unsure, leave it out.
- Describe what is actually on screen at that moment (that is what makes the no-sound version work).
- rUv's projects (Ruflo, RuVector, RVM, MetaHarness, ...) are MIT, by rUv / ruvnet. Never diminish rUv's tools: the
  positioning is additive (Ruflo already has swarms, consensus, its own policy engine and memory; sgit adds a memory
  with history and a written mandate). Do not frame Ruflo or the hive as a weak link or a problem to fix.
- Do not name Cognitum. Avoid the phrase "autonomy you can trust". Mondweep Chakravorty may be named.
- Keep it interesting: a narrative with a thread, not a list. Each persona hears the same deck, told for them.
