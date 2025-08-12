import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface NotificationOptions {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  allowHtml?: boolean;
}

export const useNotificationStore = defineStore('notification', () => {
  const show = ref(false);
  const message = ref('');
  const type = ref<'success' | 'error' | 'warning' | 'info'>('info');
  const allowHtml = ref(false);
  const duration = ref(5000); // Default 5 seconds

  const showNotification = (options: NotificationOptions | string) => {
    if (typeof options === 'string') {
      // Backward compatibility for simple string messages
      message.value = options;
      type.value = 'info';
      allowHtml.value = false;
      duration.value = 5000;
    } else {
      message.value = options.message;
      type.value = options.type || 'info';
      allowHtml.value = options.allowHtml || false;
      duration.value = options.duration || 5000;
    }
    
    show.value = true;
    
    // Auto-hide after duration
    if (duration.value > 0) {
      setTimeout(() => {
        hide();
      }, duration.value);
    }
  };

  const hide = () => {
    show.value = false;
    message.value = '';
    allowHtml.value = false;
    duration.value = 5000;
  };

  const success = (message: string, options?: Partial<NotificationOptions>) => {
    showNotification({
      message,
      type: 'success',
      ...options
    });
  };

  const error = (message: string, options?: Partial<NotificationOptions>) => {
    showNotification({
      message,
      type: 'error',
      ...options
    });
  };

  const info = (message: string, options?: Partial<NotificationOptions>) => {
    showNotification({
      message,
      type: 'info',
      ...options
    });
  };

  const warning = (message: string, options?: Partial<NotificationOptions>) => {
    showNotification({
      message,
      type: 'warning',
      ...options
    });
  };

  return {
    show,
    message,
    type,
    allowHtml,
    duration,
    showNotification,
    hide,
    success,
    error,
    warning,
    info
  };
}); 