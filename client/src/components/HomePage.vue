<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { marked } from 'marked'
import { useAuthStore } from '../stores/auth'
import { useFlashcardStore } from '../stores/flashcards'
import { usePreferencesStore } from '../stores/preferences'
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE } from '../constants/languages'

const term = ref('')
const selectedLanguage = ref(DEFAULT_LANGUAGE)
const translation = ref('')
const explanation = ref('')
const examples = ref<string[]>([])
const loading = ref(false)
const error = ref('')
const showCreateDropdown = ref(false)

const authStore = useAuthStore()
const flashcardStore = useFlashcardStore()
const preferencesStore = usePreferencesStore()

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES

// Content creation options
const contentTypes = [
  { id: 'flashcard', label: 'Flashcard', icon: '📚' }
]

// Combine translation and explanation into a single markdown response
const combinedResponse = computed(() => {
  if (!translation.value && !explanation.value) return ''
  
  let response = ''
  
  if (translation.value) {
    response += `**${translation.value}**\n\n`
  }
  
  if (explanation.value) {
    response += explanation.value
  }
  
  return response
})

// Render markdown to HTML
const renderedResponse = computed(() => {
  if (!combinedResponse.value) return ''
  return marked(combinedResponse.value)
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
    
    const res = await fetch(`${API_BASE}/api/translate`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ 
        term: term.value,
        language: selectedLanguage.value 
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
  } catch (e) {
    error.value = 'Error contacting backend. Please try again.'
    console.error('Translation error:', e)
  } finally {
    loading.value = false
  }
}

function toggleCreateDropdown() {
  showCreateDropdown.value = !showCreateDropdown.value
}

function createContent(type: string) {
  if (!authStore.isAuthenticated) {
    // Show authentication prompt
            alert('Please sign in to create content!')
    return
  }
  
  showCreateDropdown.value = false
  
  switch (type) {
    case 'flashcard':
      createFlashcard()
      break
    // Add more content types here in the future
    default:
      // Unknown content type
      break
  }
}

async function createFlashcard() {
  if (!authStore.isAuthenticated) {
            alert('Please sign in to create flashcards!')
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
  const target = event.target as HTMLElement
  if (!target.closest('.create-dropdown-container')) {
    showCreateDropdown.value = false
  }
}

// Load user preferences and set default language
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await preferencesStore.loadPreferences()
    // Set the selected language to user's preferred language if available
    if (preferencesStore.preferredLanguage) {
      selectedLanguage.value = preferencesStore.preferredLanguage
    }
  }
})

// Watch for authentication changes to load preferences
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await preferencesStore.loadPreferences()
    // Set the selected language to user's preferred language if available
    if (preferencesStore.preferredLanguage) {
      selectedLanguage.value = preferencesStore.preferredLanguage
    }
  }
})

// Watch for changes in selected language and update preferences if user is authenticated
watch(selectedLanguage, async (newLanguage) => {
  if (authStore.isAuthenticated && preferencesStore.preferences.preferred_languages) {
    // Update the first preferred language
    const currentLanguages = [...(preferencesStore.preferences.preferred_languages || [])]
    if (currentLanguages.length > 0) {
      currentLanguages[0] = newLanguage
    } else {
      currentLanguages.push(newLanguage)
    }
    await preferencesStore.updatePreferredLanguages(currentLanguages)
  }
})
</script>

<template>
  <div class="home-container" @click="handleClickOutside">
    <p class="subtitle">A simple tool to help you learn and understand new vocabulary with instant translations and explanations.</p>
    
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
    
    <button @click="lookup" :disabled="loading" class="lookup-btn">
      <span v-if="!loading">Look up</span>
      <span v-else>Looking up...</span>
    </button>
    
    <div v-if="error" class="error-box">
      <p>{{ error }}</p>
    </div>
    
    <div v-if="renderedResponse" class="response-container">
      <div class="response-box" v-html="renderedResponse"></div>
      
      <!-- Create Content Dropdown -->
      <div class="create-dropdown-container">
        <button @click="toggleCreateDropdown" class="create-content-btn">
          <span class="plus-icon">+</span>
          <span class="create-text">Create</span>
        </button>
        
        <div v-if="showCreateDropdown" class="create-dropdown">
          <div 
            v-for="contentType in contentTypes" 
            :key="contentType.id"
            @click="createContent(contentType.id)"
            class="dropdown-item"
          >
            <span class="item-icon">{{ contentType.icon }}</span>
            <span class="item-label">{{ contentType.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <!-- Removed as per edit hint -->
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
  color: #fff;
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
  color: #fff;
  border-radius: 8px;
  text-align: left;
}

.response-container {
  position: relative;
  margin-top: 1.5rem;
}

.response-box {
  background: var(--bg-primary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: left;
  line-height: 1.6;
  text-align: left;
}

/* Create Content Dropdown Styles */
.create-dropdown-container {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 10;
}

.create-content-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--primary-orange, #e19f5d);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s, transform 0.1s;
  box-shadow: 0 2px 4px rgba(225, 159, 93, 0.2);
}

.create-content-btn:hover {
  background: #d18f4d;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(225, 159, 93, 0.3);
}

.plus-icon {
  font-size: 1rem;
  font-weight: bold;
  line-height: 1;
}

.create-text {
  font-size: 0.875rem;
}

.create-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 140px;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: var(--bg-primary, #f8fafc);
}

.item-icon {
  font-size: 1rem;
}

.item-label {
  font-size: 0.875rem;
  color: var(--text-primary, #1e293b);
}

/* Markdown styling */
.response-box :deep(h2) {
  color: var(--text-primary, #1e293b);
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 2px solid var(--primary-blue, #6690ff);
  padding-bottom: 0.5rem;
}

.response-box :deep(h3) {
  color: var(--text-primary, #1e293b);
  margin: 1.5rem 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.response-box :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.response-box :deep(ul), .response-box :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.response-box :deep(li) {
  margin: 0.25rem 0;
  line-height: 1.5;
}

.response-box :deep(strong) {
  font-weight: 600;
  color: var(--text-primary, #1e293b);
}

.response-box :deep(code) {
  background: var(--border-color, #e2e8f0);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.response-box :deep(blockquote) {
  border-left: 4px solid var(--primary-blue, #6690ff);
  margin: 1rem 0;
  padding-left: 1rem;
  font-style: italic;
  color: var(--text-secondary, #64748b);
}

@media (max-width: 768px) {
  .input-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .term-input, .language-select {
    width: 100%;
  }
  
  .home-container {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .create-dropdown-container {
    top: 0.5rem;
    right: 0.5rem;
  }
  
  .create-content-btn {
    padding: 0.4rem 0.6rem;
    font-size: 0.8rem;
  }
  
  .create-text {
    display: none;
  }
}
</style> 