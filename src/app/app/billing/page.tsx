"use client";

import { useState, useEffect, useCallback } from "react";
import {
  CreditCard,
  RefreshCw,
  Download,
  CheckCircle2,
  XCircle,
  AlertCircle,
  TrendingUp,
  Award,
  Mail,
  ShieldCheck,
  Zap,
  ChevronRight,
  ExternalLink,
  Clock,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { Invoice, Subscription, UsageMeter } from "@/types";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Demo data ────────────────────────────────────────────────────────────────
const DEMO_SUBSCRIPTION: Subscription = {
  id: "sub-1",
  plan_id: "growth",
  plan_name: "Growth",
  status: "active",
  current_period_start: new Date(Date.now() - 86400 * 15 * 1000).toISOString(),
  current_period_end: new Date(Date.now() + 86400 * 15 * 1000).toISOString(),
  cancel_at_period_end: false,
  amount: 4900,
  currency: "usd",
  interval: "month",
  seats: 5,
  trial_end: undefined,
};

const DEMO_METERS: UsageMeter[] = [
  { id: "m1", label: "Certificates Issued", used: 2480, limit: 5000, unit: "certs", overage_rate: 0.02, color: "indigo" },
  { id: "m2", label: "Emails Sent", used: 2980, limit: 10000, unit: "emails", overage_rate: 0.001, color: "blue" },
  { id: "m3", label: "Digital Credentials", used: 340, limit: 500, unit: "credentials", overage_rate: 0.05, color: "purple" },
  { id: "m4", label: "Storage Used", used: 1.4, limit: 25, unit: "GB", overage_rate: 0.1, color: "emerald" },
  { id: "m5", label: "API Requests", used: 84200, limit: 500000, unit: "reqs", overage_rate: 0.0001, color: "amber" },
  { id: "m6", label: "Team Seats", used: 3, limit: 5, unit: "seats", overage_rate: 10, color: "gray" },
];

const DEMO_INVOICES: Invoice[] = [
  { id: "inv-1", invoice_number: "INV-2026-009", amount: 4900, currency: "usd", status: "paid", period_start: "2026-09-01", period_end: "2026-09-30", paid_at: "2026-09-01", created_at: "2026-09-01", pdf_url: "#" },
  { id: "inv-2", invoice_number: "INV-2026-008", amount: 4900, currency: "usd", status: "paid", period_start: "2026-08-01", period_end: "2026-08-31", paid_at: "2026-08-01", created_at: "2026-08-01", pdf_url: "#" },
  { id: "inv-3", invoice_number: "INV-2026-007", amount: 5240, currency: "usd", status: "paid", period_start: "2026-07-01", period_end: "2026-07-31", paid_at: "2026-07-01", created_at: "2026-07-01", pdf_url: "#" },
  { id: "inv-4", invoice_number: "INV-2026-006", amount: 4900, currency: "usd", status: "paid", period_start: "2026-06-01", period_end: "2026-06-30", paid_at: "2026-06-01", created_at: "2026-06-01", pdf_url: "#" },
];

// ─── Plans ────────────────────────────────────────────────────────────────────
const PLANS = [
  {
    id: "starter", name: "Starter", price: 19, interval: "month",
    features: ["1,000 certificates/mo", "5,000 emails/mo", "100 credentials", "5 GB storage", "2 team seats", "Email support"],
    highlight: false,
  },
  {
    id: "growth", name: "Growth", price: 49, interval: "month",
    features: ["5,000 certificates/mo", "10,000 emails/mo", "500 credentials", "25 GB storage", "5 team seats", "Priority support", "API access"],
    highlight: true,
  },
  {
    id: "scale", name: "Scale", price: 149, interval: "month",
    features: ["25,000 certificates/mo", "100,000 emails/mo", "5,000 credentials", "250 GB storage", "20 team seats", "Dedicated support", "Custom domain", "SSO / SAML"],
    highlight: false,
  },
  {
    id: "enterprise", name: "Enterprise", price: null, interval: "month",
    features: ["Unlimited certificates", "Unlimited emails", "Unlimited credentials", "Custom storage", "Unlimited seats", "SLA + dedicated CSM", "On-prem option"],
    highlight: false,
  },
];

// ─── Usage meter bar ──────────────────────────────────────────────────────────
function UsageBar({ meter }: { meter: UsageMeter }) {
  const pct = Math.min((meter.used / meter.limit) * 100, 100);
  const warning = pct >= 80;
  const critical = pct >= 95;
  const colorClass = critical ? "bg-red-500" : warning ? "bg-amber-400" : `bg-${meter.color || "indigo"}-500`;
  const trackClass = critical ? "bg-red-100" : warning ? "bg-amber-50" : "bg-gray-100";

  const fmt = (n: number, u: string) => {
    if (u === "GB") return `${n.toFixed(1)} GB`;
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return `${n}`;
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-[12px]">
        <span className="font-semibold text-[var(--color-text)]">{meter.label}</span>
        <span className={`font-bold ${critical ? "text-red-600" : warning ? "text-amber-600" : "text-[var(--color-text-secondary)]"}`}>
          {fmt(meter.used, meter.unit)} / {fmt(meter.limit, meter.unit)}
          {meter.unit !== "GB" && meter.unit !== "seats" && ` ${meter.unit}`}
        </span>
      </div>
      <div className={`w-full h-2.5 rounded-full ${trackClass}`}>
        <div className={`h-2.5 rounded-full transition-all duration-700 ${colorClass}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-[10px] text-[var(--color-text-tertiary)]">{Math.round(pct)}% used</span>
        {warning && (
          <span className={`text-[10px] font-semibold ${critical ? "text-red-500" : "text-amber-500"}`}>
            {critical ? "⚠ At limit — overage applies" : "Approaching limit"}
          </span>
        )}
        {!warning && meter.overage_rate && (
          <span className="text-[10px] text-[var(--color-text-tertiary)]">+${meter.overage_rate} per extra {meter.unit === "reqs" ? "1k req" : meter.unit}</span>
        )}
      </div>
    </div>
  );
}

// ─── Plan card ────────────────────────────────────────────────────────────────
function PlanCard({ plan, isCurrent, onUpgrade }: { plan: typeof PLANS[0]; isCurrent: boolean; onUpgrade: (id: string) => void }) {
  return (
    <div className={`bg-white rounded-2xl border-2 p-5 relative transition-all ${plan.highlight ? "border-[var(--color-primary)] shadow-md" : isCurrent ? "border-emerald-400" : "border-[var(--color-border)] hover:border-[var(--color-border-hover)]"}`}>
      {plan.highlight && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="bg-[var(--color-primary)] text-white text-[11px] font-bold px-3 py-0.5 rounded-full flex items-center gap-1">
            <Star className="w-3 h-3" />MOST POPULAR
          </span>
        </div>
      )}
      {isCurrent && (
        <div className="absolute -top-3 right-4">
          <span className="bg-emerald-500 text-white text-[11px] font-bold px-3 py-0.5 rounded-full">CURRENT PLAN</span>
        </div>
      )}

      <div className="mb-4">
        <h3 className="text-[16px] font-bold text-[var(--color-text)]">{plan.name}</h3>
        <div className="flex items-baseline gap-1 mt-1">
          {plan.price !== null ? (
            <>
              <span className="text-[28px] font-bold text-[var(--color-text)]">${plan.price}</span>
              <span className="text-[13px] text-[var(--color-text-tertiary)]">/month</span>
            </>
          ) : (
            <span className="text-[20px] font-bold text-[var(--color-text)]">Custom pricing</span>
          )}
        </div>
      </div>

      <ul className="space-y-2 mb-5">
        {plan.features.map(f => (
          <li key={f} className="flex items-center gap-2 text-[12px] text-[var(--color-text-secondary)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
            {f}
          </li>
        ))}
      </ul>

      {isCurrent ? (
        <div className="w-full py-2 rounded-xl text-center text-[13px] font-bold text-emerald-600 bg-emerald-50 border border-emerald-200">
          Active Plan
        </div>
      ) : (
        <button onClick={() => onUpgrade(plan.id)}
          className={`w-full py-2 rounded-xl text-[13px] font-bold transition-all ${plan.highlight ? "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-dark)]" : "border border-[var(--color-border)] text-[var(--color-text)] hover:bg-gray-50"}`}>
          {plan.price === null ? "Contact Sales" : plan.price > 49 ? "Upgrade" : "Downgrade"}
        </button>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
type BillingTab = "overview" | "plans" | "invoices";

export default function BillingPage() {
  const [tab, setTab] = useState<BillingTab>("overview");
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [meters, setMeters] = useState<UsageMeter[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [sRes, mRes, iRes] = await Promise.allSettled([
        api.billing.getSubscription(),
        api.billing.getUsage(),
        api.billing.getInvoices(),
      ]);
      setSubscription(sRes.status === "fulfilled" ? sRes.value : DEMO_SUBSCRIPTION);
      setMeters(mRes.status === "fulfilled" ? (mRes.value?.meters || (Array.isArray(mRes.value) ? mRes.value : DEMO_METERS)) : DEMO_METERS);
      setInvoices(iRes.status === "fulfilled" ? ((iRes.value as any)?.items || (Array.isArray(iRes.value) ? iRes.value : [])) : DEMO_INVOICES);
    } catch {
      setSubscription(DEMO_SUBSCRIPTION);
      setMeters(DEMO_METERS);
      setInvoices(DEMO_INVOICES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleUpgrade = (planId: string) => {
    alert(`Redirecting to checkout for the ${planId} plan…`);
  };

  const handleCancelPlan = () => {
    if (!confirm("Cancel your subscription at end of billing period?")) return;
    setSubscription(prev => prev ? { ...prev, cancel_at_period_end: true } : prev);
  };

  const daysLeft = subscription ? Math.ceil((new Date(subscription.current_period_end).getTime() - Date.now()) / 86400000) : 0;
  const periodPct = subscription ? Math.round(((Date.now() - new Date(subscription.current_period_start).getTime()) / (new Date(subscription.current_period_end).getTime() - new Date(subscription.current_period_start).getTime())) * 100) : 0;

  const fmtAmount = (cents: number, currency: string) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: currency.toUpperCase() }).format(cents / 100);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Billing</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">Subscription, usage meters, and invoice history</p>
        </div>
        <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0.5 bg-gray-100/70 rounded-xl p-1 w-fit">
        {([
          { id: "overview" as BillingTab, label: "Overview" },
          { id: "plans" as BillingTab, label: "Plans" },
          { id: "invoices" as BillingTab, label: "Invoices" },
        ]).map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Overview tab ─────────────────────────────────────────────── */}
      {tab === "overview" && (
        <div className="space-y-6">
          {/* Current plan card */}
          {loading ? <Skeleton className="h-44 w-full rounded-2xl" /> : subscription && (
            <div className={`rounded-2xl border-2 p-6 ${subscription.cancel_at_period_end ? "border-amber-400 bg-amber-50/30" : "border-[var(--color-primary)] bg-[var(--color-primary-subtle)]"}`}>
              {subscription.cancel_at_period_end && (
                <div className="flex items-center gap-2 text-amber-700 text-[12px] font-semibold mb-4 bg-amber-100 border border-amber-200 px-3 py-2 rounded-xl">
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                  Cancels at end of billing period · {daysLeft} days remaining
                </div>
              )}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2.5 mb-1">
                    <h3 className="text-[20px] font-bold text-[var(--color-text)]">{subscription.plan_name} Plan</h3>
                    <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-full">ACTIVE</span>
                  </div>
                  <p className="text-[14px] text-[var(--color-text-secondary)]">
                    {fmtAmount(subscription.amount, subscription.currency)} / {subscription.interval} · {subscription.seats} seats included
                  </p>
                  <p className="text-[12px] text-[var(--color-text-tertiary)] mt-1">
                    Current period: {new Date(subscription.current_period_start).toLocaleDateString("en-US", { month: "short", day: "numeric" })} – {new Date(subscription.current_period_end).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button onClick={() => setTab("plans")} className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white text-[13px] font-semibold hover:bg-[var(--color-primary-dark)] transition-colors">
                    <TrendingUp className="w-3.5 h-3.5" />Upgrade
                  </button>
                  {!subscription.cancel_at_period_end && (
                    <button onClick={handleCancelPlan} className="px-4 py-2 rounded-xl border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-white transition-colors">
                      Cancel
                    </button>
                  )}
                </div>
              </div>

              {/* Billing period progress */}
              <div className="mt-5">
                <div className="flex items-center justify-between text-[11px] mb-1.5">
                  <span className="text-[var(--color-text-tertiary)]">Billing period</span>
                  <span className="font-semibold text-[var(--color-text-secondary)]">{daysLeft} days remaining</span>
                </div>
                <div className="w-full bg-white/60 h-1.5 rounded-full">
                  <div className="h-1.5 rounded-full bg-[var(--color-primary)] transition-all duration-700" style={{ width: `${periodPct}%` }} />
                </div>
              </div>
            </div>
          )}

          {/* Payment method */}
          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gray-50 border border-[var(--color-border)] flex items-center justify-center">
                  <CreditCard className="w-5 h-5 text-gray-500" />
                </div>
                <div>
                  <p className="text-[13px] font-bold text-[var(--color-text)]">Visa •••• 4242</p>
                  <p className="text-[11px] text-[var(--color-text-tertiary)]">Expires 12/2028 · Default payment method</p>
                </div>
              </div>
              <button className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline">Update</button>
            </div>
          </div>

          {/* Usage meters */}
          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="text-[15px] font-bold text-[var(--color-text)]">Current Period Usage</h3>
                <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">Usage resets at the start of each billing cycle</p>
              </div>
              <button onClick={() => setTab("plans")} className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-1">
                Upgrade for more <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-12" />)}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {meters.map(m => <UsageBar key={m.id} meter={m} />)}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Plans tab ────────────────────────────────────────────────── */}
      {tab === "plans" && (
        <div className="space-y-4">
          <div className="text-center mb-6">
            <p className="text-[14px] text-[var(--color-text-secondary)]">Changes take effect immediately. You'll be charged the prorated difference.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mt-6">
            {PLANS.map(plan => (
              <PlanCard key={plan.id} plan={plan} isCurrent={subscription?.plan_id === plan.id} onUpgrade={handleUpgrade} />
            ))}
          </div>
          <div className="flex items-center justify-center gap-2 pt-4 text-[12px] text-[var(--color-text-tertiary)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />All plans include 99.9% uptime SLA, SOC 2 Type II compliance, and GDPR DPA
          </div>
        </div>
      )}

      {/* ── Invoices tab ─────────────────────────────────────────────── */}
      {tab === "invoices" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
            <div>
              <h3 className="text-[15px] font-bold text-[var(--color-text)]">Invoice History</h3>
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">All invoices are auto-collected on the billing date</p>
            </div>
          </div>

          <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
            <span className="col-span-3">Invoice</span>
            <span className="col-span-3">Period</span>
            <span className="col-span-2">Status</span>
            <span className="col-span-2 text-right">Amount</span>
            <span className="col-span-2 text-right">Download</span>
          </div>

          <div className="divide-y divide-[var(--color-border)]">
            {loading ? (
              [1, 2, 3].map(i => (
                <div key={i} className="px-5 py-4 grid grid-cols-12 gap-3 items-center">
                  <Skeleton className="col-span-3 h-4" />
                  <Skeleton className="col-span-3 h-3" />
                  <Skeleton className="col-span-2 h-4 w-12" />
                  <Skeleton className="col-span-2 h-4 ml-auto w-16" />
                  <Skeleton className="col-span-2 h-4 ml-auto w-8" />
                </div>
              ))
            ) : invoices.length === 0 ? (
              <div className="px-5 py-16 text-center">
                <CreditCard className="w-8 h-8 text-gray-200 mx-auto mb-3" />
                <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No invoices yet</p>
              </div>
            ) : (
              invoices.map(inv => (
                <div key={inv.id} className="px-5 py-4 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50 transition-colors">
                  <div className="col-span-3">
                    <p className="text-[13px] font-semibold text-[var(--color-text)] font-mono">{inv.invoice_number}</p>
                    <p className="text-[11px] text-[var(--color-text-tertiary)]">
                      {inv.paid_at ? `Paid ${new Date(inv.paid_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}` : "—"}
                    </p>
                  </div>
                  <div className="col-span-3">
                    <p className="text-[12px] text-[var(--color-text-secondary)]">
                      {new Date(inv.period_start).toLocaleDateString("en-US", { month: "short", year: "numeric" })}
                    </p>
                  </div>
                  <div className="col-span-2">
                    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${inv.status === "paid" ? "bg-emerald-50 text-emerald-700 border-emerald-200" : inv.status === "open" ? "bg-amber-50 text-amber-700 border-amber-200" : "bg-red-50 text-red-700 border-red-200"}`}>
                      {inv.status === "paid" ? <CheckCircle2 className="w-3 h-3" /> : inv.status === "open" ? <Clock className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                      {inv.status.charAt(0).toUpperCase() + inv.status.slice(1)}
                    </span>
                  </div>
                  <div className="col-span-2 text-right">
                    <span className="text-[14px] font-bold text-[var(--color-text)]">{fmtAmount(inv.amount, inv.currency)}</span>
                  </div>
                  <div className="col-span-2 flex justify-end">
                    {inv.pdf_url && (
                      <a href={inv.pdf_url} target="_blank" rel="noopener" className="flex items-center gap-1 text-[12px] font-semibold text-[var(--color-primary)] hover:underline">
                        <Download className="w-3.5 h-3.5" />PDF
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
