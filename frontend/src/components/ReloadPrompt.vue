<script setup lang="ts">
import { useRegisterSW } from "virtual:pwa-register/vue";

const UPDATE_INTERVAL_MS = 60 * 60 * 1000; // check every hour

const {
  needRefresh,
  updateServiceWorker,
} = useRegisterSW({
  onRegisteredSW(_swUrl, registration) {
    if (!registration) return;
    setInterval(() => {
      registration.update();
    }, UPDATE_INTERVAL_MS);
  },
});

function close() {
  needRefresh.value = false;
}
</script>

<template>
  <div v-if="needRefresh" class="reload-prompt" role="alert">
    <span class="reload-prompt__message">
      Nouvelle version disponible
    </span>
    <button class="reload-prompt__btn reload-prompt__btn--primary" @click="updateServiceWorker()">
      Recharger
    </button>
    <button class="reload-prompt__btn reload-prompt__btn--dismiss" @click="close">
      ✕
    </button>
  </div>
</template>

<style scoped>
.reload-prompt {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--color-primary-dark, #1565c0);
  color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10000;
  font-size: 0.9rem;
}

.reload-prompt__message {
  white-space: nowrap;
}

.reload-prompt__btn {
  border: none;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.85rem;
  padding: 0.4rem 0.75rem;
}

.reload-prompt__btn--primary {
  background: #fff;
  color: var(--color-primary-dark, #1565c0);
  font-weight: 600;
}

.reload-prompt__btn--dismiss {
  background: transparent;
  color: #fff;
  font-size: 1rem;
  padding: 0.25rem 0.5rem;
}
</style>

