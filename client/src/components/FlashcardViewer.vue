<template>
  <div class="flashcard-viewer-overlay" v-if="show" @click="closeViewer">
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
}
</style> 