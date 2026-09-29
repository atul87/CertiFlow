export type CertificateStatus = "active" | "revoked" | "expired" | "invalid" | "draft";

export interface Certificate {
  id: string;
  organization_id?: string;
  certificate_number: string;
  verification_code: string;
  status: CertificateStatus;
  recipient_name: string;
  recipient_email?: string;
  program_name?: string;
  issue_date?: string;
  expiry_date?: string;
  template_id: string;
  template_name?: string;
  job_id?: string;
  sha256_hash?: string;
  pdf_url?: string;
  issuer_name?: string;
  metadata?: Record<string, any>;
  revoked_at?: string;
  revocation_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface CertificateTimelineEvent {
  event: string;
  description: string;
  timestamp: string;
  actor?: string;
}
