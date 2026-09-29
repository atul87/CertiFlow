"use client";

import {
  Zap,
  Play,
  Pause,
  X,
  RotateCcw,
  Download,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ChevronDown,
} from "lucide-react";
import { api } from "@/lib/api";
import type { IssuanceJob } from "@/types";
import { IssuanceStatusBadge, ISSUANCE_STATUS_CONFIG } from "./IssuanceStatusBadge";

interface IssuanceJobCardProps {
  job: IssuanceJob;
  onAction: (action: string, id: string) => void;
  onExpand: (id: string) => void;
  expanded: boolean;
}

export function IssuanceJobCard({
  job,
  onAction,
  onExpand,
  expanded,
}: IssuanceJobCardProps) {
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  const progressColor =
    job.status === "failed"
      ? "bg-red-500"
      : job.status === "completed"
      ? "bg-emerald-500"
      : job.status === "paused"
      ? "bg-amber-400"
      : "bg-[var(--color-primary)]";

  const isActive = job.status === "running" || job.status === "queued" || job.status === "paused";

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs hover:shadow-sm transition-shadow overflow-hidden">
      {/* Main card row */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Status Icon */}
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
              ISSUANCE_STATUS_CONFIG[job.status]?.bg || "bg-gray-50"
            }`}
          >
            {job.status === "running" ? (
              <Loader2 className={`w-5 h-5 ${ISSUANCE_STATUS_CONFIG.running.color} animate-spin`} />
            ) : job.status === "completed" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : job.status === "failed" ? (
              <AlertCircle className="w-5 h-5 text-red-500" />
            ) : (
              <Zap className={`w-5 h-5 ${ISSUANCE_STATUS_CONFIG[job.status]?.color || "text-gray-500"}`} />
            )}
          </div>

          {/* Job Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-[14px] font-bold text-[var(--color-text)] truncate">
                {job.template_name || job.name || `Job ${job.id.slice(0, 8)}`}
              </h3>
              <IssuanceStatusBadge status={job.status} />
              {job.priority === "high" && (
                <span className="text-[10px] font-bold text-purple-700 bg-purple-50 border border-purple-200 px-1.5 py-0.5 rounded-full">
                  HIGH PRIORITY
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 mt-1 text-[12px] text-[var(--color-text-tertiary)]">
              <span suppressHydrationWarning>Created {relTime(job.created_at)}</span>
              <span>·</span>
              <span className="font-mono">ID: {job.id.slice(0, 12)}…</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-1.5 shrink-0">
            {job.status === "running" && (
              <button
                onClick={() => onAction("pause", job.id)}
                title="Pause Job"
                className="p-2 rounded-lg text-amber-600 hover:bg-amber-50 border border-amber-200 transition-colors"
              >
                <Pause className="w-3.5 h-3.5" />
              </button>
            )}
            {job.status === "paused" && (
              <button
                onClick={() => onAction("resume", job.id)}
                title="Resume Job"
                className="p-2 rounded-lg text-blue-600 hover:bg-blue-50 border border-blue-200 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
              </button>
            )}
            {(job.status === "failed" || job.status === "partial") && (
              <button
                onClick={() => onAction("retry", job.id)}
                title="Retry Failed"
                className="p-2 rounded-lg text-indigo-600 hover:bg-indigo-50 border border-indigo-200 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
            {isActive && (
              <button
                onClick={() => onAction("cancel", job.id)}
                title="Cancel Job"
                className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 border border-gray-200 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
            {job.status === "completed" && (
              <a
                href={api.issuanceJobs.getZipUrl(job.id)}
                target="_blank"
                rel="noopener"
                title="Download certificates ZIP"
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[12px] font-semibold text-indigo-700 hover:bg-indigo-50 border border-indigo-200 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                ZIP
              </a>
            )}
            <button
              onClick={() => onExpand(job.id)}
              aria-label="Toggle details"
              className={`p-2 rounded-lg text-gray-400 hover:bg-gray-100 transition-all ${
                expanded ? "rotate-180" : ""
              }`}
            >
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between text-[12px]">
            <span className="font-semibold text-[var(--color-text)]">
              {job.completed.toLocaleString()} / {job.total.toLocaleString()} certificates
            </span>
            <span className="font-bold text-[var(--color-text)]">{Math.round(job.progress)}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${progressColor}`}
              style={{ width: `${job.progress}%` }}
            />
          </div>
          {job.failed > 0 && (
            <p className="text-[11px] text-red-500 font-medium">
              {job.failed} certificates failed to generate
            </p>
          )}
        </div>
      </div>

      {/* Expanded Details Drawer */}
      {expanded && (
        <div className="px-5 py-4 bg-gray-50 border-t border-[var(--color-border)] grid grid-cols-2 sm:grid-cols-4 gap-4 text-[12px]">
          <div>
            <p className="text-[var(--color-text-tertiary)] text-[11px] font-semibold">TOTAL RECORDS</p>
            <p className="font-bold text-[var(--color-text)] mt-0.5">{job.total.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-[var(--color-text-tertiary)] text-[11px] font-semibold">SUCCESSFUL</p>
            <p className="font-bold text-emerald-600 mt-0.5">{job.completed.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-[var(--color-text-tertiary)] text-[11px] font-semibold">FAILED</p>
            <p className="font-bold text-red-600 mt-0.5">{job.failed.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-[var(--color-text-tertiary)] text-[11px] font-semibold">EST. TIME REMAINING</p>
            <p className="font-bold text-[var(--color-text)] mt-0.5">
              {job.estimated_remaining_seconds
                ? `${job.estimated_remaining_seconds}s`
                : job.status === "completed"
                ? "Done"
                : "—"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
