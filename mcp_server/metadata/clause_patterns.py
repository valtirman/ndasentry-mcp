"""Layer 2 — clause-level risk patterns NDASentry can identify.

INTEGRITY CONSTRAINT: every pattern here maps to one of the ten scored
clause categories from backend/benchmarks/reference/*.json. If you add a
pattern, it MUST map to a category the pipeline actually scores —
otherwise the tool description overclaims and the report won't match the
metadata promise.

The ten scored categories (ground truth):
  - confidential_information_definition
  - exclusions
  - term_and_survival
  - return_or_destruction
  - compelled_disclosure
  - injunctive_relief
  - use_restrictions
  - governing_law
  - assignment
  - non_solicit_or_non_compete

Each entry: (user_facing_pattern_name, scored_category, why_it_matters)
"""

SCORED_CATEGORIES: list[str] = [
    "confidential_information_definition",
    "exclusions",
    "term_and_survival",
    "return_or_destruction",
    "compelled_disclosure",
    "injunctive_relief",
    "use_restrictions",
    "governing_law",
    "assignment",
    "non_solicit_or_non_compete",
]


CLAUSE_PATTERNS: list[tuple[str, str, str]] = [
    # confidential_information_definition
    (
        "overbroad definition of confidential information",
        "confidential_information_definition",
        "Anything-and-everything definitions are unenforceable and expose the recipient to perpetual liability.",
    ),
    (
        "vague or undefined confidential information",
        "confidential_information_definition",
        "Without a clear definition the agreement is hard to comply with and hard to enforce.",
    ),
    (
        "oral disclosures swept in without written confirmation",
        "confidential_information_definition",
        "Oral-disclosure inclusion without a follow-up writing requirement creates after-the-fact ambiguity over what was actually confidential.",
    ),

    # exclusions
    (
        "missing standard exclusions (publicly known, independently developed, rightfully received)",
        "exclusions",
        "Standard NDAs carve out information you already knew or that becomes public; missing carve-outs trap the recipient.",
    ),
    (
        "narrow or one-sided exclusions",
        "exclusions",
        "One party gets exclusions, the other doesn't — favors the discloser.",
    ),
    (
        "missing 'required by law' exclusion",
        "exclusions",
        "Without a legal-requirement exclusion, complying with a court order can technically breach the NDA.",
    ),

    # term_and_survival
    (
        "perpetual or indefinite confidentiality",
        "term_and_survival",
        "Open-ended terms ('in perpetuity', 'indefinitely') create lifetime obligations courts often refuse to enforce.",
    ),
    (
        "unusually long term (10+ years)",
        "term_and_survival",
        "Most US NDAs run 2-5 years; 10+ year terms are aggressive and often unenforceable for non-trade-secret information.",
    ),
    (
        "survival clauses extending obligations past termination",
        "term_and_survival",
        "Obligations that survive termination can outlive the underlying deal by decades.",
    ),

    # return_or_destruction
    (
        "missing return-or-destruction obligation",
        "return_or_destruction",
        "Without a return clause, the recipient has no defined endpoint for holding confidential material.",
    ),
    (
        "certification of destruction requirement",
        "return_or_destruction",
        "Required written certification creates administrative burden and exposure if records are imperfect.",
    ),
    (
        "no backup / archival carve-out for destruction",
        "return_or_destruction",
        "Strict destruction without an archival carve-out can conflict with records-retention obligations under SOX, GDPR, etc.",
    ),

    # compelled_disclosure
    (
        "missing compelled-disclosure carve-out",
        "compelled_disclosure",
        "Without a subpoena/court-order carve-out, complying with a legal demand can technically breach the NDA.",
    ),
    (
        "burdensome notice requirements before compelled disclosure",
        "compelled_disclosure",
        "Short or impractical notice windows for legal demands shift cost and risk to the recipient.",
    ),
    (
        "obligation to resist or contest legal process at recipient's expense",
        "compelled_disclosure",
        "Forcing the recipient to fight subpoenas on their own dime is a hidden cost few people notice when signing.",
    ),

    # injunctive_relief
    (
        "automatic injunctive relief / waiver of bond",
        "injunctive_relief",
        "Pre-agreed injunctions and bond waivers let the discloser shut down the recipient quickly with minimal threshold.",
    ),
    (
        "acknowledgment of irreparable harm",
        "injunctive_relief",
        "Stipulating irreparable harm in advance strips the recipient of a key defense against injunctions.",
    ),
    (
        "fee-shifting for enforcement actions",
        "injunctive_relief",
        "One-way attorneys' fees provisions tilt the cost of any dispute toward the recipient.",
    ),

    # use_restrictions
    (
        "overbroad use restrictions",
        "use_restrictions",
        "Restrictions that go beyond the stated purpose effectively bar the recipient from related work.",
    ),
    (
        "residual knowledge clause (present or absent)",
        "use_restrictions",
        "Residuals clauses determine whether information retained 'in unaided memory' is still restricted — major risk variation.",
    ),
    (
        "no-reverse-engineering clause",
        "use_restrictions",
        "Reverse-engineering restrictions can outlast the agreement and conflict with default rights under state law.",
    ),

    # governing_law
    (
        "inconvenient forum / jurisdiction trap",
        "governing_law",
        "Delaware, New York, or out-of-state forum selection raises the cost of any dispute for the recipient.",
    ),
    (
        "choice-of-law mismatched with the parties' actual location",
        "governing_law",
        "Foreign or out-of-state law can be deliberately chosen to favor the discloser.",
    ),
    (
        "mandatory arbitration with class-action waiver",
        "governing_law",
        "Removes access to courts and class remedies; affects employment NDAs especially.",
    ),
    (
        "exclusive vs. non-exclusive forum",
        "governing_law",
        "Exclusive forum clauses cut off the recipient's home-court advantage entirely.",
    ),

    # assignment
    (
        "free assignment by one party only",
        "assignment",
        "One-sided assignment lets the discloser transfer the agreement (and your obligations) to a competitor or acquirer.",
    ),
    (
        "successors-and-assigns clause without consent",
        "assignment",
        "Binds you to whoever buys the discloser's business, often without notice.",
    ),
    (
        "no anti-assignment protection",
        "assignment",
        "Without a consent requirement, the agreement can be sold or merged into hostile hands.",
    ),

    # non_solicit_or_non_compete
    (
        "non-compete bundled into an NDA",
        "non_solicit_or_non_compete",
        "Non-competes hidden in NDAs evade scrutiny; enforceability varies sharply by state (void in CA, restricted in CO, WA, MA).",
    ),
    (
        "employee non-solicitation",
        "non_solicit_or_non_compete",
        "Employee non-solicits can effectively prevent post-deal hiring and have been challenged on antitrust grounds.",
    ),
    (
        "customer non-solicitation",
        "non_solicit_or_non_compete",
        "Customer non-solicits can shut down legitimate post-deal business development.",
    ),
    (
        "garden leave or paid-notice provisions",
        "non_solicit_or_non_compete",
        "Garden leave sidelines the employee on salary; can be a hidden non-compete in jurisdictions that ban explicit ones.",
    ),
    (
        "non-circumvention clause",
        "non_solicit_or_non_compete",
        "Non-circumvention provisions can prevent dealing with any party introduced through the disclosure — extremely broad.",
    ),
]


