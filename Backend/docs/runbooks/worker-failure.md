# Runbook: Background Worker Scaling & Failure Recovery

## Severity: P2 / Moderate

### Overview
This runbook covers diagnosing stuck jobs, dead workers, queue backpressure, and worker memory consumption in CertiFlow.

---

### 1. Queue Depth & Latency Inspection
Inspect pending queue length using Redis CLI:
```bash
redis-cli -u "$REDIS_URL" llen "arq:queue"
```
Healthy threshold: $< 200$ items.
Alert threshold: $> 1000$ items or jobs stalled $> 5$ minutes.

---

### 2. Identifying Worker Container Health
Check worker heartbeat and container logs:
```bash
docker ps --filter "name=worker"
docker logs --tail 100 certiflow-worker-certificate
```
Common issues:
- OOMKilled (Exit code 137): Worker exceeded memory limit when rendering high-DPI image assets.
  - Fix: Increase container memory limit or decrease concurrency (`WORKER_CONCURRENCY=5`).
- Font loading exception: Missing TTF font file for custom template.
  - Fix: Verify font directory mount at `/app/storage/fonts`.

---

### 3. Recovering Stranded Job Items
If a worker crashes while processing a batch, items may remain in `processing` state:
1. Locate items claimed by dead worker:
   ```javascript
   db.issuance_job_items.find({
     status: "processing",
     updated_at: { $lt: new Date(Date.now() - 15 * 60 * 1000) }
   });
   ```
2. Reset stranded items back to `pending`:
   ```javascript
   db.issuance_job_items.updateMany(
     { status: "processing", updated_at: { $lt: new Date(Date.now() - 15 * 60 * 1000) } },
     { $set: { status: "pending" } }
   );
   ```

---

### 4. Horizontal Worker Autoscaling
Under high issuance spikes:
```bash
# Scale certificate generation workers to 4 replicas
docker-compose -f docker-compose.prod.yml up -d --scale worker-certificate=4
```
Workers will automatically coordinate and divide work atomically via MongoDB item claiming (`claim_next`).
