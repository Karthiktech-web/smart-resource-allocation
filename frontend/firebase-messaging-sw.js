importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyA__xAvct5pZPmeyhX9rlQd2TE3IS1q0_Y",
  authDomain: "sra-backend-2026.firebaseapp.com",
  projectId: "sra-backend-2026",
  messagingSenderId: "256611262132",
  appId: "1:256611262132:web:d990bce2f611cac36101e1"
});

const messaging = firebase.messaging();


messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification?.title || 'Background Message Title';
  const notificationOptions = {
    body: payload.notification?.body || 'Background Message body.',
    icon: payload.notification?.icon || '/firebase-logo.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
