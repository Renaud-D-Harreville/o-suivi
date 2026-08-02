import router from "../router";
import { useToast } from "../composables/useToast";
import { enqueue, dequeueByUrl } from "../offline/sync-engine";

function getToken(): string | null {
  return localStorage.getItem("token");
}

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (!payload.exp) return false;
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
}

function handleAuthFailure(): void {
  localStorage.removeItem("token");
  router.push("/login");
}

const MUTATION_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

function isMutationRequest(options: RequestInit): boolean {
  const method = (options.method || "GET").toUpperCase();
  return MUTATION_METHODS.has(method);
}

/**
 * Centralized fetch wrapper.
 * - Injects JWT auth header automatically
 * - Checks JWT expiration before each call
 * - Redirects to /login on 401
 * - Queues mutation requests in IndexedDB for offline resilience
 * - Surfaces network errors via toast (GET only — mutations are queued silently)
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  const token = getToken();

  if (token && isTokenExpired(token)) {
    handleAuthFailure();
    const { showError } = useToast();
    showError("Session expirée — veuillez vous reconnecter");
    return Promise.reject(new Error("Token expired"));
  }

  const headers = new Headers(options.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const method = (options.method || "GET").toUpperCase();
  const isMutation = isMutationRequest(options);
  const bodyStr = typeof options.body === "string" ? options.body : null;

  // For mutations: enqueue in IndexedDB before attempting the network call
  if (isMutation) {
    await enqueue(url, method, bodyStr);
  }

  try {
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      handleAuthFailure();
      const { showError } = useToast();
      showError("Session expirée — veuillez vous reconnecter");
      // Remove from queue — auth issue, not a network issue
      if (isMutation) {
        await dequeueByUrl(url, method, bodyStr);
      }
      return response;
    }

    // Success — remove from pending queue
    if (isMutation && response.ok) {
      await dequeueByUrl(url, method, bodyStr);
    }

    return response;
  } catch (error) {
    if (isMutation) {
      // Mutation is safely queued — notify user but don't throw
      const { showInfo } = useToast();
      showInfo("Action enregistrée — sera synchronisée au retour réseau");
      // Return a synthetic response so callers don't crash
      return new Response(null, { status: 202, statusText: "Queued Offline" });
    }
    const { showError } = useToast();
    showError("Erreur réseau — vérifiez votre connexion");
    throw error;
  }
}

