#!/usr/bin/env bash
set -e

PORT="${PORT:-8000}"

# If running on Render free tier or EMBEDDED_WORKER is enabled, run ARQ worker in background
if [ "${EMBEDDED_WORKER:-false}" = "true" ]; then
    echo "Starting embedded ARQ worker inside API container..."
    arq app.workers.worker.WorkerSettings &
fi

echo "Starting Uvicorn web server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --workers "${UVICORN_WORKERS:-2}" --proxy-headers
