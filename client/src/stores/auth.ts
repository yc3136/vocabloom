import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { auth } from '../firebase';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  updatePassword,
  EmailAuthProvider,
  reauthenticateWithCredential,
  sendPasswordResetEmail,
  sendEmailVerification,
  GoogleAuthProvider,
  signInWithPopup,
  type User
} from 'firebase/auth';
import { useNotificationStore } from './notification';
import { usePreferencesStore } from './preferences';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);
  const isFirebaseConfigured = ref(true);
  
  // Global auth modal management
  const showAuthModal = ref(false);
  const showSignUpModal = ref(false);
  
  const notificationStore = useNotificationStore();

  const initAuth = () => {
    // Check if Firebase is properly configured
    try {
      const app = (auth as any).app;
      isFirebaseConfigured.value = app.options.apiKey !== 'mock-api-key';
    } catch (e) {
      isFirebaseConfigured.value = false;
    }

    if (!isFirebaseConfigured.value) {
      // Firebase not configured, using mock authentication
      return
    }

    onAuthStateChanged(auth as any, (firebaseUser) => {
      user.value = firebaseUser;
      loading.value = false;
    });
  };

  const signIn = async (email: string, password: string) => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      const userCredential = await signInWithEmailAndPassword(auth as any, email, password);
      
      // Check if email is verified
      if (!userCredential.user.emailVerified) {
        notificationStore.info('Please verify your email address. Check your inbox for a verification link.');
      }
    } catch (err: any) {
      error.value = err.message;
      notificationStore.error('Sign in failed: ' + err.message);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const signUp = async (email: string, password: string) => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      
      // Create user account
      const userCredential = await createUserWithEmailAndPassword(auth as any, email, password);
      
      // Send email verification
      await sendEmailVerification(userCredential.user);
      
      notificationStore.success('Account created successfully! Please check your email to verify your account.');
    } catch (err: any) {
      error.value = err.message;
      notificationStore.error('Sign up failed: ' + err.message);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const signInWithGoogle = async () => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      
      const provider = new GoogleAuthProvider();
      // Add scopes if needed
      provider.addScope('email');
      provider.addScope('profile');
      
      // Customize the OAuth popup
      provider.setCustomParameters({
        prompt: 'select_account'
      });
      
      const userCredential = await signInWithPopup(auth as any, provider);
      
      // Call backend to create/update user in database
      const token = await userCredential.user.getIdToken();
      const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${API_BASE}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          uid: userCredential.user.uid,
          email: userCredential.user.email,
          displayName: userCredential.user.displayName,
          photoURL: userCredential.user.photoURL
        })
      });

      if (!response.ok) {
        throw new Error('Failed to sync user data with backend');
      }
      

    } catch (err: any) {
      error.value = err.message;
      
      if (err.code === 'auth/popup-closed-by-user') {
        notificationStore.info('Sign in was cancelled');
      } else {
        notificationStore.error('Google sign in failed: ' + err.message);
      }
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    if (!isFirebaseConfigured.value) {
      user.value = null;
      return;
    }

    try {
      await signOut(auth as any);
      user.value = null;
      
      // Clear user preferences on logout
      const preferencesStore = usePreferencesStore();
      preferencesStore.clearPreferences();
      
      notificationStore.success('Successfully signed out!');
    } catch (err: any) {
      error.value = err.message;
      notificationStore.error('Sign out failed: ' + err.message);
    }
  };

  const changePassword = async (newPassword: string, currentPassword?: string) => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    if (!user.value) {
      notificationStore.error('User not authenticated');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      
      // If current password is provided, re-authenticate first
      if (currentPassword) {
        const credential = EmailAuthProvider.credential(user.value.email!, currentPassword);
        await reauthenticateWithCredential(user.value, credential);
      }
      
      await updatePassword(user.value, newPassword);
      notificationStore.success('Password changed successfully!');
    } catch (err: any) {
      error.value = err.message;
      
      if (err.code === 'auth/requires-recent-login') {
        notificationStore.error('Please provide your current password to change your password');
        throw new Error('REAUTH_REQUIRED');
      } else if (err.code === 'auth/wrong-password') {
        notificationStore.error('Current password is incorrect');
        throw new Error('WRONG_PASSWORD');
      } else {
        notificationStore.error('Password change failed: ' + err.message);
        throw err;
      }
    } finally {
      loading.value = false;
    }
  };

  const forgotPassword = async (email: string) => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      
      await sendPasswordResetEmail(auth as any, email);
      notificationStore.success('Password reset email sent! Check your inbox for instructions.');
    } catch (err: any) {
      error.value = err.message;
      
      if (err.code === 'auth/user-not-found') {
        notificationStore.error('No account found with this email address');
      } else if (err.code === 'auth/invalid-email') {
        notificationStore.error('Please enter a valid email address');
      } else {
        notificationStore.error('Failed to send password reset email: ' + err.message);
      }
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const resendEmailVerification = async () => {
    if (!isFirebaseConfigured.value) {
      notificationStore.error('Firebase is not configured. Please check your environment variables.');
      return;
    }

    if (!user.value) {
      notificationStore.error('User not authenticated');
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      
      await sendEmailVerification(user.value);
      notificationStore.success('Verification email sent! Check your inbox.');
    } catch (err: any) {
      error.value = err.message;
      notificationStore.error('Failed to send verification email: ' + err.message);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getIdToken = async (): Promise<string> => {
    if (!user.value) {
      throw new Error('User not authenticated');
    }
    return await user.value.getIdToken();
  };

  const isAuthenticated = computed(() => !!user.value);

  // Global auth modal management functions
  const openAuthModal = () => {
    showAuthModal.value = true;
  };

  const closeAuthModal = () => {
    showAuthModal.value = false;
  };

  const openSignUpModal = () => {
    showSignUpModal.value = true;
  };

  const closeSignUpModal = () => {
    showSignUpModal.value = false;
  };

  const handleAuthSuccess = () => {
    showAuthModal.value = false;
    showSignUpModal.value = false;
    notificationStore.success('Successfully signed in!');
  };

  const handleOpenSignUp = () => {
    showAuthModal.value = false;
    showSignUpModal.value = true;
  };

  const handleOpenLogIn = () => {
    showSignUpModal.value = false;
    showAuthModal.value = true;
  };

  // Function to require authentication - shows auth modal if not authenticated
  const requireAuth = (action: string = 'continue'): boolean => {
    if (!isAuthenticated.value) {
      notificationStore.info(`Please sign in to ${action}.`);
      openAuthModal();
      return false;
    }
    return true;
  };

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isFirebaseConfigured,
    // Auth modal management
    showAuthModal,
    showSignUpModal,
    openAuthModal,
    closeAuthModal,
    openSignUpModal,
    closeSignUpModal,
    handleAuthSuccess,
    handleOpenSignUp,
    handleOpenLogIn,
    requireAuth,
    signIn,
    signUp,
    signInWithGoogle,
    logout,
    changePassword,
    forgotPassword,
    resendEmailVerification,
    getIdToken,
    initAuth
  };
}); 