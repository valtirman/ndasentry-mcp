"""NDASentry MCP server.

Exposes the NDA risk analysis pipeline as MCP tools so AI agents
(Claude Desktop, Cursor, etc.) can discover and invoke it directly.

Two tools:
  preview_nda_risk(pdf_base64, filename) -- free regex-based preview,
    returns clause-level summary plus a Stripe payment link.
  get_nda_report(session_token) -- paid full report after Stripe payment
    verifies, returns structured AnalysisReport JSON.

Thin protocol adapter: this module does no analysis itself. It serializes
agent-side calls into HTTP requests against the NDASentry backend
(default https://ndasentry.ai) which runs the analyzer pipeline.

Tool metadata (server description + tool docstrings) is composed from
three reviewable layers in `mcp_server/metadata/`:
  - document_types.py   (Layer 1: document types we can analyze)
  - clause_patterns.py  (Layer 2: clause patterns mapped to scored categories)
  - user_phrasings.py   (Layer 3: real user query phrasings)
Edit there, not here.

For full README, see the repository root.
"""
from __future__ import annotations

import base64
import os

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .metadata import (
    SERVER_INSTRUCTIONS,
    PREVIEW_DOCSTRING,
    REPORT_DOCSTRING,
)


def _with_docstring(docstring: str):
    """Decorator that sets __doc__ on a function BEFORE other decorators run.

    Why: @mcp.tool reads func.__doc__ at decoration time and snapshots it as
    the MCP tool description. If we assign __doc__ after @mcp.tool, the tool
    description ends up empty. This helper ensures the docstring is in place
    BEFORE @mcp.tool sees the function.

    Usage:
        @mcp.tool(annotations={...})
        @_with_docstring(MY_COMPOSED_DOCSTRING)
        def my_tool(...):
            ...
    """
    def _apply(fn):
        fn.__doc__ = docstring
        return fn
    return _apply


# Backend URL. Default to local dev. Override via env in production.
BACKEND_URL = os.getenv("NDASENTRY_BACKEND_URL", "http://localhost:8001")

# Disclaimer string. MUST appear in every tool response payload.
# This is the line that makes NDASentry a screening tool, not a law firm.
DISCLAIMER = (
    "NDASentry is a contract risk screening tool, not a law firm. "
    "Output is not legal advice. For binding legal interpretation, "
    "consult a licensed attorney."
)

# Configure transport security (DNS rebinding protection).
# Default allowlist is local-only; production hosts must be added via
# MCP_ALLOWED_HOSTS / MCP_ALLOWED_ORIGINS env vars (comma-separated).
_default_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
_default_origins = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]

_extra_hosts = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
_extra_origins = [o.strip() for o in os.getenv("MCP_ALLOWED_ORIGINS", "").split(",") if o.strip()]

_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=_default_hosts + _extra_hosts,
    allowed_origins=_default_origins + _extra_origins,
)

# Initialize the MCP server.
# `name` is what agents see in their tool catalog.
# `instructions` is the server-level description shown in catalogs that
# support it — composed from the three metadata layers.
mcp = FastMCP(
    "ndasentry",
    instructions=SERVER_INSTRUCTIONS,
    transport_security=_security,
)


