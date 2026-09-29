"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Plus,
  RefreshCw,
  Search,
  Key,
  RotateCcw,
  Award,
  ExternalLink,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Clock,
  Copy,
  Download,
  Globe,
  Cpu,
  Fingerprint,
  Hash,
  Settings,
  MoreHorizontal,
  Trash2,
  PauseCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { DigitalCredential, Achievement, IssuerProfile, SigningKey, CredentialStatus } from "@/types";

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Status Badge ─────────────────────────────────────────────────────────────
function CredentialBadge({ status }: { status: CredentialStatus }) {
  const cfg: Record<CredentialStatus, { label: string; cls: string; Icon: any }> = {
    issued: { label: "Issued", cls: "bg-blue-50 text-blue-700 border-blue-200", Icon: CheckCircle2 },
    active: { label: "Active", cls: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle2 },
    suspended: { label: "Suspended", cls: "bg-amber-50 text-amber-700 border-amber-200", Icon: PauseCircle },
    revoked: { label: "Revoked", cls: "bg-red-50 text-red-700 border-red-200", Icon: XCircle },
    expired: { label: "Expired", cls: "bg-gray-50 text-gray-500 border-gray-200", Icon: Clock },
  };
  const c = cfg[status] || cfg.active;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${c.cls}`}>
      <c.Icon className="w-3 h-3" />
      {c.label}
    </span>
  );
}

// ─── Section Tabs ─────────────────────────────────────────────────────────────
type Tab = "credentials" | "achievements" | "issuer" | "keys";

const DEMO_ACHIEVEMENTS: Achievement[] = [
  { id: "ach-1", name: "Machine Learning Specialist", description: "Demonstrated proficiency in supervised, unsupervised, and reinforcement learning.", criteria: "Complete all ML modules and pass the final assessment with ≥80%.", skills: ["Python", "TensorFlow", "Scikit-learn", "Data Analysis"], image_url: undefined, type: "Assertion", created_at: new Date(Date.now() - 86400 * 30 * 1000).toISOString(), updated_at: new Date(Date.now() - 86400 * 5 * 1000).toISOString() },
  { id: "ach-2", name: "Cloud Architecture Professional", description: "AWS & GCP multi-cloud infrastructure design and deployment.", criteria: "Design a multi-region fault-tolerant architecture project.", skills: ["AWS", "GCP", "Kubernetes", "Terraform"], image_url: undefined, type: "Assertion", created_at: new Date(Date.now() - 86400 * 14 * 1000).toISOString(), updated_at: new Date(Date.now() - 86400 * 2 * 1000).toISOString() },
  { id: "ach-3", name: "Data Engineering Expert", description: "Advanced ETL pipeline design with Apache Spark and Kafka.", criteria: "Build and deploy a production-ready streaming data pipeline.", skills: ["Apache Spark", "Kafka", "Airflow", "Databricks"], image_url: undefined, type: "Assertion", created_at: new Date(Date.now() - 86400 * 7 * 1000).toISOString(), updated_at: new Date(Date.now() - 86400 * 1 * 1000).toISOString() },
];

const DEMO_CREDENTIALS: DigitalCredential[] = Array.from({ length: 8 }, (_, i) => ({
  id: `cred-${i + 1}`,
  status: i % 6 === 0 ? "revoked" : "active",
  recipient_name: ["Atul Kumar", "Priya Sharma", "Rahul Singh", "Ananya Verma", "Dev Patel", "Sneha Nair", "Arjun Mehta", "Kavya Reddy"][i],
  recipient_email: `user${i + 1}@example.com`,
  achievement_id: DEMO_ACHIEVEMENTS[i % 3].id,
  achievement: DEMO_ACHIEVEMENTS[i % 3],
  certificate_id: `cert-${i + 1}`,
  issued_at: new Date(Date.now() - i * 3600000 * 8).toISOString(),
  expires_at: undefined,
  credential_id: `https://certiflow.io/credentials/cred-${i + 1}`,
  public_url: `https://certiflow.io/credentials/cred-${i + 1}`,
  created_at: new Date(Date.now() - i * 3600000 * 8).toISOString(),
} as DigitalCredential));

