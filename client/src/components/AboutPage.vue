<template>
  <div class="about-container">
    <h1>About Vocabloom</h1>
    <p>Vocabloom is an open-source vocabulary learning tool. Built with Vue 3, FastAPI, and AWS.</p>
    <p>
      <a href="https://github.com/yc3136/vocabloom" target="_blank" rel="noopener">View on GitHub</a>
    </p>
    <p>
      More info and credits coming soon.
    </p>
  </div>
</template>

<script setup lang="ts">
// ... existing code ...
</script>

<style scoped>
.about-container {
  max-width: 500px;
  margin: 2rem auto;
  background: #f8fafd;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(30, 34, 90, 0.07);
  padding: 2rem 2rem 2.5rem 2rem;
  color: #222;
  text-align: center;
}
h1 {
  color: #2a3a5e;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}
a {
  color: #3b5bdb;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
a:hover {
  color: #4254e7;
  text-decoration: underline;
}
</style> 