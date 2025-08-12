<template>
  <div class="my-images-page">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading your images...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadImages" class="retry-btn">Try Again</button>
    </div>

    <div v-else-if="images.length === 0" class="empty-state">
      <div class="empty-icon">🖼️</div>
      <h3>No images yet</h3>
      <p>Start by generating some images on the learn page!</p>
      <router-link to="/" class="cta-btn">Go to Learn</router-link>
    </div>

    <div v-else class="images-content">
      <div class="images-header">
        <div class="search-filters">
          <div class="search-box">
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Search by word, translation, or title..."
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
          <div class="status-filter">
            <select v-model="selectedStatus" class="status-select">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
        <div class="stats">
          <span class="stat-item">
            <strong>{{ filteredImages.length }}</strong> images
          </span>
          <button @click="refreshImages" class="refresh-btn" :disabled="refreshing" title="Refresh images">
            <svg v-if="!refreshing" class="refresh-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <div v-else class="refresh-spinner"></div>
          </button>
        </div>
      </div>

      <div class="images-grid">
        <div 
          v-for="image in paginatedImages" 
          :key="image.id"
          class="image-card"
          :class="{ 'pending': image.status === 'pending', 'failed': image.status === 'failed' }"
        >
          <!-- Image Display -->
          <div class="image-container">
            <div v-if="image.status === 'pending'" class="image-placeholder">
              <div class="placeholder-spinner"></div>
              <p>Generation in progress...</p>
            </div>
            <div v-else-if="image.status === 'failed'" class="image-placeholder failed" @click="showErrorNotification">
              <div class="failed-icon">❌</div>
              <p>Generation failed (click for details)</p>
            </div>
            <img 
              v-else-if="image.image_url" 
              :src="image.image_url" 
              :alt="`Generated image for ${image.original_word}`"
              class="generated-image"
              @error="handleImageError"
            />
            <div v-else class="image-placeholder">
              <div class="placeholder-icon">🖼️</div>
              <p>No image available</p>
            </div>
          </div>

          <!-- Image Metadata -->
          <div class="image-metadata">
            <div class="image-details">
              <div class="word-pair">
                <span class="original-word">{{ image.original_word }}</span>
                <span class="separator">→</span>
                <span class="translated-word">{{ image.translated_word }}</span>
              </div>
              
              <div class="image-badges">
                <span class="language-badge">{{ getLanguageDisplay(image.target_language) }}</span>
                <span v-if="image.child_age" class="age-badge">{{ image.child_age }} years old</span>
                <span class="status-badge" :class="image.status">{{ image.status }}</span>
              </div>
            </div>

            <div v-if="image.custom_instructions" class="custom-instructions">
              <p class="instructions-label">Custom Instructions:</p>
              <p class="instructions-text">{{ image.custom_instructions }}</p>
            </div>

            <div class="image-actions">
              <button 
                @click="deleteImage(image.id)"
                class="remove-btn"
                title="Delete image"
              >
                ×
              </button>
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
import { useImageStore } from '../stores/images'
import { useNotificationStore } from '../stores/notification'
import { SUPPORTED_LANGUAGES } from '../constants/languages'

const imageStore = useImageStore()
const notificationStore = useNotificationStore()

// State
const searchTerm = ref('')
const selectedLanguage = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const refreshing = ref(false)

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES

// Computed properties
const images = computed(() => imageStore.images)
const loading = computed(() => imageStore.loading)
const error = computed(() => imageStore.error)

const filteredImages = computed(() => {
  let filtered = images.value

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(image => 
      image.original_word.toLowerCase().includes(search) ||
      image.translated_word.toLowerCase().includes(search) ||
      (image.title && image.title.toLowerCase().includes(search))
    )
  }

  // Filter by language
  if (selectedLanguage.value) {
    filtered = filtered.filter(image => image.target_language === selectedLanguage.value)
  }

  // Filter by status
  if (selectedStatus.value) {
    filtered = filtered.filter(image => image.status === selectedStatus.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredImages.value.length / itemsPerPage.value))

const paginatedImages = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredImages.value.slice(start, end)
})

// Methods
const loadImages = async () => {
  await imageStore.loadImages()
}

const refreshImages = async () => {
  refreshing.value = true
  await imageStore.refreshImages()
  refreshing.value = false
}

const deleteImage = async (imageId: number) => {
  if (confirm('Are you sure you want to delete this image?')) {
    await imageStore.deleteImage(imageId)
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement?.classList.add('image-error')
}

const getLanguageDisplay = (languageCode: string) => {
  const language = languages.find(lang => lang.value === languageCode)
  return language ? language.label : languageCode
}

const showErrorNotification = () => {
  notificationStore.error('Image generation failed. Check the server logs for details.')
}

// Watch for changes in filters and reset pagination
watch([searchTerm, selectedLanguage, selectedStatus], () => {
  currentPage.value = 1
})

// Load images on mount
onMounted(() => {
  loadImages()
})
</script>

<style scoped>
.my-images-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 60px 20px;
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

.error {
  color: #dc2626;
}

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.empty-state {
  color: #6b7280;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.cta-btn {
  display: inline-block;
  background: #6690ff;
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 6px;
  margin-top: 16px;
  transition: background-color 0.2s;
}

.cta-btn:hover {
  background: #5a7cff;
}

.images-header {
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
  flex-wrap: wrap;
  flex: 1;
}

.search-input,
.language-select,
.status-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.search-input {
  min-width: 200px;
}

.stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-item {
  color: #6b7280;
  font-size: 0.875rem;
}

.refresh-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.refresh-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  width: 18px;
  height: 18px;
}

.refresh-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-top: 2px solid #374151;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.image-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.image-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.image-card.pending {
  border-color: #fbbf24;
}

.image-card.failed {
  border-color: #ef4444;
}

.image-container {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  text-align: center;
  padding: 20px;
}

.image-placeholder.failed {
  color: #dc2626;
}

.placeholder-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #fbbf24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

.placeholder-icon,
.failed-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.generated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-metadata {
  padding: 16px;
}



.image-details {
  margin-bottom: 12px;
}

.word-pair {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.original-word {
  font-weight: 600;
  color: #111827;
}

.separator {
  color: #6b7280;
}

.translated-word {
  font-weight: 600;
  color: #6690ff;
}

.image-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.language-badge,
.age-badge,
.status-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.language-badge {
  background: #6690ff;
  color: white;
}

.age-badge {
  background: #8b5cf6;
  color: white;
}

.status-badge {
  text-transform: capitalize;
}

.status-badge.pending {
  background: #fbbf24;
  color: #92400e;
}

.status-badge.completed {
  background: #10b981;
  color: white;
}

.status-badge.failed {
  background: #ef4444;
  color: white;
}

.custom-instructions {
  margin-top: 12px;
  padding: 8px;
  background: #f9fafb;
  border-radius: 6px;
}

.instructions-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.instructions-text {
  font-size: 0.875rem;
  color: #374151;
  margin: 0;
  line-height: 1.4;
}

.image-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.pagination-btn {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .my-images-page {
    padding: 16px;
  }
  
  .images-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .images-grid {
    grid-template-columns: 1fr;
    gap: 16px;
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