const CACHE_NAME = 'swmm-search-v1';
const OFFLINE_DOCS_KEY = 'swmm-offline-docs';

const APP_SHELL = [
  '/',
  '/static/app.js?v=8',
  '/static/manifest.json',
  '/static/favicon.png',
  '/static/icon-192.png',
  '/static/icon-512.png',
];

const API_CACHE_URLS = [
  '/stats',
  '/chapters',
  '/featured-search',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(APP_SHELL);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (url.pathname === '/offline-docs') {
    event.respondWith(networkFirstThenCache(event.request));
    return;
  }

  if (API_CACHE_URLS.some(u => url.pathname === u)) {
    event.respondWith(networkFirstThenCache(event.request));
    return;
  }

  if (url.pathname === '/search') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({ error: 'offline', offline: true }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })
    );
    return;
  }

  if (url.pathname === '/' || url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirstThenNetwork(event.request));
    return;
  }

  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

async function cacheFirstThenNetwork(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirstThenCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ error: 'offline' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CACHE_OFFLINE_DOCS') {
    event.waitUntil(
      fetch('/offline-docs')
        .then(res => {
          if (res.ok) {
            return caches.open(CACHE_NAME).then(cache => cache.put('/offline-docs', res));
          }
        })
        .then(() => {
          self.clients.matchAll().then(clients => {
            clients.forEach(client => client.postMessage({ type: 'OFFLINE_DOCS_CACHED' }));
          });
        })
        .catch(() => {
          self.clients.matchAll().then(clients => {
            clients.forEach(client => client.postMessage({ type: 'OFFLINE_DOCS_FAILED' }));
          });
        })
    );
  }
});
