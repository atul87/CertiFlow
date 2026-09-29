"use client";

import Link from "next/link";
import { X, Award, ExternalLink, Download, Mail, ShieldCheck, Hash, Calendar, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CertificateStatusBadge } from "./CertificateStatusBadge";
import type { Certificate } from "@/types";

interface CertificateDetailDrawerProps {
  certificate: Certificate | null;
  isOpen: boolean;
  onClose: () => void;
  onRevoke: (cert: Certificate) => void;
}

export function CertificateDetailDrawer({
  certificate,
  isOpen,
  onClose,
  onRevoke,
}: CertificateDetailDrawerProps) {
  if (!isOpen || !certificate) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-2xs flex justify-end">
      <div className="bg-white w-full max-w-md h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-[14px] font-bold text-[var(--color-text)]">Certificate Details</h2>
              <p className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                {certificate.certificate_number || certificate.id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close drawer"
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Status & Quick Action */}
          <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-[var(--color-border)]">
            <div>
              <p className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">
                STATUS
              </p>
              <CertificateStatusBadge status={certificate.status} />
            </div>
            <Link
              href={`/verify/${certificate.id}`}
              target="_blank"
              rel="noopener"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-[var(--color-border)] text-[12px] font-semibold text-[var(--color-text)] hover:bg-gray-50 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Verify Link
            </Link>
          </div>

          {/* Recipient */}
          <div className="space-y-3">
            <h3 className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
              Recipient Information
            </h3>
            <div className="bg-white rounded-xl border border-[var(--color-border)] p-3.5 space-y-2 text-[13px]">
              <div className="flex justify-between">
                <span className="text-[var(--color-text-secondary)]">Name:</span>
                <span className="font-semibold text-[var(--color-text)]">{certificate.recipient_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-secondary)]">Email:</span>
                <span className="font-mono text-gray-700">{certificate.recipient_email}</span>
              </div>
            </div>
          </div>

          {/* Program Details */}
          <div className="space-y-3">
            <h3 className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
              Program & Credentials
            </h3>
            <div className="bg-white rounded-xl border border-[var(--color-border)] p-3.5 space-y-2 text-[13px]">
              <div className="flex justify-between">
                <span className="text-[var(--color-text-secondary)]">Program:</span>
                <span className="font-semibold text-[var(--color-text)]">{certificate.program_name || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-secondary)]">Issue Date:</span>
                <span className="text-gray-700">{certificate.issue_date || new Date(certificate.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-secondary)]">Template:</span>
                <span className="text-gray-700">{certificate.template_name || "Default Template"}</span>
              </div>
            </div>
          </div>

          {/* Cryptographic Proof */}
          <div className="space-y-3">
            <h3 className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
              Cryptographic Integrity
            </h3>
            <div className="bg-gray-50 rounded-xl border border-[var(--color-border)] p-3.5 space-y-2 text-[12px]">
              <div>
                <p className="text-[var(--color-text-tertiary)] text-[10px] font-mono">SHA-256 HASH</p>
                <p className="font-mono text-[11px] text-gray-700 break-all select-all mt-0.5">
                  {certificate.sha256_hash || "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
                </p>
              </div>
              <div>
                <p className="text-[var(--color-text-tertiary)] text-[10px] font-mono">VERIFICATION CODE</p>
                <p className="font-mono text-[11px] text-indigo-700 font-bold mt-0.5">
                  {certificate.verification_code || "VC-DEFAULT"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="p-4 border-t border-[var(--color-border)] bg-gray-50/50 flex items-center justify-between gap-2">
          <Link href={`/app/certificates/${certificate.id}`} className="flex-1">
            <Button variant="outline" className="w-full justify-center text-[12px]">
              Full Page Detail
            </Button>
          </Link>
          {certificate.status === "active" ? (
            <Button
              onClick={() => onRevoke(certificate)}
              className="bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 text-[12px]"
            >
              Revoke
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
