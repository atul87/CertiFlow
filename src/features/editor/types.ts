export type LayerType = "text" | "variable" | "qr" | "signature" | "badge" | "shape" | "divider";

export interface Layer {
  id: string;
  type: LayerType;
  name: string;
  // Content & Binding
  content: string;
  variableKey?: string; // e.g. "NAME", "COURSE", "DATE", "SCORE", "CERTIFICATE_ID"
  // Geometry (as percentage of canvas 0-100 or relative units for crisp scaling)
  x: number; // percentage from left (0 to 100)
  y: number; // percentage from top (0 to 100)
  width?: number; // percentage width
  height?: number; // percentage height
  rotation?: number; // degrees
  // Typography
  fontSize: number; // pt/px reference at 1000px base width
  fontFamily: string;
  fontWeight: "normal" | "500" | "600" | "bold" | "800";
  fontStyle?: "normal" | "italic";
  color: string;
  textAlign: "left" | "center" | "right";
  letterSpacing: number; // em or px
  lineHeight: number;
  textTransform?: "none" | "uppercase" | "capitalize" | "lowercase";
  // Auto-fit
  autoFit?: boolean;
  minFontSize?: number;
  // Styling
  opacity: number;
  locked: boolean;
  visible: boolean;
  shadow?: {
    color: string;
    blur: number;
    offsetX: number;
    offsetY: number;
  };
  // QR specifics
  qrData?: string;
  qrSize?: number;
  // Shape/Seal specifics
  shapeType?: "seal" | "rect" | "circle" | "badge" | "divider";
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  signerName?: string;
  signerTitle?: string;
}

export interface RecipientRecord {
  id: string;
  row: number;
  name: string;
  course: string;
  date: string;
  score: string;
  email: string;
  certificateId: string;
}

export interface TemplatePreset {
  id: string;
  name: string;
  category: "academic" | "tech" | "executive" | "minimal";
  description: string;
  theme: {
    background: string;
    borderColor: string;
    accentColor: string;
    primaryFont: string;
    serifFont: string;
  };
  layers: Layer[];
}
