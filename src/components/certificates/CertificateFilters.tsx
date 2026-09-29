"use client";

import { Search, Filter } from "lucide-react";
import type { CertificateStatus } from "@/types";

interface CertificateFiltersProps {
  currentStatus: CertificateStatus | "all";
  onStatusChange: (status: CertificateStatus | "all") => void;
  search: string;
  onSearchChange: (val: string) => void;
  totalCount: number;
}

const STATUSES: { id: CertificateStatus | "all"; label: string }[] = [
  { id: "all", label: "All Records" },
  { id: "active", label: "Active" },
  { id: "revoked", label: "Revoked" },
  { id: "expired", label: "Expired" },
];

export function CertificateFilters({
  currentStatus,
  onStatusChange,
  search,
  onSearchChange,
  totalCount,
}: CertificateFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
      {/* Search Input */}
      <div className="relative flex-1 max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search by recipient name, email, or certificate ID…"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-9 pr-4 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-[var(--color-primary)] transition-colors shadow-2xs"
        />
      </div>

      {/* Status Segmented Buttons */}
      <div className="flex items-center gap-1 bg-gray-100/80 p-1 rounded-xl self-start sm:self-auto">
        {STATUSES.map((s) => (
          <button
            key={s.id}
            onClick={() => onStatusChange(s.id)}
            className={`px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all ${
              currentStatus === s.id
                ? "bg-white text-[var(--color-text)] shadow-xs"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
