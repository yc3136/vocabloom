<template>
  <div class="my-stories-page">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading your stories...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadStories" class="retry-btn">Try Again</button>
    </div>

    <div v-else-if="stories.length === 0" class="empty-state">
      <div class="empty-icon">📖</div>
      <h3>No stories yet</h3>
      <p>Start by generating some stories on the learn page!</p>
      <router-link to="/" class="cta-btn">Go to Learn</router-link>
    </div>

    <div v-else class="stories-content">
      <div class="stories-header">
        <div class="search-filters">
          <div class="search-box">
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Search stories..."
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
            <strong>{{ filteredStories.length }}</strong> stories
          </span>
        </div>
      </div>

      <div class="stories-list">
        <div 
          v-for="story in paginatedStories" 
          :key="story.id"
          class="story-row"
          :class="{ 'expanded': expandedStories.includes(story.id) }"
        >
          <div class="story-main" @click="toggleExpand(story.id)">
            <div class="story-info">
              <div class="story-title">{{ story.story_title }}</div>
              <div class="story-meta">
                <span v-if="story.story_theme" class="theme-badge">{{ story.story_theme }}</span>
                <span v-if="story.target_language" class="language-badge">{{ story.target_language }}</span>
                <span v-if="story.target_age_range" class="age-badge">For {{ getAgeDisplay(story.target_age_range) }}</span>
              </div>
              <div class="story-words">
                <span class="words-label">Words:</span>
                <span v-for="word in story.original_words" :key="word" class="word-chip">
                  {{ word }}
                </span>
              </div>
            </div>
            <div class="story-actions">
              <button 
                @click.stop="deleteStory(story.id)"
                class="remove-btn"
                title="Delete story"
              >
                ×
              </button>
            </div>
          </div>
          
          <div v-if="expandedStories.includes(story.id)" class="story-details">
            <div class="story-content">
              <div v-html="renderMarkdown(story.story_content)" class="markdown-content"></div>
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
        
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        
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
import { ref, computed, onMounted, watch } from 'vue'
import { marked } from 'marked'
import { useStoriesStore } from '../stores/stories'
import { useAuthStore } from '../stores/auth'
import { SUPPORTED_LANGUAGES } from '../constants/languages'

const storiesStore = useStoriesStore()
const authStore = useAuthStore()

// Use store properties directly instead of destructuring to maintain reactivity
const stories = computed(() => storiesStore.stories)
const loading = computed(() => storiesStore.loading)
const error = computed(() => storiesStore.error)

const searchTerm = ref('')
const selectedLanguage = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const expandedStories = ref<number[]>([])

const languages = SUPPORTED_LANGUAGES

// Computed properties
const filteredStories = computed(() => {
  let filtered = stories.value || []

  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(story => 
      story.story_title.toLowerCase().includes(search) ||
      story.story_content.toLowerCase().includes(search) ||
      story.original_words.some(word => word.toLowerCase().includes(search))
    )
  }

  if (selectedLanguage.value) {
    filtered = filtered.filter(story => story.target_language === selectedLanguage.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredStories.value.length / itemsPerPage))

const paginatedStories = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredStories.value.slice(start, end)
})

// Methods
const loadStories = async () => {
  console.log('loadStories called, auth status:', authStore.isAuthenticated)
  if (authStore.isAuthenticated) {
    console.log('Fetching stories...')
    await storiesStore.fetchStories()
    console.log('Stories fetched, count:', stories.value?.length || 0)
  } else {
    console.log('User not authenticated, skipping story fetch')
  }
}

const toggleExpand = (storyId: number) => {
  const index = expandedStories.value.indexOf(storyId)
  if (index > -1) {
    expandedStories.value.splice(index, 1)
  } else {
    expandedStories.value.push(storyId)
  }
}

const deleteStory = async (storyId: number) => {
  if (confirm('Are you sure you want to delete this story?')) {
    try {
      await storiesStore.deleteStory(storyId)
    } catch (error) {
      console.error('Failed to delete story:', error)
    }
  }
}

const renderMarkdown = (content: string) => {
  return marked(content)
}

const getAgeDisplay = (ageRange: string) => {
  const ageMap: Record<string, string> = {
    'toddler': '2-3 years',
    'preschool': '4-5 years',
    'elementary': '6-10 years',
    'middle_school': '11-13 years'
  }
  return ageMap[ageRange] || ageRange
}

// Lifecycle
onMounted(() => {
  console.log('MyStoriesPage mounted, loading stories...')
  loadStories()
})

// Watch for changes in stories
watch(stories, (newStories) => {
  console.log('Stories changed:', newStories?.length || 0, 'stories')
}, { immediate: true })
</script>

<style scoped>
.my-stories-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  background: #f7fafc;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #e53e3e;
}

.retry-btn {
  background: #4299e1;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
}

.empty-state {
  color: #718096;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.cta-btn {
  display: inline-block;
  background: #4299e1;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  margin-top: 1rem;
  transition: background-color 0.2s;
}

.cta-btn:hover {
  background: #3182ce;
}

.stories-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-input, .language-select {
  width: 100%;
  padding: 0.5rem;
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

.stories-list {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.story-row {
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s;
}

.story-row:last-child {
  border-bottom: none;
}

.story-row:hover {
  background: #f8fafc;
}

.story-row.expanded {
  background: #f8fafc;
}

.story-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.story-main:hover {
  background: #f1f5f9;
}

.story-info {
  flex: 1;
  min-width: 0;
}

.story-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.story-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.theme-badge {
  background: #4299e1;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.language-badge {
  background: #48bb78;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.age-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 400;
}

.story-words {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.words-label {
  font-size: 0.8rem;
  color: #718096;
  font-weight: 500;
}

.word-chip {
  background: #f1f5f9;
  color: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.story-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
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

.story-details {
  padding: 0 20px 20px;
  border-top: 1px solid #e2e8f0;
  background: #fafbfc;
}

.story-content {
  margin-top: 16px;
}

.story-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  background: #4299e1;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background: #3182ce;
}

.pagination-btn.disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.page-info {
  color: #718096;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .my-stories-page {
    padding: 1rem;
  }
  
  .stories-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
  }
  
  .story-main {
    flex-direction: column;
    align-items: stretch;
  }
  
  .story-actions {
    align-self: flex-end;
    margin-top: 0.5rem;
  }
}
</style> 