export type TemplateStatus = "draft" | "published" | "archived";

export interface Template {
  id: string;
  name: string;
  description?: string;
  status: TemplateStatus;
  thumbnail_url?: string;
  background_url?: string;
  width_mm: number;
  height_mm: number;
  orientation: "landscape" | "portrait";
  current_version_id: string;
  version_number: number;
  variable_tags: string[];
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface TemplateVersion {
  id: string;
  template_id: string;
  version: number;
  canvas_json: any;
  published: boolean;
  created_at: string;
}

export interface TemplateElement {
  id: string;
  type: "text" | "image" | "shape" | "qr" | "signature" | "badge";
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  content?: string;
  font_family?: string;
  font_size?: number;
  color?: string;
  align?: "left" | "center" | "right";
  is_dynamic?: boolean;
  field_key?: string;
}
