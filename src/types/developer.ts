export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  last_four: string;
  scopes: string[];
  status: "active" | "revoked";
  created_at: string;
  last_used_at?: string;
}

export interface Webhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  status: "active" | "inactive";
  secret_prefix: string;
  created_at: string;
  last_triggered_at?: string;
  success_rate: number;
}

export interface WebhookLog {
  id: string;
  webhook_id: string;
  event: string;
  status_code?: number;
  duration_ms?: number;
  delivered_at?: string;
  attempts: number;
  next_retry_at?: string;
  success: boolean;
}

export interface ServiceAccount {
  id: string;
  name: string;
  client_id: string;
  scopes: string[];
  created_at: string;
}
