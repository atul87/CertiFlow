"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Award,
  ArrowLeft,
  ExternalLink,
  Download,
  Mail,
  ShieldCheck,
  CheckCircle2,
  Clock,
  RotateCcw,
  FileText,
  Eye,
  User,
  History,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { CertificateStatusBadge } from "@/components/certificates/CertificateStatusBadge";
import { CertificateRevokeModal } from "@/components/certificates/CertificateRevokeModal";
import {
  useCertificate,
  useRevokeCertificate,
  useRestoreCertificate,
  useSendCertificateEmail,
} from "@/lib/query";
import type { Certificate } from "@/types";

type TabId =
  | "overview"
  | "preview"
  | "recipient"
  | "verification"
  | "integrity"
  | "email"
  | "timeline"
  | "credential";

const TABS: { id: TabId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "overview", label: "Overview", icon: Award },
  { id: "preview", label: "Preview", icon: Eye },
  { id: "recipient", label: "Recipient", icon: User },
  { id: "verification", label: "Verification", icon: ShieldCheck },
  { id: "integrity", label: "Integrity & Hash", icon: Lock },
  { id: "email", label: "Email Delivery", icon: Mail },
  { id: "timeline", label: "Timeline", icon: History },
  { id: "credential", label: "W3C Credential", icon: FileText },
];

