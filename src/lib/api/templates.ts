import { apiRequest } from "./client";
import { Template, TemplateVersion, PaginatedResponse } from "@/types";

export const templatesApi = {
  list: (params?: { page?: number; limit?: number; status?: string; search?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<Template>>(`/api/v1/templates${qs ? `?${qs}` : ""}`);
  },

  get: (id: string) => apiRequest<Template>(`/api/v1/templates/${id}`),

  create: (payload: {
    name: string;
    description?: string;
    width_mm?: number;
    height_mm?: number;
    orientation?: "landscape" | "portrait";
    canvas_json?: any;
  }) =>
    apiRequest<Template>("/api/v1/templates", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  update: (id: string, payload: Partial<Template>) =>
    apiRequest<Template>(`/api/v1/templates/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  delete: (id: string) =>
    apiRequest(`/api/v1/templates/${id}`, { method: "DELETE" }),

  publish: (id: string) =>
    apiRequest<Template>(`/api/v1/templates/${id}/publish`, { method: "POST" }),

  archive: (id: string) =>
    apiRequest<Template>(`/api/v1/templates/${id}/archive`, { method: "POST" }),

  duplicate: (id: string) =>
    apiRequest<Template>(`/api/v1/templates/${id}/duplicate`, { method: "POST" }),

  createVersion: (id: string, payload: { canvas_json: any; note?: string }) =>
    apiRequest<TemplateVersion>(`/api/v1/templates/${id}/versions`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listVersions: (id: string) =>
    apiRequest<TemplateVersion[]>(`/api/v1/templates/${id}/versions`),

  preview: (id: string, sampleData?: Record<string, string>) =>
    apiRequest<{ svg: string; sample_data?: Record<string, string> }>(
      `/api/v1/templates/${id}/preview`,
      {
        method: "POST",
        body: JSON.stringify({ sample_data: sampleData || {} }),
      }
    ),
};
