import { SubscriptionPlan } from "./billing";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  logo_url?: string;
  website?: string;
  plan: SubscriptionPlan;
  created_at: string;
}

export interface OrganizationMember {
  id: string;
  user_id: string;
  name: string;
  email: string;
  role: "owner" | "admin" | "member" | "viewer";
  joined_at: string;
}

export interface OrganizationSettings {
  name: string;
  slug: string;
  custom_domain?: string;
  cname_verified?: boolean;
  brand_color?: string;
  logo_url?: string;
}
