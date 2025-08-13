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
      <!-- Clear Pending Generation Button -->
      <div v-if="hasPendingImages" class="pending-warning">
        <div class="warning-content">
          <div class="warning-icon">⚠️</div>
          <div class="warning-text">
            <p>You have pending image generations. If you're experiencing issues, you can clear them.</p>
          </div>
          <button 
            @click="clearPendingGeneration" 
            class="clear-pending-btn"
            :disabled="clearingPending"
          >
            {{ clearingPending ? 'Clearing...' : 'Clear Pending Generation' }}
          </button>
        </div>
      </div>

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
            <div v-else-if="image.status === 'failed'" class="image-placeholder failed">
              <div class="failed-icon">❌</div>
              <p>Generation failed</p>
            </div>
            <img 
              v-else-if="image.image_url" 
              :src="image.image_url" 
              :alt="`Generated image for ${image.original_word}`"
              class="generated-image"
              @error="handleImageError"
              @click="openImageInNewTab(image.image_url)"
              title="Click to open image in new tab"
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
              
              <div v-if="image.title" class="image-title">
                <p class="title-text">{{ image.title }}</p>
              </div>
              
                      <div class="image-badges">
          <span class="badge badge--language">{{ getLanguageDisplay(image.target_language) }}</span>
          <span v-if="image.child_age" class="badge badge--age">{{ image.child_age }} years old</span>
              </div>
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
          ‹
        </button>
        
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </span>
        
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-btn"
          :class="{ 'disabled': currentPage === totalPages }"
        >
          ›
        </button>
      </div>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <ConfirmationModal
    :show="showDeleteModal"
    title="Delete Image"
    message="Are you sure you want to delete this image?"
    type="danger"
    confirm-text="Delete"
    cancel-text="Cancel"
    @confirm="handleDeleteConfirm"
    @cancel="handleDeleteCancel"
    @close="handleDeleteCancel"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useImageStore } from '../stores/images'

import { SUPPORTED_LANGUAGES } from '../constants/languages'
import ConfirmationModal from './ConfirmationModal.vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

const imageStore = useImageStore()

// State
const searchTerm = ref('')
const selectedLanguage = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const refreshing = ref(false)
const clearingPending = ref(false)

// Confirmation modal state
const showDeleteModal = ref(false)
const imageToDelete = ref<number | null>(null)

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES

// Computed properties
const images = computed(() => imageStore.images)
const loading = computed(() => imageStore.loading)
const error = computed(() => imageStore.error)

const hasPendingImages = computed(() => {
  return images.value.some(image => image.status === 'pending')
})

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
  imageToDelete.value = imageId
  showDeleteModal.value = true
}

const handleDeleteConfirm = async () => {
  if (imageToDelete.value) {
    await imageStore.deleteImage(imageToDelete.value)
    showDeleteModal.value = false
    imageToDelete.value = null
  }
}

const handleDeleteCancel = () => {
  showDeleteModal.value = false
  imageToDelete.value = null
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

const openImageInNewTab = (imageUrl: string) => {
  window.open(imageUrl, '_blank')
}

const clearPendingGeneration = async () => {
  clearingPending.value = true
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const authStore = useAuthStore()
    
    if (!authStore.isAuthenticated) {
      throw new Error('User not authenticated')
    }
    
    const token = await authStore.getIdToken()
    const response = await fetch(`${API_BASE}/api/quota/image/clear-pending`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to clear pending generation')
    }
    
    const result = await response.json()
    
    if (result.cleared) {
      // Show success message
      const notificationStore = useNotificationStore()
      notificationStore.success('Pending generation cleared successfully! You can now generate new images.')
      
      // Refresh images to update the UI
      await refreshImages()
    } else {
      // Show info message if nothing was cleared
      const notificationStore = useNotificationStore()
      notificationStore.info('No pending generation found to clear.')
    }
    
  } catch (err) {
    console.error('Error clearing pending generation:', err)
    const notificationStore = useNotificationStore()
    notificationStore.error('Failed to clear pending generation. Please try again.')
  } finally {
    clearingPending.value = false
  }
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

.error {
  color: var(--error-red);
}

.retry-btn {
  background: var(--error-red);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.empty-state {
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.cta-btn {
  display: inline-block;
  background: var(--primary-blue);
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 6px;
  margin-top: 16px;
  transition: background-color 0.2s;
}

.cta-btn:hover {
  background: var(--blue-hover);
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
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.875rem;
  background: var(--bg-surface);
  color: var(--text-primary);
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
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.refresh-btn {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
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
  background: var(--border-color);
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
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--text-primary);
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
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
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
  border-color: var(--warning-amber);
}

.image-card.failed {
  border-color: var(--error-red);
}

.image-container {
  position: relative;
  width: 100%;
  height: 200px;
  background: var(--bg-primary);
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
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.image-placeholder.failed {
  color: var(--error-red);
}

.placeholder-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--warning-amber);
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
  cursor: pointer;
  transition: transform 0.2s ease;
}

.generated-image:hover {
  transform: scale(1.02);
}

.image-metadata {
  padding: 16px;
}



.image-details {
  margin-bottom: 12px;
}

.image-title {
  margin: 8px 0;
}

.title-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-style: italic;
  margin: 0;
  line-height: 1.4;
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
  color: var(--text-primary);
}

.separator {
  color: var(--text-secondary);
}

.translated-word {
  font-weight: 600;
  color: var(--primary-blue);
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
  background: var(--primary-blue);
  color: var(--bg-surface);
}

.age-badge {
  background: var(--premium-purple);
  color: var(--bg-surface);
}

.status-badge {
  text-transform: capitalize;
}

.status-badge.pending {
  background: var(--warning-amber);
  color: var(--text-primary);
}

.status-badge.completed {
  background: var(--success-green);
  color: var(--bg-surface);
}

.status-badge.failed {
  background: var(--error-red);
  color: var(--bg-surface);
}



.image-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1;
}

.remove-btn:hover {
  background: var(--border-color);
  color: var(--error-red);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.pagination-btn {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background: var(--bg-primary);
  border-color: var(--text-secondary);
}

.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Pending Warning Section */
.pending-warning {
  background: var(--warning-amber);
  border: 1px solid var(--warning-amber);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.warning-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.warning-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.warning-text {
  flex: 1;
  min-width: 0;
}

.warning-text p {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.clear-pending-btn {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  flex-shrink: 0;
}

.clear-pending-btn:hover:not(:disabled) {
  background: var(--bg-primary);
  border-color: var(--text-secondary);
}

.clear-pending-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .warning-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .clear-pending-btn {
    align-self: stretch;
  }
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
  
  .pagination {
    flex-direction: row;
    gap: 8px;
    padding: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
    min-width: 80px;
  }
  
  .page-info {
    font-size: 0.8rem;
    white-space: nowrap;
  }
}
</style> 