import { createApp } from 'vue'
import App from './App.vue'

// Import Vuetify and styles
// import 'vuetify/styles'
// import { createVuetify } from 'vuetify'
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'
import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './components/HomePage.vue';
import AboutPage from './components/AboutPage.vue';

// const vuetify = createVuetify({
//   components,
//   directives,
// })

const routes = [
  { path: '/', component: HomePage },
  { path: '/about', component: AboutPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);
app.use(router);
// app.use(vuetify)
app.mount('#app');
