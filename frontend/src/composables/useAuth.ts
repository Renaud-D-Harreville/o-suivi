export function useAuth() {
  function getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  return { getAuthHeaders };
}

