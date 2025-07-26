<script setup lang="ts">
// TODO: Implement translation functionality
</script>

<template>
  <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link>
  </nav>
  <router-view />
</template>

<style scoped>
nav {
  margin-bottom: 1rem;
}
nav a {
  margin: 0 0.5rem;
  text-decoration: none;
  color: #3b5bdb;
  font-weight: 500;
  transition: color 0.2s;
}
nav a.router-link-exact-active {
  font-weight: bold;
  text-decoration: underline;
  color: #2a3a5e;
}
nav a:hover {
  color: #4254e7;
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
</style>
