<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { marked } from 'marked'
import { useAuthStore } from '../stores/auth'
import { useFlashcardStore } from '../stores/flashcards'
import { usePreferencesStore } from '../stores/preferences'
import { useTranslationStore } from '../stores/translations'
import { useQuotaStore } from '../stores/quota'
import { useNotificationStore } from '../stores/notification'
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE } from '../constants/languages'
import StoryGenerationModal from './StoryGenerationModal.vue'
import ImageGenerationModal from './ImageGenerationModal.vue'

const term = ref('')
const selectedLanguage = ref(DEFAULT_LANGUAGE)
const translation = ref('')
const explanation = ref('')
const examples = ref<string[]>([])
const loading = ref(false)
const error = ref('')
const showStoryModal = ref(false)
const showImageModal = ref(false)

const authStore = useAuthStore()
const flashcardStore = useFlashcardStore()
const preferencesStore = usePreferencesStore()
const translationStore = useTranslationStore()
const quotaStore = useQuotaStore()
const notificationStore = useNotificationStore()

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES

// Combine translation, explanation, and examples into a single markdown response
const combinedResponse = computed(() => {
  if (!translation.value && !explanation.value && examples.value.length === 0) return ''
  
  let response = ''
  
  if (translation.value) {
    response += `**${translation.value}**\n\n`
  }
  
  if (explanation.value) {
    response += explanation.value
  }
  
  if (examples.value && examples.value.length > 0) {
    response += '\n\n**Examples:**\n'
    examples.value.forEach((example, index) => {
      response += `${index + 1}. ${example}\n`
    })
  }
  
  return response
})

// Render markdown to HTML
const renderedResponse = computed(() => {
  if (!combinedResponse.value) return ''
  return marked(combinedResponse.value)
})

// Computed property to ensure word is properly captured for story generation
const storyWords = computed(() => {
  return term.value ? [term.value] : []
})

async function lookup() {
  if (!term.value) return
  loading.value = true
  translation.value = ''
  explanation.value = ''
  examples.value = []
  error.value = ''
  
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    
    // Add auth token if user is logged in
    if (authStore.isAuthenticated) {
      const token = await authStore.getIdToken();
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Get user's child age from preferences for age-appropriate examples
    const childAge = preferencesStore.preferences?.child_age || null;
    
    const res = await fetch(`${API_BASE}/api/translate`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ 
        term: term.value,
        language: selectedLanguage.value,
        child_age: childAge
      })
    })
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    
    const data = await res.json()
    translation.value = data.translation || 'No translation available'
    explanation.value = data.explanation || 'No explanation available'
    // Store examples for flashcard creation
    examples.value = data.examples || []
    
    // Save translation to user's history if authenticated
    if (authStore.isAuthenticated && translation.value && translation.value !== 'No translation available') {
      try {
        await translationStore.saveTranslation({
          original_term: term.value,
          target_language: selectedLanguage.value,
          translation: translation.value,
          explanation: explanation.value
        })
      } catch (error) {
        console.error('Failed to save translation to history:', error)
        // Don't show error to user as this is not critical
      }
    }
  } catch (e) {
    error.value = 'Error contacting backend. Please try again.'
    console.error('Translation error:', e)
  } finally {
    loading.value = false
  }
}

function openStoryModal() {
  // Check if user is authenticated
  if (!authStore.requireAuth('generate stories')) {
    return
  }
  
  if (!term?.value?.trim()) {
    notificationStore.error('Please enter a word first to generate a story!')
    return
  }
  
  if (!selectedLanguage.value) {
    notificationStore.error('Please select a language first to generate a story!')
    return
  }
  
  // Check quota before opening modal
  if (!quotaStore.hasQuota('story')) {
    const quota = quotaStore.getQuota('story')
    if (quota) {
      notificationStore.warning(`Daily story generation limit reached! You have used ${quota.used}/${quota.limit} stories today. Please try again tomorrow.`)
    } else {
      notificationStore.warning('Daily story generation limit reached. Please try again tomorrow.')
    }
    return
  }
  
  console.log('Opening story modal with language:', selectedLanguage.value)
  showStoryModal.value = true
}

function closeStoryModal() {
  showStoryModal.value = false
}

function handleStorySave(story: any) {
  // Story saved successfully
  console.log('Story saved:', story)
}

