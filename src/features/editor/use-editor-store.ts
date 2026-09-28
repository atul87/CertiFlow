import { create } from "zustand";
import { Layer, RecipientRecord } from "./types";
import { DEFAULT_ACADEMIC_LAYERS, SAMPLE_RECIPIENTS, TEMPLATE_PRESETS } from "./sample-data";

interface EditorStore {
  // State
  layers: Layer[];
  selectedLayerId: string | null;
  recipients: RecipientRecord[];
  activeRecipientIndex: number;
  zoom: number;
  showGrid: boolean;
  showSafeMargin: boolean;
  isSaving: boolean;
  lastSavedAt: string | null;

  // History Stack for Undo/Redo
  history: Layer[][];
  historyIndex: number;

  // Actions
  selectLayer: (id: string | null) => void;
  updateLayer: (id: string, updates: Partial<Layer>) => void;
  addLayer: (layer: Partial<Layer>) => void;
  removeLayer: (id: string) => void;
  duplicateLayer: (id: string) => void;
  moveLayer: (id: string, direction: "up" | "down" | "top" | "bottom") => void;
  toggleLayerVisibility: (id: string) => void;
  toggleLayerLock: (id: string) => void;
  setZoom: (zoom: number) => void;
  toggleGrid: () => void;
  toggleSafeMargin: () => void;
  setActiveRecipientIndex: (index: number) => void;
  undo: () => void;
  redo: () => void;
  loadPreset: (presetId: string) => void;
  resetToDefault: () => void;
  saveCanvas: () => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  layers: DEFAULT_ACADEMIC_LAYERS,
  selectedLayerId: "layer-name",
  recipients: SAMPLE_RECIPIENTS,
  activeRecipientIndex: 0,
  zoom: 1.0,
  showGrid: false,
  showSafeMargin: true,
  isSaving: false,
  lastSavedAt: "Just now",

  history: [DEFAULT_ACADEMIC_LAYERS],
  historyIndex: 0,

  selectLayer: (id) => set({ selectedLayerId: id }),

  updateLayer: (id, updates) => {
    const { layers, history, historyIndex } = get();
    const newLayers = layers.map((layer) =>
      layer.id === id ? { ...layer, ...updates } : layer
    );

    // Save to history (truncate any redo future)
    const newHistory = [...history.slice(0, historyIndex + 1), newLayers];
    // Keep max 20 history states
    const trimmedHistory = newHistory.length > 20 ? newHistory.slice(newHistory.length - 20) : newHistory;

    set({
      layers: newLayers,
      history: trimmedHistory,
      historyIndex: trimmedHistory.length - 1,
      lastSavedAt: "Unsaved changes",
    });
  },

  addLayer: (partialLayer) => {
    const { layers, history, historyIndex } = get();
    const newId = `layer-${Date.now()}`;
    const newLayer: Layer = {
      id: newId,
      type: partialLayer.type || "text",
      name: partialLayer.name || "New Element",
      content: partialLayer.content || "Double click to edit",
      x: partialLayer.x ?? 50,
      y: partialLayer.y ?? 50,
      width: partialLayer.width ?? 50,
      height: partialLayer.height ?? 8,
      fontSize: partialLayer.fontSize ?? 18,
      fontFamily: partialLayer.fontFamily ?? "Inter",
      fontWeight: partialLayer.fontWeight ?? "500",
      color: partialLayer.color ?? "#111111",
      textAlign: partialLayer.textAlign ?? "center",
      letterSpacing: partialLayer.letterSpacing ?? 0,
      lineHeight: partialLayer.lineHeight ?? 1.2,
      opacity: 1,
      locked: false,
      visible: true,
      ...partialLayer,
    };

    const newLayers = [...layers, newLayer];
    const newHistory = [...history.slice(0, historyIndex + 1), newLayers];

    set({
      layers: newLayers,
      selectedLayerId: newId,
      history: newHistory,
      historyIndex: newHistory.length - 1,
      lastSavedAt: "Unsaved changes",
    });
  },

