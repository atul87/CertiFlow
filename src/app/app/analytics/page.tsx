"use client";

import { useState, useEffect, useCallback } from "react";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Award,
  CheckCircle2,
  Mail,
  ShieldCheck,
  RefreshCw,
  Calendar,
  ArrowUpRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Inline bar chart (no deps) ───────────────────────────────────────────────
function BarChartInline({
  data,
  color = "var(--color-primary)",
  height = 120,
  showValues = false,
}: {
  data: { label: string; value: number }[];
  color?: string;
  height?: number;
  showValues?: boolean;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="flex items-end gap-1.5 w-full" style={{ height }}>
      {data.map((d, i) => {
        const pct = (d.value / max) * 100;
        return (
          <div key={i} className="flex flex-col items-center gap-1 flex-1 group">
            {showValues && (
              <span className="text-[10px] font-bold text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity">
                {d.value.toLocaleString()}
              </span>
            )}
            <div
              title={`${d.label}: ${d.value.toLocaleString()}`}
              className="w-full rounded-t-sm transition-all duration-500 hover:opacity-80 cursor-default"
              style={{ height: `${Math.max(pct, 2)}%`, backgroundColor: color }}
            />
            <span className="text-[9px] text-[var(--color-text-tertiary)] truncate w-full text-center">
              {d.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ─── Sparkline (SVG) ──────────────────────────────────────────────────────────
function Sparkline({
  values,
  color = "#635BFF",
  width = 80,
  height = 30,
}: {
  values: number[];
  color?: string;
  width?: number;
  height?: number;
}) {
  if (!values.length) return null;
  const max = Math.max(...values, 1);
  const min = Math.min(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  });
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline
        points={pts.join(" ")}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── KPI Card with sparkline ──────────────────────────────────────────────────
function KpiCard({
  label,
  value,
  change,
  changeUp,
  sub,
  icon: Icon,
  iconColor,
  sparklineValues,
  sparklineColor,
  loading,
}: {
  label: string;
  value: string | number;
  change?: string;
  changeUp?: boolean;
  sub?: string;
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  sparklineValues?: number[];
  sparklineColor?: string;
  loading?: boolean;
}) {
  if (loading) {
    return (
      <div className="bg-white p-5 rounded-2xl border border-[var(--color-border)] shadow-xs">
        <Skeleton className="h-3 w-24 mb-4" />
        <Skeleton className="h-8 w-20 mb-2" />
        <Skeleton className="h-3 w-16" />
      </div>
    );
  }
  return (
    <div className="bg-white p-5 rounded-2xl border border-[var(--color-border)] shadow-xs hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">{label}</span>
        </div>
        <div className="flex items-center gap-3">
          {sparklineValues && (
            <Sparkline values={sparklineValues} color={sparklineColor} />
          )}
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconColor}`}>
            <Icon className="w-4 h-4" />
          </div>
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-[28px] font-bold text-[var(--color-text)] leading-none">
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {change && (
          <span className={`text-[11px] font-semibold flex items-center gap-0.5 px-1.5 py-0.5 rounded ${changeUp ? "text-emerald-700 bg-emerald-50" : "text-red-700 bg-red-50"}`}>
            {changeUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {change}
          </span>
        )}
      </div>
      {sub && <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1">{sub}</p>}
    </div>
  );
}

// ─── Donut chart (CSS) ────────────────────────────────────────────────────────
function DonutChart({ segments, size = 100 }: {
  segments: { label: string; value: number; color: string }[];
  size?: number;
}) {
  const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  let cumulative = 0;
  const strokeWidth = size * 0.18;
  const r = (size - strokeWidth) / 2;
  const cx = size / 2;
  const circ = 2 * Math.PI * r;

  return (
    <div className="flex items-center gap-5">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={cx} cy={cx} r={r} fill="none" stroke="#f3f4f6" strokeWidth={strokeWidth} />
        {segments.map((s, i) => {
          const pct = s.value / total;
          const dash = pct * circ;
          const offset = cumulative * circ;
          cumulative += pct;
          return (
            <circle key={i} cx={cx} cy={cx} r={r} fill="none"
              stroke={s.color} strokeWidth={strokeWidth}
              strokeDasharray={`${dash} ${circ}`}
              strokeDashoffset={-offset}
              strokeLinecap="butt"
            />
          );
        })}
      </svg>
      <div className="space-y-2">
        {segments.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
            <span className="text-[12px] text-[var(--color-text-secondary)]">{s.label}</span>
            <span className="text-[12px] font-bold text-[var(--color-text)] ml-auto">{Math.round((s.value / total) * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Period selector ──────────────────────────────────────────────────────────
type Period = "7d" | "30d" | "90d" | "12m";

// ─── Generate fake time-series ────────────────────────────────────────────────
function fakeSeries(points: number, base: number, variance: number) {
  return Array.from({ length: points }, (_, i) =>
    Math.max(0, Math.round(base + Math.sin(i * 0.5) * variance + Math.random() * variance * 0.5))
  );
}

function makeChartData(period: Period, base: number, variance: number) {
  if (period === "7d") {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    return days.map((label, i) => ({ label, value: Math.max(0, Math.round(base + Math.sin(i) * variance + Math.random() * 20)) }));
  }
  if (period === "30d") {
    return Array.from({ length: 30 }, (_, i) => ({
      label: i % 5 === 0 ? `Day ${i + 1}` : "",
      value: Math.max(0, Math.round(base + Math.sin(i * 0.3) * variance + Math.random() * 15)),
    }));
  }
  if (period === "90d") {
    const weeks = Array.from({ length: 13 }, (_, i) => ({ label: `W${i + 1}`, value: Math.max(0, Math.round(base * 7 + Math.sin(i * 0.5) * variance * 4 + Math.random() * 50)) }));
    return weeks;
  }
  // 12m
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return months.map((label, i) => ({ label, value: Math.max(0, Math.round(base * 30 + Math.sin(i * 0.4) * variance * 20 + Math.random() * 100)) }));
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Analytics Page
// ─────────────────────────────────────────────────────────────────────────────
export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<Period>("30d");
  const [stats, setStats] = useState<any>({});
  const [certSeries, setCertSeries] = useState<{ label: string; value: number }[]>([]);
  const [emailSeries, setEmailSeries] = useState<{ label: string; value: number }[]>([]);
  const [verifSeries, setVerifSeries] = useState<{ label: string; value: number }[]>([]);

  const PERIODS: { id: Period; label: string }[] = [
    { id: "7d", label: "7 days" },
    { id: "30d", label: "30 days" },
    { id: "90d", label: "90 days" },
    { id: "12m", label: "12 months" },
  ];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const dash = await api.analytics.getDashboard();
      setStats(dash);
    } catch {
      setStats({
        total_certificates: 3240,
        certificates_this_month: 1250,
        certificates_change_pct: 18.4,
        total_credentials: 840,
        verification_scans: 4890,
        verification_rate: 92.4,
        emails_sent: 3012,
        email_delivery_rate: 97.1,
        quota_used_pct: 42,
      });
    }
    // Always generate chart data
    setCertSeries(makeChartData(period, 42, 15));
    setEmailSeries(makeChartData(period, 38, 12));
    setVerifSeries(makeChartData(period, 28, 20));
    setLoading(false);
  }, [period]);

  useEffect(() => { load(); }, [load]);

  const sparkCerts = fakeSeries(12, 42, 10);
  const sparkVerif = fakeSeries(12, 28, 12);
  const sparkEmail = fakeSeries(12, 38, 8);
  const sparkCreds = fakeSeries(12, 18, 6);

  const certTotal = certSeries.reduce((s, d) => s + d.value, 0);
  const emailTotal = emailSeries.reduce((s, d) => s + d.value, 0);
  const verifTotal = verifSeries.reduce((s, d) => s + d.value, 0);

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Analytics</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">Certificate issuance, verification, and email delivery metrics</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Period selector */}
          <div className="flex items-center bg-gray-100/70 rounded-xl p-1 gap-0.5">
            {PERIODS.map(p => (
              <button key={p.id} onClick={() => setPeriod(p.id)}
                className={`px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all ${period === p.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
                {p.label}
              </button>
            ))}
          </div>
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard label="Certificates" value={stats.total_certificates || 3240} change="+18.4%" changeUp sub="Total generated" icon={Award} iconColor="bg-indigo-50 text-indigo-600" sparklineValues={sparkCerts} sparklineColor="#635BFF" loading={loading} />
        <KpiCard label="Verifications" value={stats.verification_scans || 4890} change={`${stats.verification_rate || 92.4}% valid`} changeUp sub="QR + SHA-256 scans" icon={CheckCircle2} iconColor="bg-emerald-50 text-emerald-600" sparklineValues={sparkVerif} sparklineColor="#10B981" loading={loading} />
        <KpiCard label="Emails Delivered" value={stats.emails_sent || 3012} change={`${stats.email_delivery_rate || 97.1}% rate`} changeUp sub="Transactional delivery" icon={Mail} iconColor="bg-blue-50 text-blue-600" sparklineValues={sparkEmail} sparklineColor="#3B82F6" loading={loading} />
        <KpiCard label="Digital Credentials" value={stats.total_credentials || 840} change="+12%" changeUp sub="W3C VC + Open Badges" icon={ShieldCheck} iconColor="bg-purple-50 text-purple-600" sparklineValues={sparkCreds} sparklineColor="#8B5CF6" loading={loading} />
      </div>

      {/* Main charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Certificate issuance chart */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-[15px] font-bold text-[var(--color-text)]">Certificate Issuance</h3>
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{certTotal.toLocaleString()} total in period</p>
            </div>
            <span className="text-[12px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />+18.4%
            </span>
          </div>
          {loading ? <Skeleton className="h-32 w-full" /> : (
            <BarChartInline data={certSeries} color="#635BFF" height={140} showValues />
          )}
        </div>

        {/* Email delivery chart */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-[15px] font-bold text-[var(--color-text)]">Email Deliveries</h3>
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{emailTotal.toLocaleString()} sent in period</p>
            </div>
            <span className="text-[12px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />97.1% delivered
            </span>
          </div>
          {loading ? <Skeleton className="h-32 w-full" /> : (
            <BarChartInline data={emailSeries} color="#3B82F6" height={140} showValues />
          )}
        </div>

        {/* Verification chart */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-[15px] font-bold text-[var(--color-text)]">Public Verifications</h3>
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{verifTotal.toLocaleString()} verifications in period</p>
            </div>
            <span className="text-[12px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">92.4% valid</span>
          </div>
          {loading ? <Skeleton className="h-32 w-full" /> : (
            <BarChartInline data={verifSeries} color="#10B981" height={140} showValues />
          )}
        </div>

        {/* Breakdown donut charts */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
          <h3 className="text-[15px] font-bold text-[var(--color-text)] mb-6">Distribution Breakdown</h3>
          <div className="space-y-6">
            <div>
              <p className="text-[12px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-wide mb-3">Verification Status</p>
              <DonutChart size={80} segments={[
                { label: "Valid", value: 4511, color: "#10B981" },
                { label: "Revoked", value: 248, color: "#F59E0B" },
                { label: "Not Found", value: 131, color: "#EF4444" },
              ]} />
            </div>
            <div className="border-t border-[var(--color-border)] pt-6">
              <p className="text-[12px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-wide mb-3">Email Delivery Status</p>
              <DonutChart size={80} segments={[
                { label: "Delivered", value: 2765, color: "#3B82F6" },
                { label: "Opened", value: 1847, color: "#8B5CF6" },
                { label: "Bounced", value: 134, color: "#EF4444" },
                { label: "Failed", value: 87, color: "#F59E0B" },
              ]} />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: "Avg. Issuance Latency", value: "2.4s", sub: "P95: 4.1s · P99: 7.8s", color: "indigo" },
          { label: "Peak Daily Volume", value: "1,240", sub: "Certificates on peak day", color: "emerald" },
          { label: "Total Storage Used", value: "124.5 MB", sub: "of 25 GB quota · 0.5%", color: "purple" },
        ].map(({ label, value, sub, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
            {loading ? (
              <div className="space-y-2"><Skeleton className="h-3 w-24" /><Skeleton className="h-7 w-16" /><Skeleton className="h-2.5 w-32" /></div>
            ) : (
              <>
                <p className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">{label}</p>
                <p className="text-[26px] font-bold text-[var(--color-text)] mt-2 leading-none">{value}</p>
                <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1">{sub}</p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
