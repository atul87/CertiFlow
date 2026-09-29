"use client";

import type { IssuanceJobStatus } from "@/types";

export const ISSUANCE_STATUS_CONFIG: Record<
  IssuanceJobStatus,
  { label: string; color: string; bg: string; border: string; dot: string }
> = {
  queued: { label: "Queued", color: "text-indigo-700", bg: "bg-indigo-50", border: "border-indigo-200", dot: "bg-indigo-400" },
  running: { label: "Running", color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", dot: "bg-blue-500" },
  paused: { label: "Paused", color: "text-amber-700", bg: "bg-amber-50", border: "border-amber-200", dot: "bg-amber-400" },
  completed: { label: "Completed", color: "text-emerald-700", bg: "bg-emerald-50", border: "border-emerald-200", dot: "bg-emerald-500" },
  failed: { label: "Failed", color: "text-red-700", bg: "bg-red-50", border: "border-red-200", dot: "bg-red-500" },
  cancelled: { label: "Cancelled", color: "text-gray-600", bg: "bg-gray-50", border: "border-gray-200", dot: "bg-gray-400" },
  partial: { label: "Partial", color: "text-orange-700", bg: "bg-orange-50", border: "border-orange-200", dot: "bg-orange-400" },
};

export function IssuanceStatusBadge({ status }: { status: IssuanceJobStatus }) {
  const cfg = ISSUANCE_STATUS_CONFIG[status] || ISSUANCE_STATUS_CONFIG.queued;
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${cfg.color} ${cfg.bg} ${cfg.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${status === "running" ? "animate-pulse" : ""}`} />
      {cfg.label}
    </span>
  );
}
