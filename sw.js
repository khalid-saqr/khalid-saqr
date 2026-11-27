// Legacy cleanup service worker. This site no longer registers one.
// CacheStorage belongs to the entire origin; do not delete unrelated project caches.
// No historical cache names are verified in the current repository.
self.addEventListener('install', event => { event.waitUntil(self.skipWaiting()); });
self.addEventListener('activate', event => {
  event.waitUntil(self.registration.unregister());
});
