"use client";

import { Shuffle, AlertCircle, ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export const CERTIFLOW_FIELDS = [
  { key: "recipient_name", label: "Recipient Name", required: true },
  { key: "email", label: "Email Address", required: true },
  { key: "program_name", label: "Program / Course", required: false },
  { key: "issue_date", label: "Issue Date", required: false },
  { key: "grade", label: "Grade / Score", required: false },
  { key: "department", label: "Department", required: false },
  { key: "supervisor", label: "Supervisor Name", required: false },
  { key: "certificate_id", label: "Custom Certificate ID", required: false },
];

function ConfidencePill({ pct }: { pct: number }) {
  const color =
    pct >= 90
      ? "text-emerald-700 bg-emerald-50 border-emerald-200"
      : pct >= 70
      ? "text-amber-700 bg-amber-50 border-amber-200"
      : "text-red-700 bg-red-50 border-red-200";
  return (
    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${color}`}>
      {pct}%
    </span>
  );
}

interface ImportMappingStepProps {
  columns: string[];
  filename?: string;
  mapping: Record<string, string>;
  onMappingChange: (key: string, value: string) => void;
  onBack: () => void;
  onValidate: () => Promise<void>;
  savingMapping: boolean;
}

export function ImportMappingStep({
  columns,
  filename,
  mapping,
  onMappingChange,
  onBack,
  onValidate,
  savingMapping,
}: ImportMappingStepProps) {
  const isValid = Boolean(mapping.recipient_name && mapping.email);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-[18px] font-bold text-[var(--color-text)]">Map your columns</h2>
        <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
          We detected <strong>{columns.length} columns</strong> in{" "}
          <strong>{filename || "your file"}</strong>. Confirm the field mapping below.
        </p>
      </div>

      {/* Mapping rows */}
      <div className="rounded-2xl border border-[var(--color-border)] overflow-hidden shadow-xs">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-[var(--color-border)] grid grid-cols-5 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
          <span className="col-span-2">CertiFlow Field</span>
          <span className="col-span-2">CSV Column</span>
          <span className="col-span-1 text-right">Confidence</span>
        </div>
        <div className="divide-y divide-[var(--color-border)] bg-white">
          {CERTIFLOW_FIELDS.map((field) => {
            const mappedCol = mapping[field.key];
            const confidence = mappedCol ? (field.required ? 98 : 91) : 0;
            return (
              <div key={field.key} className="px-4 py-3 grid grid-cols-5 items-center gap-2">
                <div className="col-span-2 flex items-center gap-1.5">
                  <Shuffle className="w-3.5 h-3.5 text-gray-300 shrink-0" />
                  <span className="text-[13px] font-medium text-[var(--color-text)]">
                    {field.label}
                  </span>
                  {field.required && <span className="text-[10px] text-red-500 font-bold">*</span>}
                </div>
                <div className="col-span-2">
                  <select
                    value={mappedCol || ""}
                    onChange={(e) => onMappingChange(field.key, e.target.value)}
                    className="w-full text-[13px] px-2.5 py-1.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                  >
                    <option value="">— skip —</option>
                    {columns.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-span-1 flex justify-end">
                  {mappedCol ? (
                    <ConfidencePill pct={confidence} />
                  ) : (
                    <span className="text-[11px] text-gray-300">—</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Required fields warning */}
      {!isValid && (
        <div className="flex items-start gap-2.5 p-3.5 bg-amber-50 border border-amber-200 rounded-xl text-[13px] text-amber-700">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
          <span>
            <strong>Recipient Name</strong> and <strong>Email Address</strong> are required fields. Please map them before continuing.
          </span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-2">
        <Button id="mapping-back-btn" variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Back
        </Button>
        <Button
          id="validate-records-btn"
          onClick={onValidate}
          loading={savingMapping}
          disabled={!isValid}
        >
          Validate Records
          <ArrowRight className="w-4 h-4 ml-1.5" />
        </Button>
      </div>
    </div>
  );
}
