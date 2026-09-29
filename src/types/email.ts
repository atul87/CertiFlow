export type EmailStatus =
  | "pending"
  | "queued"
  | "sent"
  | "delivered"
  | "opened"
  | "clicked"
  | "bounced"
  | "failed"
  | "unsubscribed"
  | "complained";

export interface EmailDelivery {
  id: string;
  status: EmailStatus;
  recipient_name?: string;
  recipient_email: string;
  subject: string;
  certificate_id?: string;
  template_id?: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
  bounce_reason?: string;
  created_at: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  html_body: string;
  text_body?: string;
  variables: string[];
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface SuppressionEntry {
  id: string;
  email: string;
  reason: "bounce" | "complaint" | "unsubscribe";
  created_at: string;
}
