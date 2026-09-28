"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  Search,
  Filter,
  Download,
  Copy,
  Check,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Eye,
  FileArchive,
  ArrowLeft,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";

interface CertificateItem {
  id: string;
  name: string;
  email: string;
  project: string;
  projectId: string;
  issueDate: string;
  status: "verified" | "revoked" | "pending";
  hash: string;
}

const INITIAL_CERTIFICATES: CertificateItem[] = [
  {
    id: "CERT-AF72K9",
    name: "Atul Kumar",
    email: "atul.kumar@certiflow.io",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "a4f89c72e3b1...d8a2",
  },
  {
    id: "CERT-BM81L2",
    name: "Rahul Sharma",
    email: "rahul.s@ai-initiative.org",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "e7b14c99d2f0...3a1c",
  },
  {
    id: "CERT-CX93M4",
    name: "Priya Singh",
    email: "priya.singh@techcorp.in",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "99c2d1b84f3e...c410",
  },
  {
    id: "CERT-DY04N5",
    name: "Dr. Vikramaditya Chandrasekharan",
    email: "v.c@stanford.edu",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "31d99e4b7c2a...f902",
  },
  {
    id: "CERT-EZ15P6",
    name: "Sneha Patel",
    email: "sneha.patel@globaltech.com",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "f4a10c883e2d...01bb",
  },
  {
    id: "CERT-FA26Q7",
    name: "Aanya Sharma",
    email: "aanya.sharma@research.edu",
    project: "AI Workshop 2026",
    projectId: "proj-ai-2026",
    issueDate: "Sep 28, 2026",
    status: "verified",
    hash: "55e21a774b99...a8f4",
  },
  {
    id: "CERT-GB37R8",
    name: "Marcus Vance",
    email: "marcus.v@devcon.com",
    project: "DevCon Global Hackathon",
    projectId: "proj-devcon",
    issueDate: "Sep 24, 2026",
    status: "verified",
    hash: "b8c33f1190de...e271",
  },
  {
    id: "CERT-REV001",
    name: "Arthur Pendelton (Duplicate Test)",
    email: "test.revoked@sample.com",
    project: "DevCon Global Hackathon",
    projectId: "proj-devcon",
    issueDate: "Sep 20, 2026",
    status: "revoked",
    hash: "000000000000...0000",
  },
];

