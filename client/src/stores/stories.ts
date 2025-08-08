import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

interface Story {
  id: number;
  original_words: string[];
  story_title: string;
  story_content: string;
  story_theme?: string;
  story_length?: string;
  target_age_range?: string;
  target_language?: string;
  view_count: number;
  created_at: string;
  updated_at: string;
}

interface StoryCreate {
  original_words: string[];
  story_title: string;
  story_content: string;
  story_theme?: string;
  story_length?: string;
  target_age_range?: string;
  target_language?: string;
}

export const useStoriesStore = defineStore('stories', () => {
  const stories = ref<Story[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  // Get all stories for the current user
  const fetchStories = async () => {
    if (!authStore.isAuthenticated) return;
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      console.log('Fetching stories from API...')
      
      const response = await fetch(`${API_BASE}/api/stories`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch stories');
      
      const fetchedStories = await response.json();
      console.log('Stories fetched from API:', fetchedStories.length, 'stories')
      stories.value = fetchedStories;
    } catch (err: any) {
      error.value = err.message;
      console.error('Error fetching stories:', err);
    } finally {
      loading.value = false;
    }
  };

  // Create a new story
  const createStory = async (storyData: StoryCreate) => {
    if (!authStore.isAuthenticated) throw new Error('Authentication required');
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/stories`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(storyData)
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Server response:', response.status, errorData);
        throw new Error(`Failed to create story: ${response.status} - ${errorData}`);
      }
      
      const newStory = await response.json();
      console.log('New story created:', newStory)
      stories.value.unshift(newStory);
      console.log('Stories after adding new story:', stories.value.length, 'stories')
      return newStory;
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Delete a story
  const deleteStory = async (storyId: number) => {
    if (!authStore.isAuthenticated) throw new Error('Authentication required');
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/stories/${storyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to delete story');
      
      // Remove from local state
      stories.value = stories.value.filter(story => story.id !== storyId);
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Get a specific story by ID
  const getStory = async (storyId: number) => {
    if (!authStore.isAuthenticated) throw new Error('Authentication required');
    
    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/stories/${storyId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch story');
      
      return await response.json();
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Clear stories (useful for logout)
  const clearStories = () => {
    stories.value = [];
    error.value = null;
  };

  // Computed properties for filtering
  const storiesByLanguage = computed(() => (language: string) => {
    return stories.value.filter(story => story.target_language === language);
  });

  const storiesByTheme = computed(() => (theme: string) => {
    return stories.value.filter(story => story.story_theme === theme);
  });

  return {
    stories,
    loading,
    error,
    fetchStories,
    createStory,
    deleteStory,
    getStory,
    clearStories,
    storiesByLanguage,
    storiesByTheme
  };
}); 