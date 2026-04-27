import re

_SMART_QUOTES = str.maketrans({
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
    "—": "-", "–": "-",
})


def normalize_title(s: str) -> str:
    """Canonical form of a publication/entry title for cross-source matching."""
    if not s:
        return ""
    s = s.translate(_SMART_QUOTES)
    s = s.strip().strip('"').strip("'").strip()
    s = s.rstrip(".")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def extract_profile_titles(profile: dict) -> list[tuple[str, str]]:
    """Walk profile.yaml's cv.sections; return (section_name, entry_title) tuples.

    Pulls a title from each entry using these field-name preferences:
    publication_entry → 'title', normal_entry → 'name', education → 'institution',
    OneLineEntry → 'label'. Bare-string sections (Summary, Skills) are skipped.
    """
    out: list[tuple[str, str]] = []
    sections = profile.get("cv", {}).get("sections", {})
    for section_name, entries in sections.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            title = (
                entry.get("title")
                or entry.get("name")
                or entry.get("institution")
                or entry.get("label")
            )
            if title:
                out.append((section_name, title))
    return out


import mammoth
from pathlib import Path


def docx_to_markdown(path: Path) -> str:
    """Convert a DOCX file to markdown text via mammoth."""
    if not path.exists():
        raise FileNotFoundError(f"DOCX not found: {path}")
    with open(path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value
