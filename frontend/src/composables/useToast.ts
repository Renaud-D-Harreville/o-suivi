import { ref } from "vue";

export type ToastType = "error" | "success" | "info";

interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

const toasts = ref<ToastMessage[]>([]);
let nextId = 0;

const DURATION_MS = 4000;

function showToast(message: string, type: ToastType = "info"): void {
  const id = nextId++;
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    removeToast(id);
  }, DURATION_MS);
}

function removeToast(id: number): void {
  const idx = toasts.value.findIndex((t) => t.id === id);
  if (idx >= 0) toasts.value.splice(idx, 1);
}

export function useToast() {
  return {
    toasts,
    showToast,
    removeToast,
    showError: (msg: string) => showToast(msg, "error"),
    showSuccess: (msg: string) => showToast(msg, "success"),
    showInfo: (msg: string) => showToast(msg, "info"),
  };
}

