<template>
  <div class="flashcard-dashboard">
    <div v-if="flashcardStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading flashcards...</p>
    </div>

    <div v-else-if="flashcardStore.error" class="error-state">
      <p>Error: {{ flashcardStore.error }}</p>
      <button @click="loadFlashcards" class="retry-btn">Retry</button>
    </div>

    <div v-else-if="flashcards.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No flashcards yet</h3>
      <p>Create your first flashcard from the homepage!</p>
    </div>

    <div v-else class="flashcards-grid">
      <div 
        v-for="flashcard in flashcards" 
        :key="flashcard.id" 
        class="flashcard-item"
        @click="selectFlashcard(flashcard)"
      >
        <div class="flashcard-content">
          <div class="flashcard-header">
            <h3>{{ flashcard.original_word }}</h3>
            <div class="flashcard-actions">
              <button 
                @click.stop="deleteFlashcard(flashcard.id)" 
                class="remove-btn"
                title="Delete flashcard"
              >
                ×
              </button>
            </div>
          </div>
          <div class="flashcard-translation">{{ flashcard.translated_word }}</div>
          <div v-if="flashcard.example_sentences?.length" class="flashcard-examples">
            <div v-for="sentence in flashcard.example_sentences.slice(0, 2)" :key="sentence" class="example-sentence">
              {{ sentence }}
            </div>
            <div v-if="flashcard.example_sentences.length > 2" class="more-examples">
              +{{ flashcard.example_sentences.length - 2 }} more
            </div>
          </div>
          <div class="flashcard-meta">
            <span class="badge badge--language">{{ flashcard.target_language || 'Language' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Flashcard Viewer -->
    <FlashcardViewer
      v-if="showViewer"
      :show="showViewer"
      :flashcard="viewingFlashcard"
      @close="closeModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useFlashcardStore } from '../stores/flashcards';
import { useAuthStore } from '../stores/auth';
import FlashcardViewer from './FlashcardViewer.vue';

const route = useRoute();
const flashcardStore = useFlashcardStore();
const authStore = useAuthStore();
const showViewer = ref(false);
const viewingFlashcard = ref<any>(null);

// Computed property to ensure reactivity
const flashcards = computed(() => {
  return flashcardStore.flashcards;
});

// Simple function to load flashcards
const loadFlashcards = async () => {
  if (!authStore.isAuthenticated) {
    return;
  }
  
  try {
    await flashcardStore.fetchFlashcards();
  } catch (error) {
    console.error('Failed to load flashcards:', error);
  }
};

// Always load flashcards when entering the page
watch(() => route.path, (newPath) => {
  if (newPath === '/flashcards' && authStore.isAuthenticated) {
    loadFlashcards();
  }
}, { immediate: true });

// Watch for authentication state changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && route.path === '/flashcards') {
    loadFlashcards();
  }
}, { immediate: true });

// Also load on mount as backup
onMounted(() => {
  if (authStore.isAuthenticated && route.path === '/flashcards') {
    loadFlashcards();
  }
});

// Watch for changes in the store
watch(() => flashcardStore.flashcards, () => {
  // Flashcards updated
}, { deep: true });

const selectFlashcard = (flashcard: any) => {
  viewingFlashcard.value = flashcard;
  showViewer.value = true;
};

const deleteFlashcard = async (id: number) => {
  if (confirm('Are you sure you want to delete this flashcard?')) {
    try {
      await flashcardStore.deleteFlashcard(id);
    } catch (error) {
      console.error('Failed to delete flashcard:', error);
    }
  }
};

const closeModal = () => {
  showViewer.value = false;
  viewingFlashcard.value = null;
};


</script>

<style scoped>
.flashcard-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 28px;
  font-weight: 700;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state p {
  color: var(--error-red);
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: var(--text-secondary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-state .empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.flashcards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.flashcard-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.flashcard-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.flashcard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.flashcard-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
}

.flashcard-actions {
  display: flex;
  gap: 8px;
}

.remove-btn {
  background: none;
  border: none;
  color: #a0aec0;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1;
}

.remove-btn:hover {
  background: #e2e8f0;
  color: #e53e3e;
}

.flashcard-translation {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
}

.flashcard-examples {
  margin-bottom: 16px;
}

.example-sentence {
  font-size: 14px;
  color: var(--text-secondary);
  font-style: italic;
  margin-bottom: 4px;
  line-height: 1.4;
}

.more-examples {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

.flashcard-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.template-badge {
  background: rgba(102, 144, 255, 0.1);
  color: var(--primary-blue);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  text-transform: capitalize;
}


</style> 