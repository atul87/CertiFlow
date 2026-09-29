"use client";

import Link from "next/link";
import { Zap, ChevronRight, CheckCircle2, AlertCircle, Clock, ArrowRight } from "lucide-react";
import { IssuanceJob } from "@/types";

interface IssuanceOverviewProps {
  jobs?: IssuanceJob[];
  isLoading?: boolean;
}

export function IssuanceOverview({ jobs, isLoading }: IssuanceOverviewProps) {
  const displayJobs = jobs && jobs.length > 0 ? jobs.slice(0, 4) : [
    {
      id: "job_01",
      name: "Q3 Full Stack Bootcamp",
      template_name: "Developer Certificate",
      status: "completed" as const,
      total: 450,
      completed: 450,
      failed: 0,
      progress: 100,
      created_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    },
    {
      id: "job_02",
      name: "Hackathon 2026 Winner Honors",
      template_name: "Winner Plaque Gold",
      status: "running" as const,
      total: 120,
      completed: 84,
      failed: 1,
      progress: 70,
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    },
    {
      id: "job_03",
      name: "Cloud Architect Certification",
      template_name: "AWS Certified Partner",
      status: "queued" as const,
      total: 800,
      completed: 0,
      failed: 0,
      progress: 0,
      created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-violet-50 flex items-center justify-center">
            <Zap className="w-3.5 h-3.5 text-violet-600" />
          </div>
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">
            Active Issuance Jobs
          </h3>
        </div>
        <Link
          href="/app/issuance"
          className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-0.5"
        >
          View all <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-3.5 rounded-xl border border-gray-100 space-y-2">
              <div className="h-4 w-40 bg-gray-100 rounded" />
              <div className="h-2 w-full bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      ) : displayJobs.length === 0 ? (
        <div className="py-8 text-center">
          <Zap className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No issuance jobs yet</p>
          <Link
            href="/app/issuance?create=1"
            className="inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-lg text-[12px] font-semibold bg-[var(--color-primary)] text-white hover:opacity-95"
          >
            Create batch job <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {displayJobs.map((job) => (
            <div
              key={job.id}
              className="p-3.5 rounded-xl border border-[var(--color-border)] hover:border-indigo-200 transition-colors group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="min-w-0">
                  <p className="text-[13px] font-bold text-[var(--color-text)] truncate">
                    {job.name || "Issuance Batch"}
                  </p>
                  <p className="text-[11px] text-[var(--color-text-tertiary)] truncate">
                    {job.template_name || "Default Template"}
                  </p>
                </div>
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-full inline-flex items-center gap-1 shrink-0 ${
                    job.status === "completed"
                      ? "bg-emerald-50 text-emerald-700"
                      : job.status === "running"
                      ? "bg-indigo-50 text-indigo-700"
                      : job.status === "failed"
                      ? "bg-red-50 text-red-700"
                      : "bg-amber-50 text-amber-700"
                  }`}
                >
                  {job.status === "completed" && <CheckCircle2 className="w-3 h-3" />}
                  {job.status === "running" && <span className="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-pulse" />}
                  {job.status === "queued" && <Clock className="w-3 h-3" />}
                  {job.status === "failed" && <AlertCircle className="w-3 h-3" />}
                  {job.status.toUpperCase()}
                </span>
              </div>

              {/* Progress bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[11px] text-[var(--color-text-tertiary)]">
                  <span>
                    {job.completed} of {job.total} generated
                  </span>
                  <span className="font-bold text-[var(--color-text)]">
                    {job.progress}%
                  </span>
                </div>
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      job.status === "completed"
                        ? "bg-emerald-500"
                        : job.status === "failed"
                        ? "bg-red-500"
                        : "bg-[var(--color-primary)]"
                    }`}
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
