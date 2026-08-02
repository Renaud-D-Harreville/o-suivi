import { ref, onMounted, onUnmounted } from "vue";
import { useEventStore } from "../stores/event-store";

const INITIAL_DELAY_MS = 1000;
const MAX_DELAY_MS = 30000;
const BACKOFF_FACTOR = 2;

export function useWebSocket(eventId: string) {
  const connected = ref(false);

  let ws: WebSocket | null = null;
  let reconnectDelay = INITIAL_DELAY_MS;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let refreshTimer: ReturnType<typeof setTimeout> | null = null;
  let stopped = false;

  const store = useEventStore();

  function getWsUrl(): string {
    const token = localStorage.getItem("token");
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${location.host}/api/events/${eventId}/ws?token=${token}`;
  }

  function debouncedRefresh() {
    if (refreshTimer) clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => {
      store.fetchTracking(eventId, true);
    }, 100);
  }

  function connect() {
    if (stopped) return;
    clearReconnectTimer();

    ws = new WebSocket(getWsUrl());

    ws.onopen = () => {
      connected.value = true;
      reconnectDelay = INITIAL_DELAY_MS;
      store.fetchTracking(eventId, true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "refresh") {
          debouncedRefresh();
        }
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      connected.value = false;
      ws = null;
      scheduleReconnect();
    };

    ws.onerror = () => {
      ws?.close();
    };
  }

  function scheduleReconnect() {
    if (stopped || document.hidden) return;
    reconnectTimer = setTimeout(() => {
      connect();
      reconnectDelay = Math.min(reconnectDelay * BACKOFF_FACTOR, MAX_DELAY_MS);
    }, reconnectDelay);
  }

  function clearReconnectTimer() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function reconnect() {
    reconnectDelay = INITIAL_DELAY_MS;
    connect();
  }

  function handleVisibilityChange() {
    if (document.hidden) {
      clearReconnectTimer();
    } else {
      if (!connected.value) {
        reconnect();
      }
    }
  }

  function cleanup() {
    stopped = true;
    clearReconnectTimer();
    if (refreshTimer) {
      clearTimeout(refreshTimer);
      refreshTimer = null;
    }
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    if (ws) {
      ws.onclose = null;
      ws.close();
      ws = null;
    }
  }

  onMounted(() => {
    document.addEventListener("visibilitychange", handleVisibilityChange);
    connect();
  });

  onUnmounted(cleanup);

  return { connected, reconnect };
}

