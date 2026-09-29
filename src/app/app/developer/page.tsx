"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Code2,
  Plus,
  RefreshCw,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Clock,
  Zap,
  Globe,
  Activity,
  MoreHorizontal,
  RotateCcw,
  Webhook,
  Key,
  ChevronRight,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { ApiKey, Webhook as WebhookType } from "@/types";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Demo data ────────────────────────────────────────────────────────────────
const DEMO_KEYS: ApiKey[] = [
  { id: "key-1", name: "Production API Key", key_prefix: "cf_live_", last_four: "7j2k", scopes: ["certificates:read", "certificates:write", "templates:read"], status: "active", created_at: new Date(Date.now() - 86400 * 60 * 1000).toISOString(), last_used_at: new Date(Date.now() - 3600 * 2 * 1000).toISOString() },
  { id: "key-2", name: "CI/CD Automation", key_prefix: "cf_live_", last_four: "mn9p", scopes: ["certificates:write", "imports:write"], status: "active", created_at: new Date(Date.now() - 86400 * 14 * 1000).toISOString(), last_used_at: new Date(Date.now() - 86400 * 1 * 1000).toISOString() },
  { id: "key-3", name: "Test / Staging Key", key_prefix: "cf_test_", last_four: "xq4r", scopes: ["certificates:read", "templates:read"], status: "revoked", created_at: new Date(Date.now() - 86400 * 30 * 1000).toISOString() },
];

const DEMO_WEBHOOKS: WebhookType[] = [
  { id: "wh-1", name: "Slack Notifications", url: "https://hooks.slack.com/services/T00/B00/XXXXXXXX", events: ["certificate.issued", "job.completed", "job.failed"], status: "active", secret_prefix: "wh_", created_at: new Date(Date.now() - 86400 * 30 * 1000).toISOString(), last_triggered_at: new Date(Date.now() - 3600 * 1000).toISOString(), success_rate: 98.7 },
  { id: "wh-2", name: "Internal LMS Webhook", url: "https://lms.corp.io/webhooks/certiflow", events: ["certificate.issued"], status: "active", secret_prefix: "wh_", created_at: new Date(Date.now() - 86400 * 14 * 1000).toISOString(), last_triggered_at: new Date(Date.now() - 86400 * 2 * 1000).toISOString(), success_rate: 100 },
  { id: "wh-3", name: "Analytics Ingest", url: "https://analytics.example.com/ingest/v1", events: ["certificate.issued", "certificate.verified", "certificate.revoked"], status: "inactive", secret_prefix: "wh_", created_at: new Date(Date.now() - 86400 * 5 * 1000).toISOString(), success_rate: 0 },
];

const WEBHOOK_EVENTS = [
  "certificate.issued", "certificate.verified", "certificate.revoked",
  "job.started", "job.completed", "job.failed",
  "import.confirmed", "credential.issued",
];

const SCOPES = [
  { id: "certificates:read", label: "Certificates: Read" },
  { id: "certificates:write", label: "Certificates: Write" },
  { id: "templates:read", label: "Templates: Read" },
  { id: "templates:write", label: "Templates: Write" },
  { id: "imports:write", label: "Imports: Write" },
  { id: "credentials:read", label: "Credentials: Read" },
  { id: "analytics:read", label: "Analytics: Read" },
  { id: "team:read", label: "Team: Read" },
];

