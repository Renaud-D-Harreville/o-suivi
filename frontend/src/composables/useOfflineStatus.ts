import { computed } from "vue";
import { online, syncing, pendingCount, flush } from "../offline/sync-engine";

export function useOfflineStatus() {
  const statusLabel = computed(() => {
    if (syncing.value) return "Synchronisation en cours...";
    if (!online.value) return `Hors-ligne — ${pendingCount.value} action(s) en attente`;
    if (pendingCount.value > 0) return `${pendingCount.value} action(s) en attente`;
    return "";
  });

  const showIndicator = computed(() => {
    return !online.value || syncing.value || pendingCount.value > 0;
  });

  function syncNow(): void {
    flush();
  }

  return {
    online,
    syncing,
    pendingCount,
    statusLabel,
    showIndicator,
    syncNow,
  };
}

