from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class WebhookEndpointCreateRequest(BaseModel):
    url: str
    events: List[str] = Field(..., min_items=1)
    description: Optional[str] = Field(None, max_length=250)


class WebhookEndpointUpdateRequest(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    status: Optional[str] = None  # active, disabled
    description: Optional[str] = None


class WebhookEndpointResponse(BaseModel):
    id: str
    organization_id: str
    url: str
    events: List[str]
    status: str
    description: Optional[str] = None
    # Secret is returned only upon initial creation or rotation
    secret: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class WebhookEndpointListResponse(BaseModel):
    items: List[WebhookEndpointResponse]
    total: int


class WebhookDeliveryResponse(BaseModel):
    id: str
    organization_id: str
    webhook_endpoint_id: str
    event_id: str
    event_type: str
    attempt: int
    status: str
    http_status: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None


class WebhookDeliveryListResponse(BaseModel):
    items: List[WebhookDeliveryResponse]
    total: int


class WebhookTestResponse(BaseModel):
    success: bool
    delivery_id: str
    http_status: Optional[int] = None
    message: str
