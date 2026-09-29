export type ReportType =
  | "certificates"
  | "issuance"
  | "emails"
  | "verification"
  | "credentials"
  | "analytics";

export interface Report {
  id: string;
  name: string;
  type: ReportType;
  status: "generating" | "ready" | "failed";
  format: "csv" | "pdf";
  download_url?: string;
  created_at: string;
  generated_at?: string;
  row_count?: number;
}

export interface CreateReportPayload {
  name: string;
  type: ReportType;
  format: "csv" | "pdf";
  date_from?: string;
  date_to?: string;
}
