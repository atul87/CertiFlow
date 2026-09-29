"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api-client";
import {
  Award,
  Plus,
  Search,
  Sliders,
  Layers,
  CheckCircle2,
  Clock,
  ArrowRight,
  ExternalLink,
  ChevronRight,
  Sparkles,
  FileSpreadsheet,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";

export default function ProjectsDirectoryPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "completed" | "draft">("all");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const [projectsList, setProjectsList] = useState<any[]>([
    {
      id: "proj-ai-2026",
      name: "AI Workshop 2026",
      description: "Annual artificial intelligence practical summit certification",
      count: 500,
      status: "Ready for Generation",
      template: "Academic Honors Landscape (A4)",
      updated: "Just now",
      verified: 498,
    },
    {
      id: "proj-hack-2026",
      name: "Global Hackathon 2026",
      description: "Worldwide student developer hackathon prize winners and attendees",
      count: 620,
      status: "Completed",
      template: "Modern Tech Gradient",
      updated: "Yesterday",
      verified: 612,
    },
    {
      id: "proj-py-bootcamp",
      name: "Python Mastery Bootcamp",
      description: "12-week comprehensive Python & data structures cohort",
      count: 110,
      status: "Draft",
      template: "Executive Minimalist",
      updated: "3 days ago",
      verified: 0,
    },
    {
      id: "proj-leadership",
      name: "Executive Leadership Summit",
      description: "Senior management leadership credentials",
      count: 85,
      status: "Completed",
      template: "Prestige Roman Honors",
      updated: "1 week ago",
      verified: 85,
    },
  ]);

  useEffect(() => {
    let isMounted = true;
    async function loadTemplates() {
      try {
        const res = await api.templates.list();
        const items = (res as any)?.items || (res as any)?.data || (Array.isArray(res) ? res : []);
        if (isMounted && items.length > 0) {
          const mapped = items.map((t: any) => ({
            id: t.id,
            name: t.name,
            description: t.description || "Production certificate template",
            count: t.certificate_count || 0,
            status: t.current_version_id ? "Active Template" : "Draft",
            template: "Canvas Vector Layout",
            updated: t.updated_at ? new Date(t.updated_at).toLocaleDateString() : "Recent",
            verified: 0,
          }));
          setProjectsList((prev) => {
            const ids = new Set(mapped.map((m: any) => m.id));
            const filteredPrev = prev.filter((p: any) => !ids.has(p.id));
            return [...mapped, ...filteredPrev];
          });
        }
      } catch {
        // Retain fallback data
      }
    }
    loadTemplates();
    return () => { isMounted = false; };
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    setIsCreating(true);
    let createdId = `proj-${Date.now()}`;

    try {
      const created = await api.templates.create({
        name: newProjectName.trim(),
        description: newProjectDesc.trim(),
      });
      if (created?.id) {
        createdId = created.id;
      }
    } catch {
      // Fallback
    }

    const newProj = {
      id: createdId,
      name: newProjectName,
      description: newProjectDesc || "Custom certification project",
      count: 0,
      status: "Active Template",
      template: "Academic Honors Landscape (A4)",
      updated: "Just now",
      verified: 0,
    };

    setProjectsList((prev) => [newProj, ...prev]);
    setIsCreating(false);
    setIsCreateModalOpen(false);
    setNewProjectName("");
    setNewProjectDesc("");
  };


  const filtered = projectsList.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase());
    const matchesFilter =
      filter === "all"
        ? true
        : filter === "completed"
        ? p.status === "Completed"
        : p.status !== "Completed";
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center font-bold">
                <Award className="w-4 h-4" />
              </div>
              <span className="text-[17px] font-bold text-[var(--color-text)]">
                CertiFlow
              </span>
              <span className="text-[12px] bg-gray-100 text-[var(--color-text-secondary)] px-2 py-0.5 rounded font-mono">
                Studio
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-1 text-[14px]">
              <Link href="/app" className="px-3 py-1.5 font-semibold text-[var(--color-primary)] bg-[var(--color-primary-subtle)] rounded-md">
                Projects
              </Link>
              <Link href="/app/certificates" className="px-3 py-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-text)] rounded-md transition-colors">
                Certificates Vault
              </Link>
              <Link href="/templates" className="px-3 py-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-text)] rounded-md transition-colors">
                Templates
              </Link>
              <Link href="/app/settings" className="px-3 py-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-text)] rounded-md transition-colors">
                Settings
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="w-4 h-4 mr-1" />
              New Project
            </Button>
            <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-[13px] border border-indigo-200">
              AK
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-10 flex-1 space-y-6">
        {/* P12 Migration Notice */}
        <div className="bg-indigo-50/80 border border-indigo-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[13px] font-bold text-indigo-950">Templates is now the central design workspace</p>
              <p className="text-[12px] text-indigo-700">Project presets and canvas designs have migrated to the new Templates & Issuance centers.</p>
            </div>
          </div>
          <Link
            href="/app/templates"
            className="px-4 py-2 rounded-xl bg-[#635BFF] text-white text-[12px] font-semibold hover:bg-indigo-600 transition-colors shrink-0 text-center shadow-xs"
          >
            Open Templates Center →
          </Link>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-[28px] font-bold text-[var(--color-text)] tracking-tight">
              All Certification Projects
            </h1>
            <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
              Manage design templates, recipient datasets, field mapping, and batch issuance.
            </p>
          </div>

          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            Create Certificate Batch
          </Button>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-4 shadow-2xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search projects by name or description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-[13px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl focus:outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          <div className="flex items-center gap-2">
            <div className="flex bg-gray-100 p-0.5 rounded-lg text-[12px]">
              <button
                onClick={() => setFilter("all")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filter === "all" ? "bg-white text-black shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                All ({projectsList.length})
              </button>
              <button
                onClick={() => setFilter("completed")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filter === "completed" ? "bg-white text-emerald-700 shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                Completed
              </button>
              <button
                onClick={() => setFilter("draft")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  filter === "draft" ? "bg-white text-amber-700 shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                In Progress
              </button>
            </div>
          </div>
        </div>

        {/* Projects Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((proj) => (
            <div
              key={proj.id}
              className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs hover:border-[var(--color-border-hover)] hover:shadow-md transition-all flex flex-col justify-between space-y-5"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge
                    variant={proj.status === "Completed" ? "success" : proj.status === "Ready for Generation" ? "primary" : "warning"}
                    className="text-[11px]"
                  >
                    {proj.status}
                  </Badge>
                  <span className="text-[11px] font-mono text-gray-400">{proj.updated}</span>
                </div>

                <div>
                  <h3 className="text-[18px] font-bold text-gray-900">{proj.name}</h3>
                  <p className="text-[13px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">
                    {proj.description}
                  </p>
                </div>
              </div>

              <div className="space-y-4 pt-2 border-t border-[var(--color-border)]">
                <div className="grid grid-cols-2 gap-2 text-[12px]">
                  <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-bold">Recipients</span>
                    <span className="font-bold text-gray-800">{proj.count} rows</span>
                  </div>
                  <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-bold">Verified</span>
                    <span className="font-bold text-emerald-600">{proj.verified} credentials</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button size="sm" variant="secondary" className="flex-1 justify-center" asChild>
                    <Link href={`/app/projects/${proj.id}/editor`}>
                      <Sliders className="w-3.5 h-3.5 mr-1" />
                      Editor
                    </Link>
                  </Button>
                  <Button size="sm" className="flex-1 justify-center" asChild>
                    <Link href={`/app/projects/${proj.id}`}>
                      Overview <ArrowRight className="w-3.5 h-3.5 ml-1" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* CREATE NEW PROJECT MODAL */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Certification Project"
        description="Set up a new project workspace for template design and bulk issuance."
        size="md"
      >
        <form onSubmit={handleCreateProject} className="space-y-4 py-2">
          <div>
            <label className="block text-[12px] font-semibold text-gray-700 mb-1">
              Project Name *
            </label>
            <input
              required
              type="text"
              placeholder="e.g. Winter 2026 DevCon Certification"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
            />
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              rows={3}
              placeholder="Short note regarding cohort, organizers, or award criteria..."
              value={newProjectDesc}
              onChange={(e) => setNewProjectDesc(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-[var(--color-border)]">
            <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Workspace</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