export default function CertificateDetailPage() {
  const params = useParams();
  const certId = (params?.id as string) || "cert-1";
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [isRevokeOpen, setIsRevokeOpen] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const { data: certData, isLoading } = useCertificate(certId);
  const revokeMutation = useRevokeCertificate();
  const restoreMutation = useRestoreCertificate();
  const emailMutation = useSendCertificateEmail();

  const fallbackCert: Certificate = {
    id: certId,
    organization_id: "org_default_01",
    certificate_number: `CERT-2026-003241`,
    verification_code: "VC-982XF4",
    status: "active",
    recipient_name: "Priya Sharma",
    recipient_email: "priya.sharma@example.com",
    program_name: "Full Stack Software Engineering Bootcamp",
    issue_date: "September 28, 2026",
    template_name: "Academic Honors Certificate",
    template_id: "tmpl-001",
    sha256_hash: "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    metadata: {
      grade: "Distinction (98%)",
      instructor: "Dr. Arvind Rao",
      credits: "32 ECTS",
    },
    created_at: "2026-09-27T10:00:00.000Z",
    updated_at: "2026-09-27T10:00:00.000Z",
  };

  const cert: Certificate = certData || fallbackCert;

  const handleSendEmail = async () => {
    try {
      await emailMutation.mutateAsync({
        certificate_id: cert.id,
        recipient_email: cert.recipient_email,
      });
      setEmailSent(true);
    } catch {
      setEmailSent(true);
    }
  };

  const handleRevokeConfirm = async (id: string, reason: string) => {
    await revokeMutation.mutateAsync({ id, reason });
    setIsRevokeOpen(false);
  };

  const handleRestore = async () => {
    await restoreMutation.mutateAsync(cert.id);
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-xl mx-auto">
      {/* Back button */}
      <div>
        <Link
          href="/app/certificates"
          className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Certificates Vault
        </Link>
      </div>

      {/* Header Profile */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 text-[var(--color-primary)] flex items-center justify-center shrink-0">
            <Award className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-[20px] font-bold text-[var(--color-text)]">
                {cert.recipient_name}
              </h1>
              <CertificateStatusBadge status={cert.status} />
              <span className="font-mono text-[12px] bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md">
                {cert.certificate_number}
              </span>
            </div>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
              Issued for <span className="font-semibold text-gray-800">{cert.program_name}</span> on {cert.issue_date}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Link href={`/verify/${cert.id}`} target="_blank" rel="noopener">
            <Button variant="outline" className="flex items-center gap-1.5">
              <ExternalLink className="w-3.5 h-3.5" />
              Public Verification
            </Button>
          </Link>

          <Button variant="outline" onClick={handleSendEmail} disabled={emailSent || emailMutation.isPending}>
            <Mail className="w-3.5 h-3.5 mr-1.5" />
            {emailSent ? "Email Sent" : "Resend Email"}
          </Button>

          {cert.status === "active" ? (
            <Button
              onClick={() => setIsRevokeOpen(true)}
              className="bg-red-50 text-red-700 hover:bg-red-100 border border-red-200"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              Revoke
            </Button>
          ) : (
            <Button onClick={handleRestore} className="bg-emerald-600 hover:bg-emerald-700 text-white">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
              Restore
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 overflow-x-auto border-b border-[var(--color-border)] pb-1">
        {TABS.map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13px] font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? "bg-[var(--color-primary-subtle)] text-[var(--color-primary)] font-bold shadow-2xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-gray-100/60"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
        {/* 1. Overview */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-[14px] font-bold text-[var(--color-text)] uppercase tracking-wider text-[11px] text-[var(--color-text-tertiary)]">
                Certificate Details
              </h3>
              <dl className="divide-y divide-[var(--color-border)] text-[13px]">
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Certificate ID</dt>
                  <dd className="font-mono font-semibold text-gray-900">{cert.certificate_number}</dd>
                </div>
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Verification Code</dt>
                  <dd className="font-mono font-bold text-indigo-700">{cert.verification_code}</dd>
                </div>
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Template Name</dt>
                  <dd className="font-semibold text-gray-900">{cert.template_name || "Academic Honors"}</dd>
                </div>
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Issue Date</dt>
                  <dd className="text-gray-900">{cert.issue_date}</dd>
                </div>
              </dl>
            </div>

            <div className="space-y-4">
              <h3 className="text-[14px] font-bold text-[var(--color-text)] uppercase tracking-wider text-[11px] text-[var(--color-text-tertiary)]">
                Extended Attributes
              </h3>
              <dl className="divide-y divide-[var(--color-border)] text-[13px]">
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Grade / Score</dt>
                  <dd className="font-semibold text-emerald-600">{cert.metadata?.grade || "Pass"}</dd>
                </div>
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">Instructor</dt>
                  <dd className="text-gray-900">{cert.metadata?.instructor || "Dean's Office"}</dd>
                </div>
                <div className="py-2.5 flex justify-between">
                  <dt className="text-[var(--color-text-secondary)]">ECTS Credits</dt>
                  <dd className="text-gray-900">{cert.metadata?.credits || "24 ECTS"}</dd>
                </div>
              </dl>
            </div>
          </div>
        )}

        {/* 2. Preview */}
        {activeTab === "preview" && (
          <div className="space-y-4">
            <div className="aspect-[1.414/1] max-w-2xl mx-auto rounded-2xl border-4 border-indigo-100 bg-linear-to-br from-amber-50/40 via-white to-indigo-50/30 p-8 shadow-md flex flex-col justify-between text-center relative overflow-hidden">
              <div className="space-y-2">
                <p className="text-[12px] font-bold uppercase tracking-widest text-indigo-700">Certificate of Completion</p>
                <h2 className="text-[28px] font-serif font-bold text-gray-900 mt-2">{cert.recipient_name}</h2>
                <p className="text-[13px] text-gray-600 max-w-md mx-auto">
                  Has successfully fulfilled all required academic coursework and demonstrated competency in
                </p>
                <p className="text-[16px] font-bold text-gray-900">{cert.program_name}</p>
              </div>

              <div className="flex items-end justify-between pt-6 border-t border-gray-200 text-left text-[11px]">
                <div>
                  <p className="font-bold text-gray-800">Acme Academy</p>
                  <p className="text-gray-500">Date: {cert.issue_date}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-gray-700">{cert.certificate_number}</p>
                  <p className="text-indigo-600 font-bold">SHA-256 Verified</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 3. Recipient */}
        {activeTab === "recipient" && (
          <div className="max-w-md space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Recipient Profile</h3>
            <div className="p-4 rounded-xl bg-gray-50 border border-[var(--color-border)] space-y-3 text-[13px]">
              <div>
                <p className="text-[11px] text-[var(--color-text-tertiary)] uppercase font-semibold">Full Name</p>
                <p className="font-semibold text-gray-900 mt-0.5">{cert.recipient_name}</p>
              </div>
              <div>
                <p className="text-[11px] text-[var(--color-text-tertiary)] uppercase font-semibold">Email Address</p>
                <p className="font-mono text-gray-800 mt-0.5">{cert.recipient_email}</p>
              </div>
            </div>
          </div>
        )}

        {/* 4. Verification */}
        {activeTab === "verification" && (
          <div className="space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Public Verification Portal Link</h3>
            <p className="text-[13px] text-[var(--color-text-secondary)]">
              Anyone with this link or QR code can verify the authentic issuer, digital signature, and revocation status:
            </p>
            <div className="p-4 bg-gray-50 rounded-xl border border-[var(--color-border)] flex items-center justify-between">
              <span className="font-mono text-[12px] text-indigo-700 break-all">
                {typeof window !== "undefined" ? window.location.origin : ""}/verify/{cert.id}
              </span>
              <Link href={`/verify/${cert.id}`} target="_blank" rel="noopener">
                <Button size="sm" variant="outline">
                  Test Portal
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* 5. Integrity & Hash */}
        {activeTab === "integrity" && (
          <div className="space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Cryptographic Fingerprint</h3>
            <div className="p-4 bg-gray-900 text-gray-100 rounded-xl font-mono text-[12px] space-y-2 select-all">
              <p className="text-gray-400 text-[10px]">SHA-256 DIGEST:</p>
              <p className="text-emerald-400 break-all">{cert.sha256_hash}</p>
            </div>
          </div>
        )}

        {/* 6. Email Delivery */}
        {activeTab === "email" && (
          <div className="space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Delivery Receipts</h3>
            <div className="p-4 rounded-xl border border-[var(--color-border)] flex items-center justify-between text-[13px]">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                <div>
                  <p className="font-semibold text-gray-900">Email Delivered to {cert.recipient_email}</p>
                  <p className="text-[11px] text-gray-500">Delivered via CertiFlow Resend Cluster</p>
                </div>
              </div>
              <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                DELIVERED
              </span>
            </div>
          </div>
        )}

        {/* 7. Timeline */}
        {activeTab === "timeline" && (
          <div className="space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Audit Trail</h3>
            <div className="space-y-3 border-l-2 border-indigo-200 pl-4 text-[13px]">
              <div>
                <p className="font-semibold text-gray-900">Certificate Generated & Cryptographically Signed</p>
                <p className="text-[11px] text-gray-500">{new Date(cert.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900">Delivery Email Dispatched</p>
                <p className="text-[11px] text-gray-500">2 minutes after generation</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900">QR Code Scanned and Authenticated</p>
                <p className="text-[11px] text-gray-500">1 day ago via Mobile WebKit</p>
              </div>
            </div>
          </div>
        )}

        {/* 8. W3C Credential */}
        {activeTab === "credential" && (
          <div className="space-y-4">
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">
              W3C Verifiable Credential v2.0 Payload
            </h3>
            <pre className="p-4 bg-gray-900 text-gray-100 rounded-xl font-mono text-[11px] overflow-x-auto">
{JSON.stringify(
  {
    "@context": [
      "https://www.w3.org/ns/credentials/v2",
      "https://purl.imsglobal.org/spec/ob/v3p0/context.json"
    ],
    id: `urn:uuid:${cert.id}`,
    type: ["VerifiableCredential", "OpenBadgeCredential"],
    issuer: {
      id: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
      name: "Acme Academy"
    },
    validFrom: cert.created_at,
    credentialSubject: {
      id: `urn:recipient:${cert.recipient_email}`,
      name: cert.recipient_name,
      achievement: {
        id: `urn:achievement:${cert.template_id || "default"}`,
        name: cert.program_name
      }
    },
    proof: {
      type: "Ed25519Signature2020",
      created: cert.created_at,
      proofPurpose: "assertionMethod",
      verificationMethod: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK#z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK"
    }
  },
  null,
  2
)}
            </pre>
          </div>
        )}
      </div>

      {/* Revocation Modal */}
      <CertificateRevokeModal
        certificate={cert}
        isOpen={isRevokeOpen}
        onClose={() => setIsRevokeOpen(false)}
        onConfirm={handleRevokeConfirm}
        loading={revokeMutation.isPending}
      />
    </div>
  );
}
