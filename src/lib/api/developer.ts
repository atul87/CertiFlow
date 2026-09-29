import { apiRequest } from "./client";
import { ApiKey, Webhook, WebhookLog, ServiceAccount } from "@/types";

export const developerApi = {
  // API Keys
  listApiKeys: () => apiRequest<ApiKey[]>("/api/v1/api-keys"),

  createApiKey: (payload: { name: string; scopes: string[] }) =>
    apiRequest<ApiKey & { key: string }>("/api/v1/api-keys", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  revokeApiKey: (id: string) =>
    apiRequest(`/api/v1/api-keys/${id}`, { method: "DELETE" }),

  // Webhooks
  listWebhooks: () => apiRequest<Webhook[]>("/api/v1/webhooks"),

  createWebhook: (payload: { name: string; url: string; events: string[] }) =>
    apiRequest<Webhook & { secret: string }>("/api/v1/webhooks", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateWebhook: (id: string, payload: Partial<Webhook>) =>
    apiRequest<Webhook>(`/api/v1/webhooks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteWebhook: (id: string) =>
    apiRequest(`/api/v1/webhooks/${id}`, { method: "DELETE" }),

  testWebhook: (id: string) =>
    apiRequest<{ success: boolean; status_code: number; response_body: string }>(
      `/api/v1/webhooks/${id}/test`,
      { method: "POST" }
    ),

  listWebhookLogs: (webhookId: string) =>
    apiRequest<WebhookLog[]>(`/api/v1/webhooks/${webhookId}/logs`),

  // Service Accounts
  listServiceAccounts: () =>
    apiRequest<ServiceAccount[]>("/api/v1/service-accounts"),

  createServiceAccount: (payload: { name: string; scopes: string[] }) =>
    apiRequest<ServiceAccount & { client_secret: string }>(
      "/api/v1/service-accounts",
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    ),

  deleteServiceAccount: (id: string) =>
    apiRequest(`/api/v1/service-accounts/${id}`, { method: "DELETE" }),

  getApiUsage: () =>
    apiRequest<{ total_calls: number; endpoints: Record<string, number> }>(
      "/api/v1/api-usage"
    ),
};
