<template>
  <div class="user-profile">
    <div class="user-info" @click="toggleDropdown">
      <div class="user-avatar">
        {{ userInitial }}
      </div>
      <span class="user-name">{{ displayName }}</span>
      <span class="dropdown-arrow" :class="{ 'rotated': showDropdown }">▼</span>
    </div>
    
    <div class="dropdown-menu" v-if="showDropdown">
      <div class="dropdown-item" @click="navigateToFlashcards">
        <span class="icon">📚</span>
        My Flashcards
      </div>
      <div class="dropdown-item" @click="handleLogout">
        <span class="icon">🚪</span>
        Sign Out
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const showDropdown = ref(false);

const displayName = computed(() => {
  return authStore.user?.displayName || authStore.user?.email || 'User';
});

const userInitial = computed(() => {
  const name = displayName.value;
  return name.charAt(0).toUpperCase();
});

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const navigateToFlashcards = () => {
  router.push('/flashcards');
  showDropdown.value = false;
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    showDropdown.value = false;
  } catch (error) {
    console.error('Logout error:', error);
  }
};

// Close dropdown when clicking outside
const closeDropdown = (event: Event) => {
  const target = event.target as Element;
  if (!target.closest('.user-profile')) {
    showDropdown.value = false;
  }
};

// Add event listener when component mounts
import { onMounted, onUnmounted } from 'vue';

onMounted(() => {
  document.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown);
});
</script>

<style scoped>
.user-profile {
  position: relative;
  display: inline-block;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 20px;
  background: var(--bg-primary);
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: var(--border-color);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-blue);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.dropdown-arrow {
  font-size: 10px;
  color: var(--text-secondary);
  transition: transform 0.2s;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  z-index: 1000;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 14px;
  color: var(--text-primary);
}

.dropdown-item:hover {
  background: var(--bg-primary);
}

.dropdown-item .icon {
  font-size: 16px;
}
</style> 