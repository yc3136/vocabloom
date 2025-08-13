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

  // Computed property for the primary preferred language
  const preferredLanguage = computed(() => {
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
      
      const response = await fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load preferences');
      }

      const userData = await response.json();
      preferences.value = userData.preferences || {};
      
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

  // Save user preferences to the backend
  const savePreferences = async (newPreferences: UserPreferences) => {
    if (!authStore.isAuthenticated) {
      throw new Error('Authentication required');
    }

    try {
      loading.value = true;
      error.value = null;
      const token = await authStore.getIdToken();
      
      const requestBody = {
        preferences: newPreferences
      };
      
      console.log('Sending preferences request:', requestBody);
      
      const response = await fetch(`${API_BASE}/api/auth/preferences`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Preferences update error:', errorData);
        throw new Error(errorData.detail || `Failed to save preferences: ${response.status}`);
      }

      // Update local preferences
      preferences.value = { ...preferences.value, ...newPreferences };
    } catch (err: any) {
      error.value = err.message;
      console.error('Error saving preferences:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

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
    error,
    loadPreferences,
    savePreferences,
    updatePreferredLanguages,
    clearPreferences
  };
}); 