"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Clock, Zap, ArrowRight, CheckCircle2, XCircle, Sparkles } from "lucide-react";
import { staggerContainer, staggerItem, viewportOnce } from "@/lib/motion";

export function BeforeAfterSection() {
  const [activeTab, setActiveTab] = useState<"after" | "before">("after");

  return (
    <section className="section-padding bg-[#F6F6F3] border-y border-[var(--color-border)] overflow-hidden">
      <div className="container-marketing">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          variants={staggerContainer}
          className="max-w-2xl mx-auto text-center mb-12"
        >
          <motion.p
            variants={staggerItem}
            className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3"
          >
            Efficiency Benchmark
          </motion.p>
          <motion.h2 variants={staggerItem} className="text-section mb-4">
            See the difference in seconds
          </motion.h2>
          <motion.p variants={staggerItem} className="text-body-lg text-[var(--color-text-secondary)]">
            Compare manual certificate preparation against CertiFlow’s automated pipeline for a 500-certificate batch.
          </motion.p>

          {/* Toggle pill */}
          <motion.div variants={staggerItem} className="inline-flex p-1.5 rounded-xl bg-white border border-[var(--color-border)] shadow-xs mt-8">
            <button
              onClick={() => setActiveTab("before")}
              className={`px-5 py-2 rounded-lg text-[14px] font-medium transition-all ${
                activeTab === "before"
                  ? "bg-[#FEF3F2] text-[var(--color-danger)] shadow-xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
              }`}
            >
              Manual Process (Before)
            </button>
            <button
              onClick={() => setActiveTab("after")}
              className={`px-5 py-2 rounded-lg text-[14px] font-medium transition-all flex items-center gap-1.5 ${
                activeTab === "after"
                  ? "bg-[var(--color-primary)] text-white shadow-xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              With CertiFlow (After)
            </button>
          </motion.div>
        </motion.div>

        {/* Comparison card container */}
        <div className="max-w-4xl mx-auto">
          {activeTab === "before" ? (
            <motion.div
              key="before"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
              className="rounded-2xl border border-red-200 bg-white p-8 md:p-10 shadow-sm"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-8 border-b border-red-100">
                <div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 text-red-700 text-[12px] font-semibold mb-2">
                    <XCircle className="w-3.5 h-3.5" />
                    Traditional Manual Creation
                  </span>
                  <h3 className="text-[24px] font-bold text-[var(--color-text)]">
                    Typing 500 certificates by hand
                  </h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                    Prone to typos, formatting drift, misaligned dates, and human fatigue.
                  </p>
                </div>
                <div className="bg-red-50 px-5 py-3 rounded-xl border border-red-100 text-right shrink-0">
                  <p className="text-[11px] uppercase font-bold text-red-500 tracking-wider">Total Time</p>
                  <p className="text-[28px] font-bold text-red-700 font-mono">~7h 45m</p>
                </div>
              </div>

              {/* Progress bars of manual steps */}
              <div className="mt-8 space-y-5">
                <div>
                  <div className="flex justify-between text-[13px] font-medium mb-1.5">
                    <span className="text-[var(--color-text-secondary)]">Copy-pasting 500 names & IDs</span>
                    <span className="text-red-600 font-mono">3 hours 20 mins</span>
                  </div>
                  <div className="h-3 rounded-full bg-red-100 overflow-hidden">
                    <div className="h-full bg-red-500 rounded-full w-[85%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[13px] font-medium mb-1.5">
                    <span className="text-[var(--color-text-secondary)]">Manual layout & font-size tweaking per length</span>
                    <span className="text-red-600 font-mono">2 hours 15 mins</span>
                  </div>
                  <div className="h-3 rounded-full bg-red-100 overflow-hidden">
                    <div className="h-full bg-red-400 rounded-full w-[65%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[13px] font-medium mb-1.5">
                    <span className="text-[var(--color-text-secondary)]">Exporting each single PDF file</span>
                    <span className="text-red-600 font-mono">1 hour 30 mins</span>
                  </div>
                  <div className="h-3 rounded-full bg-red-100 overflow-hidden">
                    <div className="h-full bg-red-400 rounded-full w-[45%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[13px] font-medium mb-1.5">
                    <span className="text-[var(--color-text-secondary)]">Verifying typos & fixing mistakes</span>
                    <span className="text-red-600 font-mono">40 mins</span>
                  </div>
                  <div className="h-3 rounded-full bg-red-100 overflow-hidden">
                    <div className="h-full bg-red-300 rounded-full w-[30%]" />
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-[var(--color-border)] flex items-center justify-between text-[13px] text-[var(--color-text-secondary)]">
                <span className="flex items-center gap-1.5 text-red-600 font-medium">
                  <Clock className="w-4 h-4" />
                  Estimated error rate: 4.8% (24 re-issues)
                </span>
                <button
                  onClick={() => setActiveTab("after")}
                  className="text-[var(--color-primary)] font-semibold hover:underline inline-flex items-center gap-1"
                >
                  Switch to CertiFlow way <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="after"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
              className="rounded-2xl border-2 border-[var(--color-primary)] bg-white p-8 md:p-10 shadow-lg relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 bg-[var(--color-primary)] text-white text-[11px] font-bold px-4 py-1 rounded-bl-xl uppercase tracking-wider">
                Automated Pipeline
              </div>

              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-8 border-b border-[var(--color-border)]">
                <div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[12px] font-semibold mb-2">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    CertiFlow Bulk Automation
                  </span>
                  <h3 className="text-[24px] font-bold text-[var(--color-text)]">
                    500 personalized certificates in 1 click
                  </h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                    Upload spreadsheet, map variables, review live preview, and download full ZIP.
                  </p>
                </div>
                <div className="bg-emerald-50 px-5 py-3 rounded-xl border border-emerald-100 text-right shrink-0">
                  <p className="text-[11px] uppercase font-bold text-emerald-600 tracking-wider">Total Time</p>
                  <p className="text-[28px] font-bold text-emerald-700 font-mono">1m 45s</p>
                </div>
              </div>

              {/* Progress steps of CertiFlow */}
              <div className="mt-8 space-y-4">
                {[
                  { title: "Upload template & CSV file", time: "20 seconds", pct: "100%", status: "Done" },
                  { title: "Map {{NAME}}, {{COURSE}}, {{DATE}}", time: "30 seconds", pct: "100%", status: "Done" },
                  { title: "Auto-fit typography & dynamic QR injection", time: "10 seconds", pct: "100%", status: "Done" },
                  { title: "Client-side PDF & ZIP bulk rendering (500/500)", time: "45 seconds", pct: "100%", status: "Done" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3.5 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)]">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[12px] font-bold">
                        ✓
                      </div>
                      <span className="text-[14px] font-medium text-[var(--color-text)]">{item.title}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-[12px] text-[var(--color-text-secondary)] font-mono">{item.time}</span>
                      <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded">
                        {item.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 pt-6 border-t border-[var(--color-border)] flex flex-col sm:flex-row items-center justify-between gap-3 text-[13px]">
                <span className="flex items-center gap-1.5 text-emerald-700 font-medium">
                  <Zap className="w-4 h-4 text-emerald-600" />
                  Over 99.6% time saved · 0 human typo risk
                </span>
                <span className="text-[var(--color-text-tertiary)] font-mono text-[12px]">
                  500 PDFs generated · 84 MB ZIP
                </span>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </section>
  );
}
