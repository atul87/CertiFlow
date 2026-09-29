/**
 * CertiFlow Modular API Layer (P12.6)
 * Assembles all domain-specific API clients into a unified interface.
 */

import { apiRequest } from "./client";
export * from "./client";
export * from "./auth";
export * from "./organizations";
export * from "./templates";
export * from "./imports";
export * from "./certificates";
export * from "./issuance";
export * from "./verification";
export * from "./email";
export * from "./analytics";
export * from "./reports";
export * from "./teams";
export * from "./credentials";
export * from "./developer";
export * from "./billing";
export * from "./system";

import { authApi } from "./auth";
import { organizationsApi } from "./organizations";
import { templatesApi } from "./templates";
import { importsApi } from "./imports";
import { certificatesApi } from "./certificates";
import { issuanceApi } from "./issuance";
import { verificationApi } from "./verification";
import { emailApi } from "./email";
import { analyticsApi } from "./analytics";
import { reportsApi } from "./reports";
import { teamsApi } from "./teams";
import { credentialsApi } from "./credentials";
import { developerApi } from "./developer";
import { billingApi } from "./billing";
import { systemApi } from "./system";

export const api = {
  auth: authApi,
  organizations: organizationsApi,
  templates: templatesApi,
  imports: importsApi,
  certificates: {
    ...certificatesApi,
    generate: (payload: any) =>
      apiRequest<any>("/api/v1/certificates/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  issuance: issuanceApi,
  issuanceJobs: issuanceApi,
  verification: verificationApi,
  public: verificationApi,
  email: emailApi,
  analytics: {
    ...analyticsApi,
    getDashboard: analyticsApi.getOverview,
  },
  reports: {
    ...reportsApi,
    download: (id: string) => reportsApi.getDownloadUrl(id),
  },
  team: {
    ...teamsApi,
    invite: teamsApi.inviteMember,
  },
  credentials: credentialsApi,
  developer: developerApi,
  apiKeys: {
    list: developerApi.listApiKeys,
    create: developerApi.createApiKey,
    revoke: developerApi.revokeApiKey,
  },
  webhooks: {
    list: developerApi.listWebhooks,
    create: developerApi.createWebhook,
    update: developerApi.updateWebhook,
    delete: developerApi.deleteWebhook,
    test: developerApi.testWebhook,
    logs: developerApi.listWebhookLogs,
  },
  serviceAccounts: {
    list: developerApi.listServiceAccounts,
    create: developerApi.createServiceAccount,
    delete: developerApi.deleteServiceAccount,
  },
  billing: billingApi,
  system: {
    ...systemApi,
    getActivity: (params?: any) => systemApi.getActivity(params),
  },
  health: {
    check: systemApi.health,
    workers: systemApi.workerStatus,
  },
};
