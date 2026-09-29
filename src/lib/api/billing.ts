import { apiRequest } from "./client";
import { Subscription, UsageMeters, Invoice, PlanPricing } from "@/types";

export const billingApi = {
  getSubscription: () =>
    apiRequest<Subscription>("/api/v1/billing/subscription"),

  getUsage: () =>
    apiRequest<UsageMeters>("/api/v1/billing/usage"),

  listInvoices: () =>
    apiRequest<Invoice[]>("/api/v1/billing/invoices"),

  getInvoices: () =>
    apiRequest<Invoice[]>("/api/v1/billing/invoices"),

  listPlans: () =>
    apiRequest<PlanPricing[]>("/api/v1/billing/plans"),

  updateSubscription: (payload: { plan_id: string; interval: "month" | "year" }) =>
    apiRequest<Subscription>("/api/v1/billing/subscription", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  cancelSubscription: () =>
    apiRequest<Subscription>("/api/v1/billing/subscription/cancel", {
      method: "POST",
    }),
};
