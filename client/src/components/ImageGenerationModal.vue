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
            <label for="title">Title (Optional)</label>
            <input 
              v-model="imageParams.title" 
              id="title" 
              class="form-input" 
              placeholder="Enter a title for your image..."
            />
          </div>
          
          <div class="form-group">
            <label for="customInstructions">Custom Instructions (Optional)</label>
            <textarea 
              v-model="imageParams.customInstructions" 
              id="customInstructions" 
              class="form-input" 
              rows="3"
              placeholder="Add any specific instructions for the image generation..."
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Image Details</label>
            
            <!-- Original word and translation -->
            <div class="image-details">
              <div class="word-pair">
                <span class="original-word">{{ props.originalWord }}</span>
                <span class="separator">→</span>
                <span class="translated-word">{{ props.translatedWord }}</span>
              </div>
              <div class="language-badge">{{ props.targetLanguage }}</div>
            </div>
          </div>
          
          <!-- Age-appropriate indicator -->
          <div v-if="childAge" class="age-indicator">
            <span class="age-badge">
              For {{ childAge }} year old
            </span>
          </div>
        </div>
        
        <!-- Generation Status Section -->
        <div v-if="generating" class="generation-status">
          <div class="loading-spinner"></div>
          <p>Starting image generation...</p>
          <p class="status-note">You can close this modal and check the status in My Images page.</p>
        </div>
        
        <!-- Error Section -->
        <div v-if="error" class="error-section">
          <p class="error-message">{{ error }}</p>
          <button @click="clearError" class="retry-btn">Try Again</button>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="closeModal" class="cancel-btn">Cancel</button>
        <button 
          @click="generateImage" 
          :disabled="generating"
          class="generate-btn"
        >
          {{ generating ? 'Starting Generation...' : 'Generate Image' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useImageStore } from '../stores/images'
import { usePreferencesStore } from '../stores/preferences'

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

const imageParams = ref({
  title: '',
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
      child_age: childAge.value || undefined,
      title: imageParams.value.title || undefined
    })

    if (result) {
      // Success - close modal after a short delay
      setTimeout(() => {
        closeModal()
      }, 2000)
    } else {
      error.value = 'Failed to start image generation'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to generate image'
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
      title: '',
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
  background: white;
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
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 16px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #374151;
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
  color: #374151;
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #6690ff;
  box-shadow: 0 0 0 3px rgba(102, 144, 255, 0.1);
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.image-details {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.word-pair {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.original-word {
  font-weight: 600;
  color: #111827;
  font-size: 1rem;
}

.separator {
  color: #6b7280;
  font-weight: 500;
}

.translated-word {
  font-weight: 600;
  color: #6690ff;
  font-size: 1rem;
}

.language-badge {
  display: inline-block;
  background: #6690ff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.age-indicator {
  margin-top: 16px;
}

.age-badge {
  display: inline-block;
  background: #10b981;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
}

.generation-status {
  text-align: center;
  padding: 32px 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #6690ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status-note {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 8px;
}

.error-section {
  text-align: center;
  padding: 24px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-bottom: 16px;
}

.error-message {
  color: #dc2626;
  margin-bottom: 16px;
}

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #b91c1c;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px 24px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.generate-btn {
  background: #6690ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: #5a7cff;
}

.generate-btn:disabled {
  background: #9ca3af;
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
  
  .word-pair {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .separator {
    display: none;
  }
}
</style> 