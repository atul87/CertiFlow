"use client";

import { motion } from "motion/react";
import { ArrowRight, RotateCcw, Clock, Sparkles, CheckCircle2, FileSpreadsheet, Layers } from "lucide-react";
import { staggerContainer, staggerItem, viewportOnce } from "@/lib/motion";

export function ProblemSection() {
  return (
    <section className="section-padding bg-[#FAFAF8] overflow-hidden">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-danger)] mb-3">
            The Traditional Bottleneck
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-4">
            Stop creating certificates one by one.
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            A certificate should take seconds to issue—not hours of repetitive editing.
          </p>
        </div>

        {/* Side by side comparison: Manual Process vs Automated CertiFlow */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto items-stretch">
          
          {/* Card 1: MANUAL PROCESS */}
          <div className="rounded-2xl border border-red-200/80 bg-white p-7 sm:p-9 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 text-red-700 text-[12px] font-bold tracking-wider uppercase">
                  <RotateCcw className="w-3.5 h-3.5" />
                  Manual Process
                </span>
                <span className="text-[12px] font-mono text-red-500 font-semibold">
                  ~8 hours / 500 certs
                </span>
              </div>

              {/* Vertical flow steps */}
              <div className="space-y-3 font-mono text-[13px] max-w-xs mx-auto text-center py-2">
                <div className="p-2.5 rounded-lg bg-gray-50 border border-gray-200 font-medium text-gray-700">
                  Open Certificate Design
                </div>
                <div className="text-gray-400">↓</div>
                <div className="p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-700 font-medium">
                  Type Attendee Name
                </div>
                <div className="text-gray-400">↓</div>
                <div className="p-2.5 rounded-lg bg-gray-50 border border-gray-200 font-medium text-gray-700">
                  Export Individual PDF
                </div>
                <div className="text-gray-400">↓</div>
                <div className="p-2.5 rounded-lg bg-gray-50 border border-gray-200 font-medium text-gray-700">
                  Rename File
                </div>
                <div className="text-gray-400">↓</div>
                <div className="p-2.5 rounded-lg bg-red-100/70 border border-red-200 text-red-800 font-semibold">
                  Repeat × 500 times
                </div>
              </div>
            </div>

            <div className="mt-8 pt-5 border-t border-red-100 flex items-center justify-between text-[12px] text-red-600 font-medium">
              <span className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                Hours of repetitive manual fatigue
              </span>
              <span>4.8% error rate</span>
            </div>
          </div>

          {/* Card 2: AUTOMATED WITH CERTIFLOW */}
          <div className="rounded-2xl border-2 border-[var(--color-primary)] bg-white p-7 sm:p-9 shadow-md flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-[var(--color-primary)] text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg uppercase tracking-wider">
              120× Faster
            </div>

            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-[var(--color-primary)] text-[12px] font-bold tracking-wider uppercase">
                  <Sparkles className="w-3.5 h-3.5" />
                  Automated Pipeline
                </span>
                <span className="text-[12px] font-mono text-emerald-600 font-bold">
                  Under 2 minutes
                </span>
              </div>

              {/* Solution Transition */}
              <div className="space-y-4 py-2">
                <div className="p-3 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-between text-[13px]">
                  <span className="text-[var(--color-text-secondary)] line-through decoration-red-400">Type Name</span>
                  <span className="text-[var(--color-primary)] font-bold">→ Map Fields Once</span>
                  <span className="text-emerald-600 font-mono text-[11px] font-semibold">✓ Done</span>
                </div>

                <div className="p-3 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-between text-[13px]">
                  <span className="text-[var(--color-text-secondary)] line-through decoration-red-400">Export PDF</span>
                  <span className="text-[var(--color-primary)] font-bold">→ Generate 500 at Once</span>
                  <span className="text-emerald-600 font-mono text-[11px] font-semibold">✓ Done</span>
                </div>

                <div className="p-3 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-between text-[13px]">
                  <span className="text-[var(--color-text-secondary)] line-through decoration-red-400">Repeat 500x</span>
                  <span className="text-[var(--color-primary)] font-bold">→ Instant ZIP + QR</span>
                  <span className="text-emerald-600 font-mono text-[11px] font-semibold">✓ Done</span>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-xl bg-[var(--color-primary-subtle)] border border-[var(--color-primary-light)] text-center">
                <p className="text-[14px] font-bold text-[var(--color-primary)]">
                  One template. One spreadsheet. Hundreds of certificates.
                </p>
              </div>
            </div>

            <div className="mt-8 pt-5 border-t border-[var(--color-border)] flex items-center justify-between text-[12px] text-emerald-700 font-medium">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Zero typo risk · Instant download
              </span>
              <span className="font-mono text-[var(--color-text-tertiary)]">84 MB compiled ZIP</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
