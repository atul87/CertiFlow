"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, Zap, FileSpreadsheet, RefreshCw } from "lucide-react";
import {
  KPIGrid,
  CertificateTrend,
  IssuanceOverview,
  EmailOverview,
  VerificationOverview,
  UsageOverview,
  RecentActivity,
  QuickActions,
} from "@/components/dashboard";
import {
  useAnalyticsOverview,
  useIssuanceJobs,
  useBillingUsage,
} from "@/lib/query";
import { useOrganization } from "@/features/organization/organization-context";
import { useAuth } from "@/features/auth/auth-guard";

export default function AppDashboard() {
  const { currentOrganization } = useOrganization();
  const { user } = useAuth();

  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
    refetch: refetchStats,
  } = useAnalyticsOverview();

  const {
    data: jobsData,
    isLoading: jobsLoading,
    refetch: refetchJobs,
  } = useIssuanceJobs({ status: "all" });

  const {
    data: usage,
    isLoading: usageLoading,
    refetch: refetchUsage,
  } = useBillingUsage();

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.allSettled([refetchStats(), refetchJobs(), refetchUsage()]);
    setIsRefreshing(false);
  };

  const jobs = (jobsData as any)?.items || (Array.isArray(jobsData) ? jobsData : undefined);

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-screen-2xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[12px] font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 uppercase tracking-wider">
              {currentOrganization?.name || "Workspace"}
            </span>
            <span className="text-[12px] text-[var(--color-text-tertiary)]">•</span>
            <span className="text-[12px] text-[var(--color-text-secondary)] font-medium">
              {currentOrganization?.plan || "Professional"} Plan
            </span>
          </div>
          <h1 className="text-[26px] font-bold tracking-tight text-[var(--color-text)]">
            Welcome back{user?.name ? `, ${user.name}` : ""}
          </h1>
          <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">
            Operational overview of credential issuance, delivery rates, and ledger verifications.
          </p>
        </div>

        {/* Top Actions */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleRefresh}
            title="Refresh dashboard metrics"
            disabled={isRefreshing}
            className="p-2.5 rounded-xl border border-[var(--color-border)] bg-white text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors shadow-xs"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          </button>
          <Link
            href="/app/imports"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[var(--color-border)] bg-white text-[13px] font-semibold text-[var(--color-text)] hover:bg-gray-50 transition-colors shadow-xs"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
            <span>Upload CSV</span>
          </Link>
          <Link
            href="/app/templates?create=1"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[var(--color-border)] bg-white text-[13px] font-semibold text-[var(--color-text)] hover:bg-gray-50 transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>New Template</span>
          </Link>
          <Link
            href="/app/issuance?create=1"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#635BFF] text-white text-[13px] font-semibold hover:bg-[#5249f0] transition-colors shadow-sm"
          >
            <Zap className="w-4 h-4" />
            <span>Start Issuance</span>
          </Link>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <QuickActions />

      {/* Primary KPI Grid */}
      <KPIGrid
        stats={stats}
        isLoading={statsLoading}
        isError={statsError}
        onRetry={refetchStats}
      />

      {/* Main 2-Column Dashboard Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Volume & Active Batches) */}
        <div className="lg:col-span-8 space-y-6">
          <CertificateTrend />
          <IssuanceOverview jobs={jobs} isLoading={jobsLoading} />
          <RecentActivity isLoading={statsLoading} />
        </div>

        {/* Right Column (Usage, Email Health & Verification) */}
        <div className="lg:col-span-4 space-y-6">
          <UsageOverview usage={usage} isLoading={usageLoading} />
          <EmailOverview
            sent={stats?.emails_sent}
            delivered={Math.round((stats?.emails_sent || 23100) * 0.992)}
            isLoading={statsLoading}
          />
          <VerificationOverview
            totalScans={stats?.verification_scans}
            isLoading={statsLoading}
          />
        </div>
      </div>
    </div>
  );
}
