<template>
  <div class="flashcard-dashboard">
    <div class="dashboard-header">
      <h2>My Flashcards</h2>
      <button @click="showCreateModal = true" class="create-btn">
        <span class="icon">➕</span>
        Create Flashcard
      </button>
    </div>

    <div v-if="flashcardStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading flashcards...</p>
    </div>

    <div v-else-if="flashcardStore.error" class="error-state">
      <p>Error: {{ flashcardStore.error }}</p>
      <button @click="loadFlashcards" class="retry-btn">Retry</button>
    </div>

    <div v-else-if="flashcardStore.flashcards.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No flashcards yet</h3>
      <p>Create your first flashcard to start learning!</p>
      <button @click="showCreateModal = true" class="create-btn">
        Create Your First Flashcard
      </button>
    </div>

    <div v-else class="flashcards-grid">
      <div 
        v-for="flashcard in flashcardStore.flashcards" 
        :key="flashcard.id" 
        class="flashcard-item"
        @click="selectFlashcard(flashcard)"
      >
        <div class="flashcard-content">
          <div class="flashcard-header">
            <h3>{{ flashcard.original_word }}</h3>
            <div class="flashcard-actions">
              <button @click.stop="editFlashcard(flashcard)" class="action-btn edit-btn">
                ✏️
              </button>
              <button @click.stop="deleteFlashcard(flashcard.id)" class="action-btn delete-btn">
                🗑️
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
            <span class="template-badge">{{ flashcard.template }}</span>
            <span class="date">{{ formatDate(flashcard.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <FlashcardModal 
      :show="showCreateModal || showEditModal"
      :initial-data="editingFlashcard"
      @close="closeModal"
      @success="handleFlashcardSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useFlashcardStore } from '../stores/flashcards';
import FlashcardModal from './FlashcardModal.vue';

const flashcardStore = useFlashcardStore();
const showCreateModal = ref(false);
const showEditModal = ref(false);
const editingFlashcard = ref(null);

onMounted(() => {
  loadFlashcards();
});

const loadFlashcards = async () => {
  try {
    await flashcardStore.fetchFlashcards();
  } catch (error) {
    console.error('Failed to load flashcards:', error);
  }
};

const selectFlashcard = (flashcard: any) => {
  // For now, just log the selection. Could be used for preview/study mode later
  console.log('Selected flashcard:', flashcard);
};

const editFlashcard = (flashcard: any) => {
  editingFlashcard.value = {
    id: flashcard.id,
    original_word: flashcard.original_word,
    translated_word: flashcard.translated_word,
    example_sentences: flashcard.example_sentences,
    template: flashcard.template,
    colors: flashcard.colors
  };
  showEditModal.value = true;
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
  showCreateModal.value = false;
  showEditModal.value = false;
  editingFlashcard.value = null;
};

const handleFlashcardSuccess = () => {
  closeModal();
  // The store will automatically update the flashcards list
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
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
  color: #333;
  font-size: 28px;
  font-weight: 700;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background: #0056b3;
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
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state p {
  color: #dc3545;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #6c757d;
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
  color: #333;
}

.empty-state p {
  color: #666;
  margin-bottom: 24px;
}

.flashcards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.flashcard-item {
  background: white;
  border: 1px solid #e9ecef;
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
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.flashcard-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: #e3f2fd;
}

.delete-btn:hover {
  background: #ffebee;
}

.flashcard-translation {
  font-size: 18px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.flashcard-examples {
  margin-bottom: 16px;
}

.example-sentence {
  font-size: 14px;
  color: #888;
  font-style: italic;
  margin-bottom: 4px;
  line-height: 1.4;
}

.more-examples {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.flashcard-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.template-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.date {
  color: #999;
}
</style> 