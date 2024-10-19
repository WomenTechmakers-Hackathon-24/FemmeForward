// src/firebase.tsx
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, User } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "AIzaSyBQXX5VUW8hHGG8dhd1c_JJYpJLv1mTzB8",
    authDomain: "empowerwomen-fbbda.firebaseapp.com",
    projectId: "empowerwomen-fbbda",
    storageBucket: "empowerwomen-fbbda.appspot.com",
    messagingSenderId: "551651188331",
    appId: "1:551651188331:web:ec269254d8b6bc08b55b2e",
    measurementId: "G-1DLFSP45VH"
  };

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

export { auth, GoogleAuthProvider, signInWithPopup, signOut };    
export type { User };

