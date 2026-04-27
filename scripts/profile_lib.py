import re


def split_authors(s: str) -> list[str]:
    """Split an author string into a list of individual author names.

    Handles three patterns:
      1. 'Last F, Last F'                               (comma-only)
      2. 'Last, First, Last, First, and Last, First'    (pairs + 'and')
      3. 'Last, F. and Last, F. and Last, F.'           ('and'-separated pairs)
    """
    if not s or not s.strip():
        return []

    s = s.strip()

    # Patterns 2 and 3: ' and ' or ' & ' disambiguates Last/First pairing.
    if re.search(r"\s+(?:and|&)\s+", s):
        pieces = re.split(r",?\s+(?:and|&)\s+", s)
        result: list[str] = []

        for piece in pieces:
            piece = piece.strip().rstrip(",").strip()
            if not piece:
                continue
            commas = piece.count(",")
            if commas <= 1:
                # Either 'Last F' (0 commas) or 'Last, First' (1 comma).
                result.append(piece)
            else:
                # Pairs of 'Last, First, Last, First, ...'
                parts = [p.strip() for p in piece.split(",") if p.strip()]
                for i in range(0, len(parts), 2):
                    if i + 1 < len(parts):
                        result.append(f"{parts[i]}, {parts[i+1]}")
                    else:
                        result.append(parts[i])

        return result
    else:
        # No ' and ': could be Pattern 1 (comma-separated singles) or Pattern 2 without final ' and '
        parts = [p.strip() for p in s.split(",") if p.strip()]

        if len(parts) == 1:
            # Single author, e.g. "Schroeder, A.D."
            return parts

        # Check if this is Pattern 1: every part matches "Surname Initial(s)" like "Lancaster V" or "Shipp S"
        # Pattern 1 parts have exactly 2 tokens (surname and initial), no commas
        looks_like_pattern1 = all(
            len(p.split()) == 2 and len(p.split()[1]) <= 2
            for p in parts
        )

        if looks_like_pattern1:
            # Pattern 1: all parts are "Surname Initial", return as-is
            return parts
        else:
            # Pattern 2/3 without ' and ': pair consecutive parts as (Last, First)
            result: list[str] = []
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    result.append(f"{parts[i]}, {parts[i+1]}")
                else:
                    result.append(parts[i])
            return result


_AARON_PATTERN = re.compile(
    r"""
    ^\s*
    (?:
        Schroeder,?\s*
            (?: Aaron (?:\s+D\.?)?
              | A\.?\s*D?\.?
            )?
        |
        (?: Aaron (?:\s+D\.?)?
          | A\.?\s*D?\.?
        )
        \s+ Schroeder
    )
    \.?\s*$
    """,
    re.VERBOSE,
)


def bold_aaron(name: str) -> str:
    """Wrap Aaron Schroeder name variants with **bold**. Pass-through otherwise."""
    if name.startswith("**") and name.endswith("**"):
        return name
    if _AARON_PATTERN.match(name.strip()):
        return f"**{name.strip()}**"
    return name


def normalize_doi(s: str | None) -> str | None:
    """Strip URL/label prefixes from a DOI; return None if not a valid bare DOI."""
    if not s or not s.strip():
        return None
    s = s.strip()
    s = re.sub(r"^DOI:\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi\.org/", "", s)
    return s if s.startswith("10.") else None


def writing_entry_to_publication(entry: dict) -> dict:
    """Convert one writing.json entry to a RenderCV publication_entry dict.

    Preserves custom keys (slug, ordinal, subcategory, content) for the
    site's content-JSON generator; RenderCV ignores them in default rendering.
    """
    out: dict = {
        "title": entry["title"],
        "authors": [bold_aaron(a) for a in split_authors(entry.get("authors", ""))],
    }

    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("sponsor"):
        out["journal"] = entry["sponsor"]

    doi = normalize_doi(entry.get("DOI"))
    if doi:
        out["doi"] = doi
    elif entry.get("website"):
        out["url"] = entry["website"]

    # Custom keys preserved verbatim — only when populated.
    for key in ("slug", "subcategory", "content"):
        val = entry.get(key)
        if val:
            out[key] = val
    for key in ("editors", "pages", "ordinal"):
        val = entry.get(key)
        if val not in (None, "", 0):
            out[key] = val

    return out
