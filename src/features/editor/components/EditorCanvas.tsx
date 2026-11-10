"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { useEditorStore } from "../use-editor-store";
import { Layer } from "../types";
import {
  Sparkles,
  ShieldCheck,
  AlignCenter,
  AlignVerticalSpaceAround,
  AlignLeft,
  AlignRight,
  Trash2,
} from "lucide-react";

export function EditorCanvas() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragLayerId, setDragLayerId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [snapGuideX, setSnapGuideX] = useState<number | null>(null);
  const [snapGuideY, setSnapGuideY] = useState<number | null>(null);

  const {
    layers,
    selectedLayerId,
    selectLayer,
    updateLayer,
    removeLayer,
    zoom,
    showGrid,
    showSafeMargin,
    recipients,
    activeRecipientIndex,
    undo,
    redo,
  } = useEditorStore();

  const currentRecipient = recipients[activeRecipientIndex] || recipients[0];
  const selectedLayer = layers.find((l) => l.id === selectedLayerId);

  // Substitute dynamic variable placeholders with active recipient data
  const renderLayerContent = useCallback((layer: Layer) => {
    let text = layer.content;
    if (layer.variableKey) {
      switch (layer.variableKey) {
        case "NAME":
          text = currentRecipient.name;
          break;
        case "COURSE":
          text = currentRecipient.course;
          break;
        case "DATE":
          text = currentRecipient.date;
          break;
        case "SCORE":
          text = currentRecipient.score;
          break;
        case "CERTIFICATE_ID":
          text = currentRecipient.certificateId;
          break;
        default:
          text = currentRecipient.name;
      }
    } else {
      text = text
        .replace(/\{\{NAME\}\}/g, currentRecipient.name)
        .replace(/\{\{COURSE\}\}/g, currentRecipient.course)
        .replace(/\{\{DATE\}\}/g, currentRecipient.date)
        .replace(/\{\{SCORE\}\}/g, currentRecipient.score)
        .replace(/\{\{CERTIFICATE_ID\}\}/g, currentRecipient.certificateId);
    }
    return text;
  }, [currentRecipient]);

  // Compute auto-fitted font size for long recipient names
  const getComputedFontSize = useCallback((layer: Layer, text: string) => {
    if (!layer.autoFit) return layer.fontSize;
    const baseSize = layer.fontSize;
    const minSize = layer.minFontSize || 16;

    if (text.length > 28) {
      const scale = Math.max(minSize / baseSize, 1 - (text.length - 28) * 0.02);
      return Math.round(baseSize * scale);
    }
    return baseSize;
  }, []);

  // Keyboard navigation & nudging
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is currently typing inside an input, textarea, or contentEditable
      const target = e.target as HTMLElement;
      if (
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.tagName === "SELECT" ||
          target.isContentEditable)
      ) {
        return;
      }

      // Undo / Redo shortcuts
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
        e.preventDefault();
        if (e.shiftKey) {
          redo();
        } else {
          undo();
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
        e.preventDefault();
        redo();
        return;
      }

      if (!selectedLayerId || !selectedLayer || selectedLayer.locked) return;

      const step = e.shiftKey ? 2.5 : 0.5;

      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          updateLayer(selectedLayerId, {
            x: Math.max(5, Math.min(95, Math.round((selectedLayer.x - step) * 10) / 10)),
          });
          break;
        case "ArrowRight":
          e.preventDefault();
          updateLayer(selectedLayerId, {
            x: Math.max(5, Math.min(95, Math.round((selectedLayer.x + step) * 10) / 10)),
          });
          break;
        case "ArrowUp":
          e.preventDefault();
          updateLayer(selectedLayerId, {
            y: Math.max(5, Math.min(95, Math.round((selectedLayer.y - step) * 10) / 10)),
          });
          break;
        case "ArrowDown":
          e.preventDefault();
          updateLayer(selectedLayerId, {
            y: Math.max(5, Math.min(95, Math.round((selectedLayer.y + step) * 10) / 10)),
          });
          break;
        case "Delete":
        case "Backspace":
          e.preventDefault();
          removeLayer(selectedLayerId);
          break;
        case "Escape":
          e.preventDefault();
          selectLayer(null);
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedLayerId, selectedLayer, updateLayer, removeLayer, selectLayer, undo, redo]);

  // Dragging logic with multi-axis magnetic snapping
  const handleMouseDown = (e: React.MouseEvent, layer: Layer) => {
    if (layer.locked) return;
    e.stopPropagation();
    selectLayer(layer.id);
    setIsDragging(true);
    setDragLayerId(layer.id);

    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 100;
      const mouseY = ((e.clientY - rect.top) / rect.height) * 100;
      setDragOffset({
        x: mouseX - layer.x,
        y: mouseY - layer.y,
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !dragLayerId || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * 100;
    const mouseY = ((e.clientY - rect.top) / rect.height) * 100;

    let newX = mouseX - dragOffset.x;
    let newY = mouseY - dragOffset.y;

    let activeGuideX: number | null = null;
    let activeGuideY: number | null = null;

    // 1. Center Snapping (Horizontal Center: X = 50%)
    if (Math.abs(newX - 50) < 1.6) {
      newX = 50;
      activeGuideX = 50;
    }

    // 2. Middle Snapping (Vertical Center: Y = 50%)
    if (Math.abs(newY - 50) < 1.6) {
      newY = 50;
      activeGuideY = 50;
    }

    // 3. Peer Layer Snapping (Align to other visible layers)
    for (const other of layers) {
      if (other.id === dragLayerId || !other.visible) continue;
      if (Math.abs(newX - other.x) < 1.2 && activeGuideX === null) {
        newX = other.x;
        activeGuideX = other.x;
      }
      if (Math.abs(newY - other.y) < 1.2 && activeGuideY === null) {
        newY = other.y;
        activeGuideY = other.y;
      }
    }

    setSnapGuideX(activeGuideX);
    setSnapGuideY(activeGuideY);

    // Keep within bounds
    newX = Math.max(5, Math.min(95, newX));
    newY = Math.max(5, Math.min(95, newY));

    updateLayer(dragLayerId, {
      x: Math.round(newX * 10) / 10,
      y: Math.round(newY * 10) / 10,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDragLayerId(null);
    setSnapGuideX(null);
    setSnapGuideY(null);
  };

  // Quick Alignment Handlers
  const handleAlignHorizontalCenter = () => {
    if (!selectedLayerId) return;
    updateLayer(selectedLayerId, { x: 50 });
  };

  const handleAlignVerticalMiddle = () => {
    if (!selectedLayerId) return;
    updateLayer(selectedLayerId, { y: 50 });
  };

  const handleAlignLeft = () => {
    if (!selectedLayerId) return;
    updateLayer(selectedLayerId, { x: 25 });
  };

  const handleAlignRight = () => {
    if (!selectedLayerId) return;
    updateLayer(selectedLayerId, { x: 75 });
  };

  return (
    <div
      className="flex-1 bg-[#ECECE9] overflow-auto flex items-center justify-center p-8 relative select-none"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onClick={() => selectLayer(null)}
    >
      {/* Scaled Workbench Area */}
      <div
        style={{
          transform: `scale(${zoom})`,
          transformOrigin: "center center",
          transition: "transform 0.15s ease-out",
        }}
        className="shrink-0 relative"
      >
        {/* Certificate Container: A4 Landscape Ratio (1.414 : 1) */}
        <div
          ref={canvasRef}
          className="w-[960px] h-[678px] bg-white rounded-lg shadow-2xl relative overflow-hidden transition-shadow"
          style={{
            backgroundImage: "radial-gradient(circle at 50% 50%, #FAF9F5 0%, #F5F3EB 100%)",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* ORNATE CERTIFICATE BACKGROUND VECTOR FRAME */}
          <div className="absolute inset-5 border-2 border-[#D4AF37] pointer-events-none rounded-sm" />
          <div className="absolute inset-7 border border-[#D4AF37]/50 pointer-events-none rounded-xs" />
          <div className="absolute inset-9 border border-[#D4AF37]/20 pointer-events-none" />

          {/* Corner Ornamental Flourishes */}
          <div className="absolute top-6 left-6 w-10 h-10 border-t-2 border-l-2 border-[#D4AF37] pointer-events-none" />
          <div className="absolute top-6 right-6 w-10 h-10 border-t-2 border-r-2 border-[#D4AF37] pointer-events-none" />
          <div className="absolute bottom-6 left-6 w-10 h-10 border-b-2 border-l-2 border-[#D4AF37] pointer-events-none" />
          <div className="absolute bottom-6 right-6 w-10 h-10 border-b-2 border-r-2 border-[#D4AF37] pointer-events-none" />

          {/* Background Watermark Crest */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.035]">
            <div className="w-96 h-96 rounded-full border-12 border-black flex items-center justify-center">
              <ShieldCheck className="w-56 h-56 text-black" />
            </div>
          </div>

          {/* PRINT SAFE MARGIN GUIDES */}
          {showSafeMargin && (
            <div className="absolute inset-12 border border-dashed border-emerald-500/40 pointer-events-none rounded">
              <span className="absolute top-1 left-2 text-[9px] font-mono text-emerald-600/70 font-semibold uppercase">
                Print Safe Margin (0.5 in)
              </span>
            </div>
          )}

          {/* ALIGNMENT GRID */}
          {showGrid && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage:
                  "linear-gradient(to right, rgba(99, 91, 255, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(99, 91, 255, 0.08) 1px, transparent 1px)",
                backgroundSize: "32px 32px",
              }}
            />
          )}

          {/* DYNAMIC MAGNETIC GUIDELINES */}
          {snapGuideX !== null && (
            <div
              style={{ left: `${snapGuideX}%` }}
              className="absolute top-0 bottom-0 w-0.5 border-l-2 border-dashed border-cyan-500 pointer-events-none z-50 shadow-sm"
            >
              <div className="bg-cyan-600 text-white font-mono text-[9px] px-1 py-0.5 rounded-xs absolute top-2 left-1">
                X: {Math.round(snapGuideX)}%
              </div>
            </div>
          )}

          {snapGuideY !== null && (
            <div
              style={{ top: `${snapGuideY}%` }}
              className="absolute left-0 right-0 h-0.5 border-t-2 border-dashed border-cyan-500 pointer-events-none z-50 shadow-sm"
            >
              <div className="bg-cyan-600 text-white font-mono text-[9px] px-1 py-0.5 rounded-xs absolute left-2 top-1">
                Y: {Math.round(snapGuideY)}%
              </div>
            </div>
          )}

          {/* LAYERS RENDERING PIPELINE */}
          {layers.map((layer) => {
            if (!layer.visible) return null;
            const isSelected = selectedLayerId === layer.id;
            const textContent = renderLayerContent(layer);
            const computedSize = getComputedFontSize(layer, textContent);
            const isAutoFitted = layer.autoFit && computedSize < layer.fontSize;

            return (
              <div
                key={layer.id}
                onMouseDown={(e) => handleMouseDown(e, layer)}
                style={{
                  position: "absolute",
                  left: `${layer.x}%`,
                  top: `${layer.y}%`,
                  transform: "translate(-50%, -50%)",
                  width: layer.width ? `${layer.width}%` : "auto",
                  opacity: layer.opacity,
                  cursor: layer.locked ? "default" : isDragging ? "grabbing" : "grab",
                  zIndex: isSelected ? 40 : 10,
                }}
                className={`group transition-all ${
                  isSelected ? "ring-2 ring-[var(--color-primary)] ring-offset-2 rounded" : ""
                }`}
              >
                {/* 1. TEXT / VARIABLE LAYER */}
                {(layer.type === "text" || layer.type === "variable") && (
                  <div
                    style={{
                      fontFamily: layer.fontFamily,
                      fontSize: `${computedSize}px`,
                      fontWeight: layer.fontWeight,
                      fontStyle: layer.fontStyle || "normal",
                      color: layer.color,
                      textAlign: layer.textAlign,
                      letterSpacing: `${layer.letterSpacing}px`,
                      lineHeight: layer.lineHeight,
                      textTransform: layer.textTransform || "none",
                    }}
                    className="w-full relative whitespace-normal select-none"
                  >
                    {textContent}

                    {/* Auto-fit indicator badge */}
                    {isAutoFitted && isSelected && (
                      <div className="absolute -top-6 right-0 bg-emerald-600 text-white text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shadow flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5" />
                        Auto-scaled: {computedSize}px ({layer.fontSize}px max)
                      </div>
                    )}
                  </div>
                )}

                {/* 2. SIGNATURE LAYER */}
                {layer.type === "signature" && (
                  <div className="text-center w-full select-none">
                    <p
                      style={{
                        fontFamily: "Great Vibes",
                        fontSize: `${layer.fontSize + 8}px`,
                        color: layer.color,
                      }}
                      className="italic leading-none mb-1.5"
                    >
                      {layer.signerName || "Dr. Arthur Pendelton"}
                    </p>
                    <div className="w-44 h-px bg-gray-400 mx-auto mb-1" />
                    <p className="text-[10px] font-bold text-gray-800 uppercase tracking-wider">
                      {layer.signerName || "Dr. Arthur Pendelton"}
                    </p>
                    <p className="text-[9px] text-gray-500">
                      {layer.signerTitle || "Chancellor & Dean of Engineering"}
                    </p>
                  </div>
                )}

                {/* 3. QR VERIFICATION CODE LAYER */}
                {layer.type === "qr" && (
                  <div className="flex flex-col items-center justify-center p-2 rounded-lg bg-white/90 border border-gray-200/80 shadow-xs select-none">
                    <svg className="w-16 h-16" viewBox="0 0 100 100" fill="none">
                      <rect width="100" height="100" fill="white" />
                      <rect x="5" y="5" width="28" height="28" fill="#111111" rx="2" />
                      <rect x="10" y="10" width="18" height="18" fill="white" />
                      <rect x="14" y="14" width="10" height="10" fill="#111111" />
                      <rect x="67" y="5" width="28" height="28" fill="#111111" rx="2" />
                      <rect x="72" y="10" width="18" height="18" fill="white" />
                      <rect x="76" y="14" width="10" height="10" fill="#111111" />
                      <rect x="5" y="67" width="28" height="28" fill="#111111" rx="2" />
                      <rect x="10" y="72" width="18" height="18" fill="white" />
                      <rect x="14" y="76" width="10" height="10" fill="#111111" />
                      <rect x="40" y="8" width="6" height="6" fill="#111111" />
                      <rect x="52" y="8" width="6" height="6" fill="#111111" />
                      <rect x="40" y="20" width="6" height="6" fill="#111111" />
                      <rect x="48" y="26" width="6" height="6" fill="#111111" />
                      <rect x="8" y="44" width="6" height="6" fill="#111111" />
                      <rect x="22" y="48" width="6" height="6" fill="#111111" />
                      <rect x="40" y="42" width="20" height="20" fill="white" />
                      <circle cx="50" cy="52" r="8" fill="#635BFF" />
                      <rect x="68" y="44" width="6" height="6" fill="#111111" />
                      <rect x="82" y="48" width="6" height="6" fill="#111111" />
                      <rect x="44" y="72" width="6" height="6" fill="#111111" />
                      <rect x="58" y="80" width="6" height="6" fill="#111111" />
                      <rect x="80" y="76" width="6" height="6" fill="#111111" />
                    </svg>

                    <div className="mt-1 text-center">
                      <span className="text-[8px] font-mono font-bold text-gray-700 block">
                        {currentRecipient.certificateId}
                      </span>
                      <span className="text-[7px] uppercase font-semibold text-[var(--color-primary)]">
                        Scan to Verify
                      </span>
                    </div>
                  </div>
                )}

                {/* 4. OFFICIAL GOLD SEAL / BADGE */}
                {layer.type === "badge" && (
                  <div className="flex flex-col items-center justify-center select-none">
                    <div className="relative w-20 h-20 flex items-center justify-center">
                      <svg className="w-20 h-20 filter drop-shadow-md" viewBox="0 0 100 100">
                        <polygon
                          points="50,0 62,20 85,15 80,38 100,50 80,62 85,85 62,80 50,100 38,80 15,85 20,62 0,50 20,38 15,15 38,20"
                          fill="#FDE68A"
                          stroke="#D97706"
                          strokeWidth="2"
                        />
                        <circle cx="50" cy="50" r="34" fill="#FEF3C7" stroke="#B45309" strokeWidth="1.5" />
                        <circle cx="50" cy="50" r="28" fill="none" stroke="#D97706" strokeWidth="1" strokeDasharray="3 2" />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-2">
                        <span className="text-[6.5px] font-extrabold uppercase text-[#92400E] tracking-tighter leading-tight font-serif">
                          OFFICIAL<br />SEAL
                        </span>
                        <span className="text-[5.5px] font-bold text-[#B45309] uppercase tracking-widest mt-0.5">
                          2026
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 5. DECORATIVE DIVIDER */}
                {layer.type === "divider" && (
                  <div
                    style={{
                      height: `${layer.strokeWidth || 1}px`,
                      backgroundColor: layer.color || "#D1D5DB",
                    }}
                    className="w-full"
                  />
                )}

                {/* SELECTION HANDLES & COORDINATE TOOLTIP */}
                {isSelected && (
                  <>
                    <div className="absolute -top-2 -left-2 w-3.5 h-3.5 bg-white border-2 border-[var(--color-primary)] rounded-full shadow-xs cursor-nwse-resize" />
                    <div className="absolute -top-2 -right-2 w-3.5 h-3.5 bg-white border-2 border-[var(--color-primary)] rounded-full shadow-xs cursor-nesw-resize" />
                    <div className="absolute -bottom-2 -left-2 w-3.5 h-3.5 bg-white border-2 border-[var(--color-primary)] rounded-full shadow-xs cursor-nesw-resize" />
                    <div className="absolute -bottom-2 -right-2 w-3.5 h-3.5 bg-white border-2 border-[var(--color-primary)] rounded-full shadow-xs cursor-nwse-resize" />

                    {/* Coordinate indicator tooltip */}
                    <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[9px] font-mono px-2 py-0.5 rounded shadow pointer-events-none whitespace-nowrap z-50 flex items-center gap-1.5">
                      <span>X: {Math.round(layer.x)}% · Y: {Math.round(layer.y)}%</span>
                      <span className="text-gray-400">|</span>
                      <span className="text-gray-300">Nudge: Arrow keys</span>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>

        {/* FLOATING QUICK ALIGNMENT TOOLBAR (Visible when a layer is selected) */}
        {selectedLayer && (
          <div className="absolute -bottom-14 left-1/2 -translate-x-1/2 bg-white/95 backdrop-blur-md border border-[var(--color-border)] px-3 py-1.5 rounded-xl shadow-lg flex items-center gap-1 z-50 text-[12px]">
            <span className="text-[11px] font-semibold text-gray-500 mr-1.5 border-r border-gray-200 pr-2">
              {selectedLayer.name}
            </span>
            <button
              onClick={handleAlignHorizontalCenter}
              title="Center Horizontally (X: 50%)"
              className="p-1.5 rounded-lg text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <AlignCenter className="w-4 h-4" />
            </button>
            <button
              onClick={handleAlignVerticalMiddle}
              title="Center Vertically (Y: 50%)"
              className="p-1.5 rounded-lg text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <AlignVerticalSpaceAround className="w-4 h-4" />
            </button>
            <button
              onClick={handleAlignLeft}
              title="Align Left (X: 25%)"
              className="p-1.5 rounded-lg text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <AlignLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleAlignRight}
              title="Align Right (X: 75%)"
              className="p-1.5 rounded-lg text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <AlignRight className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-gray-200 mx-1" />
            <button
              onClick={() => removeLayer(selectedLayer.id)}
              title="Delete Layer (Del)"
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
