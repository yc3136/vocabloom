<template>
  <div v-if="show && message" class="notification-toast" :class="type">
    <div class="notification-content">
      <span class="notification-icon">{{ icon }}</span>
      <span 
        class="notification-message"
        v-if="!allowHtml"
      >{{ message }}</span>
      <span 
        class="notification-message"
        v-else
        v-html="message"
      ></span>
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
  allowHtml?: boolean;
}

interface Emits {
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 5000,
  allowHtml: false
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
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  min-width: 320px;
  max-width: 450px;
  animation: slideIn 0.3s ease-out;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.notification-toast.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
}

.notification-toast.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
}

.notification-toast.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.notification-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.notification-message {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.notification-message a {
  color: white;
  text-decoration: underline;
  font-weight: 600;
  transition: all 0.2s;
  padding: 2px 4px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
}

.notification-message a:hover {
  background: rgba(255, 255, 255, 0.2);
  text-decoration: none;
  transform: translateY(-1px);
}

.notification-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  margin-left: 12px;
  border-radius: 6px;
  transition: all 0.2s;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-close:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
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