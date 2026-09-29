"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Mail,
  Plus,
  RefreshCw,
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  MousePointerClick,
  Eye,
  RotateCcw,
  Send,
  Edit3,
  Trash2,
  MoreHorizontal,
  AlertTriangle,
  TrendingUp,
  Inbox,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { EmailDelivery, EmailTemplate, EmailStatus } from "@/types";

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Email status badge ───────────────────────────────────────────────────────
function EmailStatusBadge({ status }: { status: EmailStatus }) {
  const cfg: Record<string, { label: string; cls: string; Icon: any }> = {
    delivered: { label: "Delivered", cls: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle2 },
    opened: { label: "Opened", cls: "bg-blue-50 text-blue-700 border-blue-200", Icon: Eye },
    clicked: { label: "Clicked", cls: "bg-indigo-50 text-indigo-700 border-indigo-200", Icon: MousePointerClick },
    sent: { label: "Sent", cls: "bg-gray-50 text-gray-600 border-gray-200", Icon: Send },
    queued: { label: "Queued", cls: "bg-indigo-50 text-indigo-600 border-indigo-200", Icon: Clock },
    pending: { label: "Pending", cls: "bg-gray-50 text-gray-500 border-gray-200", Icon: Clock },
    bounced: { label: "Bounced", cls: "bg-red-50 text-red-700 border-red-200", Icon: XCircle },
    failed: { label: "Failed", cls: "bg-red-50 text-red-700 border-red-200", Icon: XCircle },
    unsubscribed: { label: "Unsubscribed", cls: "bg-amber-50 text-amber-700 border-amber-200", Icon: AlertTriangle },
    complained: { label: "Complained", cls: "bg-orange-50 text-orange-700 border-orange-200", Icon: AlertCircle },
  };
  const c = cfg[status] || cfg.sent;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${c.cls}`}>
      <c.Icon className="w-3 h-3" />
      {c.label}
    </span>
  );
}

// ─── Demo data ────────────────────────────────────────────────────────────────
const NAMES = ["Atul Kumar", "Priya Sharma", "Rahul Singh", "Ananya Verma", "Dev Patel", "Sneha Nair", "Arjun Mehta", "Kavya Reddy", "Vikram Joshi", "Pooja Gupta", "Aditya Choudhary", "Lakshmi Iyer"];
const STATUSES: EmailStatus[] = ["delivered", "opened", "clicked", "bounced", "delivered", "opened", "sent", "delivered", "failed", "delivered", "opened", "delivered"];

const BASE_EMAIL_TIME = new Date("2026-09-29T12:00:00.000Z").getTime();

const DEMO_DELIVERIES: EmailDelivery[] = NAMES.map((name, i) => ({
  id: `del-${i + 1}`,
  status: STATUSES[i],
  recipient_name: name,
  recipient_email: `${name.split(" ")[0].toLowerCase()}${i + 1}@example.com`,
  subject: "Your Certificate is Ready — CertiFlow",
  certificate_id: `cert-${i + 1}`,
  sent_at: new Date(BASE_EMAIL_TIME - i * 3600000 * 3).toISOString(),
  delivered_at: STATUSES[i] !== "failed" && STATUSES[i] !== "bounced" ? new Date(BASE_EMAIL_TIME - i * 3600000 * 3 + 30000).toISOString() : undefined,
  opened_at: ["opened", "clicked"].includes(STATUSES[i]) ? new Date(BASE_EMAIL_TIME - i * 3600000 * 2).toISOString() : undefined,
  created_at: new Date(BASE_EMAIL_TIME - i * 3600000 * 3).toISOString(),
}));

const DEMO_TEMPLATES: EmailTemplate[] = [
  {
    id: "etmpl-1", name: "Certificate Ready", subject: "Your Certificate is Ready — {{org_name}}",
    html_body: "<h1>Hi {{recipient_name}},</h1><p>Your certificate for <strong>{{program_name}}</strong> is ready.</p>",
    text_body: "Hi {{recipient_name}}, Your certificate is ready.", variables: ["recipient_name", "program_name", "org_name", "certificate_url"],
    is_default: true, created_at: "2026-08-30T10:00:00.000Z", updated_at: "2026-09-24T10:00:00.000Z",
  },
  {
    id: "etmpl-2", name: "Certificate Reminder", subject: "Reminder: Pick up your certificate — {{program_name}}",
    html_body: "<h1>Hi {{recipient_name}},</h1><p>This is a reminder to download your certificate.</p>",
    text_body: "Hi {{recipient_name}}, Reminder: your certificate is waiting.", variables: ["recipient_name", "program_name", "certificate_url"],
    is_default: false, created_at: "2026-09-15T10:00:00.000Z", updated_at: "2026-09-27T10:00:00.000Z",
  },
  {
    id: "etmpl-3", name: "Bulk Issuance Complete", subject: "Bulk issuance completed — {{job_name}}",
    html_body: "<p>Your bulk certificate job <strong>{{job_name}}</strong> has completed.</p>",
    text_body: "Your bulk job {{job_name}} is complete.", variables: ["job_name", "total_issued", "failed_count", "download_url"],
    is_default: false, created_at: "2026-09-22T10:00:00.000Z", updated_at: "2026-09-28T10:00:00.000Z",
  },
];

// ─── KPI mini card ────────────────────────────────────────────────────────────
function MiniKpi({ label, value, pct, color }: { label: string; value: number | string; pct?: number; color: string }) {
  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
      <p className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-2">{label}</p>
      <p className="text-[26px] font-bold text-[var(--color-text)] leading-none">
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
      {pct !== undefined && (
        <div className="mt-3">
          <div className="flex justify-between text-[11px] mb-1">
            <span className="text-[var(--color-text-tertiary)]">Rate</span>
            <span className="font-semibold">{pct}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-1.5">
            <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Template card ────────────────────────────────────────────────────────────
function TemplateCard({ tmpl, onDelete }: { tmpl: EmailTemplate; onDelete: (id: string) => void }) {
  const [open, setOpen] = useState(false);
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    return d < 86400 ? `${Math.round(d / 3600)}h ago` : `${Math.round(d / 86400)}d ago`;
  };
  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
          <Mail className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex items-center gap-2">
          {tmpl.is_default && (
            <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-1.5 py-0.5 rounded-full">DEFAULT</span>
          )}
          <div className="relative">
            <button onClick={() => setOpen(o => !o)} className="p-1.5 text-gray-300 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {open && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
                <div className="absolute right-0 top-full mt-1 z-20 w-36 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
                  <button className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50">
                    <Edit3 className="w-3.5 h-3.5 text-gray-400" /> Edit
                  </button>
                  <button onClick={() => { setOpen(false); onDelete(tmpl.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50">
                    <Trash2 className="w-3.5 h-3.5" /> Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-1">{tmpl.name}</h3>
      <p className="text-[12px] font-mono text-[var(--color-text-secondary)] bg-gray-50 px-2 py-1 rounded-lg truncate mb-3">{tmpl.subject}</p>
      <div className="flex flex-wrap gap-1 mb-3">
        {tmpl.variables.map(v => (
          <span key={v} className="text-[11px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-mono">{`{{${v}}}`}</span>
        ))}
      </div>
      <div className="pt-3 border-t border-[var(--color-border)] text-[11px] text-[var(--color-text-tertiary)] flex justify-between">
        <span>{tmpl.variables.length} variables</span>
        <span suppressHydrationWarning>Updated {relTime(tmpl.updated_at)}</span>
      </div>
    </div>
  );
}

// ─── Suppression list ─────────────────────────────────────────────────────────
const DEMO_SUPPRESSIONS = [
  { email: "bounced@example.com", reason: "hard_bounce", added_at: "2026-09-24T10:00:00.000Z" },
  { email: "unsubscribed@corp.io", reason: "unsubscribe", added_at: "2026-09-17T10:00:00.000Z" },
  { email: "complaint@mail.net", reason: "spam_complaint", added_at: "2026-09-09T10:00:00.000Z" },
];

type EmailTab = "deliveries" | "templates" | "suppressions";

// ─────────────────────────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────────────────────────
export default function EmailPage() {
  const [tab, setTab] = useState<EmailTab>("deliveries");
  const [loading, setLoading] = useState(true);
  const [deliveries, setDeliveries] = useState<EmailDelivery[]>([]);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [suppressions, setSuppressions] = useState(DEMO_SUPPRESSIONS);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<EmailStatus | "all">("all");
  const [showCreateTmpl, setShowCreateTmpl] = useState(false);
  const [newTmpl, setNewTmpl] = useState({ name: "", subject: "" });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [dRes, tRes] = await Promise.allSettled([
        api.email.listDeliveries({ limit: 50 }),
        api.email.listTemplates(),
      ]);
      setDeliveries(dRes.status === "fulfilled" ? (dRes.value?.items || dRes.value || []) : DEMO_DELIVERIES);
      setTemplates(tRes.status === "fulfilled" ? ((tRes.value as any)?.items || (Array.isArray(tRes.value) ? tRes.value : [])) : DEMO_TEMPLATES);
    } catch {
      setDeliveries(DEMO_DELIVERIES);
      setTemplates(DEMO_TEMPLATES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // KPI calculations
  const total = deliveries.length;
  const delivered = deliveries.filter(d => ["delivered", "opened", "clicked"].includes(d.status)).length;
  const opened = deliveries.filter(d => ["opened", "clicked"].includes(d.status)).length;
  const bounced = deliveries.filter(d => d.status === "bounced").length;
  const deliveryRate = total ? Math.round((delivered / total) * 100) : 0;
  const openRate = delivered ? Math.round((opened / delivered) * 100) : 0;

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  const filteredDeliveries = deliveries.filter(d => {
    const matchStatus = statusFilter === "all" || d.status === statusFilter;
    const matchSearch = !search || d.recipient_name?.toLowerCase().includes(search.toLowerCase()) || d.recipient_email?.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const STATUS_OPTS: { id: EmailStatus | "all"; label: string }[] = [
    { id: "all", label: "All" },
    { id: "delivered", label: "Delivered" },
    { id: "opened", label: "Opened" },
    { id: "bounced", label: "Bounced" },
    { id: "failed", label: "Failed" },
  ];

  const handleCreateTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await api.email.createTemplate({
        name: newTmpl.name,
        subject: newTmpl.subject,
        html_body: `<p>Hi {{recipient_name}},</p>`,
        variables: ["recipient_name"],
      });
      setTemplates(p => [res, ...p]);
    } catch {
      setTemplates(p => [{
        id: `etmpl-${Date.now()}`,
        name: newTmpl.name,
        subject: newTmpl.subject,
        html_body: "<p>Hi {{recipient_name}},</p>",
        text_body: "",
        variables: ["recipient_name"],
        is_default: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }, ...p]);
    } finally {
      setCreating(false);
      setShowCreateTmpl(false);
      setNewTmpl({ name: "", subject: "" });
    }
  };

  const TAB_DEFS: { id: EmailTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "deliveries", label: "Deliveries", icon: Send },
    { id: "templates", label: "Templates", icon: Edit3 },
    { id: "suppressions", label: "Suppressions", icon: AlertTriangle },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Email Center</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">Transactional delivery logs, email templates, and suppression list</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
          </Button>
          {tab === "templates" && (
            <Button size="sm" onClick={() => setShowCreateTmpl(true)}>
              <Plus className="w-4 h-4 mr-1.5" />New Template
            </Button>
          )}
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MiniKpi label="Emails Sent" value={total} color="bg-[var(--color-primary)]" />
        <MiniKpi label="Delivery Rate" value={`${deliveryRate}%`} pct={deliveryRate} color="bg-emerald-500" />
        <MiniKpi label="Open Rate" value={`${openRate}%`} pct={openRate} color="bg-blue-500" />
        <MiniKpi label="Bounced" value={bounced} color="bg-red-400" />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0.5 bg-gray-100/70 rounded-xl p-1 w-fit">
        {TAB_DEFS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
            <t.icon className="w-3.5 h-3.5" />{t.label}
          </button>
        ))}
      </div>

      {/* ── Deliveries tab ─────────────────────────────────────────────── */}
      {tab === "deliveries" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex items-center bg-gray-100/70 rounded-xl p-1 gap-0.5 flex-wrap">
              {STATUS_OPTS.map(s => (
                <button key={s.id} onClick={() => setStatusFilter(s.id)}
                  className={`px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all ${statusFilter === s.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
                  {s.label}
                </button>
              ))}
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
              <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search recipient…"
                className="pl-9 pr-3.5 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-[var(--color-primary)] transition-colors w-56" />
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
            <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
              <span className="col-span-3">Recipient</span>
              <span className="col-span-4">Subject</span>
              <span className="col-span-2">Status</span>
              <span className="col-span-2 text-right">Sent</span>
              <span className="col-span-1 text-right">Action</span>
            </div>
            <div className="divide-y divide-[var(--color-border)]">
              {loading ? (
                [1, 2, 3, 4].map(i => (
                  <div key={i} className="px-5 py-4 grid grid-cols-12 gap-3 items-center">
                    <Skeleton className="col-span-3 h-4" />
                    <Skeleton className="col-span-4 h-3" />
                    <Skeleton className="col-span-2 h-4 w-14" />
                    <Skeleton className="col-span-2 h-3 ml-auto" />
                    <Skeleton className="col-span-1 h-4 ml-auto w-6" />
                  </div>
                ))
              ) : filteredDeliveries.length === 0 ? (
                <div className="px-5 py-16 text-center">
                  <Inbox className="w-8 h-8 text-gray-200 mx-auto mb-3" />
                  <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No deliveries found</p>
                </div>
              ) : (
                filteredDeliveries.map(d => (
                  <div key={d.id} className="px-5 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50 transition-colors">
                    <div className="col-span-3">
                      <p className="text-[13px] font-semibold text-[var(--color-text)] truncate">{d.recipient_name || "—"}</p>
                      <p className="text-[11px] text-[var(--color-text-tertiary)] truncate">{d.recipient_email}</p>
                    </div>
                    <div className="col-span-4">
                      <p className="text-[12px] text-[var(--color-text-secondary)] truncate">{d.subject}</p>
                    </div>
                    <div className="col-span-2"><EmailStatusBadge status={d.status} /></div>
                    <div className="col-span-2 text-right">
                      <span className="text-[11px] text-[var(--color-text-tertiary)]" suppressHydrationWarning>{d.sent_at ? relTime(d.sent_at) : "—"}</span>
                    </div>
                    <div className="col-span-1 flex justify-end">
                      {(d.status === "failed" || d.status === "bounced") && (
                        <button className="p-1.5 rounded-lg text-gray-300 hover:text-blue-600 hover:bg-blue-50 transition-colors" title="Retry">
                          <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Templates tab ─────────────────────────────────────────────── */}
      {tab === "templates" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading ? (
            [1, 2].map(i => <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5"><Skeleton className="h-28" /></div>)
          ) : (
            <>
              <button onClick={() => setShowCreateTmpl(true)}
                className="bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] hover:border-blue-400 hover:bg-blue-50/20 transition-all group flex flex-col items-center justify-center gap-3 py-12">
                <div className="w-10 h-10 rounded-xl border-2 border-dashed border-gray-200 group-hover:border-blue-400 flex items-center justify-center transition-colors">
                  <Plus className="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
                </div>
                <p className="text-[13px] font-bold text-[var(--color-text-secondary)] group-hover:text-blue-600">New Template</p>
              </button>
              {templates.map(t => (
                <TemplateCard key={t.id} tmpl={t} onDelete={id => setTemplates(p => p.filter(t => t.id !== id))} />
              ))}
            </>
          )}
        </div>
      )}

      {/* ── Suppressions tab ─────────────────────────────────────────── */}
      {tab === "suppressions" && (
        <div className="space-y-4">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-[13px] text-amber-700">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
            <span>Emails in the suppression list will not be delivered. These addresses opted out, reported spam, or had hard bounces. Remove with caution.</span>
          </div>

          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
            <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
              <span className="col-span-5">Email Address</span>
              <span className="col-span-4">Reason</span>
              <span className="col-span-2 text-right">Added</span>
              <span className="col-span-1 text-right">Remove</span>
            </div>
            <div className="divide-y divide-[var(--color-border)]">
              {suppressions.map((s, i) => (
                <div key={i} className="px-5 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50">
                  <div className="col-span-5">
                    <span className="text-[13px] font-mono text-[var(--color-text)]">{s.email}</span>
                  </div>
                  <div className="col-span-4">
                    <span className="text-[12px] text-[var(--color-text-secondary)]">{s.reason.replace(/_/g, " ")}</span>
                  </div>
                  <div className="col-span-2 text-right">
                    <span className="text-[11px] text-[var(--color-text-tertiary)]" suppressHydrationWarning>{relTime(s.added_at)}</span>
                  </div>
                  <div className="col-span-1 flex justify-end">
                    <button
                      onClick={async () => {
                        try { await api.email.removeSupression(s.email); } catch { /* demo */ }
                        setSuppressions(p => p.filter((_, j) => j !== i));
                      }}
                      className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors" title="Remove from suppression list">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
              {suppressions.length === 0 && (
                <div className="px-5 py-12 text-center">
                  <CheckCircle2 className="w-8 h-8 text-emerald-300 mx-auto mb-3" />
                  <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">Suppression list is empty</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Template Modal */}
      {showCreateTmpl && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) setShowCreateTmpl(false); }}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-[var(--color-border)]">
            <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
              <h2 className="text-[17px] font-bold text-[var(--color-text)]">New Email Template</h2>
              <button onClick={() => setShowCreateTmpl(false)} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
            </div>
            <form onSubmit={handleCreateTemplate} className="px-6 py-5 space-y-4">
              <div>
                <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Template Name <span className="text-red-500">*</span></label>
                <input required value={newTmpl.name} onChange={e => setNewTmpl(p => ({ ...p, name: e.target.value }))} placeholder="e.g. Certificate Ready"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors" />
              </div>
              <div>
                <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Subject Line <span className="text-red-500">*</span></label>
                <input required value={newTmpl.subject} onChange={e => setNewTmpl(p => ({ ...p, subject: e.target.value }))} placeholder="e.g. Your Certificate is Ready — {{org_name}}"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors" />
              </div>
              <div className="p-3 bg-blue-50 border border-blue-100 rounded-xl text-[12px] text-blue-700">
                The HTML body editor is available after creation. This creates a blank template with the subject line.
              </div>
              <div className="flex gap-3">
                <button type="button" onClick={() => setShowCreateTmpl(false)} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
                <Button type="submit" loading={creating} className="flex-1 justify-center"><Mail className="w-3.5 h-3.5 mr-1.5" />Create</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
