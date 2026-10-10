const CACHE = 'prapatti-v3';
const SHELL = [
  '/',
  '/stotras/',
  '/resources/',
  '/forum/',
  '/css/main.css',
  '/js/font-size.js',
  '/js/stotra-search.js',
  '/images/Thiruvadis_bg.png',
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

  // Network first, so new stotras and updates show on the first visit;
  // the saved copy is only used when offline
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request))
  );
});
