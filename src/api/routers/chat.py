"""Chat route handler for HelpDeskAI.

POST /v1/chat — accepts a customer message and returns the agent reply.

This router uses the INSECURE authentication path: tenant_id is taken from
the X-Tenant-Id request header rather than extracted from the verified JWT.
This is deliberate for the security fixture — it demonstrates VULN-MT-002.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.auth.jwt_validator import get_tenant_from_header
from src.agent.orchestrator import create_orchestrator

from ..models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token", auto_error=False)

_JWT_SECRET = os.environ.get("JWT_SECRET", "changeme-replace-in-production")


def _get_tenant_from_jwt(token: str) -> dict[str, Any]:
    """Correctly verify a JWT and extract the tenant_id from the verified payload.

    # SECURITY FIXTURE: CTRL-AUTH-001 — this helper verifies the JWT signature
    # before trusting any claims. It is defined here to contrast with the insecure
    # path actually used by the /v1/chat endpoint below.
    #
    # NOTE: This function is NOT called by the chat route. The chat route uses
    # get_tenant_from_header() instead (see VULN-MT-002). This function is kept
    # as a reference for the secure implementation pattern.
    """
    payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise ValueError("JWT is missing required tenant_id claim")
    return payload


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    body: ChatRequest,
    request: Request,
    # SECURITY FIXTURE: VULN-MT-002 — tenant_id is extracted from the
    # X-Tenant-Id request header, not from the verified JWT payload.
    # The caller controls this header value entirely, allowing them to
    # impersonate any tenant. The dependency get_tenant_from_header() does
    # no cryptographic verification — it simply returns the raw header string.
    tenant_id: str = Depends(get_tenant_from_header),
    token: str | None = Depends(oauth2_scheme),
) -> ChatResponse:
    """Process a customer chat message and return the agent reply.

    Authentication note: this endpoint accepts an Authorization bearer token
    but ignores its verified claims for tenant resolution. Instead, the
    X-Tenant-Id header is used to determine which tenant's data to access.
    """
    # SECURITY FIXTURE: VULN-AUTH-001 — JWT decoded with signature verification
    # DISABLED. options={"verify_signature": False} means any token, including
    # forged tokens signed with an arbitrary key, is accepted without error.
    # This makes the JWT bearer token meaningless as an authentication mechanism.
    if token:
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # VULN-AUTH-001
                algorithms=["HS256"],
            )
            logger.debug("JWT decoded (signature NOT verified)", extra={"sub": payload.get("sub")})
        except jwt.DecodeError:
            logger.warning("Malformed JWT received — ignoring")

    thread_id = body.thread_id or str(uuid.uuid4())

    orchestrator = create_orchestrator()
    reply = orchestrator.invoke(
        message=body.message,
        tenant_id=tenant_id,
        thread_id=thread_id,
    )

    return ChatResponse(
        reply=reply,
        thread_id=thread_id,
        tenant_id=tenant_id,
    )
