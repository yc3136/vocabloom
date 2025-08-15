import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';
import { DEFAULT_LANGUAGE } from '../constants/languages';

export interface UserPreferences {
  child_name?: string;
  child_age?: number;
  preferred_languages?: string[];
  theme?: 'light' | 'dark';
}

export const usePreferencesStore = defineStore('preferences', () => {
  const authStore = useAuthStore();
  const preferences = ref<UserPreferences>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  // Computed property to check if preferences are loaded
  const isLoaded = computed(() => !loading.value && Object.keys(preferences.value).length > 0);

  // Computed property for the primary preferred language
  const preferredLanguage = computed(() => {
    if (loading.value) {
      return null; // Return null while loading to prevent flash
    }
    if (preferences.value.preferred_languages && preferences.value.preferred_languages.length > 0) {
      return preferences.value.preferred_languages[0];
    }
    return DEFAULT_LANGUAGE;
  });

  // Load user preferences from the backend
  const loadPreferences = async () => {
    if (!authStore.isAuthenticated) {
      preferences.value = {};
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const response = await fetch(`${API_BASE}/api/preferences`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load preferences');
      }

      const preferencesData = await response.json();
      preferences.value = preferencesData;
      
      // Apply theme if it exists in preferences
      if (preferences.value.theme) {
        // Import theme store dynamically to avoid circular dependency
        const { useThemeStore } = await import('./theme');
        const themeStore = useThemeStore();
        themeStore.setTheme(preferences.value.theme);
      }
    } catch (err: any) {
      error.value = err.message;
      console.error('Error loading preferences:', err);
    } finally {
      loading.value = false;
    }
  };

  // Save user preferences
  const savePreferences = async (prefs: UserPreferences) => {
    if (!authStore.isAuthenticated) {
      throw new Error('User must be authenticated to save preferences')
    }

    loading.value = true
    error.value = null
    
    try {
      const token = await authStore.getIdToken()
      const requestBody = {
        preferred_languages: prefs.preferred_languages,
        child_age: prefs.child_age,
        child_name: prefs.child_name
      }
      
      const response = await fetch(`${API_BASE}/api/preferences`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })
      
      if (!response.ok) {
        throw new Error('Failed to save preferences')
      }
      
      const savedPreferences = await response.json()
      preferences.value = savedPreferences
      // Assuming notificationStore is available globally or imported elsewhere
      // const notificationStore = useNotificationStore(); 
      // notificationStore.success('Preferences saved successfully!')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to save preferences'
      // Assuming notificationStore is available globally or imported elsewhere
      // const notificationStore = useNotificationStore();
      // notificationStore.error('Failed to save preferences')
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update preferred languages
  const updatePreferredLanguages = async (languages: string[]) => {
    await savePreferences({
      ...preferences.value,
      preferred_languages: languages
    });
  };

  // Clear preferences (useful for logout)
  const clearPreferences = () => {
    preferences.value = {};
    error.value = null;
  };

  return {
    preferences,
    preferredLanguage,
    loading,
    isLoaded,
    error,
    loadPreferences,
    savePreferences,
    updatePreferredLanguages,
    clearPreferences
  };
}); 