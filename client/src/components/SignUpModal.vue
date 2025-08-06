<template>
  <div class="auth-modal-overlay" v-if="show" @click="closeModal">
    <div class="auth-modal" @click.stop>
      <div class="auth-modal-header">
        <h2>Sign Up</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required 
            placeholder="Enter your email"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input-container">
            <input 
              :type="showPassword ? 'text' : 'password'"
              id="password" 
              v-model="password" 
              required 
              placeholder="Create a password (min 6 characters)"
              class="password-input"
            />
            <button 
              type="button"
              @click="showPassword = !showPassword"
              class="password-toggle-btn"
              :title="showPassword ? 'Hide password' : 'Show password'"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="password-input-container">
            <input 
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirmPassword" 
              v-model="confirmPassword" 
              required 
              placeholder="Confirm your password"
              class="password-input"
            />
            <button 
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="password-toggle-btn"
              :title="showConfirmPassword ? 'Hide password' : 'Show password'"
            >
              {{ showConfirmPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        
        <div class="error-message" v-if="authStore.error">
          {{ authStore.error }}
        </div>
        
        <div class="warning-message" v-if="!authStore.isFirebaseConfigured">
          ⚠️ Firebase is not configured. Please set up your Firebase credentials in the .env file.
          <br>
          <small>See env.example for the required variables.</small>
        </div>
        
        <button type="submit" class="submit-btn" :disabled="authStore.loading || !authStore.isFirebaseConfigured || !canSubmit">
          {{ authStore.loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>
      
      <!-- Divider -->
      <div class="divider">
        <span>or</span>
      </div>
      
      <!-- Google Sign Up Button -->
      <button 
        @click="handleGoogleSignIn" 
        class="google-signin-btn" 
        :disabled="authStore.loading || !authStore.isFirebaseConfigured"
        type="button"
      >
        <svg class="google-icon" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        {{ authStore.loading ? 'Loading...' : 'Sign up with Google' }}
      </button>
      
      <div class="auth-footer">
        <p>
          Already have an account? 
          <button @click="openLogInModal" class="login-link">
            Sign In
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notification';

interface Props {
  show: boolean;
}

interface Emits {
  (e: 'close'): void;
  (e: 'success'): void;
  (e: 'openLogIn'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const showConfirmPassword = ref(false);

const canSubmit = computed(() => {
  return email.value && 
         password.value && 
         confirmPassword.value && 
         password.value === confirmPassword.value &&
         password.value.length >= 6;
});

const closeModal = () => {
  emit('close');
  // Reset form
  email.value = '';
  password.value = '';
  confirmPassword.value = '';
  authStore.error = null;
};

const handleSubmit = async () => {
  if (!canSubmit.value) {
    notificationStore.error('Please fill in all fields correctly');
    return;
  }
  
  try {
    await authStore.signUp(email.value, password.value);
    emit('success');
    closeModal();
  } catch (error) {
    // Error is handled by the store
    console.error('Sign up error:', error);
  }
};

const handleGoogleSignIn = async () => {
  try {
    await authStore.signInWithGoogle();
    emit('success');
    closeModal();
  } catch (error) {
    // Error is handled by the store
    console.error('Google sign up error:', error);
  }
};

const openLogInModal = () => {
  closeModal();
  emit('openLogIn');
};
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.auth-modal {
  background: white;
  border-radius: 8px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.auth-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.auth-modal-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--text-primary);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.password-input {
  padding-right: 40px; /* Make room for the toggle button */
  width: 100%;
  box-sizing: border-box;
}

.password-toggle-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  font-size: 16px;
  color: var(--text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
}

.password-toggle-btn:hover {
  color: var(--text-primary);
  background: var(--bg-primary);
}

.error-message {
  color: var(--error-red);
  font-size: 14px;
  margin-top: 8px;
}

.warning-message {
  color: var(--warning-amber);
  font-size: 14px;
  margin-top: 8px;
  padding: 8px;
  background-color: rgba(251, 191, 36, 0.1);
  border: 1px solid var(--warning-amber);
  border-radius: 4px;
}

.submit-btn {
  background: var(--primary-blue);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--blue-hover);
}

.submit-btn:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  margin: 20px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.divider span {
  padding: 0 16px;
}

.google-signin-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.google-signin-btn:hover:not(:disabled) {
  background: var(--bg-primary);
  border-color: var(--text-secondary);
}

.google-signin-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.google-icon {
  width: 20px;
  height: 20px;
}

.auth-footer {
  margin-top: 24px;
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.auth-footer p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-link {
  background: none;
  border: none;
  color: var(--primary-blue);
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  padding: 0;
  margin-left: 4px;
}

.login-link:hover {
  color: var(--blue-hover);
}
</style> 