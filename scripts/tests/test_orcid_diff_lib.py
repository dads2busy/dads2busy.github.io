import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orcid_diff_lib import orcid_group_to_entry, compute_diff


SAMPLE_GROUP = {
    "external-ids": {
        "external-id": [
            {"external-id-type": "doi", "external-id-value": "10.18130/foo"},
        ],
    },
    "work-summary": [
        {
            "title": {"title": {"value": "Sample Paper Title"}},
            "type": "journal-article",
            "publication-date": {"year": {"value": "2023"}},
            "journal-title": {"value": "Some Journal"},
        },
    ],
}


def test_orcid_group_extracts_basic_fields():
    out = orcid_group_to_entry(SAMPLE_GROUP)
    assert out["title"] == "Sample Paper Title"
    assert out["doi"] == "10.18130/foo"
    assert out["year"] == "2023"
    assert out["journal"] == "Some Journal"
    assert out["type"] == "journal-article"


def test_orcid_group_handles_missing_doi():
    group = dict(SAMPLE_GROUP, **{"external-ids": {"external-id": []}})
    out = orcid_group_to_entry(group)
    assert out["doi"] is None


def test_orcid_group_handles_missing_journal():
    group_summary = {**SAMPLE_GROUP["work-summary"][0]}
    group_summary.pop("journal-title")
    group = {**SAMPLE_GROUP, "work-summary": [group_summary]}
    out = orcid_group_to_entry(group)
    assert out["journal"] is None


def test_orcid_group_handles_missing_pubdate():
    group_summary = {**SAMPLE_GROUP["work-summary"][0]}
    group_summary.pop("publication-date")
    group = {**SAMPLE_GROUP, "work-summary": [group_summary]}
    out = orcid_group_to_entry(group)
    assert out["year"] is None


def test_orcid_group_returns_none_when_empty_summary():
    group = {**SAMPLE_GROUP, "work-summary": []}
    assert orcid_group_to_entry(group) is None


def test_compute_diff_title_match():
    orcid = [{"title": "Sample Paper Title", "doi": "10.x/new", "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Sample Paper Title")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
    assert len(fuzzy) == 0


def test_compute_diff_doi_match():
    orcid = [{"title": "ORCID Title v2", "doi": "10.x/abc", "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Old Title v1")}
    profile_dois = {"10.x/abc"}
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 0
    assert len(fuzzy) == 1
    assert fuzzy[0]["title"] == "ORCID Title v2"


def test_compute_diff_new_entry():
    orcid = [{"title": "Brand New Paper", "doi": "10.x/new", "year": "2024", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Other Paper")}
    profile_dois = {"10.x/old"}
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 0
    assert len(new) == 1
    assert len(fuzzy) == 0
    assert new[0]["title"] == "Brand New Paper"


def test_compute_diff_title_match_normalizes():
    orcid = [{"title": "Sample paper title.", "doi": None, "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Sample Paper Title")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
