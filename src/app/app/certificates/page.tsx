"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Download, RefreshCw, Plus, Award, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  CertificateTable,
  CertificateFilters,
  CertificateRevokeModal,
  CertificateDetailDrawer,
} from "@/components/certificates";
import {
  useCertificates,
  useRevokeCertificate,
  useRestoreCertificate,
} from "@/lib/query";
import type { Certificate, CertificateStatus } from "@/types";

const DEMO_CERTS: Certificate[] = Array.from({ length: 12 }, (_, i) => ({
  id: `cert-${i + 1}`,
  organization_id: "org_default_01",
  certificate_number: `CERT-2026-${String(3241 - i).padStart(6, "0")}`,
  verification_code: `VC-${(i * 1337 + 1000).toString(36).toUpperCase()}`,
  status: (i % 7 === 0 ? "revoked" : "active") as CertificateStatus,
  recipient_name: [
    "Atul Kumar",
    "Priya Sharma",
    "Rahul Singh",
    "Ananya Verma",
    "Dev Patel",
    "Sneha Nair",
    "Arjun Mehta",
    "Kavya Reddy",
    "Vikram Joshi",
    "Pooja Gupta",
    "Aditya Choudhary",
    "Lakshmi Iyer",
  ][i],
  recipient_email: `user${i + 1}@example.com`,
  program_name: [
    "ML Workshop",
    "AI Bootcamp",
    "DevOps Fundamentals",
    "Python Mastery",
    "Cloud Architecture",
    "Data Science 101",
  ][i % 6],
  issue_date: "September 28, 2026",
  template_name: "Academic Honors Certificate",
  template_id: "tmpl-001",
  sha256_hash: `sha256:${(i * 987654321).toString(16).padEnd(64, "a")}`,
  created_at: "2026-09-28T12:00:00.000Z",
  updated_at: "2026-09-28T12:00:00.000Z",
}));

