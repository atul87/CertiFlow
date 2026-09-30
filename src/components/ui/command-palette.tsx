"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Award,
  FileSpreadsheet,
  Zap,
  FileText,
  Users,
  BarChart3,
  Code2,
  CreditCard,
  Mail,
  ShieldCheck,
  Settings,
  ArrowRight,
  X,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────
interface SearchResult {
  id: string;
  type: "certificate" | "template" | "import" | "job" | "page" | "recipient";
  title: string;
  subtitle?: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  iconBg: string;
}

interface SearchGroup {
  label: string;
  results: SearchResult[];
}

// ─── Static page results ──────────────────────────────────────────────────────
const PAGES: SearchResult[] = [
  { id: "page-dashboard", type: "page", title: "Dashboard", subtitle: "Overview and KPIs", href: "/app", icon: BarChart3, iconColor: "text-indigo-600", iconBg: "bg-indigo-50" },
  { id: "page-templates", type: "page", title: "Templates", subtitle: "Certificate design templates", href: "/app/templates", icon: FileText, iconColor: "text-blue-600", iconBg: "bg-blue-50" },
  { id: "page-imports", type: "page", title: "Import Center", subtitle: "Upload CSV recipient lists", href: "/app/imports", icon: FileSpreadsheet, iconColor: "text-emerald-600", iconBg: "bg-emerald-50" },
  { id: "page-issuance", type: "page", title: "Issuance", subtitle: "Bulk certificate generation jobs", href: "/app/issuance", icon: Zap, iconColor: "text-violet-600", iconBg: "bg-violet-50" },
  { id: "page-certificates", type: "page", title: "Certificate Vault", subtitle: "All issued certificates", href: "/app/certificates", icon: Award, iconColor: "text-amber-600", iconBg: "bg-amber-50" },
  { id: "page-credentials", type: "page", title: "Digital Credentials", subtitle: "W3C VC & Open Badges 3.0", href: "/app/credentials", icon: ShieldCheck, iconColor: "text-purple-600", iconBg: "bg-purple-50" },
  { id: "page-email", type: "page", title: "Email Center", subtitle: "Delivery logs and templates", href: "/app/email", icon: Mail, iconColor: "text-sky-600", iconBg: "bg-sky-50" },
  { id: "page-analytics", type: "page", title: "Analytics", subtitle: "Metrics and trends", href: "/app/analytics", icon: BarChart3, iconColor: "text-indigo-600", iconBg: "bg-indigo-50" },
  { id: "page-team", type: "page", title: "Team", subtitle: "Members and invitations", href: "/app/team", icon: Users, iconColor: "text-amber-600", iconBg: "bg-amber-50" },
  { id: "page-developer", type: "page", title: "Developer Portal", subtitle: "API keys and webhooks", href: "/app/developer", icon: Code2, iconColor: "text-gray-600", iconBg: "bg-gray-100" },
  { id: "page-billing", type: "page", title: "Billing", subtitle: "Subscription and invoices", href: "/app/billing", icon: CreditCard, iconColor: "text-teal-600", iconBg: "bg-teal-50" },
  { id: "page-settings", type: "page", title: "Settings", subtitle: "Organization and profile", href: "/app/settings", icon: Settings, iconColor: "text-gray-600", iconBg: "bg-gray-100" },
];

// ─── Command suggestions ──────────────────────────────────────────────────────
const QUICK_ACTIONS: SearchResult[] = [
  { id: "action-new-template", type: "page", title: "New Template", subtitle: "Create a certificate template", href: "/app/templates?create=1", icon: FileText, iconColor: "text-blue-600", iconBg: "bg-blue-50" },
  { id: "action-new-job", type: "page", title: "New Issuance Job", subtitle: "Start bulk certificate generation", href: "/app/issuance?create=1", icon: Zap, iconColor: "text-violet-600", iconBg: "bg-violet-50" },
  { id: "action-invite", type: "page", title: "Invite Team Member", subtitle: "Add a new member to your org", href: "/app/team?invite=1", icon: Users, iconColor: "text-amber-600", iconBg: "bg-amber-50" },
  { id: "action-new-key", type: "page", title: "Create API Key", subtitle: "Generate a new live API key", href: "/app/developer?create=1", icon: Code2, iconColor: "text-gray-600", iconBg: "bg-gray-100" },
];

// ─── Recent items (simulated from localStorage) ───────────────────────────────
const RECENT_KEY = "certiflow_search_recent";

function getRecent(): SearchResult[] {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
  } catch {
    return [];
  }
}

function addRecent(item: SearchResult) {
  try {
    const prev = getRecent().filter(r => r.id !== item.id).slice(0, 4);
    localStorage.setItem(RECENT_KEY, JSON.stringify([item, ...prev]));
  } catch { /* ok */ }
}

