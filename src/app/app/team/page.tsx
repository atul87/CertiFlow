"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Users,
  Plus,
  RefreshCw,
  Search,
  MoreHorizontal,
  Mail,
  Shield,
  ShieldCheck,
  Eye,
  Trash2,
  Crown,
  Clock,
  CheckCircle2,
  XCircle,
  Send,
  UserPlus,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { Member, Invitation, MemberRole } from "@/types";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Role config ───────────────────────────────────────────────────────────────
const ROLE_CONFIG: Record<MemberRole, { label: string; color: string; bg: string; border: string; Icon: any; description: string }> = {
  owner: { label: "Owner", color: "text-purple-700", bg: "bg-purple-50", border: "border-purple-200", Icon: Crown, description: "Full access + billing" },
  admin: { label: "Admin", color: "text-indigo-700", bg: "bg-indigo-50", border: "border-indigo-200", Icon: ShieldCheck, description: "Manage team + templates" },
  member: { label: "Member", color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", Icon: Shield, description: "Issue certificates" },
  viewer: { label: "Viewer", color: "text-gray-600", bg: "bg-gray-50", border: "border-gray-200", Icon: Eye, description: "Read-only access" },
};

function RoleBadge({ role }: { role: MemberRole }) {
  const c = ROLE_CONFIG[role] || ROLE_CONFIG.viewer;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full border ${c.color} ${c.bg} ${c.border}`}>
      <c.Icon className="w-3 h-3" />
      {c.label}
    </span>
  );
}

// ─── Demo data ────────────────────────────────────────────────────────────────
const DEMO_MEMBERS: Member[] = [
  { id: "m1", user_id: "u1", name: "Atul Kumar", email: "atul@certiflow.io", role: "owner", joined_at: "2026-03-30T10:00:00.000Z", last_active: "2026-09-29T17:50:00.000Z" },
  { id: "m2", user_id: "u2", name: "Priya Sharma", email: "priya@certiflow.io", role: "admin", joined_at: "2026-06-30T10:00:00.000Z", last_active: "2026-09-29T15:55:00.000Z" },
  { id: "m3", user_id: "u3", name: "Rahul Singh", email: "rahul@certiflow.io", role: "member", joined_at: "2026-08-30T10:00:00.000Z", last_active: "2026-09-28T17:00:00.000Z" },
  { id: "m4", user_id: "u4", name: "Ananya Verma", email: "ananya@certiflow.io", role: "member", joined_at: "2026-09-15T10:00:00.000Z", last_active: "2026-09-26T14:30:00.000Z" },
  { id: "m5", user_id: "u5", name: "Dev Patel", email: "dev@certiflow.io", role: "viewer", joined_at: "2026-09-22T10:00:00.000Z" },
];

const DEMO_INVITATIONS: Invitation[] = [
  { id: "inv-1", email: "sneha@corp.io", role: "member", status: "pending", invited_at: "2026-09-27T10:00:00.000Z", expires_at: "2026-10-04T10:00:00.000Z" },
  { id: "inv-2", email: "vikram@example.com", role: "viewer", status: "pending", invited_at: "2026-09-24T10:00:00.000Z", expires_at: "2026-10-01T10:00:00.000Z" },
];

// ─── Member row ───────────────────────────────────────────────────────────────
function MemberRow({ member, isCurrentUser, onRoleChange, onRemove }: {
  member: Member;
  isCurrentUser: boolean;
  onRoleChange: (id: string, role: MemberRole) => void;
  onRemove: (id: string) => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [roleOpen, setRoleOpen] = useState(false);

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 120) return "Just now";
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  return (
    <div className="px-5 py-4 flex items-center gap-4 hover:bg-gray-50/50 transition-colors">
      {/* Avatar */}
      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-[13px] font-bold shrink-0">
        {member.name[0].toUpperCase()}
      </div>

      {/* Name + email */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-[13px] font-semibold text-[var(--color-text)] truncate">{member.name}</p>
          {isCurrentUser && <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-1.5 py-0.5 rounded-full">YOU</span>}
        </div>
        <p className="text-[12px] text-[var(--color-text-tertiary)] truncate">{member.email}</p>
      </div>

      {/* Role (clickable dropdown) */}
      <div className="relative">
        <button
          onClick={() => { if (!isCurrentUser && member.role !== "owner") setRoleOpen(o => !o); }}
          disabled={isCurrentUser || member.role === "owner"}
          className={`flex items-center gap-1.5 ${!isCurrentUser && member.role !== "owner" ? "cursor-pointer hover:opacity-80" : "cursor-default"}`}
        >
          <RoleBadge role={member.role} />
          {!isCurrentUser && member.role !== "owner" && <ChevronDown className="w-3 h-3 text-[var(--color-text-tertiary)]" />}
        </button>
        {roleOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setRoleOpen(false)} />
            <div className="absolute right-0 top-full mt-1 z-20 w-52 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
              {(["admin", "member", "viewer"] as MemberRole[]).map(role => {
                const rc = ROLE_CONFIG[role];
                return (
                  <button key={role} onClick={() => { onRoleChange(member.id, role); setRoleOpen(false); }}
                    className={`w-full flex items-start gap-2.5 px-3.5 py-2.5 hover:bg-gray-50 text-left ${member.role === role ? "bg-[var(--color-primary-subtle)]" : ""}`}>
                    <div className={`w-6 h-6 rounded-lg ${rc.bg} flex items-center justify-center shrink-0 mt-0.5`}>
                      <rc.Icon className={`w-3.5 h-3.5 ${rc.color}`} />
                    </div>
                    <div>
                      <p className="text-[13px] font-semibold text-[var(--color-text)]">{rc.label}</p>
                      <p className="text-[11px] text-[var(--color-text-tertiary)]">{rc.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Last active */}
      <div className="text-right hidden sm:block w-24 shrink-0">
        <p className="text-[11px] text-[var(--color-text-tertiary)]" suppressHydrationWarning>
          {member.last_active ? relTime(member.last_active) : "Never"}
        </p>
        <p className="text-[10px] text-[var(--color-text-tertiary)]" suppressHydrationWarning>Joined {relTime(member.joined_at)}</p>
      </div>

      {/* Actions */}
      {!isCurrentUser && member.role !== "owner" && (
        <div className="relative shrink-0">
          <button onClick={() => setMenuOpen(o => !o)} className="p-1.5 rounded-lg text-gray-300 hover:text-gray-700 hover:bg-gray-100 transition-colors">
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full mt-1 z-20 w-40 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5">
                <button className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50">
                  <Mail className="w-3.5 h-3.5 text-gray-400" />Send Message
                </button>
                <div className="border-t border-[var(--color-border)] my-1" />
                <button onClick={() => { setMenuOpen(false); onRemove(member.id); }}
                  className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50">
                  <Trash2 className="w-3.5 h-3.5" />Remove
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Invite Modal ─────────────────────────────────────────────────────────────
function InviteModal({ onClose, onInvited }: { onClose: () => void; onInvited: (inv: Invitation) => void }) {
  const [emails, setEmails] = useState("");
  const [role, setRole] = useState<MemberRole>("member");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const emailList = emails.split(/[\n,]/).map(e => e.trim()).filter(Boolean);
    for (const email of emailList) {
      try {
        const res = await api.team.invite({ email, role });
        onInvited(res);
      } catch {
        onInvited({ id: `inv-${Date.now()}`, email, role, status: "pending", invited_at: new Date().toISOString(), expires_at: new Date(Date.now() + 86400 * 7 * 1000).toISOString() });
      }
    }
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-[var(--color-border)]">
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
          <div>
            <h2 className="text-[17px] font-bold text-[var(--color-text)]">Invite Team Members</h2>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">Send invitations to join your organization</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 text-[20px] leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">Email Addresses <span className="text-red-500">*</span></label>
            <textarea required rows={3} value={emails} onChange={e => setEmails(e.target.value)}
              placeholder="Enter one or more emails, separated by commas or newlines&#10;e.g. alice@corp.io, bob@example.com"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors resize-none" />
          </div>
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2">Role</label>
            <div className="grid grid-cols-2 gap-2">
              {(["admin", "member", "viewer"] as MemberRole[]).map(r => {
                const rc = ROLE_CONFIG[r];
                return (
                  <button key={r} type="button" onClick={() => setRole(r)}
                    className={`flex items-start gap-2.5 p-3 rounded-xl border text-left transition-all ${role === r ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)]" : "border-[var(--color-border)] hover:bg-gray-50"}`}>
                    <div className={`w-7 h-7 rounded-lg ${rc.bg} flex items-center justify-center shrink-0`}>
                      <rc.Icon className={`w-4 h-4 ${rc.color}`} />
                    </div>
                    <div>
                      <p className="text-[12px] font-bold text-[var(--color-text)]">{rc.label}</p>
                      <p className="text-[11px] text-[var(--color-text-tertiary)]">{rc.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50">Cancel</button>
            <Button type="submit" loading={loading} className="flex-1 justify-center"><Send className="w-3.5 h-3.5 mr-1.5" />Send Invites</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
type TeamTab = "members" | "invitations" | "roles";

export default function TeamPage() {
  const [tab, setTab] = useState<TeamTab>("members");
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState<Member[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [search, setSearch] = useState("");
  const [showInvite, setShowInvite] = useState(false);

  const CURRENT_USER_ID = "u1"; // demo

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [mRes, iRes] = await Promise.allSettled([
        api.team.listMembers(),
        api.team.listInvitations(),
      ]);
      setMembers(mRes.status === "fulfilled" ? ((mRes.value as any)?.items || (Array.isArray(mRes.value) ? mRes.value : [])) : DEMO_MEMBERS);
      setInvitations(iRes.status === "fulfilled" ? ((iRes.value as any)?.items || (Array.isArray(iRes.value) ? iRes.value : [])) : DEMO_INVITATIONS);
    } catch {
      setMembers(DEMO_MEMBERS);
      setInvitations(DEMO_INVITATIONS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleRoleChange = async (id: string, role: MemberRole) => {
    try { await api.team.updateMemberRole(id, role); } catch { /* demo */ }
    setMembers(prev => prev.map(m => m.id === id ? { ...m, role } : m));
  };

  const handleRemove = async (id: string) => {
    if (!confirm("Remove this member from your organization?")) return;
    try { await api.team.removeMember(id); } catch { /* demo */ }
    setMembers(prev => prev.filter(m => m.id !== id));
  };

  const handleCancelInvite = async (id: string) => {
    try { await api.team.cancelInvite(id); } catch { /* demo */ }
    setInvitations(prev => prev.filter(i => i.id !== id));
  };

  const handleResendInvite = async (id: string) => {
    try { await api.team.resendInvite(id); } catch { /* demo */ }
  };

  const filteredMembers = members.filter(m =>
    !search || m.name.toLowerCase().includes(search.toLowerCase()) || m.email.toLowerCase().includes(search.toLowerCase())
  );

  const PERMISSIONS_MATRIX = [
    { action: "Issue certificates", owner: true, admin: true, member: true, viewer: false },
    { action: "Create templates", owner: true, admin: true, member: true, viewer: false },
    { action: "Upload CSV imports", owner: true, admin: true, member: true, viewer: false },
    { action: "Revoke certificates", owner: true, admin: true, member: false, viewer: false },
    { action: "Manage team members", owner: true, admin: true, member: false, viewer: false },
    { action: "Manage API keys", owner: true, admin: true, member: false, viewer: false },
    { action: "Manage webhooks", owner: true, admin: true, member: false, viewer: false },
    { action: "View analytics", owner: true, admin: true, member: true, viewer: true },
    { action: "View certificates", owner: true, admin: true, member: true, viewer: true },
    { action: "Manage billing", owner: true, admin: false, member: false, viewer: false },
    { action: "Delete organization", owner: true, admin: false, member: false, viewer: false },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Team Management</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">Manage members, roles, and pending invitations</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />Refresh
          </Button>
          <Button size="sm" onClick={() => setShowInvite(true)}>
            <UserPlus className="w-4 h-4 mr-1.5" />Invite Members
          </Button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total Members", value: members.length, color: "text-indigo-600", bg: "bg-indigo-50" },
          { label: "Pending Invites", value: invitations.filter(i => i.status === "pending").length, color: "text-amber-600", bg: "bg-amber-50" },
          { label: "Admins & Owners", value: members.filter(m => m.role === "admin" || m.role === "owner").length, color: "text-purple-600", bg: "bg-purple-50" },
        ].map(({ label, value, color, bg }) => (
          <div key={label} className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs p-5 text-center">
            <p className={`text-[28px] font-bold ${color}`}>{value}</p>
            <p className="text-[12px] font-medium text-[var(--color-text-secondary)] mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0.5 bg-gray-100/70 rounded-xl p-1 w-fit">
        {([
          { id: "members" as TeamTab, label: "Members", count: members.length },
          { id: "invitations" as TeamTab, label: "Invitations", count: invitations.filter(i => i.status === "pending").length },
          { id: "roles" as TeamTab, label: "Permissions Matrix" },
        ]).map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${tab === t.id ? "bg-white text-[var(--color-text)] shadow-sm" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"}`}>
            {t.label}
            {t.count !== undefined && t.count > 0 && (
              <span className={`text-[11px] px-1.5 py-0.5 rounded-full font-bold ${tab === t.id ? "bg-[var(--color-primary)] text-white" : "bg-gray-200 text-gray-500"}`}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* ── Members tab ─────────────────────────────────────────────── */}
      {tab === "members" && (
        <div className="space-y-4">
          <div className="relative max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search members…"
              className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-[var(--color-primary)] transition-colors" />
          </div>

          <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
            <div className="divide-y divide-[var(--color-border)]">
              {loading ? (
                [1, 2, 3].map(i => (
                  <div key={i} className="px-5 py-4 flex items-center gap-4">
                    <Skeleton className="w-9 h-9 rounded-full shrink-0" />
                    <div className="flex-1 space-y-1.5"><Skeleton className="h-4 w-40" /><Skeleton className="h-3 w-32" /></div>
                    <Skeleton className="h-5 w-16" />
                  </div>
                ))
              ) : filteredMembers.length === 0 ? (
                <div className="px-5 py-16 text-center"><Users className="w-8 h-8 text-gray-200 mx-auto mb-3" /><p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No members found</p></div>
              ) : (
                filteredMembers.map(m => (
                  <MemberRow key={m.id} member={m} isCurrentUser={m.user_id === CURRENT_USER_ID} onRoleChange={handleRoleChange} onRemove={handleRemove} />
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Invitations tab ──────────────────────────────────────────── */}
      {tab === "invitations" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
          {invitations.length === 0 ? (
            <div className="px-5 py-16 text-center">
              <Mail className="w-8 h-8 text-gray-200 mx-auto mb-3" />
              <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No pending invitations</p>
              <button onClick={() => setShowInvite(true)} className="mt-2 text-[12px] text-[var(--color-primary)] hover:underline">Send an invite</button>
            </div>
          ) : (
            <>
              <div className="px-5 py-3 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] bg-gray-50">
                <span className="col-span-4">Email</span>
                <span className="col-span-2">Role</span>
                <span className="col-span-2">Status</span>
                <span className="col-span-2">Expires</span>
                <span className="col-span-2 text-right">Actions</span>
              </div>
              <div className="divide-y divide-[var(--color-border)]">
                {invitations.map(inv => {
                  const expired = new Date(inv.expires_at) < new Date();
                  const relExpiry = () => {
                    const d = (new Date(inv.expires_at).getTime() - Date.now()) / 1000;
                    if (d < 0) return "Expired";
                    if (d < 86400) return `${Math.round(d / 3600)}h left`;
                    return `${Math.round(d / 86400)}d left`;
                  };
                  return (
                    <div key={inv.id} className="px-5 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50">
                      <div className="col-span-4">
                        <p className="text-[13px] font-semibold text-[var(--color-text)] font-mono">{inv.email}</p>
                      </div>
                      <div className="col-span-2"><RoleBadge role={inv.role} /></div>
                      <div className="col-span-2">
                        <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${expired ? "bg-red-50 text-red-600 border-red-200" : "bg-amber-50 text-amber-700 border-amber-200"}`}>
                          {expired ? "Expired" : "Pending"}
                        </span>
                      </div>
                      <div className="col-span-2">
                        <span className={`text-[11px] font-medium ${expired ? "text-red-500" : "text-[var(--color-text-tertiary)]"}`} suppressHydrationWarning>{relExpiry()}</span>
                      </div>
                      <div className="col-span-2 flex items-center justify-end gap-1">
                        <button onClick={() => handleResendInvite(inv.id)} title="Resend" className="p-1.5 rounded-lg text-gray-300 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                          <Send className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => handleCancelInvite(inv.id)} title="Cancel" className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors">
                          <XCircle className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}

      {/* ── Roles / Permissions Matrix tab ───────────────────────────── */}
      {tab === "roles" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-[var(--color-border)]">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Permissions Matrix</h3>
            <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">What each role can do in your CertiFlow organization</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-[var(--color-border)]">
                  <th className="px-5 py-3 text-left text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] w-1/2">Action</th>
                  {(["owner", "admin", "member", "viewer"] as MemberRole[]).map(role => {
                    const rc = ROLE_CONFIG[role];
                    return (
                      <th key={role} className="px-4 py-3 text-center w-[12.5%]">
                        <div className="flex flex-col items-center gap-1">
                          <div className={`w-7 h-7 rounded-lg ${rc.bg} flex items-center justify-center`}>
                            <rc.Icon className={`w-4 h-4 ${rc.color}`} />
                          </div>
                          <span className={`text-[11px] font-bold ${rc.color}`}>{rc.label}</span>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]">
                {PERMISSIONS_MATRIX.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-5 py-3 text-[13px] text-[var(--color-text)]">{row.action}</td>
                    {(["owner", "admin", "member", "viewer"] as MemberRole[]).map(role => (
                      <td key={role} className="px-4 py-3 text-center">
                        {(row as any)[role] ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 mx-auto" />
                        ) : (
                          <XCircle className="w-4 h-4 text-gray-200 mx-auto" />
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showInvite && (
        <InviteModal
          onClose={() => setShowInvite(false)}
          onInvited={inv => setInvitations(prev => [inv, ...prev])}
        />
      )}
    </div>
  );
}
