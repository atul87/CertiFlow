"use client";

import Link from "next/link";
import {
  ArrowLeft,
  Undo2,
  Redo2,
  Grid,
  ShieldCheck,
  Download,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useEditorStore } from "../use-editor-store";

interface EditorTopBarProps {
  projectId: string;
  projectName?: string;
  onOpenExportModal: () => void;
}

export function EditorTopBar({
  projectId,
  projectName = "AI Workshop 2026",
  onOpenExportModal,
}: EditorTopBarProps) {
  const {
    zoom,
    setZoom,
    showGrid,
    toggleGrid,
    showSafeMargin,
    toggleSafeMargin,
    historyIndex,
    history,
    undo,
    redo,
    recipients,
    activeRecipientIndex,
    setActiveRecipientIndex,
    isSaving,
    lastSavedAt,
    saveCanvas,
  } = useEditorStore();

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  const handlePrevRecipient = () => {
    if (activeRecipientIndex > 0) {
      setActiveRecipientIndex(activeRecipientIndex - 1);
    }
  };

  const handleNextRecipient = () => {
    if (activeRecipientIndex < recipients.length - 1) {
      setActiveRecipientIndex(activeRecipientIndex + 1);
    }
  };

  return (
    <header className="h-14 border-b border-[var(--color-border)] bg-white px-4 flex items-center justify-between select-none z-30 shrink-0">
      {/* Left: Navigation & Project Context */}
      <div className="flex items-center gap-3">
        <Link
          href={`/app/projects/${projectId}`}
          className="p-1.5 rounded-lg text-gray-500 hover:text-black hover:bg-gray-100 transition-colors"
          title="Back to Project Overview"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>

        <div className="h-4 w-px bg-gray-200" />

        <div className="flex items-center gap-2">
          <span className="font-semibold text-[14px] text-[var(--color-text)]">
            {projectName}
          </span>
          <Badge variant="outline" className="text-[10px] font-mono py-0 text-gray-500">
            A4 300 DPI
          </Badge>
        </div>

        {/* History Controls */}
        <div className="flex items-center gap-0.5 ml-2">
          <button
            onClick={undo}
            disabled={!canUndo}
            className={`p-1.5 rounded-md transition-colors ${
              canUndo
                ? "text-gray-600 hover:bg-gray-100 hover:text-black"
                : "text-gray-300 cursor-not-allowed"
            }`}
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={redo}
            disabled={!canRedo}
            className={`p-1.5 rounded-md transition-colors ${
              canRedo
                ? "text-gray-600 hover:bg-gray-100 hover:text-black"
                : "text-gray-300 cursor-not-allowed"
            }`}
            title="Redo (Ctrl+Y)"
          >
            <Redo2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Middle: Recipient Data Switcher */}
      <div className="flex items-center gap-2 bg-[var(--color-background)] px-2.5 py-1 rounded-lg border border-[var(--color-border)]">
        <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">
          Data Record:
        </span>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handlePrevRecipient}
            disabled={activeRecipientIndex === 0}
            title="Previous Recipient"
            className="p-1 rounded text-gray-500 hover:text-black hover:bg-white disabled:opacity-30 disabled:hover:bg-transparent"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>

          <select
            value={activeRecipientIndex}
            onChange={(e) => setActiveRecipientIndex(Number(e.target.value))}
            className="text-[12px] font-medium bg-transparent border-0 py-0.5 pl-1 pr-6 cursor-pointer focus:ring-0 text-gray-800"
          >
            {recipients.map((r, i) => (
              <option key={r.id} value={i}>
                #{r.row}: {r.name} ({r.certificateId})
              </option>
            ))}
          </select>

          <button
            onClick={handleNextRecipient}
            disabled={activeRecipientIndex === recipients.length - 1}
            title="Next Recipient"
            className="p-1 rounded text-gray-500 hover:text-black hover:bg-white disabled:opacity-30 disabled:hover:bg-transparent"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Right: View Options & Actions */}
      <div className="flex items-center gap-2">
        {/* View toggles */}
        <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
          <button
            onClick={toggleGrid}
            className={`p-1.5 rounded-md text-[12px] font-medium transition-colors ${
              showGrid
                ? "bg-white text-[var(--color-primary)] shadow-2xs font-semibold"
                : "text-gray-500 hover:text-black"
            }`}
            title="Toggle Alignment Grid"
          >
            <Grid className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={toggleSafeMargin}
            className={`p-1.5 rounded-md text-[12px] font-medium transition-colors ${
              showSafeMargin
                ? "bg-white text-[var(--color-primary)] shadow-2xs font-semibold"
                : "text-gray-500 hover:text-black"
            }`}
            title="Toggle Safe Margins (Print Boundaries)"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Zoom selector */}
        <select
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
          className="text-[12px] bg-gray-50 border border-[var(--color-border)] rounded-lg px-2 py-1 text-gray-700 font-mono"
        >
          <option value={0.6}>60%</option>
          <option value={0.8}>80%</option>
          <option value={1.0}>100%</option>
          <option value={1.25}>125%</option>
          <option value={1.5}>150%</option>
        </select>

        <div className="h-4 w-px bg-gray-200" />

        {/* Save indicator button */}
        <button
          onClick={saveCanvas}
          className="text-[11px] text-gray-500 flex items-center gap-1.5 hover:text-gray-800 transition-colors px-2 py-1 rounded"
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isSaving
                ? "bg-amber-400 animate-ping"
                : "bg-emerald-500"
            }`}
          />
          <span>{isSaving ? "Saving..." : lastSavedAt}</span>
        </button>

        {/* Export sample */}
        <Button
          size="sm"
          variant="secondary"
          className="h-8 text-[12px]"
          onClick={onOpenExportModal}
        >
          <Download className="w-3 h-3 mr-1" />
          Sample PDF
        </Button>

        {/* Next step: Step 4 Live Preview Studio */}
        <Button size="sm" className="h-8 text-[12px] font-semibold gap-1.5 shadow-xs" asChild>
          <Link href={`/app/projects/${projectId}/preview`}>
            <span>Step 4: Live Preview</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </Button>
      </div>
    </header>
  );
}
