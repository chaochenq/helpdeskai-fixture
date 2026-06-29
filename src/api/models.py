"""Pydantic request and response models for the HelpDeskAI API."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    tenant_id: str


class KBUploadRequest(BaseModel):
    document_key: str
    content_base64: str


class KBUploadResponse(BaseModel):
    document_key: str
    tenant_id: str
    uploaded: bool


class TenantInfo(BaseModel):
    tenant_id: str
    name: str
    plan: str
    created_at: str
