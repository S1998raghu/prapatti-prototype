const CACHE = 'prapatti-v1';
const SHELL = [
  '/',
  '/stotras/',
  '/resources/',
  '/forum/',
  '/css/main.css',
  '/js/search.js',
  '/index.json',
  '/images/Thiruvadis.png',
  '/images/ramanujar.png',
  '/images/SwamiDesikar.png',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // Only cache same-origin GET requests — never R2/worker PDFs
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      const network = fetch(e.request).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
        return res;
      });
      return cached || network;
    })
  );
});
