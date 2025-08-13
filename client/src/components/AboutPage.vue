<template>
  <div class="about-container">
    <p>Vocabloom is an open-source vocabulary learning platform. Built with Vue 3, FastAPI, and Google Cloud Platform.</p>
    
    <!-- Content Statistics -->
    <div v-if="discoverStore.stats" class="stats-section">
      <h2>Platform Statistics</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">{{ discoverStore.stats.content_counts.total }}</div>
          <div class="stat-label">Total Content Items</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ discoverStore.stats.content_counts.flashcards }}</div>
          <div class="stat-label">Flashcards</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ discoverStore.stats.content_counts.stories }}</div>
          <div class="stat-label">Stories</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ discoverStore.stats.content_counts.images }}</div>
          <div class="stat-label">Images</div>
        </div>
      </div>
    </div>
    
    <p>
      <a href="https://github.com/yc3136/vocabloom" target="_blank" rel="noopener">View on GitHub</a>
    </p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useDiscoverStore } from '../stores/discover';

const discoverStore = useDiscoverStore();

onMounted(async () => {
  // Load stats for the About page
  await discoverStore.fetchStats();
});
</script>

<style scoped>
.about-container {
  max-width: 800px;
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
  margin-bottom: 1rem;
}

h2 {
  color: var(--text-primary);
  font-weight: 600;
  margin: 2rem 0 1rem 0;
}

p {
  margin-bottom: 1rem;
  line-height: 1.6;
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

.stats-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-top: 1rem;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .about-container {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style> 