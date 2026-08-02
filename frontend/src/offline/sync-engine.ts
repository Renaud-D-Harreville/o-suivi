import { db } from "./db";
import type { PendingAction } from "./pending-action";
import { ref } from "vue";

const MAX_RETRIES = 5;
const SYNC_INTERVAL_MS = 60_000;

export const pendingCount = ref(0);
export const syncing = ref(false);
export const online = ref(navigator.onLine);

let intervalId: ReturnType<typeof setInterval> | null = null;
let started = false;

export async function refreshPendingCount(): Promise<void> {
  pendingCount.value = await db.pendingActions
    .filter((a) => !a.failed)
    .count();
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function replayAction(action: PendingAction): Promise<"success" | "retry" | "stop"> {
  try {
    const init: RequestInit = {
      method: action.method,
      headers: getAuthHeaders(),
    };
    if (action.body) {
      init.body = action.body;
    }
    const response = await fetch(action.url, init);

    if (response.ok) {
      return "success";
    }

    // 4xx — action likely already applied (deduplication) or validation error
    if (response.status >= 400 && response.status < 500) {
      return "success";
    }

    // 5xx — server error, retry later
    return "retry";
  } catch {
    // Network error — stop flushing
    return "stop";
  }
}

export async function flush(): Promise<void> {
  if (syncing.value) return;
  syncing.value = true;

  try {
    const actions = await db.pendingActions
      .orderBy("createdAt")
      .filter((a) => !a.failed)
      .toArray();

    for (const action of actions) {
      const result = await replayAction(action);

      if (result === "success") {
        await db.pendingActions.delete(action.id!);
      } else if (result === "retry") {
        const newRetryCount = action.retryCount + 1;
        await db.pendingActions.update(action.id!, {
          retryCount: newRetryCount,
          failed: newRetryCount >= MAX_RETRIES,
        });
      } else {
        // "stop" — network error, abort flush
        break;
      }
    }
  } finally {
    syncing.value = false;
    await refreshPendingCount();
  }
}

export async function enqueue(
  url: string,
  method: string,
  body: string | null,
): Promise<void> {
  const action: PendingAction = {
    url,
    method,
    body,
    createdAt: new Date().toISOString(),
    retryCount: 0,
    failed: false,
  };
  await db.pendingActions.add(action);
  await refreshPendingCount();
}

export async function dequeueByUrl(url: string, method: string, body: string | null): Promise<void> {
  // Remove the most recent matching pending action (successful immediate send)
  const matches = await db.pendingActions
    .where("createdAt")
    .above("")
    .filter((a) => a.url === url && a.method === method && a.body === body)
    .sortBy("createdAt");

  const last = matches[matches.length - 1];
  if (last?.id) {
    await db.pendingActions.delete(last.id);
    await refreshPendingCount();
  }
}

function handleOnline(): void {
  online.value = true;
  flush();
}

function handleOffline(): void {
  online.value = false;
}

function handleVisibilityChange(): void {
  if (!document.hidden && online.value) {
    flush();
  }
}

export function start(): void {
  if (started) return;
  started = true;

  window.addEventListener("online", handleOnline);
  window.addEventListener("offline", handleOffline);
  document.addEventListener("visibilitychange", handleVisibilityChange);

  intervalId = setInterval(() => {
    if (online.value && !syncing.value) {
      flush();
    }
  }, SYNC_INTERVAL_MS);

  // Initial state
  online.value = navigator.onLine;
  refreshPendingCount();

  // Flush any leftover actions from previous session
  if (online.value) {
    flush();
  }
}

export function stop(): void {
  started = false;
  window.removeEventListener("online", handleOnline);
  window.removeEventListener("offline", handleOffline);
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}





