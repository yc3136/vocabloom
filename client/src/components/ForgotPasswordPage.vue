<template>
  <div class="forgot-password-page">
    <div class="container">
      <div class="forgot-password-card">
        <div class="header">
          <h1>Forgot Password</h1>
          <p>Enter your email address and we'll send you a link to reset your password.</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="forgot-password-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              required 
              placeholder="Enter your email address"
              class="form-input"
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
            {{ authStore.loading ? 'Sending...' : 'Send Reset Email' }}
          </button>
        </form>
        
        <div class="links">
          <router-link to="/" class="back-link">← Back to Home</router-link>
          <router-link to="/" class="login-link">Remember your password? Log in</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';


const authStore = useAuthStore();
const email = ref('');

const handleSubmit = async () => {
  try {
    await authStore.forgotPassword(email.value);
    // Success message is handled by the auth store
  } catch (error) {
    // Error is already handled by the auth store
    console.error('Forgot password error:', error);
  }
};
</script>

<style scoped>
.forgot-password-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.container {
  width: 100%;
  max-width: 400px;
}

.forgot-password-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.header p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.forgot-password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.form-input {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.error-message {
  color: var(--error-red);
  font-size: 14px;
  padding: 8px;
  background-color: rgba(248, 113, 113, 0.1);
  border: 1px solid var(--error-red);
  border-radius: 4px;
}

.warning-message {
  color: var(--warning-amber);
  font-size: 14px;
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
  border-radius: 6px;
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

.links {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: center;
}

.back-link, .login-link {
  color: var(--primary-blue);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.back-link:hover, .login-link:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .forgot-password-card {
    padding: 24px;
  }
  
  .header h1 {
    font-size: 20px;
  }
}
</style> 