<template>
  <div class="flashcard-viewer-overlay" v-if="show" @click="closeViewer">
    <div class="flashcard-viewer" @click.stop>
      <div class="viewer-header">
        <h2>Flashcard</h2>
        <div class="viewer-actions">
          <button @click="closeViewer" class="close-btn">&times;</button>
        </div>
      </div>
      
      <div class="viewer-content">
        <FlipCard
          :front-content="flashcard.original_word"
          :back-content="{
            translation: flashcard.translated_word,
            examples: flashcard.example_sentences || []
          }"
          :editable="false"
        />
      </div>
      
      <div class="viewer-footer">
        <div class="flashcard-meta">
          <span class="template-badge">{{ flashcard.target_language || 'Language' }}</span>
          <span class="date">{{ formatDate(flashcard.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import FlipCard from './FlipCard.vue';

interface Props {
  show: boolean;
  flashcard: {
    id: number;
    original_word: string;
    translated_word: string;
    example_sentences?: string[];
    template?: string;
    created_at: string;
    target_language?: string;
  };
}

interface Emits {
  (e: 'close'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const closeViewer = () => {
  emit('close');
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};
</script>

<style scoped>
.flashcard-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.flashcard-viewer {
  background: var(--bg-surface);
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.viewer-header h2 {
  margin: 0;
  color: var(--text-primary, #1e293b);
  font-size: 1.5rem;
  font-weight: 600;
}

.viewer-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary, #64748b);
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: var(--bg-primary, #f8fafc);
  color: var(--text-primary, #1e293b);
}

.viewer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 350px;
  margin-bottom: 2rem;
}

.viewer-footer {
  border-top: 1px solid var(--border-color, #e2e8f0);
  padding-top: 1rem;
}

.flashcard-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.template-badge {
  background: rgba(102, 144, 255, 0.1);
  color: var(--primary-blue, #6690ff);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.date {
  color: var(--text-secondary, #64748b);
}

/* Responsive design */
@media (max-width: 768px) {
  .flashcard-viewer {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .viewer-header h2 {
    font-size: 1.25rem;
  }
  
  .viewer-actions {
    gap: 0.5rem;
  }
  
  .action-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
}
</style> 