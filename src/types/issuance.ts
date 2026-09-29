export type IssuanceJobStatus =
  | "queued"
  | "running"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled"
  | "partial";

export type IssuancePriority = "high" | "normal" | "low";

export interface IssuanceJob {
  id: string;
  organization_id?: string;
  name?: string;
  status: IssuanceJobStatus;
  priority: IssuancePriority;
  template_id: string;
  template_name?: string;
  import_id?: string;
  total: number;
  completed: number;
  failed: number;
  progress: number; // 0–100
  zip_url?: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
  estimated_completion?: string;
  estimated_remaining_seconds?: number;
}

export interface CreateJobPayload {
  name?: string;
  template_id: string;
  import_id?: string;
  recipients?: Array<Record<string, string>>;
  priority?: IssuancePriority;
  send_email?: boolean;
}
