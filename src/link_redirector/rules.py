"""The redirect table for the 2025 site restructure.

Fixed redirects map one old page to its new home. Keep the list sorted by
old path so diffs stay readable.
"""

FIXED_REDIRECTS: dict[str, str] = {
    "/about-us": "/company",
    "/blog/archive": "/blog",
    "/contact-us": "/contact",
    "/docs/getting-started": "/docs/quickstart",
    "/old-pricing": "/pricing",
    "/support/faq": "/help",
    "/team": "/company#team",
}

# Section-wide moves: everything under the old prefix keeps its remaining path.
PREFIX_MOVES: list[tuple[str, str]] = [
    ("/legacy/", "/"),
]


def describe(fixed: dict[str, str]) -> list[dict]:
    """Return the rule table as plain dicts, for the /rules endpoint.

    All redirects are permanent (301) so search engines move their index.
    """
    status = 301
    rules = [
        {"kind": "fixed", "from": source, "to": target, "status": status}
        for source, target in sorted(fixed.items())
    ]
    rules.extend(
        {"kind": "prefix", "from": old + "*", "to": new + "*", "status": status}
        for old, new in PREFIX_MOVES
    )
    return rules
