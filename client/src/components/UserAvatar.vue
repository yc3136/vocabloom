<template>
  <div class="user-avatar" :class="{ 'small': size === 'small', 'medium': size === 'medium', 'large': size === 'large' }">
    {{ userInitial }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  email?: string;
  size?: 'small' | 'medium' | 'large';
}

const props = withDefaults(defineProps<Props>(), {
  email: '',
  size: 'medium'
});

const userInitial = computed(() => {
  const email = props.email;
  return email ? email.charAt(0).toUpperCase() : '?';
});
</script>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-blue);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.user-avatar.small {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.user-avatar.medium {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.user-avatar.large {
  width: 40px;
  height: 40px;
  font-size: 16px;
}
</style> 