// ruv.sgit.ai join page: the provider application and "keep me posted". Built like the shop: static, no backend, no payment,
// and no network request on submit. Each form builds a mailto: to CONTACT, opened in the visitor's own email app; the provider
// application can also be copied as JSON (the shape in articles/next-phase.html, "Joining"). Applications are kept by the agent
// at CONTACT in its own private repository, never in this site's git repository.
(() => {
  'use strict'
  const CONTACT = 'agent@riskmandate.ai'
  const MAIL_MAX = 1800   // characters of plain-text body, the same limit the shop uses for mail links
  const $ = id => document.getElementById(id)
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
  const live = msg => { const l = $('live'); l.textContent = ''; setTimeout(() => { l.textContent = msg }, 30) }
  const v = id => $(id).value.trim()
  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const clip = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s
  const checked = name => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value)
  const mailHref = (subject, body) => `mailto:${CONTACT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  function setErr (el, eid, msg, errs) {
    if (msg) { el.setAttribute('aria-invalid', 'true'); errs.push(el) } else el.removeAttribute('aria-invalid')
    $(eid).textContent = msg || ''
  }
  async function copyText (text, pre) {
    try { await navigator.clipboard.writeText(text); return true } catch (e) {
      try { const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); return document.execCommand('copy') } catch (e2) { return false }
    }
  }

  // ---- the provider application ----------------------------------------------------------------------------------
  function validateApp () {
    const errs = []
    setErr($('a-name'), 'ae-name', v('a-name') ? '' : 'Please give your name, as you want it shown.', errs)
    setErr($('a-email'), 'ae-email', !v('a-email') ? 'Please give an email address we can reply to.' : EMAIL.test(v('a-email')) ? '' : 'That email address does not look right.', errs)
    setErr($('a-location'), 'ae-location', v('a-location') ? '' : 'Please give your city and country.', errs)
    setErr($('a-delivers'), 'ae-delivers', v('a-delivers').length >= 10 ? '' : 'Please say, in a paragraph, what you deliver.', errs)
    const anyOffer = checked('offers').length + checked('project_types').length > 0
    setErr($('a-offers'), 'ae-offers', anyOffer ? '' : 'Please tick at least one offer or project type.', errs)
    if (!anyOffer) errs[errs.length - 1] = $('a-offers').querySelector('input')
    setErr($('a-languages'), 'ae-languages', languages().length ? '' : 'Please list the languages you can work in.', errs)
    setErr($('a-consent'), 'ae-consent', $('a-consent').checked ? '' : 'Please tick to consent to your profile being published once approved.', errs)
    setErr($('a-rules'), 'ae-rules', $('a-rules').checked ? '' : 'Please tick to agree to the rules of engagement.', errs)
    $('ae-all').textContent = errs.length ? `Please fix ${errs.length} thing${errs.length === 1 ? '' : 's'} above before sending.` : ''
    return errs
  }
  const languages = () => v('a-languages').split(/[,;\n]+/).map(s => s.trim()).filter(Boolean)
  const links = () => v('a-links').split(/[\n\s,]+/).map(s => s.trim()).filter(Boolean)
  function buildApp () {
    return {
      type: 'provider-application',
      version: 1,
      name: v('a-name'), company: v('a-company'), email: v('a-email'), location: v('a-location'),
      delivers: v('a-delivers'), offers: checked('offers'), project_types: checked('project_types'), rates: v('a-rates'),
      languages: languages(), links: links(), heard: v('a-heard'),
      consent_publish_profile: $('a-consent').checked, agrees_rules: $('a-rules').checked,
      created: new Date().toISOString()
    }
  }
  function appText (a) {
    let delivers = a.delivers, linkList = a.links
    const build = () => [
      'Provider application · ruv.sgit',
      `Created ${a.created.slice(0, 16).replace('T', ' ')} UTC`,
      '',
      `Name: ${a.name}`,
      a.company ? `Company: ${a.company}` : null,
      `Email: ${a.email}`,
      `Location: ${a.location}`,
      `Languages: ${a.languages.join(', ')}`,
      `Offers: ${a.offers.length ? a.offers.join(', ') : 'none ticked'}`,
      `Project types: ${a.project_types.length ? a.project_types.join('; ') : 'none ticked'}`,
      a.rates ? `Rates: ${a.rates}` : null,
      a.heard ? `Heard via: ${a.heard}` : null,
      '',
      'What I deliver:',
      delivers,
      '',
      'Links:',
      ...(linkList.length ? linkList.map(l => '- ' + l) : ['- none given']),
      '',
      `Consent to publish my profile once approved: ${a.consent_publish_profile ? 'yes' : 'no'}`,
      `I agree to the rules of engagement: ${a.agrees_rules ? 'yes' : 'no'}`,
      '',
      'The same application as JSON can be copied from the join page.'
    ].filter(x => x != null).join('\n')
    let txt = build()
    if (txt.length <= MAIL_MAX) return txt
    // keep it under the mailto limit: shorten the paragraph, then the links; contact details and the ticks stay intact
    delivers = clip(a.delivers, 600); txt = build()
    for (let keep = a.links.length - 1; txt.length > MAIL_MAX && keep >= 1; keep--) { linkList = [...a.links.slice(0, keep).map(l => clip(l, 200)), `… and ${a.links.length - keep} more (in the JSON copy)`]; txt = build() }
    if (txt.length > MAIL_MAX) { delivers = clip(a.delivers, 200); linkList = linkList.map(l => clip(l, 120)); txt = build() }
    return txt.length > MAIL_MAX ? clip(txt, MAIL_MAX) : txt
  }
  function showApp (a, mode) {
    const body = appText(a), href = mailHref(`Provider application: ${clip(a.name, 80)}`, body), json = JSON.stringify(a, null, 2)
    window.__joinApp = { app: a, text: body, mail: href, json }   // for checks
    const done = $('app-done')
    done.innerHTML = `<h3 id="app-done-h">Your application is ready</h3>
<p>${mode === 'mail' ? `Your email app should have opened with the application addressed to <b>${CONTACT}</b>: press send there.` : `The application is copied as JSON below; paste it into an email to <a href="mailto:${CONTACT}">${CONTACT}</a>, or keep it.`} It goes on the waiting list, and a person replies by email.</p>
<p class="k">The agent keeps it in its own private repository, never in this site's git repository.</p>
<div class="acts"><a class="b p" id="a-mail" href="${esc(href)}">${mode === 'mail' ? 'Open email again' : 'Open it as an email'}</a><button class="b" type="button" id="a-copy2">Copy as JSON</button></div>
<pre id="a-jsontext">${esc(json)}</pre>`
    done.hidden = false
    $('a-copy2').onclick = async () => { const ok = await copyText(json, $('a-jsontext')); $('a-copy2').textContent = ok ? 'Copied' : 'Select the JSON below and copy it'; live(ok ? 'Application copied as JSON.' : 'Copy failed: select the JSON and copy it.') }
    return done
  }
  $('apply').addEventListener('submit', e => {
    e.preventDefault()
    const errs = validateApp()
    if (errs.length) { errs[0].focus(); live($('ae-all').textContent); return }
    const done = showApp(buildApp(), 'mail')
    done.focus()
    live('Application ready. Opening your email app.')
    $('a-mail').click()   // the mailto opens the email app; the page stays put and nothing is sent from here
  })
  $('a-json').addEventListener('click', async () => {
    const errs = validateApp()
    if (errs.length) { errs[0].focus(); live($('ae-all').textContent); return }
    const done = showApp(buildApp(), 'json')
    const ok = await copyText(window.__joinApp.json, $('a-jsontext'))
    $('a-json').textContent = ok ? 'Copied as JSON' : 'Copy as JSON'
    done.focus()
    live(ok ? 'Application copied as JSON.' : 'Copy failed: select the JSON below and copy it.')
  })
  $('apply').addEventListener('input', () => { if ($('ae-all').textContent) validateApp() })
  $('apply').addEventListener('change', () => { if ($('ae-all').textContent) validateApp() })

  // ---- keep me posted ----------------------------------------------------------------------------------------------
  function validateKeep () {
    const errs = []
    setErr($('k-email'), 'ke-email', !v('k-email') ? 'Please give an email address.' : EMAIL.test(v('k-email')) ? '' : 'That email address does not look right.', errs)
    const it = checked('interest')
    setErr($('k-interest'), 'ke-interest', it.length ? '' : 'Please choose what you are interested in.', errs)
    if (!it.length) errs[errs.length - 1] = $('k-interest').querySelector('input')
    return errs
  }
  $('keep').addEventListener('submit', e => {
    e.preventDefault()
    const errs = validateKeep()
    if (errs.length) { errs[0].focus(); live(`Please fix ${errs.length} thing${errs.length === 1 ? '' : 's'} before sending.`); return }
    const k = { email: v('k-email'), name: v('k-name'), interest: checked('interest')[0], created: new Date().toISOString() }
    const body = [
      'Please keep me posted about ruv.sgit.', '',
      `Email: ${k.email}`, k.name ? `Name: ${k.name}` : null, `Interested in: ${k.interest}`, '',
      'Sent from https://ruv.sgit.ai/join/index.html#updates'
    ].filter(x => x != null).join('\n')
    const href = mailHref('Keep me posted', body.length > MAIL_MAX ? clip(body, MAIL_MAX) : body)
    window.__joinKeep = { keep: k, text: body, mail: href }   // for checks
    const done = $('upd-done')
    done.innerHTML = `<h3 id="upd-done-h">Your email is ready</h3>
<p>Your email app should have opened with a short email to <b>${CONTACT}</b>, subject "Keep me posted": press send there. A person replies by hand.</p>
<p class="k">For the wider stream, the newsroom has its own newsletter at <a href="https://newsroom.sgit.ai">newsroom.sgit.ai</a>.</p>
<div class="acts"><a class="b p" id="k-mail" href="${esc(href)}">Open email again</a></div>`
    done.hidden = false
    done.focus()
    live('Email ready. Opening your email app.')
    $('k-mail').click()
  })
  $('keep').addEventListener('input', e => { if (e.target.closest('[aria-invalid="true"]')) validateKeep() })
})()
