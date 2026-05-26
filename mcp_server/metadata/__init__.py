"""NDASentry MCP server metadata package.

Three reviewable layers + a docstring assembler:

  document_types.py   -- Layer 1: document types the pipeline handles
  clause_patterns.py  -- Layer 2: clause-level risk patterns (mapped to scored categories)
  user_phrasings.py   -- Layer 3: real user query phrasings to match against
  docstrings.py       -- Composes the three layers into final MCP tool docstrings

Edit one file, get consistent updates across all surfaces (MCP tool descriptions,
Smithery listing, registry pack, ndasentry.ai/taxonomy page).
"""
from .document_types import (
    DOCUMENT_TYPES,
    as_prose as document_types_prose,
    canonical_names,
    all_aliases,
)
from .clause_patterns import (
    CLAUSE_PATTERNS,
    SCORED_CATEGORIES,
    as_grouped_prose as clause_patterns_prose,
    patterns_for_category,
    validate as validate_clause_patterns,
)
from .user_phrasings import (
    ENFORCEABILITY_QUESTIONS,
    MEANING_QUESTIONS,
    DECISION_QUESTIONS,
    LIFE_EVENT_CONTEXTS,
    DOCUMENT_HANDOFF_PHRASES,
    all_phrasings,
    as_prose_sample as user_phrasings_sample,
    by_category as user_phrasings_by_category,
)
from .docstrings import (
    SERVER_INSTRUCTIONS,
    PREVIEW_DOCSTRING,
    REPORT_DOCSTRING,
)

__all__ = [
    # Layer 1
    "DOCUMENT_TYPES",
    "document_types_prose",
    "canonical_names",
    "all_aliases",
    # Layer 2
    "CLAUSE_PATTERNS",
    "SCORED_CATEGORIES",
    "clause_patterns_prose",
    "patterns_for_category",
    "validate_clause_patterns",
    # Layer 3
    "ENFORCEABILITY_QUESTIONS",
    "MEANING_QUESTIONS",
    "DECISION_QUESTIONS",
    "LIFE_EVENT_CONTEXTS",
    "DOCUMENT_HANDOFF_PHRASES",
    "all_phrasings",
    "user_phrasings_sample",
    "user_phrasings_by_category",
    # Assembled docstrings
    "SERVER_INSTRUCTIONS",
    "PREVIEW_DOCSTRING",
    "REPORT_DOCSTRING",
]
