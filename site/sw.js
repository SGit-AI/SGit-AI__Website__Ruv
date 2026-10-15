// ruv.sgit.ai: keep every file the talk has used on this machine, so the talk loads instantly and works with bad wifi.
// Stale-while-revalidate for same-origin GETs: answer from the cache at once, refresh the cache from the network behind it
// (a change on the site shows on the next load). Query strings are ignored for the cache key (the site is static).
// Registered by talk/player.html. Apache-2.0.
const CACHE = 'ruv-sgit-talk-v1'
self.addEventListener('install', () => self.skipWaiting())
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()))
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url)
  if (r.method !== 'GET' || u.origin !== location.origin || r.headers.has('range')) return
  const key = u.origin + u.pathname
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(key)
    const net = fetch(r).then(res => { if (res.ok && res.type === 'basic') c.put(key, res.clone()); return res })
    if (hit) { e.waitUntil(net.catch(() => {})); return hit }
    return net
  }))
})
