const CACHE_NAME = 'marketplace-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/search',
  '/cart',
  '/wishlist',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
  'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&display=swap'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version if available
        if (response) {
          return response;
        }

        // Clone the request because it's a stream
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then((response) => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response because it's a stream
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });

          return response;
        }).catch(() => {
          // Return offline page for navigation requests
          if (event.request.destination === 'document') {
            return caches.match('/offline.html');
          }
          
          // Return placeholder image for image requests
          if (event.request.destination === 'image') {
            return caches.match('/icons/offline-image.png');
          }
        });
      }
    )
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('Push event received:', event);
  
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'MarketPlace', body: event.data.text() };
    }
  }

  const options = {
    title: data.title || 'MarketPlace',
    body: data.body || 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    image: data.image,
    data: data.data || {},
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: '/icons/view-32x32.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/close-32x32.png'
      }
    ],
    tag: data.tag || 'general',
    renotify: true,
    requireInteraction: false,
    silent: false,
    vibrate: [200, 100, 200]
  };

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Notification click received:', event);
  
  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  const urlToOpen = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then((clientList) => {
      // Check if there's already a window/tab open with the target URL
      for (let client of clientList) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }

      // If no window/tab is open, open a new one
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Background sync event:', event.tag);

  if (event.tag === 'background-sync-cart') {
    event.waitUntil(syncCart());
  } else if (event.tag === 'background-sync-wishlist') {
    event.waitUntil(syncWishlist());
  } else if (event.tag === 'background-sync-orders') {
    event.waitUntil(syncOrders());
  }
});

// Sync functions
async function syncCart() {
  try {
    // Get pending cart updates from IndexedDB
    const pendingUpdates = await getPendingCartUpdates();
    
    for (const update of pendingUpdates) {
      try {
        const response = await fetch(update.url, {
          method: update.method,
          headers: update.headers,
          body: update.body
        });
        
        if (response.ok) {
          await removePendingCartUpdate(update.id);
          console.log('Cart sync successful:', update.id);
        }
      } catch (error) {
        console.error('Cart sync failed:', update.id, error);
      }
    }
  } catch (error) {
    console.error('Background cart sync failed:', error);
  }
}

async function syncWishlist() {
  try {
    // Similar implementation for wishlist sync
    console.log('Wishlist sync completed');
  } catch (error) {
    console.error('Background wishlist sync failed:', error);
  }
}

async function syncOrders() {
  try {
    // Similar implementation for orders sync
    console.log('Orders sync completed');
  } catch (error) {
    console.error('Background orders sync failed:', error);
  }
}

// Helper functions for IndexedDB operations
async function getPendingCartUpdates() {
  // Implementation for getting pending updates from IndexedDB
  return [];
}

async function removePendingCartUpdate(id) {
  // Implementation for removing completed updates from IndexedDB
  console.log('Removed pending cart update:', id);
}

// Message handling from the main thread
self.addEventListener('message', (event) => {
  console.log('Service worker received message:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'CACHE_URLS') {
    // Cache specific URLs on demand
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(event.data.urls);
      })
    );
  }
});

// Network status change handling
self.addEventListener('online', () => {
  console.log('Network is online');
  // Trigger background sync for pending actions
  self.registration.sync.register('background-sync-cart');
  self.registration.sync.register('background-sync-wishlist');
  self.registration.sync.register('background-sync-orders');
});

self.addEventListener('offline', () => {
  console.log('Network is offline');
});