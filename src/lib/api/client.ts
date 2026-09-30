/**
 * CertiFlow Base HTTP Client
 * Manages authorization tokens, organization context headers, and error handling.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiEnvelope<T = any> {
  success: boolean;
  data: T;
  error: {
    code: string;
    message: string;
    details?: any;
  } | null;
  request_id?: string;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
    has_next?: boolean;
  };
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: any;

  constructor(message: string, code = "API_ERROR", status = 500, details?: any) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

// CSRF token extractor from document.cookie
export function getCsrfToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp("(?:^|;\\s*)certiflow_csrf_token=([^;]*)"));
  return match ? decodeURIComponent(match[1]) : null;
}

// Session management helpers (P13.1 — tokens reside purely in HttpOnly cookies)
export const tokenStorage = {
  getAccess: (): string | null => null,
  getRefresh: (): string | null => null,
  setTokens: (_access: string, _refresh?: string | null) => {},
  clearTokens: () => {},
  isAuthenticated: (): boolean => {
    // Session presence indicated by CSRF token cookie existence
    if (typeof document === "undefined") return false;
    return !!getCsrfToken();
  },
  isDemoMode: (): boolean => false,
  setDemoMode: (_enabled: boolean) => {},
};

// Organization context helper
export const orgStorage = {
  getOrgId: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("certiflow_org_id");
  },
  setOrgId: (orgId: string) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("certiflow_org_id", orgId);
  },
};

let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const csrf = getCsrfToken();
      if (csrf) {
        headers["X-CSRF-Token"] = csrf;
      }
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: "POST",
        headers,
        credentials: "include",
      });

      return res.ok;
    } catch {
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Core HTTP Request Wrapper (P13.1 Hardened)
 * - Automatically sends credentials: "include" for HttpOnly session cookies
 * - Automatically attaches X-CSRF-Token header on state-mutating requests
 * - Seamlessly rotates sessions on 401 Unauthorized
 */
export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
  const headers = new Headers(options.headers || {});
  const method = (options.method || "GET").toUpperCase();

  // Attach X-Organization-Id header if available
  const orgId = orgStorage.getOrgId();
  if (orgId && !headers.has("X-Organization-Id")) {
    headers.set("X-Organization-Id", orgId);
  }

  // Attach CSRF protection header for mutating browser requests (P13.1)
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrf = getCsrfToken();
    if (csrf && !headers.has("X-CSRF-Token")) {
      headers.set("X-CSRF-Token", csrf);
    }
  }

  // Set default JSON Content-Type unless body is FormData
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  try {
    const response = await fetch(url, {
      ...options,
      credentials: options.credentials || "include",
      headers,
    });

    // Handle token refresh on 401 Unauthorized (unless already calling auth endpoints)
    if (
      response.status === 401 &&
      !endpoint.includes("/auth/login") &&
      !endpoint.includes("/auth/refresh") &&
      !endpoint.includes("/auth/logout")
    ) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        const csrf = getCsrfToken();
        if (csrf && ["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
          headers.set("X-CSRF-Token", csrf);
        }
        const retryResponse = await fetch(url, {
          ...options,
          credentials: options.credentials || "include",
          headers,
        });
        return handleResponse<T>(retryResponse);
      }
    }

    return handleResponse<T>(response);
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      err.message || "Failed to communicate with backend server",
      "NETWORK_ERROR",
      0
    );
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  let json: any = null;
  const contentType = response.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
    json = await response.json();
  }

  if (!response.ok) {
    const message =
      json?.error?.message ||
      json?.detail ||
      json?.message ||
      `HTTP Error ${response.status}: ${response.statusText}`;
    const code = json?.error?.code || `HTTP_${response.status}`;
    const details = json?.error?.details || json;
    throw new ApiError(message, code, response.status, details);
  }

  if (json && typeof json === "object" && "success" in json && "data" in json) {
    return json.data as T;
  }

  return (json !== null ? json : (response as any)) as T;
}
