const CACHE_NAME = 'globalscore-v1';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
    .then(cache => cache.addAll([
      '/',
      '/en/',
      '/ar/',
      '/assets/css/main.css',
      '/assets/js/app.js',
      '/assets/js/data-source.js',
      '/assets/data/live.json'
    ]))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request)
    .then(res => res || fetch(e.request))
  );
});
