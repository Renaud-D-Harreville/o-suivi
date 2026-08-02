import router from "../router";
import { useToast } from "../composables/useToast";

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

/**
 * Centralized fetch wrapper.
 * - Injects JWT auth header automatically
 * - Checks JWT expiration before each call
 * - Redirects to /login on 401
 * - Surfaces network errors via toast
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

  try {
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      handleAuthFailure();
      const { showError } = useToast();
      showError("Session expirée — veuillez vous reconnecter");
      return response;
    }

    return response;
  } catch (error) {
    const { showError } = useToast();
    showError("Erreur réseau — vérifiez votre connexion");
    throw error;
  }
}

