import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import global design tokens and design system
import './design-tokens.css'
import './design-system.css'

// Import Vuetify and styles
// import 'vuetify/styles'
// import { createVuetify } from 'vuetify'
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'
import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './components/HomePage.vue';
import AboutPage from './components/AboutPage.vue';
import FlashcardDashboard from './components/FlashcardDashboard.vue';
import MyWordsPage from './components/MyWordsPage.vue';
import MyStoriesPage from './components/MyStoriesPage.vue';
import MyImagesPage from './components/MyImagesPage.vue';
import UserPreferencesPage from './components/UserPreferencesPage.vue';
import ForgotPasswordPage from './components/ForgotPasswordPage.vue';
import DiscoverPage from './components/DiscoverPage.vue';

// const vuetify = createVuetify({
//   components,
//   directives,
// })

const routes = [
  { path: '/', component: HomePage },
  { path: '/discover', component: DiscoverPage },
  { path: '/about', component: AboutPage },
  { path: '/forgot-password', component: ForgotPasswordPage },
  { 
    path: '/flashcards', 
    component: FlashcardDashboard,
    meta: { requiresAuth: true }
  },
  { 
    path: '/words', 
    component: MyWordsPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/stories', 
    component: MyStoriesPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/images', 
    component: MyImagesPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/profile', 
    component: UserPreferencesPage,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route guard for authentication
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  
  // If Firebase is still loading authentication state, wait for it
  if (authStore.loading) {
    // Wait for authentication to be determined
    await new Promise<void>((resolve) => {
      const unwatch = watch(() => authStore.loading, (loading) => {
        if (!loading) {
          unwatch();
          resolve();
        }
      });
    });
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to home page if not authenticated
    next('/');
  } else {
    // Allow navigation
    next();
  }
});

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
// app.use(vuetify)

// Initialize Firebase auth
import { useAuthStore } from './stores/auth';


const authStore = useAuthStore();
authStore.initAuth();

// Watch for authentication state changes and redirect if needed
import { watch } from 'vue';
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated && router.currentRoute.value.meta.requiresAuth) {
    // User logged out while on a protected route, redirect to home
    router.push('/');
  }
});

app.mount('#app');
