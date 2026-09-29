"use client";

import { useState } from "react";
import { X, Zap, Award, FileSpreadsheet, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Template, ImportRecord } from "@/types";

interface IssuanceCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  templates: Template[];
  imports: ImportRecord[];
  onCreateJob: (payload: {
    template_id: string;
    import_id?: string;
    name: string;
    send_email: boolean;
    priority: "normal" | "high";
  }) => Promise<void>;
  loading: boolean;
}

export function IssuanceCreateModal({
  isOpen,
  onClose,
  templates,
  imports,
  onCreateJob,
  loading,
}: IssuanceCreateModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState(templates[0]?.id || "");
  const [selectedImport, setSelectedImport] = useState(imports[0]?.id || "");
  const [jobName, setJobName] = useState("");
  const [sendEmail, setSendEmail] = useState(true);
  const [priority, setPriority] = useState<"normal" | "high">("normal");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTemplate) return;

    await onCreateJob({
      template_id: selectedTemplate,
      import_id: selectedImport || undefined,
      name: jobName.trim() || `Batch Issuance - ${new Date().toLocaleDateString()}`,
      send_email: sendEmail,
      priority,
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-2xl max-w-lg w-full overflow-hidden animate-in fade-in-50 zoom-in-95">
        <div className="px-6 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[var(--color-primary-subtle)] text-[var(--color-primary)] flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
            <h2 className="text-[16px] font-bold text-[var(--color-text)]">New Issuance Batch</h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-[13px] font-semibold text-[var(--color-text)] mb-1.5">
              Batch Name
            </label>
            <input
              type="text"
              placeholder="e.g., Q3 Full Stack Bootcamp Graduation"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              className="w-full px-3.5 py-2.2 rounded-lg border border-[var(--color-border)] text-[13px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
            />
          </div>

          <div>
            <label className="block text-[13px] font-semibold text-[var(--color-text)] mb-1.5">
              Certificate Template *
            </label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              required
              className="w-full px-3.5 py-2.2 rounded-lg border border-[var(--color-border)] text-[13px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
            >
              <option value="" disabled>Select template</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[13px] font-semibold text-[var(--color-text)] mb-1.5">
              Recipient Data Source
            </label>
            <select
              value={selectedImport}
              onChange={(e) => setSelectedImport(e.target.value)}
              className="w-full px-3.5 py-2.2 rounded-lg border border-[var(--color-border)] text-[13px] bg-[var(--color-background)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
            >
              <option value="">Demo Seed Recipients (450 rows)</option>
              {imports.map((imp) => (
                <option key={imp.id} value={imp.id}>
                  {imp.original_filename} ({imp.valid_rows} valid recipients)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="flex items-center gap-2 p-3 rounded-xl border border-[var(--color-border)] bg-gray-50/50">
              <input
                id="send-email-check"
                type="checkbox"
                checked={sendEmail}
                onChange={(e) => setSendEmail(e.target.checked)}
                className="w-4 h-4 rounded text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
              <label htmlFor="send-email-check" className="text-[12px] font-medium text-[var(--color-text)]">
                Email certificates automatically
              </label>
            </div>

            <div className="p-3 rounded-xl border border-[var(--color-border)] bg-gray-50/50">
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as "normal" | "high")}
                className="w-full text-[12px] bg-transparent font-semibold text-[var(--color-text)] focus:outline-none"
              >
                <option value="normal">Standard Queue</option>
                <option value="high">High Priority</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" loading={loading} disabled={!selectedTemplate}>
              <Zap className="w-4 h-4 mr-1.5" />
              Launch Batch
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
