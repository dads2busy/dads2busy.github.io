def _strip_bold(s: str) -> str:
    """Remove markdown bold markers from an author name."""
    if s.startswith("**") and s.endswith("**"):
        return s[2:-2]
    return s


def _coerce_ordinal(val):
    """profile.yaml stores ordinal as a string (or empty); website expects int (or absent)."""
    if val in (None, ""):
        return ""
    try:
        return int(val)
    except (ValueError, TypeError):
        return val


def _website_field(entry: dict) -> str:
    """Recover the original website field from Plan A's url/local_path split."""
    return entry.get("url") or entry.get("local_path") or ""


def _doi_with_prefix(entry: dict) -> str:
    """profile.yaml stores bare DOI; the original writing.json had full URLs."""
    doi = entry.get("doi", "")
    if not doi:
        return ""
    if doi.startswith("http"):
        return doi
    return f"https://doi.org/{doi}"


def _passthrough(entry: dict, out: dict, keys: tuple) -> None:
    """Copy keys from entry to out only when present and non-None."""
    for k in keys:
        if k in entry and entry[k] is not None:
            out[k] = entry[k]


def publication_entry_to_writing(entry: dict) -> dict:
    out: dict = {
        "title": entry["title"],
        "authors": ", ".join(_strip_bold(a) for a in entry.get("authors", [])),
    }
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("journal"):
        out["journal"] = entry["journal"]
    doi = _doi_with_prefix(entry)
    if doi:
        out["DOI"] = doi
    website = _website_field(entry)
    if website:
        out["website"] = website
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(entry, out, ("slug", "subcategory", "abstract", "editors", "pages"))
    return out


def experience_entry_to_working(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["dates"] = entry["date"]
    if entry.get("summary"):
        out["subtitle"] = entry["summary"]
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(entry, out, ("slug", "subcategory"))
    return out


def project_entry_to_research(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["dates"] = entry["date"]
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    if entry.get("url"):
        out["website"] = entry["url"]
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(
        entry, out,
        (
            "slug", "subcategory",
            "funder", "award", "role",
            "report", "report2", "report3", "report4", "report5", "report6",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def presentation_entry_to_speaking(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    if entry.get("url"):
        out["website"] = entry["url"]
    _passthrough(
        entry, out,
        (
            "slug", "subcategory",
            "event", "role",
            "report",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def teaching_entry_to_teaching(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("abstract"):
        out["abstract"] = entry["abstract"]
    if entry.get("url"):
        out["website"] = entry["url"]
    _passthrough(entry, out, ("slug",))
    return out
