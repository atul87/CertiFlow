"use client";

import { CheckCircle2, XCircle, Clock, AlertTriangle } from "lucide-react";
import type { CertificateStatus } from "@/types";

export const CERTIFICATE_STATUS_CONFIG: Record<
  CertificateStatus,
  { label: string; cls: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  active: { label: "Active", cls: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle2 },
  revoked: { label: "Revoked", cls: "bg-red-50 text-red-700 border-red-200", Icon: XCircle },
  expired: { label: "Expired", cls: "bg-gray-50 text-gray-600 border-gray-200", Icon: Clock },
  invalid: { label: "Invalid", cls: "bg-amber-50 text-amber-700 border-amber-200", Icon: AlertTriangle },
  draft: { label: "Draft", cls: "bg-blue-50 text-blue-700 border-blue-200", Icon: Clock },
};

export function CertificateStatusBadge({ status }: { status: CertificateStatus }) {
  const cfg = CERTIFICATE_STATUS_CONFIG[status] || CERTIFICATE_STATUS_CONFIG.active;
  const Icon = cfg.Icon;

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${cfg.cls}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}
