"use client";

import { use, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Sliders,
  Check,
  RotateCcw,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface MappingItem {
  tag: string;
  label: string;
  selectedColumn: string;
  confidence: number;
  sampleValue: string;
}

const DEFAULT_MAPPINGS: MappingItem[] = [
  {
    tag: "{{NAME}}",
    label: "Recipient Name",
    selectedColumn: "Full Name",
    confidence: 99,
    sampleValue: "Atul Kumar",
  },
  {
    tag: "{{COURSE}}",
    label: "Course / Event Title",
    selectedColumn: "Course",
    confidence: 96,
    sampleValue: "Advanced Deep Learning & AI Systems",
  },
  {
    tag: "{{DATE}}",
    label: "Issue Date",
    selectedColumn: "Completion Date",
    confidence: 95,
    sampleValue: "September 28, 2026",
  },
  {
    tag: "{{SCORE}}",
    label: "Score / Grade",
    selectedColumn: "Score",
    confidence: 94,
    sampleValue: "98% (Honors Distinction)",
  },
  {
    tag: "{{CERTIFICATE_ID}}",
    label: "Cryptographic Certificate UUID",
    selectedColumn: "AUTO_GENERATED_HASH",
    confidence: 100,
    sampleValue: "CERT-AF72K9 (Auto Generated)",
  },
];

const CSV_COLUMNS = [
  "Full Name",
  "Course",
  "Completion Date",
  "Score",
  "Recipient Email",
  "AUTO_GENERATED_HASH",
  "— Do not map —",
];

export default function FieldMappingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [mappings, setMappings] = useState<MappingItem[]>(DEFAULT_MAPPINGS);
  const [autoMatchedNotice, setAutoMatchedNotice] = useState(false);

  const handleColumnChange = (tag: string, col: string) => {
    setMappings((prev) =>
      prev.map((m) =>
        m.tag === tag
          ? {
              ...m,
              selectedColumn: col,
              confidence: col === "— Do not map —" ? 0 : 100,
            }
          : m
      )
    );
  };

  const handleAutoMatch = () => {
    setMappings(DEFAULT_MAPPINGS);
    setAutoMatchedNotice(true);
    setTimeout(() => setAutoMatchedNotice(false), 3000);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href={`/app/projects/${id || "proj-ai-2026"}/data`}
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="w-8 h-8 rounded-lg bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-[16px] font-bold text-gray-900">
                  Field Mapping Studio
                </h1>
                <Badge variant="success" className="text-[11px]">
                  All Fields Connected
                </Badge>
              </div>
              <p className="text-[11px] text-gray-500">
                5 Template Variables · 5 CSV Columns
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" onClick={handleAutoMatch}>
              <RotateCcw className="w-3.5 h-3.5 mr-1" />
              Auto-Match Columns
            </Button>
            <Button size="sm" asChild>
              <Link href={`/app/projects/${id || "proj-ai-2026"}/preview`}>
                Continue to Preview <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-6 max-w-4xl mx-auto">
        <div className="space-y-1">
          <h2 className="text-[22px] font-bold text-gray-900">
            Connect Template Placeholders to Spreadsheet Columns
          </h2>
          <p className="text-[13px] text-gray-500">
            CertiFlow automatically detects matching headers. Review and confirm dynamic tag bindings below.
          </p>
        </div>

        {autoMatchedNotice && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Auto-matching algorithm successfully connected all 5 variables with &gt;90% confidence.</span>
          </div>
        )}

        {/* Mapping Rows */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs space-y-4">
          <div className="grid grid-cols-12 text-[11px] font-bold uppercase tracking-wider text-gray-400 pb-2 border-b border-[var(--color-border)]">
            <div className="col-span-4">Certificate Template Tag</div>
            <div className="col-span-1 text-center"></div>
            <div className="col-span-4">Spreadsheet Column (CSV)</div>
            <div className="col-span-3 text-right">Sample Preview</div>
          </div>

          <div className="divide-y divide-[var(--color-border)]">
            {mappings.map((m) => (
              <div key={m.tag} className="py-4 grid grid-cols-12 items-center gap-2 text-[13px]">
                {/* Template Tag */}
                <div className="col-span-4 flex items-center gap-2.5">
                  <span className="font-mono bg-[var(--color-primary-light)] text-[var(--color-primary)] font-bold px-2.5 py-1 rounded-lg text-[12px]">
                    {m.tag}
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">{m.label}</p>
                    <span className="text-[10px] text-emerald-600 font-medium">
                      ✓ {m.confidence}% Confidence
                    </span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="col-span-1 text-center text-gray-400 font-bold">
                  →
                </div>

                {/* CSV Column Selector */}
                <div className="col-span-4">
                  <select
                    value={m.selectedColumn}
                    onChange={(e) => handleColumnChange(m.tag, e.target.value)}
                    className="w-full text-[13px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl p-2 font-medium text-gray-800 focus:outline-none focus:border-[var(--color-primary)]"
                  >
                    {CSV_COLUMNS.map((col) => (
                      <option key={col} value={col}>
                        {col === "AUTO_GENERATED_HASH" ? "⚡ Auto-Generate Unique QR UUID" : col}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sample Value */}
                <div className="col-span-3 text-right">
                  <span className="text-[12px] font-mono text-gray-600 bg-gray-50 px-2 py-1 rounded border border-gray-200 truncate inline-block max-w-full">
                    {m.sampleValue}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Verification Banner */}
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>
              All template tags are mapped. Ready to verify rendering in the live preview studio.
            </span>
          </div>

          <Button size="sm" asChild>
            <Link href={`/app/projects/${id || "proj-ai-2026"}/preview`}>
              Inspect Preview <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
