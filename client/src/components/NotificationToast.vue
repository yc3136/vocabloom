<template>
  <div v-if="show && message" class="notification-toast" :class="type">
    <div class="notification-content">
      <span class="notification-icon">{{ icon }}</span>
      <span class="notification-message">{{ message }}</span>
    </div>
    <button @click="close" class="notification-close">&times;</button>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue';

interface Props {
  show: boolean;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

interface Emits {
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 5000
});

const emit = defineEmits<Emits>();

const timeoutId = ref<number | null>(null);

const icon = computed(() => {
  switch (props.type) {
    case 'success': return '✅';
    case 'error': return '❌';
    case 'info': return 'ℹ️';
    default: return 'ℹ️';
  }
});

const close = () => {
  // Clear any existing timeout
  if (timeoutId.value) {
    clearTimeout(timeoutId.value);
    timeoutId.value = null;
  }
  emit('close');
};

// Watch for changes in show prop and set up auto-dismiss
watch(() => props.show, (newShow) => {
  // Clear any existing timeout
  if (timeoutId.value) {
    clearTimeout(timeoutId.value);
    timeoutId.value = null;
  }
  
  // Set up new timeout when toast becomes visible
  if (newShow && props.duration > 0) {
    timeoutId.value = setTimeout(() => {
      close();
    }, props.duration);
  }
}, { immediate: true });
</script>

<style scoped>
.notification-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 400px;
  animation: slideIn 0.3s ease-out;
}

.notification-toast.success {
  background: color-mix(in srgb, var(--success-green) 15%, transparent);
  color: var(--success-green);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--success-green) 25%, transparent);
}

.notification-toast.error {
  background: color-mix(in srgb, var(--error-red) 15%, transparent);
  color: var(--error-red);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--error-red) 25%, transparent);
}

.notification-toast.info {
  background: color-mix(in srgb, var(--info-cyan) 15%, transparent);
  color: var(--info-cyan);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--info-cyan) 25%, transparent);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.notification-icon {
  font-size: 16px;
}

.notification-message {
  font-size: 14px;
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: 12px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.notification-close:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .notification-toast {
    bottom: 10px;
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
}
</style> 