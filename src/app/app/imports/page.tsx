"use client";

import { ImportWizard, ImportHistory } from "@/components/imports";

export default function ImportsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-screen-xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)] tracking-tight">
            Import Center
          </h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-0.5">
            Upload CSV or Excel files, map dynamic variables, and validate records for bulk certificate issuance.
          </p>
        </div>
      </div>

      {/* Wizard Card (Upload -> Map -> Validate -> Confirm) */}
      <ImportWizard />

      {/* Historical Uploads */}
      <ImportHistory />
    </div>
  );
}
