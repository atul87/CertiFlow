"use client";

import Link from "next/link";
import {
  FileSpreadsheet,
  Layers,
  Palette,
  Eye,
  Zap,
  ArrowLeft,
  ChevronRight,
  Check,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export type PipelineStep = "data" | "mapping" | "editor" | "preview" | "generate";

interface ProjectPipelineHeaderProps {
  projectId: string;
  projectName?: string;
  currentStep: PipelineStep;
  recipientCount?: number;
  onLoadSampleData?: () => void;
}

const STEPS: Array<{
  id: PipelineStep;
  number: number;
  label: string;
  sub: string;
  icon: typeof FileSpreadsheet;
  path: (id: string) => string;
}> = [
  {
    id: "data",
    number: 1,
    label: "Data Ingestion",
    sub: "CSV Roster",
    icon: FileSpreadsheet,
    path: (id) => `/app/projects/${id}/data`,
  },
  {
    id: "mapping",
    number: 2,
    label: "Field Mapping",
    sub: "Variables",
    icon: Layers,
    path: (id) => `/app/projects/${id}/mapping`,
  },
  {
    id: "editor",
    number: 3,
    label: "Canvas Studio",
    sub: "Vector Layout",
    icon: Palette,
    path: (id) => `/app/projects/${id}/editor`,
  },
  {
    id: "preview",
    number: 4,
    label: "Live Preview",
    sub: "Auto-Fit & Cards",
    icon: Eye,
    path: (id) => `/app/projects/${id}/preview`,
  },
  {
    id: "generate",
    number: 5,
    label: "Batch Issuance",
    sub: "PDF & Delivery",
    icon: Zap,
    path: (id) => `/app/projects/${id}/generate`,
  },
];

export function ProjectPipelineHeader({
  projectId,
  projectName = "AI Workshop 2026",
  currentStep,
  recipientCount = 500,
  onLoadSampleData,
}: ProjectPipelineHeaderProps) {
  const currentIndex = STEPS.findIndex((s) => s.id === currentStep);
  const nextStep = currentIndex < STEPS.length - 1 ? STEPS[currentIndex + 1] : null;

  return (
    <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30 shadow-2xs">
      {/* Upper Meta Bar */}
      <div className="container-marketing h-14 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/app/projects"
            className="p-1.5 rounded-lg text-gray-500 hover:text-black hover:bg-gray-100 transition-colors shrink-0"
            title="Back to Projects Directory"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div className="h-4 w-px bg-gray-200 shrink-0" />

          <div className="min-w-0 flex items-center gap-2">
            <span className="text-[14px] font-bold text-[var(--color-text)] truncate">
              {projectName}
            </span>
            <Badge variant="outline" className="text-[11px] font-mono shrink-0 hidden sm:inline-flex">
              {recipientCount} Recipients
            </Badge>
          </div>
        </div>

        {/* Quick Step Navigation and Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {onLoadSampleData && (
            <Button
              size="sm"
              variant="secondary"
              onClick={onLoadSampleData}
              className="hidden md:inline-flex text-[12px] h-8 px-2.5 gap-1.5 border-dashed border-indigo-200 text-indigo-700 hover:bg-indigo-50"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Load Sample CSV</span>
            </Button>
          )}

          {nextStep ? (
            <Button size="sm" asChild className="h-8 text-[12px] px-3 font-semibold gap-1.5 shadow-xs">
              <Link href={nextStep.path(projectId)}>
                <span>Next: {nextStep.label}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </Button>
          ) : (
            <Button size="sm" asChild className="h-8 text-[12px] px-3 font-semibold bg-emerald-600 hover:bg-emerald-700 shadow-xs">
              <Link href="/app/certificates">
                <span>View Certificate Vault</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </Button>
          )}
        </div>
      </div>

      {/* 5-Step Visual Stepper Bar */}
      <div className="bg-[#FAF9F5] border-t border-[var(--color-border)] px-4 sm:px-6 py-2 overflow-x-auto scrollbar-none">
        <div className="container-marketing flex items-center justify-between min-w-[680px] gap-2">
          {STEPS.map((step, idx) => {
            const isCurrent = step.id === currentStep;
            const isCompleted = idx < currentIndex;
            const Icon = step.icon;

            return (
              <div key={step.id} className="flex items-center flex-1 last:flex-none">
                <Link
                  href={step.path(projectId)}
                  className={`flex items-center gap-2.5 py-1 px-2.5 rounded-lg transition-all group ${
                    isCurrent
                      ? "bg-white border border-[var(--color-primary)] shadow-xs"
                      : isCompleted
                      ? "hover:bg-white text-gray-700"
                      : "opacity-60 hover:opacity-100 hover:bg-white text-gray-400"
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-bold transition-colors ${
                      isCurrent
                        ? "bg-[var(--color-primary)] text-white"
                        : isCompleted
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-gray-200 text-gray-600 group-hover:bg-gray-300"
                    }`}
                  >
                    {isCompleted ? <Check className="w-3.5 h-3.5" /> : step.number}
                  </div>

                  <div className="text-left">
                    <p
                      className={`text-[12px] font-semibold leading-tight flex items-center gap-1.5 ${
                        isCurrent
                          ? "text-[var(--color-primary)]"
                          : isCompleted
                          ? "text-gray-900"
                          : "text-gray-600"
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{step.label}</span>
                    </p>
                    <p className="text-[10px] text-gray-400 font-normal leading-tight">
                      {step.sub}
                    </p>
                  </div>
                </Link>

                {idx < STEPS.length - 1 && (
                  <div className="flex-1 mx-2 h-px bg-gray-200 hidden sm:block" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </header>
  );
}
