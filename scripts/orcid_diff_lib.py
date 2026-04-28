import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyzer_lib import normalize_title


def orcid_group_to_entry(group: dict) -> dict | None:
    """Extract {title, doi, year, journal, type} from one ORCID work-group dict.

    Returns None if the group has no work-summary.
    """
    summaries = group.get("work-summary", [])
    if not summaries:
        return None

    work = summaries[0]
    title_obj = work.get("title") or {}
    title = (title_obj.get("title") or {}).get("value") or ""

    pub_date = work.get("publication-date") or {}
    year_obj = (pub_date.get("year") or {}) if pub_date else {}
    year = year_obj.get("value") if year_obj else None

    journal_obj = work.get("journal-title")
    journal = journal_obj.get("value") if journal_obj else None

    ext_ids = (group.get("external-ids") or {}).get("external-id") or []
    doi = next(
        (eid["external-id-value"] for eid in ext_ids if eid.get("external-id-type") == "doi"),
        None,
    )

    return {
        "title": title,
        "doi": doi,
        "year": year,
        "journal": journal,
        "type": work.get("type", "unknown"),
    }


def compute_diff(orcid_entries, profile_titles, profile_dois):
    """Bucket ORCID entries against the SSOT.

    Returns (matched, new, fuzzy):
      - matched: title found in profile.yaml AND (no DOI OR DOI matches)
      - fuzzy:   DOI matches but title differs — stale metadata to flag
      - new:     neither title nor DOI in profile.yaml
    """
    profile_norm_titles = {normalize_title(t) for _, t in profile_titles}
    matched, new, fuzzy = [], [], []
    for entry in orcid_entries:
        title_in_profile = normalize_title(entry["title"]) in profile_norm_titles
        doi_in_profile = bool(entry["doi"]) and entry["doi"] in profile_dois

        if doi_in_profile and not title_in_profile:
            fuzzy.append(entry)
        elif title_in_profile or doi_in_profile:
            matched.append(entry)
        else:
            new.append(entry)
    return matched, new, fuzzy
