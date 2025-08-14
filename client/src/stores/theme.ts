import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export type Theme = 'light' | 'dark';

export const useThemeStore = defineStore('theme', () => {
  // Initialize theme from localStorage or default to 'light'
  const saved = localStorage.getItem('vocabloom-theme');
  const currentTheme = ref<Theme>((saved as Theme) || 'light');

  // Apply theme to document
  const applyTheme = (theme: Theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vocabloom-theme', theme);
  };

  // Toggle between light and dark themes
  const toggleTheme = () => {
    const newTheme = currentTheme.value === 'light' ? 'dark' : 'light'
    currentTheme.value = newTheme
    localStorage.setItem('theme', newTheme)
  }

  // Set specific theme
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme;
    applyTheme(theme);
  };

  // Initialize theme on store creation
  applyTheme(currentTheme.value);

  // Watch for theme changes and apply them
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme);
  });

  return {
    currentTheme,
    toggleTheme,
    setTheme,
    applyTheme
  };
}); 