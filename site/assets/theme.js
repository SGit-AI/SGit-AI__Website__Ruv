/* ruv.sgit.ai: the theme, chosen and remembered. A classic script in <head>, before first paint (the newsroom's
   themes.js does the same, for the same reason). The stored value is checked against THEMES before it reaches the
   DOM. Nothing stored: the system preference picks Night or Newsprint. The same key is read by the site, the talk
   player and the live app (one origin), so they change together; other open windows follow via the storage event. */
(function () {
  'use strict';
  var KEY = 'ruv.theme';
  var THEMES = { newsprint: ['Newsprint', 'Warm off-white, teal'], night: ['Night', 'Dark, teal'], paper: ['Paper', 'Warm cream, terracotta'],
                 blueprint: ['Blueprint', 'White, electric blue'], ember: ['Ember', 'Dark, amber'] };
  var has = function (k) { return Object.prototype.hasOwnProperty.call(THEMES, k); };
  function stored() { try { var v = localStorage.getItem(KEY); if (has(v)) return v; var old = localStorage.getItem('theme'); return old === 'dark' ? 'night' : old === 'light' ? 'newsprint' : null; } catch (e) { return null; } }
  function system() { try { return matchMedia('(prefers-color-scheme: dark)').matches ? 'night' : 'newsprint'; } catch (e) { return 'newsprint'; } }
  var q = null; try { q = new URLSearchParams(location.search).get('theme'); } catch (e) {}
  function current() { return has(q) ? q : (stored() || system()); }
  function apply(n) { document.documentElement.setAttribute('data-theme', n); return n; }
  function set(n) { if (!has(n)) return current(); q = null; try { localStorage.setItem(KEY, n); } catch (e) {} apply(n); window.dispatchEvent(new CustomEvent('ruv-theme', { detail: n })); return n; }
  apply(current());
  window.addEventListener('storage', function (e) { if (e.key === KEY && has(e.newValue)) { apply(e.newValue); window.dispatchEvent(new CustomEvent('ruv-theme', { detail: e.newValue })); } });
  window.RuvTheme = {
    THEMES: THEMES, current: current, set: set,
    isDark: function () { var n = current(); return n === 'night' || n === 'ember'; },
    picker: function (host) {   // draws the picker into host (a button replaced by it)
      var wrap = document.createElement('div'); wrap.className = 'theme-pick';
      var b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-haspopup', 'true'); b.setAttribute('aria-expanded', 'false');
      var ul = document.createElement('ul'); ul.hidden = true;
      function label() { var n = current(); b.innerHTML = '<span class="sw sw-' + n + '"></span><span class="name">' + THEMES[n][0] + '</span><span class="caret">▾</span>'; b.title = 'Theme: ' + THEMES[n][0]; }
      Object.keys(THEMES).forEach(function (k) {
        var li = document.createElement('li'), x = document.createElement('button'); x.type = 'button';
        x.innerHTML = '<span class="sw sw-' + k + '"></span><span>' + THEMES[k][0] + '<span class="n">' + THEMES[k][1] + '</span></span>';
        x.addEventListener('click', function (e) { e.stopPropagation(); set(k); ul.hidden = true; b.setAttribute('aria-expanded', 'false'); });
        li.appendChild(x); ul.appendChild(li);
      });
      function mark() { label(); [].forEach.call(ul.querySelectorAll('li button'), function (x, i) { x.setAttribute('aria-current', Object.keys(THEMES)[i] === current() ? 'true' : 'false'); }); }
      b.addEventListener('click', function (e) { e.stopPropagation(); ul.hidden = !ul.hidden; b.setAttribute('aria-expanded', String(!ul.hidden)); });
      document.addEventListener('click', function () { ul.hidden = true; b.setAttribute('aria-expanded', 'false'); });
      window.addEventListener('ruv-theme', mark);
      wrap.appendChild(b); wrap.appendChild(ul); mark(); host.replaceWith(wrap); return wrap;
    }
  };
})();
