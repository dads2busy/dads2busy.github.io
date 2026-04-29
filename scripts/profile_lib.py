import re


def _split_url_or_local(website: str | None) -> tuple[str | None, str | None]:
    """Return (http_url, local_path). Exactly one is non-None when website truthy.

    URL fragments (#...) are stripped from http(s) URLs because Typst interprets
    '#' as a code marker inside link text, causing TypstError at PDF compile time.
    """
    if not website:
        return None, None
    if website.startswith(("http://", "https://")):
        # Strip any URL fragment — Typst treats # as code and chokes on it.
        url = website.split("#")[0]
        return url, None
    return None, website


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
    else:
        url, local = _split_url_or_local(entry.get("website"))
        if url:
            out["url"] = url
        if local:
            out["local_path"] = local

    # Custom keys preserved verbatim — only when populated.
    for key in ("slug", "subcategory", "abstract"):
        val = entry.get(key)
        if val:
            out[key] = val
    for key in ("editors", "pages", "ordinal"):
        val = entry.get(key)
        if val not in (None, "", 0):
            out[key] = str(val) if isinstance(val, int) else val

    return out


def _passthrough_custom(entry: dict, out: dict, keys: tuple[str, ...]) -> None:
    """Copy non-empty custom keys from entry into out.

    Integer values are coerced to strings so RenderCV's template engine
    (which calls re.sub on all entry fields) never receives a bare int.
    """
    for key in keys:
        val = entry.get(key)
        if val not in (None, "", 0, False):
            out[key] = str(val) if isinstance(val, int) else val


def working_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("dates"):
        out["date"] = entry["dates"]
    if entry.get("subtitle"):
        out["summary"] = entry["subtitle"]
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    _passthrough_custom(entry, out, ("slug", "subcategory", "ordinal"))
    return out


def research_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("dates"):
        out["date"] = str(entry["dates"])

    summary = entry.get("sponsor") or ""
    if entry.get("award"):
        summary = f"{summary} — {entry['award']}" if summary else entry["award"]
    if entry.get("role"):
        summary = f"{summary} ({entry['role']})" if summary else f"({entry['role']})"
    if summary:
        out["summary"] = summary

    url, local = _split_url_or_local(entry.get("website"))
    if url:
        out["url"] = url
    if local:
        out["local_path"] = local
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]

    _passthrough_custom(
        entry, out,
        (
            "slug", "subcategory", "ordinal",
            "report", "report2", "report3", "report4", "report5", "report6",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def speaking_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("date"):
        out["date"] = entry["date"]

    summary_parts = []
    if entry.get("role"):
        summary_parts.append(entry["role"])
    if entry.get("sponsor"):
        if summary_parts:
            summary_parts[0] = f"{summary_parts[0]} at {entry['sponsor']}"
        else:
            summary_parts.append(entry["sponsor"])
    if summary_parts:
        out["summary"] = summary_parts[0]

    url, local = _split_url_or_local(entry.get("website"))
    if url:
        out["url"] = url
    if local:
        out["local_path"] = local
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]

    _passthrough_custom(
        entry, out,
        (
            "slug", "subcategory",
            "report",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def teaching_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    url, local = _split_url_or_local(entry.get("website"))
    if url:
        out["url"] = url
    if local:
        out["local_path"] = local
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    _passthrough_custom(entry, out, ("slug",))
    return out
