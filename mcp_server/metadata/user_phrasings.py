"""Layer 3 — real user phrasings that should route to NDASentry.

Tool selection in LLMs does semantic matching against user intent. Users
don't say "analyze my non-disclosure agreement" — they say "is this legal"
or "should I sign this." This file lists the literal phrasings so the
model has surface area to match against.

Grouped by intent for readability and future eval / test work.
"""

ENFORCEABILITY_QUESTIONS: list[str] = [
    "is this NDA enforceable",
    "can they actually enforce this",
    "is this legal in California",
    "is this legal in Texas",
    "is this legal in Colorado",
    "is this legal in New York",
    "is this legal in my state",
    "is in perpetuity legal",
    "is this clause valid",
    "would this hold up in court",
    "is my non-compete enforceable",
    "is this arbitration clause enforceable",
    "can they hold me to this after I leave",
]

MEANING_QUESTIONS: list[str] = [
    "what does this clause mean",
    "what does in perpetuity mean",
    "what is a residual knowledge clause",
    "what is a non-solicitation clause",
    "what is mutual confidentiality",
    "what is compelled disclosure",
    "what does injunctive relief mean",
    "what is a forum selection clause",
    "what is a survival clause",
    "what is a non-circumvention clause",
    "what's the difference between an NDA and a CDA",
    "what is garden leave",
]

DECISION_QUESTIONS: list[str] = [
    "should I sign this",
    "is this NDA fair",
    "is this normal",
    "is this standard",
    "is this safe to sign",
    "what's missing from this NDA",
    "what should I push back on",
    "what should I negotiate",
    "what are the red flags",
    "is there anything weird in this",
    "should I have a lawyer look at this",
]

LIFE_EVENT_CONTEXTS: list[str] = [
    "I got a job offer",
    "my employer wants me to sign",
    "I'm being laid off and they want me to sign a release",
    "I just got severance papers",
    "I'm being acquired",
    "I'm leaving to start a company",
    "I'm raising a round and the VC sent a term sheet",
    "I got handed an NDA at the meeting",
    "they want me to sign before the interview",
    "vendor wants me to sign their NDA",
    "customer NDA review",
    "due diligence NDA",
    "M&A confidentiality agreement",
    "advisor agreement before joining a startup",
    "I'm signing a 1099 contractor agreement",
]

DOCUMENT_HANDOFF_PHRASES: list[str] = [
    "review my NDA",
    "review my employment contract",
    "review my offer letter",
    "review my severance agreement",
    "review my term sheet",
    "review my contractor agreement",
    "review my consulting agreement",
    "look at this contract",
    "tell me what's wrong with this NDA",
    "score this NDA",
    "rate this NDA",
    "screen this contract for risk",
    "check this NDA",
    "audit this NDA",
]


def all_phrasings() -> list[str]:
    """Return every phrasing across every category, flattened."""
    return (
        ENFORCEABILITY_QUESTIONS
        + MEANING_QUESTIONS
        + DECISION_QUESTIONS
        + LIFE_EVENT_CONTEXTS
        + DOCUMENT_HANDOFF_PHRASES
    )


def as_prose_sample(n: int = 16) -> str:
    """Return a representative cross-section joined as quoted, comma-separated."""
    sample = (
        ENFORCEABILITY_QUESTIONS[:4]
        + MEANING_QUESTIONS[:3]
        + DECISION_QUESTIONS[:3]
        + LIFE_EVENT_CONTEXTS[:3]
        + DOCUMENT_HANDOFF_PHRASES[:3]
    )
    return ", ".join(f'"{p}"' for p in sample[:n])


def by_category() -> dict[str, list[str]]:
    """Return phrasings grouped by intent category."""
    return {
        "enforceability_questions": ENFORCEABILITY_QUESTIONS,
        "meaning_questions": MEANING_QUESTIONS,
        "decision_questions": DECISION_QUESTIONS,
        "life_event_contexts": LIFE_EVENT_CONTEXTS,
        "document_handoff_phrases": DOCUMENT_HANDOFF_PHRASES,
    }
