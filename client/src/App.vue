<script setup lang="ts">
import { ref } from 'vue'

const term = ref('')
const response = ref('')
const loading = ref(false)

async function lookup() {
  if (!term.value) return
  loading.value = true
  response.value = ''
  try {
    const res = await fetch('http://127.0.0.1:8000/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term: term.value })
    })
    const data = await res.json()
    response.value = data.message || JSON.stringify(data)
  } catch (e) {
    response.value = 'Error contacting backend.'
  } finally {
    loading.value = false
  }
}
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
