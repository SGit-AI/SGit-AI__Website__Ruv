// ruv.sgit.ai shop: a mix-and-match cart that emails the order. No payment, no tracking; the only network call is the
// catalogue (../data/offers.json, or a same-origin ?offers=<url> for testing). The order always goes to CONTACT.
(() => {
  'use strict'
  const CONTACT = 'agent@riskmandate.ai'
  const KEY = 'ruv.shop.cart'
  const MAIL_MAX = 1800   // characters of plain-text body, for mailto limits
  const $ = id => document.getElementById(id)
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
  const live = msg => { const l = $('live'); l.textContent = ''; setTimeout(() => { l.textContent = msg }, 30) }
  const params = new URLSearchParams(location.search)

  let CAT = null, ITEMS = new Map(), cart = []
  const fmt = (n, cur) => n == null ? 'on request' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: cur || CAT?.currency || 'GBP', minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n)
  const plain = n => n == null ? 'on request' : (CAT?.currency || 'GBP') + ' ' + (Number.isInteger(n) ? n.toLocaleString('en-GB') : n.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))

  // ---- catalogue -------------------------------------------------------------------------------------------------
  function catalogueUrl () {
    const q = params.get('offers')
    if (q) { try { const u = new URL(q, location.href); if (u.origin === location.origin) return u.href } catch (e) {} }
    return '../data/offers.json'
  }
  function defaults (it) { const o = {}; (it.options || []).forEach(op => { if (op.choices?.length) o[op.id] = op.choices[0].id }); return o }
  function choice (it, opId, chId) { const op = (it.options || []).find(o => o.id === opId); return op && (op.choices || []).find(c => c.id === chId) }
  function unitPrice (it, opts) {
    if (typeof it.price !== 'number') return null
    let p = it.price
    for (const op of it.options || []) { const c = choice(it, op.id, opts[op.id]); if (c && typeof c.delta === 'number') p += c.delta }
    return Math.round(p * 100) / 100
  }
  const maxQ = it => Number.isInteger(it.max_qty) && it.max_qty > 0 ? it.max_qty : 99
  const lineKey = (id, opts) => id + '|' + Object.keys(opts).sort().map(k => k + '=' + opts[k]).join('&')

  // ---- cart state --------------------------------------------------------------------------------------------------
  function load () {
    let raw = []
    try { raw = JSON.parse(localStorage.getItem(KEY) || '[]') } catch (e) { raw = [] }
    if (!Array.isArray(raw)) raw = []
    const out = []
    for (const l of raw) {
      const it = l && ITEMS.get(l.id); if (!it) continue
      const opts = defaults(it)
      for (const k of Object.keys(opts)) if (l.opts && choice(it, k, l.opts[k])) opts[k] = l.opts[k]
      const qty = Math.min(maxQ(it), Math.max(1, parseInt(l.qty, 10) || 1))
      const ex = out.find(x => x.key === lineKey(it.id, opts))
      if (ex) ex.qty = Math.min(maxQ(it), ex.qty + qty); else out.push({ key: lineKey(it.id, opts), id: it.id, opts, qty })
    }
    return out
  }
  function save () { try { localStorage.setItem(KEY, JSON.stringify(cart.map(({ id, opts, qty }) => ({ id, opts, qty })))) } catch (e) {} }
  function add (id, opts, qty) {
    const it = ITEMS.get(id); if (!it) return false
    const key = lineKey(id, opts), ex = cart.find(l => l.key === key)
    let capped = false
    if (ex) { const n = ex.qty + qty; capped = n > maxQ(it); ex.qty = Math.min(maxQ(it), n) } else { capped = qty > maxQ(it); cart.push({ key, id, opts: { ...opts }, qty: Math.min(maxQ(it), qty) }) }
    save(); renderCart()
    live(`Added ${qty} × ${it.name} to your order.` + (capped ? ` Limited to ${maxQ(it)}.` : '') + ` ${summaryText()}`)
    return true
  }
  function totals () {
    let sum = 0, onReq = 0, n = 0
    for (const l of cart) { const it = ITEMS.get(l.id), u = unitPrice(it, l.opts); n += l.qty; if (u == null) onReq++; else sum += u * l.qty }
    return { sum: Math.round(sum * 100) / 100, onReq, n }
  }
  const summaryText = () => { const t = totals(); return t.n ? `Order: ${t.n} item${t.n === 1 ? '' : 's'}, total ${fmt(t.sum)}${t.onReq ? ' + priced on request' : ''}.` : 'Your order is empty.' }
  const optText = (it, opts) => (it.options || []).map(op => { const c = choice(it, op.id, opts[op.id]); return c ? `${op.label}: ${c.label}` : '' }).filter(Boolean).join(' · ')

  // ---- render: catalogue -------------------------------------------------------------------------------------------
  // honest status per group, shown under its summary (the catalogue holds prices; this holds what is not built yet)
  const STATUS = {
    runs: 'Not automated end to end yet: a person on our side starts, watches and hands over every run. The materials sandbox for uploads is not built yet; we agree how materials reach the run when we reply.',
    compute: 'Not built yet: dedicated compute is designed, and SG Compute is not connected to runs. EC2 prices are on-demand London rates from third-party aggregators, to confirm on AWS\'s price list.'
  }
  function renderCatalogue () {
    const host = $('catalogue')
    host.innerHTML = (CAT.groups || []).map(g => `<section class="grp" id="g-${esc(g.id)}" aria-labelledby="gh-${esc(g.id)}">
<h2 id="gh-${esc(g.id)}">${esc(g.title)}</h2>${g.summary ? `<p>${esc(g.summary)}</p>` : ''}${g.who ? `<p class="k who">For: ${esc(g.who)}</p>` : ''}${STATUS[g.id] ? `<p class="callout warn">${esc(STATUS[g.id])}</p>` : ''}
<div class="items">${(g.items || []).map(itemCard).join('')}</div></section>`).join('') +
      `<p class="k">Catalogue updated ${esc(CAT.updated || '')}. Prices in ${esc(CAT.currency || 'GBP')}, excluding VAT. An item “on request” can still be ordered: we price it when we follow up.</p>`
    host.removeAttribute('aria-busy')
    host.querySelectorAll('form.item').forEach(f => {
      const it = ITEMS.get(f.dataset.id)
      const upd = () => { const p = unitPrice(it, readOpts(f, it)); f.querySelector('.pv').textContent = fmt(p) }
      f.addEventListener('change', upd)
      f.addEventListener('submit', e => {
        e.preventDefault()
        const qi = f.querySelector('input[name=qty]'), q = parseInt(qi.value, 10)
        if (!(q >= 1)) { qi.setAttribute('aria-invalid', 'true'); qi.focus(); live('Quantity must be at least 1.'); return }
        qi.removeAttribute('aria-invalid')
        add(it.id, readOpts(f, it), Math.min(q, maxQ(it)))
        qi.value = 1
      })
    })
  }
  function readOpts (f, it) { const o = defaults(it); (it.options || []).forEach(op => { const s = f.querySelector(`select[data-op="${CSS.escape(op.id)}"]`); if (s && choice(it, op.id, s.value)) o[op.id] = s.value }); return o }
  function itemCard (it) {
    const id = esc(it.id), p = unitPrice(it, defaults(it))
    const opts = (it.options || []).filter(op => op.choices?.length).map(op => `<label class="fld"><span>${esc(op.label)}</span><select data-op="${esc(op.id)}">${op.choices.map(c => `<option value="${esc(c.id)}">${esc(c.label)}${typeof c.delta === 'number' && c.delta ? ` (${c.delta > 0 ? '+' : '−'}${esc(fmt(Math.abs(c.delta)))})` : ''}</option>`).join('')}</select></label>`).join('')
    return `<form class="card item" id="item-${id}" data-id="${id}" aria-labelledby="ih-${id}">
<h3 id="ih-${id}">${esc(it.name)}</h3>
<div class="price${p == null ? ' req' : ''}"><span class="pv">${p == null ? 'Priced on request' : esc(fmt(p))}</span>${it.unit ? `<small>${esc(it.unit)}</small>` : ''}</div>
${it.summary ? `<p>${esc(it.summary)}</p>` : ''}
${it.details?.length ? `<ul>${it.details.map(d => `<li>${esc(d)}</li>`).join('')}</ul>` : ''}
<div class="opts">${opts}
<div class="addrow"><label class="fld"><span>Quantity</span><input name="qty" type="number" inputmode="numeric" min="1" max="${maxQ(it)}" value="1"></label><button class="b p full" type="submit">Add<span class="sr"> ${esc(it.name)} to order</span></button></div></div>
</form>`
  }

  // ---- render: cart ------------------------------------------------------------------------------------------------
  function renderCart () {
    const body = $('cart-body'), t = totals()
    if (!cart.length) body.innerHTML = '<p class="empty">Nothing yet: add something from the catalogue.</p>'
    else {
      body.innerHTML = `<ol>${cart.map((l, i) => {
        const it = ITEMS.get(l.id), u = unitPrice(it, l.opts), o = optText(it, l.opts)
        return `<li class="line"><div class="nm">${esc(it.name)}</div>${o ? `<div class="op">${esc(o)}</div>` : ''}<div class="op">${esc(fmt(u))}${u != null && it.unit ? ' ' + esc(it.unit) : ''}</div>
<div class="row" role="group" aria-label="${esc(it.name)} quantity"><button class="b sm" type="button" data-act="dec" data-i="${i}" aria-label="One fewer ${esc(it.name)}"${l.qty <= 1 ? ' disabled' : ''}>−</button><span class="q" aria-label="quantity">${l.qty}</span><button class="b sm" type="button" data-act="inc" data-i="${i}" aria-label="One more ${esc(it.name)}"${l.qty >= maxQ(it) ? ' disabled' : ''}>+</button><button class="b link" type="button" data-act="rm" data-i="${i}" aria-label="Remove ${esc(it.name)}">remove</button><span class="sub">${u == null ? 'on request' : esc(fmt(u * l.qty))}</span></div></li>`
      }).join('')}</ol>
<div class="tot"><span>Total</span><b id="total">${esc(fmt(t.sum))}</b></div>${t.onReq ? `<p class="k">+ ${t.onReq} line${t.onReq === 1 ? '' : 's'} priced on request</p>` : ''}
<p class="k">Prices exclude VAT. No payment is taken here.</p>
<div class="acts"><a class="b p full" href="#checkout-sec">Check out</a><button class="b" type="button" data-act="clear">Empty</button></div>`
    }
    const bar = $('mbar'); bar.hidden = !cart.length; document.body.classList.toggle('has-bar', !!cart.length)
    $('mbar-t').textContent = cart.length ? `${t.n} item${t.n === 1 ? '' : 's'} · ${fmt(t.sum)}${t.onReq ? ' +' : ''}` : ''
  }
  $('cart-body').addEventListener('click', e => {
    const b = e.target.closest('button[data-act]'); if (!b) return
    const act = b.dataset.act, i = +b.dataset.i, l = cart[i], it = l && ITEMS.get(l.id)
    if (act === 'clear') { cart = []; save(); renderCart(); live('Your order is empty.'); $('cart').focus(); return }
    if (!l) return
    if (act === 'inc') l.qty = Math.min(maxQ(it), l.qty + 1)
    if (act === 'dec') l.qty = Math.max(1, l.qty - 1)
    if (act === 'rm') cart.splice(i, 1)
    save(); renderCart()
    live(act === 'rm' ? `Removed ${it.name}. ${summaryText()}` : `${it.name}: quantity ${l.qty}. ${summaryText()}`)
    // keep focus on the same control after re-render (or a sensible neighbour)
    const sel = act === 'rm' ? (cart.length ? `button[data-act="rm"][data-i="${Math.min(i, cart.length - 1)}"]` : null) : `button[data-act="${act}"][data-i="${i}"]:not([disabled])`
    const nx = sel && $('cart-body').querySelector(sel)
    ;(nx || $('cart-body').querySelector(`button[data-i="${i}"]:not([disabled])`) || $('cart')).focus()
  })

  // ---- checkout ----------------------------------------------------------------------------------------------------
  const FIELDS = { name: 'f-name', email: 'f-email', organisation: 'f-org', start: 'f-start', what: 'f-what', heard: 'f-heard' }
  function validate () {
    const errs = []
    const set = (id, eid, msg) => { const el = $(id); if (msg) { el.setAttribute('aria-invalid', 'true'); errs.push(el) } else el.removeAttribute('aria-invalid'); $(eid).textContent = msg || '' }
    const v = id => $(id).value.trim()
    set('f-name', 'e-name', v('f-name') ? '' : 'Please give your name.')
    set('f-email', 'e-email', !v('f-email') ? 'Please give an email address we can reply to.' : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('f-email')) ? '' : 'That email address does not look right.')
    set('f-what', 'e-what', v('f-what').length >= 10 ? '' : 'Please say, in a sentence or two, what you want done.')
    $('e-cart').textContent = cart.length ? '' : 'Your order is empty: add at least one item from the catalogue.'
    if (!cart.length) errs.push($('catalogue').querySelector('select, input') || $('cart'))
    return errs
  }
  function orderId () {
    const d = new Date(), p = n => String(n).padStart(2, '0')
    const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', r = new Uint32Array(4)
    try { crypto.getRandomValues(r) } catch (e) { for (let i = 0; i < 4; i++) r[i] = Math.floor(Math.random() * 1e9) }
    return `RS-${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${[...r].map(x => A[x % A.length]).join('')}`
  }
  function buildOrder () {
    const t = totals(), f = {}
    for (const [k, id] of Object.entries(FIELDS)) f[k] = $(id).value.trim()
    return {
      id: orderId(), created: new Date().toISOString(), to: CONTACT, currency: CAT.currency || 'GBP', vat: 'excluded', payment: 'none taken: we follow up by email',
      catalogue_updated: CAT.updated || null, page: location.origin + location.pathname,
      lines: cart.map(l => {
        const it = ITEMS.get(l.id), u = unitPrice(it, l.opts)
        return { item: it.id, name: it.name, unit: it.unit || null, base_price: typeof it.price === 'number' ? it.price : null,
          options: (it.options || []).map(op => { const c = choice(it, op.id, l.opts[op.id]); return c ? { option: op.id, label: op.label, choice: c.id, choice_label: c.label, delta: c.delta ?? 0 } : null }).filter(Boolean),
          unit_price: u, qty: l.qty, subtotal: u == null ? null : Math.round(u * l.qty * 100) / 100 }
      }),
      totals: { items: t.n, total: t.sum, lines_on_request: t.onReq },
      customer: f
    }
  }
  function lineTxt (l) { return `- ${l.qty} x ${l.name}${l.options.length ? ' (' + l.options.map(o => o.choice_label).join(', ') + ')' : ''}: ` + (l.unit_price == null ? 'priced on request' : `${plain(l.unit_price)}${l.unit ? ' ' + l.unit : ''} = ${plain(l.subtotal)}`) }
  function orderText (o, short) {
    const c = o.customer, clip = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s
    const head = [`Order ${o.id} · ruv.sgit`, `Created ${o.created.slice(0, 16).replace('T', ' ')} UTC`, '']
    const who = [`Name: ${c.name}`, `Email: ${c.email}`, c.organisation && `Organisation: ${c.organisation}`, c.start && `Preferred start: ${c.start}`, c.heard && `Heard via: ${c.heard}`].filter(Boolean)
    let lines = o.lines.map(lineTxt)
    const tot = [`Total: ${plain(o.totals.total)} excl. VAT (${o.totals.items} item${o.totals.items === 1 ? '' : 's'})` + (o.totals.lines_on_request ? ` + ${o.totals.lines_on_request} line${o.totals.lines_on_request === 1 ? '' : 's'} priced on request` : ''), 'No payment taken: please follow up by email.']
    let what = c.what
    const build = () => [...head, 'Lines:', ...lines, '', ...tot, '', 'What I want done:', what, '', ...who].join('\n')
    let txt = build()
    if (!short || txt.length <= MAIL_MAX) return txt
    // summarise for mailto: shorten the paragraph, then fold lines, keeping totals and contact details intact
    const note = '[summary: the full order is in the copied text and the downloaded JSON]'
    what = clip(c.what, 500); head.push(note, ''); txt = build()
    for (let keep = o.lines.length - 1; txt.length > MAIL_MAX && keep >= 1; keep--) {
      const rest = o.lines.slice(keep)
      lines = [...o.lines.slice(0, keep).map(lineTxt), `- … and ${rest.length} more line${rest.length === 1 ? '' : 's'}`]
      txt = build()
    }
    if (txt.length > MAIL_MAX) { what = clip(c.what, 160); txt = build() }
    return txt.length > MAIL_MAX ? clip(txt, MAIL_MAX) : txt
  }
  const mailHref = o => `mailto:${CONTACT}?subject=${encodeURIComponent(`Order ${o.id} · ruv.sgit`)}&body=${encodeURIComponent(orderText(o, true))}`

  $('checkout').addEventListener('submit', e => {
    e.preventDefault()
    const errs = validate()
    if (errs.length) { errs[0].focus(); live(`Please fix ${errs.length} thing${errs.length === 1 ? '' : 's'} before sending.`); return }
    const o = buildOrder(), full = orderText(o, false), href = mailHref(o)
    window.__shopOrder = { order: o, text: full, mail: href }   // for checks
    const done = $('done')
    done.innerHTML = `<h3 id="done-h" style="margin-top:0">Order ${esc(o.id)} is ready</h3>
<p>Your email app should have opened with the order addressed to <b>${CONTACT}</b>: press send there. We follow up by email. No payment has been taken.</p>
<p class="callout warn">If your email app did not open, copy the order and send it to <a href="mailto:${CONTACT}">${CONTACT}</a>.</p>
<div class="acts"><a class="b p" id="mail-again" href="${esc(href)}">Open email again</a><button class="b" type="button" id="copy">Copy order</button><button class="b" type="button" id="dl">Download order (JSON)</button><button class="b link" type="button" id="new">Start a new order</button></div>
<pre id="order-text">${esc(full)}</pre>`
    done.hidden = false
    $('copy').onclick = async () => {
      let ok = false
      try { await navigator.clipboard.writeText(full); ok = true } catch (er) {
        try { const r = document.createRange(); r.selectNodeContents($('order-text')); const s = getSelection(); s.removeAllRanges(); s.addRange(r); ok = document.execCommand('copy') } catch (er2) {}
      }
      $('copy').textContent = ok ? 'Copied' : 'Select the text below and copy it'; live(ok ? 'Order copied.' : 'Copy failed: select the order text and copy it.')
    }
    $('dl').onclick = () => {
      const a = document.createElement('a'), url = URL.createObjectURL(new Blob([JSON.stringify(o, null, 2)], { type: 'application/json' }))
      a.href = url; a.download = `${o.id}.json`; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000)
    }
    $('new').onclick = () => { cart = []; save(); renderCart(); done.hidden = true; $('checkout').reset(); live('Started a new order.'); $('catalogue').scrollIntoView(); }
    done.focus()
    live(`Order ${o.id} ready. Opening your email app.`)
    $('mail-again').click()   // the mailto opens the email app; the page stays put
  })
  $('checkout').addEventListener('input', e => { if (e.target.getAttribute('aria-invalid') === 'true') validate() })

  // ---- start -------------------------------------------------------------------------------------------------------
  ;(async () => {
    try {
      const r = await fetch(catalogueUrl(), { cache: 'no-cache' })
      if (!r.ok) throw new Error(r.status)
      CAT = await r.json()
      if (!Array.isArray(CAT.groups)) throw new Error('no groups')
    } catch (e) {
      $('catalogue').removeAttribute('aria-busy')
      $('cat-status').innerHTML = `The catalogue could not be loaded (data/offers.json). You can still write to <a href="mailto:${CONTACT}">${CONTACT}</a> with what you need.`
      return
    }
    for (const g of CAT.groups) for (const it of g.items || []) if (it && it.id) ITEMS.set(it.id, it)
    renderCatalogue()
    cart = load(); renderCart()
    const a = params.get('add')
    if (a) {
      if (ITEMS.has(a)) { add(a, defaults(ITEMS.get(a)), 1); const card = $('item-' + a); if (card) card.scrollIntoView({ block: 'center' }) }
      else live(`No item “${a}” in the catalogue.`)
      params.delete('add')
      try { history.replaceState(null, '', location.pathname + (params.toString() ? '?' + params : '') + location.hash) } catch (e) {}
    }
  })()
})()
