// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
//import { getStorage } from "firebase/storage";
// import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: process.env.REACT_APP_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_PROJECT_ID,
  storageBucket: process.env.REACT_APP_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_ID,
  measurementId: process.env.REACT_APP_MEASUREMENT_ID
};

// Initialize Firebase
const fbapp = initializeApp(firebaseConfig);
export const analytics = getAnalytics(fbapp);
//export const recaptcha = initializeAppCheck(fbapp, {
//  provider: new ReCaptchaV3Provider('process.env.REACT_APP_RECAPCHA_KEY'),
//
//  // Optional argument. If true, the SDK automatically refreshes App Check
//  // tokens as needed.
//  isTokenAutoRefreshEnabled: true
//});
const db = getFirestore(fbapp);

export default db;