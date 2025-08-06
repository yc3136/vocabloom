<template>
  <div class="my-words-page">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading your words...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadWords" class="retry-btn">Try Again</button>
    </div>

    <div v-else-if="words.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No words yet</h3>
      <p>Start by looking up some words on the learn page!</p>
      <router-link to="/" class="cta-btn">Go to Learn</router-link>
    </div>

    <div v-else class="words-content">
      <div class="words-header">
        <div class="search-filters">
          <div class="search-box">
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Search words..."
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
            <strong>{{ filteredWords.length }}</strong> words
          </span>
        </div>
      </div>

      <div class="words-list">
        <div 
          v-for="word in paginatedWords" 
          :key="`${word.original_word}-${word.target_language}`"
          class="word-row"
          :class="{ 'expanded': expandedWords.includes(`${word.original_word}-${word.target_language}`) }"
        >
          <div class="word-main" @click="toggleExpand(`${word.original_word}-${word.target_language}`)">
            <div class="word-info">
              <div class="word-pair">
                <span class="word-text">{{ word.original_word }}</span>
                <span class="separator">→</span>
                <span class="translation-text">{{ word.translation }}</span>
              </div>
            </div>
            <div class="word-meta">
              <span class="language-badge">{{ word.target_language }}</span>
              <button 
                @click.stop="removeWord(word.original_word)"
                class="remove-btn"
                title="Remove from history"
              >
                ×
              </button>
            </div>
          </div>
          
          <div v-if="expandedWords.includes(`${word.original_word}-${word.target_language}`)" class="word-details">
            <div class="explanation" v-if="word.explanation">
              <h4>Explanation</h4>
              <div v-html="renderMarkdown(word.explanation)" class="markdown-content"></div>
            </div>
            <div class="examples" v-if="word.examples && word.examples.length > 0">
              <h4>Examples</h4>
              <ul>
                <li v-for="example in word.examples" :key="example">{{ example }}</li>
              </ul>
            </div>
            <div v-if="!word.explanation && (!word.examples || word.examples.length === 0)" class="no-content">
              <p>No additional details available for this word.</p>
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
          ← Previous
        </button>
        
        <div class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-btn"
          :class="{ 'disabled': currentPage === totalPages }"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { marked } from 'marked';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notification';
import { SUPPORTED_LANGUAGES } from '../constants/languages';

interface WordSummary {
  original_word: string;
  target_language: string;
  translation: string;
  explanation?: string;
  examples?: string[];
  created_at: string;
}

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES;

const words = ref<WordSummary[]>([]);
const loading = ref(true);
const error = ref('');
const searchTerm = ref('');
const selectedLanguage = ref('');
const expandedWords = ref<string[]>([]);
const currentPage = ref(1);
const itemsPerPage = 20;

const filteredWords = computed(() => {
  let filtered = words.value;
  
  // Filter by search term
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(word => 
      word.original_word.toLowerCase().includes(term) ||
      word.translation.toLowerCase().includes(term)
    );
  }
  
  // Filter by language
  if (selectedLanguage.value) {
    filtered = filtered.filter(word => 
      word.target_language === selectedLanguage.value
    );
  }
  
  return filtered;
});

const totalPages = computed(() => {
  return Math.ceil(filteredWords.value.length / itemsPerPage);
});

const paginatedWords = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filteredWords.value.slice(startIndex, endIndex);
});

const renderMarkdown = (text: string): string => {
  try {
    return marked(text);
  } catch (error) {
    console.error('Error rendering markdown:', error);
    return text; // Fallback to plain text
  }
};

const loadWords = async () => {
  if (!authStore.isAuthenticated) {
    error.value = 'Please log in to view your words';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = '';
    
    const token = await authStore.getIdToken();
    const response = await fetch('http://127.0.0.1:8000/api/words/my', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        error.value = 'Please log in to view your words';
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } else {
      const data = await response.json();
      console.log('Words API response:', data);
      words.value = data;
    }
  } catch (err) {
    console.error('Error loading words:', err);
    error.value = 'Failed to load your words. Please try again.';
    notificationStore.error('Failed to load words');
  } finally {
    loading.value = false;
  }
};

const toggleExpand = (wordKey: string) => {
  const index = expandedWords.value.indexOf(wordKey);
  if (index > -1) {
    expandedWords.value.splice(index, 1);
  } else {
    expandedWords.value.push(wordKey);
  }
};

