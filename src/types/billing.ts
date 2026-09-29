export type SubscriptionPlan =
  | "free"
  | "starter"
  | "growth"
  | "scale"
  | "professional"
  | "enterprise";

export interface Subscription {
  id: string;
  plan_id: string;
  plan_name: string;
  status: "active" | "past_due" | "cancelled" | "trialing";
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  amount: number;
  currency: string;
  interval: "month" | "year";
  seats: number;
  trial_end?: string;
}

export interface UsageMeter {
  id: string;
  label: string;
  used: number;
  limit: number;
  unit: string;
  overage_rate?: number;
  color?: string;
}

export interface UsageMeters {
  plan: SubscriptionPlan;
  period: string;
  certificates: { used: number; limit: number; percent: number };
  emails: { used: number; limit: number; percent: number };
  storage_mb: { used: number; limit: number; percent: number };
  api_requests: { used: number; limit: number; percent: number };
  credentials?: { used: number; limit: number; percent: number };
  meters?: UsageMeter[];
}

export interface Invoice {
  id: string;
  invoice_number: string;
  amount: number;
  currency: string;
  status: "paid" | "open" | "pending" | "failed" | "void";
  period_start: string;
  period_end: string;
  issued_at?: string;
  paid_at?: string;
  pdf_url?: string;
  created_at: string;
}

export interface PlanPricing {
  id: SubscriptionPlan;
  name: string;
  description: string;
  monthly_price: number;
  yearly_price: number;
  certificate_quota: number;
  features: string[];
  is_popular?: boolean;
}
