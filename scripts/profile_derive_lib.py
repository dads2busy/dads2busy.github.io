import re

CATEGORIES = (
    "Panelist", "Presentation", "Committee", "Lecture",
    "Expert Forum", "Expert Webinar", "Workshop",
)

_KEYWORD_TO_CATEGORY = {
    "Panelist": "Panelist",
    "Presentation": "Presentations/Workshops",
    "Committee": "Committee",
    "Lecture": "Lecture",
    "Expert Forum": "Expert Forum",
    "Expert Webinar": "Expert Webinar",
    "Workshop": "Presentations/Workshops",
}

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
    """Map a content-keyword to its canonical category. Returns None if no match.

    The 6 canonical categories: Panelist, Presentations/Workshops, Committee,
    Lecture, Expert Forum, Expert Webinar. Both 'Presentation:' and 'Workshop:'
    in prose map to 'Presentations/Workshops' (the umbrella category).
    """
    if not content:
        return None
    # Order matters: longer keywords first (e.g. 'Expert Forum' before 'Forum'),
    # so we use the dict's keys in their original CATEGORIES order.
    for kw in CATEGORIES:
        if re.search(rf"\b{re.escape(kw)}\s*:", content):
            return _KEYWORD_TO_CATEGORY[kw]
    return None
