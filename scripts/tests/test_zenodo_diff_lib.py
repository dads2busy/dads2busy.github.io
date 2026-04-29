import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zenodo_diff_lib import zenodo_record_to_entry, compute_diff


SAMPLE_RECORD = {
    "id": 1234567,
    "doi": "10.5281/zenodo.1234567",
    "metadata": {
        "title": "My Awesome Dataset",
        "publication_date": "2023-05-15",
        "description": "<p>A dataset about things.</p>",
        "creators": [
            {"name": "Schroeder, Aaron"},
            {"name": "Doe, Jane"},
        ],
        "resource_type": {"type": "dataset", "title": "Dataset"},
        "keywords": ["data", "research"],
        "license": {"id": "cc-by-4.0"},
    },
    "links": {"html": "https://zenodo.org/records/1234567"},
}


def test_zenodo_record_extracts_basic_fields():
    out = zenodo_record_to_entry(SAMPLE_RECORD)
    assert out is not None
    assert out["title"] == "My Awesome Dataset"
    assert out["doi"] == "10.5281/zenodo.1234567"
    assert out["year"] == "2023"
    assert out["html_url"] == "https://zenodo.org/records/1234567"
    assert out["resource_type"] == "Dataset"
    assert out["description"] == "<p>A dataset about things.</p>"
    assert out["authors"] == ["Schroeder, Aaron", "Doe, Jane"]


def test_zenodo_record_handles_missing_description():
    record = {
        **SAMPLE_RECORD,
        "metadata": {**SAMPLE_RECORD["metadata"]},
    }
    del record["metadata"]["description"]
    out = zenodo_record_to_entry(record)
    assert out is not None
    assert out["description"] is None


def test_zenodo_record_handles_missing_publication_date():
    record = {
        **SAMPLE_RECORD,
        "metadata": {**SAMPLE_RECORD["metadata"]},
    }
    del record["metadata"]["publication_date"]
    out = zenodo_record_to_entry(record)
    assert out is not None
    assert out["year"] is None


def test_zenodo_record_handles_missing_doi():
    record = {k: v for k, v in SAMPLE_RECORD.items() if k != "doi"}
    out = zenodo_record_to_entry(record)
    assert out is not None
    assert out["doi"] is None


def test_zenodo_record_returns_none_for_missing_metadata():
    record = {"id": 9999, "links": {"html": "https://zenodo.org/records/9999"}}
    assert zenodo_record_to_entry(record) is None


def test_zenodo_record_handles_missing_creators():
    record = {
        **SAMPLE_RECORD,
        "metadata": {**SAMPLE_RECORD["metadata"]},
    }
    del record["metadata"]["creators"]
    out = zenodo_record_to_entry(record)
    assert out is not None
    assert out["authors"] == []


def test_compute_diff_title_match():
    entries = [{"title": "My Awesome Dataset", "doi": "10.5281/zenodo.1234567",
                "year": "2023", "description": None, "html_url": None,
                "resource_type": "Dataset", "authors": []}]
    profile_titles = {("Datasets", "My Awesome Dataset")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(entries, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
    assert len(fuzzy) == 0


def test_compute_diff_doi_match_fuzzy():
    entries = [{"title": "New Title for Known Dataset", "doi": "10.5281/zenodo.1234567",
                "year": "2023", "description": None, "html_url": None,
                "resource_type": "Dataset", "authors": []}]
    profile_titles = {("Datasets", "Old Title for Known Dataset")}
    profile_dois = {"10.5281/zenodo.1234567"}
    matched, new, fuzzy = compute_diff(entries, profile_titles, profile_dois)
    assert len(matched) == 0
    assert len(fuzzy) == 1
    assert fuzzy[0]["title"] == "New Title for Known Dataset"


def test_compute_diff_new_entry():
    entries = [{"title": "Brand New Dataset", "doi": "10.5281/zenodo.9999999",
                "year": "2024", "description": None, "html_url": None,
                "resource_type": "Dataset", "authors": []}]
    profile_titles = {("Datasets", "Other Dataset")}
    profile_dois = {"10.5281/zenodo.111"}
    matched, new, fuzzy = compute_diff(entries, profile_titles, profile_dois)
    assert len(matched) == 0
    assert len(new) == 1
    assert len(fuzzy) == 0
    assert new[0]["title"] == "Brand New Dataset"


def test_compute_diff_title_match_normalizes():
    entries = [{"title": "my awesome dataset.", "doi": None,
                "year": "2023", "description": None, "html_url": None,
                "resource_type": "Dataset", "authors": []}]
    profile_titles = {("Datasets", "My Awesome Dataset")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(entries, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
    assert len(fuzzy) == 0
