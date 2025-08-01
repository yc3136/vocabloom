import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import { useNotificationStore } from './notification';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface Flashcard {
  id: number;
  user_id: string;
  original_word: string;
  translated_word: string;
  target_language: string;
  example_sentences: string[];
  created_at: string;
  updated_at: string;
  colors: { primary: string; secondary: string };
}

export interface FlashcardCreate {
  original_word: string;
  translated_word: string;
  target_language: string;
  example_sentences: string[];
  colors: { primary: string; secondary: string };
}

export const useFlashcardStore = defineStore('flashcards', () => {
  const flashcards = ref<Flashcard[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  const authStore = useAuthStore();
  const notificationStore = useNotificationStore();

  const fetchFlashcards = async () => {
    if (!authStore.isAuthenticated) {
      flashcards.value = [];
      return;
    }

    loading.value = true;
    error.value = null;
    
    try {
      const token = await authStore.getIdToken();
      const response = await fetch(`${API_BASE}/api/flashcards/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch flashcards');
      }
      
      const data = await response.json();
      flashcards.value = data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch flashcards';
      notificationStore.error('Failed to load flashcards');
    } finally {
      loading.value = false;
    }
  };

  const createFlashcard = async (flashcard: FlashcardCreate) => {
    if (!authStore.isAuthenticated) {
      throw new Error('User must be authenticated to create flashcards');
    }

    loading.value = true;
    error.value = null;
    
    try {
      const token = await authStore.getIdToken();
      const response = await fetch(`${API_BASE}/api/flashcards/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(flashcard)
      });
      
      if (!response.ok) {
        throw new Error('Failed to create flashcard');
      }
      
      const newFlashcard = await response.json();
      flashcards.value.unshift(newFlashcard);
      // Show success notification with link to flashcards
      notificationStore.success(
        `Flashcard created successfully! <a href="/flashcards" style="color: white; text-decoration: underline;">View in My Flashcards →</a>`,
        { allowHtml: true, duration: 6000 }
      )
      return newFlashcard;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create flashcard';
      notificationStore.error('Failed to create flashcard');
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateFlashcard = async (id: number, updates: Partial<FlashcardCreate>) => {
    if (!authStore.isAuthenticated) {
      throw new Error('User must be authenticated to update flashcards');
    }

    loading.value = true;
    error.value = null;
    
    try {
      const token = await authStore.getIdToken();
      const response = await fetch(`${API_BASE}/api/flashcards/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update flashcard');
      }
      
      const updatedFlashcard = await response.json();
      const index = flashcards.value.findIndex(f => f.id === id);
      if (index !== -1) {
        flashcards.value[index] = updatedFlashcard;
      }
      notificationStore.success('Flashcard updated successfully!');
      return updatedFlashcard;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update flashcard';
      notificationStore.error('Failed to update flashcard');
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteFlashcard = async (id: number) => {
    if (!authStore.isAuthenticated) {
      throw new Error('User must be authenticated to delete flashcards');
    }

    loading.value = true;
    error.value = null;
    
    try {
      const token = await authStore.getIdToken();
      const response = await fetch(`${API_BASE}/api/flashcards/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete flashcard');
      }
      
      flashcards.value = flashcards.value.filter(f => f.id !== id);
      notificationStore.success('Flashcard deleted successfully!');
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete flashcard';
      notificationStore.error('Failed to delete flashcard');
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const previewFlashcard = async (flashcard: FlashcardCreate) => {
    try {
      const response = await fetch(`${API_BASE}/api/flashcards/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(flashcard)
      });
      
      if (!response.ok) {
        throw new Error('Failed to preview flashcard');
      }
      
      return await response.json();
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to preview flashcard';
      throw err;
    }
  };

  return {
    flashcards,
    loading,
    error,
    fetchFlashcards,
    createFlashcard,
    updateFlashcard,
    deleteFlashcard,
    previewFlashcard
  };
}); 