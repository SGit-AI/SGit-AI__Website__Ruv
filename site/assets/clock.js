// ruv.sgit.ai: a virtual clock for animated pages, so the talk player can pause, speed up, step and seek them.
// Load it FIRST in an animation page (before any other script). It replaces performance.now, Date.now,
// requestAnimationFrame, setTimeout and setInterval with versions driven by one virtual clock, and keeps
// CSS animations, Web Animations and <video> in step with it. A page that times itself with those APIs
// needs no other change. Apache-2.0.
//
//   RuvClock.pause() / play() / setRate(r) / seek(seconds since the page started) / elapsed() / paused
//   ?ruvt=12.5  start the page already 12.5 s in (the player uses this to step backwards: reload, then fast-forward)
//   ?ruvpaused  start paused
//   window.RUV_STEPS = [{ t: 0, label: '...' }, ...]   optional: the page's own steps, in seconds; the player shows them
//   postMessage({ ruvClock: 'pause' | 'play' | 'rate' | 'seek', rate, t }) from a parent window does the same
(function () {
  if (window.RuvClock) return
  const P = performance.now.bind(performance), D0 = Date.now() - P()
  const rRAF = window.requestAnimationFrame.bind(window), rSetI = window.setInterval.bind(window)
  const q = new URLSearchParams(location.search)
  let rate = 1, paused = q.has('ruvpaused'), vBase = 0, rAnchor = P(), seq = 1, dirty = true
  const vnow = () => paused ? vBase : vBase + (P() - rAnchor) * rate
  const rebase = () => { vBase = vnow(); rAnchor = P() }
  const timers = new Map(), rafs = new Map()
  // ?ruvledger=NAME: read the ledger snapshot data/vaults-NAME.json instead of data/vaults.json, so a narrated deck shows the
  // numbers its narration describes (talk/narration.html pins ?ruvledger=narrated)
  const LEDGER = q.get('ruvledger')
  if (LEDGER && /^[\w-]+$/.test(LEDGER)) { const f0 = window.fetch.bind(window); window.fetch = (u, o) => f0(typeof u === 'string' ? u.replace(/(^|\/)data\/vaults\.json(?=$|\?)/, `$1data/vaults-${LEDGER}.json`) : u, o) }

  try { Object.defineProperty(performance, 'now', { value: vnow, configurable: true, writable: true }) } catch { performance.now = vnow }
  Date.now = () => Math.round(D0 + vnow())
  window.setTimeout = (fn, ms, ...a) => { const id = seq++; timers.set(id, { fn, a, due: vnow() + (+ms || 0), every: 0 }); return id }
  window.setInterval = (fn, ms, ...a) => { const id = seq++, every = Math.max(+ms || 0, 4); timers.set(id, { fn, a, due: vnow() + every, every }); return id }
  window.clearTimeout = window.clearInterval = id => { timers.delete(id) }
  window.requestAnimationFrame = cb => { const id = seq++; rafs.set(id, cb); return id }
  window.cancelAnimationFrame = id => { rafs.delete(id) }

  function flush() {   // run every timer that is due, earliest first (timers set while flushing run too, if due)
    for (let guard = 0; guard < 20000; guard++) {
      const v = vnow(); let best = null, bid = 0
      for (const [id, t] of timers) if (t.due <= v && (!best || t.due < best.due)) { best = t; bid = id }
      if (!best) return
      if (best.every) best.due += best.every; else timers.delete(bid)
      try { typeof best.fn === 'function' ? best.fn(...best.a) : (0, eval)(String(best.fn)) } catch (e) { console.error(e) }
    }
  }
  function frame() {
    const cbs = [...rafs.values()]; rafs.clear(); const v = vnow()
    for (const cb of cbs) try { cb(v) } catch (e) { console.error(e) }
  }
  const mine = new WeakSet()
  function syncMedia() {
    if (document.getAnimations) for (const a of document.getAnimations()) {
      try {
        if (a.playbackRate !== rate) a.playbackRate = rate
        if (paused && a.playState === 'running') { a.pause(); mine.add(a) }
        else if (!paused && a.playState === 'paused' && mine.has(a)) { a.play(); mine.delete(a) }
      } catch {}
    }
    for (const m of document.querySelectorAll('video,audio')) {
      if (m.playbackRate !== rate) m.playbackRate = rate
      if (paused && !m.paused) { m.pause(); m.dataset.ruvPaused = 1 } else if (!paused && m.paused && m.dataset.ruvPaused) { delete m.dataset.ruvPaused; m.play().catch(() => {}) }
    }
  }
  // the real loop: timers every 4 ms, frames on the real animation frame (held while paused, so a paused page stands still)
  rSetI(flush, 4)
  ;(function loop() { flush(); if (!paused || dirty) { frame(); dirty = false } syncMedia(); rRAF(loop) })()

  function advance(dt) {   // fast-forward dt seconds in 100 ms frames, so frame-by-frame animations get there too
    const wasPaused = paused; if (!paused) rebase(); paused = true
    let left = dt * 1000
    while (left > 0) { const s = Math.min(100, left); vBase += s; left -= s; flush(); frame() }
    if (document.getAnimations) for (const a of document.getAnimations()) {
      try {
        const tm = a.effect?.getComputedTiming?.()
        if (a.constructor.name === 'CSSTransition') a.finish()
        else if (tm && tm.endTime !== Infinity && a.playState !== 'finished') a.currentTime = Math.min((a.currentTime || 0) + dt * 1000, tm.endTime)
      } catch {}
    }
    rAnchor = P(); paused = wasPaused; dirty = true
  }
  const elapsed = () => vnow() / 1000
  function seek(t) {
    t = Math.max(0, +t || 0)
    if (t + 0.05 < elapsed()) {   // backwards: reload at that time
      const u = new URL(location.href); u.searchParams.set('ruvt', t.toFixed(2)); if (paused) u.searchParams.set('ruvpaused', ''); else u.searchParams.delete('ruvpaused')
      location.replace(u.href); return
    }
    advance(t - elapsed())
  }
  window.RuvClock = {
    get paused() { return paused }, get rate() { return rate }, elapsed, seek,
    pause() { if (!paused) { rebase(); paused = true } },
    play() { if (paused) { rAnchor = P(); paused = false } },
    setRate(r) { rebase(); rate = Math.max(0.1, +r || 1) },
  }
  addEventListener('message', e => {
    const m = e.data; if (!m || !m.ruvClock) return
    const C = window.RuvClock
    if (m.ruvClock === 'pause') C.pause(); else if (m.ruvClock === 'play') C.play()
    else if (m.ruvClock === 'rate') C.setRate(m.rate); else if (m.ruvClock === 'seek') C.seek(m.t)
  })
  if (q.has('ruvt')) { const t0 = +q.get('ruvt'); const go = () => advance(Math.max(0, t0 - elapsed())); document.readyState === 'complete' ? go() : addEventListener('load', go) }
})()
// a looping page plays once and holds when the player asks (?once): ruvLoop(t, loop, hold)
window.ruvLoop = (function () { const once = new URLSearchParams(location.search).has('once'); return (t, loop, hold) => once ? Math.min(t, hold == null ? loop - 0.01 : hold) : t % loop })()
