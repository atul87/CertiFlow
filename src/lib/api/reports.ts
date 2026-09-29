import { apiRequest } from "./client";
import { Report, CreateReportPayload, PaginatedResponse } from "@/types";

export const reportsApi = {
  list: (params?: { page?: number; limit?: number }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<Report>>(`/api/v1/reports${qs ? `?${qs}` : ""}`);
  },

  get: (id: string) => apiRequest<Report>(`/api/v1/reports/${id}`),

  create: (payload: CreateReportPayload) =>
    apiRequest<Report>("/api/v1/reports", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  delete: (id: string) =>
    apiRequest(`/api/v1/reports/${id}`, { method: "DELETE" }),

  getDownloadUrl: (id: string) => `/api/v1/reports/${id}/download`,
};
