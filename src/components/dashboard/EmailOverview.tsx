"use client";

import Link from "next/link";
import { Mail, CheckCircle2, Eye, AlertTriangle, ChevronRight } from "lucide-react";

interface EmailOverviewProps {
  sent?: number;
  delivered?: number;
  opened?: number;
  bounced?: number;
  isLoading?: boolean;
}

export function EmailOverview({
  sent = 23100,
  delivered = 22915,
  opened = 16840,
  bounced = 185,
  isLoading,
}: EmailOverviewProps) {
  const deliveryPct = Math.round((delivered / Math.max(sent, 1)) * 100);
  const openRate = Math.round((opened / Math.max(delivered, 1)) * 100);

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-sky-50 flex items-center justify-center">
            <Mail className="w-3.5 h-3.5 text-sky-600" />
          </div>
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">
            Email Delivery Health
          </h3>
        </div>
        <Link
          href="/app/email"
          className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-0.5"
        >
          Email center <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          <div className="h-4 w-32 bg-gray-100 rounded" />
          <div className="grid grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-gray-50 rounded-xl" />
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-100/60">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-800 mb-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Delivered
              </div>
              <p className="text-[18px] font-bold text-emerald-950">
                {delivered.toLocaleString()}
              </p>
              <span className="text-[10px] text-emerald-700 font-medium">{deliveryPct}% rate</span>
            </div>

            <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100/60">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-800 mb-1">
                <Eye className="w-3.5 h-3.5 text-blue-600" />
                Opened
              </div>
              <p className="text-[18px] font-bold text-blue-950">
                {opened.toLocaleString()}
              </p>
              <span className="text-[10px] text-blue-700 font-medium">{openRate}% open rate</span>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-50/50 border border-amber-100/60">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-800 mb-1">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                Bounced
              </div>
              <p className="text-[18px] font-bold text-amber-950">{bounced}</p>
              <span className="text-[10px] text-amber-700 font-medium">0.8% bounce rate</span>
            </div>

            <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-700 mb-1">
                <Mail className="w-3.5 h-3.5 text-gray-500" />
                Total Sent
              </div>
              <p className="text-[18px] font-bold text-gray-900">{sent.toLocaleString()}</p>
              <span className="text-[10px] text-gray-500 font-medium">All-time</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
