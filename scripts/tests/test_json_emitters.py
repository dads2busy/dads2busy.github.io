import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from json_emitters import (
    publication_entry_to_writing,
    experience_entry_to_working,
    project_entry_to_research,
    presentation_entry_to_speaking,
    teaching_entry_to_teaching,
    release_entry_to_releases,
)


def test_publication_basic():
    entry = {
        "title": "Census Curated Data Enterprise",
        "authors": ["Lancaster V", "Shipp S", "**Schroeder A**", "Mortveit H"],
        "date": "2023-01-01",
        "doi": "10.18130/ce97-sp05",
        "journal": "Proceedings of the Biocomplexity Institute",
        "slug": "census_curated_data_enterprise",
        "subcategory": "Research/Technical Reports",
        "ordinal": "0",
        "abstract": "Abstract...",
    }
    out = publication_entry_to_writing(entry)
    assert out["title"] == "Census Curated Data Enterprise"
    assert out["authors"] == "Lancaster V, Shipp S, Schroeder A, Mortveit H"
    assert out["date"] == "2023-01-01"
    assert out["DOI"] == "https://doi.org/10.18130/ce97-sp05"
    assert out["journal"] == "Proceedings of the Biocomplexity Institute"
    assert out["slug"] == "census_curated_data_enterprise"
    assert out["subcategory"] == "Research/Technical Reports"
    assert out["ordinal"] == 0
    assert out["abstract"] == "Abstract..."


def test_publication_local_path_to_website():
    entry = {
        "title": "Old paper",
        "authors": ["Schroeder A"],
        "local_path": "/downloads/foo.pdf",
    }
    out = publication_entry_to_writing(entry)
    assert out["website"] == "/downloads/foo.pdf"


def test_publication_url_to_website():
    entry = {
        "title": "Modern paper",
        "authors": ["Schroeder A"],
        "url": "https://example.com/paper.pdf",
    }
    out = publication_entry_to_writing(entry)
    assert out["website"] == "https://example.com/paper.pdf"


def test_publication_doi_unchanged_if_already_url():
    entry = {
        "title": "Paper",
        "authors": ["Schroeder A"],
        "doi": "https://doi.org/10.1234/abc",
    }
    out = publication_entry_to_writing(entry)
    assert out["DOI"] == "https://doi.org/10.1234/abc"


def test_publication_omits_doi_field_when_absent():
    entry = {"title": "Paper", "authors": ["Schroeder A"]}
    out = publication_entry_to_writing(entry)
    assert "DOI" not in out or out["DOI"] == ""


def test_experience_basic():
    entry = {
        "name": "Associate Research Professor",
        "date": "2018-Present",
        "summary": "Research Associate Professor at SDAL",
        "slug": "associate-research-professor",
        "ordinal": "1",
        "abstract": "Description...",
    }
    out = experience_entry_to_working(entry)
    assert out["title"] == "Associate Research Professor"
    assert out["dates"] == "2018-Present"
    assert out["subtitle"] == "Research Associate Professor at SDAL"
    assert out["slug"] == "associate-research-professor"
    assert out["ordinal"] == 1
    assert out["abstract"] == "Description..."


def test_research_project_basic():
    entry = {
        "name": "ATIS Implementation Center",
        "date": "2004-2005",
        "summary": "U.S. DOT — $543,000 (Co-PI)",
        "slug": "atis_rce",
        "subcategory": "Data Integration & Management",
        "ordinal": "9",
    }
    out = project_entry_to_research(entry)
    assert out["title"] == "ATIS Implementation Center"
    assert out["dates"] == "2004-2005"
    assert out["slug"] == "atis_rce"
    assert out["subcategory"] == "Data Integration & Management"
    assert out["ordinal"] == 9


def test_research_project_preserves_award_field():
    entry = {
        "name": "VDH Data Commons",
        "date": "2021-2024",
        "award": "$1,150,000",
        "summary": "Phase 1 & 2",
    }
    out = project_entry_to_research(entry)
    assert out["award"] == "$1,150,000"


def test_presentation_basic():
    entry = {
        "name": "The Social Impact Data Commons",
        "date": "2023-12-02",
        "summary": "Lecture at COPAFS",
        "slug": "COPAFS",
        "subcategory": "Lecture",
    }
    out = presentation_entry_to_speaking(entry)
    assert out["title"] == "The Social Impact Data Commons"
    assert out["date"] == "2023-12-02"
    assert out["slug"] == "COPAFS"
    assert out["subcategory"] == "Lecture"


