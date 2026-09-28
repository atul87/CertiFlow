from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class APIUsageMetricsResponse(BaseModel):
    period: str
    total_requests: int = 0
    successful_2xx: int = 0
    client_errors_4xx: int = 0
    server_errors_5xx: int = 0
    rate_limited_429: int = 0
    average_latency_ms: float = 0.0
    by_key: List[Dict[str, Any]] = []
    by_endpoint: List[Dict[str, Any]] = []
