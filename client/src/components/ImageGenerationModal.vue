<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Generate Image</h2>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- Input Section -->
        <div class="input-section">
          <div class="form-group">
            <label for="customInstructions" class="form-label">Custom Instructions (Optional)</label>
            <textarea 
              v-model="imageParams.customInstructions" 
              id="customInstructions" 
              class="form-input" 
              rows="3"
              placeholder="Add any specific instructions for the image generation..."
            ></textarea>
          </div>
          
          <div class="form-group">
            
            <!-- Word pair, language, and age info row -->
            <div class="info-row">
              <!-- Word pair display -->
              <div class="words-display">
                <div class="word-pair">
                  <span class="word-pair__original">{{ props.originalWord }}</span>
                  <span class="word-pair__divider">/</span>
                  <span class="word-pair__translation">{{ props.translatedWord }}</span>
                </div>
              </div>
              
              <!-- Language badge -->
              <div class="badge badge--language">{{ props.targetLanguage }}</div>
              
              <!-- Age-appropriate indicator -->
              <div v-if="childAge" class="age-indicator">
                <span class="badge badge--age">
                  For {{ childAge }} year old
                </span>
              </div>
            </div>
          </div>
          

          
          <!-- Error Section -->
          <div v-if="error" class="error-section">
            <p class="error-message">{{ error }}</p>
            <button @click="clearError" class="retry-btn">Try Again</button>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn--secondary">Cancel</button>
          <button 
            @click="generateImage" 
            :disabled="generating"
            class="btn btn--primary"
          >
            {{ generating ? 'Starting...' : 'Generate Image' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useImageStore } from '../stores/images'
import { usePreferencesStore } from '../stores/preferences'
import { useNotificationStore } from '../stores/notification'

interface Props {
  show: boolean
  originalWord: string
  translatedWord: string
  targetLanguage: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const imageStore = useImageStore()
const preferencesStore = usePreferencesStore()
const notificationStore = useNotificationStore()

const imageParams = ref({
  customInstructions: ''
})

const generating = ref(false)
const error = ref('')

// Get child age from preferences
const childAge = computed(() => preferencesStore.preferences?.child_age || null)

const closeModal = () => {
  emit('close')
}

const clearError = () => {
  error.value = ''
  imageStore.clearError()
}

const generateImage = async () => {
  if (!props.originalWord || !props.translatedWord) {
    error.value = 'Missing word or translation'
    return
  }

  generating.value = true
  error.value = ''

  try {
    const result = await imageStore.generateImage({
      original_word: props.originalWord,
      translated_word: props.translatedWord,
      target_language: props.targetLanguage,
      custom_instructions: imageParams.value.customInstructions || undefined,
      child_age: childAge.value || undefined
    })

    if (result) {
      // Success - close modal immediately and show toast
      closeModal()
      notificationStore.success(
        `Image generation started for "${props.originalWord}"! Check My Images page for progress.`,
        { duration: 4000 }
      )
    } else {
      error.value = 'Failed to start image generation'
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to generate image'
    
    // Check if it's a quota error and show as warning
    if (errorMessage.includes('limit reached') || errorMessage.includes('quota')) {
      error.value = `⚠️ ${errorMessage}`
    } else {
      error.value = errorMessage
    }
  } finally {
    generating.value = false
  }
}

// Watch for store errors
watch(() => imageStore.error, (newError) => {
  if (newError) {
    error.value = newError
  }
})

// Reset form when modal opens
watch(() => props.show, (show) => {
  if (show) {
    imageParams.value = {
      customInstructions: ''
    }
    error.value = ''
    generating.value = false
  }
})
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  background: var(--bg-surface);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.input-section {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
  background: var(--bg-surface);
  color: var(--text-primary);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(102, 144, 255, 0.1);
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.words-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-start;
}

.word-chip {
  display: inline-block;
  padding: 0.5rem 0.75rem;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  height: 32px;
  line-height: 1;
  display: flex;
  align-items: center;
}

.word-chip.selected {
  background: var(--primary-blue);
  color: var(--bg-surface);
  border-color: var(--primary-blue);
}

.language-badge {
  display: inline-flex;
  align-items: center;
  background: var(--primary-blue);
  color: var(--bg-surface);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  height: 32px;
  line-height: 1;
}

.age-indicator {
  display: flex;
  align-items: center;
}

.age-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 400;
}

.generation-status {
  text-align: center;
  padding: 32px 16px;
}

.loading-spinner {
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

.status-note {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-top: 8px;
}

.error-section {
  text-align: center;
  padding: 24px;
  background: var(--bg-primary);
  border: 1px solid var(--error-red);
  border-radius: 8px;
  margin-bottom: 16px;
}

.error-message {
  color: var(--error-red);
  margin-bottom: 16px;
}

.retry-btn {
  background: var(--error-red);
  color: var(--bg-surface);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: var(--error-red);
  opacity: 0.8;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px 24px;
  border-top: 1px solid var(--border-color);
}

.cancel-btn {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-primary);
  border-color: var(--text-secondary);
}

.generate-btn {
  background: var(--primary-blue);
  color: var(--bg-surface);
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: var(--blue-hover);
}

.generate-btn:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style> 