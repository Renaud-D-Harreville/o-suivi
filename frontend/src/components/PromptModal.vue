<script setup lang="ts">
import { ref, watch, nextTick } from "vue";

const props = defineProps<{
  visible: boolean;
  title: string;
  placeholder?: string;
  defaultValue?: string;
}>();

const emit = defineEmits<{
  confirm: [value: string];
  cancel: [];
}>();

const inputValue = ref("");
const inputRef = ref<HTMLInputElement | null>(null);

watch(() => props.visible, async (v) => {
  if (v) {
    inputValue.value = props.defaultValue || "";
    await nextTick();
    inputRef.value?.focus();
  }
});

function handleConfirm() {
  if (inputValue.value.trim()) {
    emit("confirm", inputValue.value.trim());
  }
}
</script>

<template>
  <div v-if="visible" class="overlay" @click.self="emit('cancel')">
    <div class="modal">
      <h2>{{ title }}</h2>
      <input
        ref="inputRef"
        v-model="inputValue"
        type="text"
        :placeholder="placeholder || ''"
        class="prompt-input"
        @keyup.enter="handleConfirm"
        @keyup.escape="emit('cancel')"
      />
      <div class="actions">
        <button type="button" class="btn-cancel" @click="emit('cancel')">
          Annuler
        </button>
        <button
          type="button"
          class="btn-confirm"
          :disabled="!inputValue.trim()"
          @click="handleConfirm"
        >
          Confirmer
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.modal {
  background: var(--color-bg, #fff);
  border-radius: 8px;
  padding: 1.5rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

h2 {
  margin: 0 0 1rem;
  font-size: 1.125rem;
}

.prompt-input {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid var(--color-border-input, #ccc);
  border-radius: 4px;
  box-sizing: border-box;
  margin-bottom: 1rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: var(--color-bg-page, #e0e0e0);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: var(--color-primary, #1976d2);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm:not(:disabled):hover {
  background-color: var(--color-primary-dark, #1565c0);
}
</style>

