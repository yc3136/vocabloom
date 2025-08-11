import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export interface Image {
  id: number
  user_id: string
  original_word: string
  translated_word: string
  target_language: string
  image_url?: string
  generation_prompt: string
  custom_instructions?: string
  status: 'pending' | 'completed' | 'failed'
  child_age?: number
  title?: string
  created_at: string
  updated_at: string
}

export interface ImageGenerationRequest {
  original_word: string
  translated_word: string
  target_language: string
  custom_instructions?: string
  child_age?: number
  title?: string
}

export const useImageStore = defineStore('images', () => {
  const images = ref<Image[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const generating = ref(false)

  const authStore = useAuthStore()

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

  // Computed properties
  const pendingImages = computed(() => 
    images.value.filter(img => img.status === 'pending')
  )

  const completedImages = computed(() => 
    images.value.filter(img => img.status === 'completed')
  )

  const failedImages = computed(() => 
    images.value.filter(img => img.status === 'failed')
  )

  // Load user's images
  const loadImages = async () => {
    if (!authStore.isAuthenticated) {
      error.value = 'User not authenticated'
      return
    }

    loading.value = true
    error.value = null

    try {
      const token = await authStore.getIdToken()
      const response = await fetch(`${API_BASE}/api/images/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      images.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load images'
      console.error('Error loading images:', err)
    } finally {
      loading.value = false
    }
  }

  // Generate a new image
  const generateImage = async (request: ImageGenerationRequest) => {
    if (!authStore.isAuthenticated) {
      error.value = 'User not authenticated'
      return null
    }

    generating.value = true
    error.value = null

    try {
      const token = await authStore.getIdToken()
      const response = await fetch(`${API_BASE}/api/images/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Add the new image to the list
      const newImage: Image = {
        id: data.id,
        user_id: authStore.user!.uid,
        original_word: request.original_word,
        translated_word: request.translated_word,
        target_language: request.target_language,
        generation_prompt: '',
        custom_instructions: request.custom_instructions,
        status: 'pending',
        child_age: request.child_age,
        title: request.title,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      images.value.unshift(newImage)
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to generate image'
      console.error('Error generating image:', err)
      return null
    } finally {
      generating.value = false
    }
  }

  // Update image metadata
  const updateImage = async (imageId: number, updates: { title?: string; custom_instructions?: string }) => {
    if (!authStore.isAuthenticated) {
      error.value = 'User not authenticated'
      return null
    }

    try {
      const token = await authStore.getIdToken()
      const response = await fetch(`${API_BASE}/api/images/${imageId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const updatedImage = await response.json()
      
      // Update the image in the store
      const index = images.value.findIndex(img => img.id === imageId)
      if (index !== -1) {
        images.value[index] = updatedImage
      }

      return updatedImage
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update image'
      console.error('Error updating image:', err)
      return null
    }
  }

  // Delete an image
  const deleteImage = async (imageId: number) => {
    if (!authStore.isAuthenticated) {
      error.value = 'User not authenticated'
      return false
    }

    try {
      const token = await authStore.getIdToken()
      const response = await fetch(`${API_BASE}/api/images/${imageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Remove the image from the store
      images.value = images.value.filter(img => img.id !== imageId)
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete image'
      console.error('Error deleting image:', err)
      return false
    }
  }

  // Refresh images (useful for checking generation status)
  const refreshImages = async () => {
    await loadImages()
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    images,
    loading,
    error,
    generating,
    
    // Computed
    pendingImages,
    completedImages,
    failedImages,
    
    // Actions
    loadImages,
    generateImage,
    updateImage,
    deleteImage,
    refreshImages,
    clearError
  }
}) 