  removeLayer: (id) => {
    const { layers, history, historyIndex, selectedLayerId } = get();
    const newLayers = layers.filter((layer) => layer.id !== id);
    const newHistory = [...history.slice(0, historyIndex + 1), newLayers];

    set({
      layers: newLayers,
      selectedLayerId: selectedLayerId === id ? null : selectedLayerId,
      history: newHistory,
      historyIndex: newHistory.length - 1,
      lastSavedAt: "Unsaved changes",
    });
  },

  duplicateLayer: (id) => {
    const { layers, history, historyIndex } = get();
    const target = layers.find((l) => l.id === id);
    if (!target) return;

    const newId = `layer-${Date.now()}`;
    const duplicated: Layer = {
      ...target,
      id: newId,
      name: `${target.name} (Copy)`,
      y: Math.min(target.y + 4, 90),
      x: Math.min(target.x + 2, 90),
    };

    const newLayers = [...layers, duplicated];
    const newHistory = [...history.slice(0, historyIndex + 1), newLayers];

    set({
      layers: newLayers,
      selectedLayerId: newId,
      history: newHistory,
      historyIndex: newHistory.length - 1,
      lastSavedAt: "Unsaved changes",
    });
  },

  moveLayer: (id, direction) => {
    const { layers } = get();
    const index = layers.findIndex((l) => l.id === id);
    if (index === -1) return;

    const newLayers = [...layers];
    const [item] = newLayers.splice(index, 1);

    if (direction === "up" && index > 0) {
      newLayers.splice(index - 1, 0, item);
    } else if (direction === "down" && index < layers.length - 1) {
      newLayers.splice(index + 1, 0, item);
    } else if (direction === "top") {
      newLayers.unshift(item);
    } else if (direction === "bottom") {
      newLayers.push(item);
    } else {
      return;
    }

    set({ layers: newLayers, lastSavedAt: "Unsaved changes" });
  },

  toggleLayerVisibility: (id) => {
    const { layers } = get();
    set({
      layers: layers.map((l) => (l.id === id ? { ...l, visible: !l.visible } : l)),
    });
  },

  toggleLayerLock: (id) => {
    const { layers } = get();
    set({
      layers: layers.map((l) => (l.id === id ? { ...l, locked: !l.locked } : l)),
    });
  },

  setZoom: (zoom) => set({ zoom }),
  toggleGrid: () => set((state) => ({ showGrid: !state.showGrid })),
  toggleSafeMargin: () => set((state) => ({ showSafeMargin: !state.showSafeMargin })),

  setActiveRecipientIndex: (index) => set({ activeRecipientIndex: index }),

  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex > 0) {
      const nextIndex = historyIndex - 1;
      set({
        layers: history[nextIndex],
        historyIndex: nextIndex,
      });
    }
  },

  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex < history.length - 1) {
      const nextIndex = historyIndex + 1;
      set({
        layers: history[nextIndex],
        historyIndex: nextIndex,
      });
    }
  },

  loadPreset: (presetId) => {
    const preset = TEMPLATE_PRESETS.find((p) => p.id === presetId);
    if (!preset) return;
    const { history, historyIndex } = get();
    const newHistory = [...history.slice(0, historyIndex + 1), preset.layers];

    set({
      layers: preset.layers,
      selectedLayerId: preset.layers[0]?.id || null,
      history: newHistory,
      historyIndex: newHistory.length - 1,
      lastSavedAt: "Loaded " + preset.name,
    });
  },

  resetToDefault: () => {
    set({
      layers: DEFAULT_ACADEMIC_LAYERS,
      selectedLayerId: "layer-name",
      history: [DEFAULT_ACADEMIC_LAYERS],
      historyIndex: 0,
      lastSavedAt: "Reset to default",
    });
  },

  saveCanvas: () => {
    set({ isSaving: true });
    setTimeout(() => {
      set({ isSaving: false, lastSavedAt: "Saved just now" });
    }, 600);
  },
}));
