"use client";

import { use, useState } from "react";
import { EditorTopBar } from "@/features/editor/components/EditorTopBar";
import { EditorLeftSidebar } from "@/features/editor/components/EditorLeftSidebar";
import { EditorCanvas } from "@/features/editor/components/EditorCanvas";
import { EditorRightInspector } from "@/features/editor/components/EditorRightInspector";
import { ExportModal } from "@/features/editor/components/ExportModal";

export default function CertificateEditorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[var(--color-background)]">
      {/* 1. Global Editor Navigation & Actions Bar */}
      <EditorTopBar
        projectId={id || "proj-ai-2026"}
        projectName="AI Workshop 2026"
        onOpenExportModal={() => setIsExportModalOpen(true)}
      />

      {/* 2. Main Studio Workbench (Left Tools | Center Canvas | Right Inspector) */}
      <div className="flex-1 flex overflow-hidden relative">
        <EditorLeftSidebar />
        <EditorCanvas />
        <EditorRightInspector />
      </div>

      {/* 3. Export Sample Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />
    </div>
  );
}
