import { apiRequest } from "./client";
import { DashboardStats, TimeSeriesPoint, AnalyticsSummary } from "@/types";

export const analyticsApi = {
  getOverview: () => apiRequest<DashboardStats>("/api/v1/analytics/overview"),

  getTrend: (range: "7d" | "30d" | "90d" | "12m" = "30d") =>
    apiRequest<TimeSeriesPoint[]>(`/api/v1/analytics/trend?range=${range}`),

  getSummary: (period = "30d") =>
    apiRequest<AnalyticsSummary>(`/api/v1/analytics/summary?period=${period}`),

  getIssuanceStats: () =>
    apiRequest<Record<string, any>>("/api/v1/analytics/issuance"),

  getEmailStats: () =>
    apiRequest<Record<string, any>>("/api/v1/analytics/email"),

  getVerificationStats: () =>
    apiRequest<Record<string, any>>("/api/v1/analytics/verification"),
};
