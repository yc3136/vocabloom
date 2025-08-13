<template>
  <div class="flashcard-viewer-overlay" v-if="show" @click="closeViewer">
    <div class="flashcard-container">
      <FlipCard
        :front-content="flashcard.original_word"
        :back-content="{
          translation: flashcard.translated_word,
          examples: flashcard.example_sentences || []
        }"
        :editable="false"
        @click.stop
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import FlipCard from './FlipCard.vue';

interface Props {
  show: boolean;
  flashcard: {
    id: number;
    original_word: string;
    translated_word: string;
    example_sentences?: string[];
    created_at: string;
    target_language?: string;
  };
}

interface Emits {
  (e: 'close'): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

const closeViewer = () => {
  emit('close');
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
  cursor: pointer;
  /* Remove any potential flash effects */
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Enhanced overlay for dark mode */
[data-theme="dark"] .flashcard-viewer-overlay {
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.flashcard-container {
  width: 90vw;
  max-width: 35rem;
  height: 60vh;
  max-height: 25rem;
  min-width: 20rem;
  min-height: 15rem;
}

/* Remove focus outline from the overlay */
.flashcard-viewer-overlay:focus {
  outline: none;
}

/* Ensure no blue flash on any child elements */
.flashcard-viewer-overlay * {
  -webkit-tap-highlight-color: transparent;
}

.flashcard-viewer-overlay *:focus {
  outline: none;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .flashcard-container {
    width: 95vw;
    height: 50vh;
    max-width: none;
    max-height: none;
  }
}

@media (max-width: 480px) {
  .flashcard-container {
    width: 98vw;
    height: 60vh;
    min-height: 18rem;
  }
}
</style> 