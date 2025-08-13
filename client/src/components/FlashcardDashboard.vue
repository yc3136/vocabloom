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

    <div v-else class="flashcards-content">
      <div class="flashcards-header">
        <div class="search-filters">
          <div class="search-box">
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Search by word, translation, or examples..."
              class="search-input"
            />
          </div>
          <div class="language-filter">
            <select v-model="selectedLanguage" class="language-select">
              <option value="">All Languages</option>
              <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                {{ lang.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="stats">
          <span class="stat-item">
            <strong>{{ filteredFlashcards.length }}</strong> flashcards
          </span>
        </div>
      </div>

      <div class="flashcards-grid">
        <div 
          v-for="flashcard in paginatedFlashcards" 
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
              <span class="badge badge--language">{{ getLanguageDisplay(flashcard.target_language) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-btn"
          :class="{ 'disabled': currentPage === 1 }"
        >
          ‹
        </button>
        
        <div class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </div>
        
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-btn"
          :class="{ 'disabled': currentPage === totalPages }"
        >
          ›
        </button>
      </div>
    </div>

    <!-- Flashcard Viewer -->
    <FlashcardViewer
      v-if="showViewer"
      :show="showViewer"
      :flashcard="viewingFlashcard"
      @close="closeModal"
    />

    <!-- Confirmation Modal -->
    <ConfirmationModal
      :show="showDeleteModal"
      title="Delete Flashcard"
      message="Are you sure you want to delete this flashcard?"
      type="danger"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
      @close="handleDeleteCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useFlashcardStore } from '../stores/flashcards';
import { useAuthStore } from '../stores/auth';
import { SUPPORTED_LANGUAGES } from '../constants/languages';
import FlashcardViewer from './FlashcardViewer.vue';
import ConfirmationModal from './ConfirmationModal.vue';

const route = useRoute();
const flashcardStore = useFlashcardStore();
const authStore = useAuthStore();
const showViewer = ref(false);
const viewingFlashcard = ref<any>(null);

// Search and filter state
const searchTerm = ref('');
const selectedLanguage = ref('');
const currentPage = ref(1);
const itemsPerPage = 12;

// Confirmation modal state
const showDeleteModal = ref(false);
const flashcardToDelete = ref<number | null>(null);

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES;

// Computed property to ensure reactivity
const flashcards = computed(() => {
  return flashcardStore.flashcards;
});

// Filtered flashcards based on search and language
const filteredFlashcards = computed(() => {
  let filtered = flashcards.value;
  
  // Filter by search term
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(flashcard => 
      flashcard.original_word.toLowerCase().includes(term) ||
      flashcard.translated_word.toLowerCase().includes(term) ||
      (flashcard.example_sentences && flashcard.example_sentences.some(sentence => 
        sentence.toLowerCase().includes(term)
      ))
    );
  }
  
  // Filter by language
  if (selectedLanguage.value) {
    filtered = filtered.filter(flashcard => 
      flashcard.target_language === selectedLanguage.value
    );
  }
  
  return filtered;
});

// Pagination
const totalPages = computed(() => {
  return Math.ceil(filteredFlashcards.value.length / itemsPerPage);
});

const paginatedFlashcards = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filteredFlashcards.value.slice(startIndex, endIndex);
});

// Helper function to get language display name
const getLanguageDisplay = (languageCode: string) => {
  const language = languages.find(lang => lang.value === languageCode);
  return language ? language.label : languageCode;
};

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

// Watch for filter changes to reset pagination
watch([searchTerm, selectedLanguage], () => {
  currentPage.value = 1;
});

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
  flashcardToDelete.value = id;
  showDeleteModal.value = true;
};

const handleDeleteConfirm = async () => {
  if (flashcardToDelete.value) {
    try {
      await flashcardStore.deleteFlashcard(flashcardToDelete.value);
    } catch (error) {
      console.error('Failed to delete flashcard:', error);
    }
    showDeleteModal.value = false;
    flashcardToDelete.value = null;
  }
};

const handleDeleteCancel = () => {
  showDeleteModal.value = false;
  flashcardToDelete.value = null;
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

.flashcards-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.search-filters {
  display: flex;
  gap: 12px;
  flex: 1;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.language-filter {
  min-width: 120px;
}

.search-input, .language-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  background: var(--bg-surface);
  color: var(--text-primary);
}

.search-input:focus, .language-select:focus {
  border-color: var(--primary-blue);
}

.language-select {
  cursor: pointer;
}

.stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-item strong {
  color: var(--text-primary);
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
  margin-bottom: 24px;
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
  color: var(--text-secondary);
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1;
}

.remove-btn:hover {
  background: var(--border-color);
  color: var(--error-red);
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

.badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.badge--language {
  background: var(--primary-blue);
  color: var(--bg-surface);
}

.template-badge {
  background: rgba(102, 144, 255, 0.1);
  color: var(--primary-blue);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

/* Pagination styles */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.pagination-btn {
  background: var(--primary-blue);
  color: var(--bg-surface);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background: var(--blue-hover);
}

.pagination-btn.disabled {
  background: var(--border-color);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .flashcards-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
  }
  
  .search-box {
    max-width: none;
  }
  
  .stats {
    justify-content: center;
  }
  
  .flashcards-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .pagination {
    flex-direction: row;
    gap: 8px;
    padding: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
    min-width: 80px;
  }
  
  .page-info {
    font-size: 0.8rem;
    white-space: nowrap;
  }
}
</style> 