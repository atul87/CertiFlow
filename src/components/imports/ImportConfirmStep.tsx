"use client";

import Link from "next/link";
import { CheckCircle2, ArrowRight, RotateCcw, Zap, FileSpreadsheet } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ImportConfirmStepProps {
  validRows: number;
  filename?: string;
  onReset: () => void;
}

export function ImportConfirmStep({
  validRows,
  filename,
  onReset,
}: ImportConfirmStepProps) {
  return (
    <div className="max-w-md mx-auto text-center py-6 space-y-6">
      <div className="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto text-emerald-600 shadow-sm">
        <CheckCircle2 className="w-8 h-8" />
      </div>

      <div>
        <h2 className="text-[22px] font-bold text-[var(--color-text)]">Import Completed!</h2>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1.5">
          Successfully imported <strong>{validRows.toLocaleString()} recipients</strong> from{" "}
          <strong>{filename || "your file"}</strong> into your organization records.
        </p>
      </div>

      <div className="p-4 rounded-2xl bg-gray-50 border border-[var(--color-border)] text-left space-y-2">
        <div className="flex items-center justify-between text-[12px]">
          <span className="text-[var(--color-text-secondary)]">Imported Records</span>
          <span className="font-bold text-emerald-600">{validRows.toLocaleString()} valid</span>
        </div>
        <div className="flex items-center justify-between text-[12px]">
          <span className="text-[var(--color-text-secondary)]">Status</span>
          <span className="font-bold text-gray-800">Ready for batch issuance</span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button id="import-another-btn" variant="outline" onClick={onReset} className="flex-1 justify-center">
          <RotateCcw className="w-4 h-4 mr-1.5" />
          Import Another File
        </Button>
        <Link href="/app/issuance?create=1" className="flex-1">
          <Button id="launch-issuance-btn" className="w-full justify-center">
            <Zap className="w-4 h-4 mr-1.5" />
            Launch Batch Issuance
          </Button>
        </Link>
      </div>
    </div>
  );
}
