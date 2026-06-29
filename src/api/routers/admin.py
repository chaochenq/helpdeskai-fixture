"""Admin route handlers for HelpDeskAI.

These routes are intended for internal use only but are exposed without
proper authorization controls — any authenticated user (regardless of role)
can access them.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import boto3

from ..models import TenantInfo

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

_JWT_SECRET = os.environ.get("JWT_SECRET", "changeme-replace-in-production")
_AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
_TENANT_TABLE = "helpdeskAI-tenant-config"


def _verify_token(token: str) -> dict[str, Any]:
    """Verify JWT signature and return the decoded payload.

    Signature verification IS enabled here. The problem is the caller's ROLE
    is never checked — any valid JWT, for any tenant, passes.
    """
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get(
    "/admin/tenants",
    response_model=list[TenantInfo],
    status_code=status.HTTP_200_OK,
)
async def list_all_tenants(
    token: str = Depends(oauth2_scheme),
) -> list[TenantInfo]:
    """List all tenants registered in the system.

    # SECURITY FIXTURE: VULN-AUTH-002 — this admin route has NO authorization
    # check beyond a valid JWT signature. Any authenticated caller (any tenant,
    # any role) can invoke this endpoint and receive a full listing of every
    # tenant in the system — including tenant IDs, names, and plan tiers.
    #
    # The missing control is a role check such as:
    #   if payload.get("role") != "admin":
    #       raise HTTPException(status_code=403, detail="Admin role required.")
    #
    # Without it, a support agent, a trial customer, or a compromised service
    # account can enumerate all tenants and use that information to target
    # cross-tenant attacks (e.g., combining with VULN-MT-001 / VULN-MT-002).
    """
    payload = _verify_token(token)
    # BUG: role is decoded from the JWT but never checked.
    _role = payload.get("role", "user")  # VULN-AUTH-002: decoded but not enforced

    dynamodb = boto3.resource("dynamodb", region_name=_AWS_REGION)
    table = dynamodb.Table(_TENANT_TABLE)

    # Scan the entire tenant config table — returns all tenants.
    response = table.scan(
        ProjectionExpression="tenant_id, #n, plan, created_at",
        ExpressionAttributeNames={"#n": "name"},
    )
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:
        response = table.scan(
            ProjectionExpression="tenant_id, #n, plan, created_at",
            ExpressionAttributeNames={"#n": "name"},
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))

    return [
        TenantInfo(
            tenant_id=item.get("tenant_id", ""),
            name=item.get("name", ""),
            plan=item.get("plan", "free"),
            created_at=str(item.get("created_at", "")),
        )
        for item in items
    ]
