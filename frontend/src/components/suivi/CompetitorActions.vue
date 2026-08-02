<script setup lang="ts">
defineProps<{
  departed: boolean;
  dns: boolean;
  abandoned: boolean;
  trackerReturned: boolean;
  trackerNumber: string | null;
}>();

defineEmits<{
  abandon: [];
  "cancel-abandon": [];
  "tracker-returned": [];
  "cancel-tracker-returned": [];
}>();
</script>

<template>
  <div class="section-actions">
    <button
      v-if="!abandoned && departed && !dns"
      class="action-btn abandon-btn"
      @click="$emit('abandon')"
    >
      Abandonner
    </button>
    <button
      v-if="abandoned"
      class="action-btn cancel-abandon-btn"
      @click="$emit('cancel-abandon')"
    >
      Annuler l'abandon
    </button>
    <button
      v-if="!trackerReturned && trackerNumber"
      class="action-btn tracker-btn"
      @click="$emit('tracker-returned')"
    >
      Tracker rendu
    </button>
    <button
      v-if="trackerReturned"
      class="action-btn cancel-tracker-btn"
      @click="$emit('cancel-tracker-returned')"
    >
      Annuler le rendu
    </button>
  </div>
</template>

<style scoped>
.section-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
  background: #fff;
}

.abandon-btn { color: #f44336; border-color: #f44336; }
.abandon-btn:hover { background: #ffebee; }
.cancel-abandon-btn { color: #ff9800; border-color: #ff9800; }
.cancel-abandon-btn:hover { background: #fff3e0; }
.tracker-btn { color: #4caf50; border-color: #4caf50; }
.tracker-btn:hover { background: #e8f5e9; }
.cancel-tracker-btn { color: #ff9800; border-color: #ff9800; }
.cancel-tracker-btn:hover { background: #fff3e0; }
</style>