// ─── Result item ──────────────────────────────────────────────────────────────
function ResultItem({
  result,
  active,
  onClick,
}: {
  result: SearchResult;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-left group ${
        active ? "bg-[var(--color-primary-subtle)] ring-1 ring-[var(--color-primary)]/20" : "hover:bg-gray-50"
      }`}
    >
      <div className={`w-8 h-8 rounded-lg ${result.iconBg} flex items-center justify-center shrink-0`}>
        <result.icon className={`w-4 h-4 ${result.iconColor}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-[13px] font-semibold truncate ${active ? "text-[var(--color-primary)]" : "text-[var(--color-text)]"}`}>
          {result.title}
        </p>
        {result.subtitle && (
          <p className="text-[11px] text-[var(--color-text-tertiary)] truncate">{result.subtitle}</p>
        )}
      </div>
      <ArrowRight className={`w-3.5 h-3.5 shrink-0 transition-opacity ${active ? "opacity-100 text-[var(--color-primary)]" : "opacity-0"}`} />
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Command Palette
// ─────────────────────────────────────────────────────────────────────────────
export function CommandPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [activeIdx, setActiveIdx] = useState(0);
  const [recent, setRecent] = useState<SearchResult[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    setRecent(getRecent());
    setTimeout(() => inputRef.current?.focus(), 50);

    const handleGlobalKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleGlobalKey);
    return () => window.removeEventListener("keydown", handleGlobalKey);
  }, [onClose]);

  // Filter pages + build groups
  const filtered = query.trim()
    ? PAGES.filter(
        p =>
          p.title.toLowerCase().includes(query.toLowerCase()) ||
          p.subtitle?.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  const groups: SearchGroup[] = query.trim()
    ? filtered.length
      ? [{ label: "Pages & Sections", results: filtered }]
      : []
    : [
        ...(recent.length ? [{ label: "Recent", results: recent }] : []),
        { label: "Quick Actions", results: QUICK_ACTIONS },
        { label: "Navigate", results: PAGES.slice(0, 6) },
      ];

  const allResults = groups.flatMap(g => g.results);

  const navigate = useCallback(
    (result: SearchResult) => {
      addRecent(result);
      router.push(result.href);
      onClose();
    },
    [router, onClose]
  );

  useEffect(() => { setActiveIdx(0); }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx(i => Math.min(i + 1, allResults.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx(i => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (allResults[activeIdx]) navigate(allResults[activeIdx]);
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  // Global counter for result index
  let globalIdx = 0;

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-start justify-center pt-[12vh] p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-xl border border-[var(--color-border)] overflow-hidden"
        style={{ maxHeight: "calc(100vh - 24vh)" }}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-[var(--color-border)]">
          <Search className="w-4 h-4 text-[var(--color-text-tertiary)] shrink-0" />
          <input
            id="command-palette-input"
            data-testid="command-palette-input"
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search pages, certificates, templates…"
            className="flex-1 text-[14px] bg-transparent text-[var(--color-text)] placeholder:text-[var(--color-text-tertiary)] outline-none"
          />
          {query && (
            <button onClick={() => setQuery("")} className="text-gray-400 hover:text-gray-600 transition-colors">
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="hidden sm:flex items-center gap-1 text-[10px] font-bold text-[var(--color-text-tertiary)] bg-gray-100 px-1.5 py-0.5 rounded border border-gray-200">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div className="overflow-y-auto" style={{ maxHeight: "calc(100vh - 24vh - 60px)" }}>
          {groups.length === 0 && query.trim() ? (
            <div className="px-4 py-12 text-center">
              <Search className="w-8 h-8 text-gray-200 mx-auto mb-3" />
              <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No results for &ldquo;{query}&rdquo;</p>
              <p className="text-[12px] text-[var(--color-text-tertiary)] mt-1">Try searching for a page, template, or team member</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {groups.map(group => (
                <div key={group.label}>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] px-3 py-2">
                    {group.label}
                  </p>
                  {group.results.map(result => {
                    const idx = globalIdx++;
                    return (
                      <ResultItem
                        key={result.id}
                        result={result}
                        active={activeIdx === idx}
                        onClick={() => navigate(result)}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          )}

          {/* Footer hints */}
          <div className="px-4 py-2.5 border-t border-[var(--color-border)] flex items-center gap-4 text-[11px] text-[var(--color-text-tertiary)]">
            <span className="flex items-center gap-1">
              <kbd className="bg-gray-100 border border-gray-200 px-1 py-0.5 rounded text-[10px] font-bold">↑↓</kbd>
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="bg-gray-100 border border-gray-200 px-1 py-0.5 rounded text-[10px] font-bold">↵</kbd>
              Open
            </span>
            <span className="flex items-center gap-1">
              <kbd className="bg-gray-100 border border-gray-200 px-1 py-0.5 rounded text-[10px] font-bold">ESC</kbd>
              Close
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────
export function useCommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key?.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(o => !o);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return { open, setOpen };
}
