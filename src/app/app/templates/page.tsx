"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  FileText,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit3,
  Copy,
  Archive,
  Trash2,
  CheckCircle,
  Clock,
  Box,
  Globe,
  Upload,
  RefreshCw,
  Award,
  ChevronDown,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { Template, TemplateStatus } from "@/types";

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

// ─── Status Badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: TemplateStatus }) {
  const config = {
    draft: { label: "Draft", class: "bg-gray-100 text-gray-600 border-gray-200", Icon: Clock },
    published: { label: "Published", class: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle },
    archived: { label: "Archived", class: "bg-amber-50 text-amber-700 border-amber-200", Icon: Archive },
  }[status] || { label: status, class: "bg-gray-100 text-gray-600 border-gray-200", Icon: Clock };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${config.class}`}>
      <config.Icon className="w-3 h-3" />
      {config.label}
    </span>
  );
}

// ─── Dropdown Menu ─────────────────────────────────────────────────────────────
function TemplateMenu({
  template,
  onAction,
}: {
  template: Template;
  onAction: (action: string, id: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={(e) => { e.stopPropagation(); setOpen((o) => !o); }}
        className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
      >
        <MoreHorizontal className="w-4 h-4" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-1 z-20 w-44 bg-white border border-[var(--color-border)] rounded-xl shadow-lg py-1.5 overflow-hidden">
            <button
              onClick={() => { setOpen(false); onAction("preview", template.id); }}
              className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50"
            >
              <Eye className="w-3.5 h-3.5 text-gray-400" />
              Preview
            </button>
            <Link
              href={`/app/templates/${template.id}/editor`}
              className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50"
              onClick={() => setOpen(false)}
            >
              <Edit3 className="w-3.5 h-3.5 text-gray-400" />
              Edit in Designer
            </Link>
            <button
              onClick={() => { setOpen(false); onAction("duplicate", template.id); }}
              className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-[var(--color-text)] hover:bg-gray-50"
            >
              <Copy className="w-3.5 h-3.5 text-gray-400" />
              Duplicate
            </button>

            {template.status === "draft" && (
              <button
                onClick={() => { setOpen(false); onAction("publish", template.id); }}
                className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-emerald-700 hover:bg-emerald-50"
              >
                <Globe className="w-3.5 h-3.5 text-emerald-500" />
                Publish
              </button>
            )}

            {template.status === "published" && (
              <button
                onClick={() => { setOpen(false); onAction("archive", template.id); }}
                className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-amber-700 hover:bg-amber-50"
              >
                <Archive className="w-3.5 h-3.5 text-amber-500" />
                Archive
              </button>
            )}

            <div className="border-t border-[var(--color-border)] my-1" />
            <button
              onClick={() => { setOpen(false); onAction("delete", template.id); }}
              className="flex items-center gap-2.5 w-full px-3.5 py-2 text-[13px] text-red-600 hover:bg-red-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          </div>
        </>
      )}
    </div>
  );
}

// ─── Template Card ─────────────────────────────────────────────────────────────
function TemplateCard({
  template,
  onAction,
}: {
  template: Template;
  onAction: (action: string, id: string) => void;
}) {
  const relTime = (iso: string) => {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
    return `${Math.round(diff / 86400)}d ago`;
  };

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs hover:shadow-md hover:border-[var(--color-border-hover)] transition-all group overflow-hidden">
      {/* Certificate preview thumbnail */}
      <Link href={`/app/projects/${template.id}/editor`}>
        <div className="relative h-40 bg-gradient-to-br from-indigo-50 via-purple-50/50 to-blue-50 border-b border-[var(--color-border)] overflow-hidden">
          {template.thumbnail_url ? (
            <img
              src={template.thumbnail_url}
              alt={template.name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              {/* Decorative certificate preview */}
              <div className="w-32 h-24 bg-white rounded-lg shadow border border-indigo-100 flex flex-col items-center justify-center p-2 gap-1.5">
                <Award className="w-5 h-5 text-indigo-400" />
                <div className="space-y-1 w-full px-1">
                  <div className="h-1.5 bg-gray-100 rounded w-full" />
                  <div className="h-1 bg-gray-100 rounded w-3/4 mx-auto" />
                  <div className="h-1 bg-gray-100 rounded w-1/2 mx-auto" />
                </div>
              </div>
              <span className="text-[10px] font-medium text-gray-400">
                {template.width_mm || 297}×{template.height_mm || 210}mm
              </span>
            </div>
          )}
          <div className="absolute top-2.5 right-2.5">
            <StatusBadge status={template.status} />
          </div>
        </div>
      </Link>

      {/* Card body */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2">
          <Link href={`/app/projects/${template.id}/editor`} className="flex-1 min-w-0">
            <h3 className="text-[14px] font-bold text-[var(--color-text)] truncate group-hover:text-[var(--color-primary)] transition-colors">
              {template.name}
            </h3>
            {template.description && (
              <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5 line-clamp-1">
                {template.description}
              </p>
            )}
          </Link>
          <TemplateMenu template={template} onAction={onAction} />
        </div>

        {/* Meta */}
        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-[var(--color-border)]">
          <span className="text-[11px] text-[var(--color-text-tertiary)]">
            v{template.version_number}
          </span>
          <span className="text-[11px] text-[var(--color-text-tertiary)]">
            {template.variable_tags?.length || 0} fields
          </span>
          <span className="text-[11px] text-[var(--color-text-tertiary)] ml-auto">
            {relTime(template.updated_at)}
          </span>
        </div>

        {/* CTA */}
        <div className="flex gap-2 mt-3">
          <Link
            href={`/app/projects/${template.id}/editor`}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold bg-[var(--color-primary-subtle)] text-[var(--color-primary)] hover:bg-[var(--color-primary-light)] transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5" />
            Edit
          </Link>
          {template.status === "published" && (
            <Link
              href="/app/imports"
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50 transition-colors"
            >
              <Upload className="w-3.5 h-3.5" />
              Use
            </Link>
          )}
          {template.status === "draft" && (
            <button
              onClick={() => onAction("publish", template.id)}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold border border-emerald-200 text-emerald-700 hover:bg-emerald-50 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />
              Publish
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Create Template Modal ─────────────────────────────────────────────────────
function CreateTemplateModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (template: Template) => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [orientation, setOrientation] = useState<"landscape" | "portrait">("landscape");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const PRESETS = [
    { label: "Course Certificate", icon: "🎓", desc: "Standard academic/training certificate" },
    { label: "Internship Certificate", icon: "💼", desc: "Professional work experience" },
    { label: "Workshop Certificate", icon: "🛠️", desc: "Short-form skill workshop" },
    { label: "Hackathon Certificate", icon: "⚡", desc: "Competition/event participation" },
    { label: "Achievement Certificate", icon: "🏆", desc: "General achievement recognition" },
    { label: "Blank Canvas", icon: "✏️", desc: "Start from scratch" },
  ];
  const [selectedPreset, setSelectedPreset] = useState(PRESETS[0].label);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const payload = {
        name: name.trim(),
        description: description.trim() || undefined,
        orientation,
        preset: selectedPreset,
        width_mm: orientation === "landscape" ? 297 : 210,
        height_mm: orientation === "landscape" ? 210 : 297,
      };

      const created = await api.templates.create(payload);
      onCreated(created);
    } catch (err: any) {
      // Demo mode fallback
      const mock: Template = {
        id: `tmpl-${Date.now()}`,
        name: name.trim(),
        description: description.trim(),
        status: "draft",
        width_mm: orientation === "landscape" ? 297 : 210,
        height_mm: orientation === "landscape" ? 210 : 297,
        orientation,
        current_version_id: `ver-${Date.now()}`,
        version_number: 1,
        variable_tags: ["recipient_name", "program_name", "issue_date", "certificate_id"],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      onCreated(mock);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl border border-[var(--color-border)]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--color-border)]">
          <div>
            <h2 className="text-[17px] font-bold text-[var(--color-text)]">New Template</h2>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">
              Choose a starting point for your certificate design
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-[20px] leading-none"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleCreate} className="px-6 py-5 space-y-5">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-[13px]">
              {error}
            </div>
          )}

          {/* Preset grid */}
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2.5 uppercase tracking-wide">
              Starting Template
            </label>
            <div className="grid grid-cols-3 gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => { setSelectedPreset(p.label); if (!name) setName(p.label); }}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all ${
                    selectedPreset === p.label
                      ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] shadow-sm"
                      : "border-[var(--color-border)] hover:border-[var(--color-border-hover)] hover:bg-gray-50"
                  }`}
                >
                  <span className="text-xl">{p.icon}</span>
                  <span className="text-[11px] font-semibold text-[var(--color-text)]">{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">
              Template Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. ML Workshop Completion Certificate"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-1.5">
              Description <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of this template's purpose"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
            />
          </div>

          {/* Orientation */}
          <div>
            <label className="block text-[12px] font-bold text-[var(--color-text)] mb-2">
              Orientation
            </label>
            <div className="flex gap-3">
              {(["landscape", "portrait"] as const).map((o) => (
                <button
                  key={o}
                  type="button"
                  onClick={() => setOrientation(o)}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg border text-[13px] font-semibold transition-all ${
                    orientation === o
                      ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] text-[var(--color-primary)]"
                      : "border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50"
                  }`}
                >
                  {o === "landscape" ? (
                    <span className="w-5 h-3.5 border-2 rounded border-current" />
                  ) : (
                    <span className="w-3.5 h-5 border-2 rounded border-current" />
                  )}
                  {o.charAt(0).toUpperCase() + o.slice(1)}
                  <span className="text-[10px] text-gray-400">
                    {o === "landscape" ? "(297×210mm)" : "(210×297mm)"}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 rounded-lg border border-[var(--color-border)] text-[13px] font-semibold text-[var(--color-text-secondary)] hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <Button type="submit" loading={loading} className="flex-1 justify-center">
              <ArrowRight className="w-3.5 h-3.5 mr-1.5" />
              Create & Open Editor
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Templates Page
// ─────────────────────────────────────────────────────────────────────────────
export default function TemplatesPage() {
  const [loading, setLoading] = useState(true);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filter, setFilter] = useState<"all" | TemplateStatus>("all");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.templates.list();
      const items: Template[] = res?.items || (Array.isArray(res) ? res : []);
      setTemplates(items);
    } catch {
      // Demo data
      setTemplates([
        {
          id: "tmpl-001",
          name: "Academic Honors Certificate",
          description: "Standard academic completion and honors recognition",
          status: "published",
          width_mm: 297,
          height_mm: 210,
          orientation: "landscape",
          current_version_id: "ver-001",
          version_number: 3,
          variable_tags: ["recipient_name", "program_name", "issue_date", "certificate_id", "grade"],
          created_at: new Date(Date.now() - 86400 * 30 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 86400 * 2 * 1000).toISOString(),
          published_at: new Date(Date.now() - 86400 * 25 * 1000).toISOString(),
        },
        {
          id: "tmpl-002",
          name: "ML Workshop Completion",
          description: "Machine Learning workshop participant certificate",
          status: "published",
          width_mm: 297,
          height_mm: 210,
          orientation: "landscape",
          current_version_id: "ver-002",
          version_number: 1,
          variable_tags: ["recipient_name", "program_name", "issue_date", "certificate_id", "trainer"],
          created_at: new Date(Date.now() - 86400 * 14 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 86400 * 1 * 1000).toISOString(),
          published_at: new Date(Date.now() - 86400 * 12 * 1000).toISOString(),
        },
        {
          id: "tmpl-003",
          name: "Internship Completion",
          description: "Corporate internship completion certificate for HR",
          status: "draft",
          width_mm: 297,
          height_mm: 210,
          orientation: "landscape",
          current_version_id: "ver-003",
          version_number: 2,
          variable_tags: ["recipient_name", "department", "duration", "supervisor", "issue_date"],
          created_at: new Date(Date.now() - 86400 * 7 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 3600 * 2 * 1000).toISOString(),
        },
        {
          id: "tmpl-004",
          name: "Hackathon Winner",
          description: "Competition placement and achievement recognition",
          status: "draft",
          width_mm: 210,
          height_mm: 297,
          orientation: "portrait",
          current_version_id: "ver-004",
          version_number: 1,
          variable_tags: ["recipient_name", "placement", "project_name", "event_date"],
          created_at: new Date(Date.now() - 86400 * 3 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 3600 * 5 * 1000).toISOString(),
        },
        {
          id: "tmpl-005",
          name: "Legacy Training Certificate",
          description: "Old format — replaced by ML Workshop template",
          status: "archived",
          width_mm: 297,
          height_mm: 210,
          orientation: "landscape",
          current_version_id: "ver-005",
          version_number: 4,
          variable_tags: ["recipient_name", "course", "issue_date"],
          created_at: new Date(Date.now() - 86400 * 90 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 86400 * 45 * 1000).toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  const handleAction = async (action: string, id: string) => {
    setActionLoading(id);
    try {
      if (action === "publish") {
        await api.templates.publish(id);
        setTemplates((prev) =>
          prev.map((t) => (t.id === id ? { ...t, status: "published" } : t))
        );
      } else if (action === "archive") {
        await api.templates.archive(id);
        setTemplates((prev) =>
          prev.map((t) => (t.id === id ? { ...t, status: "archived" } : t))
        );
      } else if (action === "duplicate") {
        const dup = await api.templates.duplicate(id);
        setTemplates((prev) => [dup, ...prev]);
      } else if (action === "delete") {
        if (!confirm("Delete this template? This cannot be undone.")) return;
        await api.templates.delete(id);
        setTemplates((prev) => prev.filter((t) => t.id !== id));
      } else if (action === "preview") {
        window.open(`/app/projects/${id}`, "_blank");
      }
    } catch {
      // Demo mode: apply optimistic update
      if (action === "publish") {
        setTemplates((prev) =>
          prev.map((t) => (t.id === id ? { ...t, status: "published" } : t))
        );
      } else if (action === "archive") {
        setTemplates((prev) =>
          prev.map((t) => (t.id === id ? { ...t, status: "archived" } : t))
        );
      } else if (action === "delete") {
        if (!confirm("Delete this template? This cannot be undone.")) return;
        setTemplates((prev) => prev.filter((t) => t.id !== id));
      }
    } finally {
      setActionLoading(null);
    }
  };

  // Filter + search
  const filtered = templates.filter((t) => {
    const matchesFilter = filter === "all" || t.status === filter;
    const matchesSearch =
      !search ||
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      (t.description || "").toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const counts = {
    all: templates.length,
    draft: templates.filter((t) => t.status === "draft").length,
    published: templates.filter((t) => t.status === "published").length,
    archived: templates.filter((t) => t.status === "archived").length,
  };

  const TABS: { id: "all" | TemplateStatus; label: string; count: number }[] = [
    { id: "all", label: "All", count: counts.all },
    { id: "published", label: "Published", count: counts.published },
    { id: "draft", label: "Drafts", count: counts.draft },
    { id: "archived", label: "Archived", count: counts.archived },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">Templates</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">
            Design and manage your certificate visual templates
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={loadTemplates} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            New Template
          </Button>
        </div>
      </div>

      {/* Tabs + Search row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        {/* Status tabs */}
        <div className="flex items-center bg-gray-100/70 rounded-xl p-1 gap-0.5">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${
                filter === tab.id
                  ? "bg-white text-[var(--color-text)] shadow-sm"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span
                  className={`text-[11px] px-1.5 py-0.5 rounded-full font-bold ${
                    filter === tab.id
                      ? "bg-[var(--color-primary)] text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search templates…"
            className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-[var(--color-primary)] transition-colors"
          />
        </div>
      </div>

      {/* Template Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden">
              <Skeleton className="h-40 rounded-none" />
              <div className="p-4 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
            <FileText className="w-7 h-7 text-gray-300" />
          </div>
          {search ? (
            <>
              <h3 className="text-[16px] font-bold text-[var(--color-text)]">No templates found</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                Try a different search term or clear the filter
              </p>
              <button
                onClick={() => { setSearch(""); setFilter("all"); }}
                className="mt-4 text-[13px] font-semibold text-[var(--color-primary)] hover:underline"
              >
                Clear filters
              </button>
            </>
          ) : (
            <>
              <h3 className="text-[16px] font-bold text-[var(--color-text)]">
                {filter === "all" ? "No templates yet" : `No ${filter} templates`}
              </h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 max-w-sm">
                {filter === "all"
                  ? "Create your first certificate template to start issuing credentials to your recipients."
                  : "Try another status filter or create a new template."}
              </p>
              {filter === "all" && (
                <Button className="mt-6" onClick={() => setShowCreate(true)}>
                  <Plus className="w-4 h-4 mr-1.5" />
                  Create First Template
                </Button>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {/* New template card */}
          <button
            onClick={() => setShowCreate(true)}
            className="h-auto bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-[var(--color-primary-subtle)] transition-all group flex flex-col items-center justify-center gap-3 py-12"
          >
            <div className="w-10 h-10 rounded-xl border-2 border-dashed border-gray-300 group-hover:border-[var(--color-primary)] flex items-center justify-center transition-colors">
              <Plus className="w-5 h-5 text-gray-400 group-hover:text-[var(--color-primary)]" />
            </div>
            <div className="text-center">
              <p className="text-[13px] font-bold text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary)]">
                New Template
              </p>
              <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">
                Start from scratch or preset
              </p>
            </div>
          </button>

          {filtered.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onAction={handleAction}
            />
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <CreateTemplateModal
          onClose={() => setShowCreate(false)}
          onCreated={(t) => {
            setTemplates((prev) => [t, ...prev]);
            setShowCreate(false);
            // Navigate to editor
            window.location.href = `/app/projects/${t.id}/editor`;
          }}
        />
      )}
    </div>
  );
}