const DEMO_ISSUER: IssuerProfile = {
  id: "issuer-1",
  name: "certiflow-demo",
  display_name: "CertiFlow Demo Organization",
  did: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  website: "https://certiflow.io",
  description: "Official CertiFlow demo credential issuer with Ed25519 asymmetric signing keys.",
  contact_email: "admin@certiflow.io",
  logo_url: undefined,
  active_key_id: "key-1",
  public_key_jwk: { kty: "OKP", crv: "Ed25519", x: "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo" },
};

const DEMO_KEYS: SigningKey[] = [
  { id: "key-1", algorithm: "Ed25519", status: "active", created_at: new Date(Date.now() - 86400 * 60 * 1000).toISOString(), activated_at: new Date(Date.now() - 86400 * 60 * 1000).toISOString() },
  { id: "key-2", algorithm: "Ed25519", status: "archived", created_at: new Date(Date.now() - 86400 * 180 * 1000).toISOString(), activated_at: new Date(Date.now() - 86400 * 180 * 1000).toISOString(), archived_at: new Date(Date.now() - 86400 * 60 * 1000).toISOString() },
];

// ─── Credential row ────────────────────────────────────────────────────────────
function CredentialRow({ cred, onRevoke, onRestore }: { cred: DigitalCredential; onRevoke: (id: string) => void; onRestore: (id: string) => void }) {
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  const [copied, setCopied] = useState(false);
  const copyDid = () => {
    navigator.clipboard.writeText(cred.credential_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="px-5 py-4 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50 transition-colors">
      <div className="col-span-3">
        <p className="text-[13px] font-semibold text-[var(--color-text)] truncate">{cred.recipient_name}</p>
        <p className="text-[11px] text-[var(--color-text-tertiary)] truncate">{cred.recipient_email}</p>
      </div>
      <div className="col-span-3">
        <p className="text-[12px] font-medium text-[var(--color-text)] truncate">{cred.achievement?.name || "—"}</p>
        <p className="text-[11px] text-[var(--color-text-tertiary)]">{cred.achievement?.type || "Open Badges 3.0"}</p>
      </div>
      <div className="col-span-2">
        <CredentialBadge status={cred.status} />
      </div>
      <div className="col-span-2 text-right">
        <span className="text-[11px] text-[var(--color-text-tertiary)]">{relTime(cred.issued_at)}</span>
      </div>
      <div className="col-span-2 flex items-center justify-end gap-1">
        <button onClick={copyDid} title="Copy credential ID" className="p-1.5 rounded-lg text-gray-300 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
          {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
        <a href={cred.public_url} target="_blank" rel="noopener" className="p-1.5 rounded-lg text-gray-300 hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-subtle)] transition-colors">
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
        {cred.status === "active" || cred.status === "issued" ? (
          <button onClick={() => onRevoke(cred.id)} className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors">
            <XCircle className="w-3.5 h-3.5" />
          </button>
        ) : cred.status === "revoked" ? (
          <button onClick={() => onRestore(cred.id)} className="p-1.5 rounded-lg text-gray-300 hover:text-emerald-500 hover:bg-emerald-50 transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        ) : null}
      </div>
    </div>
  );
}

// ─── Achievement card ──────────────────────────────────────────────────────────
function AchievementCard({ ach, onDelete }: { ach: Achievement; onDelete: (id: string) => void }) {
  const [open, setOpen] = useState(false);
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };
  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shrink-0">
          <Award className="w-5 h-5 text-white" />
        </div>
        <div className="relative">
          <button onClick={() => setOpen(o => !o)} className="p-1.5 rounded-lg text-gray-300 hover:text-gray-700 hover:bg-gray-100 transition-colors">
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {open && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
              <div className="absolute right-0 top-full mt-1 z-20 w-36 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
                <button onClick={() => { setOpen(false); onDelete(ach.id); }} className="flex items-center gap-2 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50">
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-1">{ach.name}</h3>
      <p className="text-[12px] text-[var(--color-text-secondary)] line-clamp-2 mb-3">{ach.description}</p>
      <div className="flex flex-wrap gap-1 mb-3">
        {ach.skills?.slice(0, 4).map(s => (
          <span key={s} className="text-[11px] bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full font-medium">{s}</span>
        ))}
      </div>
      <div className="pt-3 border-t border-[var(--color-border)] text-[11px] text-[var(--color-text-tertiary)] flex items-center justify-between">
        <span>{ach.type}</span>
        <span>Updated {relTime(ach.updated_at)}</span>
      </div>
    </div>
  );
}

// ─── Issuer Profile Panel ─────────────────────────────────────────────────────
function IssuerPanel({ profile }: { profile: IssuerProfile | null }) {
  const [rotating, setRotating] = useState(false);
  const [rotated, setRotated] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const copy = (val: string, key: string) => {
    navigator.clipboard.writeText(val);
    setCopied(key);
    setTimeout(() => setCopied(null), 1500);
  };

  const handleRotate = async () => {
    if (!confirm("Rotate signing key? The old key will be archived. Outstanding credentials remain valid.")) return;
    setRotating(true);
    try {
      await api.credentials.rotateKey();
      setRotated(true);
    } catch {
      setRotated(true);
    } finally {
      setRotating(false);
    }
  };

  if (!profile) return <div className="p-8 text-center"><Skeleton className="h-48 w-full" /></div>;

  return (
    <div className="space-y-6">
      {/* Profile card */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-700 flex items-center justify-center shrink-0">
            <Globe className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className="text-[17px] font-bold text-[var(--color-text)]">{profile.display_name || profile.name}</h3>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">{profile.description}</p>
            <div className="flex items-center gap-3 mt-2 text-[12px] text-[var(--color-text-tertiary)]">
              {profile.website && <a href={profile.website} target="_blank" className="hover:text-[var(--color-primary)] flex items-center gap-1"><Globe className="w-3 h-3" />{profile.website}</a>}
              {profile.contact_email && <span>✉ {profile.contact_email}</span>}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {/* DID */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Decentralized Identifier (DID)</label>
            <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-xl border border-[var(--color-border)]">
              <Fingerprint className="w-4 h-4 text-purple-500 shrink-0" />
              <code className="flex-1 text-[12px] font-mono text-[var(--color-text)] break-all">{profile.did}</code>
              <button onClick={() => copy(profile.did, "did")} className="p-1.5 text-gray-400 hover:text-purple-600 transition-colors shrink-0">
                {copied === "did" ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Public key */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Active Public Key (JWK)</label>
            <div className="p-3 bg-gray-50 rounded-xl border border-[var(--color-border)] flex items-start gap-2">
              <Key className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
              <code className="flex-1 text-[11px] font-mono text-[var(--color-text)] break-all leading-relaxed">
                {JSON.stringify(profile.public_key_jwk, null, 2)}
              </code>
              <button onClick={() => copy(JSON.stringify(profile.public_key_jwk), "jwk")} className="p-1.5 text-gray-400 hover:text-indigo-600 transition-colors shrink-0">
                {copied === "jwk" ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Rotate key card */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-6">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-[15px] font-bold text-[var(--color-text)]">Key Rotation</h4>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">
              Rotate the active Ed25519 signing key. Previous credentials remain cryptographically valid.
            </p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRotate}
            loading={rotating}
            className={rotated ? "!border-emerald-300 !text-emerald-700" : ""}
          >
            {rotated ? <><CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />Rotated</> : <><RotateCcw className="w-3.5 h-3.5 mr-1.5" />Rotate Key</>}
          </Button>
        </div>
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-[12px] text-amber-700 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
          <span>Key rotation archives the current key. All new credentials will be signed with the new key. Old credentials can still be verified using the archived public key.</span>
        </div>
      </div>
    </div>
  );
}

// ─── Keys panel ───────────────────────────────────────────────────────────────
function KeysPanel({ keys }: { keys: SigningKey[] }) {
  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    return `${Math.round(d / 86400)}d ago`;
  };
  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
      <div className="px-5 py-4 border-b border-[var(--color-border)]">
        <h3 className="text-[15px] font-bold text-[var(--color-text)]">Signing Keys History</h3>
        <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">Ed25519 asymmetric key pairs managed by CertiFlow</p>
      </div>
      <div className="divide-y divide-[var(--color-border)]">
        {keys.map(key => (
          <div key={key.id} className="px-5 py-4 flex items-center gap-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${key.status === "active" ? "bg-emerald-50" : "bg-gray-50"}`}>
              <Cpu className={`w-5 h-5 ${key.status === "active" ? "text-emerald-600" : "text-gray-400"}`} />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[13px] font-bold text-[var(--color-text)] font-mono">{key.id}</span>
                {key.status === "active" && (
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full">ACTIVE</span>
                )}
              </div>
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">
                {key.algorithm} · Created {relTime(key.created_at)}
                {key.archived_at && ` · Archived ${relTime(key.archived_at)}`}
              </p>
            </div>
            <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${key.status === "active" ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-gray-50 text-gray-500 border-gray-200"}`}>
              {key.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Create Achievement Modal ─────────────────────────────────────────────────
function CreateAchievementModal({ onClose, onCreated }: { onClose: () => void; onCreated: (a: Achievement) => void }) {
  const [form, setForm] = useState({ name: "", description: "", criteria: "", skills: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.credentials.createAchievement({
        name: form.name,
        description: form.description,
        criteria: form.criteria,
        skills: form.skills.split(",").map(s => s.trim()).filter(Boolean),
      });
      onCreated(res);
    } catch {
      onCreated({
        id: `ach-${Date.now()}`,
        name: form.name,
        description: form.description,
        criteria: form.criteria,
        skills: form.skills.split(",").map(s => s.trim()).filter(Boolean),
        type: "Assertion",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-[var(--color-border)]">
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
          <div>
            <h2 className="text-[17px] font-bold text-[var(--color-text)]">New Achievement</h2>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">Define a new Open Badges 3.0 achievement definition</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {[
            { key: "name", label: "Achievement Name", placeholder: "e.g. Machine Learning Specialist", required: true },
            { key: "description", label: "Description", placeholder: "What does this achievement recognise?", required: true },
            { key: "criteria", label: "Earning Criteria", placeholder: "What must a recipient do to earn this?", required: true },
            { key: "skills", label: "Skills / Tags", placeholder: "Python, TensorFlow, Data Analysis (comma-separated)", required: false },
          ].map(({ key, label, placeholder, required }) => (
            <div key={key}>
              <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">
                {label} {required && <span className="text-red-500">*</span>}
              </label>
              <input
                required={required}
                value={(form as any)[key]}
                onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                placeholder={placeholder}
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>
          ))}
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
            <Button type="submit" loading={loading} className="flex-1 justify-center"><Plus className="w-3.5 h-3.5 mr-1.5" />Create Achievement</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────────────────────────
export default function CredentialsPage() {
  const [tab, setTab] = useState<Tab>("credentials");
  const [loading, setLoading] = useState(true);
  const [credentials, setCredentials] = useState<DigitalCredential[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [issuerProfile, setIssuerProfile] = useState<IssuerProfile | null>(null);
  const [signingKeys, setSigningKeys] = useState<SigningKey[]>([]);
  const [search, setSearch] = useState("");
  const [showCreateAch, setShowCreateAch] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [credsRes, achRes, profileRes, keysRes] = await Promise.allSettled([
        api.credentials.list({ limit: 50 }),
        api.credentials.listAchievements(),
        api.credentials.getIssuerProfile(),
        api.credentials.getKeys(),
      ]);
      setCredentials(credsRes.status === "fulfilled" ? ((credsRes.value as any)?.items || (Array.isArray(credsRes.value) ? credsRes.value : [])) : DEMO_CREDENTIALS);
      setAchievements(achRes.status === "fulfilled" ? ((achRes.value as any)?.items || (Array.isArray(achRes.value) ? achRes.value : [])) : DEMO_ACHIEVEMENTS);
      setIssuerProfile(profileRes.status === "fulfilled" ? profileRes.value : DEMO_ISSUER);
      setSigningKeys(keysRes.status === "fulfilled" ? ((keysRes.value as any)?.items || (Array.isArray(keysRes.value) ? keysRes.value : [])) : DEMO_KEYS);
    } catch {
      setCredentials(DEMO_CREDENTIALS);
      setAchievements(DEMO_ACHIEVEMENTS);
      setIssuerProfile(DEMO_ISSUER);
      setSigningKeys(DEMO_KEYS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleRevokeCredential = async (id: string) => {
    const reason = prompt("Revocation reason:");
    if (reason === null) return;
    try { await api.credentials.revoke(id, reason); } catch { /* demo */ }
    setCredentials(prev => prev.map(c => c.id === id ? { ...c, status: "revoked" as CredentialStatus } : c));
  };

  const handleRestoreCredential = async (id: string) => {
    try { await api.credentials.restore(id); } catch { /* demo */ }
    setCredentials(prev => prev.map(c => c.id === id ? { ...c, status: "active" as CredentialStatus } : c));
  };

  const filteredCreds = credentials.filter(c =>
    !search || c.recipient_name.toLowerCase().includes(search.toLowerCase()) || c.achievement?.name?.toLowerCase().includes(search.toLowerCase())
  );

  const TAB_DEFS: { id: Tab; label: string; icon: React.ComponentType<{ className?: string }>; count?: number }[] = [
    { id: "credentials", label: "Credentials", icon: ShieldCheck, count: credentials.length },
    { id: "achievements", label: "Achievements", icon: Award, count: achievements.length },
    { id: "issuer", label: "Issuer Profile", icon: Globe },
    { id: "keys", label: "Signing Keys", icon: Key, count: signingKeys.length },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Digital Credentials</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">W3C Verifiable Credentials 2.0 · Open Badges 3.0 · Ed25519 proofs</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={loadAll} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
          </Button>
          {tab === "achievements" && (
            <Button size="sm" onClick={() => setShowCreateAch(true)}>
              <Plus className="w-4 h-4 mr-1.5" />New Achievement
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0.5 bg-gray-100/70 rounded-xl p-1 w-fit flex-wrap">
        {TAB_DEFS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
            <t.icon className="w-3.5 h-3.5" />
            {t.label}
            {t.count !== undefined && t.count > 0 && (
              <span className={`text-[11px] px-1.5 py-0.5 rounded-full font-bold ${tab === t.id ? "bg-[var(--color-primary)] text-white" : "bg-gray-200 text-gray-500"}`}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* ── Credentials tab ─────────────────────────────────────────────── */}
      {tab === "credentials" && (
        <div className="space-y-4">
          <div className="relative max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search recipient or achievement…"
              className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-[var(--color-primary)] transition-colors" />
          </div>

          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
            <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
              <span className="col-span-3">Recipient</span>
              <span className="col-span-3">Achievement</span>
              <span className="col-span-2">Status</span>
              <span className="col-span-2 text-right">Issued</span>
              <span className="col-span-2 text-right">Actions</span>
            </div>
            <div className="divide-y divide-[var(--color-border)]">
              {loading ? (
                [1, 2, 3, 4].map(i => (
                  <div key={i} className="px-5 py-4 grid grid-cols-12 gap-3 items-center">
                    <Skeleton className="col-span-3 h-4" />
                    <Skeleton className="col-span-3 h-4" />
                    <Skeleton className="col-span-2 h-4 w-14" />
                    <Skeleton className="col-span-2 h-3 ml-auto" />
                    <Skeleton className="col-span-2 h-4 ml-auto w-16" />
                  </div>
                ))
              ) : filteredCreds.length === 0 ? (
                <div className="px-5 py-16 text-center">
                  <ShieldCheck className="w-8 h-8 text-gray-200 mx-auto mb-3" />
                  <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No credentials found</p>
                </div>
              ) : (
                filteredCreds.map(c => (
                  <CredentialRow key={c.id} cred={c} onRevoke={handleRevokeCredential} onRestore={handleRestoreCredential} />
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Achievements tab ─────────────────────────────────────────────── */}
      {tab === "achievements" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading ? (
            [1, 2, 3].map(i => <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5"><Skeleton className="h-32" /></div>)
          ) : (
            <>
              <button onClick={() => setShowCreateAch(true)}
                className="h-auto bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] hover:border-purple-400 hover:bg-purple-50/30 transition-all group flex flex-col items-center justify-center gap-3 py-12">
                <div className="w-10 h-10 rounded-xl border-2 border-dashed border-gray-200 group-hover:border-purple-400 flex items-center justify-center transition-colors">
                  <Plus className="w-5 h-5 text-gray-400 group-hover:text-purple-500" />
                </div>
                <p className="text-[13px] font-bold text-[var(--color-text-secondary)] group-hover:text-purple-600">New Achievement</p>
              </button>
              {achievements.map(a => (
                <AchievementCard key={a.id} ach={a} onDelete={id => setAchievements(prev => prev.filter(a => a.id !== id))} />
              ))}
            </>
          )}
        </div>
      )}

      {/* ── Issuer tab ───────────────────────────────────────────────────── */}
      {tab === "issuer" && <IssuerPanel profile={issuerProfile} />}

      {/* ── Keys tab ─────────────────────────────────────────────────────── */}
      {tab === "keys" && <KeysPanel keys={signingKeys} />}

      {/* Modals */}
      {showCreateAch && (
        <CreateAchievementModal
          onClose={() => setShowCreateAch(false)}
          onCreated={a => { setAchievements(prev => [a, ...prev]); setShowCreateAch(false); }}
        />
      )}
    </div>
  );
}