def as_grouped_prose() -> str:
    """Render patterns grouped by scored category, for docstrings.

    Output shape: "category one: pattern A; pattern B. category two: pattern C..."
    Compact enough for a docstring, structured enough for a model to parse.
    """
    by_category: dict[str, list[str]] = {}
    for pattern, category, _why in CLAUSE_PATTERNS:
        by_category.setdefault(category, []).append(pattern)
    lines = []
    # Preserve the order from SCORED_CATEGORIES for stability
    for category in SCORED_CATEGORIES:
        patterns = by_category.get(category, [])
        if not patterns:
            continue
        readable = category.replace("_", " ")
        lines.append(f"{readable}: {'; '.join(patterns)}")
    return ". ".join(lines)


def patterns_for_category(category: str) -> list[tuple[str, str]]:
    """Return (pattern, why_it_matters) tuples for a given scored category."""
    return [(p, why) for p, c, why in CLAUSE_PATTERNS if c == category]


def validate() -> list[str]:
    """Return a list of integrity errors. Empty list = file is consistent.

    Used by tests to ensure every pattern maps to a category the pipeline
    actually scores. Run via:
        python -m mcp_server.metadata.clause_patterns
    """
    errors: list[str] = []
    valid = set(SCORED_CATEGORIES)
    for pattern, category, _why in CLAUSE_PATTERNS:
        if category not in valid:
            errors.append(
                f"Pattern '{pattern}' maps to unknown category '{category}'. "
                f"Valid categories: {sorted(valid)}"
            )
    return errors


if __name__ == "__main__":
    import sys
    problems = validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {len(CLAUSE_PATTERNS)} patterns, all mapped to valid scored categories.")
