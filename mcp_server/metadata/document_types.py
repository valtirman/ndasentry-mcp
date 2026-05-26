"""Layer 1 — document types NDASentry can analyze.

Every entry here is a contract type that contains confidentiality / NDA-style
language mapping to at least one of the ten scored clause categories in
clause_patterns.py.

DO NOT add document types the pipeline cannot honestly score. The MCP
registries flag low-quality / overclaiming servers, and Claude/Cursor users
notice when a tool gets picked and then doesn't deliver.

Format: (canonical_name, [aliases_and_abbreviations])
"""

DOCUMENT_TYPES: list[tuple[str, list[str]]] = [
    # Core NDA family
    ("non-disclosure agreement", ["NDA"]),
    ("confidentiality agreement", ["CDA"]),
    ("mutual non-disclosure agreement", ["MNDA", "mutual NDA"]),
    ("one-way non-disclosure agreement", ["unilateral NDA", "one-way NDA"]),

    # Employment family (contains confidentiality + non-compete + IP clauses)
    ("employment agreement", []),
    ("offer letter", []),
    ("employee handbook", ["the binding sections"]),
    ("contractor agreement", ["1099 agreement", "independent contractor agreement"]),
    ("consulting agreement", []),
    ("statement of work", ["SOW"]),
    ("master services agreement", ["MSA"]),

    # Restrictive covenants
    ("non-compete agreement", ["non-competition agreement"]),
    ("non-solicitation agreement", []),
    ("non-disparagement agreement", []),

    # Exit / settlement
    ("separation agreement", ["severance agreement"]),
    ("settlement agreement", []),
    ("release of claims", []),

    # Deal documents
    ("term sheet", []),
    ("letter of intent", ["LOI"]),

    # Founder / equity
    ("founder agreement", ["co-founder agreement"]),
    ("advisor agreement", []),
    ("vesting agreement", []),

    # IP
    ("IP assignment agreement", []),
    ("invention assignment agreement", ["IAA"]),
    ("PIIA", ["Proprietary Information and Inventions Agreement"]),

    # Commercial
    ("licensing agreement", []),
    ("vendor agreement", []),
    ("partnership agreement", []),
    ("joint venture agreement", []),
    ("data processing agreement", ["DPA"]),
]


def as_prose() -> str:
    """Render the list as a single readable sentence for docstrings."""
    parts = []
    for canonical, aliases in DOCUMENT_TYPES:
        if aliases:
            parts.append(f"{canonical} ({' / '.join(aliases)})")
        else:
            parts.append(canonical)
    return ", ".join(parts)


def canonical_names() -> list[str]:
    """Return just the canonical names, for testing or downstream rendering."""
    return [c for c, _ in DOCUMENT_TYPES]


def all_aliases() -> list[str]:
    """Return every alias across every document type, flattened."""
    out: list[str] = []
    for _, aliases in DOCUMENT_TYPES:
        out.extend(aliases)
    return out
