<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  title: string;
  visible: boolean;
}>();

const emit = defineEmits<{
  cancel: [];
  confirm: [name: string];
}>();

const name = ref("");

function handleConfirm() {
  if (name.value.trim()) {
    emit("confirm", name.value.trim());
    name.value = "";
  }
}

function handleCancel() {
  name.value = "";
  emit("cancel");
}
</script>

<template>
  <div v-if="visible" class="overlay" @click.self="handleCancel">
    <div class="modal">
      <h2>{{ title }}</h2>
      <div class="field">
        <label for="create-name">Nom</label>
        <input
          id="create-name"
          v-model="name"
          type="text"
          required
          @keyup.enter="handleConfirm"
        />
      </div>
      <div class="actions">
        <button type="button" class="btn-cancel" @click="handleCancel">
          Annuler
        </button>
        <button
          type="button"
          class="btn-confirm"
          :disabled="!name.trim()"
          @click="handleConfirm"
        >
          Créer
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
  background: #fff;
  border-radius: 8px;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

h2 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.5rem;
}

label {
  margin-bottom: 0.25rem;
  font-weight: 600;
}

input {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: #1976d2;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm:not(:disabled):hover {
  background-color: #1565c0;
}
</style>

