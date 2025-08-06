import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import global design tokens
import './design-tokens.css'

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
import UserPreferencesPage from './components/UserPreferencesPage.vue';

// const vuetify = createVuetify({
//   components,
//   directives,
// })

const routes = [
  { path: '/', component: HomePage },
  { path: '/about', component: AboutPage },
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
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
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

app.mount('#app');
