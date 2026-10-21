/* ruv.sgit providers: renders the providers list (providers/index.html, #provider-list) and a provider's profile
   (providers/<id>.html, <body data-provider="<id>">) from data/providers.json and data/offers.json, read at load.
   Nothing about a provider is typed into this file: names, bios, specialisms, proof of work and links come from
   providers.json exactly as given; prices come from offers.json. The HTML carries static fallbacks (name, headline,
   short bio) so a page reads without JavaScript and in link previews.
   Enquire to book opens an email to agent@riskmandate.ai with the offer and the provider filled in; no payment. */
(function () {
  'use strict';
  var CONTACT = 'agent@riskmandate.ai';
  var root = document.body.dataset.root || '';
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var $ = function (id) { return document.getElementById(id); };
  var gbp = function (n) { return '£' + Number(n).toLocaleString('en-GB', { minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 }); };
  var ext = function (u) { return /^https?:\/\//.test(u); };
  // an internal URL in the data is relative to the site root; an external one opens as a normal link, rel="noopener"
  var href = function (u) { return ext(u) ? u : root + u; };
  var link = function (l, cls) { return '<a' + (cls ? ' class="' + cls + '"' : '') + ' href="' + esc(href(l.url)) + '"' + (ext(l.url) ? ' rel="noopener"' : '') + '>' + esc(l.label) + '</a>'; };
  var host = function (u) { try { return new URL(u).host.replace(/^www\./, ''); } catch (e) { return ''; } };

  // the five project types of the newsroom article (next-phase brief, "The engagement path"): packages of the four offers;
  // `from` names the offers.json items that set the starting price, so no price is typed here
  var TYPES = [
    { id: 'first-run', title: 'A first run, with a guide', text: 'A task run on a real problem of yours, with expert time to shape the brief and read the vault with you.', from: ['run-s', 'expert-hours'] },
    { id: 'policy', title: "A behaviour policy for one team's agents", text: 'A day to write the Agent Behaviour Policy for one team: what each agent can reach, may do, and is stopped from doing.', from: ['expert-day'] },
    { id: 'pilot', title: 'A four-day pilot', text: 'ruv.sgit set up in your own environment (Claude Code, AWS or your own), with your policies and your first runs, then handed over.', from: ['expert-days'] },
    { id: 'workshop', title: 'A talk or workshop, built the way ours was', text: 'A talk or workshop for your people, prepared with ruv.sgit runs the way ours was, every run in a vault you keep.', from: [] },
    { id: 'review', title: 'A review of an agent that is already running', text: 'A look at an agent you already run: what it can reach, what it does, and the behaviour policy it should have.', from: [] }
  ];
  // the engagement path (next-phase brief, "How it works"), short; prices filled from offers.json
  var PATH = [
    ['A conversation', 'What you want agents to do, and what they must never do. Free.', null],
    ['A first run', 'A task run on a real problem, no network access, materials provided up front.', ['run-s', 'run-m', 'run-l']],
    ['Expert time', 'Two hours to steer it, or a day to write the behaviour policy for one team.', ['expert-hours', 'expert-day']],
    ['A pilot', 'Four days setting it up in your own environment.', ['expert-days']],
    ['Run it yourself', 'The maintained repository: the code that runs this, kept current.', ['repo-individual', 'repo-team', 'repo-white-label']]
  ];
  var RULES = [
    ['Open', 'Everything we publish is open source (Apache-2.0) and Creative Commons (CC BY 4.0); rUv\'s projects are MIT, by rUv / ruvnet.'],
    ['Your code and data stay yours', 'They are not published, reused or kept after the engagement; each job runs in its own encrypted vault, handed to you.'],
    ['Equal split, after costs', 'Direct costs go back to whoever paid them, itemised; what is left is split equally between the providers involved.'],
    ['Whoever has the client bills', 'One invoice, from the provider you work with; they pay the other parties their share.']
  ];

  // Enquire to book: a mailto with a short plain-text body, kept well under 1,800 characters
  function mailto(offer, provider) {
    var subject = 'Enquiry: ' + (offer || 'a conversation') + (provider ? ' with ' + provider.name : '');
    var body = [
      'Hello,', '',
      'I would like to enquire about: ' + (offer || 'a conversation'),
      'Preferred provider: ' + (provider ? provider.name : 'none'), '',
      'Who it is for (name, organisation, role):', '', '',
      'What do you want agents to do?', '', '',
      'What must they never do?', '', '',
      'When would you like to start?', '', '',
      '(sent from ' + location.href.split('#')[0] + ')'
    ].join('\n');
    if (body.length > 1700) body = body.slice(0, 1700);
    return 'mailto:' + CONTACT + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  }
  var shopUrl = function (p) { return root + 'shop/index.html?provider=' + encodeURIComponent(p.id); };

  function avatar(p, cls) {
    // a photo only when providers.json gives a local path (never a remote image); otherwise the initials
    if (p.photo && !/^[a-z]+:/i.test(p.photo) && !/^\/\//.test(p.photo)) return '<span class="' + cls + ' has-photo"><img src="' + esc(root + p.photo) + '" alt="Photo of ' + esc(p.name) + '" width="160" height="160"></span>';
    return '<span class="' + cls + '" role="img" aria-label="' + esc(p.name) + ' (initials)"><span aria-hidden="true">' + esc(p.initials) + '</span></span>';
  }
  var avail = function (s) { s = String(s || 'enquire to book'); return s.charAt(0).toUpperCase() + s.slice(1); };
  var items = function (offers) { var m = {}; offers.groups.forEach(function (g) { g.items.forEach(function (i) { m[i.id] = i; }); }); return m; };
  var range = function (g) {
    var ps = g.items.map(function (i) { return i.price; }), lo = Math.min.apply(null, ps), hi = Math.max.apply(null, ps), unit = g.items[0].unit;
    var same = g.items.every(function (i) { return i.unit === unit; });
    return gbp(lo) + (hi > lo ? ' to ' + gbp(hi) : '') + (same ? ' ' + unit : '');
  };

  // ---- the providers list (providers/index.html) ----
  function renderList(el, data) {
    el.innerHTML = data.providers.map(function (p) {
      var page = root + p.page;
      return '<article class="pv-card">' +
        '<div class="pv-head">' + avatar(p, 'pv-av') + '<div class="pv-id"><h3><a href="' + esc(page) + '">' + esc(p.name) + '</a></h3>' +
        (p.founding ? '<span class="badge t pv-badge">Founding provider</span>' : '') + '</div></div>' +
        '<p class="pv-headline">' + esc(p.headline) + '</p>' +
        '<p class="pv-meta">' + esc(p.location) + ' · ' + esc(avail(p.availability)) + '</p>' +
        '<p class="pv-bio">' + esc(p.bio_short) + '</p>' +
        '<ul class="pv-tags" aria-label="Specialisms">' + p.specialisms.slice(0, 4).map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul>' +
        '<div class="pv-acts"><a class="btn p" href="' + esc(page) + '">View profile</a><a class="btn" href="' + esc(mailto(null, p)) + '">Enquire to book</a></div>' +
        '</article>';
    }).join('');
    var c = $('provider-count');
    if (c) c.textContent = data.providers.length + (data.providers.length === 1 ? ' provider' : ' providers') + ', listed with their consent · updated ' + data.updated;
  }

  // ---- a provider's profile (providers/<id>.html) ----
  function renderProfile(p, offers) {
    var byId = items(offers), first = p.name.split(' ')[0];
    document.title = p.name + ' · ruv.sgit providers';
    var set = function (id, html) { var e = $(id); if (e) e.innerHTML = html; };
    set('pf-avatar', avatar(p, 'pf-av'));
    set('pf-name', esc(p.name));
    set('pf-headline', esc(p.headline));
    set('pf-location', esc(p.location));
    set('pf-avail', esc(avail(p.availability)));
    set('pf-short', esc(p.bio_short));
    var f = $('pf-founding'); if (f) f.hidden = !p.founding;
    ['pf-enquire', 'pf-enquire-2'].forEach(function (id) { var e = $(id); if (e) e.href = mailto(null, p); });
    ['pf-shop', 'pf-shop-2'].forEach(function (id) { var e = $(id); if (e) e.href = shopUrl(p); });
    set('pf-first', esc(first));

    set('pf-bio', p.bio_long.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('') +
      (p.role_here ? '<p class="pf-role"><b>On ruv.sgit.</b> ' + esc(p.role_here) + '</p>' : ''));
    set('pf-tags', p.specialisms.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join(''));
    set('pf-glance', '<div><dt>Based in</dt><dd>' + esc(p.location) + '</dd></div>' +
      '<div><dt>Availability</dt><dd>' + esc(avail(p.availability)) + '</dd></div>' +
      '<div><dt>Offers</dt><dd>' + p.offers.map(function (id) { var g = offers.groups.find(function (x) { return x.id === id; }); return g ? esc(g.title) : ''; }).filter(Boolean).join(', ') + '</dd></div>' +
      '<div><dt>Enquiries</dt><dd><a href="mailto:' + CONTACT + '">' + CONTACT + '</a></dd></div>');
    set('pf-links', p.links.map(function (l) { return '<li>' + link(l) + (ext(l.url) ? ' <span class="pf-host">' + esc(host(l.url)) + '</span>' : '') + '</li>'; }).join(''));

    // what I can do for you: the provider's offers, in offers.json order, with every price
    set('pf-offers', offers.groups.filter(function (g) { return p.offers.indexOf(g.id) >= 0; }).map(function (g) {
      return '<article class="pf-offer" id="offer-' + esc(g.id) + '"><h3>' + esc(g.title) + '</h3>' +
        '<p class="pf-from">' + esc(range(g)) + '</p>' +
        '<p class="pf-sum">' + esc(g.summary) + '</p>' +
        '<ul class="pf-prices">' + g.items.map(function (i) { return '<li><span>' + esc(i.name) + '<small>' + esc(i.summary) + '</small></span><b>' + esc(gbp(i.price)) + '<small>' + esc(i.unit) + '</small></b></li>'; }).join('') + '</ul>' +
        '<div class="pf-oacts"><a class="btn p" href="' + esc(mailto(g.title, p)) + '">Enquire about ' + esc(g.title.toLowerCase()) + '</a><a class="pf-more" href="' + esc(shopUrl(p)) + '">order in the shop</a></div></article>';
    }).join(''));
    set('pf-vat', 'Prices in ' + esc(offers.currency) + ', excluding VAT: the published list prices, the same for every provider. The site takes no payment: you enquire, and a person replies with dates and a quote.');

    // ways to start: the five project types, priced from offers.json where an offer sets the price
    set('pf-types', TYPES.map(function (t) {
      var parts = t.from.map(function (id) { return byId[id]; }).filter(Boolean);
      var price = parts.length ? 'From ' + gbp(parts.reduce(function (s, i) { return s + i.price; }, 0)) + ' (' + parts.map(function (i) { return i.name.toLowerCase() + ' ' + gbp(i.price); }).join(' + ') + ')' : 'Quoted after a conversation';
      return '<li class="pf-type"><h3>' + esc(t.title) + '</h3><p>' + esc(t.text) + '</p><p class="pf-tprice">' + esc(price) + '</p>' +
        '<a href="' + esc(mailto(t.title, p)) + '">Enquire about this <span aria-hidden="true">&rarr;</span></a></li>';
    }).join(''));

    set('pf-path', PATH.map(function (s) {
      var its = (s[2] || []).map(function (id) { return byId[id]; }).filter(Boolean);
      var price = its.length ? its.map(function (i) { return gbp(i.price); }).join(its.length > 2 ? ', ' : ' or ').replace(/, ([^,]*)$/, ' or $1') + (its.every(function (i) { return i.unit === its[0].unit; }) ? ' ' + its[0].unit.replace(/^per /, 'a ').replace('a engagement', 'an engagement') : '') : 'free';
      return '<li><h3>' + esc(s[0]) + ' <span class="pf-step-price">' + esc(price) + '</span></h3><p>' + esc(s[1]) + '</p></li>';
    }).join(''));

    set('pf-proof', p.proof_of_work.map(function (l) { return '<li>' + link(l) + (ext(l.url) ? ' <span class="pf-host">' + esc(host(l.url)) + '</span>' : '') + '</li>'; }).join(''));
    set('pf-rules', RULES.map(function (r) { return '<li><b>' + esc(r[0]) + '.</b> ' + esc(r[1]) + '</li>'; }).join(''));
  }

  function load(u) { return fetch(root + u).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); }); }
  var list = $('provider-list'), pid = document.body.dataset.provider;
  if (!list && !pid) return;
  Promise.all([load('data/providers.json'), load('data/offers.json')]).then(function (d) {
    if (list) renderList(list, d[0]);
    if (pid) {
      var p = d[0].providers.find(function (x) { return x.id === pid; });
      if (p) renderProfile(p, d[1]);
    }
    document.body.classList.add('pv-ready');
  }).catch(function () {
    document.querySelectorAll('.pv-fallback').forEach(function (e) { e.hidden = false; });
  });
  window.RuvProviders = { mailto: mailto };
})();
