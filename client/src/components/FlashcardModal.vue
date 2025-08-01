<template>
  <div class="flashcard-modal-overlay" v-if="show" @click="closeModal">
    <div class="flashcard-modal" @click.stop>
      <div class="modal-header">
        <h2>{{ props.initialData?.id ? 'Edit Flashcard' : 'Create Flashcard' }}</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-content">
        <!-- Flashcard Preview/Editor -->
        <div class="flashcard-section">
          <FlipCard
            :front-content="flashcard.original_word"
            :back-content="{
              translation: flashcard.translated_word,
              examples: flashcard.example_sentences
            }"
            :editable="true"
            @update:front-content="updateOriginalWord"
            @update:back-content="updateBackContent"
          />
        </div>
        
        <!-- Action Buttons -->
        <div class="action-buttons">
          <button 
            type="button" 
            class="btn-secondary" 
            @click="closeModal"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn-primary" 
            @click="handleSubmit"
            :disabled="flashcardStore.loading || !authStore.isFirebaseConfigured || !isValid"
          >
            {{ flashcardStore.loading ? 'Loading...' : (props.initialData?.id ? 'Update Flashcard' : 'Create Flashcard') }}
          </button>
        </div>
        
        <!-- Error Message -->
        <div class="error-message" v-if="flashcardStore.error">
          {{ flashcardStore.error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useFlashcardStore } from '../stores/flashcards';
import { useAuthStore } from '../stores/auth';
import FlipCard from './FlipCard.vue';

interface Props {
  show: boolean;
  initialData?: {
    id?: number;
    original_word: string;
    translated_word: string;
    target_language?: string;
    example_sentences?: string[];
  };
}

interface Emits {
  (e: 'close'): void;
  (e: 'success'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const flashcardStore = useFlashcardStore();
const authStore = useAuthStore();

const flashcard = ref({
  original_word: '',
  translated_word: '',
  target_language: '',
  example_sentences: [] as string[],
  colors: { primary: '#6690ff', secondary: '#64748b' }
});

// Validation computed property
const isValid = computed(() => {
  return flashcard.value.original_word.trim() !== '' && 
         flashcard.value.translated_word.trim() !== '';
});

// Update functions for two-way binding
const updateOriginalWord = (value: string) => {
  flashcard.value.original_word = value;
};

const updateBackContent = (value: { translation: string, examples: string[] }) => {
  flashcard.value.translated_word = value.translation;
  flashcard.value.example_sentences = value.examples;
};

// Initialize with props data
watch(() => props.initialData, (newData) => {
  if (newData) {
    flashcard.value.original_word = newData.original_word;
    flashcard.value.translated_word = newData.translated_word;
    flashcard.value.target_language = newData.target_language || '';
    if (newData.example_sentences) {
      flashcard.value.example_sentences = [...newData.example_sentences];
    } else {
      flashcard.value.example_sentences = [];
    }
  } else {
    // Reset to empty state
    flashcard.value = {
      original_word: '',
      translated_word: '',
      target_language: '',
      example_sentences: [],
      colors: { primary: '#6690ff', secondary: '#64748b' }
    };
  }
}, { immediate: true });

const closeModal = () => {
  emit('close');
  // Reset form
  flashcard.value = {
    original_word: '',
    translated_word: '',
    target_language: '',
    example_sentences: [],
    colors: { primary: '#6690ff', secondary: '#64748b' }
  };
  flashcardStore.error = null;
};

const handleSubmit = async () => {
  if (!isValid.value) return;
  
  try {
    if (props.initialData?.id) {
      // Update existing flashcard
      await flashcardStore.updateFlashcard(props.initialData.id, flashcard.value);
    } else {
      // Create new flashcard
      await flashcardStore.createFlashcard(flashcard.value);
    }
    emit('success');
    closeModal();
  } catch (error) {
    console.error('Flashcard operation error:', error);
  }
};
</script>

<style scoped>
.flashcard-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.flashcard-modal {
  background: var(--bg-surface);
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary, #1e293b);
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary, #64748b);
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: var(--bg-primary, #f8fafc);
  color: var(--text-primary, #1e293b);
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.flashcard-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 350px;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary-blue, #6690ff);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--blue-hover, #4a7aff);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: var(--text-secondary, #64748b);
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--text-secondary, #64748b);
  color: white;
}

.btn-secondary:hover {
  background: var(--text-primary, #1e293b);
  transform: translateY(-1px);
}

.error-message {
  color: var(--error-red, #f87171);
  font-size: 0.875rem;
  text-align: center;
  padding: 0.75rem;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(248, 113, 113, 0.2);
}

/* Responsive design */
@media (max-width: 768px) {
  .flashcard-modal {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .modal-header h2 {
    font-size: 1.25rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style> 