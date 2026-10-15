// ruv.sgit.ai: Wardley maps from data/maps.json, drawn as inline SVG. No dependencies.
//   RuvMaps.render(el, 'runs', { data: '../data/maps.json', reading: true })   one map into el
//   RuvMaps.renderAll('[data-map]')                                             every element with data-map="<id>"
// Every colour is a theme token from assets/themes.css (set through style="", since var() does not work in SVG
// presentation attributes), so a map follows all five themes. Groups differ by shape as well as colour, so two
// tokens that look alike in one theme still read apart. The SVG is laid out at the element's own width (not scaled
// down), so labels stay readable on a phone; it is redrawn when the width changes.
(() => {
  const SRC = document.currentScript && document.currentScript.src;
  const DEFAULT_DATA = SRC ? new URL('../data/maps.json', SRC).href : 'data/maps.json';
  const cache = {};
  const load = url => (cache[url] ||= fetch(url).then(r => { if (!r.ok) throw new Error(`${url}: ${r.status}`); return r.json(); }));
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let uid = 0;

  const GROUP = {
    ours:   { tok: '--accent', shape: 'circle' },
    rUv:    { tok: '--warm',   shape: 'diamond' },
    cloud:  { tok: '--dim',    shape: 'square' },
    model:  { tok: '--yellow', shape: 'triangle' },
    people: { tok: '--red',    shape: 'ring' },
  };
  const STAGES = [['Genesis', 0, .17], ['Custom', .17, .4], ['Product', .4, .7], ['Commodity', .7, 1]];

  function shape(kind, x, y, r, tok, extra = '') {
    const f = `fill:var(${tok});stroke:var(--panel);stroke-width:1.5${extra}`;
    if (kind === 'diamond') return `<path d="M${x} ${y - r * 1.25}L${x + r * 1.25} ${y}L${x} ${y + r * 1.25}L${x - r * 1.25} ${y}Z" style="${f}"/>`;
    if (kind === 'square') return `<rect x="${x - r}" y="${y - r}" width="${2 * r}" height="${2 * r}" rx="1.5" style="${f}"/>`;
    if (kind === 'triangle') return `<path d="M${x} ${y - r * 1.3}L${x + r * 1.2} ${y + r * .85}L${x - r * 1.2} ${y + r * .85}Z" style="${f}"/>`;
    if (kind === 'ring') return `<circle cx="${x}" cy="${y}" r="${r - 1}" style="fill:var(--panel);stroke:var(${tok});stroke-width:2.6${extra}"/>`;
    return `<circle cx="${x}" cy="${y}" r="${r}" style="${f}"/>`;
  }

  function wrap(text, max) {
    const out = []; let line = '';
    for (const w of String(text).split(/\s+/)) {
      if (line && (line + ' ' + w).length > max) { out.push(line); line = w; } else line = line ? line + ' ' + w : w;
    }
    if (line) out.push(line);
    return out;
  }

  // overlap helpers for the label placer
  const area = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  function segIn(box, s) {   // how much of segment s runs through box, in px (sampled)
    const n = 16; let k = 0;
    const len = Math.hypot(s[2] - s[0], s[3] - s[1]);
    for (let i = 0; i <= n; i++) {
      const x = s[0] + (s[2] - s[0]) * i / n, y = s[1] + (s[3] - s[1]) * i / n;
      if (x > box.x && x < box.x + box.w && y > box.y && y < box.y + box.h) k++;
    }
    return k / (n + 1) * len;
  }

  function draw(el, data, id, opts) {
    const m = data.maps && data.maps[id];
    if (!m) { el.textContent = `No map "${id}" in the data.`; return; }
    const n = ++uid;
    const W = Math.max(300, Math.round(el.clientWidth || el.getBoundingClientRect().width || 800));
    const narrow = W < 620;
    const fs = narrow ? 11 : 12.5, lh = fs * 1.18;
    const ctx = document.createElement('canvas').getContext('2d'), fam = getComputedStyle(el).fontFamily || 'sans-serif';
    const tw = (s, size, weight = 500, style = '') => { ctx.font = `${style} ${weight} ${size}px ${fam}`; return ctx.measureText(s).width; };
    const maxCh = narrow ? 15 : 24;
    const L = narrow ? 24 : 34, R = 10, T = 10;
    const PW = W - L - R, PH = Math.round(narrow ? W * 1.75 : Math.min(W * .58, 640));
    const pad = narrow ? 16 : 20;
    const px = x => L + 6 + x * (PW - 12), py = y => T + pad + (1 - y) * (PH - 2 * pad);
    const byId = {};
    const dotR = narrow ? 5.5 : 6.5;

    // nodes: the user anchor plus the components
    const nodes = [{ id: 'user', anchor: true, label: m.user, sub: m.need, x: m.user_x ?? .4, y: 1, group: null }]
      .concat(m.components.map(c => ({ ...c })));
    nodes.forEach(c => { c.cx = px(c.x); c.cy = c.anchor ? T + pad - 2 : py(c.y); byId[c.id] = c; });

    // segments: links and movements (obstacles for labels)
    const links = (m.links || []).map(([a, b]) => byId[a] && byId[b] && [byId[a].cx, byId[a].cy, byId[b].cx, byId[b].cy]).filter(Boolean);
    const moves = (m.movements || []).filter(v => byId[v.id]).map(v => {
      const c = byId[v.id], tx = px(v.to_x), dir = Math.sign(tx - c.cx) || 1;
      return { ...v, c, x1: c.cx + dir * (dotR + 3), x2: tx, y: c.cy, dir };
    });
    const segs = links.concat(moves.map(v => [v.x1, v.y, v.x2, v.y]));
    const dots = nodes.map(c => ({ x: c.cx - dotR - 2, y: c.cy - dotR - 2, w: 2 * dotR + 4, h: 2 * dotR + 4 }))
      .concat(moves.map(v => ({ x: v.x2 - dotR, y: v.y - dotR, w: 2 * dotR, h: 2 * dotR })));
    const plot = { x: L, y: T, w: PW, h: PH };

    // labels: each node's box, then candidate positions scored against everything else
    const labs = nodes.map(c => {
      const lines = wrap(c.label, c.anchor ? maxCh + 6 : maxCh), sub = c.sub ? wrap(c.sub, maxCh + 8) : [];
      const w = Math.max(...lines.map(s => tw(s, c.anchor ? fs + .5 : fs, c.anchor ? 700 : 500)), ...sub.map(s => tw(s, fs - 1.5, 400))) + 3;
      return { c, lines, sub, w, h: lines.length * lh + sub.length * lh * .92 };
    });
    const mlabs = moves.map(v => {
      const lines = wrap(v.label, maxCh + 4), w = Math.max(...lines.map(s => tw(s, fs - 1.5, 400, 'italic'))) + 3;
      return { v, lines, w, h: lines.length * lh * .9, move: true };
    });
    function cands(l) {
      const g = dotR + 4;
      if (l.move) {   // above or below the arrow, at its middle or near its head
        const { x1, x2, y } = l.v, out = [];
        for (const f of [.5, .75, .25, .95]) {
          const mx = x1 + (x2 - x1) * f;
          out.push({ x: mx - l.w / 2, y: y - 4 - l.h, p: f === .5 ? 0 : 6 }, { x: mx - l.w / 2, y: y + 4, p: f === .5 ? 4 : 10 });
        }
        return out;
      }
      const { cx, cy } = l.c, w = l.w, h = l.h;
      return [
        { x: cx + g, y: cy - h / 2, p: 0 }, { x: cx - g - w, y: cy - h / 2, p: 8 },
        { x: cx - w / 2, y: cy - g - h, p: 14 }, { x: cx - w / 2, y: cy + g, p: 14 },
        { x: cx + g - 3, y: cy - g - h + 4, p: 18 }, { x: cx + g - 3, y: cy + g - 4, p: 18 },
        { x: cx - g - w + 3, y: cy - g - h + 4, p: 22 }, { x: cx - g - w + 3, y: cy + g - 4, p: 22 },
        { x: cx + g, y: cy - lh * .6, p: 26 }, { x: cx + g, y: cy - h + lh * .6, p: 26 },
      ];
    }
    const all = labs.concat(mlabs);
    function score(l, b) {
      const box = { x: b.x, y: b.y, w: l.w, h: l.h };
      let s = b.p;
      const inside = area(box, plot); s += (box.w * box.h - inside) * 40;
      for (const o of all) if (o !== l && o.box) s += area(box, o.box) * 12;
      for (const d of dots) s += area(box, d) * 14;
      for (const sg of segs) s += segIn(box, sg) * (l.move ? 2 : 3.5);
      return s;
    }
    for (let pass = 0; pass < 4; pass++) for (const l of all) {
      let best = null, bs = Infinity;
      for (const b of cands(l)) { const s = score(l, b); if (s < bs) { bs = s; best = b; } }
      l.box = { x: best.x, y: best.y, w: l.w, h: l.h };
    }

    // stages and axes
    const sb = T + PH;
    let svg = '';
    svg += `<rect x="0.5" y="0.5" width="${W - 1}" height="__H__" rx="10" style="fill:var(--panel);stroke:var(--line)"/>`;
    STAGES.forEach(([name, a, b], i) => {
      const x0 = i ? px(a) : L, x1 = i === 3 ? L + PW : px(b);
      if (i % 2) svg += `<rect x="${x0}" y="${T}" width="${x1 - x0}" height="${PH}" style="fill:var(--panel2);opacity:.6"/>`;
      if (i) svg += `<line x1="${x0}" y1="${T}" x2="${x0}" y2="${sb}" style="stroke:var(--line2);stroke-dasharray:3 4"/>`;
      svg += `<text x="${(x0 + x1) / 2}" y="${sb + fs + 6}" text-anchor="middle" style="fill:var(--dim);font-size:${fs - .5}px;font-weight:600">${name}</text>`;
    });
    svg += `<line x1="${L}" y1="${sb}" x2="${L + PW}" y2="${sb}" style="stroke:var(--line2)"/>`;
    svg += `<text x="${L + PW}" y="${sb + 2 * fs + 10}" text-anchor="end" style="fill:var(--dim2);font-size:${fs - 1.5}px">evolution →</text>`;
    svg += `<line x1="${L}" y1="${sb}" x2="${L}" y2="${T + 4}" style="stroke:var(--line2)" marker-end="url(#ax${n})"/>`;
    const yl = (t, y, anchor) => `<text transform="translate(${L - 8} ${y}) rotate(-90)" text-anchor="${anchor}" style="fill:var(--dim2);font-size:${fs - 1.5}px">${t}</text>`;
    svg += yl('visible ↑', T + 6, 'end') + yl('invisible', sb - 4, 'start');

    // links, movements, nodes
    svg += links.map(s => `<line x1="${s[0]}" y1="${s[1]}" x2="${s[2]}" y2="${s[3]}" style="stroke:var(--line2);stroke-width:1.2"/>`).join('');
    for (const v of moves) {
      const g = GROUP[v.c.group] || GROUP.ours;
      svg += `<line x1="${v.x1}" y1="${v.y}" x2="${v.x2 - v.dir * (dotR + 3)}" y2="${v.y}" style="stroke:var(--red);stroke-width:1.6;stroke-dasharray:5 4" marker-end="url(#mv${n})"/>`;
      svg += `<circle cx="${v.x2}" cy="${v.y}" r="${dotR - .5}" style="fill:none;stroke:var(${g.tok});stroke-width:1.3;stroke-dasharray:2.5 2"/>`;
    }
    for (const c of nodes) {
      const title = `<title>${esc(c.anchor ? `${c.label}: needs ${c.sub}` : `${c.label}. ${c.note || ''}`)}</title>`;
      if (c.anchor) svg += `<g>${title}<circle cx="${c.cx}" cy="${c.cy}" r="${dotR + 1}" style="fill:var(--head);stroke:var(--panel);stroke-width:2"/></g>`;
      else { const g = GROUP[c.group] || GROUP.ours; svg += `<g>${title}${shape(g.shape, c.cx, c.cy, dotR, g.tok)}</g>`; }
    }
    // labels on a halo so a crossing line never cuts the text
    const halo = 'paint-order:stroke;stroke:var(--panel);stroke-width:3.5px;stroke-linejoin:round';
    for (const l of labs) {
      const { box, c } = l, right = box.x >= c.cx - 1, left = box.x + box.w <= c.cx + 1;
      const anchor = right ? 'start' : left ? 'end' : 'middle', tx = right ? box.x : left ? box.x + box.w : box.x + box.w / 2;
      let y = box.y + fs * .95, t = '';
      for (const s of l.lines) { t += `<tspan x="${tx}" y="${y}">${esc(s)}</tspan>`; y += lh; }
      for (const s of l.sub) { t += `<tspan x="${tx}" y="${y - lh * .06}" style="fill:var(--dim);font-weight:400;font-size:${fs - 1.5}px">${esc(s)}</tspan>`; y += lh * .92; }
      svg += `<text text-anchor="${anchor}" style="fill:var(${c.anchor ? '--head' : '--fg'});font-size:${c.anchor ? fs + .5 : fs}px;font-weight:${c.anchor ? 700 : 500};${halo}">${t}</text>`;
    }
    for (const l of mlabs) {
      let y = l.box.y + fs * .85, t = '';
      for (const s of l.lines) { t += `<tspan x="${l.box.x + l.box.w / 2}" y="${y}">${esc(s)}</tspan>`; y += lh * .9; }
      svg += `<text text-anchor="middle" style="fill:var(--red);font-size:${fs - 1.5}px;font-style:italic;${halo}">${t}</text>`;
    }

    // legend, wrapped to the width
    const items = Object.keys(GROUP).filter(k => m.components.some(c => c.group === k))
      .map(k => ({ k, text: (data.groups && data.groups[k]) || k }));
    items.push({ k: 'move', text: 'movement: where it is going' });
    let lx = L, ly = sb + 2 * fs + 30;
    const lfs = fs - 1;
    for (const it of items) {
      const w = 22 + tw(it.text, lfs, 400) + 16;
      if (lx + w > W - R && lx > L) { lx = L; ly += lfs + 10; }
      const icon = it.k === 'move'
        ? `<line x1="${lx}" y1="${ly - lfs * .35}" x2="${lx + 14}" y2="${ly - lfs * .35}" style="stroke:var(--red);stroke-width:1.6;stroke-dasharray:4 3" marker-end="url(#mv${n})"/>`
        : shape(GROUP[it.k].shape, lx + 6, ly - lfs * .35, 5, GROUP[it.k].tok);
      svg += `${icon}<text x="${lx + 20}" y="${ly}" style="fill:var(--dim);font-size:${lfs}px">${esc(it.text)}</text>`;
      lx += w;
    }
    const H = Math.round(ly + 14);
    svg = svg.replace('__H__', H - 1);

    const order = m.components.slice().sort((a, b) => a.x - b.x).map(c => `${c.label} (${STAGES.find(s => c.x < s[2] || s[2] === 1)[0].toLowerCase()})`);
    const desc = `${m.user} needs ${m.need}. Components from genesis to commodity: ${order.join('; ')}. `
      + (moves.length ? `Movements: ${moves.map(v => `${v.c.label}, ${v.label}`).join('; ')}. ` : '') + (m.reading || '');
    const defs = `<defs><marker id="mv${n}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" style="fill:var(--red)"/></marker>`
      + `<marker id="ax${n}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--line2)"/></marker></defs>`;
    el.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="mt${n} md${n}" style="display:block;width:100%;height:auto;max-width:100%;font-family:inherit">`
      + `<title id="mt${n}">${esc(`Wardley map: ${m.title}`)}</title><desc id="md${n}">${esc(desc)}</desc>${defs}${svg}</svg>`
      + (opts.reading && m.reading ? `<p class="map-reading" style="color:var(--text);margin:.6em 0 0">${esc(m.reading)}</p>` : '');
    el.dataset.mapWidth = W;
  }

  function render(el, mapId, opts = {}) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return Promise.resolve();
    const url = opts.data ? new URL(opts.data, location.href).href : DEFAULT_DATA;
    return load(url).then(data => {
      draw(el, data, mapId, opts);
      if (!el._ruvMapRO && 'ResizeObserver' in window) {   // relayout at the new width, not a scaled picture
        let t;
        el._ruvMapRO = new ResizeObserver(() => {
          clearTimeout(t);
          t = setTimeout(() => { if (Math.abs((el.clientWidth || 0) - (+el.dataset.mapWidth || 0)) > 8) draw(el, data, mapId, opts); }, 120);
        });
        el._ruvMapRO.observe(el);
      }
    }).catch(e => { el.textContent = `The map could not be loaded (${e.message}).`; });
  }

  function renderAll(selector = '[data-map]', opts = {}) {
    return Promise.all([...document.querySelectorAll(selector)].map(el =>
      render(el, el.dataset.map, { ...opts, data: el.dataset.mapData || opts.data, reading: 'mapReading' in el.dataset || opts.reading })));
  }

  window.RuvMaps = { render, renderAll };
})();
