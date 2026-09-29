/**
 * Standardized TanStack Query Key Factory (P12.9)
 * Guarantees predictable caching, invalidation, and deduplication.
 */

export const queryKeys = {
  // Organization
  organization: {
    all: ["organization"] as const,
    current: () => [...queryKeys.organization.all, "current"] as const,
    members: (orgId: string) => [...queryKeys.organization.all, orgId, "members"] as const,
  },

  // Templates
  templates: {
    all: ["templates"] as const,
    list: (filters?: Record<string, any>) => [...queryKeys.templates.all, "list", filters || {}] as const,
    detail: (id: string) => [...queryKeys.templates.all, id] as const,
    versions: (id: string) => [...queryKeys.templates.all, id, "versions"] as const,
  },

  // Certificates
  certificates: {
    all: ["certificates"] as const,
    list: (orgId?: string, filters?: Record<string, any>) =>
      [...queryKeys.certificates.all, orgId || "default", filters || {}] as const,
    detail: (id: string) => [...queryKeys.certificates.all, "detail", id] as const,
    timeline: (id: string) => [...queryKeys.certificates.all, "timeline", id] as const,
  },

  // Issuance Jobs
  issuanceJobs: {
    all: ["issuance-jobs"] as const,
    list: (filters?: Record<string, any>) => [...queryKeys.issuanceJobs.all, "list", filters || {}] as const,
    detail: (jobId: string) => [...queryKeys.issuanceJobs.all, jobId] as const,
    progress: (jobId: string) => [...queryKeys.issuanceJobs.all, jobId, "progress"] as const,
  },

  // Digital Credentials
  credentials: {
    all: ["credentials"] as const,
    list: (filters?: Record<string, any>) => [...queryKeys.credentials.all, "list", filters || {}] as const,
    detail: (id: string) => [...queryKeys.credentials.all, id] as const,
    achievements: () => [...queryKeys.credentials.all, "achievements"] as const,
    issuer: () => [...queryKeys.credentials.all, "issuer"] as const,
    keys: () => [...queryKeys.credentials.all, "keys"] as const,
  },

  // Imports
  imports: {
    all: ["imports"] as const,
    list: (filters?: Record<string, any>) => [...queryKeys.imports.all, "list", filters || {}] as const,
    detail: (id: string) => [...queryKeys.imports.all, id] as const,
    rows: (id: string, params?: Record<string, any>) => [...queryKeys.imports.all, id, "rows", params || {}] as const,
  },

  // Email
  email: {
    all: ["email"] as const,
    deliveries: (filters?: Record<string, any>) => [...queryKeys.email.all, "deliveries", filters || {}] as const,
    templates: () => [...queryKeys.email.all, "templates"] as const,
    suppressions: () => [...queryKeys.email.all, "suppressions"] as const,
  },

  // Analytics
  analytics: {
    all: ["analytics"] as const,
    overview: () => [...queryKeys.analytics.all, "overview"] as const,
    trend: (range: string) => [...queryKeys.analytics.all, "trend", range] as const,
    summary: (period: string) => [...queryKeys.analytics.all, "summary", period] as const,
  },

  // Billing & Usage
  billing: {
    all: ["billing"] as const,
    subscription: () => [...queryKeys.billing.all, "subscription"] as const,
    usage: () => [...queryKeys.billing.all, "usage"] as const,
    invoices: () => [...queryKeys.billing.all, "invoices"] as const,
    plans: () => [...queryKeys.billing.all, "plans"] as const,
  },

  // Team
  team: {
    all: ["team"] as const,
    members: () => [...queryKeys.team.all, "members"] as const,
    invitations: () => [...queryKeys.team.all, "invitations"] as const,
    roles: () => [...queryKeys.team.all, "roles"] as const,
  },

  // Developer
  developer: {
    all: ["developer"] as const,
    apiKeys: () => [...queryKeys.developer.all, "apiKeys"] as const,
    webhooks: () => [...queryKeys.developer.all, "webhooks"] as const,
    webhookLogs: (webhookId: string) => [...queryKeys.developer.all, "webhooks", webhookId, "logs"] as const,
    serviceAccounts: () => [...queryKeys.developer.all, "serviceAccounts"] as const,
    usage: () => [...queryKeys.developer.all, "usage"] as const,
  },
};
