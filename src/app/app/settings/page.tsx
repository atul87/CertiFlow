"use client";

import { useState, useEffect, useCallback } from "react";
import {
  User,
  Building2,
  Globe,
  Bell,
  Shield,
  Palette,
  Trash2,
  Save,
  RefreshCw,
  Camera,
  CheckCircle2,
  Eye,
  EyeOff,
  Copy,
  AlertTriangle,
  Lock,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

type SettingsTab = "profile" | "organization" | "notifications" | "security" | "appearance" | "danger";

const TABS: { id: SettingsTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "profile", label: "Profile", icon: User },
  { id: "organization", label: "Organization", icon: Building2 },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "security", label: "Security", icon: Shield },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "danger", label: "Danger Zone", icon: AlertTriangle },
];

// ─── Save toast ───────────────────────────────────────────────────────────────
function SaveToast({ show }: { show: boolean }) {
  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 bg-gray-900 text-white text-[13px] font-semibold px-4 py-3 rounded-2xl shadow-xl transition-all duration-300 ${show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"}`}>
      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
      Settings saved successfully
    </div>
  );
}

// ─── Section wrapper ──────────────────────────────────────────────────────────
function Section({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
      <div className="px-6 py-4 border-b border-[var(--color-border)]">
        <h3 className="text-[15px] font-bold text-[var(--color-text)]">{title}</h3>
        {description && <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{description}</p>}
      </div>
      <div className="px-6 py-5">{children}</div>
    </div>
  );
}

