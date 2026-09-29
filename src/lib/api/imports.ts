import { apiRequest } from "./client";
import { ImportRecord, ImportRow, PaginatedResponse } from "@/types";

export const importsApi = {
  list: (params?: { page?: number; limit?: number }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<ImportRecord>>(`/api/v1/imports${qs ? `?${qs}` : ""}`);
  },

  get: (id: string) => apiRequest<ImportRecord>(`/api/v1/imports/${id}`),

  upload: (file: File, templateId?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (templateId) {
      formData.append("template_id", templateId);
    }
    return apiRequest<ImportRecord>("/api/v1/imports/upload", {
      method: "POST",
      body: formData,
    });
  },

  analyze: (id: string) =>
    apiRequest<ImportRecord>(`/api/v1/imports/${id}/analyze`, { method: "POST" }),

  saveMapping: (id: string, mapping: Record<string, string>, templateId?: string) =>
    apiRequest<ImportRecord>(`/api/v1/imports/${id}/map`, {
      method: "POST",
      body: JSON.stringify({ mapping, template_id: templateId }),
    }),

  mapColumns: (id: string, mapping: Record<string, string>, templateId?: string) =>
    apiRequest<ImportRecord>(`/api/v1/imports/${id}/map`, {
      method: "POST",
      body: JSON.stringify({ mapping, template_id: templateId }),
    }),

  validate: (id: string) =>
    apiRequest<{
      valid_rows: number;
      invalid_rows: number;
      errors: Array<{ row: number; field: string; message: string }>;
    }>(`/api/v1/imports/${id}/validate`, { method: "POST" }),

  getRows: (id: string, params?: { page?: number; limit?: number; valid_only?: boolean }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<ImportRow>>(`/api/v1/imports/${id}/rows${qs ? `?${qs}` : ""}`);
  },

  confirm: (id: string) =>
    apiRequest<ImportRecord>(`/api/v1/imports/${id}/confirm`, { method: "POST" }),
};
