"use client";

import Link from "next/link";
import { ShieldCheck, CheckCircle2, XCircle, AlertCircle, ExternalLink } from "lucide-react";

interface VerificationOverviewProps {
  totalScans?: number;
  validScans?: number;
  revokedScans?: number;
  isLoading?: boolean;
}

export function VerificationOverview({
  totalScans = 8920,
  validScans = 8902,
  revokedScans = 18,
  isLoading,
}: VerificationOverviewProps) {
  const validPct = ((validScans / Math.max(totalScans, 1)) * 100).toFixed(1);

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-50 flex items-center justify-center">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          </div>
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">
            Trust & Verification Audits
          </h3>
        </div>
        <Link
          href="/verify/demo"
          target="_blank"
          className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-1"
        >
          Public portal <ExternalLink className="w-3 h-3" />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-3 animate-pulse">
          <div className="h-6 w-32 bg-gray-100 rounded" />
          <div className="h-2 w-full bg-gray-100 rounded" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-[26px] font-bold text-[var(--color-text)] tracking-tight">
                {validPct}%
              </p>
              <p className="text-[11px] text-[var(--color-text-secondary)]">Authentic verification pass rate</p>
            </div>
            <div className="text-right">
              <span className="text-[13px] font-semibold text-[var(--color-text)]">
                {totalScans.toLocaleString()}
              </span>
              <p className="text-[11px] text-[var(--color-text-tertiary)]">Total QR scans</p>
            </div>
          </div>

          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden flex">
            <div className="bg-emerald-500 h-full" style={{ width: `${validPct}%` }} />
            <div className="bg-red-400 h-full" style={{ width: `${100 - Number(validPct)}%` }} />
          </div>

          <div className="grid grid-cols-2 gap-2 text-[12px]">
            <div className="flex items-center gap-2 text-emerald-700">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{validScans.toLocaleString()} Valid</span>
            </div>
            <div className="flex items-center gap-2 text-red-600">
              <XCircle className="w-4 h-4 shrink-0" />
              <span>{revokedScans} Revoked / Tampered</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
