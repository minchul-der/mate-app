// Firebase 설정
const firebaseConfig = {
  apiKey:            "AIzaSyCKIndlAxNuQuNtSi6ddZwPTEytuRMJ2v8",
  authDomain:        "mate-app-d2f06.firebaseapp.com",
  projectId:         "mate-app-d2f06",
  storageBucket:     "mate-app-d2f06.firebasestorage.app",
  messagingSenderId: "355984297741",
  appId:             "1:355984297741:web:8a1cb8159c49f504742a44",
  measurementId:     "G-9F4R2738XF"
};

// Firebase 초기화 (중복 방지)
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
