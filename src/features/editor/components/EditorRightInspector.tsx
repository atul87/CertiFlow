"use client";

import {
  AlignLeft,
  AlignCenter,
  AlignRight,
  Maximize,
  Sliders,
  Type,
  Lock,
  Trash2,
  Sparkles,
  QrCode,
  Stamp,
  Palette,
  Layers,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEditorStore } from "../use-editor-store";
import { Layer } from "../types";

export function EditorRightInspector() {
  const {
    layers,
    selectedLayerId,
    updateLayer,
    removeLayer,
    selectLayer,
  } = useEditorStore();

  const selectedLayer = layers.find((l) => l.id === selectedLayerId);

  // If no layer is selected, display Canvas Master Settings
  if (!selectedLayer) {
    return (
      <aside className="w-80 bg-white border-l border-[var(--color-border)] flex flex-col shrink-0 select-none z-20 overflow-y-auto p-5 space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
            Canvas Properties
          </span>
          <h3 className="text-[16px] font-bold text-gray-900">Certificate Master</h3>
          <p className="text-[12px] text-gray-500 mt-1">
            Select any element on the canvas to configure typography, auto-fit, and data binding.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] space-y-3 text-[12px]">
          <div className="flex justify-between">
            <span className="text-gray-500">Dimensions:</span>
            <span className="font-semibold text-gray-800">3508 × 2480 px (A4)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Resolution:</span>
            <span className="font-semibold text-gray-800">300 DPI Vector Print</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Orientation:</span>
            <span className="font-semibold text-gray-800">Landscape</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Total Layers:</span>
            <span className="font-semibold text-[var(--color-primary)]">{layers.length} layers</span>
          </div>
        </div>

        <div className="space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
            Quick Select Layer
          </span>
          <div className="space-y-1">
            {layers.slice(0, 6).map((l) => (
              <button
                key={l.id}
                onClick={() => selectLayer(l.id)}
                className="w-full text-left p-2 rounded-lg border border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-indigo-50/20 text-[12px] flex items-center justify-between"
              >
                <span className="font-medium text-gray-700">{l.name}</span>
                <span className="text-[10px] text-gray-400 font-mono">{l.type}</span>
              </button>
            ))}
          </div>
        </div>
      </aside>
    );
  }

  const isTextOrVariable =
    selectedLayer.type === "text" ||
    selectedLayer.type === "variable" ||
    selectedLayer.type === "signature";

  const presetColors = [
    "#111111", // Charcoal
    "#635BFF", // CertiFlow Royal Indigo
    "#0F172A", // Slate Dark
    "#D97706", // Gold / Amber
    "#059669", // Emerald
    "#DC2626", // Crimson
    "#4B5563", // Gray
    "#1E1B4B", // Midnight Navy
  ];

  return (
    <aside className="w-80 bg-white border-l border-[var(--color-border)] flex flex-col shrink-0 select-none z-20 overflow-y-auto p-4 space-y-6">
      {/* Top Header of Selected Layer */}
      <div className="border-b border-[var(--color-border)] pb-3">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-primary)] bg-indigo-50 px-2 py-0.5 rounded">
            {selectedLayer.type.toUpperCase()}
          </span>

          <div className="flex items-center gap-1">
            <button
              onClick={() => removeLayer(selectedLayer.id)}
              className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Delete Layer"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <input
          type="text"
          value={selectedLayer.name}
          onChange={(e) => updateLayer(selectedLayer.id, { name: e.target.value })}
          className="text-[14px] font-bold text-gray-900 mt-2 w-full bg-transparent border-0 p-0 focus:ring-0 focus:outline-none"
        />
      </div>

      {/* DYNAMIC CSV BINDING (For variables or text) */}
      {(selectedLayer.type === "variable" || selectedLayer.type === "text") && (
        <div className="p-3.5 rounded-xl bg-indigo-50/50 border border-indigo-100 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              CSV Data Binding
            </span>
          </div>

          <label className="text-[11px] text-gray-600 block">Connected Spreadsheet Column</label>
          <select
            value={selectedLayer.variableKey || "NONE"}
            onChange={(e) => {
              const val = e.target.value;
              if (val === "NONE") {
                updateLayer(selectedLayer.id, {
                  type: "text",
                  variableKey: undefined,
                  content: selectedLayer.content.replace(/\{\{.*?\}\}/g, "Static Text"),
                });
              } else {
                updateLayer(selectedLayer.id, {
                  type: "variable",
                  variableKey: val,
                  content: `{{${val}}}`,
                });
              }
            }}
            className="w-full text-[12px] bg-white border border-indigo-200 rounded-lg p-2 font-medium text-gray-800"
          >
            <option value="NONE">— None (Static Text) —</option>
            <option value="NAME">Full Name (&#123;&#123;NAME&#125;&#125;)</option>
            <option value="COURSE">Course Title (&#123;&#123;COURSE&#125;&#125;)</option>
            <option value="DATE">Completion Date (&#123;&#123;DATE&#125;&#125;)</option>
            <option value="SCORE">Score / Grade (&#123;&#123;SCORE&#125;&#125;)</option>
            <option value="CERTIFICATE_ID">Certificate UUID (&#123;&#123;CERTIFICATE_ID&#125;&#125;)</option>
          </select>
        </div>
      )}

      {/* AUTO-FIT TEXT SCALING (Crucial SaaS feature for variable text) */}
      {selectedLayer.type === "variable" && (
        <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-100 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                Smart Text Fit
              </span>
              <p className="text-[10px] text-emerald-600">Auto-shrink font for long recipient names</p>
            </div>
            <input
              type="checkbox"
              checked={selectedLayer.autoFit ?? true}
              onChange={(e) => updateLayer(selectedLayer.id, { autoFit: e.target.checked })}
              className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4 cursor-pointer"
            />
          </div>

          {selectedLayer.autoFit && (
            <div>
              <div className="flex justify-between text-[11px] text-emerald-800 mb-1">
                <span>Minimum Font Size:</span>
                <span className="font-mono font-bold">{selectedLayer.minFontSize || 16}px</span>
              </div>
              <input
                type="range"
                min="12"
                max="32"
                value={selectedLayer.minFontSize || 16}
                onChange={(e) => updateLayer(selectedLayer.id, { minFontSize: Number(e.target.value) })}
                className="w-full accent-emerald-600 cursor-pointer"
              />
            </div>
          )}
        </div>
      )}

      {/* TYPOGRAPHY PROPERTIES */}
      {isTextOrVariable && (
        <div className="space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
            Typography
          </span>

          {/* Font Family */}
          <div>
            <label className="text-[11px] text-gray-500 block mb-1">Font Family</label>
            <select
              value={selectedLayer.fontFamily}
              onChange={(e) => updateLayer(selectedLayer.id, { fontFamily: e.target.value })}
              className="w-full text-[12px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-2 font-medium"
            >
              <option value="Playfair Display">Playfair Display (Academic Serif)</option>
              <option value="Cinzel">Cinzel (Prestige Roman)</option>
              <option value="Inter">Inter (Modern Clean Sans)</option>
              <option value="Outfit">Outfit (Geometric Tech)</option>
              <option value="Montserrat">Montserrat (Architectural)</option>
              <option value="Great Vibes">Great Vibes (Formal Calligraphy)</option>
            </select>
          </div>

          {/* Font Size & Weight */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[11px] text-gray-500 block mb-1">Size (px)</label>
              <input
                type="number"
                min="8"
                max="120"
                value={selectedLayer.fontSize}
                onChange={(e) => updateLayer(selectedLayer.id, { fontSize: Number(e.target.value) })}
                className="w-full text-[12px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-2 font-mono font-medium"
              />
            </div>

            <div>
              <label className="text-[11px] text-gray-500 block mb-1">Weight</label>
              <select
                value={selectedLayer.fontWeight}
                onChange={(e) => updateLayer(selectedLayer.id, { fontWeight: e.target.value as Layer["fontWeight"] })}
                className="w-full text-[12px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-2 font-medium"
              >
                <option value="normal">Regular (400)</option>
                <option value="500">Medium (500)</option>
                <option value="600">SemiBold (600)</option>
                <option value="bold">Bold (700)</option>
                <option value="800">Black (800)</option>
              </select>
            </div>
          </div>

          {/* Text Alignment */}
          <div>
            <label className="text-[11px] text-gray-500 block mb-1">Alignment</label>
            <div className="grid grid-cols-3 gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                type="button"
                onClick={() => updateLayer(selectedLayer.id, { textAlign: "left" })}
                className={`py-1.5 rounded-md flex justify-center text-[12px] ${
                  selectedLayer.textAlign === "left" ? "bg-white shadow-2xs font-bold text-black" : "text-gray-500"
                }`}
              >
                <AlignLeft className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => updateLayer(selectedLayer.id, { textAlign: "center" })}
                className={`py-1.5 rounded-md flex justify-center text-[12px] ${
                  selectedLayer.textAlign === "center" ? "bg-white shadow-2xs font-bold text-black" : "text-gray-500"
                }`}
              >
                <AlignCenter className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => updateLayer(selectedLayer.id, { textAlign: "right" })}
                className={`py-1.5 rounded-md flex justify-center text-[12px] ${
                  selectedLayer.textAlign === "right" ? "bg-white shadow-2xs font-bold text-black" : "text-gray-500"
                }`}
              >
                <AlignRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Letter Spacing */}
          <div>
            <div className="flex justify-between text-[11px] text-gray-500 mb-1">
              <span>Letter Spacing:</span>
              <span className="font-mono">{selectedLayer.letterSpacing || 0}px</span>
            </div>
            <input
              type="range"
              min="-1"
              max="10"
              value={selectedLayer.letterSpacing || 0}
              onChange={(e) => updateLayer(selectedLayer.id, { letterSpacing: Number(e.target.value) })}
              className="w-full accent-[var(--color-primary)] cursor-pointer"
            />
          </div>

          {/* Color Swatches */}
          <div>
            <label className="text-[11px] text-gray-500 block mb-1.5">Color Palette</label>
            <div className="flex flex-wrap gap-2 items-center">
              {presetColors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => updateLayer(selectedLayer.id, { color })}
                  className={`w-6 h-6 rounded-full border-2 transition-transform ${
                    selectedLayer.color === color
                      ? "border-black scale-110 shadow-xs"
                      : "border-transparent hover:scale-105"
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
              <input
                type="color"
                value={selectedLayer.color}
                onChange={(e) => updateLayer(selectedLayer.id, { color: e.target.value })}
                className="w-6 h-6 rounded-full cursor-pointer border-0 p-0"
                title="Custom color"
              />
            </div>
          </div>
        </div>
      )}

      {/* SIGNATURE SPECIFICS */}
      {selectedLayer.type === "signature" && (
        <div className="space-y-3 p-3 rounded-xl bg-gray-50 border border-[var(--color-border)]">
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500 block">
            Signatory Details
          </span>
          <div>
            <label className="text-[10px] text-gray-500 block mb-0.5">Printed Name</label>
            <input
              type="text"
              value={selectedLayer.signerName || ""}
              onChange={(e) => updateLayer(selectedLayer.id, { signerName: e.target.value })}
              className="w-full text-[12px] bg-white border border-[var(--color-border)] rounded-md p-1.5"
            />
          </div>
          <div>
            <label className="text-[10px] text-gray-500 block mb-0.5">Title / Designation</label>
            <input
              type="text"
              value={selectedLayer.signerTitle || ""}
              onChange={(e) => updateLayer(selectedLayer.id, { signerTitle: e.target.value })}
              className="w-full text-[12px] bg-white border border-[var(--color-border)] rounded-md p-1.5"
            />
          </div>
        </div>
      )}

      {/* QR CODE SPECIFICS */}
      {selectedLayer.type === "qr" && (
        <div className="space-y-3 p-3 rounded-xl bg-gray-50 border border-[var(--color-border)]">
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500 block">
            QR Verification Parameters
          </span>
          <div>
            <label className="text-[10px] text-gray-500 block mb-0.5">Destination URL Pattern</label>
            <input
              type="text"
              value={selectedLayer.qrData || ""}
              onChange={(e) => updateLayer(selectedLayer.id, { qrData: e.target.value })}
              className="w-full text-[11px] font-mono bg-white border border-[var(--color-border)] rounded-md p-1.5"
            />
          </div>
          <p className="text-[10px] text-gray-400">
            Dynamically substitutes <code>{"{{CERTIFICATE_ID}}"}</code> with the recipient&apos;s verified hash code.
          </p>
        </div>
      )}

      {/* POSITION & LAYOUT GEOMETRY */}
      <div className="space-y-3 border-t border-[var(--color-border)] pt-4">
        <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
          Canvas Coordinates (%)
        </span>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-gray-500 block mb-0.5">Center X (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={Math.round(selectedLayer.x)}
              onChange={(e) => updateLayer(selectedLayer.id, { x: Number(e.target.value) })}
              className="w-full text-[12px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-2 font-mono font-medium"
            />
          </div>

          <div>
            <label className="text-[10px] text-gray-500 block mb-0.5">Center Y (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={Math.round(selectedLayer.y)}
              onChange={(e) => updateLayer(selectedLayer.id, { y: Number(e.target.value) })}
              className="w-full text-[12px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-2 font-mono font-medium"
            />
          </div>
        </div>

        {/* Quick alignment shortcuts */}
        <div className="flex gap-1">
          <Button
            size="sm"
            variant="secondary"
            className="flex-1 text-[11px] py-1 h-7"
            onClick={() => updateLayer(selectedLayer.id, { x: 50 })}
          >
            Snap to Center
          </Button>
        </div>
      </div>
    </aside>
  );
}
