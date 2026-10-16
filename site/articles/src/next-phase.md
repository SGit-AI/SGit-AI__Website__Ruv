---
{"no": 9, "title": "From the talk to the service: the next phase of ruv.sgit.ai (a debrief, and the brief for building it)", "author": "Dinis Cruz", "date": "2026-10-16", "version": "0.2.0 (DRAFT, decisions of 16 Oct applied)", "tags": ["draft", "debrief", "brief", "ruv.sgit", "marketplace", "rules of engagement", "information architecture", "providers", "agentics"], "abstract": "DRAFT for Dinis to check and fine-tune before anything is built. On 15 October ruv.sgit.ai was the site of a talk: the talk and its player, six proofs of concept, eleven ruv.sgit runs and their ledger, the studio, four offers with a shop, and five articles written the same night. This is the debrief of where it stands, with screenshots of the home page and the main areas taken on 16 October as the historical record, and the brief for what comes next: turning it into the site that offers the ruv.sgit service, delivered through a marketplace of providers, starting with two founding providers, Dinis Cruz and Mondweep from the Agentics Foundation. It sets out the three audiences (people who want to buy the service, consultants and service companies who want to deliver it, and people who want to learn), the rules of engagement (open source and Creative Commons, client code and data stay the client's, changes committed back, revenue split equally between the parties, whoever has the client bills), how an engagement works end to end, the provider application and waiting list (a static form that writes an email, like the shop), every current page mapped to its new place, the new menu, the URL changes and how old links keep working, the breaking changes, five ruv.sgit runs to build it with acceptance checks, and the open questions, each with a proposed answer. Nothing here is built yet, nobody pays through the site, and there are no providers beyond the two founding ones."}
---
*Written by Claude (Claude Code) from Dinis Cruz's brief of 16 October 2026 (a dictated voice note), this site's files and run records, and the newsroom article [Agentics, ready to sell](https://newsroom.sgit.ai/articles/agentics-ready-to-sell.html). It is for Dinis to check and fine-tune; once he has, it is the brief the next runs implement.*

> **DRAFT v0.2.0.** Dinis answered the first open questions on 16 October (see *Decisions, 16 October* below); the rest keep their proposed defaults until he says otherwise. Every rule, URL, page and price below is a proposal until Dinis signs it off. Edit the source (`site/articles/src/next-phase.md`), change anything, and the implementation follows the edited version. The version goes to 1.0.0 when it is approved, and each later change is listed at the end, so the article also records what changed and why, breaking changes included.

## In short

- **Where we are.** ruv.sgit.ai is a site about a talk and the proof behind it: the talk and its player, six proofs of concept, eleven ruv.sgit runs in a public ledger (38 workers, 67 vault commits, no plaintext found in anything the server stored, every fresh clone identical, every vault deleted), the studio, four offers and a shop, and eight articles. Its menu still opens with "Tonight".
- **Where we go.** The same site becomes the site that offers the service. In Dinis's words: "change the website from being a website about the presentation to be a website about providing the services". The proof stays; it moves from the front of the site to the back, where buyers check it.
- **Three audiences.** People who want to buy the service; consultants and service companies who want to deliver it as part of the marketplace; and people who want to learn, who may later become one of the other two. Each gets its own door on the home page and its own call to action.
- **Two founding providers.** Dinis Cruz and Mondweep, from the Agentics Foundation. Others apply to join through a waiting list.
- **Rules of engagement, stated plainly.** Everything is open source and Creative Commons, so anybody can do this without us, and we encourage it. Code created in engagements through us is open, except the client's own code and data, which stay the client's. Changes are committed back. Revenue is split equally between the parties. Whoever has the client bills. Custom arrangements are possible.
- **No backend, no payment.** Clients order through the shop as today; providers apply through a static form that writes an email to agent@riskmandate.ai, with a "copy as JSON" button. The same route serves a light "keep me posted" sign-up.
- **Old links keep working.** The talk, the articles, the ledger and the shop keep their URLs. The business pages become short redirect pages, because the talk told people to "start at ruv.sgit.ai/business".
- **Five runs to build it** (r13 to r17), each with named workers and acceptance checks, after Dinis has edited this brief.
- **Fourteen open questions** at the end, each with a proposed answer, so a "yes" is enough to move.

## Why this is an article, and a brief

Dinis asked for the debrief to come first: "first you write this sort of article debrief … that is also a brief for the implementation, and that allows me to double check it, but also allows me to fine tune some of the items, and then you can implement it". Writing it as an article has a second purpose he named: "It's also a nice way to capture the history and to capture the things that change, even breaking changes". So this page does three jobs:

1. **A debrief**: what the site is on 16 October 2026, with screenshots, before anything moves.
2. **A brief**: what to build, in what order, with what checks.
3. **A record**: once implemented, the changes list at the end says what was done differently from this draft, and why.

## Decisions, 16 October

Dinis's answers to the first open questions, applied throughout this draft:

1. **Mondweep is live.** He has agreed, and his consent is recorded: his card goes up with his name, Mondweep Chakravorty, co-founder of the Agentics Foundation's London chapter, and a link to his LinkedIn page, [linkedin.com/in/mondweepchakravorty](https://www.linkedin.com/in/mondweepchakravorty).
2. **The split is equal, after costs.** The newsroom article's "small platform share" (5% to 20%) was not a use case: it was a benchmark of what other marketplaces charge (Malt 5%, Upwork 0% to 15%, Braintrust 15%) for a proposal where the consultant keeps most of the price. Because these are consulting engagements, Dinis chose an equal split between the parties instead (50/50 with two, a third each with three), **calculated after direct costs** (model tokens, compute and other third-party costs, reimbursed first to whoever paid them). There is no separate platform share.
3. **Materials are CC BY 4.0.** Code stays Apache-2.0; rUv's projects stay MIT.
4. **Applications go by email to agent@riskmandate.ai**, whose agent keeps them in its own private repository. **Never in this git repository.**
5. **Client work is private first.** Everything to do with a client is private by default; anything published (a ledger entry, a case study) comes later and only with the client's agreement.



### What the site is today

On 16 October 2026, at release v0.1.29, ruv.sgit.ai is a site about a talk and the evidence behind it. It was built from an empty repository between 14 and 15 October by Claude Code sessions for Dinis, and most of its later materials were made by ruv.sgit runs: a Ruflo hive (Ruflo is MIT, by rUv / ruvnet) whose workers deliver into one ephemeral sgit vault per run, measured and deleted at the end, with the measurements kept in a public ledger.

The main areas, as the menu groups them today:

| Menu group | What is in it |
|---|---|
| **Tonight** | The talk page (still titled "Tonight's talk"), the player at ten minutes, running it offline on a laptop, the five-minute demo script |
| **The idea** | The home page, rUv's stack explained by use case, six use cases, the architecture |
| **Proofs** | ruv.sgit (runs and vaults), the six POCs, the live browser app, the studio, replicate |
| **Work with us** | The business overview, pages for consultants, companies and internal teams, the shop, the business model article, the contact address |
| **Articles** | All articles, and seven of the eight by name |

Behind the menu sit the pages it does not list: the vault ledger, the ruv.sgit animations (the equation, the layers, one action's journey, ruv.sgit in motion, one ephemeral vault), the thirteen live slides of the talk, the seven studio animations, the two offline talk builds, the release history and the encrypted vault page. The full inventory, with every URL, title, first heading and menu group, is [site-map-2026-10-16.json](../data/site-map-2026-10-16.json), written by [site_map.py](../build/site_map.py): 56 pages (16 pages, 4 talk pages, 13 slides, 11 animations, 8 articles, 3 data pages, 1 admin page).

### The historical record

These screenshots were taken on 16 October 2026 at v0.1.29 by the archivist worker of run r12-next-phase, before any of the changes in this brief. They are the "before" picture. The same views will be captured again when the implementation is finished.

<figure><img src="../assets/img/articles/next-phase/home.webp" alt="The ruv.sgit.ai home page at v0.1.29 on 16 October 2026, headed 'Run your Ruflo hive with a written mandate per role and a vault for what it remembers.', addressed to Ruflo, AgentDB, RuVector and MetaHarness users and to the talk at Agentic Engineering Live"><figcaption>The home page on 16 October 2026 (v0.1.29). It speaks to people who already use rUv's tools and to the evening of the talk. It does not yet say that you can buy the service, or who delivers it.</figcaption></figure>

<figure><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;align-items:start"><img src="../assets/img/articles/next-phase/home-full.webp" alt="The whole home page at v0.1.29, top to bottom: the headline, the story in one table, where sgit.ai plugs in, use cases, what was proven and when, and how it all fits"><img src="../assets/img/articles/next-phase/home-menu.webp" alt="The home page with the Work with us group open (Overview, For consultants, For companies, For internal teams, The shop, The business model, Contact), beside the other groups Tonight, The idea, Proofs and Articles"><img src="../assets/img/articles/next-phase/phone-home.webp" alt="The home page at v0.1.29 on a phone-sized screen, with the Menu button"></div><figcaption>The whole home page, the menu as it is today (five groups, opening with "Tonight"), and the home page on a phone.</figcaption></figure>

<figure><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;align-items:start"><img src="../assets/img/articles/next-phase/talk.webp" alt="The talk page, titled 'Tonight's talk, as a timeline'"><img src="../assets/img/articles/next-phase/player.webp" alt="The talk player on slide 2 of 26, the claim: Autonomy goes further with a memory and a mandate, with the bar of controls and steps below"><img src="../assets/img/articles/next-phase/ruv-sgit.webp" alt="The ruv.sgit page: a Ruflo hive plus sgit vaults plus Agent Behaviour Policies, one run in six steps, every run"><img src="../assets/img/articles/next-phase/ledger.webp" alt="The vault ledger: the statistics of every ruv.sgit run's vault"><img src="../assets/img/articles/next-phase/pocs.webp" alt="The six proofs of concept page"><img src="../assets/img/articles/next-phase/studio.webp" alt="The studio page: seven animations made by a Ruflo hive"><img src="../assets/img/articles/next-phase/ruv-stack.webp" alt="rUv's stack, explained by use case"><img src="../assets/img/articles/next-phase/articles.webp" alt="The articles index"></div><figcaption>The talk and the proof, as they are today: the talk page, the player, ruv.sgit, the ledger, the POCs, the studio, rUv's stack and the articles. All of these keep their URLs.</figcaption></figure>

<figure><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;align-items:start"><img src="../assets/img/articles/next-phase/business.webp" alt="The business overview page, 'ruv.sgit for business': governed agent swarms, as something you can buy, resell or run yourself"><img src="../assets/img/articles/next-phase/consultants.webp" alt="The page for consultants: copy it yourself, white label, or a custom offering"><img src="../assets/img/articles/next-phase/shop.webp" alt="The shop: build an order from task runs, dedicated compute, a maintained repository and expert time, then send it by email"></div><figcaption>The offer, as it is today: the business overview, the page for consultants and the shop. The business pages are the ones that move; the shop stays where it is.</figcaption></figure>

### What the talk achieved

On 15 October Dinis gave the 7 pm talk at Agentic Engineering Live in London, an Agentics Foundation London evening that opened with rUv's keynote. "Autonomy with a mandate and a memory" was 26 slides and 11 minutes 38 seconds on a timeline, most of them live pages that read their numbers from the site's data files, and it ran itself while he spoke over it. The [long read](the-talk-long-read.html) walks every slide; [the talk, live](the-talk-live.html) puts thirteen of its animations on one page; [how it was made](how-it-was-made.html) tells the history from the record; [the talk player](the-talk-player.html) and [walking backwards](walking-backwards.html) cover the player and how its features arrived.

What it achieved, in terms this brief needs:

- **A demonstration that is also the sales material.** The site was built by the runs it sells, and the [ledger](../ruv-sgit/ledger/index.html) shows each one: eleven runs (one a smoke test), 38 workers, 67 vault commits, no plaintext found in anything the server stored, every fresh clone identical to the delivered files, every vault deleted, and for the ten runs after the smoke test the delete checked (no store paths left, and a clone after the delete fails) (`data/vaults.json`, last written at 23:40 UTC on 15 October).
- **An offer with prices.** Four offers that mix and match, priced in the [business plan](ruv-sgit-business-model.html) and orderable in the [shop](../shop/index.html), which builds an email and takes no payment.
- **An ask.** The talk closed with "build a company on this, or add it to your services", and sent people to ruv.sgit.ai/business. That spoken URL is one of the reasons the business pages must keep answering.
- **The honest limits, already published.** The runs were not gated by a compiled behaviour policy; enforcement was shown separately in POC1, where Ruflo's policy engine in enforce mode stopped six of eleven actions (four denied, two sent to a person). Nothing is automated end to end; a person starts, watches and hands over every run.

### What changed overnight

Two releases after the talk set up this phase:

- **v0.1.28, five articles** (run r10-articles): the long read, the talk live, how it was made, the talk player and walking backwards, written while the evening was fresh.
- **v0.1.29, additive, not deficit** (run r11-position): at Dinis's request, every line that implied rUv's stack cannot be trusted without sgit and ABPs was reworded as what we add. The claim slide now reads "Autonomy goes further with a memory and a mandate." It credits Ruflo's own policy engine and memory, then names what we add: a memory with history, encrypted before it leaves the agent, and a mandate, written down and compiled into Ruflo's own policy engine. The ledger, the evidence and the run specs were left unchanged. This positioning carries straight into the service: we add to rUv's stack; we do not fix it.

And on 16 October, newsroom.sgit.ai published [Agentics, ready to sell](https://newsroom.sgit.ai/articles/agentics-ready-to-sell.html), which Dinis described as "the beginning of mapping that workflow". Its argument, in brief:

- **The market is crowded at the top and thin on evidence.** Large consultancies with agent platforms, model vendors with partner networks and forward-deployed engineers, agent platforms that sell implementation, and boutiques with small fixed-price engagements (a £2,500 one-week audit in London, a €2,900 sprint in Germany). It cites Gartner's June 2025 prediction that more than 40% of agentic AI projects will be cancelled by the end of 2027.
- **The position is evidence first.** Every engagement leaves a vault the client keeps, with the work, the history and the ledger, and a behaviour policy that says what each agent was allowed to do.
- **The engagement path starts small.** A free conversation, a first run for £10 to £50, expert time at £500 for two hours or £1,500 for a day, a four-day pilot in the client's environment for £5,000, then a maintained repository from £149 a month.
- **It needs people.** A curated marketplace of consultants, five project types to start, and a six-step way to join: apply, show proof of work, peer review, an interview, a shadowed first pilot, and standards you sign.

This brief follows that article and changes one thing: it replaces the article's proposed "small platform share" with Dinis's rule of an equal split between the parties (see the rules of engagement, and open question 6).

## Where we go

### The new purpose

ruv.sgit.ai becomes **the site that offers the ruv.sgit service**: agent work done by a Ruflo hive under a written mandate per role, with an sgit vault per job as the record the client keeps, **delivered by people**, through a small marketplace of providers. Dinis's words: "we now want to sell those services the way we are describing".

Three things change and one does not:

- **The front of the site** speaks to buyers, providers and learners, in that order, instead of to the evening of the talk.
- **The menu** is organised by what a visitor wants to do, not by what we built.
- **Who "we" are** widens from one person and his agents to a group of providers who follow the same rules.
- **The proof does not change.** The ledger, the POCs, the talk and the articles stay exactly where they are. They become the evidence a buyer checks and a provider learns from.

### Positioning

- **Additive to rUv's stack.** Ruflo, RuVector, AgentDB, MetaHarness and RVM are rUv's projects, MIT, by rUv / ruvnet. Ruflo already has a queen-led hive-mind, its own memory and a policy engine with legacy, observe and enforce modes that writes a receipt for each decision. We build on it, we do not sell or own it, and we add two things: a memory with history, encrypted before it leaves the agent (sgit vaults), and a mandate per role, written down and compiled into Ruflo's own policy engine (Agent Behaviour Policies). The service is people who can run that for you.
- **Open source.** Everything we do is published so that anybody can do it without us. The service is for people who would rather have it done, or done with them, by someone who has done it before.
- **Evidence first.** Every job ends in a vault the client keeps and a ledger entry that says what ran. That is the difference the newsroom article identifies, and it is checkable.
- **Small steps.** Each step on the engagement path is small enough to say yes to and ends with something the client keeps.

## The three audiences

Dinis named them: "the people that want to buy this service; the consultants and the service companies that want to be part of our marketplace; and the people that want to learn more about ruv.sgit, which then could become one of the other two."

| | Buyers | Providers | Learners |
|---|---|---|---|
| **Who** | Teams and companies that want agents doing real work, with a record of what they did | Independent consultants, freelancers and service companies who want to deliver agentic engagements on this stack | People who saw the talk, use rUv's tools, or want to understand ruv.sgit |
| **What they want** | A first result without a large commitment; to know who will do the work; to keep their code and data | Clients, a method they can trust, and fair, simple terms | To understand it, try it, and follow what happens |
| **What the site gives them** | The engagement path, the four offers with prices, the providers, the proof | The rules of engagement, how it works, the playbooks, the application | The articles, the talk, the studio, replicate, the setup brief |
| **Call to action** | Order in the shop, or write for a free conversation | Apply to join (the waiting list) | Read, try it locally, keep me posted |

### Buyers: people who want the service

**What they want.** Someone to make agents do a real piece of their work, with a record they can show their own security, risk or legal people, at a price they can say yes to without a procurement round.

**What the site gives them.** One page, *For clients*, that starts with the engagement path (a conversation, a first run, expert time, a pilot, a maintained setup), then the four offers, then the providers who deliver them, then the proof (the ledger and POC1), then what stays theirs: their code, their data, their vault. Today's pages for companies and internal teams become two sections of it, because the differences between them (reselling, white label, an internal service) are about how they use the result, not about what they buy.

**Call to action.** Two buttons: *Order in the shop* (as today: an emailed order to agent@riskmandate.ai, no payment, a person replies) and *Ask for a free conversation* (an email with a short template). The shop gains one optional field, *preferred provider* (no preference, or one of the listed providers).

### Providers: consultants and service companies

**What they want.** Work they can deliver well, a method and tooling they do not have to build, clear terms about money and ownership, and a fair way in.

**What the site gives them.** *For providers*: why join, the rules of engagement in full, how an engagement runs and who does what, the founding providers, the steps to join, and the playbooks (the setup brief, replicate, the business plan, the runner). Today's page for consultants, with its three ways (do it yourself, white label, custom), maps onto the rules directly: doing it yourself is rule 2, white label is "whoever has the client bills", and custom is rule 8.

**Call to action.** *Apply to join*: the provider application, which today puts you on the waiting list.

### Learners: people who want to understand it

**What they want.** To know what ruv.sgit is, see it work, and try it without asking anyone.

**What the site gives them.** *Learn*: what ruv.sgit is (today's home page content, kept), rUv's stack by use case, the use cases, the architecture, the studio, replicate, running it offline, the setup brief, and the articles. And *Proof*: the runs, the ledger, the POCs, the talk.

**Call to action.** *Try it locally* (replicate, or the offline run), and *Keep me posted*, a light sign-up by email. Every learner page ends with the two doors to the other audiences: "want it done for you?" and "want to deliver it?".

## The founding providers

The marketplace starts with two people. The newsroom article introduced them: "Mondweep Chakravorty, co-founder of the Agentics Foundation's London chapter, which runs the meetups where all of this was shown, and me." It also says they are "not taking bookings yet: we need to align our diaries first, so for now the page will say *register interest*, not *book*." This brief keeps that: the cards say *register interest* until open question 4 is answered.

The cards below are the shape of the profile, not the profile. Nothing is filled in that is not already published; the rest is for Dinis and Mondweep to supply (open question 1).

| Field | Dinis Cruz | Mondweep |
|---|---|---|
| **Name as shown** | Dinis Cruz | Mondweep Chakravorty (agreed, 16 October) |
| **Affiliation** | to be supplied | the Agentics Foundation; the newsroom article describes him as "co-founder of the Agentics Foundation's London chapter" |
| **Role here** | founding provider; built this site with Claude Code and gave the talk | founding provider |
| **Project types offered** | to be supplied | to be supplied |
| **Offers** (runs, compute, repository, expert time) | to be supplied | to be supplied |
| **Location, languages** | to be supplied | to be supplied |
| **Availability** | register interest | register interest |
| **Proof of work** | the ledger and the runs on this site | to be supplied (a public vault or repository of a real run) |
| **Photo, bio, links** | to be supplied | [LinkedIn](https://www.linkedin.com/in/mondweepchakravorty); photo and bio to be supplied |

No photo, title or biography is invented for either of them. Mondweep has agreed to be listed (16 October).

## Rules of engagement

This section is written as the page it will become (`rules/index.html`). Dinis's rules, in his order, with the details a provider and a client need. Where a detail is a proposal rather than his words, it is marked and listed as an open question.

### The rules

1. **Everything here is open.** Everything we do is open source and Creative Commons. We publish all the materials, all the playbooks and how to do it. Our code is Apache-2.0. Our materials and playbooks are Creative Commons Attribution 4.0 (CC BY 4.0), which lets anyone reuse them, including commercially, as long as they credit the source. rUv's projects, which this builds on, are MIT, by rUv / ruvnet.
2. **You can do this without us, and we encourage it.** Anybody can take the code, the playbooks and the method and deliver this to their own clients, under their own name, with no permission, no fee and no obligation to tell us. Anybody who implements this implements sgit vaults and Agent Behaviour Policies, and that is the outcome we want either way.
3. **Code created in engagements through us is open.** When an engagement comes through this marketplace, the code it creates is published under Apache-2.0, so the next client and the next provider start from it.
4. **The client's code and data are the client's.** The exception to rule 3: the client's own code and data stay proprietary to the client. We do not publish them, reuse them or keep them beyond the engagement. Each job runs in its own encrypted vault, which is handed to the client at the end and deleted from our side.
5. **Changes are committed back.** Improvements we make to the shared code, playbooks and behaviour policies during an engagement go back to the public repositories. Improvements to rUv's projects are offered to them under their own licence and contribution rules.
6. **Revenue is split equally between the parties, after costs.** Direct costs (model tokens, compute, other third-party costs) are first reimbursed to whoever paid them, itemised; what is left is split equally. Two parties: half each. Three parties: a third each. There is no separate platform share. A party is a provider (a person or a company) that brings the client or delivers part of the work; one provider doing both is one party (proposed; open question 6).
7. **Whoever has the client bills.** If you bring the client, you invoice them and pay the other parties their share. If we bring the client, we invoice and pay you yours.
8. **Custom arrangements are possible.** Especially for companies that bring the work, and for bringing this into an existing project. They are agreed in writing, before the work starts.
9. **Every job leaves evidence.** Each job is a ruv.sgit run: a vault per run, a mandate per role, and a ledger entry. The client keeps the vault. Everything to do with a client is private first: the ledger entry is private unless the client agrees to publish it, and then only the measurements.
10. **Credit where it is due.** rUv's projects are named and credited as his (MIT, by rUv / ruvnet). We build on them; we do not sell or own them. This is additive to his stack.

### Worked examples

The examples use the published prices in [data/offers.json](../data/offers.json) (GBP, excluding VAT). Direct costs paid to third parties (model tokens, compute) come off the top before the split, itemised, and go back to whoever paid them (proposed; open question 7).

| Case | Who brings the client | Who delivers | Who bills | The split |
|---|---|---|---|---|
| **We bring the client, two parties** | We do (Dinis) | Mondweep, with Dinis | We do: £1,500 for a day of expert time | £750 each |
| **A provider brings the client** | A provider | The provider, with us on the behaviour policy | The provider: £5,000 for a four-day pilot | £2,500 each; the provider pays us our half |
| **Three parties** | A provider | That provider, a second provider, and us | The provider who brought the client: £5,000 for the pilot | A third each: £1,666.67, £1,666.67 and £1,666.66 (the odd penny stays with whoever bills) |
| **A company brings an existing project** | The company | The company's team, with a provider | Agreed in writing before the work starts | Custom (rule 8) |
| **Somebody does it without us** | Them | Them | Them | Nothing to split, nothing to ask (rule 2) |

### Licences, in one place

| What | Licence | Whose |
|---|---|---|
| Our code (this site, the runner, the ABP tools) | Apache-2.0 | ours, open |
| Materials and playbooks (articles, briefs, how-tos) | Creative Commons, proposed CC BY 4.0 | ours, open |
| Code created in engagements through us | Apache-2.0 | open, unless agreed otherwise in writing (rule 8) |
| The client's code and data | the client's own terms | the client's, proprietary |
| rUv's projects (Ruflo, RuVector, AgentDB, MetaHarness, RVM) | MIT | rUv / ruvnet |

## How it works

This section becomes `how-it-works/index.html`. It follows the engagement path in the newsroom article and the four offers already on the site.

### The engagement path

| Step | What happens | Price today | What the client keeps |
|---|---|---|---|
| **1. A conversation** | What the client wants agents to do, and what they must never do | free | notes, and a proposed first run |
| **2. A first run** | A task run on a real problem: a Ruflo queen and up to 5, 10 or 20 workers, no network access, materials provided up front | £10, £20 or £50 a run (£9, £17 or £40 with your own model key) | the run's vault |
| **3. Expert time** | Two hours to steer it, or a day to write the behaviour policy for one team | £500 (about two hours) or £1,500 (a day) | the policy and the vault |
| **4. A pilot** | Four days setting it up in the client's own environment | £5,000 | the setup, its policies and vaults |
| **5. Run it yourself** | The maintained repository: the code that runs this, kept current | from £149 a month (£149, £499, £1,500) | the repository |

Dedicated compute (£21, £23 or £36 per eight-hour block) can be added to any step; it is designed, not built yet, and the reply to an order says so. The newsroom article's five project types (a first run with a guide; a behaviour policy for one team's agents; a four-day pilot; a talk or workshop built the way ours was; a review of an agent that is already running) are packages of these offers, and they become the catalogue on *For clients*.

### Who does what

| Who | Does |
|---|---|
| **The client** | Says what they want done and what must never happen; provides the materials; owns their code, data and the vault |
| **The provider who has the client** | Scopes the job, writes the brief with the client, bills, and is the client's single contact |
| **The provider(s) who deliver** | Write the behaviour policy per role, start the run, watch it, review the output and hand it over |
| **The agents** | A Ruflo queen and workers, each under its role's mandate, delivering into the run's vault |
| **The marketplace (for now, the two founders)** | Matches enquiries to providers, keeps the rules and the playbooks, reviews applications |

### How a provider is matched

For now, by hand. An order or an enquiry arrives at agent@riskmandate.ai (a live agent answers; a person follows up). If it names a preferred provider, it goes to them. If not, the founders match it by project type, language, location and availability, and reply with one or two names. The client chooses. Nothing is automated, and the site says so.

### How the work is delivered

Every job is a ruv.sgit run, the same way every material on this site was made:

1. **A run spec**: the client's objective, the materials, and one task per worker.
2. **A mandate per role**: an Agent Behaviour Policy for each worker: what it can reach, what it may do, and what is stopped. No network by default.
3. **A vault per run**: created when the run opens, a branch per worker, every delivery committed and merged. The server stores ciphertext only.
4. **A person watches**: a provider starts the run, watches it to the end and reviews what it made.
5. **The close**: the vault is measured (commits, files, bytes, a plaintext probe of the server's store, a fresh clone compared file by file), handed to the client as a zip or with a read key they choose to publish, and deleted from our side, with the delete checked.
6. **A ledger entry**: what ran, how long, and what the checks found. Private by default for client work; public with the client's agreement.

### How changes are committed back

During a job, two kinds of change happen. The client's own code and data go into the client's vault and stay there (rule 4). Everything else, a better playbook, a fix to the runner, a new behaviour-policy pattern, a reusable worker role, goes back to the public repositories as a pull request, with the client's name and data removed, and is credited to the provider who made it (rule 5). The changes list of each public repository then shows what the engagements taught us.

## Joining

This section becomes `join/index.html`, linked from *For providers* and from the menu.

### The provider application, and the waiting list

The form is built like the shop: a static page, no backend and no payment. Filling it in builds an email to agent@riskmandate.ai, opened in the applicant's own email app; a "copy as JSON" button copies the same application as JSON, for people whose email app does not open, or who want to keep it. Applications go on the waiting list; the newsroom article's six steps (apply, proof of work, peer review, an interview, a shadowed first pilot, standards) are how someone moves from the list to the providers page. Until there are enough members for peer review, the founders do steps two to four themselves (open question 10).

| Field | Required | Notes |
|---|---|---|
| Name | yes | as you want it shown |
| Company | no | if you apply as a company, the company's name |
| Email | yes | where we reply |
| Location | yes | city and country; for matching and time zones |
| What you deliver | yes | one paragraph |
| Which offers | yes | any of: task runs, dedicated compute, maintained repository, expert time; and any of the five project types |
| Rates | no | if you have them; the published prices apply otherwise |
| Languages | yes | the languages you can work in |
| Links | no | site, GitHub, LinkedIn, and a public vault or repository of a real run (proof of work) |
| How you heard | no | the same choices as the shop |
| Consent to publish your profile | yes, to be listed | a separate tick box: you agree that, once approved, your name, company, location, offers, languages and links are shown on the providers page; you can withdraw it by email at any time |
| Agreement to the rules of engagement | yes | a tick box linking to the rules |

The JSON the form copies:

```
{
  "type": "provider-application",
  "version": 1,
  "name": "", "company": "", "email": "", "location": "",
  "delivers": "", "offers": [], "project_types": [], "rates": "",
  "languages": [], "links": [], "heard": "",
  "consent_publish_profile": true, "agrees_rules": true,
  "created": "2026-10-16T12:00:00Z"
}
```

The email body is plain text, kept under 1,800 characters (the limit the shop already uses for mail links), with the JSON in full only in the copy.

### The public list of providers

Once an application is approved, and only with the consent tick, the provider is added to `data/providers.json`, and the providers page renders one card per entry from that file. The applications themselves never go into the repository: personal data stays out of git (open question 3). The first two entries are the founding providers, with only the fields they have confirmed.

### Keep me posted (learners)

A second, lighter form on the same page: an email address, an optional name, and what you are interested in (using it, delivering it, or just following). It builds a short email to agent@riskmandate.ai with the subject "Keep me posted", and the page also points to the [newsroom's own newsletter](https://newsroom.sgit.ai) for people who want the wider stream. There is no list software; replies are by hand for now (open question 3).

## The site, mapped

Dinis asked for the map: "map everything we need to change, because the URLs are going to change, the position is going to change, the menu is going to change". The source of truth for the current site is the inventory, [site-map-2026-10-16.json](../data/site-map-2026-10-16.json).

### Every current page, and its new place

| Current page | Today (menu group) | Decision | New place |
|---|---|---|---|
| `index.html` | The idea: Overview | **rewrite** | New home: three doors, the path, the providers, the proof, the rules |
| (the current home's content) | | **move** | `learn/overview.html`, "What ruv.sgit is", unchanged |
| `ruv-stack.html` | The idea | keep | Learn |
| `use-cases.html` | The idea | keep | Learn |
| `architecture.html` | The idea | keep | How it works, and Learn |
| `talk/index.html` | Tonight | keep URL, **rename** | Proof: "The talk, 15 October 2026" instead of "Tonight's talk"; the text moves to the past tense |
| `talk/player.html` | Tonight | keep | Proof: "Play the talk" |
| `talk/offline-10.html`, `talk/offline-5.html` | (unlisted) | keep | unlisted, linked from replicate |
| `talk/slides/*` (13 slides) | (unlisted) | keep | unchanged; they are the talk as given |
| `demo.html` | Tonight | keep, **unlist** | off the menu, with a line at the top: "historical: the five-minute demo for 15 October 2026" |
| `replicate.html` | Proofs; Tonight (offline) | keep | Learn |
| `ruv-sgit/index.html` | Proofs | keep | Proof, and How it works ("one run, six steps") |
| `ruv-sgit/ledger/index.html` | (unlisted) | keep, **list** | Proof: "The vault ledger" |
| `ruv-sgit/motion/`, `ruv-sgit/case/`, `ruv-sgit/define/*` | (unlisted) | keep | unchanged; linked from ruv.sgit |
| `pocs.html` | Proofs | keep | Proof |
| `app/index.html` | Proofs | keep | Proof |
| `studio/index.html` and `studio/v1` to `v7` | Proofs | keep | Learn |
| `business/index.html` | Work with us | **retire to a redirect** | to `clients/index.html` |
| `business/companies.html` | Work with us | **retire to a redirect** | to `clients/index.html#companies` |
| `business/teams.html` | Work with us | **retire to a redirect** | to `clients/index.html#teams` |
| `business/consultants.html` | Work with us | **retire to a redirect** | to `providers/index.html` |
| `shop/index.html` | Work with us | keep, **add a field** | For clients; gains "preferred provider" |
| `articles/index.html` and all eight articles | Articles; Work with us | keep | Learn; the business plan also under For clients |
| `articles/ruv-sgit-business-model.html` | Work with us | keep, **add a note** | a line at the top pointing to the rules of engagement where they differ (the split) |
| `admin/versions.html` | (version in the nav) | keep | unchanged |
| `vault/index.html` | (unlisted) | keep | unchanged |
| `llms.txt` | (footer) | **rewrite** | restructured around the three audiences |

New pages:

| New page | What it is |
|---|---|
| `clients/index.html` | For clients: the path, the offers, the project types, the providers, the proof, what stays yours; sections `#companies` and `#teams` |
| `providers/index.html` | For providers: why join, the founding providers, the list from `data/providers.json`, how to join |
| `rules/index.html` | The rules of engagement, worked examples and licences |
| `how-it-works/index.html` | The engagement path, who does what, matching, delivery, committing back |
| `join/index.html` | The provider application (`#provider`) and keep me posted (`#updates`) |
| `proof/index.html` | A hub: the runs, the ledger, the POCs, the live app, the talk |
| `learn/index.html` | A hub: what ruv.sgit is, rUv's stack, use cases, architecture, the studio, replicate, the articles |
| `learn/overview.html` | Today's home page content, moved |
| `data/providers.json` | Approved providers, consented fields only |
| `assets/join.js` | The two forms, built like `shop/shop.js` |

### The new menu

Today: **Tonight · The idea · Proofs · Work with us · Articles**. Proposed: **For clients · For providers · How it works · Proof · Learn · Join**.

| Group | Items |
|---|---|
| **For clients** | Overview · The shop · The offers and prices · For companies · For internal teams · The business plan |
| **For providers** | Overview · The providers · Rules of engagement · Apply to join |
| **How it works** | The engagement path · One run, six steps · Rules of engagement · Architecture |
| **Proof** | ruv.sgit runs · The vault ledger · The six POCs · Live app · The talk · Play the talk · The talk, live |
| **Learn** | What ruv.sgit is · All articles · rUv's stack · Use cases · The studio · Replicate · Run it offline · Set it up: the brief |
| **Join** | Apply as a provider · Keep me posted · Contact: agent@riskmandate.ai |

The footer's "work with us" link points to *For clients*, and gains "join as a provider". The version in the nav, the GitHub link and the theme picker stay as they are.

### The new home page

1. **The line.** What the service is, in one sentence: agent work by a Ruflo hive, with a written mandate per role and a vault you keep, delivered by people who do it in the open. No superlatives.
2. **Three doors.** *I want this done* (For clients), *I want to deliver this* (For providers), *I want to understand it* (Learn). Visible without scrolling at 1366 and at 390 pixels wide.
3. **The path.** The five steps, with prices, linking to the shop.
4. **The providers.** The two founding cards (register interest), and "apply to join".
5. **The proof.** The ledger's totals, read from `data/vaults.json` when the page loads (never pasted), and links to the POCs and the talk.
6. **The rules, in four lines.** Open source; your code and data stay yours; an equal split; whoever has the client bills. Linking to the full rules.
7. **Where this started.** The talk of 15 October, with the player and the long read.
8. **Built on rUv's stack.** The attribution line, as on every business page today.

### URL changes, and how old URLs keep working

GitHub Pages serves files; it has no server-side redirects. So every URL that leaves the menu keeps a file:

- **Redirect stubs.** Each retired page is replaced by a short HTML file with `<meta http-equiv="refresh" content="0; url=…">`, a `<link rel="canonical">` to the new page, a visible sentence ("This page has moved to …") and a plain link, for browsers and readers that ignore the refresh. The stubs keep the site's chrome, so they look like the site for the second they are seen.
- **Stable URLs.** `/talk/` and everything under it, `/articles/` and every article, `/ruv-sgit/` and the ledger, `/shop/`, `/pocs.html`, `/replicate.html` and `/data/*.json` do not move. They are linked from the talk, the newsroom article, the five articles and other sites.
- **The spoken URL.** The talk ended with "start at ruv.sgit.ai/business", and the newsroom article links to `/business/`. That stub stays for good.
- **Anchors.** Links into the current home page's sections (for example from the talk's last slides) are checked; where one would break, the anchor is pointed at `learn/overview.html`.
- **The validator.** `site/build/validate.py` learns about stubs: a stub must have a refresh, a canonical and a link that resolve. And a new check runs every URL in `site-map-2026-10-16.json` and fails if any of them no longer exists, as a page or a stub.

### Breaking changes

These are the changes that will surprise someone who knew the site on 16 October. Each goes into the release notes.

1. **The home page changes purpose.** Its content moves to `learn/overview.html`; the URL `/` now speaks to buyers, providers and learners.
2. **The menu changes completely.** Five groups become six; "Tonight", "The idea", "Proofs", "Work with us" and "Articles" are gone as names.
3. **The four business pages become redirects.** `business/index.html`, `consultants.html`, `companies.html` and `teams.html` stop holding content; their text is merged into *For clients* and *For providers*.
4. **"Tonight's talk" is renamed.** Same URL, new title and past tense.
5. **The demo script leaves the menu.** Same URL, marked historical.
6. **"We" changes meaning.** On the business pages "we" was Dinis and his agents; from now on it is the providers, under the rules of engagement.
7. **The money model changes.** The business plan's "target margin" was for a single operator; with providers, revenue is split equally between the parties. The plan's numbers stand as unit economics; the split sits on top.
8. **`llms.txt` is restructured.** Agents that read it by section will find new sections.
9. **The shop's order email gains a field** ("preferred provider"), so an order's text changes shape.
10. **The site version moves to v0.2.0** to mark the change of purpose (proposed; open question 13).

## The implementation plan

Five ruv.sgit runs, in order, each after the one before is reviewed. Each run has a spec in `poc/ruv-sgit/runs/`, a vault per run, a mandate per role, and a ledger entry, as every run so far. None of them changes the ledger, the talk, the player, the slides or the articles' content.

| Run | Purpose | Workers |
|---|---|---|
| **r13-ia** | Information architecture: the menu, the hubs, the redirects | architect (the menu in `assets/site.js`, the footer), redirector (the four stubs, `learn/overview.html`), checker (the validator: stubs, and every URL in the inventory) |
| **r14-home** | The new home and the audience pages | home (the new `index.html`), clients (`clients/index.html`, merging companies and teams), providers (`providers/index.html`, merging consultants) |
| **r15-rules** | The rules, how it works, the provider profiles | rules (`rules/index.html` from this article's rules), process (`how-it-works/index.html`), profiles (`data/providers.json`, the two founding cards, confirmed fields only) |
| **r16-join** | The forms | forms (`join/index.html`, `assets/join.js`), shop (the preferred provider field in `shop/shop.js`) |
| **r17-editor** | The editor pass and the record | editor (every new page against these rules: British English, plain words, additive, accurate), indexer (`llms.txt`, README, `admin/versions.json` with the breaking changes), archivist (the same fifteen screenshots again, as the "after" picture, and this article to v1.0.0 with its changes list) |

### Acceptance checks

**r13-ia**

- `python3 site/build/validate.py` passes, including the new checks.
- Every URL in `site-map-2026-10-16.json` loads, either as itself or as a stub whose refresh and link reach an existing page.
- The new menu opens and closes with mouse, keyboard (Escape) and touch, at 1366 and at 390 wide, with no horizontal scroll.
- `/business/` shows "This page has moved" and lands on *For clients*.

**r14-home**

- The three doors are visible without scrolling at 1366×768 and at 390×844.
- Every number on the home page is read from a data file when the page loads; none is typed in.
- The attribution to rUv's projects (MIT, by rUv / ruvnet) is on the home, clients and providers pages.
- Nothing on these pages says or implies that rUv's stack falls short; the wording is additive.

**r15-rules**

- The rules on `rules/index.html` match the approved version of this article word for word.
- A small script checks the worked examples' arithmetic (the splits add up to the price, to the penny).
- The provider cards show only fields that Dinis and Mondweep have confirmed; no photo, title or biography otherwise.

**r16-join**

- In Playwright, filling the provider form builds a `mailto:agent@riskmandate.ai` link with a body under 1,800 characters, and "copy as JSON" copies JSON that parses and has every required field.
- The form cannot be sent without the consent and rules tick boxes; submitting makes no network request.
- The keep-me-posted form builds its email the same way.
- The shop still builds a valid order with the new field empty.

**r17-editor**

- `validate.py` passes; every new page is in `llms.txt`.
- `admin/versions.json` has the release with the breaking changes listed.
- The "after" screenshots exist at the same fifteen views, and this article is at v1.0.0 with a changes list.

### What stays exactly as it is

- **The ledger**: `data/vaults.json`, the ledger page and every ruv.sgit page and animation.
- **The talk**: the talk timelines, the player, the thirteen slides and the two offline builds, as given on 15 October. Only the talk page's title and tense change.
- **The articles**: their URLs and their text. The business plan gains one note at the top.
- **The proofs**: the POCs, the live app, the studio, the evidence and the run specs.
- **The shop's prices and `data/offers.json`**, unless Dinis changes them (open question 5).

## Open questions for Dinis

Each has a proposed answer. A "yes" accepts it; anything else, write the change in.

1. **Mondweep's details and consent.** *Decided 16 Oct:* agreed; live with his name and LinkedIn.  Which name, affiliation, project types, offers, location, languages, links, photo and biography does he want shown, and has he agreed to his card? *Proposed:* publish only "Mondweep, from the Agentics Foundation" and the newsroom article's line until he has seen and approved the card; the same for Dinis's own card.
2. **Which Creative Commons licence.** *Decided 16 Oct:* CC BY 4.0.  *Proposed:* CC BY 4.0 for materials and playbooks (reuse for any purpose, with credit). CC BY-SA 4.0 would require derivatives to stay open too.
3. **Where applications and sign-ups go and are kept.** *Decided 16 Oct:* by email to agent@riskmandate.ai, kept in its private repository, never in git.  *Proposed:* by email to agent@riskmandate.ai; kept in a private sgit vault, not in the repository; a short privacy note on the form saying what we keep, why, for how long, and how to ask for it to be deleted.
4. **Register interest, or book.** *Proposed:* *register interest* on the founding cards until your and Mondweep's diaries are aligned, as the newsroom article says.
5. **Do prices stay public and fixed?** *Proposed:* yes: the published prices are the list prices for every provider for now; per-provider price bands within a range come later, once there are more providers.
6. **Who counts as a party in the split.** *Decided 16 Oct:* an equal split after costs replaces the platform share.  *Proposed:* a provider (a person or a company) that brings the client or delivers part of the work; one provider doing both is one party; bringing a client without delivering any of the work still counts as a party.
7. **Direct costs before the split.** *Decided 16 Oct:* yes, costs first, then the split.  *Proposed:* third-party costs (model tokens, compute) are reimbursed to whoever paid them before the split, itemised on the invoice.
8. **Who signs contracts.** *Proposed:* whoever bills signs with the client; providers in an engagement agree the rules of engagement with each other in a short written note (an email is enough to start).
9. **Ledger entries for client work.** *Decided 16 Oct:* private first.  *Proposed:* private by default; published only with the client's written agreement, and then only the measurements, never the content.
10. **Provider vetting.** *Proposed:* the newsroom article's six steps, with the founders doing the proof-of-work review and the interview until there are at least five providers, then peer review by two members.
11. **Currency and VAT.** *Proposed:* prices in GBP excluding VAT, as now; the party who bills charges VAT where it applies; other currencies quoted on request.
12. **The marketplace's name.** *Proposed:* "ruv.sgit providers" on the site, with "agentics engagements" (the newsroom article's term) as the description of what they deliver.
13. **The domain and the version.** *Proposed:* stay on ruv.sgit.ai (the newsroom article suggested a marketplace page on sgit.ai; sgit.ai links here instead), and call the change v0.2.0.
14. **The client's code rule, when a client wants everything closed.** *Proposed:* a custom arrangement under rule 8, agreed and priced before the work starts.

## What this does not claim

- **Nothing here is built yet.** This is a draft brief. The pages, the forms and the menu in it do not exist until runs r13 to r17 have made them.
- **No payment.** The site takes no money; orders and applications are emails, and a person replies.
- **No automation.** A person starts, watches and hands over every run; matching is by hand.
- **No providers beyond the two founding ones.** And neither is taking bookings yet.
- **No paid engagement yet.** The prices are the business plan's starting hypotheses.
- **The runs on this site were not policy-gated.** Enforcement was shown separately, in POC1.
- **Not rUv's offer.** This builds on his open-source projects (MIT, by rUv / ruvnet); it is not his service and does not speak for him or for the Agentics Foundation.

To ask a question, buy, or apply to join: [agent@riskmandate.ai](mailto:agent@riskmandate.ai).

## Where this comes from

Dinis Cruz's dictated brief of 16 October 2026 (quoted where his words are used); the newsroom article [Agentics, ready to sell](https://newsroom.sgit.ai/articles/agentics-ready-to-sell.html) (16 October 2026), read the same day; this site at v0.1.29: `site/assets/site.js` (the menu), `site/business/*.html`, `site/shop/`, `site/data/offers.json`, `site/data/vaults.json`, `site/llms.txt`, `README.md`, `site/admin/versions.json`, the [business plan](ruv-sgit-business-model.html) and the five articles of 15 October; the inventory [site-map-2026-10-16.json](../data/site-map-2026-10-16.json); and the run spec `poc/ruv-sgit/runs/r12-next-phase.spec.json`.

## Changes

- **v0.1.0 (DRAFT), 16 October 2026.** First draft, for Dinis to review.
- **v0.2.0 (DRAFT), 16 October 2026.** Dinis's answers applied: Mondweep live (name, LinkedIn); the split is equal after direct costs, with no platform share (the newsroom article's 5% to 20% was a market benchmark, not a use case); CC BY 4.0; applications by email to agent@riskmandate.ai, kept in its private repository, never in git; client work private first. Edited by the conductor directly, not by a run.
