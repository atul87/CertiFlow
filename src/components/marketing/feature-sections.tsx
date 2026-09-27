"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Layers,
  MousePointerClick,
  Type,
  Maximize2,
  QrCode,
  ShieldCheck,
  Send,
  Download,
  ArrowRight,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Mail,
  FileCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 1: Bulk Generation
   Layout: Text Left / Visual Right
   ───────────────────────────────────────────── */
export function FeatureBulk() {
  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-[#FAFAF8]">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Text (Left 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 01 · Bulk Generation
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              One spreadsheet. <br className="hidden sm:inline" />
              Hundreds of certificates.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Stop opening the same certificate 500 times. Upload your recipient list once and let CertiFlow generate every personalized certificate automatically.
            </p>
            <Link
              href="/#demo"
              className="inline-flex items-center gap-1.5 text-[14px] font-semibold text-[var(--color-primary)] hover:underline"
            >
              See how it works <ArrowRight className="w-4 h-4 ml-0.5" />
            </Link>
          </div>

          {/* Visual (Right 50%) */}
          <div className="lg:col-span-6 w-full">
            <div className="rounded-2xl border border-[var(--color-border)] bg-white p-6 sm:p-7 shadow-sm">
              <div className="flex items-center justify-between pb-4 border-b border-[var(--color-border)] mb-5 text-[12px]">
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  <span className="font-mono font-medium">students_2026.csv</span>
                </div>
                <span className="font-mono text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded">
                  500 rows loaded
                </span>
              </div>

              {/* Engine Flow Diagram */}
              <div className="space-y-3 font-mono text-[12px]">
                <div className="p-3 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex justify-between items-center">
                  <span>Atul Kumar · AI Workshop</span>
                  <span className="text-emerald-600 font-semibold">Row #001</span>
                </div>
                <div className="p-3 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex justify-between items-center">
                  <span>Rahul Sharma · AI Workshop</span>
                  <span className="text-emerald-600 font-semibold">Row #002</span>
                </div>
                <div className="p-3 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex justify-between items-center">
                  <span>Priya Singh · AI Workshop</span>
                  <span className="text-emerald-600 font-semibold">Row #003</span>
                </div>

                <div className="py-2 text-center text-gray-400 font-sans text-[12px]">
                  ↓ Processed via Parallel Rendering Engine ↓
                </div>

                <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-200 text-center">
                  <p className="text-[13px] font-bold text-[var(--color-primary)] font-sans">
                    ✓ 500 Individual Vector PDFs Generated (84 MB ZIP)
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 2: Visual Certificate Editor
   Layout: Visual Left / Text Right
   ───────────────────────────────────────────── */
export function FeatureEditor() {
  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-white">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Visual (Left 50%) */}
          <div className="lg:col-span-6 w-full order-2 lg:order-1">
            <div className="rounded-2xl border border-[var(--color-border)] bg-[#FAFAF8] overflow-hidden shadow-sm">
              {/* Editor Bar */}
              <div className="px-4 py-2.5 bg-white border-b border-[var(--color-border)] flex items-center justify-between text-[11px] font-medium">
                <span className="text-[var(--color-text)] font-semibold">Studio Canvas · 3508 × 2480px</span>
                <span className="text-[var(--color-primary)] bg-indigo-50 px-2 py-0.5 rounded font-mono">100% Zoom</span>
              </div>

              <div className="grid grid-cols-12 min-h-[260px]">
                {/* Tools Sidebar */}
                <div className="col-span-3 border-r border-[var(--color-border)] bg-white p-3 space-y-1 text-[12px]">
                  <p className="text-[9px] uppercase font-bold text-gray-400 px-2 py-1">Tools</p>
                  <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-[var(--color-background)] font-medium text-[var(--color-primary)]">
                    <Type className="w-3.5 h-3.5" />
                    Text
                  </div>
                  <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-gray-600">
                    <MousePointerClick className="w-3.5 h-3.5" />
                    Fields
                  </div>
                  <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-gray-600">
                    <QrCode className="w-3.5 h-3.5" />
                    QR
                  </div>
                </div>

                {/* Canvas Area */}
                <div className="col-span-9 p-6 flex items-center justify-center relative">
                  <div className="w-full max-w-[280px] aspect-[1.4/1] bg-white rounded-lg border-2 border-[var(--color-border)] shadow-xs p-5 flex flex-col justify-between text-center relative">
                    <p className="text-[8px] uppercase tracking-widest text-gray-400">Certificate</p>

                    {/* Draggable Placeholder */}
                    <div className="border-2 border-dashed border-[var(--color-primary)] bg-indigo-50/80 rounded-md py-1 px-3 mx-auto shadow-2xs">
                      <span className="font-mono text-[12px] font-bold text-[var(--color-primary)]">
                        {"{{NAME}}"}
                      </span>
                    </div>

                    <p className="text-[8px] text-gray-400">Completion of Course</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Text (Right 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start order-1 lg:order-2">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 02 · Certificate Studio
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Design exactly where the name belongs.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Place text, dynamic variable tags, and verification QR codes with pixel precision on top of your background design. Adjust font families, weights, and alignment effortlessly.
            </p>
            <div className="flex flex-wrap gap-2 text-[12px]">
              <span className="px-3 py-1 rounded-full bg-[var(--color-background)] border border-[var(--color-border)] text-gray-700 font-medium">
                Drag & Drop Field Placement
              </span>
              <span className="px-3 py-1 rounded-full bg-[var(--color-background)] border border-[var(--color-border)] text-gray-700 font-medium">
                Custom Google Fonts
              </span>
              <span className="px-3 py-1 rounded-full bg-[var(--color-background)] border border-[var(--color-border)] text-gray-700 font-medium">
                Layer Alignment Guides
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 3: Dynamic Fields
   Layout: Text Left / Visual Right
   ───────────────────────────────────────────── */
export function FeatureDynamicFields() {
  const [activeStage, setActiveStage] = useState<"csv" | "template" | "result">("result");

  useEffect(() => {
    const cycle = setInterval(() => {
      setActiveStage((prev) => (prev === "csv" ? "template" : prev === "template" ? "result" : "csv"));
    }, 2600);
    return () => clearInterval(cycle);
  }, []);

  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-[#FAFAF8]">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Text (Left 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 03 · Variable Binding
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Your spreadsheet becomes your certificate.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Connect every column in your CSV—from full name and course title to scores and departments—into live dynamic variables that bind seamlessly to every issued certificate.
            </p>

            <div className="flex gap-2">
              <button
                onClick={() => setActiveStage("csv")}
                className={`px-3 py-1 text-[12px] rounded-lg border font-medium transition-colors ${
                  activeStage === "csv" ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]" : "bg-white text-gray-600 border-[var(--color-border)]"
                }`}
              >
                1. CSV Columns
              </button>
              <button
                onClick={() => setActiveStage("template")}
                className={`px-3 py-1 text-[12px] rounded-lg border font-medium transition-colors ${
                  activeStage === "template" ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]" : "bg-white text-gray-600 border-[var(--color-border)]"
                }`}
              >
                2. Template Tags
              </button>
              <button
                onClick={() => setActiveStage("result")}
                className={`px-3 py-1 text-[12px] rounded-lg border font-medium transition-colors ${
                  activeStage === "result" ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]" : "bg-white text-gray-600 border-[var(--color-border)]"
                }`}
              >
                3. Final Render
              </button>
            </div>
          </div>

          {/* Visual (Right 50%) */}
          <div className="lg:col-span-6 w-full">
            <div className="rounded-2xl border border-[var(--color-border)] bg-white p-6 sm:p-8 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border)] mb-4 text-[12px] font-mono">
                <span className="text-gray-500">Live Stage:</span>
                <span className="font-bold text-[var(--color-primary)] uppercase tracking-wider">
                  {activeStage === "csv" ? "Spreadsheet Ingestion" : activeStage === "template" ? "Placeholder Resolution" : "Personalized Output"}
                </span>
              </div>

              <div className="space-y-3 font-mono text-[13px]">
                {activeStage === "csv" && (
                  <div className="space-y-2">
                    <div className="p-2.5 rounded bg-gray-50 border border-gray-200 flex justify-between">
                      <span className="text-gray-500">Column 1:</span>
                      <strong className="text-gray-800">Name</strong>
                    </div>
                    <div className="p-2.5 rounded bg-gray-50 border border-gray-200 flex justify-between">
                      <span className="text-gray-500">Column 2:</span>
                      <strong className="text-gray-800">Course</strong>
                    </div>
                    <div className="p-2.5 rounded bg-gray-50 border border-gray-200 flex justify-between">
                      <span className="text-gray-500">Column 3:</span>
                      <strong className="text-gray-800">Date</strong>
                    </div>
                    <div className="p-2.5 rounded bg-gray-50 border border-gray-200 flex justify-between">
                      <span className="text-gray-500">Column 4:</span>
                      <strong className="text-gray-800">Score</strong>
                    </div>
                  </div>
                )}

                {activeStage === "template" && (
                  <div className="space-y-2">
                    <div className="p-2.5 rounded bg-indigo-50 border border-indigo-200 flex justify-between text-[var(--color-primary)] font-bold">
                      <span>Variable Tag:</span>
                      <span>{"{{NAME}}"}</span>
                    </div>
                    <div className="p-2.5 rounded bg-indigo-50 border border-indigo-200 flex justify-between text-[var(--color-primary)] font-bold">
                      <span>Variable Tag:</span>
                      <span>{"{{COURSE}}"}</span>
                    </div>
                    <div className="p-2.5 rounded bg-indigo-50 border border-indigo-200 flex justify-between text-[var(--color-primary)] font-bold">
                      <span>Variable Tag:</span>
                      <span>{"{{DATE}}"}</span>
                    </div>
                    <div className="p-2.5 rounded bg-indigo-50 border border-indigo-200 flex justify-between text-[var(--color-primary)] font-bold">
                      <span>Variable Tag:</span>
                      <span>{"{{SCORE}}"}</span>
                    </div>
                  </div>
                )}

                {activeStage === "result" && (
                  <div className="space-y-2">
                    <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 flex justify-between text-emerald-900 font-sans">
                      <span className="text-emerald-700 font-mono text-[12px]">Recipient:</span>
                      <strong>Atul Kumar</strong>
                    </div>
                    <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 flex justify-between text-emerald-900 font-sans">
                      <span className="text-emerald-700 font-mono text-[12px]">Course:</span>
                      <strong>Python Masterclass</strong>
                    </div>
                    <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 flex justify-between text-emerald-900 font-sans">
                      <span className="text-emerald-700 font-mono text-[12px]">Date:</span>
                      <strong>27 September 2026</strong>
                    </div>
                    <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 flex justify-between text-emerald-900 font-sans">
                      <span className="text-emerald-700 font-mono text-[12px]">Score:</span>
                      <strong>92% (Honors Distinction)</strong>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 4: Smart Text Fit
   Layout: Visual Left / Text Right
   ───────────────────────────────────────────── */
export function FeatureAutoFit() {
  const [currentSize, setCurrentSize] = useState<72 | 68 | 64>(64);

  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-white">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Visual (Left 50%) */}
          <div className="lg:col-span-6 w-full order-2 lg:order-1">
            <div className="rounded-2xl border border-[var(--color-border)] bg-[#FAFAF8] p-7 shadow-sm text-center">
              <div className="flex items-center justify-between text-[11px] font-mono text-gray-500 mb-4 pb-2 border-b border-[var(--color-border)]">
                <span>Text Box Container Width: 480px</span>
                <span className="text-emerald-600 font-bold">Auto-Fit: Active</span>
              </div>

              {/* Box demonstration */}
              <div className="relative border-2 border-dashed border-[var(--color-primary)]/40 rounded-xl p-6 bg-white min-h-[110px] flex items-center justify-center">
                <p
                  style={{ fontSize: `${currentSize * 0.3}px` }}
                  className="font-bold text-[var(--color-text)] font-serif whitespace-nowrap transition-all duration-300"
                >
                  Dr. Abhishek Kumar Choudhary Sharma
                </p>
              </div>

              <div className="flex items-center justify-center gap-3 mt-5">
                {[72, 68, 64].map((sz) => (
                  <button
                    key={sz}
                    onClick={() => setCurrentSize(sz as any)}
                    className={`px-3 py-1 rounded text-[12px] font-mono border transition-colors ${
                      currentSize === sz
                        ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]"
                        : "bg-white text-gray-600 border-[var(--color-border)]"
                    }`}
                  >
                    {sz}px {sz === 64 ? "✓ Perfect Fit" : "Overflowing"}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Text (Right 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start order-1 lg:order-2">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 04 · Typography Engine
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Long names? No problem.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Smart text fitting keeps names and dynamic fields looking polished—even when the data isn&apos;t. CertiFlow automatically calculates text boundaries and scales font metrics down dynamically so everything stays centered.
            </p>
            <div className="flex items-center gap-2 text-[13px] text-emerald-700 bg-emerald-50 px-3.5 py-1.5 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Zero manual adjustment across 10,000 attendee records</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 5: QR Verification
   Layout: Text Left / Visual Right
   ───────────────────────────────────────────── */
export function FeatureVerification() {
  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-[#FAFAF8]">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Text (Left 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 05 · Cryptographic Proof
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Every certificate can be verifiable.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              CertiFlow embeds an encrypted QR code and unique certificate ID on every generated document. Anyone can scan it with their phone camera to instantly confirm authentic issuance.
            </p>
            <Link
              href="/verify/CERT-2026-00042"
              className="inline-flex items-center gap-1.5 text-[14px] font-semibold text-[var(--color-primary)] hover:underline"
            >
              Explore verification page <ArrowRight className="w-4 h-4 ml-0.5" />
            </Link>
          </div>

          {/* Visual (Right 50%) */}
          <div className="lg:col-span-6 w-full">
            <div className="rounded-2xl border border-[var(--color-border)] bg-white p-6 sm:p-8 shadow-sm">
              <div className="aspect-[1.5/1] bg-[#FAFAF8] rounded-xl border border-[var(--color-border)] p-6 flex flex-col justify-between text-center relative mb-5">
                <div>
                  <p className="text-[8px] uppercase font-bold tracking-widest text-gray-400">Official Certificate</p>
                  <h4 className="text-[20px] font-bold font-serif text-[var(--color-text)] mt-1">Atul Kumar</h4>
                  <p className="text-[11px] text-[var(--color-primary)] font-medium">AI Workshop 2026</p>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-gray-200 text-[10px]">
                  <span className="text-gray-500 font-mono">CERT-2026-00042</span>
                  <div className="w-8 h-8 rounded bg-white border border-gray-300 flex items-center justify-center">
                    <QrCode className="w-5 h-5 text-gray-800" />
                  </div>
                  <span className="text-emerald-600 font-bold">✓ Signed</span>
                </div>
              </div>

              {/* 3 Step Verification Flow */}
              <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-medium pt-2 border-t border-[var(--color-border)]">
                <div className="p-2 rounded bg-gray-50">1. Scan QR</div>
                <div className="p-2 rounded bg-gray-50">2. Verify Token</div>
                <div className="p-2 rounded bg-emerald-50 text-emerald-800 font-bold">3. ✓ Valid Cert</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 6: Delivery
   Layout: Visual Left / Text Right
   ───────────────────────────────────────────── */
export function FeatureDelivery() {
  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-white">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Visual (Left 50%) */}
          <div className="lg:col-span-6 w-full order-2 lg:order-1">
            <div className="rounded-2xl border border-[var(--color-border)] bg-[#FAFAF8] p-6 sm:p-8 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border)] mb-4 text-[12px]">
                <span className="font-semibold text-gray-700">Distribution Queue</span>
                <span className="text-emerald-600 font-bold">1,000 / 1,000 Ready</span>
              </div>

              <div className="space-y-2.5 text-[12px]">
                <div className="p-3 rounded-lg bg-white border border-[var(--color-border)] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Download className="w-4 h-4 text-indigo-600" />
                    <span className="font-medium">Download Single Compressed ZIP</span>
                  </div>
                  <span className="font-mono text-gray-500">142 MB</span>
                </div>

                <div className="p-3 rounded-lg bg-white border border-[var(--color-border)] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-emerald-600" />
                    <span className="font-medium">Direct Individual PDF Exports</span>
                  </div>
                  <span className="font-mono text-gray-500">1,000 Files</span>
                </div>

                <div className="p-3 rounded-lg bg-white border border-[var(--color-border)] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-amber-600" />
                    <span className="font-medium">Automated Email Dispatch</span>
                  </div>
                  <span className="font-mono text-emerald-600 font-bold">Scheduled ✓</span>
                </div>
              </div>
            </div>
          </div>

          {/* Text (Right 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start order-1 lg:order-2">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 06 · Dispatch & Delivery
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Generate. Deliver. Done.
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Export high-resolution PDFs directly into a single compressed ZIP or send personalized emails with attached credentials to all recipients with one click.
            </p>
            <div className="space-y-2 text-[13px] text-gray-700">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Instant bulk ZIP archive with clean naming conventions</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Scheduled personalized email dispatch</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   FEATURE SHOWCASE 7: Batch Dashboard
   Layout: Text Left / Visual Right
   ───────────────────────────────────────────── */
export function FeatureBatchDashboard() {
  return (
    <section className="section-padding border-t border-[var(--color-border)] bg-[#FAFAF8]">
      <div className="container-marketing">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Text (Left 50%) */}
          <div className="lg:col-span-6 flex flex-col items-start">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-3">
              Feature 07 · Batch Telemetry
            </span>
            <h2 className="text-section text-[var(--color-text)] mb-5">
              Generation Progress
            </h2>
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-6 leading-relaxed">
              Operational visibility across every certificate. Track rendering throughput in real-time, inspect any row validation warnings, and retry individual failures without restarting the batch.
            </p>
            <div className="flex gap-3">
              <Button size="sm" variant="secondary" className="gap-1.5">
                <RotateCcw className="w-3.5 h-3.5 text-amber-600" />
                Retry Failed (3)
              </Button>
              <Button size="sm" className="gap-1.5">
                <Download className="w-3.5 h-3.5" />
                Download Batch
              </Button>
            </div>
          </div>

          {/* Visual (Right 50%) */}
          <div className="lg:col-span-6 w-full">
            <div className="rounded-2xl border border-[var(--color-border)] bg-white p-6 sm:p-8 shadow-sm space-y-5">
              <div className="flex items-center justify-between text-[13px] font-semibold">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
                  1,000 Total in Batch
                </span>
                <span className="font-mono text-[var(--color-primary)]">84.2%</span>
              </div>

              {/* Progress bar */}
              <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-[var(--color-primary)] rounded-full w-[84.2%]" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-[13px] pt-2">
                <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-700 block">
                    Successful
                  </span>
                  <span className="text-[22px] font-bold text-emerald-800 font-mono">839</span>
                </div>
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-amber-700 block">
                    Failed Validation
                  </span>
                  <span className="text-[22px] font-bold text-amber-800 font-mono">3</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
