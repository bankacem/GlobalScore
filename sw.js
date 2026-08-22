const CACHE_NAME = 'globalscore-v3';

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME)
    .then(cache => cache.addAll([
      './',
      './en/',
      './ar/',
      './assets/css/main.css',
      './assets/css/critical.css',
      './assets/js/app.js',
      './assets/js/data-source.js',
      './assets/js/components.js',
      './assets/js/utils.js',
      './assets/data/live.json',
      './assets/data/content.json',
      './ar/articles/arsenal-chelsea-match-report.html',
      './ar/articles/real-madrid-barcelona-tactical-notes.html',
      './ar/articles/player-watch-odegaard.html',
      './en/articles/arsenal-chelsea-match-report.html',
      './en/articles/real-madrid-barcelona-tactical-notes.html',
      './en/articles/player-watch-odegaard.html',
      './Sitemap.xml',
      './assets/img/logo.svg'
    ]))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', e => {
  const requestUrl = new URL(e.request.url);
  const isDynamicAsset = requestUrl.pathname.endsWith('.js') || requestUrl.pathname.endsWith('.json');
  if (isDynamicAsset) {
    e.respondWith(fetch(e.request).then(response => {
      const copy = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(e.request, copy));
      return response;
    }).catch(() => caches.match(e.request)));
    return;
  }
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});
