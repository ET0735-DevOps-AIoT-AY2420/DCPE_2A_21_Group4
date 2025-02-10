// Import the Firebase modules you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAVmQ8dh6pGV9pbTk1I6GmvZuXT-FR8Sus",
  authDomain: "library-system-67346.firebaseapp.com",
  databaseURL: "https://library-system-67346-default-rtdb.firebaseio.com",
  projectId: "library-system-67346",
  storageBucket: "library-system-67346.firebasestorage.app",
  messagingSenderId: "487833718014",
  appId: "1:487833718014:web:20e8256c3deb8e22d7a9af",
  measurementId: "G-W081J17K2Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Firestore database instance
export const db = getFirestore(app);

// Firebase authentication instance
export const auth = getAuth(app);
