import { ref, onMounted, onUnmounted } from "vue";
import { apiFetch } from "../utils/api";

export type GpsColor = "green" | "orange" | "red";

const POLL_INTERVAL_MS = 30_000;
const GREEN_THRESHOLD_MS = 60_000;
const ORANGE_THRESHOLD_MS = 600_000;

export function useGpsStatus(eventId: string) {
  const statuses = ref<Record<string, GpsColor>>({});
  let intervalId: number | undefined;

  function computeColor(lastTimestamp: string | null): GpsColor {
    if (!lastTimestamp) return "red";
    const age = Date.now() - new Date(lastTimestamp).getTime();
    if (age < GREEN_THRESHOLD_MS) return "green";
    if (age < ORANGE_THRESHOLD_MS) return "orange";
    return "red";
  }

  async function fetchStatus() {
    try {
      const res = await apiFetch(`/api/events/${eventId}/gps-status`);
      if (!res.ok) return;
      const data = await res.json();
      const result: Record<string, GpsColor> = {};
      for (const [userId, entry] of Object.entries(data.statuses)) {
        result[userId] = computeColor((entry as any).last_timestamp);
      }
      statuses.value = result;
    } catch {
      // silently ignore — keep last known state
    }
  }

  onMounted(() => {
    fetchStatus();
    intervalId = window.setInterval(fetchStatus, POLL_INTERVAL_MS);
  });

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
  });

  return { gpsStatuses: statuses };
}
