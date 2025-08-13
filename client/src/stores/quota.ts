import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export interface QuotaInfo {
  limit: number
  used: number
  remaining: number
}

export interface UserQuotas {
  image: QuotaInfo
  story: QuotaInfo
  translation: QuotaInfo
}

export const useQuotaStore = defineStore('quota', () => {
  const quotas = ref<UserQuotas | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

  // Load user quotas
  const loadQuotas = async () => {
    if (!authStore.isAuthenticated) {
      quotas.value = null
      return
    }

    loading.value = true
    error.value = null

    try {
      const token = await authStore.getIdToken()
      const response = await fetch(`${API_BASE}/api/quota/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      quotas.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load quotas'
      console.error('Error loading quotas:', err)
    } finally {
      loading.value = false
    }
  }

  // Get quota for specific content type
  const getQuota = (contentType: keyof UserQuotas): QuotaInfo | null => {
    return quotas.value?.[contentType] || null
  }

  // Check if user has remaining quota for content type
  const hasQuota = (contentType: keyof UserQuotas): boolean => {
    const quota = getQuota(contentType)
    if (!quota) return true // No quota info, assume unlimited
    return quota.limit === -1 || quota.remaining > 0
  }

  // Get remaining quota count
  const getRemainingQuota = (contentType: keyof UserQuotas): number => {
    const quota = getQuota(contentType)
    if (!quota) return -1 // No quota info, assume unlimited
    return quota.remaining
  }

  // Clear quotas (useful on logout)
  const clearQuotas = () => {
    quotas.value = null
    error.value = null
  }

  return {
    // State
    quotas,
    loading,
    error,
    
    // Actions
    loadQuotas,
    getQuota,
    hasQuota,
    getRemainingQuota,
    clearQuotas
  }
}) 