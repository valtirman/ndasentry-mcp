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

For full README, see the repository root.
"""
from __future__ import annotations

import base64
import os

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

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
# The name is what agents see in their tool catalog.
mcp = FastMCP("ndasentry", transport_security=_security)


@mcp.tool(
    annotations={
        "title": "Preview NDA risk (free)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
def preview_nda_risk(pdf_base64: str, filename: str = "nda.pdf") -> dict:
    """Stage an NDA for analysis and return a free risk preview.

    Accepts a base64-encoded PDF (max 10MB). Returns a partial risk
    assessment covering the first ~3 pages of the document plus a
    Stripe Checkout URL the user must complete to unlock the full
    report via `get_nda_report`.

    This tool creates session state and a one-time Stripe checkout
    URL. It is NOT idempotent: each call mints a new session token
    and a new checkout URL.

    Args:
        pdf_base64: The NDA as a base64-encoded PDF string.
        filename: Optional original filename (for display only).

    Returns:
        A dict with: session_token, checkout_url, preview (partial
        risk findings), and disclaimer.
    """
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
        "title": "Get full NDA report (paid)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
def get_nda_report(session_token: str) -> dict:
    """Retrieve the full NDA risk report for a paid session.

    Polls /api/check_payment until Stripe webhook confirms payment, then
    calls /api/results to fetch the analysis. The /api/results endpoint
    caches the result for 5 minutes so transient retries within that
    window are idempotent.

    Polling: 2s interval, 5 minute total cap (150 attempts).

    Args:
        session_token: The token returned by `preview_nda_risk`.

    Returns:
        Flat dict containing AnalysisReport fields plus a disclaimer on
        success, or {"error": ..., "message": ..., "disclaimer": ...} on
        failure. Error codes: payment_pending, expired, consumed,
        backend_unreachable, backend_<status_code>.
    """
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
