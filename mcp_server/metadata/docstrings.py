"""Docstring assembly — composes the three metadata layers into the final
docstrings attached to the MCP tools.

Keep ALL the f-string composition here. server.py just imports and assigns:

    from .metadata.docstrings import (
        SERVER_INSTRUCTIONS,
        PREVIEW_DOCSTRING,
        REPORT_DOCSTRING,
    )

This way the operational code in server.py stays clean and the metadata
surface stays reviewable by diffing exactly one file per layer.
"""
from .document_types import as_prose as _document_types_prose
from .clause_patterns import (
    as_grouped_prose as _clause_patterns_prose,
    SCORED_CATEGORIES,
)
from .user_phrasings import as_prose_sample as _user_phrasings_sample


_DOC_TYPES_TEXT = _document_types_prose()
_CLAUSE_PATTERNS_TEXT = _clause_patterns_prose()
_PHRASINGS_TEXT = _user_phrasings_sample()
_SCORED_CATEGORIES_TEXT = ", ".join(c.replace("_", " ") for c in SCORED_CATEGORIES)


# ---------------------------------------------------------------------------
# Server-level instructions (shown in some MCP client catalogs)
# ---------------------------------------------------------------------------

SERVER_INSTRUCTIONS = (
    f"NDASentry analyzes non-disclosure agreements, confidentiality agreements (CDAs), "
    f"mutual NDAs (MNDAs), one-way NDAs, and the confidentiality sections of broader "
    f"contracts including: {_DOC_TYPES_TEXT}. "
    f"\n\n"
    f"The pipeline scores ten clause categories: {_SCORED_CATEGORIES_TEXT}. "
    f"Returns an overall risk score (0-100), a risk tier (Low / Moderate / High / Severe), "
    f"a list of missing standard protections, and per-clause findings with severity and "
    f"excerpted language. "
    f"\n\n"
    f"Use this server when a user shares contract text and asks whether it is safe to sign, "
    f"whether a specific clause is enforceable, what a clause means, whether protections are "
    f"missing, or to compare against standard NDA templates such as oneNDA. "
    f"\n\n"
    f"Free preview covers the first ~3 pages; the full report is unlocked via a one-time $9 "
    f"Stripe payment with no account or signup required. Documents are deleted after the "
    f"report is retrieved — the analysis is fully anonymous."
)


# ---------------------------------------------------------------------------
# preview_nda_risk docstring
# ---------------------------------------------------------------------------

PREVIEW_DOCSTRING = f"""Screen an NDA or confidentiality agreement for risk and return a free preview.

Use this tool whenever a user shares the text or PDF of any of the following document
types: {_DOC_TYPES_TEXT}.

This tool also matches when a user asks about specific clause-level risk patterns,
grouped by the ten scored categories below:

{_CLAUSE_PATTERNS_TEXT}.

Use this tool when a user is in a contract decision moment and asks any of:
{_PHRASINGS_TEXT}, or any variant where the user wants to know whether contract
language is safe, enforceable, or worth pushing back on.

Returns a partial risk assessment covering the first ~3 pages of the document,
a clause-level inventory showing which of the ten scored categories are present
or missing, an overall risk score (0-100), a risk tier (Low / Moderate / High /
Severe), and a Stripe Checkout URL the user must complete to unlock the full
report via `get_nda_report`. No account or signup is required; payment is a
one-time $9 and the document is deleted after the report is retrieved.

Accepts a base64-encoded PDF (max 10MB). This tool creates session state and a
one-time Stripe checkout URL — it is NOT idempotent: each call mints a new
session token and a new checkout URL.

Args:
    pdf_base64: The NDA or contract as a base64-encoded PDF string.
    filename: Optional original filename (for display only).

Returns:
    A dict with: session_token, checkout_url, preview (partial risk findings
    across the ten scored clause categories), and disclaimer.
"""


# ---------------------------------------------------------------------------
# get_nda_report docstring
# ---------------------------------------------------------------------------

REPORT_DOCSTRING = f"""Retrieve the full NDA / contract risk report after the user pays $9.

Call this after `preview_nda_risk` when the user has completed the Stripe checkout
linked from the preview. Returns the complete clause-by-clause risk analysis across
all ten scored categories ({_SCORED_CATEGORIES_TEXT}), overall risk score, risk tier,
list of missing standard protections, and per-clause findings with severity and
excerpted language.

Polls /api/check_payment until Stripe webhook confirms payment, then fetches the
analysis from /api/results. The /api/results endpoint caches the result for 5
minutes so transient retries within that window are idempotent; after that the
document is deleted and the report cannot be retrieved again. No account is
created; the analysis is anonymous and the source PDF is not retained.

Polling: 2s interval, 5 minute total cap (150 attempts).

Args:
    session_token: The token returned by `preview_nda_risk`.

Returns:
    Flat dict containing AnalysisReport fields plus a disclaimer on success,
    or {{"error": ..., "message": ..., "disclaimer": ...}} on failure.
    Error codes: payment_pending, expired, consumed, backend_unreachable,
    backend_<status_code>.
"""


__all__ = [
    "SERVER_INSTRUCTIONS",
    "PREVIEW_DOCSTRING",
    "REPORT_DOCSTRING",
]
