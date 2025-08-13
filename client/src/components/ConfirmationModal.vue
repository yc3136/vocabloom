<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="show" @click="handleOverlayClick">
      <div class="modal-content confirmation-modal" @click.stop>
        <div class="modal-header">
          <div class="header-content">
            <div class="icon-container" :class="type">
              <span class="icon">{{ icon }}</span>
            </div>
            <h2>{{ title }}</h2>
          </div>
          <button class="close-btn" @click="handleCancel">&times;</button>
        </div>
        
        <div class="modal-body">
          <p class="message">{{ message }}</p>
          <div v-if="details" class="details">
            {{ details }}
          </div>
        </div>
        
        <div class="modal-footer">
          <button 
            @click="handleCancel" 
            class="btn btn--secondary"
            :disabled="loading"
          >
            {{ cancelText }}
          </button>
          <button 
            @click="handleConfirm" 
            class="btn"
            :class="confirmButtonClass"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  show: boolean;
  title: string;
  message: string;
  details?: string;
  type?: 'danger' | 'warning' | 'info';
  confirmText?: string;
  cancelText?: string;
  loading?: boolean;
  preventClose?: boolean;
}

interface Emits {
  (e: 'confirm'): void;
  (e: 'cancel'): void;
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'warning',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loading: false,
  preventClose: false
});

const emit = defineEmits<Emits>();

const icon = computed(() => {
  switch (props.type) {
    case 'danger': return '⚠️';
    case 'warning': return '⚠️';
    case 'info': return 'ℹ️';
    default: return '⚠️';
  }
});

const confirmButtonClass = computed(() => {
  switch (props.type) {
    case 'danger': return 'btn--danger';
    case 'warning': return 'btn--warning';
    case 'info': return 'btn--primary';
    default: return 'btn--warning';
  }
});

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm');
  }
};

const handleCancel = () => {
  if (!props.loading && !props.preventClose) {
    emit('cancel');
    emit('close');
  }
};

const handleOverlayClick = () => {
  if (!props.preventClose) {
    handleCancel();
  }
};
</script>

<style>
.confirmation-modal {
  max-width: 480px;
  width: 100%;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-primary);
}

.icon-container.danger {
  background: rgba(248, 113, 113, 0.1);
}

.icon-container.warning {
  background: rgba(251, 191, 36, 0.1);
}

.icon-container.info {
  background: rgba(56, 189, 248, 0.1);
}

.icon {
  font-size: 1.25rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-body {
  padding: 20px 24px;
}

.message {
  margin: 0 0 12px 0;
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.5;
}

.details {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.modal-footer {
  padding: 16px 24px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 80px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--border-color);
}

.btn--primary {
  background: var(--primary-blue);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: var(--blue-hover);
}

.btn--warning {
  background: var(--warning-amber);
  color: white;
}

.btn--warning:hover:not(:disabled) {
  background: #f59e0b;
}

.btn--danger {
  background: var(--error-red);
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background: #ef4444;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .confirmation-modal {
    margin: 16px;
    max-width: none;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
  }
}
</style> 