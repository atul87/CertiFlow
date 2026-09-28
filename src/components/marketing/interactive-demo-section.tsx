"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Download,
  QrCode,
  RotateCcw,
  Check,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const sampleAttendees = [
  { name: "Atul Kumar", course: "AI Mastery 2026", date: "27 Sep 2026", id: "CERT-001" },
  { name: "Rahul Sharma", course: "AI Mastery 2026", date: "27 Sep 2026", id: "CERT-002" },
  { name: "Priya Singh", course: "AI Mastery 2026", date: "27 Sep 2026", id: "CERT-003" },
];

type DemoStep = 1 | 2 | 3 | 4;

const toDemoStep = (value: number): DemoStep => Math.min(4, Math.max(1, value)) as DemoStep;

export function InteractiveDemoSection() {
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);
  const [selectedAttendee, setSelectedAttendee] = useState(0);

  return (
    <section className="section-padding bg-white border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-12">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Interactive Product Demo
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            See the entire workflow in action.
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            No signup required. Click through the 4 steps below.
          </p>

          {/* Stepper Tabs */}
          <div className="grid grid-cols-4 gap-2 mt-8 max-w-lg mx-auto">
            {[
              { num: 1, label: "1 Upload" },
              { num: 2, label: "2 Map" },
              { num: 3, label: "3 Preview" },
              { num: 4, label: "4 Generate" },
            ].map((s) => (
              <button
                key={s.num}
                onClick={() => setCurrentStep(toDemoStep(s.num))}
                className={`py-2 px-1 text-[13px] font-semibold rounded-lg border transition-all text-center ${currentStep === s.num
                    ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)] shadow-xs"
                    : currentStep > s.num
                      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                      : "bg-[var(--color-background)] text-[var(--color-text-secondary)] border-[var(--color-border)] hover:bg-gray-100"
                  }`}
              >
                {currentStep > s.num ? `✓ ${s.label.split(" ")[1]}` : s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Demo Box */}
        <div className="max-w-3xl mx-auto rounded-2xl border border-[var(--color-border)] bg-[#FAFAF8] p-6 sm:p-10 shadow-sm min-h-[420px] flex flex-col justify-between">
          <AnimatePresence mode="wait">
            {/* Step 1: Upload CSV */}
            {currentStep === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="space-y-6 text-center max-w-md mx-auto py-4"
              >
                <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                  <FileSpreadsheet className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-[20px] font-bold text-[var(--color-text)]">Upload CSV</h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                    Spreadsheet loaded with recipient records
                  </p>
                </div>

                <div className="p-5 rounded-xl bg-white border border-[var(--color-border)] shadow-2xs space-y-2">
                  <div className="flex items-center justify-between font-mono text-[13px]">
                    <span className="font-semibold text-emerald-700 flex items-center gap-2">
                      <FileSpreadsheet className="w-4 h-4" />
                      students.csv
                    </span>
                    <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-bold">
                      248 records
                    </span>
                  </div>
                  <p className="text-[12px] text-gray-500 text-left font-mono">
                    Headers parsed: Name, Course, Date, Score
                  </p>
                </div>
              </motion.div>
            )}

            {/* Step 2: Map Fields */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="space-y-4 max-w-md mx-auto py-2"
              >
                <div className="text-center mb-6">
                  <h3 className="text-[20px] font-bold text-[var(--color-text)]">Connect Fields</h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                    Columns mapped to template placeholders
                  </p>
                </div>

                <div className="space-y-2.5 font-mono text-[13px] bg-white p-5 rounded-xl border border-[var(--color-border)]">
                  <div className="flex items-center justify-between p-2.5 rounded bg-[var(--color-background)]">
                    <span className="font-medium text-gray-700">Name</span>
                    <span className="text-gray-400">→</span>
                    <span className="text-[var(--color-primary)] font-bold">{"{{NAME}}"}</span>
                    <span className="text-emerald-600 text-[11px] font-semibold">✓ Matched</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded bg-[var(--color-background)]">
                    <span className="font-medium text-gray-700">Course</span>
                    <span className="text-gray-400">→</span>
                    <span className="text-[var(--color-primary)] font-bold">{"{{COURSE}}"}</span>
                    <span className="text-emerald-600 text-[11px] font-semibold">✓ Matched</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded bg-[var(--color-background)]">
                    <span className="font-medium text-gray-700">Date</span>
                    <span className="text-gray-400">→</span>
                    <span className="text-[var(--color-primary)] font-bold">{"{{DATE}}"}</span>
                    <span className="text-emerald-600 text-[11px] font-semibold">✓ Matched</span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 3: Certificate Preview */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="space-y-5"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-[18px] font-bold">Certificate Preview</h3>
                  <div className="flex gap-1.5 bg-white p-1 rounded-lg border border-[var(--color-border)]">
                    {sampleAttendees.map((a, i) => (
                      <button
                        key={a.name}
                        onClick={() => setSelectedAttendee(i)}
                        className={`px-3 py-1 text-[12px] font-medium rounded-md transition-colors ${selectedAttendee === i
                            ? "bg-[var(--color-primary)] text-white shadow-xs"
                            : "text-[var(--color-text-secondary)] hover:text-black"
                          }`}
                      >
                        {a.name.split(" ")[0]}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Rendered Certificate Card */}
                <div className="relative rounded-xl border-2 border-[var(--color-border)] bg-white p-6 max-w-xl mx-auto shadow-sm text-center">
                  <p className="text-[9px] uppercase font-bold tracking-[0.25em] text-gray-400 mb-1">
                    Certificate of Achievement
                  </p>
                  <p className="text-[11px] text-gray-500 mb-3">This certifies that</p>

                  <h4 className="text-[24px] font-bold font-serif text-[var(--color-text)] my-2">
                    {sampleAttendees[selectedAttendee].name}
                  </h4>

                  <p className="text-[12px] text-[var(--color-text-secondary)]">
                    has successfully completed <strong className="text-[var(--color-primary)]">{sampleAttendees[selectedAttendee].course}</strong>
                  </p>

                  <div className="flex items-center justify-between pt-4 mt-4 border-t border-[var(--color-border)] text-[10px] text-gray-500">
                    <span>{sampleAttendees[selectedAttendee].date}</span>
                    <div className="w-5 h-5 border flex items-center justify-center font-mono text-[7px]">QR</div>
                    <span className="font-mono">{sampleAttendees[selectedAttendee].id}</span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 4: Generate Complete */}
            {currentStep === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="space-y-6 text-center max-w-md mx-auto py-6"
              >
                <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-[22px] font-bold text-[var(--color-text)]">
                    ✓ 248 certificates generated
                  </h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                    Batch complete in 1.4 seconds. Print-ready 300 DPI PDFs.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white border border-[var(--color-border)] shadow-xs">
                  <Button size="lg" className="w-full justify-center shadow-sm" asChild>
                    <Link href="/signup">
                      <Sparkles className="w-4 h-4 mr-1.5" />
                      Build your own batch
                    </Link>
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Stepper Navigation Buttons */}
          <div className="mt-8 pt-6 border-t border-[var(--color-border)] flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              disabled={currentStep === 1}
              onClick={() => setCurrentStep((prev) => toDemoStep(prev - 1))}
              className="gap-1"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>

            <span className="text-[12px] font-mono text-gray-500">
              Step {currentStep} of 4
            </span>

            {currentStep < 4 ? (
              <Button
                size="sm"
                onClick={() => setCurrentStep((prev) => toDemoStep(prev + 1))}
                className="gap-1"
              >
                Next Step
                <ArrowRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCurrentStep(1)}
              >
                Restart Demo
              </Button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
