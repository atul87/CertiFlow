/**
 * CertiFlow Unified API Client
 * Connects Next.js Frontend to FastAPI Backend (P0 to P11)
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
        // Retry original request once with fresh token
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
    const errorMessage =
      json?.error?.message ||
      json?.detail ||
      `Request failed with status ${response.status}`;
    const errorCode = json?.error?.code || json?.code || `HTTP_${response.status}`;
    throw new ApiError(errorMessage, errorCode, response.status, json?.error?.details || json);
  }

  // If payload is wrapped in CertiFlow APIResponse envelope
  if (json && typeof json === "object" && "success" in json) {
    if (json.success === false) {
      throw new ApiError(
        json.error?.message || "Operation failed",
        json.error?.code || "OPERATION_FAILED",
        response.status,
        json.error?.details
      );
    }
    return json.data !== undefined ? json.data : json;
  }

  return json as T;
}

async function tryRefreshToken(): Promise<boolean> {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) return false;

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

    const data = await res.json();
    const tokenData = data.data || data;
    if (tokenData?.access_token) {
      tokenStorage.setTokens(tokenData.access_token, tokenData.refresh_token || refresh);
      return true;
    }
    return false;
  } catch {
    tokenStorage.clearTokens();
    return false;
  }
}

/**
 * Service-Specific API Methods
 */
export const api = {
  // Health
  health: {
    check: () => apiRequest<{ status: string; app: string }>("/health"),
    readiness: () => apiRequest<any>("/health/ready"),
  },

  // Auth (P0)
  auth: {
    register: async (payload: { name: string; email: string; password: string }) => {
      const res = await apiRequest<{ access_token: string; refresh_token: string }>(
        "/api/v1/auth/register",
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
      if (res.access_token) {
        tokenStorage.setTokens(res.access_token, res.refresh_token);
      }
      return res;
    },

    login: async (payload: { email: string; password: string }) => {
      const res = await apiRequest<{ access_token: string; refresh_token: string }>(
        "/api/v1/auth/login",
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
      if (res.access_token) {
        tokenStorage.setTokens(res.access_token, res.refresh_token);
      }
      return res;
    },

    me: () => apiRequest<any>("/api/v1/auth/me"),

    logout: async () => {
      try {
        await apiRequest("/api/v1/auth/logout", { method: "POST" });
      } finally {
        tokenStorage.clearTokens();
      }
    },
  },

  // Certificates (P3 & P5)
  certificates: {
    list: (params: { page?: number; limit?: number; status?: string; search?: string } = {}) => {
      const query = new URLSearchParams();
      if (params.page) query.set("page", params.page.toString());
      if (params.limit) query.set("limit", params.limit.toString());
      if (params.status) query.set("status", params.status);
      if (params.search) query.set("search", params.search);
      return apiRequest<any>(`/api/v1/certificates?${query.toString()}`);
    },

    get: (id: string) => apiRequest<any>(`/api/v1/certificates/${id}`),

    generate: (payload: {
      template_version_id: string;
      data: Record<string, any>;
      recipient?: {
        name: string;
        email: string;
      };
    }) =>
      apiRequest<any>("/api/v1/certificates/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),


    preview: (payload: {
      template_id: string;
      sample_data: Record<string, string>;
    }) =>
      apiRequest<{ preview_image_base64: string }>("/api/v1/certificates/preview", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    revoke: (id: string, reason: string) =>
      apiRequest<any>(`/api/v1/certificates/${id}/revoke`, {
        method: "POST",
        body: JSON.stringify({ reason }),
      }),

    restore: (id: string) =>
      apiRequest<any>(`/api/v1/certificates/${id}/restore`, {
        method: "POST",
      }),

    getPdfUrl: (id: string) => `${API_BASE_URL}/api/v1/certificates/${id}/pdf`,
  },

  // Public Verification & Trust (P5 & P11)
  public: {
    verifyCode: (code: string) =>
      apiRequest<{
        valid: boolean;
        status: string;
        certificate?: {
          certificate_number: string;
          recipient_name: string;
          program_name?: string;
          issue_date?: string;
          issuer_name?: string;
          issuer_website?: string;
          issuer_logo_url?: string;
          public_download_available?: boolean;
        };
        revoked_at?: string;
        revocation_reason?: string;
        verified_at: string;
        message?: string;
      }>(`/api/v1/public/verify/${encodeURIComponent(code)}`),

    verifyFile: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiRequest<any>("/api/v1/public/verify-file", {
        method: "POST",
        body: formData,
      });
    },

    getCredential: (id: string) =>
      apiRequest<any>(`/api/v1/public/credentials/${encodeURIComponent(id)}`),

    getBadge: (id: string) =>
      apiRequest<any>(`/api/v1/public/credentials/${encodeURIComponent(id)}/badge`),

    getVC: (id: string) =>
      apiRequest<any>(`/api/v1/public/credentials/${encodeURIComponent(id)}/vc`),
  },

  // Templates (P1)
  templates: {
    list: () => apiRequest<any>("/api/v1/templates"),
    get: (id: string) => apiRequest<any>(`/api/v1/templates/${id}`),
    create: (data: any) =>
      apiRequest<any>("/api/v1/templates", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  // Analytics (P7)
  analytics: {
    getDashboard: () => apiRequest<any>("/api/v1/analytics/dashboard"),
  },
};
