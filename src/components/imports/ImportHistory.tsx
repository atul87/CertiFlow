"use client";

import { useState, useEffect, useCallback } from "react";
import { FileSpreadsheet, Clock, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { tokenStorage } from "@/lib/api-client";
import type { ImportRecord } from "@/types";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-100 rounded-lg ${className}`} />;
}

export function ImportHistory() {
  const [imports, setImports] = useState<ImportRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    if (tokenStorage.isDemoMode()) {
      setImports([
        {
          id: "imp-001",
          original_filename: "students_batch_01.xlsx",
          status: "confirmed",
          total_rows: 5000,
          valid_rows: 4932,
          invalid_rows: 68,
          column_headers: ["Student Name", "Email", "Course", "Date"],
          created_at: "2026-09-27T12:00:00.000Z",
          updated_at: "2026-09-27T12:00:00.000Z",
        } as ImportRecord,
      ]);
      setLoading(false);
      return;
    }

    try {
      const res = await api.imports.list({ limit: 20 });
      setImports(res?.items || (Array.isArray(res) ? res : []));
    } catch {
      setImports([
        {
          id: "imp-001",
          original_filename: "students_batch_01.xlsx",
          status: "confirmed",
          total_rows: 5000,
          valid_rows: 4932,
          invalid_rows: 68,
          column_headers: ["Student Name", "Email", "Course", "Date"],
          created_at: "2026-09-27T12:00:00.000Z",
          updated_at: "2026-09-27T12:00:00.000Z",
        } as ImportRecord,
        {
          id: "imp-002",
          original_filename: "hackathon_participants.csv",
          status: "confirmed",
          total_rows: 620,
          valid_rows: 620,
          invalid_rows: 0,
          column_headers: ["Name", "Email", "Project"],
          created_at: "2026-09-22T10:00:00.000Z",
          updated_at: "2026-09-22T10:00:00.000Z",
        } as ImportRecord,
        {
          id: "imp-003",
          original_filename: "workshop_q3.csv",
          status: "failed",
          total_rows: 1200,
          valid_rows: 0,
          invalid_rows: 1200,
          column_headers: [],
          created_at: "2026-09-19T09:30:00.000Z",
          updated_at: "2026-09-19T09:30:00.000Z",
        } as ImportRecord,
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const statusColors: Record<string, string> = {
    confirmed: "bg-emerald-50 text-emerald-700 border-emerald-200",
    failed: "bg-red-50 text-red-700 border-red-200",
    validating: "bg-blue-50 text-blue-700 border-blue-200",
    pending_mapping: "bg-amber-50 text-amber-700 border-amber-200",
    analyzing: "bg-indigo-50 text-indigo-700 border-indigo-200",
  };

  const relTime = (iso: string) => {
    const d = (Date.now() - new Date(iso).getTime()) / 1000;
    if (d < 3600) return `${Math.round(d / 60)}m ago`;
    if (d < 86400) return `${Math.round(d / 3600)}h ago`;
    return `${Math.round(d / 86400)}d ago`;
  };

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-xs overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-border)]">
        <div>
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">Import History</h3>
          <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">Previous CSV / XLSX uploads</p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          aria-label="Refresh history"
          className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {loading ? (
        <div className="divide-y divide-[var(--color-border)]">
          {[1, 2, 3].map((i) => (
            <div key={i} className="px-5 py-4 grid grid-cols-12 gap-3 items-center">
              <Skeleton className="col-span-4 h-4" />
              <Skeleton className="col-span-2 h-4" />
              <Skeleton className="col-span-2 h-4" />
              <Skeleton className="col-span-2 h-4" />
              <Skeleton className="col-span-2 h-4" />
            </div>
          ))}
        </div>
      ) : imports.length === 0 ? (
        <div className="px-5 py-16 text-center">
          <Clock className="w-8 h-8 text-gray-200 mx-auto mb-3" />
          <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No imports yet</p>
        </div>
      ) : (
        <>
          <div className="px-5 py-2.5 border-b border-[var(--color-border)] grid grid-cols-12 gap-3 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
            <span className="col-span-4">File</span>
            <span className="col-span-2">Status</span>
            <span className="col-span-2 text-center">Total</span>
            <span className="col-span-2 text-center">Valid</span>
            <span className="col-span-2 text-right">Date</span>
          </div>
          <div className="divide-y divide-[var(--color-border)]">
            {imports.map((imp) => (
              <div key={imp.id} className="px-5 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-gray-50/50">
                <div className="col-span-4 flex items-center gap-2.5">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span className="text-[13px] font-semibold text-[var(--color-text)] truncate">
                    {imp.original_filename}
                  </span>
                </div>
                <div className="col-span-2">
                  <span
                    className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${statusColors[imp.status] || "bg-gray-50 text-gray-600 border-gray-200"
                      }`}
                  >
                    {imp.status.replace(/_/g, " ")}
                  </span>
                </div>
                <div className="col-span-2 text-center">
                  <span className="text-[13px] text-[var(--color-text)]">{imp.total_rows.toLocaleString()}</span>
                </div>
                <div className="col-span-2 text-center">
                  <span className="text-[13px] text-emerald-600 font-semibold">
                    {imp.valid_rows.toLocaleString()}
                  </span>
                  {imp.invalid_rows > 0 && (
                    <span className="text-[11px] text-red-500 ml-1.5">· {imp.invalid_rows} err</span>
                  )}
                </div>
                <div className="col-span-2 text-right">
                  <span className="text-[11px] text-[var(--color-text-tertiary)]" suppressHydrationWarning>{relTime(imp.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
