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
  type User
} from 'firebase/auth';
import { useNotificationStore } from './notification';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);
  const isFirebaseConfigured = ref(true);
  
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
      await signInWithEmailAndPassword(auth as any, email, password);
      notificationStore.success('Successfully signed in!');
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
      await createUserWithEmailAndPassword(auth as any, email, password);
      
      notificationStore.success('Account created successfully!');
    } catch (err: any) {
      error.value = err.message;
      notificationStore.error('Sign up failed: ' + err.message);
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

  const getIdToken = async (): Promise<string> => {
    if (!user.value) {
      throw new Error('User not authenticated');
    }
    return await user.value.getIdToken();
  };

  const isAuthenticated = computed(() => !!user.value);

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isFirebaseConfigured,
    signIn,
    signUp,
    logout,
    changePassword,
    getIdToken,
    initAuth
  };
}); 