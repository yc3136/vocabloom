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
        
        <div class="form-group" v-if="!isLogin">
          <label for="displayName">Display Name (Optional)</label>
          <input 
            type="text" 
            id="displayName" 
            v-model="displayName" 
            placeholder="Enter your display name"
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
const displayName = ref('');

const closeModal = () => {
  emit('close');
  // Reset form
  email.value = '';
  password.value = '';
  displayName.value = '';
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
      await authStore.signUp(email.value, password.value, displayName.value || undefined);
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
  background: white;
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
  color: #333;
  font-size: 24px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
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
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 8px;
}

.warning-message {
  color: #ffc107; /* Yellow color for warning */
  font-size: 14px;
  margin-top: 8px;
  padding: 8px;
  background-color: #fffbeb; /* Light yellow background */
  border: 1px solid #ffeeba; /* Light border */
  border-radius: 4px;
}

.submit-btn {
  background: #007bff;
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
  background: #0056b3;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.auth-switch {
  margin-top: 24px;
  text-align: center;
}

.auth-switch p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.switch-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  padding: 0;
  margin-left: 4px;
}

.switch-btn:hover {
  color: #0056b3;
}
</style> 