// ─── Text input ───────────────────────────────────────────────────────────────
function Field({ label, value, onChange, type = "text", placeholder = "", hint = "" }: {
  label: string; value: string; onChange: (v: string) => void;
  type?: string; placeholder?: string; hint?: string;
}) {
  return (
    <div>
      <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
      />
      {hint && <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1.5">{hint}</p>}
    </div>
  );
}

// ─── Toggle ───────────────────────────────────────────────────────────────────
function Toggle({ label, description, checked, onChange }: {
  label: string; description?: string; checked: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3.5 border-b border-[var(--color-border)] last:border-0">
      <div>
        <p className="text-[13px] font-semibold text-[var(--color-text)]">{label}</p>
        {description && <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        role="switch"
        aria-checked={checked}
        className={`relative w-11 h-6 rounded-full transition-colors shrink-0 mt-0.5 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30 ${checked ? "bg-[var(--color-primary)]" : "bg-gray-200"}`}
      >
        <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${checked ? "translate-x-5" : "translate-x-0"}`} />
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
export default function SettingsPage() {
  const [tab, setTab] = useState<SettingsTab>("profile");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  // Profile state
  const [profile, setProfile] = useState({
    name: "Atul Kumar",
    email: "atul@certiflow.io",
    phone: "+91 98765 43210",
    location: "Bengaluru, India",
    bio: "Founder at CertiFlow. Building digital credential infrastructure.",
    avatar_url: "",
  });

  // Organization state
  const [org, setOrg] = useState({
    name: "CertiFlow Inc.",
    slug: "certiflow",
    website: "https://certiflow.io",
    description: "Digital certificate and credential issuance platform.",
    contact_email: "hello@certiflow.io",
    logo_url: "",
    domain: "certiflow.io",
  });

  // Notification prefs
  const [notifPrefs, setNotifPrefs] = useState({
    job_completed: true,
    job_failed: true,
    certificate_verified: false,
    email_bounced: true,
    quota_warning: true,
    team_joined: true,
    webhook_failed: true,
    new_invoice: false,
    product_updates: true,
    security_alerts: true,
  });

  // Security
  const [passwords, setPasswords] = useState({ current: "", new: "", confirm: "" });
  const [sessions] = useState([
    { id: "s1", device: "Chrome · macOS", ip: "103.x.x.x", location: "Bengaluru, IN", last_active: "2026-09-29T17:55:00.000Z", current: true },
    { id: "s2", device: "Safari · iOS 17", ip: "14.x.x.x", location: "Mumbai, IN", last_active: "2026-09-27T10:00:00.000Z", current: false },
  ]);

  // Appearance
  const [appearance, setAppearance] = useState({
    theme: "light" as "light" | "dark" | "system",
    density: "normal" as "compact" | "normal" | "comfortable",
    date_format: "MMM D, YYYY",
    timezone: "Asia/Kolkata",
  });

  useEffect(() => {
    setLoading(true);
    setTimeout(() => setLoading(false), 400);
  }, []);

  const save = useCallback(async () => {
    setSaving(true);
    await new Promise(r => setTimeout(r, 600));
    setSaving(false);
    setShowSaved(true);
    setTimeout(() => setShowSaved(false), 3000);
  }, []);

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 60) return "just now";
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  return (
    <div className="flex h-full">
      {/* ── Left nav ──────────────────────────────────────────────── */}
      <div className="w-52 shrink-0 border-r border-[var(--color-border)] bg-gray-50/50 p-4 hidden md:block">
        <p className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-3 px-2">Settings</p>
        <nav className="space-y-0.5">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm border border-[var(--color-border)]" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-white"} ${t.id === "danger" ? "text-red-500 hover:text-red-600 mt-4" : ""}`}>
              <t.icon className={`w-4 h-4 shrink-0 ${t.id === "danger" ? "text-red-400" : ""}`} />
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Mobile tab bar */}
      <div className="md:hidden border-b border-[var(--color-border)] overflow-x-auto flex items-center gap-1 p-2 bg-gray-50/50 absolute top-0 left-0 right-0">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-semibold shrink-0 transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)]"}`}>
            <t.icon className="w-3.5 h-3.5" />{t.label}
          </button>
        ))}
      </div>

      {/* ── Content ───────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-5 max-w-2xl">

        {/* ── Profile ── */}
        {tab === "profile" && (
          <>
            <Section title="Profile" description="Your personal details visible to teammates">
              <div className="space-y-4">
                {/* Avatar */}
                <div className="flex items-center gap-4 mb-5">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-2xl font-bold shrink-0">
                    {profile.name[0]}
                  </div>
                  <div>
                    <button className="flex items-center gap-1.5 text-[13px] font-semibold text-[var(--color-primary)] hover:underline">
                      <Camera className="w-3.5 h-3.5" />Upload photo
                    </button>
                    <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">JPG or PNG, max 2 MB</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Field label="Full Name" value={profile.name} onChange={v => setProfile(p => ({ ...p, name: v }))} />
                  <Field label="Email Address" value={profile.email} onChange={v => setProfile(p => ({ ...p, email: v }))} type="email" />
                  <Field label="Phone" value={profile.phone} onChange={v => setProfile(p => ({ ...p, phone: v }))} placeholder="+1 (555) 000-0000" />
                  <Field label="Location" value={profile.location} onChange={v => setProfile(p => ({ ...p, location: v }))} placeholder="City, Country" />
                </div>
                <div>
                  <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Bio</label>
                  <textarea rows={3} value={profile.bio} onChange={e => setProfile(p => ({ ...p, bio: e.target.value }))}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors resize-none" />
                </div>
                <Button onClick={save} loading={saving} className="w-full sm:w-auto justify-center">
                  <Save className="w-3.5 h-3.5 mr-1.5" />Save Profile
                </Button>
              </div>
            </Section>
          </>
        )}

        {/* ── Organization ── */}
        {tab === "organization" && (
          <>
            <Section title="Organization Details" description="Settings visible to your entire organization">
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Field label="Organization Name" value={org.name} onChange={v => setOrg(p => ({ ...p, name: v }))} />
                  <Field label="Slug" value={org.slug} onChange={v => setOrg(p => ({ ...p, slug: v }))} hint={`certiflow.io/org/${org.slug}`} />
                  <Field label="Website" value={org.website} onChange={v => setOrg(p => ({ ...p, website: v }))} type="url" />
                  <Field label="Contact Email" value={org.contact_email} onChange={v => setOrg(p => ({ ...p, contact_email: v }))} type="email" />
                </div>
                <div>
                  <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Description</label>
                  <textarea rows={2} value={org.description} onChange={e => setOrg(p => ({ ...p, description: e.target.value }))}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors resize-none" />
                </div>
                <Button onClick={save} loading={saving} className="w-full sm:w-auto justify-center">
                  <Save className="w-3.5 h-3.5 mr-1.5" />Save Organization
                </Button>
              </div>
            </Section>

            <Section title="Custom Domain" description="Serve public certificate pages on your own domain">
              <div className="space-y-3">
                <Field label="Domain" value={org.domain} onChange={v => setOrg(p => ({ ...p, domain: v }))} placeholder="certs.yourdomain.com" />
                <div className="bg-gray-50 rounded-xl border border-[var(--color-border)] p-3 text-[12px] space-y-1.5">
                  <p className="font-bold text-[var(--color-text)]">DNS Configuration</p>
                  <div className="flex items-center justify-between gap-4">
                    <code className="font-mono text-emerald-700 text-[11px]">CNAME certs.yourdomain.com → verify.certiflow.io</code>
                    <button className="text-gray-400 hover:text-gray-700 shrink-0"><Copy className="w-3.5 h-3.5" /></button>
                  </div>
                </div>
                <button className="flex items-center gap-1.5 text-[12px] font-semibold text-[var(--color-primary)] hover:underline">
                  View SSL status <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            </Section>
          </>
        )}

        {/* ── Notifications ── */}
        {tab === "notifications" && (
          <>
            <Section title="Email Notifications" description="Choose which events send you an email">
              <div className="divide-y divide-[var(--color-border)]">
                {[
                  { key: "job_completed", label: "Job completed", desc: "When a bulk issuance job finishes" },
                  { key: "job_failed", label: "Job failed", desc: "When a job fails or has errors" },
                  { key: "certificate_verified", label: "Certificate verified", desc: "Each time someone verifies your certificate" },
                  { key: "email_bounced", label: "Email bounced", desc: "When a delivery bounces or fails" },
                  { key: "quota_warning", label: "Quota warning", desc: "When usage exceeds 80% of your plan limit" },
                  { key: "team_joined", label: "Team member joined", desc: "When an invitation is accepted" },
                  { key: "webhook_failed", label: "Webhook failure", desc: "When a webhook delivery fails multiple times" },
                  { key: "new_invoice", label: "New invoice", desc: "Monthly billing invoice ready" },
                ].map(({ key, label, desc }) => (
                  <Toggle key={key} label={label} description={desc}
                    checked={(notifPrefs as any)[key]}
                    onChange={v => setNotifPrefs(p => ({ ...p, [key]: v }))} />
                ))}
              </div>
            </Section>

            <Section title="Product & Security" description="Important platform announcements">
              <div>
                {[
                  { key: "product_updates", label: "Product updates", desc: "New features and improvements" },
                  { key: "security_alerts", label: "Security alerts", desc: "Suspicious login and API activity (recommended)" },
                ].map(({ key, label, desc }) => (
                  <Toggle key={key} label={label} description={desc}
                    checked={(notifPrefs as any)[key]}
                    onChange={v => setNotifPrefs(p => ({ ...p, [key]: v }))} />
                ))}
              </div>
            </Section>

            <Button onClick={save} loading={saving} className="w-full sm:w-auto justify-center">
              <Save className="w-3.5 h-3.5 mr-1.5" />Save Preferences
            </Button>
          </>
        )}

        {/* ── Security ── */}
        {tab === "security" && (
          <>
            <Section title="Change Password" description="Use a strong, unique password">
              <div className="space-y-3">
                {[
                  { key: "current", label: "Current Password", show: showCurrentPw, toggle: () => setShowCurrentPw(o => !o) },
                  { key: "new", label: "New Password", show: showNewPw, toggle: () => setShowNewPw(o => !o) },
                  { key: "confirm", label: "Confirm New Password", show: showNewPw, toggle: () => setShowNewPw(o => !o) },
                ].map(({ key, label, show, toggle }) => (
                  <div key={key}>
                    <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">{label}</label>
                    <div className="relative">
                      <input type={show ? "text" : "password"} value={(passwords as any)[key]}
                        onChange={e => setPasswords(p => ({ ...p, [key]: e.target.value }))}
                        className="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
                        placeholder="••••••••" />
                      <button type="button" onClick={toggle} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700">
                        {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                ))}
                <div className="pt-1">
                  <Button onClick={save} loading={saving} disabled={!passwords.new || passwords.new !== passwords.confirm} className="w-full sm:w-auto justify-center">
                    <Lock className="w-3.5 h-3.5 mr-1.5" />Update Password
                  </Button>
                </div>
              </div>
            </Section>

            <Section title="Two-Factor Authentication" description="Add an extra layer of security to your account">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[13px] font-semibold text-[var(--color-text)]">Authenticator App</p>
                  <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Use Google Authenticator or 1Password to generate codes</p>
                </div>
                <button className="px-3.5 py-2 rounded-xl bg-[var(--color-primary)] text-white text-[13px] font-semibold hover:bg-[var(--color-primary-dark)] transition-colors">
                  Enable 2FA
                </button>
              </div>
            </Section>

            <Section title="Active Sessions" description="Manage devices where you're logged in">
              <div className="space-y-3">
                {sessions.map(s => (
                  <div key={s.id} className="flex items-center justify-between gap-4 p-3 rounded-xl border border-[var(--color-border)] hover:bg-gray-50/50">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-[13px] font-semibold text-[var(--color-text)]">{s.device}</p>
                        {s.current && <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full">CURRENT</span>}
                      </div>
                      <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5" suppressHydrationWarning>{s.ip} · {s.location} · {relTime(s.last_active)}</p>
                    </div>
                    {!s.current && (
                      <button className="text-[12px] font-semibold text-red-600 hover:underline shrink-0">Revoke</button>
                    )}
                  </div>
                ))}
                <button className="text-[13px] font-semibold text-red-600 hover:underline">Sign out all other sessions</button>
              </div>
            </Section>
          </>
        )}

        {/* ── Appearance ── */}
        {tab === "appearance" && (
          <>
            <Section title="Theme">
              <div className="grid grid-cols-3 gap-3">
                {(["light", "dark", "system"] as const).map(t => (
                  <button key={t} onClick={() => setAppearance(p => ({ ...p, theme: t }))}
                    className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${appearance.theme === t ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)]" : "border-[var(--color-border)] hover:border-[var(--color-border-hover)]"}`}>
                    <div className={`w-10 h-7 rounded-lg border border-gray-200 ${t === "dark" ? "bg-gray-900" : t === "system" ? "bg-gradient-to-r from-white to-gray-900" : "bg-white"}`} />
                    <span className="text-[12px] font-semibold capitalize text-[var(--color-text)]">{t}</span>
                  </button>
                ))}
              </div>
            </Section>

            <Section title="Density" description="Control how compact the interface feels">
              <div className="grid grid-cols-3 gap-3">
                {(["compact", "normal", "comfortable"] as const).map(d => (
                  <button key={d} onClick={() => setAppearance(p => ({ ...p, density: d }))}
                    className={`px-4 py-3 rounded-xl border-2 text-[12px] font-semibold capitalize transition-all ${appearance.density === d ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] text-[var(--color-primary)]" : "border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-hover)]"}`}>
                    {d}
                  </button>
                ))}
              </div>
            </Section>

            <Section title="Date Format & Timezone">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Date Format</label>
                  <select value={appearance.date_format} onChange={e => setAppearance(p => ({ ...p, date_format: e.target.value }))}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors appearance-none">
                    {["MMM D, YYYY", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"].map(f => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Timezone</label>
                  <select value={appearance.timezone} onChange={e => setAppearance(p => ({ ...p, timezone: e.target.value }))}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors appearance-none">
                    {["Asia/Kolkata", "America/New_York", "America/Los_Angeles", "Europe/London", "UTC"].map(tz => (
                      <option key={tz} value={tz}>{tz}</option>
                    ))}
                  </select>
                </div>
              </div>
            </Section>

            <Button onClick={save} loading={saving} className="w-full sm:w-auto justify-center">
              <Save className="w-3.5 h-3.5 mr-1.5" />Save Appearance
            </Button>
          </>
        )}

        {/* ── Danger Zone ── */}
        {tab === "danger" && (
          <div className="space-y-4">
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
              <div className="flex items-start gap-3 mb-4">
                <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-[15px] font-bold text-red-800">Danger Zone</h3>
                  <p className="text-[13px] text-red-600 mt-0.5">Actions in this section are permanent and cannot be undone.</p>
                </div>
              </div>

              <div className="space-y-4">
                {[
                  {
                    title: "Export Data",
                    desc: "Download a full export of your organization data including certificates, templates, and settings.",
                    action: "Export All Data",
                    variant: "secondary" as const,
                    handler: () => alert("Data export initiated. You'll receive an email when ready."),
                  },
                  {
                    title: "Transfer Ownership",
                    desc: "Transfer your organization to another member. You will lose owner privileges.",
                    action: "Transfer Ownership",
                    variant: "secondary" as const,
                    handler: () => alert("Please select the new owner from the Team page."),
                  },
                  {
                    title: "Delete Organization",
                    desc: "Permanently delete your organization, all certificates, templates, and data. This cannot be undone.",
                    action: "Delete Organization",
                    variant: "danger" as const,
                    handler: () => {
                      if (confirm("Are you absolutely sure? Type DELETE to confirm.")) {
                        alert("Organization deletion request submitted.");
                      }
                    },
                  },
                ].map(({ title, desc, action, variant, handler }) => (
                  <div key={title} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-4 border-t border-red-200 first:border-0 first:pt-0">
                    <div>
                      <p className="text-[13px] font-bold text-red-800">{title}</p>
                      <p className="text-[12px] text-red-600 mt-0.5 max-w-sm">{desc}</p>
                    </div>
                    <button
                      onClick={handler}
                      className={`shrink-0 px-4 py-2 rounded-xl text-[13px] font-bold border transition-all ${variant === "danger" ? "bg-red-600 text-white border-red-600 hover:bg-red-700" : "bg-white text-red-600 border-red-300 hover:bg-red-50"}`}>
                      {action}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <SaveToast show={showSaved} />
    </div>
  );
}
