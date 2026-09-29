"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Bell,
  Award,
  Zap,
  Mail,
  AlertCircle,
  CheckCircle2,
  Info,
  X,
  ChevronRight,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────
export type NotificationType = "success" | "info" | "warning" | "error";

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  href?: string;
  read: boolean;
  created_at: string;
}

// ─── Demo notifications ───────────────────────────────────────────────────────
const DEMO_NOTIFICATIONS: AppNotification[] = [
  { id: "n1", type: "success", title: "Issuance job completed", body: "Job 'Q3 Workshop Batch' issued 1,240 certificates successfully.", href: "/app/issuance", read: false, created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString() },
  { id: "n2", type: "warning", title: "Approaching certificate limit", body: "You've used 94% of your monthly certificate quota. Upgrade to continue.", href: "/app/billing", read: false, created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString() },
  { id: "n3", type: "info", title: "New team member joined", body: "Priya Sharma accepted your invitation and joined as Admin.", href: "/app/team", read: false, created_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString() },
  { id: "n4", type: "error", title: "Webhook delivery failed", body: "Slack Notifications webhook failed 3 consecutive deliveries.", href: "/app/developer", read: true, created_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString() },
  { id: "n5", type: "success", title: "Report ready to download", body: "Your 'Q3 Certificate Report' is ready.", href: "/app/reports", read: true, created_at: new Date(Date.now() - 24 * 3600 * 1000).toISOString() },
];

// ─── Icon per type ────────────────────────────────────────────────────────────
const TYPE_CONFIG: Record<NotificationType, { Icon: React.ComponentType<{ className?: string }>; color: string; bg: string }> = {
  success: { Icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50" },
  info: { Icon: Info, color: "text-blue-600", bg: "bg-blue-50" },
  warning: { Icon: AlertCircle, color: "text-amber-600", bg: "bg-amber-50" },
  error: { Icon: AlertCircle, color: "text-red-600", bg: "bg-red-50" },
};

function relTime(iso: string) {
  const d = (Date.now() - new Date(iso).getTime()) / 1000;
  if (d < 60) return "just now";
  if (d < 3600) return `${Math.round(d / 60)}m ago`;
  if (d < 86400) return `${Math.round(d / 3600)}h ago`;
  return `${Math.round(d / 86400)}d ago`;
}

// ─── Notification item ────────────────────────────────────────────────────────
function NotificationItem({
  n,
  onRead,
  onDismiss,
  onClick,
}: {
  n: AppNotification;
  onRead: (id: string) => void;
  onDismiss: (id: string) => void;
  onClick: (n: AppNotification) => void;
}) {
  const tc = TYPE_CONFIG[n.type];

  return (
    <div
      className={`relative group flex items-start gap-3 px-4 py-3.5 hover:bg-gray-50/60 transition-colors cursor-pointer ${!n.read ? "bg-[var(--color-primary-subtle)]" : ""}`}
      onClick={() => { onRead(n.id); onClick(n); }}
    >
      {/* Unread dot */}
      {!n.read && (
        <span className="absolute top-4 left-1.5 w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
      )}

      <div className={`w-8 h-8 rounded-xl ${tc.bg} flex items-center justify-center shrink-0 mt-0.5`}>
        <tc.Icon className={`w-4 h-4 ${tc.color}`} />
      </div>

      <div className="flex-1 min-w-0">
        <p className={`text-[13px] font-semibold text-[var(--color-text)] leading-snug ${!n.read ? "font-bold" : ""}`}>
          {n.title}
        </p>
        <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5 leading-relaxed line-clamp-2">{n.body}</p>
        <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1">{relTime(n.created_at)}</p>
      </div>

      <button
        onClick={e => { e.stopPropagation(); onDismiss(n.id); }}
        className="opacity-0 group-hover:opacity-100 p-1 rounded-lg text-gray-300 hover:text-gray-600 hover:bg-gray-100 transition-all shrink-0"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Notification Bell + Panel
// ─────────────────────────────────────────────────────────────────────────────
export function NotificationBell({ isSidebarOpen = false }: { isSidebarOpen?: boolean }) {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>(DEMO_NOTIFICATIONS);

  const unread = notifications.filter(n => !n.read).length;

  const markRead = useCallback((id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  }, []);

  const dismiss = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  const handleClick = useCallback((n: AppNotification) => {
    if (n.href) window.location.href = n.href;
    setOpen(false);
  }, []);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      const panel = document.getElementById("notification-panel");
      const bell = document.getElementById("notification-bell");
      if (!panel?.contains(e.target as Node) && !bell?.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    setTimeout(() => document.addEventListener("mousedown", handler), 100);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div className="relative">
      <button
        id="notification-bell"
        onClick={() => setOpen(o => !o)}
        className={`relative w-9 h-9 rounded-xl flex items-center justify-center transition-colors ${open ? "bg-[var(--color-primary-subtle)] text-[var(--color-primary)]" : "text-gray-400 hover:text-[var(--color-text)] hover:bg-gray-100"}`}
        aria-label={`Notifications${unread > 0 ? ` (${unread} unread)` : ""}`}
      >
        <Bell className="w-4.5 h-4.5" style={{ width: 18, height: 18 }} />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 bg-[var(--color-primary)] text-white text-[9px] font-bold rounded-full flex items-center justify-center">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div
          id="notification-panel"
          className="absolute right-0 top-full mt-2 w-[360px] bg-white border border-[var(--color-border)] rounded-2xl shadow-xl overflow-hidden z-50"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3.5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-2">
              <h3 className="text-[14px] font-bold text-[var(--color-text)]">Notifications</h3>
              {unread > 0 && (
                <span className="text-[10px] font-bold bg-[var(--color-primary)] text-white px-1.5 py-0.5 rounded-full">{unread}</span>
              )}
            </div>
            {unread > 0 && (
              <button onClick={markAllRead} className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline">
                Mark all read
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-[420px] overflow-y-auto divide-y divide-[var(--color-border)]">
            {notifications.length === 0 ? (
              <div className="px-4 py-12 text-center">
                <Bell className="w-8 h-8 text-gray-200 mx-auto mb-3" />
                <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">All caught up!</p>
                <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">No new notifications</p>
              </div>
            ) : (
              notifications.map(n => (
                <NotificationItem key={n.id} n={n} onRead={markRead} onDismiss={dismiss} onClick={handleClick} />
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-3 border-t border-[var(--color-border)] text-center">
              <button className="text-[12px] font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-1 mx-auto">
                View all activity <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
