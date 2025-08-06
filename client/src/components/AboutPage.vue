<template>
  <div class="about-container">
    <p>Vocabloom is an open-source vocabulary learning platform. Built with Vue 3, FastAPI, and Google Cloud Platform.</p>
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
  background: var(--bg-surface);
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(30, 34, 90, 0.07);
  padding: 2rem 2rem 2.5rem 2rem;
  color: var(--text-primary);
  text-align: center;
}
h1 {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}
a {
  color: var(--primary-blue);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
a:hover {
  color: var(--blue-hover);
  text-decoration: underline;
}
</style> 