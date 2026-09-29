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

// Token management helpers
export const tokenStorage = {
  getAccess: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("certiflow_access_token");
  },
  getRefresh: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("certiflow_refresh_token");
  },
  setTokens: (access: string, refresh: string) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("certiflow_access_token", access);
    localStorage.setItem("certiflow_refresh_token", refresh);
  },
  clearTokens: () => {
    if (typeof window === "undefined") return;
    localStorage.removeItem("certiflow_access_token");
    localStorage.removeItem("certiflow_refresh_token");
  },
  isAuthenticated: (): boolean => {
    return !!tokenStorage.getAccess();
  },
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
  const refresh = tokenStorage.getRefresh();
  if (!refresh) return false;

  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!res.ok) {
        tokenStorage.clearTokens();
        return false;
      }

      const json = await res.json();
      const data = json.data || json;
      if (data.access_token) {
        tokenStorage.setTokens(data.access_token, data.refresh_token || refresh);
        return true;
      }
      return false;
    } catch {
      tokenStorage.clearTokens();
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Core HTTP Request Wrapper
 */
export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
  const headers = new Headers(options.headers || {});

  // Automatically attach Authorization header if available
  const token = tokenStorage.getAccess();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // Attach X-Organization-Id header if available
  const orgId = orgStorage.getOrgId();
  if (orgId && !headers.has("X-Organization-Id")) {
    headers.set("X-Organization-Id", orgId);
  }

  // Set default JSON Content-Type unless body is FormData
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle token refresh on 401 Unauthorized
    if (response.status === 401 && tokenStorage.getRefresh()) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        headers.set("Authorization", `Bearer ${tokenStorage.getAccess()}`);
        const retryResponse = await fetch(url, { ...options, headers });
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