const removeWord = async (originalWord: string) => {
  if (!confirm(`Remove "${originalWord}" from your history?`)) {
    return;
  }

  try {
    const token = await authStore.getIdToken();
    const response = await fetch(`http://127.0.0.1:8000/api/words/my/${encodeURIComponent(originalWord)}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Remove from local state
    words.value = words.value.filter(word => word.original_word !== originalWord);
    // Also remove from expanded words
    expandedWords.value = expandedWords.value.filter(word => !word.startsWith(originalWord + '-'));
    notificationStore.success(`Removed "${originalWord}" from history`);
  } catch (err) {
    console.error('Error removing word:', err);
    notificationStore.error('Failed to remove word from history');
  }
};



// Watch for authentication state changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    loadWords();
  } else {
    // Clear words when user logs out
    words.value = [];
    error.value = '';
  }
}, { immediate: true });

// Watch for filter changes to reset pagination
watch([searchTerm, selectedLanguage], () => {
  currentPage.value = 1;
});

// Also load on mount as backup
onMounted(() => {
  if (authStore.isAuthenticated) {
    loadWords();
  }
});
</script>

<style scoped>
.my-words-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 64px 24px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error p {
  color: #e53e3e;
  margin-bottom: 16px;
}

.retry-btn {
  background: #4299e1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.retry-btn:hover {
  background: #3182ce;
}

.empty-state {
  color: #718096;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #2d3748;
  margin-bottom: 8px;
}

.cta-btn {
  display: inline-block;
  background: #4299e1;
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 8px;
  margin-top: 16px;
  font-weight: 500;
}

.cta-btn:hover {
  background: #3182ce;
}

.words-header {
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
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  background: white;
}

.search-input:focus, .language-select:focus {
  border-color: #4299e1;
}

.language-select {
  cursor: pointer;
}

.stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  color: #718096;
  font-size: 0.9rem;
}

.stat-item strong {
  color: #2d3748;
}

.words-list {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.word-row {
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s;
}

.word-row:last-child {
  border-bottom: none;
}

.word-row:hover {
  background: #f8fafc;
}

.word-row.expanded {
  background: #f8fafc;
}

.word-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.word-main:hover {
  background: #f1f5f9;
}

.word-info {
  flex: 1;
  min-width: 0;
}

.word-pair {
  display: flex;
  align-items: center;
  gap: 8px;
}

.word-text, .translation-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a202c;
}

.translation-text {
  color: #4299e1;
}

.separator {
  color: #a0aec0;
  font-weight: 400;
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.language-badge {
  background: #4299e1;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.remove-btn {
  background: none;
  border: none;
  color: #a0aec0;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1;
}

.remove-btn:hover {
  background: #e2e8f0;
  color: #e53e3e;
}

.word-details {
  padding: 0 20px 20px;
  border-top: 1px solid #e2e8f0;
  background: #fafbfc;
}

.explanation, .examples {
  margin-top: 16px;
}

.explanation h4, .examples h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.explanation p {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.5;
  margin: 0;
}

.markdown-content {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.6;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  color: #2d3748;
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}

.markdown-content :deep(h1) { font-size: 1.4rem; }
.markdown-content :deep(h2) { font-size: 1.3rem; }
.markdown-content :deep(h3) { font-size: 1.2rem; }
.markdown-content :deep(h4) { font-size: 1.1rem; }
.markdown-content :deep(h5) { font-size: 1rem; }
.markdown-content :deep(h6) { font-size: 0.9rem; }

.markdown-content :deep(p) {
  margin-bottom: 12px;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 12px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin-bottom: 4px;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #4299e1;
  padding-left: 16px;
  margin: 16px 0;
  color: #4a5568;
  font-style: italic;
}

.markdown-content :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85rem;
}

.markdown-content :deep(pre) {
  background: #f1f5f9;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #2d3748;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(a) {
  color: #4299e1;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.examples ul {
  margin: 0;
  padding-left: 20px;
}

.examples li {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.5;
  margin-bottom: 4px;
}

.examples li:last-child {
  margin-bottom: 0;
}

.no-content {
  margin-top: 16px;
  text-align: center;
  color: #a0aec0;
  font-style: italic;
}

.no-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* Pagination styles */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.pagination-btn {
  background: #4299e1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background: #3182ce;
}

.pagination-btn.disabled {
  background: #e2e8f0;
  color: #a0aec0;
  cursor: not-allowed;
}

.page-info {
  color: #718096;
  font-size: 0.9rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .words-header {
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
  
  .word-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .word-meta {
    align-self: flex-end;
  }
  
  .word-pair {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .separator {
    display: none;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style> 