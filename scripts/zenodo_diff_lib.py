import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyzer_lib import normalize_title


def zenodo_record_to_entry(record: dict) -> dict | None:
    """Extract {title, doi, year, description, html_url, resource_type, authors} from a Zenodo record dict.

    Returns None if metadata is missing.
    """
    metadata = record.get("metadata")
    if not metadata:
        return None

    title = metadata.get("title") or ""

    # Year from ISO publication_date (e.g. "2023-05-15" → "2023")
    pub_date = metadata.get("publication_date")
    year = pub_date.split("-")[0] if pub_date else None

    doi = record.get("doi") or None

    description = metadata.get("description") or None

    html_url = (record.get("links") or {}).get("html") or None

    resource_type_obj = metadata.get("resource_type") or {}
    resource_type = resource_type_obj.get("title") or resource_type_obj.get("type") or None

    creators = metadata.get("creators") or []
    authors = [c["name"] for c in creators if isinstance(c, dict) and c.get("name")]

    return {
        "title": title,
        "doi": doi,
        "year": year,
        "description": description,
        "html_url": html_url,
        "resource_type": resource_type,
        "authors": authors,
    }


def compute_diff(zenodo_entries, profile_titles, profile_dois):
    """Bucket entries against profile.yaml's Data & Software section.

    Returns (matched, new, fuzzy):
      - matched: title found in profile AND (no DOI OR DOI matches)
      - fuzzy:   DOI matches but title differs
      - new:     neither title nor DOI in profile
    """
    profile_norm_titles = {normalize_title(t) for _, t in profile_titles}
    matched, new, fuzzy = [], [], []

    for entry in zenodo_entries:
        title_in_profile = normalize_title(entry["title"]) in profile_norm_titles
        doi_in_profile = bool(entry["doi"]) and entry["doi"] in profile_dois

        if doi_in_profile and not title_in_profile:
            fuzzy.append(entry)
        elif title_in_profile or doi_in_profile:
            matched.append(entry)
        else:
            new.append(entry)

    return matched, new, fuzzy
