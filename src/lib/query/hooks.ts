import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "./keys";
import { api } from "@/lib/api";
import {
  Template,
  Certificate,
  IssuanceJob,
  DigitalCredential,
  DashboardStats,
  TimeSeriesPoint,
  UsageMeters,
  Subscription,
  CreateJobPayload,
} from "@/types";

// ─── Queries ──────────────────────────────────────────────────────────────────

export function useTemplates(params?: { status?: string; search?: string }) {
  return useQuery({
    queryKey: queryKeys.templates.list(params),
    queryFn: () => api.templates.list(params),
  });
}

export function useTemplate(id: string) {
  return useQuery({
    queryKey: queryKeys.templates.detail(id),
    queryFn: () => api.templates.get(id),
    enabled: !!id,
  });
}

export function useCertificates(filters?: {
  page?: number;
  limit?: number;
  status?: string;
  template_id?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: queryKeys.certificates.list("current", filters),
    queryFn: () => api.certificates.list(filters),
  });
}

export function useCertificate(id: string) {
  return useQuery({
    queryKey: queryKeys.certificates.detail(id),
    queryFn: () => api.certificates.get(id),
    enabled: !!id,
  });
}

export function useIssuanceJobs(filters?: { status?: string }, options?: Record<string, any>) {
  return useQuery({
    queryKey: queryKeys.issuanceJobs.list(filters),
    queryFn: () => api.issuance.list(filters),
    ...options,
  });
}

export function useIssuanceJob(id: string) {
  return useQuery({
    queryKey: queryKeys.issuanceJobs.detail(id),
    queryFn: () => api.issuance.get(id),
    enabled: !!id,
  });
}

/**
 * Real-time job polling hook (P12.23)
 * Automatically polls every 2 seconds while status is "running" or "queued".
 */
export function useIssuanceProgress(jobId: string, isRunning: boolean) {
  return useQuery({
    queryKey: queryKeys.issuanceJobs.progress(jobId),
    queryFn: () => api.issuance.getProgress(jobId),
    enabled: !!jobId && isRunning,
    refetchInterval: isRunning ? 2000 : false,
    refetchIntervalInBackground: false,
  });
}

export function useCredentials(filters?: { status?: string }) {
  return useQuery({
    queryKey: queryKeys.credentials.list(filters),
    queryFn: () => api.credentials.list(filters),
  });
}

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: queryKeys.analytics.overview(),
    queryFn: () => api.analytics.getOverview(),
  });
}

export function useAnalyticsTrend(range: "7d" | "30d" | "90d" | "12m" = "30d") {
  return useQuery({
    queryKey: queryKeys.analytics.trend(range),
    queryFn: () => api.analytics.getTrend(range),
  });
}

export function useBillingUsage() {
  return useQuery({
    queryKey: queryKeys.billing.usage(),
    queryFn: () => api.billing.getUsage(),
  });
}

export function useBillingSubscription() {
  return useQuery({
    queryKey: queryKeys.billing.subscription(),
    queryFn: () => api.billing.getSubscription(),
  });
}

// ─── Mutations ────────────────────────────────────────────────────────────────

export function useCreateTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name: string; description?: string; canvas_json?: any }) =>
      api.templates.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.all });
    },
  });
}

export function usePublishTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.templates.publish(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.detail(id) });
    },
  });
}

export function useCreateIssuanceJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateJobPayload) => api.issuance.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.billing.usage() });
    },
  });
}

export function useRevokeCertificate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.certificates.revoke(id, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.certificates.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.certificates.detail(id) });
    },
  });
}

export function useRestoreCertificate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.certificates.restore(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.certificates.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.certificates.detail(id) });
    },
  });
}

export function usePauseIssuanceJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.issuance.pause(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.detail(id) });
    },
  });
}

export function useResumeIssuanceJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.issuance.resume(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.detail(id) });
    },
  });
}

export function useCancelIssuanceJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.issuance.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.detail(id) });
    },
  });
}

export function useRetryIssuanceJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.issuance.retry(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.issuanceJobs.detail(id) });
    },
  });
}

export function useSendCertificateEmail() {
  return useMutation({
    mutationFn: (payload: string | { certificate_id: string; recipient_email?: string }) => {
      const id = typeof payload === "string" ? payload : payload.certificate_id;
      return api.certificates.sendEmail(id);
    },
  });
}

export function useCreateCredential() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      recipient_name: string;
      recipient_email?: string;
      achievement_id: string;
      certificate_id?: string;
    }) => api.credentials.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.credentials.all });
    },
  });
}
