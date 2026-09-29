import { apiRequest } from "./client";
import { DigitalCredential, Achievement, IssuerProfile, SigningKey, PaginatedResponse } from "@/types";

export const credentialsApi = {
  list: (params?: { page?: number; limit?: number; status?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<DigitalCredential>>(
      `/api/v1/credentials${qs ? `?${qs}` : ""}`
    );
  },

  get: (id: string) =>
    apiRequest<DigitalCredential>(`/api/v1/credentials/${id}`),

  create: (payload: {
    recipient_name: string;
    recipient_email?: string;
    achievement_id: string;
    certificate_id?: string;
    expires_at?: string;
  }) =>
    apiRequest<DigitalCredential>("/api/v1/credentials", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  revoke: (id: string, reason: string) =>
    apiRequest<DigitalCredential>(`/api/v1/credentials/${id}/revoke`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  restore: (id: string) =>
    apiRequest<DigitalCredential>(`/api/v1/credentials/${id}/restore`, {
      method: "POST",
    }),

  suspend: (id: string, reason: string) =>
    apiRequest<DigitalCredential>(`/api/v1/credentials/${id}/suspend`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  listAchievements: () =>
    apiRequest<Achievement[]>("/api/v1/achievements"),

  createAchievement: (payload: Partial<Achievement>) =>
    apiRequest<Achievement>("/api/v1/achievements", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateAchievement: (id: string, payload: Partial<Achievement>) =>
    apiRequest<Achievement>(`/api/v1/achievements/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteAchievement: (id: string) =>
    apiRequest(`/api/v1/achievements/${id}`, { method: "DELETE" }),

  getIssuerProfile: () =>
    apiRequest<IssuerProfile>("/api/v1/issuers/profile"),

  updateIssuerProfile: (payload: Partial<IssuerProfile>) =>
    apiRequest<IssuerProfile>("/api/v1/issuers/profile", {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  getKeys: () =>
    apiRequest<SigningKey[]>("/api/v1/issuers/keys"),

  rotateKey: (algorithm = "Ed25519") =>
    apiRequest<SigningKey>("/api/v1/issuers/keys/rotate", {
      method: "POST",
      body: JSON.stringify({ algorithm }),
    }),
};
