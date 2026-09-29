export interface DashboardStats {
  total_certificates: number;
  certificates_this_month: number;
  certificates_change_pct: number;
  total_credentials: number;
  verification_scans: number;
  verification_rate: number;
  emails_sent: number;
  email_delivery_rate: number;
  quota_used_pct: number;
  quota_remaining: number;
  storage_mb: number;
}

export interface TimeSeriesPoint {
  date: string;
  value: number;
}

export interface AnalyticsSummary {
  period: string;
  total_issued: number;
  total_verified: number;
  total_emails: number;
  trends: TimeSeriesPoint[];
  top_templates: Array<{ template_id: string; template_name: string; count: number }>;
}
