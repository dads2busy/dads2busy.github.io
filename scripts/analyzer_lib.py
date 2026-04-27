import re


def normalize_title(s: str) -> str:
    """Canonical form of a publication/entry title for cross-source matching."""
    if not s:
        return ""
    # Strip leading/trailing whitespace first
    s = s.strip()
    # Replace smart quotes and dashes (U+201C, U+201D, U+2018, U+2019, U+2014, U+2013)
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("—", "-").replace("–", "-")
    # Strip quotes and whitespace again
    s = s.strip().strip('"').strip("'").strip()
    # Remove trailing period
    s = s.rstrip(".")
    # Collapse multiple whitespace to single space
    s = re.sub(r"\s+", " ", s)
    # Lowercase
    return s.lower()
