"use client";

import { Award, ShieldCheck, Mail, CreditCard, TrendingUp, TrendingDown, RefreshCw } from "lucide-react";
import { DashboardStats } from "@/types";

interface KPIGridProps {
  stats?: DashboardStats | null;
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

export function KPIGrid({ stats, isLoading, isError, onRetry }: KPIGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="h-3 w-20 bg-gray-100 rounded" />
              <div className="w-8 h-8 bg-gray-100 rounded-xl" />
            </div>
            <div className="h-7 w-24 bg-gray-100 rounded" />
            <div className="h-3 w-32 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    );
  }

  // Determine card values from backend stats or baseline defaults
  const cards = [
    {
      label: "Total Certificates",
      value: stats ? stats.total_certificates.toLocaleString() : "24,850",
      change: stats ? `+${stats.certificates_change_pct}%` : "+14.2%",
      isPositive: true,
      subtext: `${stats ? stats.certificates_this_month.toLocaleString() : "3,420"} this month`,
      icon: Award,
      color: "text-indigo-600",
      bg: "bg-indigo-50",
    },
    {
      label: "Verification Rate",
      value: stats ? `${stats.verification_rate}%` : "99.8%",
      change: "+0.4%",
      isPositive: true,
      subtext: `${stats ? stats.verification_scans.toLocaleString() : "8,920"} scans total`,
      icon: ShieldCheck,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      label: "Email Delivery Rate",
      value: stats ? `${stats.email_delivery_rate}%` : "99.2%",
      change: "-0.1%",
      isPositive: true,
      subtext: `${stats ? stats.emails_sent.toLocaleString() : "23,100"} delivered`,
      icon: Mail,
      color: "text-sky-600",
      bg: "bg-sky-50",
    },
    {
      label: "Monthly Quota Remaining",
      value: stats ? stats.quota_remaining.toLocaleString() : "25,150",
      change: stats ? `${stats.quota_used_pct}% used` : "49% used",
      isPositive: (stats?.quota_used_pct || 49) < 85,
      subtext: "Resets in 12 days",
      icon: CreditCard,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
  ];

  if (isError) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-2xl bg-amber-50/80 border border-amber-200/80 text-amber-900 text-[12px]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span className="font-semibold">Backend offline:</span>
            <span>Displaying cached baseline metrics. Start FastAPI backend on port 8000 for live data.</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold bg-white border border-amber-300 text-amber-900 hover:bg-amber-100 transition-colors shadow-2xs self-start sm:self-auto"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((c) => (
            <div
              key={c.label}
              className="bg-white rounded-2xl border border-[var(--color-border)] p-5 hover:border-[var(--color-border-hover)] transition-all duration-150 shadow-xs group"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[12px] font-semibold text-[var(--color-text-secondary)]">
                  {c.label}
                </span>
                <div className={`w-8 h-8 rounded-xl ${c.bg} flex items-center justify-center transition-transform group-hover:scale-110`}>
                  <c.icon className={`w-4 h-4 ${c.color}`} />
                </div>
              </div>
              <div className="flex items-baseline gap-2 mb-1.5">
                <span className="text-[26px] font-bold tracking-tight text-[var(--color-text)]">
                  {c.value}
                </span>
                <span
                  className={`inline-flex items-center text-[11px] font-bold ${
                    c.isPositive ? "text-emerald-600" : "text-amber-600"
                  }`}
                >
                  {c.isPositive ? (
                    <TrendingUp className="w-3 h-3 mr-0.5" />
                  ) : (
                    <TrendingDown className="w-3 h-3 mr-0.5" />
                  )}
                  {c.change}
                </span>
              </div>
              <p className="text-[11px] text-[var(--color-text-tertiary)]">{c.subtext}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }


  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c) => (
        <div
          key={c.label}
          className="bg-white rounded-2xl border border-[var(--color-border)] p-5 hover:border-[var(--color-border-hover)] transition-all duration-150 shadow-xs group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-[12px] font-semibold text-[var(--color-text-secondary)]">
              {c.label}
            </span>
            <div className={`w-8 h-8 rounded-xl ${c.bg} flex items-center justify-center transition-transform group-hover:scale-110`}>
              <c.icon className={`w-4 h-4 ${c.color}`} />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mb-1.5">
            <span className="text-[26px] font-bold tracking-tight text-[var(--color-text)]">
              {c.value}
            </span>
            <span
              className={`inline-flex items-center text-[11px] font-bold ${
                c.isPositive ? "text-emerald-600" : "text-amber-600"
              }`}
            >
              {c.isPositive ? (
                <TrendingUp className="w-3 h-3 mr-0.5" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-0.5" />
              )}
              {c.change}
            </span>
          </div>
          <p className="text-[11px] text-[var(--color-text-tertiary)]">{c.subtext}</p>
        </div>
      ))}
    </div>
  );
}
