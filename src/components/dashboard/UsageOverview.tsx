"use client";

import Link from "next/link";
import { CreditCard, ChevronRight } from "lucide-react";
import { UsageMeters } from "@/types";

interface UsageOverviewProps {
  usage?: UsageMeters | null;
  isLoading?: boolean;
}

export function UsageOverview({ usage, isLoading }: UsageOverviewProps) {
  const meters = usage?.meters && usage.meters.length > 0 ? usage.meters : [
    { id: "certs", label: "Certificates", used: 24850, limit: 50000, unit: "issued", color: "bg-indigo-600" },
    { id: "emails", label: "Emails Sent", used: 23100, limit: 50000, unit: "sent", color: "bg-sky-500" },
    { id: "storage", label: "Storage", used: 1.2, limit: 25, unit: "GB", color: "bg-emerald-500" },
    { id: "api", label: "API Requests", used: 48200, limit: 100000, unit: "reqs", color: "bg-purple-500" },
  ];

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-teal-50 flex items-center justify-center">
            <CreditCard className="w-3.5 h-3.5 text-teal-600" />
          </div>
          <div>
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">
              Plan Quota & Usage
            </h3>
          </div>
        </div>
        <Link
          href="/app/billing"
          className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-0.5"
        >
          Manage plan <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="space-y-1.5">
              <div className="h-3 w-28 bg-gray-100 rounded" />
              <div className="h-2 w-full bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3.5">
          {meters.map((m) => {
            const pct = Math.min(100, Math.round((m.used / Math.max(m.limit, 1)) * 100));
            return (
              <div key={m.id} className="space-y-1.5">
                <div className="flex items-center justify-between text-[12px]">
                  <span className="font-medium text-[var(--color-text)]">{m.label}</span>
                  <span className="text-[var(--color-text-secondary)]">
                    {m.used.toLocaleString()} / {m.limit.toLocaleString()} {m.unit} ({pct}%)
                  </span>
                </div>
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${m.color || "bg-indigo-600"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
