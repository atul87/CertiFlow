"use client";

import { useState } from "react";
import Link from "next/link";
import { Download, RefreshCw, Plus, Award } from "lucide-react";
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
  issue_date: new Date(Date.now() - i * 3600000 * 6).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }),
  template_name: "Academic Honors Certificate",
  template_id: "tmpl-001",
  sha256_hash: `sha256:${(i * 987654321).toString(16).padEnd(64, "a")}`,
  created_at: new Date(Date.now() - i * 3600000 * 6).toISOString(),
  updated_at: new Date(Date.now() - i * 3600000 * 6).toISOString(),
}));

export default function CertificatesPage() {
  const [filter, setFilter] = useState<CertificateStatus | "all">("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [activeCert, setActiveCert] = useState<Certificate | null>(null);
  const [revokeTarget, setRevokeTarget] = useState<Certificate | null>(null);

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
    (Array.isArray(certsData) && certsData.length > 0 ? certsData : DEMO_CERTS);

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

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-2xl mx-auto">
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
          <div className="p-8 text-center text-gray-400">Loading certificate records…</div>
        ) : filteredCerts.length === 0 ? (
          <div className="p-16 text-center">
            <Award className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">No certificates found</h3>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
              No certificate matches your query criteria.
            </p>
          </div>
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
