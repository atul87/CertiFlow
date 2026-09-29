import { apiRequest } from "./client";
import { IssuanceJob, IssuanceJobStatus, CreateJobPayload, PaginatedResponse } from "@/types";

export const issuanceApi = {
  list: (params?: { page?: number; limit?: number; status?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<IssuanceJob>>(
      `/api/v1/issuance-jobs${qs ? `?${qs}` : ""}`
    );
  },

  get: (id: string) => apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}`),

  create: (payload: CreateJobPayload) =>
    apiRequest<IssuanceJob>("/api/v1/issuance-jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  retry: (id: string) =>
    apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}/retry`, {
      method: "POST",
    }),

  retryFailed: (id: string) =>
    apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}/retry`, {
      method: "POST",
    }),

  pause: (id: string) =>
    apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}/pause`, {
      method: "POST",
    }),

  resume: (id: string) =>
    apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}/resume`, {
      method: "POST",
    }),

  cancel: (id: string) =>
    apiRequest<IssuanceJob>(`/api/v1/issuance-jobs/${id}/cancel`, {
      method: "POST",
    }),

  getProgress: (id: string) =>
    apiRequest<{ progress: number; completed: number; failed?: number; total: number; status: IssuanceJobStatus }>(
      `/api/v1/issuance-jobs/${id}/progress`
    ),

  getDownloadUrl: (id: string) => `/api/v1/issuance-jobs/${id}/zip`,

  getZipUrl: (id: string) => `/api/v1/issuance-jobs/${id}/zip`,
};
