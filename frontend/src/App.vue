<script setup lang="ts">
import ToastNotification from "./components/ToastNotification.vue";
import PromptModal from "./components/PromptModal.vue";
import ReloadPrompt from "./components/ReloadPrompt.vue";
import { usePrompt } from "./composables/usePrompt";

const promptState = usePrompt();
</script>

<template>
  <router-view />
  <ToastNotification />
  <ReloadPrompt />
  <PromptModal
    :visible="promptState.visible.value"
    :title="promptState.title.value"
    :placeholder="promptState.placeholder.value"
    :default-value="promptState.defaultValue.value"
    @confirm="promptState.handleConfirm"
    @cancel="promptState.handleCancel"
  />
</template>
