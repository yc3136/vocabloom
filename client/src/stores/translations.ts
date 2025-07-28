import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

interface Translation {
  id: number;
  user_id: string;
  original_term: string;
  target_language: string;
  translation: string;
  explanation?: string;
  bookmarked: boolean;
  created_at: string;
}

interface TranslationCreate {
  original_term: string;
  target_language: string;
  translation: string;
  explanation?: string;
  bookmarked?: boolean;
}

export const useTranslationStore = defineStore('translations', () => {
  const translations = ref<Translation[]>([]);
  const currentTranslation = ref<TranslationCreate | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  // Get translation history for current user
  const fetchTranslations = async () => {
    if (!authStore.isAuthenticated) return;
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/translations/history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch translations');
      
      translations.value = await response.json();
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Save translation to history
  const saveTranslation = async (translation: TranslationCreate) => {
    if (!authStore.isAuthenticated) throw new Error('Authentication required');
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/translations/save`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(translation)
      });
      
      if (!response.ok) throw new Error('Failed to save translation');
      
      const savedTranslation = await response.json();
      translations.value.unshift(savedTranslation);
      return savedTranslation;
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Toggle bookmark status
  const toggleBookmark = async (id: number, bookmarked: boolean) => {
    if (!authStore.isAuthenticated) throw new Error('Authentication required');
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/translations/${id}/bookmark`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ bookmarked })
      });
      
      if (!response.ok) throw new Error('Failed to update bookmark');
      
      const index = translations.value.findIndex(t => t.id === id);
      if (index !== -1) {
        translations.value[index].bookmarked = bookmarked;
      }
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Set current translation (for preview/save flow)
  const setCurrentTranslation = (translation: TranslationCreate | null) => {
    currentTranslation.value = translation;
  };

  // Get bookmarked translations
  const bookmarkedTranslations = computed(() => 
    translations.value.filter(t => t.bookmarked)
  );

  return {
    translations,
    currentTranslation,
    loading,
    error,
    bookmarkedTranslations,
    fetchTranslations,
    saveTranslation,
    toggleBookmark,
    setCurrentTranslation
  };
}); 