"use client";

import { useState } from "react";
import { Plus, Zap, RefreshCw, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  IssuanceJobCard,
  IssuanceFilters,
  IssuanceCreateModal,
  type IssuanceFilterTab,
} from "@/components/issuance";
import {
  useIssuanceJobs,
  useCreateIssuanceJob,
  usePauseIssuanceJob,
  useResumeIssuanceJob,
  useCancelIssuanceJob,
  useRetryIssuanceJob,
  useTemplates,
} from "@/lib/query";
import { api } from "@/lib/api";
import type { IssuanceJob, Template, ImportRecord } from "@/types";

export default function IssuancePage() {
  const [tab, setTab] = useState<IssuanceFilterTab>("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [imports, setImports] = useState<ImportRecord[]>([]);

  // TanStack Query for live issuance jobs with polling
  const {
    data: jobsData,
    isLoading,
    isRefetching,
    refetch,
  } = useIssuanceJobs(
    { status: tab === "all" ? undefined : tab },
    {
      // Poll every 3 seconds if any job is currently queued or running
      refetchInterval: (query: any) => {
        const items: IssuanceJob[] =
          (query.state.data as any)?.items ||
          (Array.isArray(query.state.data) ? query.state.data : []);
        const hasActive = items.some((j) => j.status === "running" || j.status === "queued");
        return hasActive ? 3000 : false;
      },
    }
  );

  const { data: templatesData } = useTemplates({ status: "published" });

  const createJobMutation = useCreateIssuanceJob();
  const pauseJobMutation = usePauseIssuanceJob();
  const resumeJobMutation = useResumeIssuanceJob();
  const cancelJobMutation = useCancelIssuanceJob();
  const retryJobMutation = useRetryIssuanceJob();

  // Baseline fallback demo jobs if backend is offline
  const fallbackJobs: IssuanceJob[] = [
    {
      id: "job-001",
      organization_id: "org_default_01",
      name: "Q3 Full Stack Bootcamp Graduation",
      template_name: "Academic Honors Certificate",
      template_id: "tmpl-001",
      status: "completed",
      priority: "normal",
      total: 450,
      completed: 450,
      failed: 0,
      progress: 100,
      created_at: new Date(Date.now() - 3600 * 4 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 3600 * 3 * 1000).toISOString(),
    },
    {
      id: "job-002",
      organization_id: "org_default_01",
      name: "Hackathon 2026 Winner Honors",
      template_name: "Winner Plaque Gold",
      template_id: "tmpl-002",
      status: "running",
      priority: "high",
      total: 120,
      completed: 84,
      failed: 0,
      progress: 70,
      estimated_remaining_seconds: 14,
      created_at: new Date(Date.now() - 600 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: "job-003",
      organization_id: "org_default_01",
      name: "Cloud Architect Certification",
      template_name: "AWS Certified Partner",
      template_id: "tmpl-003",
      status: "queued",
      priority: "normal",
      total: 800,
      completed: 0,
      failed: 0,
      progress: 0,
      created_at: new Date(Date.now() - 120 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const jobs: IssuanceJob[] =
    (jobsData as any)?.items || (Array.isArray(jobsData) && jobsData.length > 0 ? jobsData : fallbackJobs);

  const filteredJobs = jobs.filter((j) => {
    if (tab === "all") return true;
    if (tab === "processing") return j.status === "running" || j.status === "queued";
    return j.status === tab;
  });

  const templates: Template[] =
    (templatesData as any)?.items ||
    (Array.isArray(templatesData) && templatesData.length > 0
      ? templatesData
      : [
          { id: "tmpl-001", name: "Academic Honors Certificate", status: "published" } as Template,
          { id: "tmpl-002", name: "Winner Plaque Gold", status: "published" } as Template,
          { id: "tmpl-003", name: "AWS Certified Partner", status: "published" } as Template,
        ]);

  const handleAction = async (action: string, id: string) => {
    try {
      if (action === "pause") await pauseJobMutation.mutateAsync(id);
      else if (action === "resume") await resumeJobMutation.mutateAsync(id);
      else if (action === "cancel") await cancelJobMutation.mutateAsync(id);
      else if (action === "retry") await retryJobMutation.mutateAsync(id);
    } catch {
      // Optimistic state reflection
    }
  };

  const handleCreateJob = async (payload: {
    template_id: string;
    import_id?: string;
    name: string;
    send_email: boolean;
    priority: "normal" | "high";
  }) => {
    try {
      await createJobMutation.mutateAsync(payload);
      setIsModalOpen(false);
    } catch {
      setIsModalOpen(false);
    }
  };

  const counts: Partial<Record<IssuanceFilterTab, number>> = {
    all: jobs.length,
    processing: jobs.filter((j) => j.status === "running" || j.status === "queued").length,
    completed: jobs.filter((j) => j.status === "completed").length,
    failed: jobs.filter((j) => j.status === "failed").length,
    paused: jobs.filter((j) => j.status === "paused").length,
    cancelled: jobs.filter((j) => j.status === "cancelled").length,
  };

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-screen-xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Issuance</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">
            Monitor background certificate generation pipelines, queue states, and batch distributions.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-1.5">
            <Plus className="w-4 h-4" />
            New Batch
          </Button>
        </div>
      </div>

      {/* Operational Filter Tabs */}
      <IssuanceFilters currentTab={tab} onTabChange={setTab} counts={counts} />

      {/* Job Cards Stream */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-6 animate-pulse space-y-3">
              <div className="h-4 bg-gray-100 rounded w-1/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
              <div className="h-2.5 bg-gray-100 rounded w-full" />
            </div>
          ))}
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-12 text-center shadow-xs">
          <Layers className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">No {tab} jobs found</h3>
          <p className="text-[13px] text-[var(--color-text-secondary)] mt-1 mb-5">
            There are no issuance jobs matching the current filter state.
          </p>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            Start Batch Issuance
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <IssuanceJobCard
              key={job.id}
              job={job}
              onAction={handleAction}
              onExpand={(id) => setExpandedId((prev) => (prev === id ? null : id))}
              expanded={expandedId === job.id}
            />
          ))}
        </div>
      )}

      {/* Launch Batch Modal */}
      <IssuanceCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        templates={templates}
        imports={imports}
        onCreateJob={handleCreateJob}
        loading={createJobMutation.isPending}
      />
    </div>
  );
}