function openImageModal() {
  // Check if user is authenticated
  if (!authStore.requireAuth('generate images')) {
    return
  }
  
  if (!term?.value?.trim()) {
    notificationStore.error('Please enter a word first to generate an image!')
    return
  }
  
  if (!selectedLanguage.value) {
    notificationStore.error('Please select a language first to generate an image!')
    return
  }
  
  // Debug quota check
  console.log('Quota check - quotas:', quotaStore.quotas)
  console.log('Quota check - hasQuota image:', quotaStore.hasQuota('image'))
  console.log('Quota check - getQuota image:', quotaStore.getQuota('image'))
  
  // Check quota before opening modal
  if (!quotaStore.hasQuota('image')) {
    const quota = quotaStore.getQuota('image')
    console.log('Quota exceeded - quota:', quota)
    if (quota) {
      notificationStore.warning(`Daily image generation limit reached! You have used ${quota.used}/${quota.limit} images today. Please try again tomorrow.`)
    } else {
      notificationStore.warning('Daily image generation limit reached. Please try again tomorrow.')
    }
    return
  }
  
  console.log('Opening image modal with language:', selectedLanguage.value)
  showImageModal.value = true
}

function closeImageModal() {
  showImageModal.value = false
}

function handleImageSave(image: any) {
  // Image saved successfully
  console.log('Image saved:', image)
}

async function createFlashcard() {
  if (!authStore.requireAuth('create flashcards')) {
    return
  }

  loading.value = true
  error.value = ''

  try {
    const flashcardData = {
      original_word: term.value,
      translated_word: translation.value,
      target_language: selectedLanguage.value,
      example_sentences: examples.value,
      colors: { primary: '#6690ff', secondary: '#64748b' }
    }

    await flashcardStore.createFlashcard(flashcardData)
    // Flashcard created successfully
  } catch (e) {
    error.value = 'Error creating flashcard. Please try again.'
    console.error('Flashcard creation error:', e)
  } finally {
    loading.value = false
  }
}



// Close dropdown when clicking outside
function handleClickOutside(event: Event) {
  // No longer needed since we removed the dropdown
}

// Load user preferences and set default language
onMounted(async () => {
  console.log('HomePage mounted, initial selectedLanguage:', selectedLanguage.value)
  if (authStore.isAuthenticated) {
    await preferencesStore.loadPreferences()
    await quotaStore.loadQuotas()
    // Set the selected language to user's preferred language if available
    if (preferencesStore.preferredLanguage) {
      selectedLanguage.value = preferencesStore.preferredLanguage
      console.log('Set selectedLanguage from preferences:', selectedLanguage.value)
    }
  }
  console.log('Final selectedLanguage after mount:', selectedLanguage.value)
})

// Watch for authentication changes to load preferences
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await preferencesStore.loadPreferences()
    await quotaStore.loadQuotas()
    // Set the selected language to user's preferred language if available
    if (preferencesStore.preferredLanguage) {
      selectedLanguage.value = preferencesStore.preferredLanguage
    }
  } else {
    quotaStore.clearQuotas()
  }
})

// Watch for changes in selected language and update preferences if user is authenticated
watch(selectedLanguage, async (newLanguage) => {
  console.log('Language changed to:', newLanguage)
  if (authStore.isAuthenticated && preferencesStore.preferences.preferred_languages) {
    try {
      // Update the first preferred language
      const currentLanguages = [...(preferencesStore.preferences.preferred_languages || [])]
      if (currentLanguages.length > 0) {
        currentLanguages[0] = newLanguage
      } else {
        currentLanguages.push(newLanguage)
      }
      await preferencesStore.updatePreferredLanguages(currentLanguages)
    } catch (error) {
      console.error('Failed to update preferred languages:', error)
      // Don't show error to user as this is not critical
    }
  }
})
</script>

<template>
  <div class="home-container" @click="handleClickOutside">    
    <div class="input-group">
      <input
        v-model="term"
        placeholder="Enter a word or phrase"
        class="term-input"
        @keyup.enter="lookup"
      />
      
      <select 
        v-model="selectedLanguage" 
        class="language-select"
      >
        <option v-for="lang in languages" :key="lang.value" :value="lang.value">
          {{ lang.label }}
        </option>
      </select>
    </div>
    
    <button 
      @click="lookup" 
      :disabled="loading || !term.trim()"
      class="lookup-btn"
    >
      {{ loading ? 'Looking up...' : 'Look Up' }}
    </button>
    
    <div v-if="error" class="error-box">
      <p>{{ error }}</p>
    </div>
    
    <div v-if="renderedResponse" class="response-container">
      <div class="response-box">
        <!-- Create Content Buttons -->
        <div class="create-buttons-container">
          <button 
            @click="openStoryModal" 
            class="create-btn story-btn"
            title="Generate a story with this word"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </svg>
            <span class="btn-text">Story</span>
          </button>
          
                  <button @click="createFlashcard" class="create-btn flashcard-btn">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <path d="M8 12h8"/>
            <path d="M8 16h8"/>
            <path d="M8 8h8"/>
          </svg>
          <span class="btn-text">Flashcard</span>
        </button>
          
          <button 
            @click="openImageModal" 
            class="create-btn image-btn"
            title="Generate an image for this word"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21,15 16,10 5,21"/>
            </svg>
            <span class="btn-text">Image</span>
          </button>
        </div>
        
        <div class="response-content" v-html="renderedResponse"></div>
      </div>
    </div>

    <!-- Story Generation Modal -->
    <StoryGenerationModal 
      v-if="showStoryModal"
      :show="showStoryModal" 
      :words="storyWords" 
      :translation="translation"
      :targetLanguage="selectedLanguage"
      @close="closeStoryModal" 
      @save="handleStorySave" 
    />

    <!-- Image Generation Modal -->
    <ImageGenerationModal 
      v-if="showImageModal"
      :show="showImageModal" 
      :originalWord="term"
      :translatedWord="translation"
      :targetLanguage="selectedLanguage"
      @close="closeImageModal" 
    />
  </div>
