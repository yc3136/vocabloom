<template>
  <div class="discover-container">
    <!-- Search and Filter Section -->
    <div class="search-filter-section">
      <div class="search-filter-row">
        <!-- Search Bar -->
        <div class="search-container">
          <div class="search-input-wrapper">
            <input
              v-model="searchQuery"
              @input="handleSearchInput"
              @keyup.enter="handleSearch"
              placeholder="Search for words, translations, or story content..."
              class="search-input"
            />
            <button @click="handleSearch" class="search-btn">
              🔍
            </button>
          </div>
        </div>

        <!-- Filters Toggle Button -->
        <button @click="toggleFilters" class="filters-toggle-btn" :class="{ 'active': hasActiveFilters }">

          <span class="filter-text">Filters</span>
          <span v-if="hasActiveFilters" class="active-indicator">●</span>
        </button>
      </div>

      <!-- Collapsible Filter Controls -->
      <div class="filter-controls" :class="{ 'show': showFilters }">
        <div class="filter-group">
          <label>Language:</label>
          <select v-model="selectedLanguage" @change="handleFilterChange" class="filter-select">
            <option value="">All Languages</option>
            <option v-for="lang in supportedLanguages" :key="lang.value" :value="lang.value">
              {{ lang.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Age Group:</label>
          <select v-model="selectedAgeGroup" @change="handleFilterChange" class="filter-select">
            <option value="">All Ages</option>
            <option value="toddler">Toddler (1-3)</option>
            <option value="preschool">Preschool (4-5)</option>
            <option value="elementary">Elementary (6-10)</option>
            <option value="middle_school">Middle School (11-13)</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Content Type:</label>
          <select v-model="selectedContentType" @change="handleFilterChange" class="filter-select">
            <option value="">All Types</option>
            <option value="flashcards">Flashcards</option>
            <option value="stories">Stories</option>
            <option value="images">Images</option>
          </select>
        </div>

        <button @click="clearFilters" class="clear-filters-btn">
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Content Section -->
    <div class="content-section">
      <!-- Loading State -->
      <div v-if="discoverStore.loading && discoverStore.items.length === 0" class="loading-state">
        <div class="spinner"></div>
        <p>Loading content...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="discoverStore.error" class="error-state">
        <p>Error: {{ discoverStore.error }}</p>
        <button @click="retryLoad" class="retry-btn">Retry</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="discoverStore.items.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>No content found</h3>
        <p>Try adjusting your search or filters to find more content.</p>
        <button @click="clearFilters" class="clear-filters-btn">Clear All Filters</button>
      </div>

      <!-- Content Grid -->
      <div v-else class="content-grid">
        <div
          v-for="item in discoverStore.items"
          :key="`${item.content_type}-${item.id}`"
          class="content-card"
          :class="`content-card--${item.content_type}`"
        >
          <!-- Flashcard Card -->
          <div v-if="item.content_type === 'flashcard'" class="card-content">
            <div class="card-body">
              <h3 class="card-title">{{ item.original_word }}</h3>
              <p class="card-subtitle">{{ item.translated_word }}</p>
              <div v-if="item.example_sentences?.length" class="card-examples">
                <div v-for="sentence in item.example_sentences.slice(0, 2)" :key="sentence" class="example-sentence">
                  {{ sentence }}
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-badges">
                <span class="content-type-badge">📚 Flashcard</span>
                <span class="language-badge">{{ item.target_language }}</span>
              </div>
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>

          <!-- Story Card -->
          <div v-else-if="item.content_type === 'story'" class="card-content">
            <div class="card-body">
              <h3 class="card-title">{{ item.story_title }}</h3>
              <div class="card-subtitle" v-html="renderMarkdown(item.story_content)"></div>
            </div>
            <div class="card-footer">
              <div class="card-badges">
                <span class="content-type-badge">📖 Story</span>
                <span class="language-badge">{{ item.target_language }}</span>
                <span v-if="item.target_age_range" class="age-badge">{{ formatAgeGroup(item.target_age_range) }}</span>
              </div>
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>

          <!-- Image Card -->
          <div v-else-if="item.content_type === 'image'" class="card-content">
            <div class="card-body">
              <div v-if="item.image_url" class="image-preview">
                <img :src="item.image_url" :alt="item.original_word" @click="openImage(item.image_url)" />
              </div>
              <h3 class="card-title">{{ item.original_word }}</h3>
              <p class="card-subtitle">{{ item.translated_word }}</p>
            </div>
            <div class="card-footer">
              <div class="card-badges">
                <span class="content-type-badge">🖼️ Image</span>
                <span class="language-badge">{{ item.target_language }}</span>
              </div>
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>

          <!-- Translation Card -->
          <div v-else-if="item.content_type === 'translation'" class="card-content">
            <div class="card-header">
              <span class="content-type-badge">🌐 Translation</span>
              <span class="language-badge">{{ item.target_language }}</span>
            </div>
            <div class="card-body">
              <h3 class="card-title">{{ item.original_word }}</h3>
              <p class="card-subtitle">{{ item.translation }}</p>
              <div v-if="item.explanation" class="card-explanation">
                {{ truncateText(item.explanation, 100) }}
              </div>
            </div>
            <div class="card-footer">
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="discoverStore.hasMore" class="load-more-section">
        <button 
          @click="loadMore" 
          :disabled="discoverStore.loading"
          class="load-more-btn"
        >
          {{ discoverStore.loading ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { marked } from 'marked';
import { useDiscoverStore } from '../stores/discover';
import { SUPPORTED_LANGUAGES } from '../constants/languages';

const discoverStore = useDiscoverStore();

// Local state for search and filters
const searchQuery = ref('');
const selectedLanguage = ref('');
const selectedAgeGroup = ref('');
const selectedContentType = ref('');
const showFilters = ref(false); // Start with filters hidden on mobile

// Debounced search
let searchTimeout: NodeJS.Timeout | null = null;

// Computed properties
const supportedLanguages = computed(() => {
  return SUPPORTED_LANGUAGES;
});

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return selectedLanguage.value || selectedAgeGroup.value || selectedContentType.value;
});

// Methods
const handleSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = setTimeout(() => {
    handleSearch();
  }, 500);
};

const handleSearch = async () => {
  await discoverStore.updateFilters({ search: searchQuery.value });
};

const handleFilterChange = async () => {
  await discoverStore.updateFilters({
    language: selectedLanguage.value,
    age_group: selectedAgeGroup.value,
    content_type: selectedContentType.value
  });
};

const clearFilters = async () => {
  searchQuery.value = '';
  selectedLanguage.value = '';
  selectedAgeGroup.value = '';
  selectedContentType.value = '';
  await discoverStore.clearFilters();
};

const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

const loadMore = async () => {
  await discoverStore.loadMore();
};

const retryLoad = async () => {
  await discoverStore.initialize();
};

const openImage = (imageUrl: string) => {
  window.open(imageUrl, '_blank');
};

const formatDate = (dateString?: string) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString();
};

