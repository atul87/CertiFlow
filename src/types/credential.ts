export type CredentialStatus = "issued" | "active" | "suspended" | "revoked" | "expired";

export interface Achievement {
  id: string;
  name: string;
  description: string;
  criteria: string;
  skills: string[];
  image_url?: string;
  type: string;
  created_at: string;
  updated_at: string;
}

export interface DigitalCredential {
  id: string;
  status: CredentialStatus;
  recipient_name: string;
  recipient_email?: string;
  achievement_id: string;
  achievement?: Achievement;
  certificate_id?: string;
  issued_at: string;
  expires_at?: string;
  revoked_at?: string;
  revocation_reason?: string;
  suspension_reason?: string;
  credential_id: string; // W3C VC ID
  public_url: string;
  created_at: string;
}

export interface IssuerProfile {
  id: string;
  name: string;
  display_name?: string;
  did: string;
  website?: string;
  description?: string;
  contact_email?: string;
  logo_url?: string;
  active_key_id: string;
  public_key_jwk?: Record<string, any>;
}

export interface SigningKey {
  id: string;
  algorithm: string;
  status: "active" | "archived" | "revoked";
  created_at: string;
  activated_at?: string;
  archived_at?: string;
}