export default function CertificatesPage() {
  const [filter, setFilter] = useState<CertificateStatus | "all">("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [activeCert, setActiveCert] = useState<Certificate | null>(null);
  const [revokeTarget, setRevokeTarget] = useState<Certificate | null>(null);

  const [demoLoaded, setDemoLoaded] = useState(true);

  // TanStack Query for certificates list
  const {
    data: certsData,
    isLoading,
    isRefetching,
    refetch,
  } = useCertificates({
    status: filter === "all" ? undefined : filter,
    search: search || undefined,
  });

  const revokeMutation = useRevokeCertificate();
  const restoreMutation = useRestoreCertificate();

  const certificates: Certificate[] =
    (certsData as any)?.items ||
    (Array.isArray(certsData) && certsData.length > 0 ? certsData : (demoLoaded ? DEMO_CERTS : []));

  const filteredCerts = certificates.filter((c) => {
    if (filter !== "all" && c.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        c.recipient_name.toLowerCase().includes(q) ||
        (c.recipient_email || "").toLowerCase().includes(q) ||
        (c.certificate_number || "").toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleToggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleToggleSelectAll = () => {
    if (selected.size === filteredCerts.length) setSelected(new Set());
    else setSelected(new Set(filteredCerts.map((c) => c.id)));
  };

  const handleRevokeConfirm = async (id: string, reason: string) => {
    try {
      await revokeMutation.mutateAsync({ id, reason });
      setRevokeTarget(null);
    } catch {
      setRevokeTarget(null);
    }
  };

  const handleRestore = async (cert: Certificate) => {
    try {
      await restoreMutation.mutateAsync(cert.id);
    } catch {
      // Optimistic
    }
  };

  // Keyboard shortcut: Esc to clear selection
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && selected.size > 0) {
        setSelected(new Set());
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selected.size]);

  // Export selected certificates to CSV
  const handleExportSelectedCSV = () => {
    const targetCerts = certificates.filter((c) => selected.has(c.id));
    if (targetCerts.length === 0) return;

    const headers = ["Certificate Number", "Recipient Name", "Recipient Email", "Program", "Status", "Issue Date", "SHA-256 Hash"];
    const rows = targetCerts.map((c) => [
      `"${c.certificate_number || c.id}"`,
      `"${c.recipient_name}"`,
      `"${c.recipient_email || ""}"`,
      `"${c.program_name || ""}"`,
      `"${c.status}"`,
      `"${c.issue_date || ""}"`,
      `"${c.sha256_hash || ""}"`,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `certiflow-export-${targetCerts.length}-certs.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleBulkRevoke = () => {
    if (selected.size === 0) return;
    const firstSelected = certificates.find((c) => selected.has(c.id) && c.status === "active");
    if (firstSelected) {
      setRevokeTarget(firstSelected);
    }
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto pb-24">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">
            Certificate Vault
          </h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">
            Search, inspect, export, and revoke cryptographic credentials across all issued batches.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Link href="/app/issuance?create=1">
            <Button className="flex items-center gap-1.5">
              <Plus className="w-4 h-4" />
              Issue Certificates
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <CertificateFilters
        currentStatus={filter}
        onStatusChange={setFilter}
        search={search}
        onSearchChange={setSearch}
        totalCount={filteredCerts.length}
      />

      {/* Certificate Table Container */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading certificate records…</div>
        ) : filteredCerts.length === 0 ? (
          search || filter !== "all" ? (
            /* Scoped Search Filter Empty State */
            <div className="p-16 text-center max-w-md mx-auto">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200">
                <Award className="w-6 h-6" />
              </div>
              <h3 className="text-[16px] font-bold text-[var(--color-text)]">No matching certificates</h3>
              <p className="text-[13px] text-[var(--color-text-secondary)] mt-1.5 mb-6">
                No credentials found matching &quot;{search || filter}&quot;. Try adjusting your search term or clearing your status filter.
              </p>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setSearch("");
                  setFilter("all");
                }}
              >
                Clear Search & Filters
              </Button>
            </div>
          ) : (
            /* Total Empty State for First-Time Users */
            <div className="p-16 text-center max-w-md mx-auto">
              <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center mx-auto mb-4 border border-indigo-100 shadow-xs">
                <Award className="w-7 h-7" />
              </div>
              <h3 className="text-[18px] font-bold text-[var(--color-text)]">Welcome to your Certificate Vault</h3>
              <p className="text-[13px] text-[var(--color-text-secondary)] mt-2 mb-6 leading-relaxed">
                You haven&apos;t generated any certificates yet. Load sample demo records to test the table, or jump straight into the issuance wizard.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setDemoLoaded(true)}
                  className="w-full sm:w-auto"
                >
                  Load 12 Sample Records
                </Button>
                <Link href="/app/issuance?create=1" className="w-full sm:w-auto">
                  <Button size="sm" className="w-full">
                    <Plus className="w-3.5 h-3.5 mr-1.5" />
                    Issue First Batch
                  </Button>
                </Link>
              </div>
            </div>
          )
        ) : (
          <CertificateTable
            certificates={filteredCerts}
            selected={selected}
            onToggleSelect={handleToggleSelect}
            onToggleSelectAll={handleToggleSelectAll}
            onRevoke={(c) => setRevokeTarget(c)}
            onRestore={handleRestore}
            onSelectRow={(c) => setActiveCert(c)}
          />
        )}
      </div>

      {/* Floating Bulk Action Bar */}
      {selected.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-[var(--color-text)] text-white px-5 py-3 rounded-2xl shadow-2xl border border-gray-800 flex items-center gap-4 animate-in fade-in slide-in-from-bottom-4 duration-200">
          <span className="text-[13px] font-semibold text-gray-300">
            <span className="text-white font-bold">{selected.size}</span> certificate{selected.size > 1 ? "s" : ""} selected
          </span>
          <div className="h-4 w-px bg-gray-700" />
          <Button
            size="sm"
            variant="secondary"
            className="h-8 text-[12px] bg-white text-gray-900 hover:bg-gray-100 flex items-center gap-1.5 font-semibold"
            onClick={handleExportSelectedCSV}
          >
            <Download className="w-3.5 h-3.5" />
            Export Selected (CSV)
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="h-8 text-[12px] text-red-300 border-red-700/60 hover:bg-red-950/40 hover:text-red-200 flex items-center gap-1.5 font-semibold"
            onClick={handleBulkRevoke}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Revoke Selected
          </Button>
          <button
            onClick={() => setSelected(new Set())}
            className="text-[12px] text-gray-400 hover:text-white underline ml-1"
          >
            Clear (Esc)
          </button>
        </div>
      )}

      {/* Detail Drawer */}
      <CertificateDetailDrawer
        certificate={activeCert}
        isOpen={Boolean(activeCert)}
        onClose={() => setActiveCert(null)}
        onRevoke={(c) => {
          setActiveCert(null);
          setRevokeTarget(c);
        }}
      />

      {/* Revoke Modal */}
      <CertificateRevokeModal
        certificate={revokeTarget}
        isOpen={Boolean(revokeTarget)}
        onClose={() => setRevokeTarget(null)}
        onConfirm={handleRevokeConfirm}
        loading={revokeMutation.isPending}
      />
    </div>
  );
}
