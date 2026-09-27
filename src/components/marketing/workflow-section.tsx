"use client";

import { motion } from "motion/react";
import { Upload, Sliders, Layers, FileSpreadsheet, FileImage, Sparkles, Check } from "lucide-react";
import { staggerContainer, staggerItem, viewportOnce } from "@/lib/motion";

const workflowSteps = [
  {
    step: "01",
    icon: Upload,
    title: "Upload your template and data.",
    description: "Add your certificate design (PDF, PNG, JPG) and recipient CSV or Excel spreadsheet.",
    visualType: "upload",
  },
  {
    step: "02",
    icon: Sliders,
    title: "Connect your fields.",
    description: "Map columns like Name, Course, Date, and Score directly to your certificate typography layers.",
    visualType: "map",
  },
  {
    step: "03",
    icon: Layers,
    title: "Generate the entire batch.",
    description: "Preview your certificates across real recipient records, generate the batch, and download everything.",
    visualType: "generate",
  },
];

export function WorkflowSection() {
  return (
    <section className="section-padding bg-white border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Workflow Architecture
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-4">
            From spreadsheet to certificates in three steps.
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Simple enough for any school or event organizer, yet engineered for enterprise batch volumes.
          </p>
        </div>

        {/* 3 Step Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {workflowSteps.map((s) => (
            <div
              key={s.step}
              className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)] p-7 flex flex-col justify-between hover:border-[var(--color-border-hover)] hover:shadow-xs transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-5">
                  <div className="w-10 h-10 rounded-xl bg-white border border-[var(--color-border)] flex items-center justify-center text-[var(--color-primary)] shadow-2xs">
                    <s.icon className="w-5 h-5" />
                  </div>
                  <span className="text-[20px] font-mono font-bold text-[var(--color-text-tertiary)]">
                    {s.step}
                  </span>
                </div>

                <h3 className="text-[18px] font-bold text-[var(--color-text)] mb-2">
                  {s.title}
                </h3>
                <p className="text-[14px] text-[var(--color-text-secondary)] leading-relaxed mb-6">
                  {s.description}
                </p>
              </div>

              {/* Visual for step */}
              <div className="rounded-xl border border-[var(--color-border)] bg-white p-4 shadow-2xs">
                {s.visualType === "upload" && (
                  <div className="space-y-2">
                    <div className="p-2 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex items-center gap-2.5 text-[12px]">
                      <FileImage className="w-4 h-4 text-indigo-600" />
                      <span className="font-mono text-[var(--color-text)]">certificate.png</span>
                      <span className="ml-auto text-emerald-600 text-[10px] font-bold">✓ 300 DPI</span>
                    </div>
                    <div className="p-2 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex items-center gap-2.5 text-[12px]">
                      <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                      <span className="font-mono text-[var(--color-text)]">students.csv</span>
                      <span className="ml-auto text-emerald-600 text-[10px] font-bold">✓ 500 rows</span>
                    </div>
                  </div>
                )}

                {s.visualType === "map" && (
                  <div className="space-y-1.5 font-mono text-[11px]">
                    <div className="flex items-center justify-between p-1.5 rounded bg-[var(--color-background)]">
                      <span className="text-gray-700">Name</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-[var(--color-primary)] font-bold">{"{{NAME}}"}</span>
                    </div>
                    <div className="flex items-center justify-between p-1.5 rounded bg-[var(--color-background)]">
                      <span className="text-gray-700">Course</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-[var(--color-primary)] font-bold">{"{{COURSE}}"}</span>
                    </div>
                    <div className="flex items-center justify-between p-1.5 rounded bg-[var(--color-background)]">
                      <span className="text-gray-700">Date</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-[var(--color-primary)] font-bold">{"{{DATE}}"}</span>
                    </div>
                  </div>
                )}

                {s.visualType === "generate" && (
                  <div className="space-y-2 text-[12px]">
                    <div className="flex justify-between font-semibold">
                      <span className="text-[var(--color-text)]">500 certificates</span>
                      <span className="text-emerald-600 font-mono">100%</span>
                    </div>
                    <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full w-full" />
                    </div>
                    <p className="text-[11px] text-[var(--color-text-tertiary)] font-mono text-center pt-0.5">
                      ✓ Instant ZIP archive ready
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
