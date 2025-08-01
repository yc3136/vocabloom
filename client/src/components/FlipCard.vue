<template>
  <div class="flip-card-container" @click="toggleFlip">
    <div class="flip-card" :class="{ 'flipped': isFlipped }">
      <!-- Front of card -->
      <div class="card-front">
        <div class="card-content">
          <div class="word-display">
            <input 
              v-if="editable"
              v-model="frontContent"
              class="word-input"
              placeholder="Enter word"
              @click.stop
            />
            <span v-else class="word-text">{{ frontContent || 'Enter word' }}</span>
          </div>
          <div class="flip-hint" v-if="!editable">
            <span>Click to flip</span>
          </div>
        </div>
      </div>
      
      <!-- Back of card -->
      <div class="card-back">
        <div class="card-content">
          <div class="translation-section">
            <input 
              v-if="editable"
              v-model="backContent.translation"
              class="translation-input"
              placeholder="Enter translation"
              @click.stop
            />
            <span v-else class="translation-text">{{ backContent.translation || 'Translation' }}</span>
          </div>
          
          <div class="examples-section" v-if="backContent.examples && backContent.examples.length > 0">
            <div class="example-navigation" v-if="!editable && backContent.examples.length > 1">
              <button 
                @click.stop="previousExample" 
                class="nav-btn"
                :disabled="currentExampleIndex === 0"
              >
                &lt;
              </button>
              <div class="example-content">
                <textarea 
                  v-if="editable"
                  v-model="backContent.examples[currentExampleIndex]"
                  class="example-input"
                  placeholder="Enter example sentence"
                  @click.stop
                />
                <span v-else class="example-text">{{ backContent.examples[currentExampleIndex] || 'Example sentence' }}</span>
              </div>
              <button 
                @click.stop="nextExample" 
                class="nav-btn"
                :disabled="currentExampleIndex === backContent.examples.length - 1"
              >
                &gt;
              </button>
            </div>
            
            <div class="example-content" v-else>
              <textarea 
                v-if="editable"
                v-model="backContent.examples[currentExampleIndex]"
                class="example-input"
                placeholder="Enter example sentence"
                @click.stop
              />
              <span v-else class="example-text">{{ backContent.examples[currentExampleIndex] || 'Example sentence' }}</span>
            </div>
          </div>
          
          <div class="flip-hint" v-if="!editable">
            <span>Click to flip back</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface Props {
  frontContent: string
  backContent: {
    translation: string
    examples: string[]
  }
  editable?: boolean
}

interface Emits {
  (e: 'update:frontContent', value: string): void
  (e: 'update:backContent', value: { translation: string, examples: string[] }): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

const isFlipped = ref(false)
const currentExampleIndex = ref(0)

// Computed properties for two-way binding
const frontContent = computed({
  get: () => props.frontContent,
  set: (value: string) => emit('update:frontContent', value)
})

const backContent = computed({
  get: () => props.backContent,
  set: (value: { translation: string, examples: string[] }) => emit('update:backContent', value)
})

const toggleFlip = () => {
  if (!props.editable) {
    isFlipped.value = !isFlipped.value
  }
}

const nextExample = () => {
  if (currentExampleIndex.value < props.backContent.examples.length - 1) {
    currentExampleIndex.value++
  }
}

const previousExample = () => {
  if (currentExampleIndex.value > 0) {
    currentExampleIndex.value--
  }
}

// Reset flip state when content changes
watch(() => props.frontContent, () => {
  if (props.editable) {
    isFlipped.value = false
  }
})
</script>

<style scoped>
.flip-card-container {
  perspective: 1000px;
  width: 100%;
  height: 300px;
  cursor: pointer;
}

.flip-card {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.6s ease-in-out;
}

.flip-card.flipped {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  background: var(--bg-surface, #ffffff);
  border: 2px solid var(--border-color, #e2e8f0);
}

.card-back {
  transform: rotateY(180deg);
}

.card-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

/* Front card styles */
.word-display {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.word-input,
.word-text {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  text-align: center;
  width: 100%;
  max-width: 300px;
}

.word-input {
  background: transparent;
  border: none;
  outline: none;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.word-input:focus {
  background: var(--bg-primary, #f8fafc);
}

/* Back card styles */
.translation-section {
  margin-bottom: 1.5rem;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.translation-input,
.translation-text {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--primary-blue, #6690ff);
  text-align: center;
  width: 100%;
  max-width: 300px;
}

.translation-input {
  background: transparent;
  border: none;
  outline: none;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.translation-input:focus {
  background: var(--bg-primary, #f8fafc);
}

.examples-section {
  width: 100%;
  max-width: 400px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.example-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  height: 100%;
}

.nav-btn {
  background: transparent;
  color: var(--primary-blue, #6690ff);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.2s;
  flex-shrink: 0;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(102, 144, 255, 0.1);
  color: var(--blue-hover, #4a7aff);
  transform: scale(1.1);
}

.nav-btn:disabled {
  color: var(--text-secondary, #64748b);
  cursor: not-allowed;
  transform: none;
  opacity: 0.5;
}

.example-content {
  flex: 1;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 1rem;
}

.example-input,
.example-text {
  font-size: 1rem;
  color: var(--text-primary, #1e293b);
  text-align: center;
  line-height: 1.5;
  font-style: italic;
  width: 100%;
  max-height: 100px;
  overflow-y: auto;
}

.example-input {
  background: transparent;
  border: none;
  outline: none;
  padding: 0.5rem;
  border-radius: 8px;
  resize: none;
  transition: background-color 0.2s;
}

.example-input:focus {
  background: var(--bg-primary, #f8fafc);
}

.flip-hint {
  position: absolute;
  bottom: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary, #64748b);
  opacity: 0.7;
}

/* Responsive design */
@media (max-width: 768px) {
  .flip-card-container {
    height: 250px;
  }
  
  .card-content {
    padding: 1.5rem;
  }
  
  .word-input,
  .word-text {
    font-size: 1.5rem;
  }
  
  .translation-input,
  .translation-text {
    font-size: 1.2rem;
  }
  
  .example-input,
  .example-text {
    font-size: 0.9rem;
  }
}
</style> 