export default function CertificatesLibraryPage() {
  const [certs, setCerts] = useState<CertificateItem[]>(INITIAL_CERTIFICATES);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "verified" | "revoked">("all");
  const [projectFilter, setProjectFilter] = useState("all");
  const [selectedCert, setSelectedCert] = useState<CertificateItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyLink = (id: string) => {
    const url = `${window.location.origin}/verify/${id}`;
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleToggleRevoke = (id: string) => {
    setCerts((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, status: c.status === "verified" ? "revoked" : "verified" }
          : c
      )
    );
  };

  const filteredCerts = certs.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "all" ? true : c.status === statusFilter;

    const matchesProject =
      projectFilter === "all" ? true : c.project === projectFilter;

    return matchesSearch && matchesStatus && matchesProject;
  });

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/app" className="font-bold flex items-center gap-2 text-[15px]">
              <span className="text-[var(--color-primary)]">✦</span> CERTIFLOW
            </Link>
            <div className="h-4 w-px bg-gray-200" />
            <span className="text-[13px] font-medium text-gray-500">
              Credential Vault & Public Registry
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" asChild>
              <Link href="/app">
                <ArrowLeft className="w-3.5 h-3.5 mr-1" />
                Back to Projects
              </Link>
            </Button>
            <Button size="sm">
              <Download className="w-3.5 h-3.5 mr-1" />
              Export Full Ledger CSV
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-6">
        {/* Title and Telemetry */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-[24px] font-bold text-[var(--color-text)]">
              Issued Credential Vault
            </h1>
            <p className="text-[13px] text-gray-500 mt-0.5">
              Search, verify, download, or revoke credentials issued across all active projects.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[12px] bg-white border border-[var(--color-border)] px-3 py-1.5 rounded-lg font-mono text-gray-700">
              Total Issued: <strong>{certs.length}</strong>
            </span>
            <span className="text-[12px] bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg font-mono text-emerald-800">
              Verified: <strong>{certs.filter((c) => c.status === "verified").length}</strong>
            </span>
          </div>
        </div>

        {/* Filters and Search Bar */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-4 shadow-2xs flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Search Input */}
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by recipient name, email, or CERT-ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-[13px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl focus:outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto">
            <div className="flex bg-gray-100 p-0.5 rounded-lg text-[12px]">
              <button
                onClick={() => setStatusFilter("all")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  statusFilter === "all" ? "bg-white text-black shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                All ({certs.length})
              </button>
              <button
                onClick={() => setStatusFilter("verified")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  statusFilter === "verified" ? "bg-white text-emerald-700 shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                Verified
              </button>
              <button
                onClick={() => setStatusFilter("revoked")}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  statusFilter === "revoked" ? "bg-white text-red-600 shadow-2xs font-semibold" : "text-gray-600"
                }`}
              >
                Revoked
              </button>
            </div>

            {/* Project Filter */}
            <select
              value={projectFilter}
              onChange={(e) => setProjectFilter(e.target.value)}
              className="text-[12px] bg-white border border-[var(--color-border)] rounded-lg px-2.5 py-1.5 text-gray-700"
            >
              <option value="all">All Projects</option>
              <option value="AI Workshop 2026">AI Workshop 2026</option>
              <option value="DevCon Global Hackathon">DevCon Global Hackathon</option>
            </select>
          </div>
        </div>

        {/* Credentials Table */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-2xs overflow-hidden">
          <div className="overflow-x-auto text-[13px]">
            <table className="w-full text-left">
              <thead className="bg-[var(--color-background)] border-b border-[var(--color-border)] text-gray-500 font-semibold text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="p-4">Recipient</th>
                  <th className="p-4">Certificate ID</th>
                  <th className="p-4">Project</th>
                  <th className="p-4">Date Issued</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]">
                {filteredCerts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-gray-400">
                      No credentials match your search criteria.
                    </td>
                  </tr>
                ) : (
                  filteredCerts.map((c) => (
                    <tr key={c.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="p-4">
                        <p className="font-bold text-gray-900">{c.name}</p>
                        <p className="text-[11px] text-gray-400 font-mono">{c.email}</p>
                      </td>

                      <td className="p-4">
                        <span className="font-mono text-[12px] bg-gray-100 text-gray-800 px-2 py-0.5 rounded font-semibold">
                          {c.id}
                        </span>
                      </td>

                      <td className="p-4">
                        <span className="font-medium text-gray-700">{c.project}</span>
                      </td>

                      <td className="p-4 text-gray-500 text-[12px]">{c.issueDate}</td>

                      <td className="p-4">
                        {c.status === "verified" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            <ShieldCheck className="w-3 h-3 text-emerald-600" />
                            Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                            <AlertTriangle className="w-3 h-3 text-red-600" />
                            Revoked
                          </span>
                        )}
                      </td>

                      <td className="p-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleCopyLink(c.id)}
                            className="p-1.5 rounded-lg border border-[var(--color-border)] hover:bg-gray-100 text-gray-600 text-[11px] flex items-center gap-1 transition-colors"
                            title="Copy Public Verification Link"
                          >
                            {copiedId === c.id ? (
                              <Check className="w-3 h-3 text-emerald-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>

                          <Link
                            href={`/verify/${c.id}`}
                            target="_blank"
                            className="p-1.5 rounded-lg border border-[var(--color-border)] hover:bg-gray-100 text-[var(--color-primary)] text-[11px] flex items-center gap-1 transition-colors"
                            title="Open Public Verification Page"
                          >
                            <ExternalLink className="w-3 h-3" />
                          </Link>

                          <Button
                            size="sm"
                            variant="secondary"
                            className="h-7 text-[11px] px-2"
                            onClick={() => setSelectedCert(c)}
                          >
                            <Eye className="w-3 h-3 mr-1" />
                            Preview
                          </Button>

                          <button
                            onClick={() => handleToggleRevoke(c.id)}
                            className={`p-1.5 rounded-lg text-[11px] font-medium border transition-colors ${
                              c.status === "verified"
                                ? "text-gray-400 hover:text-red-600 hover:border-red-200"
                                : "text-emerald-600 border-emerald-200 bg-emerald-50"
                            }`}
                            title={c.status === "verified" ? "Revoke Credential" : "Reinstate Credential"}
                          >
                            <RotateCcw className="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* CERTIFICATE PREVIEW MODAL */}
      {selectedCert && (
        <Modal
          isOpen={!!selectedCert}
          onClose={() => setSelectedCert(null)}
          title={`Certificate: ${selectedCert.name}`}
          description={`Cryptographic Hash: ${selectedCert.hash}`}
          size="lg"
        >
          <div className="space-y-4 py-2">
            {/* Visual Certificate Card */}
            <div className="aspect-[1.414/1] bg-[#FAF9F5] rounded-xl border-2 border-[#D4AF37] p-8 text-center flex flex-col justify-between relative shadow-md">
              <div className="absolute inset-2 border border-[#D4AF37]/40 pointer-events-none rounded" />
              <p className="text-[10px] uppercase font-bold tracking-widest text-[#B45309]">
                ACADEMY OF COMPUTING & SYSTEMS
              </p>
              <div>
                <h2 className="text-[26px] font-bold font-serif text-gray-900">
                  {selectedCert.name}
                </h2>
                <p className="text-[13px] text-[var(--color-primary)] font-medium mt-1">
                  {selectedCert.project} · Completed with Distinction
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-gray-200 pt-3 text-[11px] text-gray-500">
                <span>{selectedCert.issueDate}</span>
                <span className="font-mono font-bold">{selectedCert.id}</span>
                <span className="text-emerald-700 font-semibold">✓ Verified Authenticity</span>
              </div>
            </div>

            <div className="flex justify-between items-center pt-2">
              <Link
                href={`/verify/${selectedCert.id}`}
                target="_blank"
                className="text-[13px] text-[var(--color-primary)] font-semibold flex items-center gap-1 hover:underline"
              >
                Open Public Verification Page <ExternalLink className="w-3.5 h-3.5" />
              </Link>

              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setSelectedCert(null)}>
                  Close
                </Button>
                <Button>
                  <Download className="w-3.5 h-3.5 mr-1" />
                  Download PDF
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
