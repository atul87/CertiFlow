"use client";

import { use, useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Download,
  Mail,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  FileSpreadsheet,
  FileArchive,
  Layers,
  Clock,
  Play,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";

interface GeneratedCert {
  id: string;
  row: number;
  name: string;
  course: string;
  email: string;
  certificateId: string;
  status: "ready" | "processing" | "completed" | "failed";
  timeMs: number;
}

export default function BatchGenerationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  // Flight Check Status
  const [flightChecks, setFlightChecks] = useState([
    { title: "Recipient Data File", desc: "students.csv (500 rows, 0 null fields)", status: "passed" },
    { title: "Field Mappings", desc: "5 of 5 dynamic placeholders matched", status: "passed" },
    { title: "Canvas Vector Layout", desc: "A4 Landscape 3508 × 2480px @ 300 DPI verified", status: "passed" },
    { title: "Cryptographic Keys", desc: "SHA-256 tamper-proof QR signing active", status: "passed" },
  ]);

  // Generation Simulation State
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [progress, setProgress] = useState(0);
  const [processedCount, setProcessedCount] = useState(0);
  const [generatedList, setGeneratedList] = useState<GeneratedCert[]>([]);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [isSendingEmails, setIsSendingEmails] = useState(false);
  const [emailsSentCount, setEmailsSentCount] = useState(0);

  // Sample data to simulate live generation stream
  const sampleBatch: Omit<GeneratedCert, "status" | "timeMs">[] = [
    { id: "1", row: 1, name: "Atul Kumar", course: "AI Mastery 2026", email: "atul@example.com", certificateId: "CERT-AF72K9" },
    { id: "2", row: 2, name: "Rahul Sharma", course: "AI Mastery 2026", email: "rahul.s@ai-initiative.org", certificateId: "CERT-BM81L2" },
    { id: "3", row: 3, name: "Priya Singh", course: "AI Mastery 2026", email: "priya.singh@techcorp.in", certificateId: "CERT-CX93M4" },
    { id: "4", row: 4, name: "Dr. Vikramaditya Chandrasekharan", course: "AI Mastery 2026", email: "v.c@stanford.edu", certificateId: "CERT-DY04N5" },
    { id: "5", row: 5, name: "Sneha Patel", course: "AI Mastery 2026", email: "sneha.patel@globaltech.com", certificateId: "CERT-EZ15P6" },
    { id: "6", row: 6, name: "Aanya Sharma", course: "AI Mastery 2026", email: "aanya.sharma@research.edu", certificateId: "CERT-FA26Q7" },
    { id: "7", row: 7, name: "Rohan Verma", course: "AI Mastery 2026", email: "rohan.v@startup.io", certificateId: "CERT-GB37R8" },
    { id: "8", row: 8, name: "Ananya Roy", course: "AI Mastery 2026", email: "ananya.roy@design.in", certificateId: "CERT-HC48S9" },
    { id: "9", row: 9, name: "Kavita Rao", course: "AI Mastery 2026", email: "kavita.rao@institute.ac.in", certificateId: "CERT-ID59T0" },
    { id: "10", row: 10, name: "Devansh Nair", course: "AI Mastery 2026", email: "devansh.n@cloudlab.org", certificateId: "CERT-JE60U1" },
  ];

  const handleStartGeneration = () => {
    setIsGenerating(true);
    setIsFinished(false);
    setProgress(0);
    setProcessedCount(0);
    setGeneratedList([]);

    let count = 0;
    const interval = setInterval(() => {
      count += 1;
      const pct = Math.min(100, Math.round((count / sampleBatch.length) * 100));
      setProgress(pct);
      setProcessedCount(count * 50); // Simulates 50 certs per tick up to 500

      if (count <= sampleBatch.length) {
        const item = sampleBatch[count - 1];
        setGeneratedList((prev) => [
          {
            ...item,
            status: "completed",
            timeMs: Math.round(18 + Math.random() * 8),
          },
          ...prev,
        ]);
      }

      if (count >= sampleBatch.length) {
        clearInterval(interval);
        setIsGenerating(false);
        setIsFinished(true);
        setProgress(100);
        setProcessedCount(500);
      }
    }, 450);
  };

  const handleSendEmails = () => {
    setIsSendingEmails(true);
    setEmailsSentCount(0);

    let sent = 0;
    const emailInterval = setInterval(() => {
      sent += 1;
      setEmailsSentCount(sent * 50);
      if (sent >= 10) {
        clearInterval(emailInterval);
        setIsSendingEmails(false);
      }
    }, 300);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href={`/app/projects/${id || "proj-ai-2026"}`}
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="w-8 h-8 rounded-lg bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-[16px] font-bold text-[var(--color-text)]">
                  Batch Generation Engine
                </h1>
                <Badge variant={isFinished ? "success" : "primary"} className="text-[11px]">
                  {isFinished ? "500 Certificates Ready" : isGenerating ? "Compiling..." : "Ready"}
                </Badge>
              </div>
              <p className="text-[11px] text-gray-500">
                Project: AI Workshop 2026 · Batch #BCH-8820
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" asChild>
              <Link href={`/app/projects/${id || "proj-ai-2026"}/editor`}>
                Edit Template Canvas
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-8 max-w-5xl mx-auto">
        {/* SECTION 1: PRE-FLIGHT VERIFICATION CHECKS */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-[16px] font-bold text-gray-900">Pre-Flight System Check</h2>
              <p className="text-[12px] text-gray-500">
                All parameters validated before batch rendering
              </p>
            </div>
            <span className="text-[12px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Ready to Produce 500 Certificates
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {flightChecks.map((fc) => (
              <div
                key={fc.title}
                className="p-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[12px] font-bold text-gray-800">{fc.title}</span>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                </div>
                <p className="text-[11px] text-gray-500 leading-snug">{fc.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION 2: LIVE ENGINE CONSOLE */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 sm:p-8 shadow-2xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-[20px] font-bold text-gray-900">High-Throughput PDF Compiler</h2>
              <p className="text-[13px] text-gray-500 mt-0.5">
                Renders personalized print-ready vector PDFs at ~48 certs/sec with embedded cryptographic verification.
              </p>
            </div>

            {!isGenerating && !isFinished && (
              <Button size="lg" onClick={handleStartGeneration} className="h-11 px-6 shadow-md">
                <Play className="w-4 h-4 mr-2" />
                Start 500 Batch Generation
              </Button>
            )}

            {isGenerating && (
              <Button size="lg" disabled className="h-11 px-6">
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Rendering {processedCount} / 500...
              </Button>
            )}

            {isFinished && (
              <div className="flex gap-2">
                <Button size="lg" variant="secondary" onClick={handleStartGeneration} className="h-11">
                  <RefreshCw className="w-4 h-4 mr-1.5" />
                  Regenerate
                </Button>
                <Button size="lg" className="h-11 shadow-md bg-emerald-600 hover:bg-emerald-700">
                  <Download className="w-4 h-4 mr-2" />
                  Download ZIP (42.8 MB)
                </Button>
              </div>
            )}
          </div>

          {/* TELEMETRY & PROGRESS BAR */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[13px]">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-800">
                  Batch Progress: {processedCount} / 500
                </span>
                <span className="text-gray-400">·</span>
                <span className="font-mono text-gray-500">
                  {isGenerating
                    ? "Compiling vector pages & signing QR hashes..."
                    : isFinished
                    ? "Batch rendering completed in 4.2 seconds"
                    : "Awaiting execution trigger"}
                </span>
              </div>
              <span className="font-mono font-bold text-[14px] text-[var(--color-primary)]">
                {progress}%
              </span>
            </div>

            {/* Visual Progress Bar */}
            <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden p-0.5 border border-gray-200">
              <div
                className="h-full bg-[var(--color-primary)] rounded-full transition-all duration-300 relative"
                style={{ width: `${progress}%` }}
              >
                {isGenerating && (
                  <div className="absolute inset-0 bg-white/30 animate-pulse rounded-full" />
                )}
              </div>
            </div>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-[12px]">
              <div className="p-3 rounded-xl bg-gray-50 border border-gray-200">
                <span className="text-gray-500 block text-[10px] uppercase font-bold">Throughput</span>
                <span className="font-mono font-bold text-gray-800 text-[14px]">
                  {isGenerating ? "48.2 certs/s" : isFinished ? "47.6 certs/s avg" : "0 certs/s"}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 border border-gray-200">
                <span className="text-gray-500 block text-[10px] uppercase font-bold">Failed Rows</span>
                <span className="font-mono font-bold text-emerald-600 text-[14px]">0 (100% Valid)</span>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 border border-gray-200">
                <span className="text-gray-500 block text-[10px] uppercase font-bold">PDF Format</span>
                <span className="font-mono font-bold text-gray-800 text-[14px]">Vector PDF (300 DPI)</span>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 border border-gray-200">
                <span className="text-gray-500 block text-[10px] uppercase font-bold">ZIP Size</span>
                <span className="font-mono font-bold text-gray-800 text-[14px]">42.8 MB</span>
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 3: POST-GENERATION ACTIONS & DISPATCH (When finished) */}
        {isFinished && (
          <div className="p-6 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-[16px] font-bold text-emerald-950">
                  500 Certificates Successfully Generated
                </h3>
                <p className="text-[13px] text-emerald-800">
                  Ready to download ZIP, export recipient verification ledger, or trigger direct email delivery.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Button
                variant="secondary"
                size="sm"
                className="bg-white hover:bg-emerald-100/50 border-emerald-300 text-emerald-900"
                onClick={() => setEmailModalOpen(true)}
              >
                <Mail className="w-4 h-4 mr-1.5 text-emerald-700" />
                Dispatch Emails
              </Button>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                <FileArchive className="w-4 h-4 mr-1.5" />
                Download All ZIP
              </Button>
            </div>
          </div>
        )}

        {/* SECTION 4: LIVE RENDERED CERTIFICATES STREAM */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-[16px] font-bold text-gray-900">
                Live Certificate Stream
              </h3>
              <p className="text-[12px] text-gray-500">
                Real-time feed of certificates compiled with individual verification hashes
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-500">
              Showing {generatedList.length} of 500 records
            </span>
          </div>

          {generatedList.length === 0 ? (
            <div className="py-12 text-center text-gray-400 space-y-2">
              <Clock className="w-8 h-8 mx-auto text-gray-300 animate-pulse" />
              <p className="text-[13px] font-medium text-gray-600">No certificates generated yet</p>
              <p className="text-[12px] text-gray-400">
                Click &quot;Start 500 Batch Generation&quot; above to watch the compiler in action.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-[var(--color-border)]">
              {generatedList.map((cert) => (
                <div
                  key={cert.id}
                  className="py-3.5 flex items-center justify-between gap-4 hover:bg-gray-50/80 px-2 rounded-xl transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-[11px] shrink-0">
                      ✓
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[14px] text-gray-900">{cert.name}</span>
                        <span className="text-[11px] font-mono bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                          {cert.certificateId}
                        </span>
                      </div>
                      <p className="text-[12px] text-gray-500">{cert.email} · {cert.course}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-[11px] font-mono text-gray-400">
                      Rendered in {cert.timeMs}ms
                    </span>
                    <Link
                      href={`/verify/${cert.certificateId}`}
                      target="_blank"
                      className="text-[12px] text-[var(--color-primary)] font-semibold flex items-center gap-1 hover:underline"
                    >
                      Verify <ExternalLink className="w-3 h-3" />
                    </Link>
                    <Button size="sm" variant="secondary" className="h-7 text-[11px] px-2.5">
                      <Download className="w-3 h-3 mr-1" />
                      PDF
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* EMAIL DELIVERY DISPATCH MODAL */}
      <Modal
        isOpen={emailModalOpen}
        onClose={() => setEmailModalOpen(false)}
        title="Dispatch Certificate Emails"
        description="Deliver personalized PDFs and verification links directly to recipient inboxes."
        size="md"
      >
        <div className="space-y-4 py-2 text-[13px]">
          <div>
            <label className="block text-[12px] font-semibold text-gray-700 mb-1">
              Email Subject Line
            </label>
            <input
              type="text"
              defaultValue="Your Certificate for AI Workshop 2026 is ready!"
              className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] text-[13px]"
            />
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-gray-700 mb-1">
              Sender Name & Address
            </label>
            <input
              type="text"
              defaultValue="CertiFlow Issuance <credentials@certiflow.io>"
              disabled
              className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-gray-50 text-[12px] font-mono text-gray-500"
            />
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-gray-700 mb-1">
              Email Body Template
            </label>
            <textarea
              rows={4}
              defaultValue={`Hi {{NAME}},

Congratulations on completing {{COURSE}}! Attached is your official digital certificate.

You can also view and verify your credential publicly anytime at:
https://certiflow.app/verify/{{CERTIFICATE_ID}}`}
              className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] text-[12px] font-mono leading-relaxed"
            />
          </div>

          {isSendingEmails && (
            <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 space-y-1.5">
              <div className="flex justify-between text-[12px] font-semibold">
                <span>Dispatching SMTP emails...</span>
                <span>{emailsSentCount} / 500 sent</span>
              </div>
              <div className="w-full h-2 bg-indigo-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--color-primary)] rounded-full transition-all duration-300"
                  style={{ width: `${(emailsSentCount / 500) * 100}%` }}
                />
              </div>
            </div>
          )}

          {emailsSentCount === 500 && !isSendingEmails && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[12px] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>All 500 emails successfully dispatched to recipients!</span>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
            <Button variant="secondary" onClick={() => setEmailModalOpen(false)}>
              Close
            </Button>
            <Button onClick={handleSendEmails} disabled={isSendingEmails || emailsSentCount === 500}>
              {isSendingEmails ? "Sending..." : "Send to All 500 Recipients"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
