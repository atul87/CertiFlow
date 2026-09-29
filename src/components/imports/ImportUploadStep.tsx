"use client";

import { useRef, useState, useCallback } from "react";
import { Upload, FileSpreadsheet, AlertCircle, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Template } from "@/types";

interface ImportUploadStepProps {
  templates: Template[];
  selectedTemplate: string;
  onSelectTemplate: (id: string) => void;
  selectedFile: File | null;
  onSelectFile: (file: File | null) => void;
  onUpload: () => Promise<void>;
  uploading: boolean;
  uploadError: string | null;
}

export function ImportUploadStep({
  templates,
  selectedTemplate,
  onSelectTemplate,
  selectedFile,
  onSelectFile,
  onUpload,
  uploading,
  uploadError,
}: ImportUploadStepProps) {
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const handleFileDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) onSelectFile(file);
    },
    [onSelectFile]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onSelectFile(file);
  };

  return (
    <div className="max-w-xl mx-auto space-y-5">
      <div className="text-center mb-6">
        <h2 className="text-[20px] font-bold text-[var(--color-text)]">Upload your recipient list</h2>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
          Supports CSV (.csv) and Excel (.xlsx, .xls) files up to 50 MB
        </p>
      </div>

      {/* Template selector */}
      <div>
        <label htmlFor="template-select" className="block text-[13px] font-semibold text-[var(--color-text)] mb-2">
          Certificate Template <span className="text-[var(--color-text-tertiary)] font-normal">(optional)</span>
        </label>
        <select
          id="template-select"
          value={selectedTemplate}
          onChange={(e) => onSelectTemplate(e.target.value)}
          className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] text-[14px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
        >
          <option value="">— Select template (detect later) —</option>
          {templates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleFileDrop}
        onClick={() => fileInput.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
          dragging
            ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] scale-[1.01]"
            : selectedFile
            ? "border-emerald-400 bg-emerald-50"
            : "border-gray-200 hover:border-[var(--color-border-hover)] hover:bg-gray-50/50"
        }`}
      >
        <input
          ref={fileInput}
          id="recipient-file-input"
          data-testid="recipient-file-input"
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={handleFileSelect}
        />
        {selectedFile ? (
          <>
            <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-3">
              <FileSpreadsheet className="w-6 h-6 text-emerald-600" />
            </div>
            <p className="font-semibold text-[var(--color-text)]">{selectedFile.name}</p>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
              {(selectedFile.size / 1024).toFixed(1)} KB · Click to change file
            </p>
          </>
        ) : (
          <>
            <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center mx-auto mb-3">
              <Upload className="w-6 h-6 text-gray-400" />
            </div>
            <p className="font-semibold text-[var(--color-text)]">Drop your file here or click to browse</p>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">CSV, XLSX, XLS · max 50 MB</p>
          </>
        )}
      </div>

      {uploadError && (
        <div className="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-xl text-[13px] text-red-700">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
          {uploadError}
        </div>
      )}

      {/* Guidance */}
      <div className="flex items-start gap-2.5 p-3.5 bg-blue-50 border border-blue-100 rounded-xl text-[12px] text-blue-700">
        <Info className="w-4 h-4 shrink-0 mt-0.5 text-blue-500" />
        <span>
          Include column headers in the first row. CertiFlow will auto-detect common field names like{" "}
          <strong>Name</strong>, <strong>Email</strong>, <strong>Course</strong>.
        </span>
      </div>

      <Button
        id="upload-analyze-btn"
        onClick={onUpload}
        loading={uploading}
        disabled={!selectedFile}
        className="w-full justify-center"
        size="lg"
      >
        <Upload className="w-4 h-4 mr-2" />
        Upload & Analyze
      </Button>
    </div>
  );
}