const formatAgeGroup = (ageGroup: string) => {
  const ageMap: Record<string, string> = {
    toddler: '1-3',
    preschool: '4-5',
    elementary: '6-10',
    middle_school: '11-13'
  };
  return ageMap[ageGroup] || ageGroup;
};

const truncateText = (text: string, maxLength: number) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

const renderMarkdown = (text: string) => {
  if (!text) return '';
  return marked(text);
};

// Initialize on mount
onMounted(async () => {
  await discoverStore.initialize();
  
  // Show filters by default on desktop, hide on mobile
  const isMobile = window.innerWidth <= 768;
  showFilters.value = !isMobile;
});

// Watch for URL changes to reset filters
watch(() => discoverStore.filters, (newFilters) => {
  searchQuery.value = newFilters.search;
  selectedLanguage.value = newFilters.language;
  selectedAgeGroup.value = newFilters.age_group;
  selectedContentType.value = newFilters.content_type;
}, { immediate: true });
</script>

<style scoped>
.discover-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.search-filter-section {
  margin-bottom: 32px;
}

.search-filter-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  justify-content: center;
  flex-wrap: wrap;
}

.search-container {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 12px 48px 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.search-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.search-btn:hover {
  background: rgba(102, 144, 255, 0.1);
}

.filters-toggle-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  height: 40px;
  white-space: nowrap;
  width: 120px;
  justify-content: center;
  flex-shrink: 0;
}

.filters-toggle-btn:hover {
  background: var(--bg-surface);
  border-color: var(--primary-blue);
}

.filters-toggle-btn.active {
  background: var(--primary-blue);
  color: white;
  border-color: var(--primary-blue);
}

.filters-toggle-btn.active:hover {
  background: var(--blue-hover);
}

.filter-icon {
  font-size: 14px;
}

.filter-text {
  font-size: 14px;
  font-weight: 500;
}

.active-indicator {
  color: #ff6b6b;
  font-size: 12px;
  margin-left: 2px;
}

.filters-toggle-btn.active .active-indicator {
  color: white;
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  justify-content: center;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, opacity 0.3s ease, margin 0.3s ease;
  opacity: 0;
  margin-top: 0;
}

.filter-controls.show {
  max-height: 200px;
  opacity: 1;
  margin-top: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  background: white;
  min-width: 120px;
  height: 40px;
}

.clear-filters-btn {
  padding: 8px 16px;
  background: var(--text-secondary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  height: 40px;
  white-space: nowrap;
}

.clear-filters-btn:hover {
  background: var(--text-primary);
}

.content-section {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
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

.error-state p {
  color: var(--error-red);
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state .empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.content-grid {
  column-count: 3;
  column-gap: 24px;
  margin-bottom: 32px;
}

.content-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  break-inside: avoid;
  page-break-inside: avoid;
  margin-bottom: 24px;
  display: inline-block;
  width: 100%;
}

.content-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-body {
  flex: 1;
  margin-bottom: 16px;
}

.card-title {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.card-subtitle {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.card-subtitle :deep(p) {
  margin: 0 0 8px 0;
}

.card-subtitle :deep(p:last-child) {
  margin-bottom: 0;
}

.card-subtitle :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.card-subtitle :deep(em) {
  font-style: italic;
}

.card-subtitle :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.card-examples {
  margin-top: 12px;
}

.example-sentence {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  line-height: 1.3;
}

.card-theme {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.theme-label {
  font-weight: 500;
}

.card-explanation {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.3;
}

.image-preview {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  width: 100%;
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.2s;
  object-fit: contain;
}

.image-preview:hover img {
  transform: scale(1.02);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.card-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.content-type-badge {
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: transparent;
}

.language-badge {
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: transparent;
}

.age-badge {
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: transparent;
}

.date {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.load-more-section {
  text-align: center;
  margin-top: 32px;
}

.load-more-btn {
  padding: 12px 24px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: var(--blue-hover);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .discover-container {
    padding: 16px;
  }
  
  .search-filter-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .search-container {
    min-width: auto;
    max-width: none;
  }

  .filters-toggle-btn {
    width: 100%;
    justify-content: center;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .clear-filters-btn {
    width: 100%;
  }
  
  .content-grid {
    column-count: 1; /* Single column on mobile */
    column-gap: 0;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-subtitle {
    font-size: 13px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .content-grid {
    column-count: 2; /* Two columns on medium screens */
  }
}

@media (min-width: 1025px) {
  .content-grid {
    column-count: 3; /* Three columns on large screens */
  }
}
</style> 