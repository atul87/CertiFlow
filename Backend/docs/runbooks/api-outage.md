# Runbook: API Outage & Service Degradation

## Severity: P0 / Critical

### Overview
This runbook covers diagnosing and resolving general unavailability or high HTTP error rates (5xx / 429) across the CertiFlow API cluster.

---

### 1. Initial Assessment & Healthcheck Triage
1. Probe the API public and readiness health endpoints:
   ```bash
   curl -I https://api.certiflow.io/api/v1/health
   curl -s https://api.certiflow.io/api/v1/health/ready | jq .
   ```
2. Interpret status codes:
   - `HTTP 200`: Core API process is responsive. Check downstream database or Redis latency.
   - `HTTP 503`: Database or Redis connection pool is saturated or unreachable.
   - `HTTP 502 / 504`: Reverse proxy / CDN (Cloudflare/Nginx) cannot reach uvicorn workers.

---

### 2. Check Container & Process Status
1. Check running API container status and resource usage:
   ```bash
   docker ps --filter "name=certiflow-api"
   docker stats --no-stream
   ```
2. Inspect application logs for unhandled crashes or traceback bursts:
   ```bash
   docker logs --tail 200 -f certiflow-api
   ```

---

### 3. Database Dependency Troubleshooting
If logs show `pymongo.errors.ServerSelectionTimeoutError` or `ConnectionRefusedError`:
1. Check MongoDB connectivity:
   ```bash
   mongosh "$MONGODB_URI" --eval "db.adminCommand('ping')"
   ```
2. Check MongoDB connection pool limits. If connections are exhausted, scale up MongoDB Atlas compute tier or increase `maxPoolSize` in database configuration.

---

### 4. Redis Dependency Troubleshooting
If logs show `redis.exceptions.ConnectionError`:
1. Check Redis availability and memory pressure:
   ```bash
   redis-cli -u "$REDIS_URL" ping
   redis-cli -u "$REDIS_URL" info memory
   ```
2. If Redis is in OOM state, verify `maxmemory-policy noeviction` and restart Redis or clear non-persistent cache keys. Note: MongoDB remains authoritative; Redis queue loss does not destroy certificate records.

---

### 5. Graceful Restart & Rollback
1. Perform rolling restart of API instances without dropping active HTTP connections:
   ```bash
   docker-compose -f docker-compose.prod.yml restart api
   ```
2. If recent deployment caused regression, rollback to previous image tag:
   ```bash
   docker-compose -f docker-compose.prod.yml pull api:previous_stable
   docker-compose -f docker-compose.prod.yml up -d --no-deps api
   ```
