<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Generate Story</h2>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- Input Section -->
        <div class="input-section">
          <div class="form-row">
            <div class="form-group">
              <label for="theme">Theme (Optional)</label>
              <select v-model="storyParams.theme" id="theme" class="form-input">
                <option value="adventure">Adventure</option>
                <option value="educational">Educational</option>
                <option value="bedtime">Bedtime</option>
                <option value="fantasy">Fantasy</option>
                <option value="nature">Nature</option>
                <option value="friendship">Friendship</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="maxWords">Max Words</label>
              <input 
                v-model.number="storyParams.maxWords" 
                id="maxWords" 
                type="number" 
                class="form-input" 
                min="50" 
                max="500" 
                placeholder="100"
              />
            </div>
          </div>
          
          <div v-if="storyParams.theme === 'custom'" class="form-group">
            <label for="customTheme">Custom Theme</label>
            <input 
              v-model="storyParams.customTheme" 
              id="customTheme" 
              class="form-input" 
              placeholder="Enter your custom theme..."
            />
          </div>
          
          <div class="form-group">
            <label for="customPrompt">Custom Instructions (Optional)</label>
            <textarea 
              v-model="storyParams.customPrompt" 
              id="customPrompt" 
              class="form-input" 
              rows="2"
              placeholder="Add any specific instructions..."
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Words to Include</label>
            <div class="words-display">
              <span v-for="word in props.words" :key="word" class="word-tag original-word">
                {{ word }}
              </span>
              <span v-if="props.translation" class="word-tag translated-word">
                {{ props.translation }}
              </span>
            </div>
          </div>
          
          <!-- Age-appropriate indicator -->
          <div v-if="childAge" class="age-indicator">
            <span class="age-badge">
              For {{ childAge }} year old
            </span>
          </div>
        </div>
        
        <!-- Generated Story Section -->
        <div v-if="generatedStory" class="story-section">
          <h3>Generated Story</h3>
          <div class="story-content" v-html="renderedStory"></div>
        </div>
        
        <!-- Loading State -->
        <div v-if="generating" class="loading-section">
          <div class="loading-spinner"></div>
          <p>Generating your story...</p>
        </div>
        
        <!-- Error State -->
        <div v-if="error" class="error-section">
          <p class="error-message">{{ error }}</p>
        </div>
      </div>
      
      <div class="modal-footer">
        <button 
          @click="generateStory" 
          :disabled="generating || !canGenerate"
          class="btn btn-primary"
        >
          {{ generatedStory ? 'Regenerate' : 'Generate Story' }}
        </button>
        
        <button 
          v-if="generatedStory" 
          @click="saveStory" 
          :disabled="saving"
          class="btn btn-secondary"
        >
          {{ saving ? 'Saving...' : 'Save Story' }}
        </button>
        
        <button @click="closeModal" class="btn btn-cancel">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import { usePreferencesStore } from '../stores/preferences'

interface StoryParams {
  theme: string
  customTheme: string
  maxWords: number
  customPrompt: string
}

interface Props {
  show: boolean
  words: string[]
  translation?: string
  targetLanguage?: string
}

