# Runbook: Disaster Recovery & Data Restoration

## Severity: P0 / Emergency

### Overview
This procedure details full recovery following catastrophic data loss, database corruption, or regional cloud provider outages.

Target Recovery Objectives:
- **Recovery Point Objective (RPO)**: $\le 1$ hour (maximum acceptable data loss window)
- **Recovery Time Objective (RTO)**: $\le 4$ hours (full service restoration to production traffic)

---

### 1. MongoDB Database Restoration
1. Stop all application containers to prevent partial or inconsistent writes:
   ```bash
   docker-compose -f docker-compose.prod.yml down api worker-certificate worker-email
   ```
2. Locate the most recent point-in-time snapshot or daily cold backup archive:
   ```bash
   aws s3 ls s3://certiflow-db-backups-ap-south-1/mongodb/
   ```
3. Restore the backup archive to a freshly provisioned MongoDB cluster:
   ```bash
   mongorestore --uri="$TARGET_MONGODB_URI" --gzip --archive=/tmp/certiflow_backup_latest.gz --drop
   ```
4. Verify document counts across critical collections:
   ```javascript
   db.organizations.countDocuments();
   db.certificates.countDocuments();
   db.subscriptions.countDocuments();
   db.usage_counters.countDocuments();
   ```

---

### 2. Redis Recovery & Re-queueing
1. If Redis data was lost:
   - Start a clean Redis instance.
   - All state in Redis is ephemeral (rate limits, queues, locks).
   - Core state resides authoritatively in MongoDB.
2. Re-queue stranded `processing` or `pending` issuance jobs:
   ```javascript
   // Query jobs that were in progress when outage hit
   db.issuance_jobs.find({ status: "processing" });
   ```
3. Re-dispatch uncompleted job items via the IssuanceService retry API.

---

### 3. Object Storage Validation
1. Verify S3 bucket access and file integrity for PDF and preview assets:
   ```bash
   aws s3 ls s3://certiflow-production-assets/certificates/ --summarize
   ```
2. If primary storage region was corrupted, switch DNS and `S3_ENDPOINT` to cross-region replica bucket.

---

### 4. Verification & Smoke Test
1. Start the API in staging/maintenance mode.
2. Execute automated smoke tests:
   ```bash
   pytest tests/integration/test_health_and_security.py
   pytest tests/integration/test_billing_and_subscriptions.py
   ```
3. Shift production DNS traffic back to the primary cluster.
