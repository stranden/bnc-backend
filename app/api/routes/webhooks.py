"""NetBox webhook receiver.

NetBox is configured to call this endpoint whenever a BNC-tagged object
changes. The payload is verified (HMAC signature) and logged; the actual
push-to-network step (via Nornir/NAPALM) will be wired in separately once
the core NetBox <-> BNC read path is solid.
"""
from __future__ import annotations

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.config import get_settings
from app.models.schemas import WebhookPayload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_signature(body: bytes, signature: str | None, secret: str) -> None:
    if not secret:
        # No secret configured: skip verification (development only).
        return
    if not signature:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-Hook-Signature header")

    expected = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid webhook signature")


@router.post("/netbox", status_code=status.HTTP_202_ACCEPTED)
async def netbox_webhook(
    request: Request,
    x_hook_signature: str | None = Header(default=None),
) -> dict:
    """Receive a NetBox webhook event for a BNC-tagged object."""
    settings = get_settings()
    body = await request.body()
    _verify_signature(body, x_hook_signature, settings.netbox_webhook_secret)

    payload = WebhookPayload.model_validate_json(body)
    logger.info(
        "Received NetBox webhook: event=%s model=%s request_id=%s",
        payload.event,
        payload.model,
        payload.request_id,
    )

    # TODO: dispatch to the Nornir/NAPALM push pipeline once implemented.

    return {"status": "accepted", "event": payload.event, "model": payload.model}