</template>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  color: var(--text-primary);
  background: var(--bg-surface);
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(30, 34, 90, 0.07);
  padding: 2rem 2rem 2.5rem 2rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 2rem;
}

.input-group {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  align-items: center;
}

@media (max-width: 768px) {
  .input-group {
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1.5rem;
  }
  
  .term-input {
    flex: none;
    width: 100%;
  }
  
  .language-select {
    flex: none;
    width: 100%;
  }
  
  .home-container {
    margin-top: 1rem;
    padding: 1.5rem 1rem 2rem 1rem;
    max-width: 100%;
    margin-left: 1rem;
    margin-right: 1rem;
  }
  
  .subtitle {
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
  }
  
  .lookup-btn {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    width: 100%;
  }
  
  .create-buttons-container {
    flex-wrap: nowrap;
    gap: 0.25rem;
    margin-bottom: 0.75rem;
  }
  
  .create-btn {
    padding: 0.4rem 0.5rem;
    font-size: 0.75rem;
    min-width: 0;
    flex: 0 0 auto;
  }
  
  .btn-text {
    font-size: 0.75rem;
  }
  
  .btn-icon {
    width: 14px;
    height: 14px;
  }
}

.term-input {
  flex: 2;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  background: var(--bg-surface);
  color: var(--text-primary);
  transition: border 0.2s;
}

.term-input:focus {
  border: 1.5px solid var(--primary-blue);
  outline: none;
}

.language-select {
  flex: 1;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e2e8f0);
  font-size: 1rem;
  background: var(--bg-surface, #ffffff);
  color: var(--text-primary, #1e293b);
  cursor: pointer;
}

.lookup-btn {
  margin-top: 1.5rem;
  padding: 0.75rem 2rem;
  background: var(--primary-blue, #6690ff);
  color: var(--bg-surface);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(102, 144, 255, 0.2);
  transition: background 0.2s, box-shadow 0.2s;
}

.lookup-btn:hover:not(:disabled) {
  background: var(--blue-hover, #4a7aff);
  box-shadow: 0 4px 16px rgba(102, 144, 255, 0.3);
}

.lookup-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-box {
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--error-red, #f87171);
  color: var(--bg-surface);
  border-radius: 8px;
  text-align: left;
}

.response-container {
  margin-top: 2rem;
  text-align: left;
  position: relative;
}

.response-box {
  background: var(--bg-primary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 1.5rem;
  line-height: 1.6;
  color: var(--text-primary, #1e293b);
}

.response-content {
  line-height: 1.6;
  color: var(--text-primary, #1e293b);
}

.create-buttons-container {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 6px;
  cursor: pointer;
  background: var(--bg-surface, #ffffff);
  transition: all 0.2s ease;
  color: var(--text-secondary, #64748b);
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  min-width: 0;
  flex-shrink: 0;
}

.create-btn:hover {
  border-color: var(--primary-blue, #6690ff);
  background: var(--primary-blue, #6690ff);
  color: var(--bg-surface);
}

.create-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: var(--border-color, #e2e8f0);
  background: var(--bg-surface, #ffffff);
  color: var(--text-secondary, #64748b);
}

.create-btn:disabled:hover {
  border-color: var(--border-color, #e2e8f0);
  background: var(--bg-surface, #ffffff);
  color: var(--text-secondary, #64748b);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-text {
  font-weight: 500;
}

/* Button-specific hover colors */
.story-btn:hover {
  border-color: var(--premium-purple);
  background: var(--premium-purple);
}

.flashcard-btn:hover {
  border-color: var(--success-green);
  background: var(--success-green);
}

.image-btn:hover {
  border-color: var(--warning-amber);
  background: var(--warning-amber);
}


</style>