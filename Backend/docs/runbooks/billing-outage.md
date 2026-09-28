# Runbook: Billing Outage & Webhook Desynchronization

## Severity: P1 / High

### Overview
This runbook guides on-call engineers when customer payments, plan upgrades, subscription cancellations, or inbound billing webhooks fail or stall.

---

### 1. Inbound Webhook Health Check
Check whether the payment provider (Stripe, Razorpay, or Mock Provider) is able to reach CertiFlow webhook endpoints:
```bash
# Verify webhook endpoint route is responding to test ping
curl -X POST https://api.certiflow.io/api/v1/billing/webhooks/mock \
  -H "Content-Type: application/json" \
  -d '{"event_id":"ping"}'
```
Expected result: `HTTP 401 Unauthorized` (indicating webhook signature verification is active).

---

### 2. Inspecting Failed Webhook Events in MongoDB
All incoming billing webhooks are logged in `billing_events` with their processing status:
```javascript
// Connect via mongosh
use certiflow_production;

// Find unprocessed or failed billing events in the last 24 hours
db.billing_events.find({
  processed: false,
  created_at: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
}).sort({ created_at: -1 });
```

---

### 3. Diagnosing Signature Verification Failures
If webhooks return `401 Unauthorized`:
1. Verify that `BILLING_WEBHOOK_SECRET` matches the active signing secret in the payment provider dashboard.
2. Confirm the raw request body has not been modified or formatted by intermediate reverse proxies before HMAC verification.
3. Check for clock drift between server and provider timestamp headers.

---

### 4. Handling Webhook Retries & Idempotency
CertiFlow features built-in idempotency via a unique index on `(provider, event_id)`:
1. Re-delivering an already-processed webhook from the provider portal is completely safe.
2. If an event was missed during an API restart:
   - Use the provider dashboard to trigger "Resend failed webhooks".
   - CertiFlow will process the event and idempotently update the organization's subscription without generating duplicate invoices.

---

### 5. Grace Period & Past-Due Manual Interventions
If a customer’s subscription is `past_due` due to credit card expiry:
1. Confirm the customer is currently in their 7-day grace period (`BILLING_GRACE_PERIOD_DAYS=7`).
2. Existing generated certificates and public verification links remain fully accessible.
3. Support admins can grant temporary promotional certificate quotas via:
   `POST /api/v1/admin/organizations/{id}/entitlements/grant`
