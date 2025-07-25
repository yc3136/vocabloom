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
  <div class="home-container">
    <h1>Vocabloom</h1>
    <p class="subtitle">A simple tool to help you learn and understand new vocabulary with instant translations and explanations.</p>
    <input
      v-model="term"
      placeholder="Enter a word or phrase"
      class="term-input"
      @keyup.enter="lookup"
    />
    <button @click="lookup" :disabled="loading" class="lookup-btn">
      <span v-if="!loading">Look up</span>
      <span v-else>Loading...</span>
    </button>
    <div v-if="response" class="response-box">
      <p>{{ response }}</p>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  color: #222;
  background: #f8fafd;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(30, 34, 90, 0.07);
  padding: 2rem 2rem 2.5rem 2rem;
}
h1 {
  color: #2a3a5e;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}
.subtitle {
  color: #5a6270;
  font-size: 1rem;
  margin-bottom: 2rem;
}
.term-input {
  margin-top: 2rem;
  padding: 0.5rem;
  width: 100%;
  border-radius: 6px;
  border: 1px solid #cfd8dc;
  font-size: 1rem;
  background: #fff;
  color: #222;
  transition: border 0.2s;
}
.term-input:focus {
  border: 1.5px solid #3b5bdb;
  outline: none;
}
.lookup-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: linear-gradient(90deg, #3b5bdb 0%, #5f6eed 100%);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(30, 34, 90, 0.08);
  transition: background 0.2s, box-shadow 0.2s;
}
.lookup-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.lookup-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #4254e7 0%, #7b8cff 100%);
  box-shadow: 0 4px 16px rgba(30, 34, 90, 0.12);
}
.response-box {
  margin-top: 2rem;
  background: #e9ecf8;
  padding: 1rem;
  border-radius: 10px;
  color: #2a3a5e;
  font-size: 1.05rem;
  box-shadow: 0 1px 6px rgba(30, 34, 90, 0.06);
}
</style> 