import re


def normalize_title(s: str) -> str:
    """Canonical form of a publication/entry title for cross-source matching."""
    if not s:
        return ""
    # Strip leading/trailing whitespace first
    s = s.strip()
    # Replace smart quotes and dashes (U+201C, U+201D, U+2018, U+2019, U+2014, U+2013)
    s = s.replace(""", '"').replace(""", '"')
    s = s.replace("'", "'").replace("'", "'")
    s = s.replace("—", "-").replace("–", "-")
    # Strip quotes and whitespace again
    s = s.strip().strip('"').strip("'").strip()
    # Remove trailing period
    s = s.rstrip(".")
    # Collapse multiple whitespace to single space
    s = re.sub(r"\s+", " ", s)
    # Lowercase
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