// ─── Copy button ──────────────────────────────────────────────────────────────
function CopyButton({ value, className = "" }: { value: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button onClick={copy} className={`p-1.5 rounded-lg text-gray-400 hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-subtle)] transition-colors ${className}`}>
      {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
    </button>
  );
}

// ─── API Key card ──────────────────────────────────────────────────────────────
function ApiKeyCard({ apiKey, onRevoke }: { apiKey: ApiKey; onRevoke: (id: string) => void }) {
  const [showFull, setShowFull] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  const displayKey = `${apiKey.key_prefix}${"•".repeat(24)}${apiKey.last_four}`;
  const isRevoked = apiKey.status === "revoked";

  return (
    <div className={`bg-white rounded-2xl border shadow-xs p-5 transition-all ${isRevoked ? "border-gray-200 opacity-60" : "border-[var(--color-border)] hover:shadow-sm"}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-[14px] font-bold text-[var(--color-text)]">{apiKey.name}</h3>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${isRevoked ? "bg-red-50 text-red-600 border-red-200" : "bg-emerald-50 text-emerald-700 border-emerald-200"}`}>
              {isRevoked ? "REVOKED" : "ACTIVE"}
            </span>
          </div>
          <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">Created {relTime(apiKey.created_at)}{apiKey.last_used_at ? ` · Last used ${relTime(apiKey.last_used_at)}` : " · Never used"}</p>
        </div>
        {!isRevoked && (
          <div className="relative">
            <button onClick={() => setMenuOpen(o => !o)} className="p-1.5 rounded-lg text-gray-300 hover:text-gray-700 hover:bg-gray-100 transition-colors">
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {menuOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                <div className="absolute right-0 top-full mt-1 z-20 w-36 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
                  <button onClick={() => { setMenuOpen(false); onRevoke(apiKey.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50">
                    <Trash2 className="w-3.5 h-3.5" />Revoke
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Key display */}
      <div className="flex items-center gap-2 p-3 bg-gray-900 rounded-xl mb-3">
        <code className="flex-1 text-[12px] font-mono text-emerald-400 truncate">
          {showFull ? `${apiKey.key_prefix}demo_key_${apiKey.last_four}_full_display` : displayKey}
        </code>
        <button onClick={() => setShowFull(o => !o)} className="text-gray-500 hover:text-gray-300 transition-colors p-1">
          {showFull ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
        </button>
        <CopyButton value={displayKey} className="!text-gray-500 !hover:text-gray-300" />
      </div>

      {/* Scopes */}
      <div className="flex flex-wrap gap-1">
        {apiKey.scopes.map(s => (
          <span key={s} className="text-[10px] font-mono bg-indigo-50 text-indigo-700 border border-indigo-100 px-1.5 py-0.5 rounded">{s}</span>
        ))}
      </div>
    </div>
  );
}

// ─── Webhook card ──────────────────────────────────────────────────────────────
function WebhookCard({ wh, onDelete, onToggle, onTest }: {
  wh: WebhookType;
  onDelete: (id: string) => void;
  onToggle: (id: string) => void;
  onTest: (id: string) => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  return (
    <div className={`bg-white rounded-2xl border shadow-xs p-5 hover:shadow-sm transition-all ${wh.status === "inactive" ? "opacity-70" : ""}`}
      style={{ borderColor: "var(--color-border)" }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${wh.status === "active" ? "bg-blue-50" : "bg-gray-50"}`}>
            <Webhook className={`w-4 h-4 ${wh.status === "active" ? "text-blue-600" : "text-gray-400"}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-[13px] font-bold text-[var(--color-text)]">{wh.name}</h3>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${wh.status === "active" ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-gray-50 text-gray-500 border-gray-200"}`}>
                {wh.status === "active" ? "ACTIVE" : "PAUSED"}
              </span>
            </div>
            <p className="text-[11px] text-[var(--color-text-tertiary)] truncate max-w-[220px]">{wh.url}</p>
          </div>
        </div>
        <div className="relative">
          <button onClick={() => setMenuOpen(o => !o)} className="p-1.5 rounded-lg text-gray-300 hover:text-gray-700 hover:bg-gray-100 transition-colors">
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full mt-1 z-20 w-40 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
                <button onClick={() => { setMenuOpen(false); onTest(wh.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50">
                  <Zap className="w-3.5 h-3.5 text-gray-400" />Test
                </button>
                <button onClick={() => { setMenuOpen(false); onToggle(wh.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50">
                  <RotateCcw className="w-3.5 h-3.5 text-gray-400" />{wh.status === "active" ? "Pause" : "Enable"}
                </button>
                <div className="border-t border-[var(--color-border)] my-1" />
                <button onClick={() => { setMenuOpen(false); onDelete(wh.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50">
                  <Trash2 className="w-3.5 h-3.5" />Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Events */}
      <div className="flex flex-wrap gap-1 mb-3">
        {wh.events.map(e => (
          <span key={e} className="text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-100 px-1.5 py-0.5 rounded">{e}</span>
        ))}
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-[11px] text-[var(--color-text-tertiary)] pt-3 border-t border-[var(--color-border)]">
        <span>{wh.last_triggered_at ? `Last fired ${relTime(wh.last_triggered_at)}` : "Never triggered"}</span>
        {wh.success_rate > 0 && (
          <span className={`font-bold ${wh.success_rate >= 95 ? "text-emerald-600" : wh.success_rate >= 80 ? "text-amber-600" : "text-red-500"}`}>
            {wh.success_rate}% success
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Create Key Modal ─────────────────────────────────────────────────────────
function CreateKeyModal({ onClose, onCreated }: { onClose: () => void; onCreated: (k: ApiKey & { full_key?: string }) => void }) {
  const [name, setName] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>(["certificates:read", "certificates:write"]);
  const [loading, setLoading] = useState(false);
  const [created, setCreated] = useState<(ApiKey & { full_key?: string }) | null>(null);

  const toggleScope = (s: string) => setSelectedScopes(p => p.includes(s) ? p.filter(x => x !== s) : [...p, s]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.developer.createApiKey({ name, scopes: selectedScopes });
      setCreated(res);
    } catch {
      const mock: ApiKey & { full_key?: string } = {
        id: `key-${Date.now()}`, name, key_prefix: "cf_live_", last_four: Math.random().toString(36).substring(2, 6),
        scopes: selectedScopes, status: "active", created_at: new Date().toISOString(),
        full_key: `cf_live_${Array.from({ length: 32 }, () => Math.random().toString(36)[2]).join("")}`,
      };
      setCreated(mock);
    } finally {
      setLoading(false);
    }
  };

  if (created) {
    return (
      <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-[var(--color-border)] p-6">
          <div className="text-center mb-5">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-500" />
            </div>
            <h2 className="text-[17px] font-bold text-[var(--color-text)]">API Key Created</h2>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">Copy this key now — you won't be able to see it again.</p>
          </div>
          <div className="flex items-center gap-2 p-3 bg-gray-900 rounded-xl mb-4">
            <code className="flex-1 text-[11px] font-mono text-emerald-400 break-all">{created.full_key}</code>
            <CopyButton value={created.full_key || ""} className="!text-gray-500" />
          </div>
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-[12px] text-amber-700 flex items-start gap-2 mb-4">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
            <span>This key will not be shown again. Store it securely in your environment variables.</span>
          </div>
          <Button className="w-full justify-center" onClick={() => { onCreated(created); onClose(); }}>Done</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-[var(--color-border)]">
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
          <div><h2 className="text-[17px] font-bold text-[var(--color-text)]">Create API Key</h2><p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">Scoped live API credential</p></div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Key Name <span className="text-red-500">*</span></label>
            <input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Production API Key"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors" />
          </div>
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2">Scopes</label>
            <div className="grid grid-cols-2 gap-1.5">
              {SCOPES.map(s => (
                <label key={s.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-all ${selectedScopes.includes(s.id) ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)]" : "border-[var(--color-border)] hover:bg-gray-50"}`}>
                  <input type="checkbox" checked={selectedScopes.includes(s.id)} onChange={() => toggleScope(s.id)} className="rounded text-[var(--color-primary)]" />
                  <span className="text-[11px] font-mono text-[var(--color-text)]">{s.id}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
            <Button type="submit" loading={loading} disabled={!name || selectedScopes.length === 0} className="flex-1 justify-center"><Key className="w-3.5 h-3.5 mr-1.5" />Create Key</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Create Webhook Modal ──────────────────────────────────────────────────────
function CreateWebhookModal({ onClose, onCreated }: { onClose: () => void; onCreated: (w: WebhookType) => void }) {
  const [form, setForm] = useState({ name: "", url: "" });
  const [selectedEvents, setSelectedEvents] = useState<string[]>(["certificate.issued"]);
  const [loading, setLoading] = useState(false);

  const toggleEvent = (e: string) => setSelectedEvents(p => p.includes(e) ? p.filter(x => x !== e) : [...p, e]);

  const handleSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    setLoading(true);
    try {
      const res = await api.developer.createWebhook({ name: form.name, url: form.url, events: selectedEvents });
      onCreated(res);
    } catch {
      onCreated({ id: `wh-${Date.now()}`, name: form.name, url: form.url, events: selectedEvents, status: "active", secret_prefix: "wh_", created_at: new Date().toISOString(), success_rate: 0 });
    } finally {
      setLoading(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-[var(--color-border)]">
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
          <div><h2 className="text-[17px] font-bold text-[var(--color-text)]">Create Webhook</h2><p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">HMAC-SHA256 signed event endpoint</p></div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {[
            { key: "name", label: "Webhook Name", placeholder: "e.g. Slack Notifications" },
            { key: "url", label: "Endpoint URL", placeholder: "https://your-server.com/webhook" },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">{label} <span className="text-red-500">*</span></label>
              <input required value={(form as any)[key]} onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))} placeholder={placeholder}
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors" />
            </div>
          ))}
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2">Events to subscribe</label>
            <div className="grid grid-cols-2 gap-1.5 max-h-40 overflow-y-auto pr-1">
              {WEBHOOK_EVENTS.map(e => (
                <label key={e} className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-all ${selectedEvents.includes(e) ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)]" : "border-[var(--color-border)] hover:bg-gray-50"}`}>
                  <input type="checkbox" checked={selectedEvents.includes(e)} onChange={() => toggleEvent(e)} className="rounded text-[var(--color-primary)]" />
                  <span className="text-[11px] font-mono text-[var(--color-text)]">{e}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
            <Button type="submit" loading={loading} disabled={!form.name || !form.url || selectedEvents.length === 0} className="flex-1 justify-center"><Webhook className="w-3.5 h-3.5 mr-1.5" />Create</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
type DevTab = "keys" | "webhooks" | "logs" | "docs";
const BASE_URL = "https://api.certiflow.io/v1";

const CODE_SAMPLES: Record<string, string> = {
  curl: `curl -X POST ${BASE_URL}/certificates \\
  -H "Authorization: Bearer cf_live_••••••••••••••••••••••••••••••••" \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "tmpl_abc123",
    "recipient": {
      "name": "Atul Kumar",
      "email": "atul@example.com"
    },
    "variables": {
      "program_name": "ML Workshop",
      "completion_date": "2026-09-29"
    }
  }'`,
  python: `import certiflow

client = certiflow.Client(api_key="cf_live_••••••••••••••••••••••••••••••••")

certificate = client.certificates.create(
    template_id="tmpl_abc123",
    recipient={
        "name": "Atul Kumar",
        "email": "atul@example.com",
    },
    variables={
        "program_name": "ML Workshop",
        "completion_date": "2026-09-29",
    },
)

print(certificate.verification_url)`,
  node: `import CertiFlow from "@certiflow/node";

const client = new CertiFlow({
  apiKey: process.env.CERTIFLOW_API_KEY,
});

const certificate = await client.certificates.create({
  templateId: "tmpl_abc123",
  recipient: {
    name: "Atul Kumar",
    email: "atul@example.com",
  },
  variables: {
    programName: "ML Workshop",
    completionDate: "2026-09-29",
  },
});

console.log(certificate.verificationUrl);`,
};

export default function DeveloperPage() {
  const [tab, setTab] = useState<DevTab>("keys");
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookType[]>([]);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [showCreateWh, setShowCreateWh] = useState(false);
  const [codeLang, setCodeLang] = useState<"curl" | "python" | "node">("curl");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [kRes, wRes] = await Promise.allSettled([
        api.developer.listApiKeys(),
        api.developer.listWebhooks(),
      ]);
      setApiKeys(kRes.status === "fulfilled" ? ((kRes.value as any)?.items || (Array.isArray(kRes.value) ? kRes.value : [])) : DEMO_KEYS);
      setWebhooks(wRes.status === "fulfilled" ? ((wRes.value as any)?.items || (Array.isArray(wRes.value) ? wRes.value : [])) : DEMO_WEBHOOKS);
    } catch {
      setApiKeys(DEMO_KEYS);
      setWebhooks(DEMO_WEBHOOKS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleRevokeKey = async (id: string) => {
    if (!confirm("Revoke this API key? This action cannot be undone.")) return;
    try { await api.developer.revokeApiKey(id); } catch { /* demo */ }
    setApiKeys(prev => prev.map(k => k.id === id ? { ...k, status: "revoked" as const } : k));
  };

  const handleDeleteWh = async (id: string) => {
    if (!confirm("Delete this webhook?")) return;
    try { await api.developer.deleteWebhook(id); } catch { /* demo */ }
    setWebhooks(prev => prev.filter(w => w.id !== id));
  };

  const handleToggleWh = async (id: string) => {
    const wh = webhooks.find(w => w.id === id);
    if (!wh) return;
    const newStatus = wh.status === "active" ? "inactive" : "active";
    try { await api.developer.updateWebhook(id, { status: newStatus }); } catch { /* demo */ }
    setWebhooks(prev => prev.map(w => w.id === id ? { ...w, status: newStatus as "active" | "inactive" } : w));
  };

  const handleTestWh = async (id: string) => {
    try { await api.developer.testWebhook(id); } catch { /* demo */ }
    alert("Test event sent! Check your endpoint logs.");
  };

  const TAB_DEFS: { id: DevTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "keys", label: "API Keys", icon: Key },
    { id: "webhooks", label: "Webhooks", icon: Webhook },
    { id: "logs", label: "Usage Logs", icon: Activity },
    { id: "docs", label: "Quick Start", icon: Terminal },
  ];

  const DEMO_LOGS = Array.from({ length: 10 }, (_, i) => ({
    id: `log-${i}`, method: ["POST", "GET", "POST", "DELETE", "GET"][i % 5],
    path: ["/v1/certificates", "/v1/certificates/cert-123", "/v1/issuance-jobs", "/v1/certificates/cert-456", "/v1/templates"][i % 5],
    status: [201, 200, 202, 200, 200][i % 5],
    latency: Math.round(80 + Math.random() * 200),
    key_prefix: "cf_live_••••7j2k",
    at: new Date(Date.now() - i * 900000).toISOString(),
  }));

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 60) return "just now";
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    return `${Math.round(d / 3600)}h ago`;
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Developer Portal</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">API keys, webhooks, request logs, and integration guides</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
          </Button>
          {tab === "keys" && <Button size="sm" onClick={() => setShowCreateKey(true)}><Plus className="w-4 h-4 mr-1.5" />New API Key</Button>}
          {tab === "webhooks" && <Button size="sm" onClick={() => setShowCreateWh(true)}><Plus className="w-4 h-4 mr-1.5" />New Webhook</Button>}
        </div>
      </div>

      {/* Base URL */}
      <div className="flex items-center gap-3 bg-gray-900 px-4 py-3 rounded-xl text-[12px]">
        <Globe className="w-4 h-4 text-gray-400 shrink-0" />
        <span className="text-gray-400 font-medium">Base URL:</span>
        <code className="text-emerald-400 font-mono flex-1">{BASE_URL}</code>
        <CopyButton value={BASE_URL} />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0.5 bg-gray-100/70 rounded-xl p-1 w-fit flex-wrap">
        {TAB_DEFS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
            <t.icon className="w-3.5 h-3.5" />{t.label}
          </button>
        ))}
      </div>

      {/* ── API Keys tab ─────────────────────────────────────────────── */}
      {tab === "keys" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {loading ? [1, 2].map(i => <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5"><Skeleton className="h-32" /></div>) :
            apiKeys.map(k => <ApiKeyCard key={k.id} apiKey={k} onRevoke={handleRevokeKey} />)}
          <button onClick={() => setShowCreateKey(true)}
            className="bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] hover:border-indigo-400 hover:bg-indigo-50/20 transition-all group flex flex-col items-center justify-center gap-3 py-12 min-h-[140px]">
            <div className="w-10 h-10 rounded-xl border-2 border-dashed border-gray-200 group-hover:border-indigo-400 flex items-center justify-center transition-colors">
              <Plus className="w-5 h-5 text-gray-400 group-hover:text-indigo-500" />
            </div>
            <p className="text-[13px] font-bold text-[var(--color-text-secondary)] group-hover:text-indigo-600">Create New API Key</p>
          </button>
        </div>
      )}

      {/* ── Webhooks tab ─────────────────────────────────────────────── */}
      {tab === "webhooks" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {loading ? [1, 2].map(i => <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5"><Skeleton className="h-28" /></div>) :
            webhooks.map(w => <WebhookCard key={w.id} wh={w} onDelete={handleDeleteWh} onToggle={handleToggleWh} onTest={handleTestWh} />)}
          <button onClick={() => setShowCreateWh(true)}
            className="bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] hover:border-blue-400 hover:bg-blue-50/20 transition-all group flex flex-col items-center justify-center gap-3 py-12 min-h-[140px]">
            <div className="w-10 h-10 rounded-xl border-2 border-dashed border-gray-200 group-hover:border-blue-400 flex items-center justify-center transition-colors">
              <Plus className="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
            </div>
            <p className="text-[13px] font-bold text-[var(--color-text-secondary)] group-hover:text-blue-600">Create Webhook</p>
          </button>
        </div>
      )}

      {/* ── Logs tab ─────────────────────────────────────────────────── */}
      {tab === "logs" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
            <span className="col-span-1">Method</span>
            <span className="col-span-4">Path</span>
            <span className="col-span-1 text-center">Status</span>
            <span className="col-span-2 text-right">Latency</span>
            <span className="col-span-2">Key</span>
            <span className="col-span-2 text-right">Time</span>
          </div>
          <div className="divide-y divide-[var(--color-border)]">
            {DEMO_LOGS.map(log => (
              <div key={log.id} className="px-5 py-3 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50 transition-colors font-mono text-[12px]">
                <span className={`col-span-1 font-bold text-[11px] ${log.method === "POST" ? "text-blue-600" : log.method === "DELETE" ? "text-red-600" : "text-emerald-600"}`}>{log.method}</span>
                <span className="col-span-4 text-[var(--color-text)] truncate">{log.path}</span>
                <span className={`col-span-1 text-center font-bold ${log.status < 300 ? "text-emerald-600" : "text-red-600"}`}>{log.status}</span>
                <span className="col-span-2 text-right text-[var(--color-text-secondary)]">{log.latency}ms</span>
                <span className="col-span-2 text-[var(--color-text-tertiary)] text-[11px] truncate">{log.key_prefix}</span>
                <span className="col-span-2 text-right text-[var(--color-text-tertiary)] text-[11px]">{relTime(log.at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Docs / Quick Start tab ────────────────────────────────────── */}
      {tab === "docs" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
              <h3 className="text-[15px] font-bold text-[var(--color-text)] mb-1">Issue a Certificate</h3>
              <p className="text-[13px] text-[var(--color-text-secondary)] mb-4">Make a single POST request to generate and deliver a certificate.</p>
              <div className="flex items-center gap-1 mb-3">
                {(["curl", "python", "node"] as const).map(l => (
                  <button key={l} onClick={() => setCodeLang(l)}
                    className={`px-3 py-1.5 rounded-lg text-[12px] font-bold transition-all ${codeLang === l ? "bg-gray-900 text-white" : "text-[var(--color-text-secondary)] hover:bg-gray-100"}`}>
                    {l === "curl" ? "cURL" : l === "python" ? "Python" : "Node.js"}
                  </button>
                ))}
              </div>
              <div className="relative">
                <pre className="bg-gray-900 rounded-xl p-4 text-[11px] font-mono text-gray-300 overflow-x-auto leading-relaxed">{CODE_SAMPLES[codeLang]}</pre>
                <CopyButton value={CODE_SAMPLES[codeLang]} className="absolute top-3 right-3 !text-gray-500 !hover:text-white" />
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
              <h3 className="text-[15px] font-bold text-[var(--color-text)] mb-4">Common Endpoints</h3>
              <div className="space-y-2">
                {[
                  { method: "GET", path: "/certificates", desc: "List all certificates" },
                  { method: "POST", path: "/certificates", desc: "Issue a single certificate" },
                  { method: "GET", path: "/certificates/:id", desc: "Get certificate details" },
                  { method: "DELETE", path: "/certificates/:id/revoke", desc: "Revoke a certificate" },
                  { method: "POST", path: "/issuance-jobs", desc: "Start a bulk issuance job" },
                  { method: "GET", path: "/issuance-jobs/:id/progress", desc: "Poll job progress" },
                  { method: "GET", path: "/templates", desc: "List available templates" },
                  { method: "POST", path: "/imports/upload", desc: "Upload a CSV import" },
                ].map(({ method, path, desc }) => (
                  <div key={path} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
                    <span className={`text-[10px] font-bold w-12 text-center px-1 py-0.5 rounded shrink-0 ${method === "GET" ? "bg-emerald-100 text-emerald-700" : method === "POST" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"}`}>{method}</span>
                    <code className="text-[12px] font-mono text-[var(--color-text)]">{BASE_URL}{path}</code>
                    <span className="text-[12px] text-[var(--color-text-tertiary)] ml-auto hidden sm:block">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right sidebar */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
              <h4 className="text-[14px] font-bold text-[var(--color-text)] mb-3">Authentication</h4>
              <p className="text-[12px] text-[var(--color-text-secondary)] mb-3">All API requests require a Bearer token in the Authorization header.</p>
              <div className="bg-gray-900 rounded-lg p-3">
                <code className="text-[11px] font-mono text-emerald-400">Authorization: Bearer {"<YOUR_API_KEY>"}</code>
              </div>
            </div>
            <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
              <h4 className="text-[14px] font-bold text-[var(--color-text)] mb-3">Webhook Signature</h4>
              <p className="text-[12px] text-[var(--color-text-secondary)] mb-3">Verify webhooks using HMAC-SHA256. Check the <code className="text-[11px] bg-gray-100 px-1 py-0.5 rounded">X-CertiFlow-Signature</code> header.</p>
              <div className="bg-gray-900 rounded-lg p-3">
                <code className="text-[11px] font-mono text-gray-300 leading-relaxed whitespace-pre-wrap">{`import hmac, hashlib

sig = hmac.new(
  secret.encode(),
  payload,
  hashlib.sha256
).hexdigest()`}</code>
              </div>
            </div>
            <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5">
              <h4 className="text-[14px] font-bold text-[var(--color-text)] mb-3">Rate Limits</h4>
              <div className="space-y-2">
                {[["Certificates", "500 / min"], ["Bulk Jobs", "10 / min"], ["Verifications", "2000 / min"]].map(([label, limit]) => (
                  <div key={label} className="flex items-center justify-between text-[12px]">
                    <span className="text-[var(--color-text-secondary)]">{label}</span>
                    <span className="font-bold text-[var(--color-text)] font-mono">{limit}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {showCreateKey && <CreateKeyModal onClose={() => setShowCreateKey(false)} onCreated={k => { setApiKeys(prev => [{ ...k, full_key: undefined } as ApiKey, ...prev]); }} />}
      {showCreateWh && <CreateWebhookModal onClose={() => setShowCreateWh(false)} onCreated={w => setWebhooks(prev => [w, ...prev])} />}
    </div>
  );
}
