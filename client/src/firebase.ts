import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Check if Firebase config is available
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Validate Firebase configuration
const requiredKeys = ['apiKey', 'authDomain', 'projectId', 'storageBucket', 'messagingSenderId', 'appId'];
const missingKeys = requiredKeys.filter(key => !firebaseConfig[key as keyof typeof firebaseConfig]);

let app;
let auth;

if (missingKeys.length > 0) {
  console.warn('Firebase configuration is incomplete. Missing keys:', missingKeys);
  console.warn('Please create a .env file in the client directory with the required Firebase configuration.');
  console.warn('See env.example for the required variables.');
  
  // For development, we'll use a mock configuration to prevent crashes
  const mockConfig = {
    apiKey: 'mock-api-key',
    authDomain: 'mock-domain.firebaseapp.com',
    projectId: 'mock-project',
    storageBucket: 'mock-project.appspot.com',
    messagingSenderId: '123456789',
    appId: 'mock-app-id'
  };
  
  console.warn('Using mock Firebase configuration for development.');
  app = initializeApp(mockConfig);
  auth = getAuth(app);
} else {
  // Initialize Firebase with real configuration
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
}

export { auth };
export default app; 