import { apiRequest } from "./client";

export const systemApi = {
  health: () => apiRequest<{ status: string; version?: string }>("/health"),

  workerStatus: () =>
    apiRequest<{
      redis: boolean;
      workers: Array<{ id: string; active_jobs: number; status: string }>;
    }>("/api/v1/health/workers"),

  diagnostics: () =>
    apiRequest<Record<string, any>>("/api/v1/admin/diagnostics"),

  getActivity: (params?: any) => {
    const qs = params ? new URLSearchParams(params).toString() : "";
    return apiRequest<any>(`/api/v1/activity${qs ? `?${qs}` : ""}`);
  },
};
