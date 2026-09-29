export interface VerificationResult {
  valid: boolean;
  status: "VALID" | "REVOKED" | "EXPIRED" | "NOT_FOUND" | "INVALID";
  certificate?: {
    certificate_number: string;
    recipient_name: string;
    program_name?: string;
    issue_date?: string;
    issuer_name?: string;
    issuer_website?: string;
    issuer_logo_url?: string;
  };
  revoked_at?: string;
  revocation_reason?: string;
  verified_at: string;
  message?: string;
}
