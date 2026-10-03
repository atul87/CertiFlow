import { apiRequest, tokenStorage, orgStorage } from "./client";
import { User, AuthTokens, LoginCredentials, RegisterData } from "@/types";

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const data = await apiRequest<any>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    if (data?.access_token) {
      tokenStorage.setTokens(data.access_token, data.refresh_token);
    }
    if (data?.organization?.id) {
      orgStorage.setOrgId(data.organization.id);
    }
    return data as AuthTokens;
  },

  register: async (payload: RegisterData) => {
    const data = await apiRequest<any>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (data?.access_token) {
      tokenStorage.setTokens(data.access_token, data.refresh_token);
    }
    if (data?.organization?.id) {
      orgStorage.setOrgId(data.organization.id);
    }
    return data as AuthTokens;
  },

  demoSession: async () => {
    const data = await apiRequest<any>("/api/v1/auth/demo-session", {
      method: "POST",
    });
    if (data?.access_token) {
      tokenStorage.setTokens(data.access_token, data.refresh_token);
    }
    if (data?.organization?.id) {
      orgStorage.setOrgId(data.organization.id);
    }
    return data as AuthTokens;
  },

  logout: async () => {
    try {
      await apiRequest("/api/v1/auth/logout", { method: "POST" });
    } finally {
      tokenStorage.clearTokens();
    }
  },

  me: () => apiRequest<User>("/api/v1/auth/me"),

  forgotPassword: (email: string) =>
    apiRequest("/api/v1/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  resetPassword: (
    tokenOrPayload: string | { token: string; password: string },
    maybePassword?: string
  ) => {
    const body =
      typeof tokenOrPayload === "string"
        ? { token: tokenOrPayload, password: maybePassword || "" }
        : tokenOrPayload;

    return apiRequest("/api/v1/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};
