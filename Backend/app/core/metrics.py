"""
In-memory Prometheus-compatible metrics collector and exporter.
Tracks HTTP requests, latencies, errors, certificate generation,
emails, and verification events without requiring heavy external dependencies.
"""
from __future__ import annotations
import threading
import time
from collections import defaultdict
from typing import Dict, Tuple


class MetricsCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._http_requests: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self._http_durations: Dict[Tuple[str, str], float] = defaultdict(float)
        self._http_errors: Dict[Tuple[str, str], int] = defaultdict(int)
        self._certificates_generated: Dict[str, int] = defaultdict(int)
        self._emails_sent: Dict[str, int] = defaultdict(int)
        self._verifications: Dict[str, int] = defaultdict(int)

    def record_http_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        # Normalize path to avoid high cardinality (strip query string, truncate IDs)
        normalized_path = self._normalize_path(path)
        with self._lock:
            key = (method, normalized_path, status_code)
            self._http_requests[key] += 1
            self._http_durations[(method, normalized_path)] += duration_seconds
            if status_code >= 400:
                self._http_errors[(normalized_path, str(status_code))] += 1

    def inc_certificate_generated(self, status: str = "issued") -> None:
        with self._lock:
            self._certificates_generated[status] += 1

    def inc_email_sent(self, status: str = "delivered") -> None:
        with self._lock:
            self._emails_sent[status] += 1

    def inc_verification(self, status: str = "valid") -> None:
        with self._lock:
            self._verifications[status] += 1

    def _normalize_path(self, path: str) -> str:
        # Simple path normalizer to prevent high cardinality
        parts = path.split("?")[0].strip("/").split("/")
        clean_parts = []
        for p in parts:
            # If 24 hex characters (Mongo ObjectId) or long uuid, replace with :id
            if len(p) >= 20 and (p.isalnum() or "-" in p):
                clean_parts.append(":id")
            else:
                clean_parts.append(p)
        return "/" + "/".join(clean_parts) if clean_parts else "/"

    def generate_prometheus_text(self) -> str:
        lines = []

        # 1. HTTP requests total
        lines.append("# HELP certiflow_http_requests_total Total number of HTTP requests processed.")
        lines.append("# TYPE certiflow_http_requests_total counter")
        with self._lock:
            for (method, path, status_code), count in self._http_requests.items():
                lines.append(f'certiflow_http_requests_total{{method="{method}",path="{path}",status="{status_code}"}} {count}')

        # 2. HTTP errors total
        lines.append("# HELP certiflow_http_errors_total Total number of HTTP error responses.")
        lines.append("# TYPE certiflow_http_errors_total counter")
        with self._lock:
            for (path, code), count in self._http_errors.items():
                lines.append(f'certiflow_http_errors_total{{path="{path}",status="{code}"}} {count}')

        # 3. Certificates generated
        lines.append("# HELP certiflow_certificates_total Total certificates processed.")
        lines.append("# TYPE certiflow_certificates_total counter")
        with self._lock:
            for status, count in self._certificates_generated.items():
                lines.append(f'certiflow_certificates_total{{status="{status}"}} {count}')

        # 4. Emails sent
        lines.append("# HELP certiflow_emails_total Total emails processed.")
        lines.append("# TYPE certiflow_emails_total counter")
        with self._lock:
            for status, count in self._emails_sent.items():
                lines.append(f'certiflow_emails_total{{status="{status}"}} {count}')

        # 5. Verifications total
        lines.append("# HELP certiflow_verifications_total Total certificate verifications performed.")
        lines.append("# TYPE certiflow_verifications_total counter")
        with self._lock:
            for status, count in self._verifications.items():
                lines.append(f'certiflow_verifications_total{{status="{status}"}} {count}')

        return "\n".join(lines) + "\n"


# Global singleton collector
metrics = MetricsCollector()
