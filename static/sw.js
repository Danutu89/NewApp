

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
  if(document.querySelector('html').getAttribute("id")){
    Notification.requestPermission().then(function(result) {
      if (result === 'denied') {
        console.log('Permission wasn\'t granted. Allow a retry.');
        return;
      }
      if (result === 'default') {
        console.log('The permission request was dismissed.');
        
        return;
      }
      subscribeUser();
    });
  }
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

this.addEventListener('fetch', function (event) {
  // it can be empty if you just want to get rid of that error
});

self.addEventListener('pushsubscriptionchange', function(event) {
  console.log('[Service Worker]: \'pushsubscriptionchange\' event fired.');
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  event.waitUntil(
    self.registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    })
    .then(function(newSubscription) {
      const dataToSend = JSON.stringify(newSubscription);
      var get_id = document.querySelector('html').getAttribute("id");
      dataToSend['user'] = get_id;
      fetch("https://newapp.nl/api/subscribe",{method:"post",body:dataToSend})
      console.log('[Service Worker] New subscription: ', newSubscription);
    })
  );
});

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