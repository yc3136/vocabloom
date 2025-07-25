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
  <v-app theme="dark">
    <v-main style="background: #181818; min-height: 100vh;">
      <div style="text-align:center; margin-top:2rem; max-width: 400px; margin-left: auto; margin-right: auto; color: #fff;">
        <h1>Vocabloom</h1>
        <p>A simple tool to help you learn and understand new vocabulary with instant translations and explanations.</p>
        <v-text-field
          v-model="term"
          label="Enter a word or phrase"
          outlined
          dense
          style="margin-top: 2rem;"
          color="primary"
        />
        <v-btn color="primary" @click="lookup" :loading="loading" style="margin-top: 1rem;">Look up</v-btn>
        <div v-if="response" style="margin-top: 2rem;">
          <p style="background: #232323; padding: 1rem; border-radius: 8px; color: #fff;">{{ response }}</p>
        </div>
      </div>
    </v-main>
  </v-app>
</template>

<style scoped>
/* Add any custom styles here if needed */
</style>
