import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface DiscoverItem {
  id: number;
  content_type: 'flashcard' | 'story' | 'image' | 'translation';
  original_word?: string;
  translated_word?: string;
  target_language?: string;
  example_sentences?: string[];
  created_at?: string;
  story_title?: string;
  story_content?: string;
  story_theme?: string;
  target_age_range?: string;
  image_url?: string;
  translation?: string;
  explanation?: string;
  user?: {
    email?: string;
  };
}

export interface DiscoverFilters {
  search: string;
  language: string;
  age_group: string;
  content_type: string;
}

export interface DiscoverStats {
  content_counts: {
    flashcards: number;
    stories: number;
    images: number;
    translations: number;
    total: number;
  };
  language_distribution: Array<{ language: string; count: number }>;
  age_group_distribution: Array<{ age_group: string; count: number }>;
}

export const useDiscoverStore = defineStore('discover', () => {
  const items = ref<DiscoverItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const hasMore = ref(false);
  const total = ref(0);
  const skip = ref(0);
  const limit = ref(20);
  
  const filters = ref<DiscoverFilters>({
    search: '',
    language: '',
    age_group: '',
    content_type: ''
  });
  
  const stats = ref<DiscoverStats | null>(null);
  const trendingItems = ref<DiscoverItem[]>([]);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  // Reset pagination when filters change
  const resetPagination = () => {
    skip.value = 0;
    items.value = [];
  };

  // Fetch discovery content
  const fetchContent = async (reset = false) => {
    try {
      loading.value = true;
      error.value = null;
      
      if (reset) {
        resetPagination();
      }
      
      const params = new URLSearchParams({
        skip: skip.value.toString(),
        limit: limit.value.toString()
      });
      
      // Add filters
      if (filters.value.search) {
        params.append('search', filters.value.search);
      }
      if (filters.value.language) {
        params.append('language', filters.value.language);
      }
      if (filters.value.age_group) {
        params.append('age_group', filters.value.age_group);
      }
      if (filters.value.content_type) {
        params.append('content_type', filters.value.content_type);
      }
      
      const response = await fetch(`${API_BASE}/api/discover/?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch discovery content');
      }
      
      const data = await response.json();
      
      if (reset) {
        items.value = data.items;
      } else {
        items.value.push(...data.items);
      }
      
      hasMore.value = data.has_more;
      total.value = data.total;
      skip.value += data.items.length;
      
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Load more content (for infinite scroll)
  const loadMore = async () => {
    if (!hasMore.value || loading.value) return;
    await fetchContent(false);
  };

  // Update filters and refetch content
  const updateFilters = async (newFilters: Partial<DiscoverFilters>) => {
    Object.assign(filters.value, newFilters);
    await fetchContent(true);
  };

  // Clear all filters
  const clearFilters = async () => {
    filters.value = {
      search: '',
      language: '',
      age_group: '',
      content_type: ''
    };
    await fetchContent(true);
  };

  // Fetch trending content
  const fetchTrending = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/discover/trending?limit=10`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch trending content');
      }
      
      const data = await response.json();
      trendingItems.value = data.trending_items;
      
    } catch (err: any) {
      console.error('Failed to fetch trending content:', err);
    }
  };

  // Fetch discovery statistics
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/discover/stats`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch discovery stats');
      }
      
      stats.value = await response.json();
      
    } catch (err: any) {
      console.error('Failed to fetch discovery stats:', err);
    }
  };

  // Computed properties for filtered content
  const filteredItems = computed(() => {
    return items.value;
  });

  const contentByType = computed(() => {
    const grouped = {
      flashcards: items.value.filter(item => item.content_type === 'flashcard'),
      stories: items.value.filter(item => item.content_type === 'story'),
      images: items.value.filter(item => item.content_type === 'image'),
      translations: items.value.filter(item => item.content_type === 'translation')
    };
    return grouped;
  });

  const availableLanguages = computed(() => {
    if (!stats.value) return [];
    return stats.value.language_distribution.map(item => item.language);
  });

  const availableAgeGroups = computed(() => {
    if (!stats.value) return [];
    return stats.value.age_group_distribution.map(item => item.age_group);
  });

  // Initialize discovery
  const initialize = async () => {
    await Promise.all([
      fetchContent(true),
      fetchTrending(),
      fetchStats()
    ]);
  };

  return {
    // State
    items,
    loading,
    error,
    hasMore,
    total,
    filters,
    stats,
    trendingItems,
    
    // Actions
    fetchContent,
    loadMore,
    updateFilters,
    clearFilters,
    fetchTrending,
    fetchStats,
    initialize,
    
    // Computed
    filteredItems,
    contentByType,
    availableLanguages,
    availableAgeGroups
  };
}); 