import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from json_emitters import (
    publication_entry_to_writing,
    experience_entry_to_working,
    project_entry_to_research,
    presentation_entry_to_speaking,
    teaching_entry_to_teaching,
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
        "content": "Abstract...",
    }
    out = publication_entry_to_writing(entry)
    assert out["title"] == "Census Curated Data Enterprise"
    assert out["authors"] == "Lancaster V, Shipp S, Schroeder A, Mortveit H"
    assert out["date"] == "2023-01-01"
    assert out["DOI"] == "https://doi.org/10.18130/ce97-sp05"
    assert out["sponsor"] == "Proceedings of the Biocomplexity Institute"
    assert out["slug"] == "census_curated_data_enterprise"
    assert out["subcategory"] == "Research/Technical Reports"
    assert out["ordinal"] == 0
    assert out["content"] == "Abstract..."


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
        "content": "Description...",
    }
    out = experience_entry_to_working(entry)
    assert out["title"] == "Associate Research Professor"
    assert out["dates"] == "2018-Present"
    assert out["subtitle"] == "Research Associate Professor at SDAL"
    assert out["slug"] == "associate-research-professor"
    assert out["ordinal"] == 1
    assert out["content"] == "Description..."


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
        "subcategory": "Presentations/Workshops",
    }
    out = presentation_entry_to_speaking(entry)
    assert out["title"] == "The Social Impact Data Commons"
    assert out["date"] == "2023-12-02"
    assert out["slug"] == "COPAFS"
    # Legacy "Presentations/Workshops" is not a valid category; no content to parse → defaults
    assert out["subcategory"] == "Presentation"


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


def test_presentation_explicit_subcategory_kept_when_valid():
    entry = {"name": "X", "subcategory": "Workshop"}
    out = presentation_entry_to_speaking(entry)
    assert out["subcategory"] == "Workshop"


def test_presentation_subcategory_derived_from_content_keyword():
    entry = {"name": "X", "content": 'Schroeder, A.D. Lecture: "X" (2023), Foo.'}
    out = presentation_entry_to_speaking(entry)
    assert out["subcategory"] == "Lecture"


def test_presentation_defaults_to_presentation_when_no_match():
    entry = {"name": "X", "content": "Some unstructured citation text"}
    out = presentation_entry_to_speaking(entry)
    assert out["subcategory"] == "Presentation"


def test_presentation_legacy_subcategory_falls_through_to_content():
    """The legacy 'Presentations/Workshops' subcategory should NOT be honored."""
    entry = {"name": "X", "subcategory": "Presentations/Workshops",
             "content": 'Schroeder, A.D. Panelist: "X" (2023), Bar.'}
    out = presentation_entry_to_speaking(entry)
    assert out["subcategory"] == "Panelist"


def test_presentation_recognizes_expert_forum_two_word():
    entry = {"name": "X", "content": 'Schroeder, A.D. Expert Forum: "X" (2023), Baz.'}
    out = presentation_entry_to_speaking(entry)
    assert out["subcategory"] == "Expert Forum"