interface Emits {
  (e: 'close'): void
  (e: 'save', story: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const preferencesStore = usePreferencesStore()

const storyParams = ref<StoryParams>({
  theme: '',
  customTheme: '',
  maxWords: 100,
  customPrompt: ''
})

const generatedStory = ref('')
const generating = ref(false)
const saving = ref(false)
const error = ref('')

const canGenerate = computed(() => {
  return props.words.length > 0
})

const renderedStory = computed(() => {
  if (!generatedStory.value) return ''
  return marked(generatedStory.value)
})

// Get child's age from preferences
const childAge = computed(() => {
  return preferencesStore.preferences.child_age
})

// Get age range category from child's age
const ageRange = computed(() => {
  if (!childAge.value) return null
  
  if (childAge.value <= 3) return 'toddler'
  if (childAge.value <= 5) return 'preschool'
  if (childAge.value <= 10) return 'elementary'
  if (childAge.value <= 13) return 'middle_school'
  return 'elementary' // default fallback
})

const closeModal = () => {
  emit('close')
}

const generateStory = async () => {
  if (!canGenerate.value) return
  
  // Additional validation
  if (!props.words || props.words.length === 0) {
    error.value = 'No words provided for story generation.'
    return
  }
  
  generating.value = true
  error.value = ''
  
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    
    // Prepare words array with both original and translated words
    const wordsToInclude = [...props.words]
    if (props.translation && props.translation.trim()) {
      wordsToInclude.push(props.translation.trim())
    }
    
    const requestBody = {
      words: wordsToInclude,
      theme: storyParams.value.theme === 'custom' ? storyParams.value.customTheme : storyParams.value.theme,
      max_words: storyParams.value.maxWords,
      custom_prompt: storyParams.value.customPrompt || null,
      target_language: props.targetLanguage || null,
      age_range: ageRange.value || null,
      original_word: props.words[0] || null,
      translated_word: props.translation || null
    }
    
    console.log('Generating story with params:', requestBody)
    
    const response = await fetch(`${API_BASE}/api/stories/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Server error details:', errorData)
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    generatedStory.value = data.story_content
  } catch (e) {
    error.value = 'Failed to generate story. Please try again.'
    console.error('Story generation error:', e)
  } finally {
    generating.value = false
  }
}

const saveStory = async () => {
  if (!generatedStory.value) return
  
  saving.value = true
  
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    
    const response = await fetch(`${API_BASE}/api/stories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        original_words: props.words,
        story_title: `Story about ${props.words.join(', ')}`,
        story_content: generatedStory.value,
        story_theme: storyParams.value.theme === 'custom' ? storyParams.value.customTheme : storyParams.value.theme,
        story_length: storyParams.value.maxWords <= 100 ? 'short' : storyParams.value.maxWords <= 300 ? 'medium' : 'long',
        target_age_range: ageRange.value // Use ageRange.value
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    emit('save', data)
    closeModal()
  } catch (e) {
    error.value = 'Failed to save story. Please try again.'
    console.error('Story save error:', e)
  } finally {
    saving.value = false
  }
}

// Reset form when modal opens
watch(() => props.show, (show) => {
  if (show) {
    generatedStory.value = ''
    error.value = ''
    storyParams.value = {
      theme: '',
      customTheme: '',
      maxWords: 100,
      customPrompt: ''
    }
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--bg-surface, #ffffff);
  border-radius: 8px;
  max-width: 500px;
  max-height: 85vh;
  width: 90%;
  position: relative;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary, #1e293b);
  font-size: 1.125rem;
  font-weight: 600;
  text-align: left;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary, #64748b);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: var(--bg-primary, #f8fafc);
}

.modal-body {
  padding: 1rem 1.5rem;
  text-align: left;
  overflow-y: auto;
  flex: 1;
}

.input-section {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  text-align: left;
}

.form-group {
  flex: 1;
  margin-bottom: 0;
  text-align: left;
}

.form-group:not(.form-row .form-group) {
  margin-bottom: 1rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  font-size: 0.875rem;
  text-align: left;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--bg-surface, #ffffff);
  color: var(--text-primary, #1e293b);
  transition: border-color 0.2s;
  text-align: left;
}

.form-input option {
  font-weight: 600;
  color: var(--text-primary, #1e293b);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue, #6690ff);
}

.words-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  justify-content: flex-start;
}

.word-tag {
  display: inline-block;
  padding: 0.5rem 0.75rem;
  background: var(--primary-blue, #6690ff);
  color: white;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0.125rem;
}

.original-word {
  background: var(--primary-blue, #6690ff);
  font-size: 1rem;
  padding: 0.625rem 1rem;
}

.translated-word {
  background: var(--primary-orange, #e19f5d);
  font-size: 1rem;
  padding: 0.625rem 1rem;
}

.age-indicator {
  margin-top: 0.75rem;
  text-align: left;
}

.age-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: transparent;
  color: var(--text-secondary, #64748b);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 400;
}

.story-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  text-align: left;
}

.story-section h3 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary, #1e293b);
  font-size: 1rem;
  font-weight: 600;
  text-align: left;
}

.story-content {
  background: var(--bg-primary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 6px;
  padding: 0.75rem;
  line-height: 1.5;
  color: var(--text-primary, #1e293b);
  font-size: 0.875rem;
  text-align: left;
}

.loading-section {
  text-align: center;
  padding: 1.5rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color, #e2e8f0);
  border-top: 2px solid var(--primary-blue, #6690ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.75rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  margin-top: 0.75rem;
  text-align: left;
}

.error-message {
  color: var(--error-red, #f87171);
  background: #fef2f2;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #fecaca;
  font-size: 0.875rem;
  text-align: left;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  justify-content: flex-end;
  background: var(--bg-surface, #ffffff);
  border-radius: 0 0 8px 8px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-blue, #6690ff);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--blue-hover, #4a7aff);
}

.btn-secondary {
  background: var(--primary-orange, #e19f5d);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #d18f4d;
}

.btn-cancel {
  background: var(--bg-primary, #f8fafc);
  color: var(--text-primary, #1e293b);
  border: 1px solid var(--border-color, #e2e8f0);
}

.btn-cancel:hover {
  background: var(--border-color, #e2e8f0);
}
</style> 