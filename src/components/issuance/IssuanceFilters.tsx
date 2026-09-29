"use client";

import { Clock, Play, CheckCircle2, AlertCircle, Pause, X } from "lucide-react";
import type { IssuanceJobStatus } from "@/types";

export type IssuanceFilterTab = "all" | "processing" | "completed" | "failed" | "paused" | "cancelled";

const TABS: { id: IssuanceFilterTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "all", label: "All Jobs", icon: Clock },
  { id: "processing", label: "Processing", icon: Play },
  { id: "completed", label: "Completed", icon: CheckCircle2 },
  { id: "failed", label: "Failed", icon: AlertCircle },
  { id: "paused", label: "Paused", icon: Pause },
  { id: "cancelled", label: "Cancelled", icon: X },
];

interface IssuanceFiltersProps {
  currentTab: IssuanceFilterTab;
  onTabChange: (tab: IssuanceFilterTab) => void;
  counts?: Partial<Record<IssuanceFilterTab, number>>;
}

export function IssuanceFilters({
  currentTab,
  onTabChange,
  counts,
}: IssuanceFiltersProps) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-1 border-b border-[var(--color-border)]">
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const count = counts?.[tab.id];
        const isActive = currentTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13px] font-semibold whitespace-nowrap transition-all ${
              isActive
                ? "bg-[var(--color-primary-subtle)] text-[var(--color-primary)] font-bold shadow-2xs"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-gray-100/60"
            }`}
          >
            <Icon className="w-3.5 h-3.5 shrink-0" />
            <span>{tab.label}</span>
            {count !== undefined && (
              <span
                className={`text-[11px] px-1.5 py-0.2 rounded-full ${
                  isActive
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
