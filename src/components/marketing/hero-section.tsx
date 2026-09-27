"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ArrowRight, Play, FileSpreadsheet, BadgeCheck, Sparkles, Check, QrCode } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface HeroSectionProps {
  onWatchDemo?: () => void;
}

const recipients = [
  { name: "Atul Kumar", course: "AI Mastery 2026", date: "Sep 27, 2026", id: "CERT-001" },
  { name: "Rahul Sharma", course: "AI Mastery 2026", date: "Sep 27, 2026", id: "CERT-002" },
  { name: "Priya Singh", course: "AI Mastery 2026", date: "Sep 27, 2026", id: "CERT-003" },
];

const counts = [1, 50, 500];

export function HeroSection({ onWatchDemo }: HeroSectionProps) {
  const [recipientIndex, setRecipientIndex] = useState(0);
  const [countIndex, setCountIndex] = useState(0);

  // Cycling recipient and count animation
  useEffect(() => {
    const timer = setInterval(() => {
      setRecipientIndex((prev) => (prev + 1) % recipients.length);
      setCountIndex((prev) => (prev + 1) % counts.length);
    }, 2800);
    return () => clearInterval(timer);
  }, []);

  const currentRecipient = recipients[recipientIndex];
  const currentCount = counts[countIndex];

  return (
    <section className="relative pt-12 pb-20 md:pt-20 md:pb-28 overflow-hidden bg-grid-pattern">
      {/* Subtle radial glow & ambient background */}
      <div className="absolute inset-0 pointer-events-none -z-10">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[850px] h-[550px] bg-[radial-gradient(ellipse_at_center,_rgba(99,91,255,0.08)_0%,_transparent_70%)] blur-3xl" />
        <div className="absolute top-10 right-10 w-96 h-96 bg-[radial-gradient(circle,_rgba(22,128,60,0.04)_0%,_transparent_60%)] blur-2xl" />
      </div>

      <div className="container-marketing">
        {/* Two-column 50/50 Desktop Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-10 items-center">
          
          {/* Left Column (50% text) */}
          <div className="lg:col-span-6 flex flex-col items-start text-left">
            {/* Eyebrow */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-primary-light)] text-[var(--color-primary)] text-[12px] font-semibold tracking-wider uppercase mb-5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Bulk Certificate Automation</span>
            </div>

            {/* Headline */}
            <h1 className="text-hero text-[var(--color-text)] mb-6 font-bold">
              Create hundreds of personalized certificates{" "}
              <span className="gradient-text">from one spreadsheet.</span>
            </h1>

            {/* Supporting text */}
            <p className="text-body-lg text-[var(--color-text-secondary)] mb-8 max-w-xl leading-relaxed">
              Upload your certificate template, connect your recipient data, and generate professional certificates automatically.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 w-full sm:w-auto mb-6">
              <Button
                size="lg"
                className="h-[48px] px-7 rounded-[10px] text-[15px] font-semibold shadow-md hover:shadow-lg"
                asChild
              >
                <Link href="/signup">
                  Create Certificates Free
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Link>
              </Button>
              <Button
                variant="secondary"
                size="lg"
                className="h-[48px] px-6 rounded-[10px] text-[15px] font-medium gap-2"
                onClick={onWatchDemo}
              >
                <Play className="w-4 h-4 text-[var(--color-primary)]" />
                Watch Demo
              </Button>
            </div>

            {/* Small reassurance */}
            <p className="text-[13px] text-[var(--color-text-tertiary)] flex items-center gap-2 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              No repetitive typing. No manual exporting.
            </p>
          </div>

          {/* Right Column (50% animated product visual) */}
          <div className="lg:col-span-6 w-full">
            <div className="relative rounded-2xl border border-[var(--color-border)] bg-white shadow-xl overflow-hidden">
              {/* Window Chrome */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[#FAFAF8]">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]" />
                    <div className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]" />
                    <div className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]" />
                  </div>
                  <span className="text-[12px] font-semibold text-[var(--color-text)] ml-2">
                    Certificate Studio
                  </span>
                </div>

                {/* Batch counter indicator */}
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-[var(--color-text-secondary)] bg-white px-2 py-0.5 rounded border border-[var(--color-border)]">
                    Batch: <strong className="text-[var(--color-primary)]">{currentCount} / 500</strong>
                  </span>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1">
                    <Check className="w-3 h-3 text-emerald-600" />
                    Generated
                  </span>
                </div>
              </div>

              {/* Simulation Body */}
              <div className="p-5 sm:p-6 space-y-5 bg-white">
                {/* CSV Source Bar */}
                <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] p-3 flex items-center justify-between text-[12px]">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                    <span className="font-mono font-medium text-[var(--color-text)]">attendees.csv</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] font-mono text-[var(--color-text-secondary)]">
                    <span>Column: <strong className="text-[var(--color-primary)]">Name</strong></span>
                    <span>→</span>
                    <span className="bg-indigo-50 text-[var(--color-primary)] px-2 py-0.5 rounded font-semibold">
                      {"{{NAME}}"}
                    </span>
                  </div>
                </div>

                {/* Live Simulated Certificate Canvas */}
                <div className="relative rounded-xl border-2 border-[var(--color-border)] bg-[#FAFAF8] p-6 text-center shadow-xs overflow-hidden">
                  <div className="absolute inset-2 border border-dashed border-amber-300/60 rounded pointer-events-none" />

                  <p className="text-[9px] uppercase font-bold tracking-[0.25em] text-[var(--color-text-tertiary)] mb-1">
                    Certificate of Completion
                  </p>
                  <p className="text-[10px] text-[var(--color-text-secondary)] mb-3">
                    This certifies that
                  </p>

                  {/* Dynamic Name Animation */}
                  <div className="h-10 flex items-center justify-center">
                    <AnimatePresence mode="wait">
                      <motion.h3
                        key={currentRecipient.name}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        transition={{ duration: 0.3 }}
                        className="text-[24px] sm:text-[26px] font-bold font-serif text-[var(--color-text)] tracking-tight"
                      >
                        {currentRecipient.name}
                      </motion.h3>
                    </AnimatePresence>
                  </div>

                  <p className="text-[11px] text-[var(--color-text-secondary)] mt-1">
                    has successfully completed <strong className="text-[var(--color-primary)]">{currentRecipient.course}</strong>
                  </p>

                  {/* Certificate Footer Row */}
                  <div className="flex items-center justify-between pt-4 mt-4 border-t border-[var(--color-border)] text-left text-[10px]">
                    <div>
                      <span className="text-[var(--color-text-tertiary)] block text-[8px] uppercase font-mono">Date</span>
                      <strong className="text-[var(--color-text)]">{currentRecipient.date}</strong>
                    </div>

                    <div className="flex items-center gap-1.5 bg-white border border-[var(--color-border)] px-2 py-1 rounded shadow-2xs">
                      <QrCode className="w-4 h-4 text-[var(--color-text)]" />
                      <span className="font-mono text-[9px] text-[var(--color-text-secondary)]">{currentRecipient.id}</span>
                    </div>

                    <div className="text-right">
                      <span className="text-[var(--color-text-tertiary)] block text-[8px] uppercase font-mono">Status</span>
                      <strong className="text-emerald-600">✓ Cryptographically Signed</strong>
                    </div>
                  </div>
                </div>

                {/* Interactive Status & Recipient Pager */}
                <div className="flex items-center justify-between text-[12px] pt-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[var(--color-text-secondary)] font-medium text-[11px]">
                      Rendering row {recipientIndex + 1} of 500
                    </span>
                  </div>

                  <div className="flex gap-1.5">
                    {recipients.map((r, i) => (
                      <button
                        key={r.name}
                        onClick={() => setRecipientIndex(i)}
                        className={`w-6 h-6 rounded-md text-[10px] font-mono font-medium transition-colors ${
                          recipientIndex === i
                            ? "bg-[var(--color-primary)] text-white"
                            : "bg-[var(--color-background)] text-[var(--color-text-secondary)] hover:bg-gray-200"
                        }`}
                        aria-label={`Preview recipient ${r.name}`}
                      >
                        0{i + 1}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