@mcp.tool(
    annotations={
        "title": "Screen an NDA / contract for risk (free preview)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
@_with_docstring(PREVIEW_DOCSTRING)
def preview_nda_risk(pdf_base64: str, filename: str = "nda.pdf") -> dict:
    # Decode the base64 PDF. Reject empty or malformed input early
    # so the agent gets a clean error before any network round-trip.
    if not pdf_base64:
        return {"error": "empty_input", "message": "pdf_base64 is empty.", "disclaimer": DISCLAIMER}
    try:
        pdf_bytes = base64.b64decode(pdf_base64, validate=True)
    except Exception as exc:
        return {"error": "bad_base64", "message": f"Could not decode pdf_base64: {exc}", "disclaimer": DISCLAIMER}

    if len(pdf_bytes) > 10 * 1024 * 1024:
        return {"error": "too_large", "message": "PDF exceeds 10MB limit.", "disclaimer": DISCLAIMER}

    # POST to the backend preview endpoint as multipart, same shape as /api/upload.
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{BACKEND_URL}/api/preview",
                files={"file": (filename, pdf_bytes, "application/pdf")},
            )
    except httpx.HTTPError as exc:
        return {"error": "backend_unreachable", "message": f"Backend call failed: {exc}", "disclaimer": DISCLAIMER}

    if resp.status_code != 200:
        # Surface backend error verbatim — backend already formats user-safe messages.
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        return {"error": f"backend_{resp.status_code}", "message": detail, "disclaimer": DISCLAIMER}

    # Backend response already includes disclaimer; pass through as-is.
    return resp.json()


@mcp.tool(
    annotations={
        "title": "Unlock full NDA / contract risk report (after $9 payment)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
@_with_docstring(REPORT_DOCSTRING)
def get_nda_report(session_token: str) -> dict:
    import time as _time

    if not session_token:
        return {"error": "empty_input", "message": "session_token is empty.", "disclaimer": DISCLAIMER}

    POLL_INTERVAL_S = 2.0
    POLL_MAX_ATTEMPTS = 150

    session_id: str | None = None

    try:
        with httpx.Client(timeout=10.0) as client:
            for _ in range(POLL_MAX_ATTEMPTS):
                try:
                    cp = client.get(
                        f"{BACKEND_URL}/api/check_payment",
                        params={"token": session_token},
                    )
                except httpx.HTTPError as exc:
                    return {
                        "error": "backend_unreachable",
                        "message": f"check_payment failed: {exc}",
                        "disclaimer": DISCLAIMER,
                    }

                if cp.status_code != 200:
                    try:
                        detail = cp.json().get("detail", cp.text)
                    except Exception:
                        detail = cp.text
                    return {
                        "error": f"backend_{cp.status_code}",
                        "message": detail,
                        "disclaimer": DISCLAIMER,
                    }

                body = cp.json()
                status = body.get("status")

                if status == "paid":
                    session_id = body.get("session_id")
                    break
                if status == "expired":
                    return {
                        "error": "expired",
                        "message": "Upload token has expired or was never staged.",
                        "disclaimer": DISCLAIMER,
                    }
                _time.sleep(POLL_INTERVAL_S)
            else:
                return {
                    "error": "payment_pending",
                    "message": "Payment not completed within 5 minutes.",
                    "disclaimer": DISCLAIMER,
                }

            if not session_id:
                return {
                    "error": "backend_unreachable",
                    "message": "check_payment returned paid but no session_id.",
                    "disclaimer": DISCLAIMER,
                }

            try:
                rr = client.post(
                    f"{BACKEND_URL}/api/results",
                    data={"session_id": session_id},
                    timeout=120.0,
                )
            except httpx.HTTPError as exc:
                return {
                    "error": "backend_unreachable",
                    "message": f"results call failed: {exc}",
                    "disclaimer": DISCLAIMER,
                }

            if rr.status_code == 409:
                return {
                    "error": "consumed",
                    "message": "Report was already retrieved and the cache has expired.",
                    "disclaimer": DISCLAIMER,
                }
            if rr.status_code != 200:
                try:
                    detail = rr.json().get("detail", rr.text)
                except Exception:
                    detail = rr.text
                return {
                    "error": f"backend_{rr.status_code}",
                    "message": detail,
                    "disclaimer": DISCLAIMER,
                }

            report = rr.json()
            if isinstance(report, dict) and "disclaimer" not in report:
                report["disclaimer"] = DISCLAIMER
            return report

    except Exception as exc:
        return {
            "error": "internal",
            "message": f"Unexpected error: {exc}",
            "disclaimer": DISCLAIMER,
        }


if __name__ == "__main__":
    # Streamable HTTP transport on /mcp.
    # Port 1966 locally; production port set by deploy environment.
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.getenv("PORT", "1966"))
    mcp.run(transport="streamable-http")