def test_teaching_basic():
    entry = {
        "name": "Administrative Data Systems & Technologies",
        "date": "2013-05-22",
        "slug": "data-systems",
    }
    out = teaching_entry_to_teaching(entry)
    assert out["title"] == "Administrative Data Systems & Technologies"
    assert out["date"] == "2013-05-22"
    assert out["slug"] == "data-systems"


def test_publication_strips_aaron_bold_in_authors_string():
    entry = {
        "title": "Paper",
        "authors": ["**Schroeder, A.D.**", "**Aaron Schroeder**", "Other, P."],
    }
    out = publication_entry_to_writing(entry)
    assert "**" not in out["authors"]
    assert out["authors"] == "Schroeder, A.D., Aaron Schroeder, Other, P."


def test_publication_ordinal_empty_string_omits_field():
    entry = {"title": "Paper", "authors": ["X"], "ordinal": ""}
    out = publication_entry_to_writing(entry)
    assert "ordinal" not in out or out["ordinal"] == ""


# ─── Shape-completeness tests ────────────────────────────────────────
# These tests pin the output key-set for each emitter. A renamed key
# causes a test failure here, catching regressions before the website breaks.

def test_publication_writing_shape_complete():
    """publication_entry_to_writing on a fully-populated entry must produce
    exactly these keys (the writing.json shape the website's content.ts expects)."""
    entry = {
        "title": "X", "authors": ["A", "B"], "date": "2023-01-01",
        "doi": "10.x/y", "journal": "J", "url": "http://example.com",
        "slug": "s", "subcategory": "Refereed Journal Articles",
        "abstract": "abstract", "editors": "ed", "pages": "1-10", "ordinal": "5",
    }
    out = publication_entry_to_writing(entry)
    expected = {
        "title", "authors", "date", "DOI", "journal", "website",
        "ordinal", "slug", "subcategory", "abstract", "editors", "pages",
    }
    assert set(out.keys()) == expected, (
        f"publication_entry_to_writing key drift: missing={expected - set(out)} extra={set(out) - expected}"
    )


def test_experience_working_shape_complete():
    entry = {
        "name": "X", "date": "2018-Present", "summary": "Role at Org",
        "abstract": "Description", "slug": "s", "subcategory": "current",
        "ordinal": "1",
    }
    out = experience_entry_to_working(entry)
    expected = {"title", "dates", "subtitle", "abstract", "ordinal", "slug", "subcategory"}
    assert set(out.keys()) == expected


def test_research_research_shape_complete():
    entry = {
        "name": "X", "date": "2020", "url": "http://x.com", "abstract": "abstract",
        "slug": "s", "subcategory": "Some Sub", "funder": "Funder X",
        "award": "$1000", "role": "PI", "ordinal": "3",
    }
    out = project_entry_to_research(entry)
    expected = {
        "title", "dates", "website", "abstract", "ordinal", "slug",
        "subcategory", "funder", "award", "role",
    }
    assert set(out.keys()) == expected


def test_presentation_speaking_shape_complete():
    entry = {
        "name": "X", "date": "2023-12-02", "abstract": "Speech text",
        "url": "http://x.com", "slug": "s", "subcategory": "Lecture",
        "event": "Venue", "role": "speaker",
    }
    out = presentation_entry_to_speaking(entry)
    expected = {
        "title", "date", "abstract", "website", "slug", "subcategory",
        "event", "role",
    }
    assert set(out.keys()) == expected, (
        f"presentation_entry_to_speaking key drift: missing={expected - set(out)} extra={set(out) - expected}"
    )


def test_teaching_teaching_shape_complete():
    entry = {
        "name": "X", "date": "2013-05-22", "url": "http://x.com",
        "abstract": "syllabus", "slug": "s",
    }
    out = teaching_entry_to_teaching(entry)
    expected = {"title", "date", "website", "abstract", "slug"}
    assert set(out.keys()) == expected


def test_release_releases_shape_complete():
    entry = {
        "name": "X", "date": "2026-01-01",
        "summary": "Brief description",
        "abstract": "Long abstract",
        "url": "https://github.com/example/repo",
        "doi": "10.x/y",
        "authors": ["Schroeder, A."],
        "slug": "s", "subcategory": "Software",
        "type": "Software",
        "ordinal": "1",
    }
    out = release_entry_to_releases(entry)
    expected = {
        "title", "date", "summary", "abstract", "url", "doi",
        "authors", "ordinal", "slug", "subcategory", "type",
    }
    assert set(out.keys()) == expected


