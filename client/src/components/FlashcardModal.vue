<template>
  <div class="flashcard-modal-overlay" v-if="show" @click="closeModal">
    <div class="flashcard-modal" @click.stop>
      <div class="modal-header">
        <h2>{{ props.initialData?.id ? 'Edit Flashcard' : 'Create Flashcard' }}</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="flashcard-form">
        <div class="form-row">
          <div class="form-group">
            <label for="originalWord">Original Word</label>
            <input 
              type="text" 
              id="originalWord" 
              v-model="flashcard.original_word" 
              required 
              placeholder="Enter original word"
            />
          </div>
          
          <div class="form-group">
            <label for="translatedWord">Translated Word</label>
            <input 
              type="text" 
              id="translatedWord" 
              v-model="flashcard.translated_word" 
              required 
              placeholder="Enter translated word"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="exampleSentences">Example Sentences (one per line)</label>
          <textarea 
            id="exampleSentences" 
            v-model="exampleSentencesText" 
            placeholder="Enter example sentences, one per line"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="template">Template</label>
            <select id="template" v-model="flashcard.template">
              <option value="classic">Classic</option>
              <option value="modern">Modern</option>
              <option value="minimal">Minimal</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Color Scheme</label>
            <div class="color-options">
              <button 
                type="button"
                class="color-option" 
                :class="{ active: flashcard.colors?.primary === color.primary }"
                v-for="color in colorSchemes" 
                :key="color.name"
                @click="selectColorScheme(color)"
                :style="{ backgroundColor: color.primary }"
              >
                {{ color.name }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="preview-section">
          <h3>Preview</h3>
          <div class="flashcard-preview" :class="flashcard.template">
            <div class="preview-content">
              <div class="preview-original">{{ flashcard.original_word || 'Original Word' }}</div>
              <div class="preview-translation">{{ flashcard.translated_word || 'Translated Word' }}</div>
              <div class="preview-examples" v-if="flashcard.example_sentences?.length">
                <div v-for="sentence in flashcard.example_sentences" :key="sentence" class="preview-sentence">
                  {{ sentence }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="error-message" v-if="flashcardStore.error">
          {{ flashcardStore.error }}
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="closeModal">
            Cancel
          </button>
          <button type="submit" class="btn-primary" :disabled="flashcardStore.loading || !authStore.isFirebaseConfigured">
            {{ flashcardStore.loading ? 'Loading...' : (props.initialData?.id ? 'Update Flashcard' : 'Create Flashcard') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useFlashcardStore } from '../stores/flashcards';
import { useAuthStore } from '../stores/auth';

interface Props {
  show: boolean;
  initialData?: {
    id?: number;
    original_word: string;
    translated_word: string;
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
  example_sentences: [] as string[],
  template: 'classic',
  colors: { primary: '#6690ff', secondary: '#64748b' }
});

const exampleSentencesText = ref('');

const colorSchemes = [
  { name: 'Blue', primary: '#6690ff', secondary: '#64748b' },
  { name: 'Green', primary: '#4ade80', secondary: '#64748b' },
  { name: 'Purple', primary: '#a78bfa', secondary: '#64748b' },
  { name: 'Orange', primary: '#e19f5d', secondary: '#64748b' },
  { name: 'Red', primary: '#f87171', secondary: '#64748b' }
];

// Watch for changes in example sentences text
watch(exampleSentencesText, (newValue) => {
  flashcard.value.example_sentences = newValue
    .split('\n')
    .map(s => s.trim())
    .filter(s => s.length > 0);
});

// Initialize with props data
watch(() => props.initialData, (newData) => {
  if (newData) {
    flashcard.value.original_word = newData.original_word;
    flashcard.value.translated_word = newData.translated_word;
    if (newData.example_sentences) {
      flashcard.value.example_sentences = [...newData.example_sentences];
      exampleSentencesText.value = newData.example_sentences.join('\n');
    }
  }
}, { immediate: true });

const selectColorScheme = (color: typeof colorSchemes[0]) => {
  flashcard.value.colors = { primary: color.primary, secondary: color.secondary };
};

const closeModal = () => {
  emit('close');
  // Reset form
  flashcard.value = {
    original_word: '',
    translated_word: '',
    example_sentences: [],
    template: 'classic',
    colors: { primary: '#6690ff', secondary: '#64748b' }
  };
  exampleSentencesText.value = '';
  flashcardStore.error = null;
};

const handleSubmit = async () => {
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
  border-radius: 8px;
  padding: 24px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary, #1e293b);
  font-size: 24px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary, #64748b);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--text-primary, #1e293b);
}

.flashcard-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary, #1e293b);
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.2s;
  background: var(--bg-surface, #ffffff);
  color: var(--text-primary, #1e293b);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-blue, #6690ff);
}

.color-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-option {
  padding: 8px 12px;
  border: 2px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  transition: all 0.2s;
}

.color-option:hover {
  transform: translateY(-1px);
}

.color-option.active {
  border-color: var(--text-primary, #1e293b);
  transform: translateY(-1px);
}

.preview-section {
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 16px;
  background: var(--bg-primary, #f8fafc);
}

.preview-section h3 {
  margin: 0 0 16px 0;
  color: var(--text-primary, #1e293b);
  font-size: 16px;
}

.flashcard-preview {
  border: 2px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 20px;
  background: var(--bg-surface, #ffffff);
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flashcard-preview.classic {
  border-color: var(--primary-blue, #6690ff);
}

.flashcard-preview.modern {
  border-color: var(--success-green, #4ade80);
  border-radius: 12px;
}

.flashcard-preview.minimal {
  border-color: var(--text-secondary, #64748b);
  border-width: 1px;
}

.preview-content {
  text-align: center;
  width: 100%;
}

.preview-original {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  margin-bottom: 8px;
}

.preview-translation {
  font-size: 20px;
  color: var(--text-secondary, #64748b);
  margin-bottom: 12px;
}

.preview-examples {
  font-size: 14px;
  color: var(--text-secondary, #64748b);
}

.preview-sentence {
  margin-bottom: 4px;
  font-style: italic;
}

.error-message {
  color: var(--error-red, #f87171);
  font-size: 14px;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
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
}

.btn-primary:disabled {
  background: var(--text-secondary, #64748b);
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--text-secondary, #64748b);
  color: white;
}

.btn-secondary:hover {
  background: var(--text-primary, #1e293b);
}
</style> 