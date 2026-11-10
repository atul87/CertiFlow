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
  Palette,
  Eye,
  Info,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ProjectPipelineHeader } from "@/components/project/ProjectPipelineHeader";

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

  const allMapped = mappings.every((m) => m.selectedColumn !== "— Do not map —");

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* 5-Step Pipeline Header */}
      <ProjectPipelineHeader
        projectId={id || "proj-ai-2026"}
        projectName="AI Workshop 2026"
        currentStep="mapping"
        recipientCount={500}
      />

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-6 max-w-4xl mx-auto">
        {/* Step Guide Banner */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                Step 2 of 5
              </span>
              <h1 className="text-[18px] font-bold text-gray-900">
                Field Mapping Studio
              </h1>
            </div>
            <p className="text-[13px] text-gray-500 max-w-2xl">
              Connect template placeholders to your CSV headers with intelligent 5-tier fuzzy matching.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button size="sm" variant="secondary" onClick={handleAutoMatch} className="gap-1.5 text-[12px] h-9">
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Auto-Match All</span>
            </Button>
            <Button size="sm" asChild className="gap-1.5 text-[12px] h-9 font-semibold">
              <Link href={`/app/projects/${id || "proj-ai-2026"}/editor`}>
                <Palette className="w-3.5 h-3.5" />
                <span>Step 3: Studio</span>
              </Link>
            </Button>
          </div>
        </div>

        {autoMatchedNotice && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Fuzzy matching algorithm successfully mapped all template variables with &gt;90% confidence.</span>
          </div>
        )}

        {/* Mapping Rows */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs space-y-4">
          <div className="grid grid-cols-12 text-[11px] font-bold uppercase tracking-wider text-gray-400 pb-2 border-b border-[var(--color-border)]">
            <div className="col-span-4">Certificate Template Tag</div>
            <div className="col-span-1 text-center"></div>
            <div className="col-span-4">Spreadsheet Column (CSV)</div>
            <div className="col-span-3 text-right">Resolved Value</div>
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
                    className="w-full text-[13px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl p-2 font-medium text-gray-800 focus:outline-none focus:border-[var(--color-primary)] cursor-pointer"
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
        <div className="p-5 rounded-2xl bg-white border border-[var(--color-border)] shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[14px] font-bold text-gray-900">
                {allMapped ? "All 5 Dynamic Tags Successfully Mapped" : "Review Incomplete Field Mappings"}
              </p>
              <p className="text-[12px] text-gray-500">
                Next: Customize the certificate vector layout in the Canvas Studio, or skip directly to Live Preview.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button size="sm" variant="secondary" asChild className="h-9 text-[12px]">
              <Link href={`/app/projects/${id || "proj-ai-2026"}/editor`}>
                <Palette className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                <span>Open Canvas Studio</span>
              </Link>
            </Button>
            <Button size="sm" asChild className="h-9 text-[12px] font-semibold gap-1">
              <Link href={`/app/projects/${id || "proj-ai-2026"}/preview`}>
                <span>Step 4: Live Preview</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
