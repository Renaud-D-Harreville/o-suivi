<script setup lang="ts">
import ToastNotification from "./components/ToastNotification.vue";
import PromptModal from "./components/PromptModal.vue";
import ReloadPrompt from "./components/ReloadPrompt.vue";
import OfflineIndicator from "./components/OfflineIndicator.vue";
import { usePrompt } from "./composables/usePrompt";
import { start as startSyncEngine } from "./offline/sync-engine";

const promptState = usePrompt();

startSyncEngine();
</script>

<template>
  <router-view />
  <ToastNotification />
  <ReloadPrompt />
  <OfflineIndicator />
  <PromptModal
    :visible="promptState.visible.value"
    :title="promptState.title.value"
    :placeholder="promptState.placeholder.value"
    :default-value="promptState.defaultValue.value"
    @confirm="promptState.handleConfirm"
    @cancel="promptState.handleCancel"
  />
</template>
