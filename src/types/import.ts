export type ImportStatus =
  | "uploading"
  | "analyzing"
  | "pending_mapping"
  | "mapping"
  | "validating"
  | "pending_confirmation"
  | "confirmed"
  | "failed";

export interface ImportRecord {
  id: string;
  original_filename: string;
  status: ImportStatus;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  column_headers: string[];
  suggested_mapping?: Record<string, string>;
  confirmed_mapping?: Record<string, string>;
  template_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ImportRow {
  row_number: number;
  data: Record<string, string>;
  is_valid: boolean;
  errors: Array<{ field: string; message: string }>;
}

export interface ColumnConfidence {
  csv_header: string;
  mapped_field: string;
  confidence: number; // 0 - 100
  sample_values: string[];
}
