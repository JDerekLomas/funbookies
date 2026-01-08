const CACHE_NAME = 'funbookies-v1';
const RUNTIME_CACHE = 'funbookies-runtime';

self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                '/reader.html',
                '/index.html',
                '/books/'
            ]);
        })
    );
    self.skipWaiting(); // Activate immediately
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Only handle same-origin requests
    if (url.origin !== location.origin) return;

    // Images: cache-first strategy
    if (url.pathname.match(/\.(png|webp|jpg|jpeg)$/)) {
        event.respondWith(
            caches.open(RUNTIME_CACHE).then((cache) => {
                return cache.match(event.request).then((cachedResponse) => {
                    // Fetch from network in background
                    const fetchPromise = fetch(event.request)
                        .then((networkResponse) => {
                            // Update cache with new response
                            if (networkResponse && networkResponse.status === 200) {
                                cache.put(event.request, networkResponse.clone());
                            }
                            return networkResponse;
                        })
                        .catch(() => cachedResponse); // Return cache on network error

                    // Return cached version immediately, or wait for network
                    return cachedResponse || fetchPromise;
                });
            })
        );
        return;
    }

    // Book JSON: network-first, fall back to cache
    if (url.pathname.match(/\.json$/)) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(RUNTIME_CACHE).then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request);
                })
        );
        return;
    }
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
                    .map((name) => {
                        console.log('Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    return self.clients.claim(); // Take control immediately
});
