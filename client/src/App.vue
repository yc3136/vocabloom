<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from './stores/auth';
import { useNotificationStore } from './stores/notification';
import AuthModal from './components/AuthModal.vue';
import UserProfile from './components/UserProfile.vue';
import NotificationToast from './components/NotificationToast.vue';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const showAuthModal = ref(false);
const authModalMode = ref<'login' | 'signup'>('login');

const openAuthModal = (mode: 'login' | 'signup') => {
  authModalMode.value = mode;
  showAuthModal.value = true;
};

const closeAuthModal = () => {
  showAuthModal.value = false;
};

const handleAuthSuccess = () => {
  showAuthModal.value = false;
  notificationStore.success('Successfully signed in!');
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
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/about" class="nav-link">About</router-link>
        </nav>
        
        <div class="auth-section">
          <div v-if="!authStore.isAuthenticated" class="auth-buttons">
            <button @click="openAuthModal('login')" class="auth-btn signin-btn">Log In</button>
            <button @click="openAuthModal('signup')" class="auth-btn signup-btn">Sign Up</button>
          </div>
          <UserProfile v-else />
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <!-- Auth Modal -->
    <AuthModal 
      :show="showAuthModal" 
      :is-login="authModalMode === 'login'"
      @close="closeAuthModal"
      @success="handleAuthSuccess"
    />

    <!-- Global Notifications -->
    <NotificationToast
      :show="notificationStore.show"
      :message="notificationStore.message"
      :type="notificationStore.type"
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
  background: transparent;
  color: #3b5bdb;
  border: 1px solid #3b5bdb;
}

.signin-btn:hover {
  background: #3b5bdb;
  color: white;
}

.signup-btn {
  background: #3b5bdb;
  color: white;
}

.signup-btn:hover {
  background: #2a3a5e;
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
