"use client";

import { useState, useEffect, useCallback } from "react";
import {
  FileBarChart,
  Plus,
  Download,
  RefreshCw,
  Trash2,
  FileText,
  Award,
  Mail,
  CheckCircle2,
  ShieldCheck,
  BarChart3,
  Clock,
  Loader2,
  CheckCircle,
  XCircle,
  Calendar,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { Report, ReportType } from "@/types";

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Report type config ───────────────────────────────────────────────────────
const REPORT_TYPE_CONFIG: Record<ReportType, { label: string; icon: React.ComponentType<{ className?: string }>; color: string; bg: string; description: string }> = {
  certificates: { label: "Certificates", icon: Award, color: "text-indigo-600", bg: "bg-indigo-50", description: "All issued certificates with status, recipient, and timestamp" },
  issuance: { label: "Issuance Jobs", icon: FileText, color: "text-blue-600", bg: "bg-blue-50", description: "Batch job history with success/failure rates" },
  emails: { label: "Email Delivery", icon: Mail, color: "text-sky-600", bg: "bg-sky-50", description: "Email delivery logs, bounce rates, and open rates" },
  verification: { label: "Verification", icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50", description: "Public verification scan logs with pass/fail breakdown" },
  credentials: { label: "Digital Credentials", icon: ShieldCheck, color: "text-purple-600", bg: "bg-purple-50", description: "W3C VC / Open Badges credential status report" },
  analytics: { label: "Analytics Summary", icon: BarChart3, color: "text-amber-600", bg: "bg-amber-50", description: "Aggregated KPIs across all certificate operations" },
};

// ─── Status badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: Report["status"] }) {
  const cfg = {
    generating: { cls: "bg-blue-50 text-blue-700 border-blue-200", Icon: Loader2, anim: "animate-spin" },
    ready: { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle, anim: "" },
    failed: { cls: "bg-red-50 text-red-700 border-red-200", Icon: XCircle, anim: "" },
  }[status] || { cls: "bg-gray-50 text-gray-600 border-gray-200", Icon: Clock, anim: "" };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${cfg.cls}`}>
      <cfg.Icon className={`w-3 h-3 ${cfg.anim}`} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

// ─── Demo reports ─────────────────────────────────────────────────────────────
const DEMO_REPORTS: Report[] = [
  { id: "rep-1", name: "Q3 2026 Certificate Report", type: "certificates", status: "ready", format: "csv", row_count: 3240, created_at: new Date(Date.now() - 86400 * 5 * 1000).toISOString(), generated_at: new Date(Date.now() - 86400 * 5 * 1000 + 60000).toISOString() },
  { id: "rep-2", name: "Email Delivery September 2026", type: "emails", status: "ready", format: "csv", row_count: 3012, created_at: new Date(Date.now() - 86400 * 2 * 1000).toISOString(), generated_at: new Date(Date.now() - 86400 * 2 * 1000 + 45000).toISOString() },
  { id: "rep-3", name: "Verification Audit Log", type: "verification", status: "ready", format: "pdf", row_count: 4890, created_at: new Date(Date.now() - 86400 * 1 * 1000).toISOString(), generated_at: new Date(Date.now() - 86400 * 1 * 1000 + 90000).toISOString() },
  { id: "rep-4", name: "Digital Credentials Report", type: "credentials", status: "generating", format: "csv", created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString() },
  { id: "rep-5", name: "Monthly Analytics Summary", type: "analytics", status: "ready", format: "pdf", row_count: 1, created_at: new Date(Date.now() - 86400 * 30 * 1000).toISOString(), generated_at: new Date(Date.now() - 86400 * 30 * 1000 + 30000).toISOString() },
];

// ─────────────────────────────────────────────────────────────────────────────
// Main Reports Page
// ─────────────────────────────────────────────────────────────────────────────
export default function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<Report[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState<{ name: string; type: ReportType; format: "csv" | "pdf"; }>({
    name: "",
    type: "certificates",
    format: "csv",
  });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.reports.list();
      setReports(res?.items || (Array.isArray(res) ? res : []));
    } catch {
      setReports(DEMO_REPORTS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await api.reports.create({
        name: createForm.name || `${REPORT_TYPE_CONFIG[createForm.type].label} Report`,
        type: createForm.type,
        format: createForm.format,
      });
      setReports(prev => [res, ...prev]);
    } catch {
      const mock: Report = {
        id: `rep-${Date.now()}`,
        name: createForm.name || `${REPORT_TYPE_CONFIG[createForm.type].label} Report`,
        type: createForm.type,
        status: "generating",
        format: createForm.format,
        created_at: new Date().toISOString(),
      };
      setReports(prev => [mock, ...prev]);
      // Simulate completion after 3s
      setTimeout(() => {
        setReports(prev => prev.map(r => r.id === mock.id ? { ...r, status: "ready" as const, row_count: Math.floor(Math.random() * 3000 + 100), generated_at: new Date().toISOString() } : r));
      }, 3000);
    } finally {
      setCreating(false);
      setShowCreate(false);
      setCreateForm({ name: "", type: "certificates", format: "csv" });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this report?")) return;
    try { await api.reports.delete(id); } catch { /* demo */ }
    setReports(prev => prev.filter(r => r.id !== id));
  };

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Reports</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">Generate and download certificate, email, and compliance reports</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-1.5" />New Report
          </Button>
        </div>
      </div>

      {/* Report type quick-create cards */}
      <div>
        <p className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-3">Quick Generate</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {(Object.entries(REPORT_TYPE_CONFIG) as [ReportType, typeof REPORT_TYPE_CONFIG[ReportType]][]).map(([type, cfg]) => (
            <button
              key={type}
              onClick={() => {
                setCreateForm(p => ({ ...p, type, name: `${cfg.label} Report` }));
                setShowCreate(true);
              }}
              className="bg-white rounded-xl border border-[var(--color-border)] p-4 text-center hover:border-[var(--color-border-hover)] hover:shadow-sm transition-all group"
            >
              <div className={`w-9 h-9 rounded-xl ${cfg.bg} flex items-center justify-center mx-auto mb-2 group-hover:scale-105 transition-transform`}>
                <cfg.icon className={`w-4 h-4 ${cfg.color}`} />
              </div>
              <p className="text-[12px] font-semibold text-[var(--color-text)]">{cfg.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Reports list */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <div>
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Generated Reports</h3>
            <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">Reports are retained for 90 days</p>
          </div>
          <span className="text-[12px] font-semibold text-[var(--color-text-tertiary)]">{reports.length} reports</span>
        </div>

        {/* Table header */}
        <div className="px-5 py-2.5 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
          <span className="col-span-4">Report Name</span>
          <span className="col-span-2">Type</span>
          <span className="col-span-1 text-center">Format</span>
          <span className="col-span-2">Status</span>
          <span className="col-span-1 text-right">Rows</span>
          <span className="col-span-1 text-right">Created</span>
          <span className="col-span-1 text-right">Actions</span>
        </div>

        <div className="divide-y divide-[var(--color-border)]">
          {loading ? (
            [1, 2, 3, 4].map(i => (
              <div key={i} className="px-5 py-4 grid grid-cols-12 gap-3 items-center">
                <Skeleton className="col-span-4 h-4" />
                <Skeleton className="col-span-2 h-4" />
                <Skeleton className="col-span-1 h-4 w-10 mx-auto" />
                <Skeleton className="col-span-2 h-4 w-16" />
                <Skeleton className="col-span-1 h-3 ml-auto" />
                <Skeleton className="col-span-1 h-3 ml-auto" />
                <Skeleton className="col-span-1 h-4 ml-auto w-8" />
              </div>
            ))
          ) : reports.length === 0 ? (
            <div className="px-5 py-16 text-center">
              <FileBarChart className="w-8 h-8 text-gray-200 mx-auto mb-3" />
              <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No reports yet</p>
              <button onClick={() => setShowCreate(true)} className="mt-2 text-[12px] text-[var(--color-primary)] hover:underline">Generate your first report</button>
            </div>
          ) : (
            reports.map(rep => {
              const cfg = REPORT_TYPE_CONFIG[rep.type] || REPORT_TYPE_CONFIG.analytics;
              return (
                <div key={rep.id} className="px-5 py-4 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50 transition-colors">
                  <div className="col-span-4 flex items-center gap-2.5">
                    <div className={`w-8 h-8 rounded-lg ${cfg.bg} flex items-center justify-center shrink-0`}>
                      <cfg.icon className={`w-4 h-4 ${cfg.color}`} />
                    </div>
                    <span className="text-[13px] font-semibold text-[var(--color-text)] truncate">{rep.name}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[12px] text-[var(--color-text-secondary)]">{cfg.label}</span>
                  </div>
                  <div className="col-span-1 text-center">
                    <span className="text-[11px] font-bold uppercase text-[var(--color-text-tertiary)] bg-gray-100 px-2 py-0.5 rounded">
                      {rep.format}
                    </span>
                  </div>
                  <div className="col-span-2">
                    <StatusBadge status={rep.status} />
                  </div>
                  <div className="col-span-1 text-right">
                    <span className="text-[12px] text-[var(--color-text-secondary)]">
                      {rep.row_count?.toLocaleString() || "—"}
                    </span>
                  </div>
                  <div className="col-span-1 text-right">
                    <span className="text-[11px] text-[var(--color-text-tertiary)]">{relTime(rep.created_at)}</span>
                  </div>
                  <div className="col-span-1 flex items-center justify-end gap-1">
                    {rep.status === "ready" && (
                      <a
                        href={api.reports.download(rep.id)}
                        target="_blank"
                        rel="noopener"
                        className="p-1.5 rounded-lg text-gray-300 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                        title="Download"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>
                    )}
                    <button
                      onClick={() => handleDelete(rep.id)}
                      className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Create Report Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) setShowCreate(false); }}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-[var(--color-border)]">
            <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
              <div>
                <h2 className="text-[17px] font-bold text-[var(--color-text)]">Generate Report</h2>
                <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">Configure and export your report</p>
              </div>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
            </div>

            <form onSubmit={handleCreate} className="px-6 py-5 space-y-5">
              {/* Report type */}
              <div>
                <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2.5 uppercase tracking-wide">Report Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.entries(REPORT_TYPE_CONFIG) as [ReportType, typeof REPORT_TYPE_CONFIG[ReportType]][]).map(([type, cfg]) => (
                    <button key={type} type="button"
                      onClick={() => setCreateForm(p => ({ ...p, type, name: p.name || `${cfg.label} Report` }))}
                      className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border text-left transition-all ${createForm.type === type ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] shadow-sm" : "border-[var(--color-border)] hover:border-[var(--color-border-hover)] hover:bg-gray-50"}`}>
                      <div className={`w-7 h-7 rounded-lg ${cfg.bg} flex items-center justify-center shrink-0`}>
                        <cfg.icon className={`w-3.5 h-3.5 ${cfg.color}`} />
                      </div>
                      <span className="text-[12px] font-semibold text-[var(--color-text)]">{cfg.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Name */}
              <div>
                <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Report Name</label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={e => setCreateForm(p => ({ ...p, name: e.target.value }))}
                  placeholder={`${REPORT_TYPE_CONFIG[createForm.type].label} Report`}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
                />
              </div>

              {/* Format */}
              <div>
                <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2">Output Format</label>
                <div className="flex gap-3">
                  {(["csv", "pdf"] as const).map(f => (
                    <button key={f} type="button"
                      onClick={() => setCreateForm(p => ({ ...p, format: f }))}
                      className={`flex-1 py-2.5 rounded-lg border text-[13px] font-bold transition-all uppercase tracking-wide ${createForm.format === f ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] text-[var(--color-primary)]" : "border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50"}`}>
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div className="p-3 bg-gray-50 border border-[var(--color-border)] rounded-xl text-[12px] text-[var(--color-text-secondary)]">
                <Calendar className="w-3.5 h-3.5 inline mr-1.5 text-[var(--color-text-tertiary)]" />
                {REPORT_TYPE_CONFIG[createForm.type].description}. Report covers all data up to now.
              </div>

              <div className="flex gap-3 pt-1">
                <button type="button" onClick={() => setShowCreate(false)} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
                <Button type="submit" loading={creating} className="flex-1 justify-center">
                  <FileBarChart className="w-3.5 h-3.5 mr-1.5" />Generate Report
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
