const CACHE_NAME = 'globalscore-v2';

self.addEventListener('install', e => {
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
      './assets/img/logo.svg'
    ]))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request)
    .then(res => res || fetch(e.request))
  );
});
