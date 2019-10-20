

const applicationServerPublicKey = 'BLbMAFGsECz6jtlDAon7PQ8i56FHwCk-hQKIHLJ04MCqwwCWs4uN2FQWxqpySpLnRzb5bJMrmKDs5q3B4nGnmYY';

/* eslint-enable max-len */

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('newapp.cache').then(function(cache) {
      return cache.addAll(
        [
          'https://newappcdn.b-cdn.net/newapp.js',
          'https://newappcdn.b-cdn.net/jquery.js',
          'https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js',
          'https://newappcdn.b-cdn.net/all.css',
          'https://newappcdn.b-cdn.net/styles.css'
        ]
      );
    })
  );
});

if (self.clients && (typeof self.clients.claim === 'function')) {
  self.addEventListener('activate', function(event) {
    event.waitUntil(self.clients.claim());
  });
}

self.addEventListener('message', function(event) {
  if (event.data.command === 'delete_all') {
    console.log('About to delete all caches...');
    deleteAllCaches().then(function() {
      console.log('Caches deleted.');
      event.ports[0].postMessage({
        error: null
      });
    }).catch(function(error) {
      console.log('Caches not deleted:', error);
      event.ports[0].postMessage({
        error: error
      });
    });
  }
});

self.addEventListener('push', function(event) {
  var title = "NewApp"
      , body = event.data.text()
      , icon = "https://newapp.nl/static/logo.jpg"
      , n = "default-tag" + body;
    event.waitUntil(self.registration.showNotification(title, {
        body: body,
        icon: icon,
        tag: n,
        data: {
            url: "https://newapp.nl"
        }
    }))
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
// self.addEventListener('pushsubscriptionchange', function(event) {
//   console.log('[Service Worker]: \'pushsubscriptionchange\' event fired.');
//   const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
//   event.waitUntil(
//     self.registration.pushManager.subscribe({
//       userVisibleOnly: true,
//       applicationServerKey: applicationServerKey
//     })
//     .then(function(newSubscription) {
//       const dataToSend = JSON.stringify(newSubscription);
//       var get_id = document.querySelector('html').getAttribute("id");
//       dataToSend['user'] = get_id;
//       fetch("https://newapp.nl/api/subscribe",{method:"post",body:dataToSend})
//       console.log('[Service Worker] New subscription: ', newSubscription);
//     })
//   );
// });

function subscribeUser() {
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  swRegistration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: applicationServerKey
  })
  .then(function(subscription) {
    console.log('User is subscribed.');

    const dataToSend = JSON.stringify(subscription);
      var get_id = document.querySelector('html').getAttribute("id");
      dataToSend['user'] = get_id;
      fetch("https://newapp.nl/api/subscribe",{method:"post",body:dataToSend})
      console.log('[Service Worker] New subscription: ', subscription);

  })
  .catch(function(err) {
    console.log('Failed to subscribe the user: ', err);
  });
}