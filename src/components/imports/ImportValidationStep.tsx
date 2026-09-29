"use client";

import { CheckCircle2, AlertCircle, Download, ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ValidationError {
  row: number;
  field: string;
  message: string;
}

interface ImportValidationStepProps {
  totalRows: number;
  validRows: number;
  invalidRows: number;
  errors: ValidationError[];
  onBack: () => void;
  onConfirm: () => Promise<void>;
  confirming: boolean;
}

export function ImportValidationStep({
  totalRows,
  validRows,
  invalidRows,
  errors,
  onBack,
  onConfirm,
  confirming,
}: ImportValidationStepProps) {
  const handleDownloadErrors = () => {
    const csvContent =
      "data:text/csv;charset=utf-8,Row,Field,Error\n" +
      errors.map((e) => `${e.row},"${e.field}","${e.message}"`).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "validation_errors.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-[18px] font-bold text-[var(--color-text)]">Validation Results</h2>
        <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
          Review rows before confirming the recipient import.
        </p>
      </div>

      {/* Validation metric cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-4 text-center">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">
            Total Rows
          </p>
          <p className="text-[24px] font-bold text-[var(--color-text)]">{totalRows.toLocaleString()}</p>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Valid</p>
          </div>
          <p className="text-[24px] font-bold text-emerald-700">{validRows.toLocaleString()}</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 mb-1">
            <AlertCircle className="w-3.5 h-3.5 text-red-600" />
            <p className="text-[11px] font-bold uppercase tracking-wider text-red-700">Errors</p>
          </div>
          <p className="text-[24px] font-bold text-red-700">{invalidRows.toLocaleString()}</p>
        </div>
      </div>

      {/* Error Breakdown table if any */}
      {invalidRows > 0 && (
        <div className="rounded-2xl border border-red-200 overflow-hidden shadow-xs">
          <div className="px-4 py-3 bg-red-50/70 border-b border-red-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-[13px] font-bold text-red-900">
                {invalidRows} Rows with Validation Errors
              </span>
            </div>
            <button
              onClick={handleDownloadErrors}
              className="inline-flex items-center gap-1.5 text-[11px] font-bold text-red-700 hover:text-red-900 hover:underline"
            >
              <Download className="w-3.5 h-3.5" />
              Download Error Report (CSV)
            </button>
          </div>
          <div className="divide-y divide-red-100 max-h-56 overflow-y-auto bg-white">
            {errors.map((err, i) => (
              <div key={i} className="px-4 py-2.5 flex items-center justify-between text-[12px]">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-gray-500">Row {err.row}</span>
                  <span className="font-semibold text-gray-800">{err.field}</span>
                </div>
                <span className="text-red-600">{err.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confirmation prompt */}
      <div className="p-4 rounded-xl bg-gray-50 border border-[var(--color-border)] text-[13px] text-[var(--color-text-secondary)]">
        {invalidRows > 0 ? (
          <p>
            Proceeding will import the <strong>{validRows.toLocaleString()} valid recipients</strong> and
            skip the invalid rows. You can fix and re-upload the skipped rows later.
          </p>
        ) : (
          <p>
            All <strong>{validRows.toLocaleString()} rows</strong> passed strict schema validation and are ready to be imported into your organization vault.
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-between pt-2">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Back to Mapping
        </Button>
        <Button
          onClick={onConfirm}
          loading={confirming}
          disabled={validRows === 0}
        >
          Confirm & Import {validRows.toLocaleString()} Records
          <ArrowRight className="w-4 h-4 ml-1.5" />
        </Button>
      </div>
    </div>
  );
}
