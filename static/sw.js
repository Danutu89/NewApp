
self.addEventListener('install', function(event) {
  self.skipWaiting();
    caches.open('newapp.cache').then(function(cache) {
      return cache.addAll(
        [
          'https://newappcdn.b-cdn.net/newapp.min.js',
          'https://newappcdn.b-cdn.net/jquery.js',
          'https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js',
          'https://newappcdn.b-cdn.net/all.css',
          'https://newappcdn.b-cdn.net/styles.css',
          'https://newappcdn.b-cdn.net/dark_code.css',
          'https://newapp.nl/static/logo.svg',
          'https://newapp.nl/static/favicon.png',
          'https://newapp.nl/static/manifest.json'
        
        ]
      );
    })
  
});

if (self.clients && (typeof self.clients.claim === 'function')) {
  self.addEventListener('activate', function(event) {
    event.waitUntil(self.clients.claim());
  });
}



self.addEventListener("fetch", function(event) { 
	event.respondWith( 
		caches.match(event.request)
			.then(function (response) { 
				return response || fetch(event.request)
			.then(function(response) { 
				return response; 
			}); 
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