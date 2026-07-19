// Service Worker for 考研助手 PWA
var CACHE_NAME = 'kaoyan-v1';
var ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/api.js',
  '/js/app.js',
  '/js/pages/dashboard.js',
  '/js/pages/plan.js',
  '/js/pages/english.js',
  '/js/pages/resources.js',
  '/js/pages/schools.js',
  '/js/pages/settings.js',
  '/manifest.json',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.js',
  'https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.css'
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('fetch', function(e) {
  // Don't cache API calls
  if (e.request.url.indexOf('/api/') >= 0) return;
  e.respondWith(
    caches.match(e.request).then(function(resp) {
      return resp || fetch(e.request);
    })
  );
});
