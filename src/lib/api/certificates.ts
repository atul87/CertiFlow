import { apiRequest } from "./client";
import { Certificate, CertificateTimelineEvent, PaginatedResponse } from "@/types";

export const certificatesApi = {
  list: (params?: {
    page?: number;
    limit?: number;
    status?: string;
    template_id?: string;
    search?: string;
  }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<Certificate>>(
      `/api/v1/certificates${qs ? `?${qs}` : ""}`
    );
  },

  get: (id: string) => apiRequest<Certificate>(`/api/v1/certificates/${id}`),

  revoke: (id: string, reason: string) =>
    apiRequest<Certificate>(`/api/v1/certificates/${id}/revoke`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  restore: (id: string) =>
    apiRequest<Certificate>(`/api/v1/certificates/${id}/restore`, {
      method: "POST",
    }),

  getTimeline: (id: string) =>
    apiRequest<CertificateTimelineEvent[]>(`/api/v1/certificates/${id}/timeline`),

  getPdfUrl: (id: string) => `/api/v1/certificates/${id}/pdf`,

  sendEmail: (id: string) =>
    apiRequest(`/api/v1/certificates/${id}/email`, { method: "POST" }),

  bulkEmail: (ids: string[]) =>
    apiRequest("/api/v1/certificates/bulk-email", {
      method: "POST",
      body: JSON.stringify({ ids }),
    }),
};
