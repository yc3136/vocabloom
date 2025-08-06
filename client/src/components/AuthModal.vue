<template>
  <div class="auth-modal-overlay" v-if="show" @click="closeModal">
    <div class="auth-modal" @click.stop>
      <div class="auth-modal-header">
        <h2>{{ isLogin ? 'Log In' : 'Sign Up' }}</h2>
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
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="Enter your password"
          />
        </div>
        

        
        <div class="error-message" v-if="authStore.error">
          {{ authStore.error }}
        </div>
        
        <div class="warning-message" v-if="!authStore.isFirebaseConfigured">
          ⚠️ Firebase is not configured. Please set up your Firebase credentials in the .env file.
          <br>
          <small>See env.example for the required variables.</small>
        </div>
        
        <button type="submit" class="submit-btn" :disabled="authStore.loading || !authStore.isFirebaseConfigured">
          {{ authStore.loading ? 'Loading...' : (isLogin ? 'Log In' : 'Sign Up') }}
        </button>
      </form>
      
      <div class="auth-switch">
        <p>
          {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
          <button @click="toggleMode" class="switch-btn">
            {{ isLogin ? 'Sign Up' : 'Log In' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

interface Props {
  show: boolean;
  isLogin?: boolean;
}

interface Emits {
  (e: 'close'): void;
  (e: 'success'): void;
}

const props = withDefaults(defineProps<Props>(), {
  isLogin: true
});

const emit = defineEmits<Emits>();

const authStore = useAuthStore();
const email = ref('');
const password = ref('');

const closeModal = () => {
  emit('close');
  // Reset form
  email.value = '';
  password.value = '';
  authStore.error = null;
};

const toggleMode = () => {
  emit('close');
  // The parent component should handle switching modes
};

const handleSubmit = async () => {
  try {
    if (props.isLogin) {
      await authStore.signIn(email.value, password.value);
    } else {
      await authStore.signUp(email.value, password.value);
    }
    emit('success');
    closeModal();
  } catch (error) {
    // Error is handled by the store
    console.error('Authentication error:', error);
  }
};
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.auth-modal {
  background: var(--bg-surface);
  border-radius: 8px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-blue);
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

.auth-switch {
  margin-top: 24px;
  text-align: center;
}

.auth-switch p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.switch-btn {
  background: none;
  border: none;
  color: var(--primary-blue);
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  padding: 0;
  margin-left: 4px;
}

.switch-btn:hover {
  color: var(--blue-hover);
}
</style> 