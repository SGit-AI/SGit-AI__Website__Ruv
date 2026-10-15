/* ruv.sgit.ai: live frames. Embeds the talk's live pages in an article, each with its own small controls.
   No dependencies. Apache-2.0.

   Markup (one per frame):
     <div class="live-frame" data-src="../talk/slides/claim/index.html" data-end="23" data-title="The claim"
          data-steps='[{"t":0,"label":"..."}]'></div>     (data-steps only for pages without window.RUV_STEPS)

   Each page is loaded when it nears the viewport, paused (?ruvpaused), set to play once (?once), in the reader's
   theme (?theme=, from window.RuvTheme). It is driven through its own virtual clock (assets/clock.js, same origin):
   iframe.contentWindow.RuvClock.pause() / play() / seek(t) / elapsed(). A step has two moments, its start and its
   end; the controls move between ends, a second before the next step starts (as the talk player does), so each stop
   shows a finished picture. Seeking backwards reloads the page paused and fast-forwards it, which is what the clock
   itself does with ?ruvt, but here we wait for the page's data to load first. A frame that scrolls away is paused. */
(function () {
  'use strict';
  var W = 1280, H = 720;   // every page is drawn at the talk player's slide size, then scaled to the column (960x540 on a phone, so it is less tiny)
  function base(box) { return box.clientWidth < 600 ? 960 : 1280; }

  var css = '' +
    '.live-frame{margin:22px 0 30px}' +
    '.live-frame .lf-box{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:var(--card)}' +
    '.live-frame iframe{position:absolute;left:0;top:0;width:' + W + 'px;height:' + H + 'px;border:0;transform-origin:0 0;background:transparent}' +
    '.live-frame .lf-wait{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:16px;color:var(--m);font-size:14px;background:var(--card)}' +
    '.live-frame .lf-wait.off{display:none}' +
    '.live-frame .lf-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:8px;font-size:13px;color:var(--m)}' +
    '.live-frame .lf-bar button{font:inherit;font-size:14px;line-height:1;min-width:36px;height:32px;padding:0 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:inherit;cursor:pointer}' +
    '.live-frame .lf-bar button:hover:not(:disabled){border-color:var(--t);color:var(--t)}' +
    '.live-frame .lf-bar button:disabled{opacity:.4;cursor:default}' +
    '.live-frame .lf-bar .lf-play{min-width:44px}' +
    '.live-frame .lf-label{flex:1 1 160px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
    '.live-frame .lf-label b{color:var(--t,inherit);font-weight:600}' +
    '.live-frame .lf-open{white-space:nowrap}' +
    '.live-frame .lf-track{flex:1 0 100%;height:3px;border-radius:2px;background:var(--line);overflow:hidden;order:9}' +
    '.live-frame .lf-track i{display:block;height:100%;width:0;background:var(--t)}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function theme() { try { return window.RuvTheme ? window.RuvTheme.current() : ''; } catch (e) { return ''; } }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(s) { s = Math.max(0, s); return Math.floor(s / 60) + ':' + ('0' + Math.floor(s % 60)).slice(-2); }

  var all = [];
  function Frame(host) {
    var f = this; all.push(f);
    f.host = host; f.src = host.getAttribute('data-src'); f.end = +host.getAttribute('data-end') || 30;
    f.title = host.getAttribute('data-title') || 'live page';
    try { f.manual = JSON.parse(host.getAttribute('data-steps') || 'null'); } catch (e) { f.manual = null; }
    f.loaded = false; f.ready = false; f.playing = false; f.pending = null; f.steps = null;
    var box = el('div', 'lf-box'); f.box = box;
    f.wait = el('div', 'lf-wait', 'The live page loads when it scrolls into view.');
    box.appendChild(f.wait);
    var bar = el('div', 'lf-bar');
    f.bPlay = el('button', 'lf-play', '▶'); f.bPlay.type = 'button'; f.bPlay.setAttribute('aria-label', 'play ' + f.title);
    f.bRestart = el('button', '', '↺'); f.bRestart.type = 'button'; f.bRestart.setAttribute('aria-label', 'restart ' + f.title); f.bRestart.title = 'restart from the beginning';
    f.bPrev = el('button', '', '‹'); f.bPrev.type = 'button'; f.bPrev.setAttribute('aria-label', 'previous step'); f.bPrev.title = 'previous step';
    f.bNext = el('button', '', '›'); f.bNext.type = 'button'; f.bNext.setAttribute('aria-label', 'next step'); f.bNext.title = 'next step (its end, fully drawn)';
    f.label = el('span', 'lf-label', 'not loaded yet');
    f.open = el('a', 'lf-open', 'open full size ↗'); f.open.href = f.src; f.open.target = '_blank'; f.open.rel = 'noopener';
    f.track = el('span', 'lf-track', '<i></i>');
    [f.bPlay, f.bRestart, f.bPrev, f.bNext, f.label, f.open, f.track].forEach(function (x) { bar.appendChild(x); });
    host.appendChild(box); host.appendChild(bar);
    f.bPlay.addEventListener('click', function () { f.toggle(); });
    f.bRestart.addEventListener('click', function () { f.reload(0, true); });
    f.bPrev.addEventListener('click', function () { f.step(-1); });
    f.bNext.addEventListener('click', function () { f.step(1); });
    f.fit();
    f.paint();
  }
  Frame.prototype.url = function () {
    return this.src + (this.src.indexOf('?') >= 0 ? '&' : '?') + 'once&ruvpaused' + (theme() ? '&theme=' + theme() : '');
  };
  Frame.prototype.fit = function () {
    if (!this.frame) return; var w = base(this.box);
    this.frame.style.width = w + 'px'; this.frame.style.height = (w * 9 / 16) + 'px'; this.frame.style.transform = 'scale(' + (this.box.clientWidth / w) + ')';
  };
  Frame.prototype.clock = function () { try { return this.ready && this.frame.contentWindow.RuvClock || null; } catch (e) { return null; } };
  Frame.prototype.elapsed = function () { var c = this.clock(); return c ? c.elapsed() : 0; };
  Frame.prototype.load = function () {
    var f = this; if (f.loaded) return; f.loaded = true;
    f.wait.textContent = 'Loading the live page…';
    f.frame = el('iframe'); f.frame.setAttribute('tabindex', '-1'); f.frame.setAttribute('title', f.title + ' (live page)');
    f.frame.setAttribute('loading', 'eager');
    f.frame.addEventListener('load', function () { f.onload(); });
    f.box.insertBefore(f.frame, f.wait); f.fit();
    f.pending = { t: null, play: false };   // null: the first step's end, once the steps are known
    f.frame.src = f.url();
  };
  // the page has loaded: wait until its steps (and its data) are in, then go where we were asked to go
  Frame.prototype.onload = function () {
    var f = this, t0 = Date.now(), w = f.frame.contentWindow;
    f.ready = false; f.paint();
    (function poll() {
      var has = false; try { has = Array.isArray(w.RUV_STEPS) && w.RUV_STEPS.length > 0; } catch (e) {}
      var waited = Date.now() - t0;
      if (!((has || f.manual) && waited >= 500) && waited < 3000) { setTimeout(poll, 100); return; }
      f.ready = true; f.steps = null;
      var c = f.clock(), p = f.pending || { t: null, play: false }; f.pending = null;
      if (!c) { f.wait.textContent = 'This page has no clock to drive; open it full size.'; return; }
      c.pause();
      var to = p.t == null ? f.firstStop() : p.t;
      if (to > 0.01) c.seek(to);
      if (p.play) f.play(); else f.playing = false;
      f.wait.classList.add('off'); f.paint();
    })();
  };
  // steps in page seconds: the page's own (window.RUV_STEPS), else the article's (data-steps), else one step
  Frame.prototype.stepsOf = function () {
    if (this.steps) return this.steps;
    var s = null, w;
    try { w = this.frame.contentWindow; if (Array.isArray(w.RUV_STEPS) && w.RUV_STEPS.length) s = w.RUV_STEPS; } catch (e) {}
    s = (s || this.manual || [{ t: 0, label: 'start' }]).map(function (x) { return { t: +x.t, label: x.label || '' }; })
      .filter(function (x) { return x.t >= 0; }).sort(function (a, b) { return a.t - b.t; });
    if (!s.length || s[0].t > 0.05) s.unshift({ t: 0, label: 'start' });
    var end = Math.max(this.end, s[s.length - 1].t + 0.5);
    s.forEach(function (x, i) {   // the end of a step: a second before the next one starts (before its part fades); the last, just before the page ends
      var nxt = i + 1 < s.length ? s[i + 1].t : end;
      x.end = Math.max(x.t, nxt - (i + 1 < s.length ? 1.0 : 0.25));
    });
    this.pageEnd = end;
    if (this.ready) this.steps = s;
    return s;
  };
  // the stops: the very start, then the end of every step
  Frame.prototype.stops = function () {
    var out = [0]; this.stepsOf().forEach(function (x) { if (x.end - x.t > 0.4 && x.end > 0.05) out.push(x.end); });
    return out;
  };
  Frame.prototype.firstStop = function () { var s = this.stops(); return s.length > 1 ? s[1] : 0; };
  Frame.prototype.stepAt = function (t) {
    var s = this.stepsOf(), ix = 0; s.forEach(function (x, i) { if (t >= x.t - 0.05) ix = i; }); return ix;
  };
  Frame.prototype.seek = function (t) {   // forwards: fast-forward; backwards: reload, then fast-forward
    var c = this.clock(); if (!c) return;
    if (t + 0.05 < c.elapsed()) { this.reload(t, false); return; }
    c.seek(t); this.paint();
  };
  Frame.prototype.reload = function (t, play) {
    var f = this; if (!f.loaded) { f.load(); f.pending = { t: t, play: play }; return; }
    f.ready = false; f.playing = false; f.pending = { t: t, play: play };
    f.wait.textContent = 'Loading…'; f.wait.classList.remove('off');
    try { f.frame.contentWindow.location.replace(f.url()); } catch (e) { f.frame.src = f.url(); }
    f.paint();
  };
  Frame.prototype.step = function (dir) {
    var c = this.clock(); if (!c) return;
    var now = c.elapsed(), s = this.stops(), to = null, i;
    this.pause();
    if (dir > 0) { for (i = 0; i < s.length; i++) if (s[i] > now + 0.05) { to = s[i]; break; } }
    else { for (i = s.length - 1; i >= 0; i--) if (s[i] < now - 0.15) { to = s[i]; break; } }
    if (to != null) this.seek(to);
    this.paint();
  };
  Frame.prototype.play = function () {
    var c = this.clock(); if (!c) return;
    this.stepsOf();
    if (c.elapsed() >= this.pageEnd - 0.3) { this.reload(0, true); return; }   // at the end: play again from the start
    pauseOthers(this); c.play(); this.playing = true; this.paint();
  };
  Frame.prototype.pause = function () { var c = this.clock(); if (c) c.pause(); this.playing = false; this.paint(); };
  Frame.prototype.toggle = function () { if (!this.loaded) { this.load(); this.pending = { t: 0, play: true }; return; } if (this.playing) this.pause(); else this.play(); };
  Frame.prototype.tick = function () {
    var c = this.clock(); if (!c) return;
    if (this.playing && c.elapsed() >= (this.pageEnd || this.end)) { c.pause(); this.playing = false; }
    this.paint();
  };
  Frame.prototype.paint = function () {
    var f = this, c = f.clock();
    f.bPlay.textContent = f.playing ? '❚❚' : '▶';
    f.bPlay.setAttribute('aria-label', (f.playing ? 'pause ' : 'play ') + f.title);
    [f.bRestart, f.bPrev, f.bNext].forEach(function (b) { b.disabled = !c; });
    if (!c) { f.label.textContent = f.loaded ? 'loading…' : 'not loaded yet'; return; }
    var t = c.elapsed(), s = f.stepsOf(), i = f.stepAt(t), stops = f.stops(), end = f.pageEnd || f.end;
    f.bPrev.disabled = !(t > 0.15);
    f.bNext.disabled = !stops.some(function (x) { return x > t + 0.05; });
    f.label.innerHTML = 'step <b>' + (i + 1) + '/' + s.length + '</b> · ' + esc(s[i].label) + ' · ' + fmt(t) + ' of ' + fmt(end);
    f.track.firstChild.style.width = Math.min(100, 100 * t / end).toFixed(1) + '%';
  };
  function pauseOthers(me) { all.forEach(function (f) { if (f !== me && f.playing) f.pause(); }); }

  function init() {
    var hosts = [].slice.call(document.querySelectorAll('.live-frame'));
    hosts.forEach(function (h) { h._lf = new Frame(h); });
    if ('IntersectionObserver' in window) {
      var near = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target._lf.load(); near.unobserve(e.target); } }); }, { rootMargin: '400px 0px' });
      var seen = new IntersectionObserver(function (es) { es.forEach(function (e) { var f = e.target._lf; if (!e.isIntersecting && f.playing) f.pause(); }); }, { threshold: 0 });
      hosts.forEach(function (h) { near.observe(h); seen.observe(h); });
    } else hosts.forEach(function (h) { h._lf.load(); });
    window.addEventListener('resize', function () { all.forEach(function (f) { f.fit(); }); });
    if ('ResizeObserver' in window) { var ro = new ResizeObserver(function () { all.forEach(function (f) { f.fit(); }); }); hosts.forEach(function (h) { ro.observe(h); }); }
    window.addEventListener('ruv-theme', function (e) {   // the live page wears the article's theme
      all.forEach(function (f) { try { if (f.frame) f.frame.contentDocument.documentElement.setAttribute('data-theme', e.detail); } catch (x) {} });
    });
    setInterval(function () { all.forEach(function (f) { if (f.ready) f.tick(); }); }, 200);
    window.LiveFrames = all;
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
