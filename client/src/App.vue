<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from './stores/auth';
import { useNotificationStore } from './stores/notification';
import AuthModal from './components/AuthModal.vue';
import SignUpModal from './components/SignUpModal.vue';
import UserProfile from './components/UserProfile.vue';
import NotificationToast from './components/NotificationToast.vue';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const showAuthModal = ref(false);
const showSignUpModal = ref(false);

const openAuthModal = () => {
  showAuthModal.value = true;
};

const closeAuthModal = () => {
  showAuthModal.value = false;
};

// const openSignUpModal = () => {
//   showSignUpModal.value = true;
// };

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
</script>

<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-link">
            <img src="/assets/vocabloom-logo-light.png" alt="Vocabloom" class="logo-image" />
          </router-link>
        </div>
        
        <nav class="nav-links">
          <router-link to="/" class="nav-link">Learn</router-link>
          <router-link to="/discover" class="nav-link">Discover</router-link>
          <router-link to="/about" class="nav-link">About</router-link>
        </nav>
        
        <div class="auth-section">
          <div class="auth-container">
            <!-- Show loading state while Firebase is initializing -->
            <div v-if="authStore.loading" class="auth-loading">
              <div class="loading-spinner"></div>
            </div>
            <!-- Show single sign in/sign up button when not loading and not authenticated -->
            <div v-else-if="!authStore.isAuthenticated" class="auth-buttons">
              <button @click="openAuthModal()" class="auth-btn signin-btn">Sign In / Sign Up</button>
            </div>
            <!-- Show user profile when authenticated -->
            <UserProfile v-else />
          </div>
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <!-- Auth Modal -->
    <AuthModal 
      :show="showAuthModal" 
      @close="closeAuthModal"
      @success="handleAuthSuccess"
      @openSignUp="handleOpenSignUp"
    />
    
    <!-- Sign Up Modal -->
    <SignUpModal 
      :show="showSignUpModal" 
      @close="closeSignUpModal"
      @success="handleAuthSuccess"
      @openLogIn="handleOpenLogIn"
    />

    <!-- Global Notifications -->
    <NotificationToast
      :show="notificationStore.show"
      :message="notificationStore.message"
      :type="notificationStore.type"
      :allow-html="notificationStore.allowHtml"
      @close="notificationStore.hide"
    />
  </div>
</template>

<style scoped>
.app-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.logo-image {
  height: 64px;
  width: auto;
  display: block;
}

.nav-links {
  display: flex;
  gap: 32px;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: #5a6270;
  font-weight: 500;
  transition: color 0.2s;
  padding: 8px 0;
}

.nav-link:hover {
  color: #2a3a5e;
}

.nav-link.router-link-active {
  color: #3b5bdb;
  border-bottom: 2px solid #3b5bdb;
}

.auth-section {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.auth-container {
  width: 200px; /* Fixed width to prevent shifting */
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.auth-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.signin-btn {
  background: #3b5bdb;
  color: white;
  border: 1px solid #3b5bdb;
}

.signin-btn:hover {
  background: #2a3a5e;
  border-color: #2a3a5e;
}

.auth-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e9ecef;
  border-top: 2px solid #3b5bdb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.app-main {
  min-height: calc(100vh - 64px);
  background: #f8fafd;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
  }
  
  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 12px;
    gap: 24px;
  }
  
  .auth-buttons {
    gap: 8px;
  }
  
  .auth-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>

<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

body, #app {
  font-family: 'Nunito', 'Segoe UI', Arial, sans-serif;
  background: #f4f6fb;
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}
</style>
