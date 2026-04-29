import re

CATEGORIES = (
    "Panelist", "Presentation", "Committee", "Lecture",
    "Expert Forum", "Expert Webinar", "Workshop",
)

# Title: <Category>: <captured>  where captured is either:
#   1. text in straight or smart double quotes
#   2. bare text up to the next period
_TITLE_PATTERNS = [
    # Quoted (straight or smart quotes)
    re.compile(
        r"\b(?:" + "|".join(re.escape(c) for c in CATEGORIES) + r")\s*:\s*[\"""]([^\"""]+)[\"""]",
    ),
    # Bare up to period
    re.compile(
        r"\b(?:" + "|".join(re.escape(c) for c in CATEGORIES) + r")\s*:\s*([^.]+?)\.",
    ),
]


def derive_title_from_content(content: str) -> str | None:
    """Extract a candidate title from a category-prefixed citation string.

    Tries quoted form first, then bare-until-period. Returns None if no match.
    """
    if not content:
        return None
    for pat in _TITLE_PATTERNS:
        m = pat.search(content)
        if m:
            return m.group(1).strip()
    return None


def derive_category_from_content(content: str) -> str | None:
    """Return the first category keyword that appears as `<cat>:` in the content."""
    if not content:
        return None
    for cat in CATEGORIES:
        if re.search(rf"\b{re.escape(cat)}\s*:", content):
            return cat
    return None
