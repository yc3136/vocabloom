<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useAuthStore } from '../stores/auth'

import FlashcardModal from './FlashcardModal.vue'

const term = ref('')
const selectedLanguage = ref('Spanish')
const translation = ref('')
const explanation = ref('')
const loading = ref(false)
const error = ref('')
const showFlashcardModal = ref(false)

const authStore = useAuthStore()
// const flashcardStore = useFlashcardStore()

// Popular languages for the dropdown
const languages = [
  { value: 'Spanish', label: 'Spanish (Español)' },
  { value: 'French', label: 'French (Français)' },
  { value: 'German', label: 'German (Deutsch)' },
  { value: 'Italian', label: 'Italian (Italiano)' },
  { value: 'Portuguese', label: 'Portuguese (Português)' },
  { value: 'Japanese', label: 'Japanese (日本語)' },
  { value: 'Korean', label: 'Korean (한국어)' },
  { value: 'Chinese', label: 'Chinese Simplified (简体中文)' },
  { value: 'Russian', label: 'Russian (Русский)' },
  { value: 'Arabic', label: 'Arabic (العربية)' },
  { value: 'Hindi', label: 'Hindi (हिन्दी)' },
  { value: 'Dutch', label: 'Dutch (Nederlands)' },
  { value: 'Swedish', label: 'Swedish (Svenska)' },
  { value: 'Norwegian', label: 'Norwegian (Norsk)' },
  { value: 'Danish', label: 'Danish (Dansk)' },
  { value: 'Finnish', label: 'Finnish (Suomi)' },
  { value: 'Polish', label: 'Polish (Polski)' },
  { value: 'Turkish', label: 'Turkish (Türkçe)' },
  { value: 'Greek', label: 'Greek (Ελληνικά)' },
  { value: 'Hebrew', label: 'Hebrew (עברית)' }
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
  error.value = ''
  
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  
  try {
    const res = await fetch(`${API_BASE}/api/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
  } catch (e) {
    error.value = 'Error contacting backend. Please try again.'
    console.error('Translation error:', e)
  } finally {
    loading.value = false
  }
}

function createFlashcard() {
  if (!authStore.isAuthenticated) {
    // Show authentication prompt
    alert('Please sign in to create flashcards!')
    return
  }
  showFlashcardModal.value = true
}

function handleFlashcardSuccess() {
  showFlashcardModal.value = false
}
</script>

<template>
  <div class="home-container">
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
      <span v-if="!loading">Translate</span>
      <span v-else>Translating...</span>
    </button>
    
    <div v-if="error" class="error-box">
      <p>{{ error }}</p>
    </div>
    
    <div v-if="renderedResponse" class="response-box" v-html="renderedResponse"></div>
    
    <div v-if="renderedResponse" class="flashcard-actions">
      <button @click="createFlashcard" class="create-flashcard-btn">
        📚 Create Flashcard
      </button>
    </div>

    <!-- Flashcard Modal -->
    <FlashcardModal 
      :show="showFlashcardModal"
      :initial-data="{
        original_word: term,
        translated_word: translation,
        example_sentences: explanation ? [explanation] : []
      }"
      @close="showFlashcardModal = false"
      @success="handleFlashcardSuccess"
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
  transition: border 0.2s;
}

.language-select:focus {
  border: 1.5px solid var(--primary-blue, #6690ff);
  outline: none;
}

.lookup-btn {
  margin-top: 1.5rem;
  padding: 0.75rem 2rem;
  background: linear-gradient(90deg, var(--primary-blue, #6690ff) 0%, var(--blue-hover, #4a7aff) 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(30, 34, 90, 0.08);
  transition: background 0.2s, box-shadow 0.2s;
}

.lookup-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.lookup-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, var(--blue-hover, #4a7aff) 0%, var(--primary-blue, #6690ff) 100%);
  box-shadow: 0 4px 16px rgba(30, 34, 90, 0.12);
}

.error-box {
  margin-top: 2rem;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid var(--error-red, #f87171);
  padding: 1rem;
  border-radius: 8px;
  color: var(--error-red, #f87171);
  font-size: 1rem;
}

.response-box {
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(102, 144, 255, 0.05);
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(30, 34, 90, 0.06);
  color: var(--text-primary, #1e293b);
  font-size: 1.05rem;
  line-height: 1.6;
  text-align: left;
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

.flashcard-actions {
  margin-top: 1.5rem;
  text-align: center;
}

.create-flashcard-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(90deg, var(--success-green, #4ade80) 0%, var(--info-cyan, #38bdf8) 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(74, 222, 128, 0.2);
  transition: background 0.2s, box-shadow 0.2s;
}

.create-flashcard-btn:hover {
  background: linear-gradient(90deg, var(--success-green, #4ade80) 0%, var(--info-cyan, #38bdf8) 100%);
  box-shadow: 0 4px 16px rgba(74, 222, 128, 0.3);
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
}
</style> 