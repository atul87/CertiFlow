"use client";

import { useState } from "react";
import {
  Type,
  Tags,
  QrCode,
  Stamp,
  PenTool,
  Layers as LayersIcon,
  LayoutTemplate,
  Plus,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Trash2,
  Copy,
  ChevronUp,
  ChevronDown,
  GripVertical,
  Minus,
  Sparkles,
} from "lucide-react";
import { useEditorStore } from "../use-editor-store";
import { TEMPLATE_PRESETS } from "../sample-data";

export function EditorLeftSidebar() {
  const [activeTab, setActiveTab] = useState<"elements" | "layers" | "templates">("elements");

  const {
    layers,
    selectedLayerId,
    selectLayer,
    addLayer,
    removeLayer,
    duplicateLayer,
    moveLayer,
    toggleLayerVisibility,
    toggleLayerLock,
    loadPreset,
  } = useEditorStore();

  const handleAddDynamicTag = (tag: string, label: string) => {
    addLayer({
      type: "variable",
      name: label,
      variableKey: tag,
      content: `{{${tag}}}`,
      fontSize: 28,
      fontFamily: "Playfair Display",
      fontWeight: "bold",
      color: "#111111",
      textAlign: "center",
      autoFit: true,
      minFontSize: 16,
      x: 50,
      y: 50,
    });
  };

  const handleAddStaticText = (type: "heading" | "body" | "subheading") => {
    if (type === "heading") {
      addLayer({
        type: "text",
        name: "Heading Text",
        content: "Certificate Title",
        fontSize: 36,
        fontFamily: "Playfair Display",
        fontWeight: "bold",
        color: "#111111",
        textAlign: "center",
        x: 50,
        y: 30,
      });
    } else if (type === "subheading") {
      addLayer({
        type: "text",
        name: "Subheading Text",
        content: "THIS CERTIFICATE IS PROUDLY PRESENTED TO",
        fontSize: 12,
        fontFamily: "Inter",
        fontWeight: "600",
        color: "#6B7280",
        letterSpacing: 2,
        textTransform: "uppercase",
        textAlign: "center",
        x: 50,
        y: 40,
      });
    } else {
      addLayer({
        type: "text",
        name: "Body Text",
        content: "for exemplary performance and dedication shown throughout the course curriculum.",
        fontSize: 13,
        fontFamily: "Inter",
        fontWeight: "normal",
        color: "#4B5563",
        textAlign: "center",
        x: 50,
        y: 58,
      });
    }
  };

  const handleAddQR = () => {
    addLayer({
      type: "qr",
      name: "QR Verification",
      variableKey: "CERTIFICATE_ID",
      content: "{{CERTIFICATE_ID}}",
      qrData: "https://certiflow.app/verify/{{CERTIFICATE_ID}}",
      x: 80,
      y: 82,
      width: 12,
      height: 12,
      color: "#111111",
      textAlign: "center",
    });
  };

  const handleAddSignature = () => {
    addLayer({
      type: "signature",
      name: "Authorized Signature",
      content: "Authorized Signatory",
      signerName: "Dr. Jane Doe",
      signerTitle: "Director of Certification",
      x: 24,
      y: 82,
      width: 24,
      height: 10,
      fontFamily: "Great Vibes",
      fontSize: 18,
      color: "#111111",
      textAlign: "center",
    });
  };

  const handleAddSeal = () => {
    addLayer({
      type: "badge",
      name: "Official Golden Seal",
      content: "VERIFIED CREDENTIAL",
      x: 50,
      y: 84,
      width: 14,
      height: 14,
      shapeType: "seal",
      fill: "#FEF3C7",
      stroke: "#D97706",
      strokeWidth: 2,
      color: "#B45309",
      fontSize: 8,
      fontFamily: "Inter",
      fontWeight: "bold",
      textAlign: "center",
    });
  };

  const handleAddDivider = () => {
    addLayer({
      type: "divider",
      name: "Decorative Line",
      content: "",
      x: 50,
      y: 50,
      width: 40,
      height: 1,
      stroke: "#D1D5DB",
      strokeWidth: 1,
      color: "#D1D5DB",
      fontSize: 1,
      fontFamily: "Inter",
      fontWeight: "normal",
      textAlign: "center",
    });
  };

  return (
    <aside className="w-72 bg-white border-r border-[var(--color-border)] flex flex-col shrink-0 select-none z-20 overflow-hidden">
      {/* Top Sidebar Navigation Tabs */}
      <div className="flex border-b border-[var(--color-border)] bg-gray-50/50 p-1">
        <button
          onClick={() => setActiveTab("elements")}
          className={`flex-1 py-2 rounded-lg text-[12px] font-semibold flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "elements"
              ? "bg-white text-[var(--color-text)] shadow-2xs"
              : "text-gray-500 hover:text-gray-800"
          }`}
        >
          <Type className="w-3.5 h-3.5" />
          Elements
        </button>
        <button
          onClick={() => setActiveTab("layers")}
          className={`flex-1 py-2 rounded-lg text-[12px] font-semibold flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "layers"
              ? "bg-white text-[var(--color-text)] shadow-2xs"
              : "text-gray-500 hover:text-gray-800"
          }`}
        >
          <LayersIcon className="w-3.5 h-3.5" />
          Layers ({layers.length})
        </button>
        <button
          onClick={() => setActiveTab("templates")}
          className={`flex-1 py-2 rounded-lg text-[12px] font-semibold flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "templates"
              ? "bg-white text-[var(--color-text)] shadow-2xs"
              : "text-gray-500 hover:text-gray-800"
          }`}
        >
          <LayoutTemplate className="w-3.5 h-3.5" />
          Presets
        </button>
      </div>

      {/* TAB CONTENT */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* ===================== TAB 1: ELEMENTS & FIELDS ===================== */}
        {activeTab === "elements" && (
          <div className="space-y-6">
            {/* Dynamic CSV Variables */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
                  CSV Dynamic Variables
                </span>
                <span className="text-[10px] bg-indigo-50 text-[var(--color-primary)] font-semibold px-1.5 py-0.5 rounded">
                  Live Bind
                </span>
              </div>
              <p className="text-[11px] text-gray-500 mb-3">
                Click any placeholder to drop onto canvas. Replaced per recipient row.
              </p>

              <div className="grid grid-cols-1 gap-1.5">
                {[
                  { tag: "NAME", label: "Recipient Name", col: "Full Name" },
                  { tag: "COURSE", label: "Course / Event", col: "Course" },
                  { tag: "DATE", label: "Issue Date", col: "Date" },
                  { tag: "SCORE", label: "Grade / Score", col: "Score" },
                  { tag: "CERTIFICATE_ID", label: "Certificate ID", col: "Unique UUID" },
                ].map((item) => (
                  <button
                    key={item.tag}
                    onClick={() => handleAddDynamicTag(item.tag, item.label)}
                    className="p-2.5 rounded-xl border border-[var(--color-border)] hover:border-[var(--color-primary)] bg-white hover:bg-indigo-50/30 transition-all flex items-center justify-between group text-left"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center font-mono font-bold text-[11px]">
                        {"{ }"}
                      </span>
                      <div>
                        <p className="text-[12px] font-semibold text-gray-800">{item.label}</p>
                        <p className="text-[10px] text-gray-400 font-mono">{"{{" + item.tag + "}}"}</p>
                      </div>
                    </div>
                    <Plus className="w-3.5 h-3.5 text-gray-300 group-hover:text-[var(--color-primary)] transition-colors" />
                  </button>
                ))}
              </div>
            </div>

            {/* Typography Blocks */}
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-2">
                Static Text Blocks
              </span>
              <div className="space-y-1.5">
                <button
                  onClick={() => handleAddStaticText("heading")}
                  className="w-full p-2.5 rounded-xl border border-[var(--color-border)] hover:border-gray-400 bg-white transition-all text-left flex items-center justify-between group"
                >
                  <span className="text-[14px] font-bold font-serif text-gray-800">
                    Add Heading
                  </span>
                  <Plus className="w-3.5 h-3.5 text-gray-300 group-hover:text-black" />
                </button>
                <button
                  onClick={() => handleAddStaticText("subheading")}
                  className="w-full p-2.5 rounded-xl border border-[var(--color-border)] hover:border-gray-400 bg-white transition-all text-left flex items-center justify-between group"
                >
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-600">
                    Add Subtitle / Pre-title
                  </span>
                  <Plus className="w-3.5 h-3.5 text-gray-300 group-hover:text-black" />
                </button>
                <button
                  onClick={() => handleAddStaticText("body")}
                  className="w-full p-2.5 rounded-xl border border-[var(--color-border)] hover:border-gray-400 bg-white transition-all text-left flex items-center justify-between group"
                >
                  <span className="text-[12px] text-gray-600">Add Paragraph Description</span>
                  <Plus className="w-3.5 h-3.5 text-gray-300 group-hover:text-black" />
                </button>
              </div>
            </div>

            {/* Credential Seals & Signatures */}
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-2">
                Trust & Verification Elements
              </span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleAddQR}
                  className="p-3 rounded-xl border border-[var(--color-border)] hover:border-[var(--color-primary)] bg-white hover:bg-indigo-50/20 text-center flex flex-col items-center gap-1.5 transition-all group"
                >
                  <QrCode className="w-5 h-5 text-[var(--color-primary)]" />
                  <span className="text-[11px] font-semibold text-gray-700">QR Code</span>
                </button>

                <button
                  onClick={handleAddSeal}
                  className="p-3 rounded-xl border border-[var(--color-border)] hover:border-amber-400 bg-white hover:bg-amber-50/30 text-center flex flex-col items-center gap-1.5 transition-all group"
                >
                  <Stamp className="w-5 h-5 text-amber-600" />
                  <span className="text-[11px] font-semibold text-gray-700">Gold Seal</span>
                </button>

                <button
                  onClick={handleAddSignature}
                  className="p-3 rounded-xl border border-[var(--color-border)] hover:border-gray-400 bg-white hover:bg-gray-50 text-center flex flex-col items-center gap-1.5 transition-all group"
                >
                  <PenTool className="w-5 h-5 text-gray-700" />
                  <span className="text-[11px] font-semibold text-gray-700">Signature</span>
                </button>

                <button
                  onClick={handleAddDivider}
                  className="p-3 rounded-xl border border-[var(--color-border)] hover:border-gray-400 bg-white hover:bg-gray-50 text-center flex flex-col items-center gap-1.5 transition-all group"
                >
                  <Minus className="w-5 h-5 text-gray-500" />
                  <span className="text-[11px] font-semibold text-gray-700">Divider</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ===================== TAB 2: LAYERS LIST ===================== */}
        {activeTab === "layers" && (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
                Layer Hierarchy
              </span>
              <span className="text-[10px] text-gray-400">Top to Bottom</span>
            </div>

            <div className="space-y-1">
              {layers.map((layer, index) => {
                const isSelected = selectedLayerId === layer.id;
                return (
                  <div
                    key={layer.id}
                    onClick={() => selectLayer(layer.id)}
                    className={`p-2 rounded-xl border transition-all flex items-center justify-between text-[12px] cursor-pointer ${
                      isSelected
                        ? "bg-indigo-50/70 border-[var(--color-primary)] shadow-2xs"
                        : "bg-white border-[var(--color-border)] hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <GripVertical className="w-3.5 h-3.5 text-gray-300 shrink-0" />
                      <div className="truncate">
                        <p
                          className={`font-semibold truncate ${
                            isSelected ? "text-[var(--color-primary)]" : "text-gray-800"
                          }`}
                        >
                          {layer.name}
                        </p>
                        <p className="text-[10px] text-gray-400 font-mono truncate">
                          {layer.type === "variable" ? `{{${layer.variableKey}}}` : layer.type}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0 ml-2" onClick={(e) => e.stopPropagation()}>
                      {/* Move up / down */}
                      <button
                        onClick={() => moveLayer(layer.id, "up")}
                        disabled={index === 0}
                        className="p-1 rounded text-gray-400 hover:text-black disabled:opacity-20"
                        title="Move layer up"
                      >
                        <ChevronUp className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => moveLayer(layer.id, "down")}
                        disabled={index === layers.length - 1}
                        className="p-1 rounded text-gray-400 hover:text-black disabled:opacity-20"
                        title="Move layer down"
                      >
                        <ChevronDown className="w-3 h-3" />
                      </button>

                      {/* Toggle visibility */}
                      <button
                        onClick={() => toggleLayerVisibility(layer.id)}
                        className={`p-1 rounded ${
                          layer.visible ? "text-gray-500 hover:text-black" : "text-gray-300"
                        }`}
                        title={layer.visible ? "Hide layer" : "Show layer"}
                      >
                        {layer.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                      </button>

                      {/* Lock / Unlock */}
                      <button
                        onClick={() => toggleLayerLock(layer.id)}
                        className={`p-1 rounded ${
                          layer.locked ? "text-amber-500" : "text-gray-400 hover:text-black"
                        }`}
                        title={layer.locked ? "Unlock layer" : "Lock layer"}
                      >
                        {layer.locked ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />}
                      </button>

                      {/* Duplicate */}
                      <button
                        onClick={() => duplicateLayer(layer.id)}
                        className="p-1 rounded text-gray-400 hover:text-black"
                        title="Duplicate layer"
                      >
                        <Copy className="w-3 h-3" />
                      </button>

                      {/* Delete */}
                      <button
                        onClick={() => removeLayer(layer.id)}
                        className="p-1 rounded text-gray-400 hover:text-red-600"
                        title="Delete layer"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ===================== TAB 3: PRESETS ===================== */}
        {activeTab === "templates" && (
          <div className="space-y-4">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                Template Themes
              </span>
              <p className="text-[11px] text-gray-500 mb-3">
                Switching template adjusts typography hierarchy and ornamentation while preserving CSV mappings.
              </p>
            </div>

            <div className="space-y-3">
              {TEMPLATE_PRESETS.map((preset) => (
                <div
                  key={preset.id}
                  className="p-3.5 rounded-2xl border border-[var(--color-border)] hover:border-[var(--color-primary)] bg-white transition-all space-y-2 group cursor-pointer"
                  onClick={() => loadPreset(preset.id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-bold text-gray-800 group-hover:text-[var(--color-primary)]">
                      {preset.name}
                    </span>
                    <span className="text-[10px] font-semibold uppercase bg-gray-100 px-2 py-0.5 rounded text-gray-600">
                      {preset.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    {preset.description}
                  </p>

                  <div className="flex items-center gap-1.5 pt-1">
                    <div
                      className="w-4 h-4 rounded-full border border-gray-300"
                      style={{ backgroundColor: preset.theme.borderColor }}
                    />
                    <div
                      className="w-4 h-4 rounded-full border border-gray-300"
                      style={{ backgroundColor: preset.theme.accentColor }}
                    />
                    <span className="text-[10px] font-mono text-gray-400 ml-1">
                      {preset.theme.primaryFont}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
