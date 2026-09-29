import { apiRequest } from "./client";
import { EmailDelivery, EmailTemplate, SuppressionEntry, PaginatedResponse } from "@/types";

export const emailApi = {
  listDeliveries: (params?: { page?: number; limit?: number; status?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiRequest<PaginatedResponse<EmailDelivery>>(
      `/api/v1/email/deliveries${qs ? `?${qs}` : ""}`
    );
  },

  listTemplates: () =>
    apiRequest<EmailTemplate[]>("/api/v1/email/templates"),

  getTemplate: (id: string) =>
    apiRequest<EmailTemplate>(`/api/v1/email/templates/${id}`),

  createTemplate: (payload: {
    name: string;
    subject: string;
    html_body: string;
    text_body?: string;
    variables?: string[];
    is_default?: boolean;
  }) =>
    apiRequest<EmailTemplate>("/api/v1/email/templates", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateTemplate: (id: string, payload: Partial<EmailTemplate>) =>
    apiRequest<EmailTemplate>(`/api/v1/email/templates/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteTemplate: (id: string) =>
    apiRequest(`/api/v1/email/templates/${id}`, { method: "DELETE" }),

  sendBatch: (payload: {
    template_id: string;
    recipients: Array<{ email: string; name: string; certificate_id: string }>;
  }) =>
    apiRequest<{ queued_count: number }>("/api/v1/email/send", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listSuppressions: () =>
    apiRequest<SuppressionEntry[]>("/api/v1/email/suppressions"),

  removeSuppression: (id: string) =>
    apiRequest(`/api/v1/email/suppressions/${id}`, { method: "DELETE" }),

  removeSupression: (id: string) =>
    apiRequest(`/api/v1/email/suppressions/${id}`, { method: "DELETE" }),

  retryDelivery: (id: string) =>
    apiRequest(`/api/v1/email/deliveries/${id}/retry`, { method: "POST" }),
};
