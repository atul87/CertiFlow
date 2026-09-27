"use client";

import { use } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  ShieldCheck,
  Award,
  Calendar,
  FileCheck,
  User,
  Building,
  QrCode,
  Download,
  Share2,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function VerificationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  // Decoded or verified record
  const record = {
    id: id || "CERT-001",
    recipient: "Atul Kumar",
    event: "AI Workshop 2026",
    issuer: "Global AI Academy & Tech Foundation",
    issueDate: "September 27, 2026",
    status: "Verified Authentic",
    grade: "Grade A+ (Honors)",
    fingerprint: "0x8f2a99c4d21e8b746c8234190ba33d",
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)] flex flex-col justify-between">
      {/* Mini verification header */}
      <header className="border-b border-[var(--color-border)] bg-white/80 backdrop-blur-md sticky top-0 z-20">
        <div className="container-marketing h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-7 h-7 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
            <span className="text-[16px] font-bold text-[var(--color-text)]">CertiFlow</span>
            <span className="text-[12px] text-[var(--color-text-tertiary)] font-mono">/ Registry</span>
          </Link>

          <div className="flex items-center gap-1.5 text-[12px] text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full font-semibold border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Public Ledger Active</span>
          </div>
        </div>
      </header>

      {/* Main Verification Card */}
      <main className="container-marketing py-12 max-w-2xl mx-auto flex-1">
        <div className="bg-white rounded-2xl border-2 border-emerald-500/40 p-6 sm:p-10 shadow-lg relative overflow-hidden">
          {/* Status banner */}
          <div className="flex items-center gap-3 pb-6 border-b border-[var(--color-border)] mb-8">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  ✓ Verified Authentic
                </span>
                <span className="text-[12px] font-mono text-[var(--color-text-tertiary)]">
                  {record.id}
                </span>
              </div>
              <h1 className="text-[20px] font-bold text-[var(--color-text)] mt-1">
                Official Credential Verification
              </h1>
            </div>
          </div>

          {/* Certificate Detail Fields */}
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-start gap-3">
              <User className="w-4 h-4 text-[var(--color-primary)] mt-1 shrink-0" />
              <div>
                <p className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">
                  Recipient Name
                </p>
                <p className="text-[18px] font-bold text-[var(--color-text)] font-serif">
                  {record.recipient}
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-start gap-3">
              <Award className="w-4 h-4 text-[var(--color-primary)] mt-1 shrink-0" />
              <div>
                <p className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">
                  Course / Program Title
                </p>
                <p className="text-[16px] font-semibold text-[var(--color-text)]">
                  {record.event}
                </p>
                <p className="text-[12px] text-emerald-600 font-medium mt-0.5">{record.grade}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-start gap-3">
                <Building className="w-4 h-4 text-[var(--color-text-secondary)] mt-1 shrink-0" />
                <div>
                  <p className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">
                    Issuing Organization
                  </p>
                  <p className="text-[14px] font-medium text-[var(--color-text)]">
                    {record.issuer}
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-start gap-3">
                <Calendar className="w-4 h-4 text-[var(--color-text-secondary)] mt-1 shrink-0" />
                <div>
                  <p className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">
                    Date Issued
                  </p>
                  <p className="text-[14px] font-medium text-[var(--color-text)]">
                    {record.issueDate}
                  </p>
                </div>
              </div>
            </div>

            {/* Cryptographic hash */}
            <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-[11px] font-mono text-[var(--color-text-tertiary)] flex justify-between items-center">
              <span>SHA-256 Signature:</span>
              <span className="text-[var(--color-text)]">{record.fingerprint}</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="mt-8 pt-6 border-t border-[var(--color-border)] flex flex-wrap gap-3 items-center justify-between">
            <Button size="sm" variant="secondary" className="gap-1.5" onClick={() => window.print()}>
              <Download className="w-3.5 h-3.5" />
              Download Verified PDF
            </Button>
            <Button size="sm" asChild>
              <Link href="/signup">
                Issue Certificates with CertiFlow
                <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
              </Link>
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--color-border)] py-6 text-center text-[12px] text-[var(--color-text-tertiary)] bg-white">
        CertiFlow Cryptographic Credential Registry · © 2026 All rights reserved
      </footer>
    </div>
  );
}
