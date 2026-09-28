"use client";

import { useState } from "react";
import { Download, FileText, Image as ImageIcon, CheckCircle, Sparkles } from "lucide-react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { useEditorStore } from "../use-editor-store";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ExportModal({ isOpen, onClose }: ExportModalProps) {
  const { recipients, activeRecipientIndex } = useEditorStore();
  const currentRecipient = recipients[activeRecipientIndex] || recipients[0];

  const [format, setFormat] = useState<"pdf" | "png">("pdf");
  const [dpi, setDpi] = useState<"300" | "150">("300");
  const [isExporting, setIsExporting] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleExport = () => {
    setIsExporting(true);
    setDownloadSuccess(false);

    setTimeout(() => {
      setIsExporting(false);
      setDownloadSuccess(true);

      // Trigger dummy download file
      const fileName = `${currentRecipient.name.toLowerCase().replace(/\s+/g, "_")}_certificate.${format}`;
      const blob = new Blob(["Sample Certificate Binary Data"], { type: format === "pdf" ? "application/pdf" : "image/png" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 1200);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Sample Certificate"
      description="Download a high-resolution sample of the currently previewed recipient record."
      size="md"
    >
      <div className="space-y-5 py-2">
        {/* Recipient summary */}
        <div className="p-3 rounded-xl bg-gray-50 border border-[var(--color-border)] flex items-center justify-between text-[13px]">
          <div>
            <p className="font-semibold text-gray-800">{currentRecipient.name}</p>
            <p className="text-[11px] text-gray-500 font-mono">
              ID: {currentRecipient.certificateId} · Row #{currentRecipient.row}
            </p>
          </div>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            Preview Active
          </span>
        </div>

        {/* Format Selection */}
        <div>
          <label className="text-[12px] font-semibold text-gray-700 block mb-2">Export Format</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setFormat("pdf")}
              className={`p-3 rounded-xl border text-left transition-all flex items-start gap-2.5 ${
                format === "pdf"
                  ? "border-[var(--color-primary)] bg-indigo-50/30 text-[var(--color-primary)]"
                  : "border-[var(--color-border)] hover:border-gray-300"
              }`}
            >
              <FileText className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="text-[13px] font-bold text-gray-900">Vector PDF</p>
                <p className="text-[11px] text-gray-500">Sharper vector text & clickable QR code</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setFormat("png")}
              className={`p-3 rounded-xl border text-left transition-all flex items-start gap-2.5 ${
                format === "png"
                  ? "border-[var(--color-primary)] bg-indigo-50/30 text-[var(--color-primary)]"
                  : "border-[var(--color-border)] hover:border-gray-300"
              }`}
            >
              <ImageIcon className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="text-[13px] font-bold text-gray-900">High-Res PNG</p>
                <p className="text-[11px] text-gray-500">Flattened raster for web sharing & social</p>
              </div>
            </button>
          </div>
        </div>

        {/* DPI Quality */}
        <div>
          <label className="text-[12px] font-semibold text-gray-700 block mb-1">Resolution & DPI</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setDpi("300")}
              className={`flex-1 py-2 px-3 rounded-lg text-[12px] font-medium border text-center transition-all ${
                dpi === "300"
                  ? "bg-gray-900 text-white border-gray-900"
                  : "border-[var(--color-border)] text-gray-700 hover:bg-gray-50"
              }`}
            >
              300 DPI (Commercial Print Ready)
            </button>
            <button
              type="button"
              onClick={() => setDpi("150")}
              className={`flex-1 py-2 px-3 rounded-lg text-[12px] font-medium border text-center transition-all ${
                dpi === "150"
                  ? "bg-gray-900 text-white border-gray-900"
                  : "border-[var(--color-border)] text-gray-700 hover:bg-gray-50"
              }`}
            >
              150 DPI (Fast Screen / Web)
            </button>
          </div>
        </div>

        {downloadSuccess && (
          <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[12px] flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Sample successfully generated and downloaded to your computer!</span>
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2 border-t border-[var(--color-border)]">
          <Button variant="secondary" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? (
              <span className="flex items-center gap-1.5">
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Rendering Vector Output...
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <Download className="w-3.5 h-3.5" />
                Download {format.toUpperCase()}
              </span>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
