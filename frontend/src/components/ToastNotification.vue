<script setup lang="ts">
import { useToast } from "../composables/useToast";

const { toasts, removeToast } = useToast();
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="removeToast(toast.id)"
      >
        {{ toast.message }}
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 90vw;
  pointer-events: none;
}

.toast {
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: auto;
  animation: toast-in 0.25s ease-out;
}

.toast-error {
  background: var(--color-error-dark, #d32f2f);
  color: #fff;
}

.toast-success {
  background: var(--color-success-bg, #2e7d32);
  color: #fff;
}

.toast-info {
  background: var(--color-text, #333);
  color: #fff;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

