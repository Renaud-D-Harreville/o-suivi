<template>
  <div v-if="showIndicator" :class="['offline-indicator', statusClass]">
    <span class="offline-indicator__icon">{{ icon }}</span>
    <span class="offline-indicator__label">{{ statusLabel }}</span>
    <button
      v-if="!online && !syncing"
      class="offline-indicator__btn"
      @click="syncNow"
    >
      Synchroniser
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useOfflineStatus } from "../composables/useOfflineStatus";

const { online, syncing, statusLabel, showIndicator, syncNow } = useOfflineStatus();

const statusClass = computed(() => {
  if (syncing.value) return "offline-indicator--syncing";
  if (!online.value) return "offline-indicator--offline";
  return "offline-indicator--pending";
});

const icon = computed(() => {
  if (syncing.value) return "🔄";
  if (!online.value) return "🔴";
  return "🟡";
});
</script>

<style scoped>
.offline-indicator {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  z-index: 9999;
  justify-content: center;
}

.offline-indicator--offline {
  background: #fee2e2;
  color: #991b1b;
}

.offline-indicator--syncing {
  background: #dbeafe;
  color: #1e40af;
}

.offline-indicator--pending {
  background: #fef3c7;
  color: #92400e;
}

.offline-indicator__icon {
  font-size: 1rem;
}

.offline-indicator__btn {
  margin-left: 0.5rem;
  padding: 0.25rem 0.75rem;
  border: 1px solid currentColor;
  border-radius: 4px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 0.8rem;
}

.offline-indicator__btn:hover {
  opacity: 0.8;
}
</style>

