"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Award,
  Plus,
  FileSpreadsheet,
  CheckCircle2,
  Clock,
  Layers,
  Search,
  Settings,
  ShieldCheck,
  ArrowUpRight,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const projects = [
  {
    id: "proj-ai-2026",
    name: "AI Workshop 2026",
    count: 250,
    status: "Completed",
    updated: "2 hours ago",
    template: "Academic Honors",
    verified: 198,
  },
  {
    id: "proj-hack-2026",
    name: "Global Hackathon 2026",
    count: 620,
    status: "Completed",
    updated: "Yesterday",
    template: "Hackathon First Prize",
    verified: 489,
  },
  {
    id: "proj-py-bootcamp",
    name: "Python Mastery Bootcamp",
    count: 110,
    status: "Draft",
    updated: "3 days ago",
    template: "Training Certificate",
    verified: 0,
  },
];

export function Dashboard() {
  const [search, setSearch] = useState("");

  const filtered = projects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* App Topbar */}
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
            <Button size="sm" asChild>
              <Link href="/demo">
                <Plus className="w-4 h-4 mr-1" />
                New Project
              </Link>
            </Button>
            <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-[13px] border border-indigo-200">
              AK
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-10 flex-1">
        {/* Welcome greeting */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-[28px] font-bold text-[var(--color-text)] tracking-tight">
              Good evening, Atul
            </h1>
            <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
              Create your next batch or monitor verified attendee credentials.
            </p>
          </div>

          <Button size="lg" asChild className="shadow-sm">
            <Link href="/demo">
              <Plus className="w-4 h-4 mr-1.5" />
              Create Batch
            </Link>
          </Button>
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10">
          <div className="bg-white p-6 rounded-2xl border border-[var(--color-border)] shadow-xs">
            <p className="text-[12px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">
              Certificates Created
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-[32px] font-bold text-[var(--color-text)] font-sans">2,340</span>
              <span className="text-[12px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                +14% this month
              </span>
            </div>
            <p className="text-[12px] text-[var(--color-text-secondary)] mt-1">Across 18 total events</p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-[var(--color-border)] shadow-xs">
            <p className="text-[12px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">
              Active Projects
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-[32px] font-bold text-[var(--color-text)] font-sans">18</span>
              <span className="text-[12px] text-[var(--color-text-tertiary)]">Batches configured</span>
            </div>
            <p className="text-[12px] text-[var(--color-text-secondary)] mt-1">3 recurring templates</p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-[var(--color-border)] shadow-xs">
            <p className="text-[12px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">
              QR Verified
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-[32px] font-bold text-[var(--color-primary)] font-sans">1,284</span>
              <span className="text-[12px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                54.8% scan rate
              </span>
            </div>
            <p className="text-[12px] text-[var(--color-text-secondary)] mt-1">Zero fraud or tamper events</p>
          </div>
        </div>

        {/* Projects Table Card */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
          <div className="p-6 border-b border-[var(--color-border)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-[18px] font-bold text-[var(--color-text)]">Recent Projects</h2>
              <p className="text-[13px] text-[var(--color-text-secondary)]">Manage certificates and export batches</p>
            </div>

            <div className="relative max-w-xs w-full">
              <Search className="w-4 h-4 text-[var(--color-text-tertiary)] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[13px] focus:outline-none focus:border-[var(--color-primary)]"
              />
            </div>
          </div>

          <div className="divide-y divide-[var(--color-border)]">
            {filtered.map((proj) => (
              <div
                key={proj.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[var(--color-background)]/60 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center shrink-0">
                    <FileSpreadsheet className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-[15px] font-semibold text-[var(--color-text)]">
                        {proj.name}
                      </h3>
                      <span className={`text-[11px] font-medium px-2 py-0.5 rounded ${
                        proj.status === "Completed"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-amber-50 text-amber-700"
                      }`}>
                        {proj.status}
                      </span>
                    </div>
                    <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">
                      {proj.count} certificates generated · Template: {proj.template} · Updated {proj.updated}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    href={`/verify/CERT-001`}
                    className="text-[13px] text-[var(--color-text-secondary)] hover:text-[var(--color-text)] font-medium flex items-center gap-1"
                  >
                    <span>{proj.verified} Scanned</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>

                  <Button size="sm" variant="secondary" asChild>
                    <Link href="/demo">
                      View Batch
                      <ChevronRight className="w-3.5 h-3.5 ml-1" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function AppPage() {
  return <Dashboard />;
}
