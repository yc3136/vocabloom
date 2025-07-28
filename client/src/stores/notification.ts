import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
  const show = ref(false);
  const message = ref('');
  const type = ref<'success' | 'error' | 'info'>('info');

  const showNotification = (msg: string, notificationType: 'success' | 'error' | 'info' = 'info') => {
    message.value = msg;
    type.value = notificationType;
    show.value = true;
  };

  const hide = () => {
    show.value = false;
    message.value = '';
  };

  const success = (msg: string) => showNotification(msg, 'success');
  const error = (msg: string) => showNotification(msg, 'error');
  const info = (msg: string) => showNotification(msg, 'info');

  return {
    show,
    message,
    type,
    showNotification,
    hide,
    success,
    error,
    info
  };
}); 