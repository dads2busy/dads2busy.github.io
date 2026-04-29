import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from profile_lib import split_authors


def test_split_pattern1_last_initial_comma():
    """Pattern 1: 'Last F, Last F' — comma-only, no internal commas."""
    s = "Lancaster V, Shipp S, Keller S, Schroeder A, Mortveit H, Swarup S, Xie D"
    assert split_authors(s) == [
        "Lancaster V", "Shipp S", "Keller S", "Schroeder A",
        "Mortveit H", "Swarup S", "Xie D",
    ]


def test_split_pattern2_last_first_pairs_with_and():
    """Pattern 2: 'Last, First, Last, First, and Last, First'."""
    s = "Schroeder, A.D., Wamsley, G.L., and Ward, R."
    assert split_authors(s) == [
        "Schroeder, A.D.", "Wamsley, G.L.", "Ward, R.",
    ]


def test_split_pattern3_and_separated_pairs():
    """Pattern 3: 'Last, F. and Last, F. and Last, F.'"""
    s = "Schroeder, A. and Shipp, S. and Kang, W. and Robinson, P. and Keller, S."
    assert split_authors(s) == [
        "Schroeder, A.", "Shipp, S.", "Kang, W.", "Robinson, P.", "Keller, S.",
    ]


def test_split_single_author():
    assert split_authors("Schroeder, A.D.") == ["Schroeder, A.D."]


def test_split_strips_trailing_whitespace():
    assert split_authors("Schroeder, A.D. ") == ["Schroeder, A.D."]


def test_split_empty_string():
    assert split_authors("") == []


def test_split_full_first_name_pairs():
    s = "Schroeder, Aaron D., Tester, Diana., Forry, Nicole"
    assert split_authors(s) == [
        "Schroeder, Aaron D.", "Tester, Diana.", "Forry, Nicole",
    ]


def test_split_ampersand_separator():
    """Real writing.json uses ' & ' as final separator instead of ' and '."""
    s = "Baker, S., Schroeder, A. D., Rakha, H. A., & Hintz, R."
    assert split_authors(s) == [
        "Baker, S.", "Schroeder, A. D.", "Rakha, H. A.", "Hintz, R.",
    ]


def test_split_ampersand_two_authors():
    s = "Schroeder, A.D. & Bradburb, I."
    assert split_authors(s) == ["Schroeder, A.D.", "Bradburb, I."]


from profile_lib import bold_aaron


def test_bold_last_initial():
    assert bold_aaron("Schroeder A") == "**Schroeder A**"


def test_bold_last_two_initials():
    assert bold_aaron("Schroeder A.D.") == "**Schroeder A.D.**"


def test_bold_last_comma_initials():
    assert bold_aaron("Schroeder, A.D.") == "**Schroeder, A.D.**"


def test_bold_last_comma_spaced_initials():
    assert bold_aaron("Schroeder, A. D.") == "**Schroeder, A. D.**"


def test_bold_last_comma_full_first():
    assert bold_aaron("Schroeder, Aaron") == "**Schroeder, Aaron**"


def test_bold_last_comma_full_first_middle():
    assert bold_aaron("Schroeder, Aaron D.") == "**Schroeder, Aaron D.**"


def test_bold_first_last():
    assert bold_aaron("Aaron Schroeder") == "**Aaron Schroeder**"


def test_bold_first_middle_last():
    assert bold_aaron("Aaron D. Schroeder") == "**Aaron D. Schroeder**"


def test_bold_initials_last():
    assert bold_aaron("A.D. Schroeder") == "**A.D. Schroeder**"


def test_bold_does_not_match_other_schroeder():
    """T.T. Schroeder appears in writing.json — should NOT match Aaron."""
    assert bold_aaron("Schroeder, T.T.") == "Schroeder, T.T."


def test_bold_does_not_match_unrelated_author():
    assert bold_aaron("Shipp S") == "Shipp S"


def test_bold_already_bolded_is_unchanged():
    assert bold_aaron("**Schroeder, A.D.**") == "**Schroeder, A.D.**"


from profile_lib import normalize_doi


def test_doi_strip_https_prefix():
    assert normalize_doi("https://doi.org/10.18130/ce97-sp05") == "10.18130/ce97-sp05"


def test_doi_strip_http_prefix():
    assert normalize_doi("http://doi.org/10.1234/abcd") == "10.1234/abcd"


def test_doi_strip_dx_prefix():
    assert normalize_doi("https://dx.doi.org/10.1234/abcd") == "10.1234/abcd"


def test_doi_bare_prefix():
    assert normalize_doi("doi.org/10.1234/abcd") == "10.1234/abcd"


def test_doi_already_bare():
    assert normalize_doi("10.18130/ce97-sp05") == "10.18130/ce97-sp05"


def test_doi_empty_returns_none():
    assert normalize_doi("") is None


def test_doi_whitespace_returns_none():
    assert normalize_doi("   ") is None


def test_doi_invalid_returns_none():
    assert normalize_doi("not-a-doi") is None


def test_doi_label_prefix():
    assert normalize_doi("DOI: 10.1234/abcd") == "10.1234/abcd"


from profile_lib import writing_entry_to_publication


SAMPLE_WRITING_ENTRY = {
    "slug": "census_curated_data_enterprise",
    "date": "2023-01-01",
    "title": "Census Curated Data Enterprise Use Case Demonstration",
    "subcategory": "Research/Technical Reports",
    "journal": "Proceedings of the Biocomplexity Institute, TR# 2023-53",
    "dates": 2023,
    "authors": "Lancaster V, Shipp S, Keller S, Schroeder A, Mortveit H, Swarup S, Xie D",
    "editors": "",
    "pages": "",
    "DOI": "https://doi.org/10.18130/ce97-sp05",
    "website": "https://doi.org/10.18130/ce97-sp05",
    "ordinal": "",
    "abstract": "The proposed Curated Data Enterprise...",
}


def test_writing_entry_basic_fields():
    out = writing_entry_to_publication(SAMPLE_WRITING_ENTRY)
    assert out["title"] == "Census Curated Data Enterprise Use Case Demonstration"
    assert out["date"] == "2023-01-01"
    assert out["doi"] == "10.18130/ce97-sp05"
    assert out["journal"] == "Proceedings of the Biocomplexity Institute, TR# 2023-53"


def test_writing_entry_authors_split_and_aaron_bolded():
    out = writing_entry_to_publication(SAMPLE_WRITING_ENTRY)
    assert out["authors"] == [
        "Lancaster V", "Shipp S", "Keller S", "**Schroeder A**",
        "Mortveit H", "Swarup S", "Xie D",
    ]


def test_writing_entry_custom_keys_preserved():
    out = writing_entry_to_publication(SAMPLE_WRITING_ENTRY)
    assert out["slug"] == "census_curated_data_enterprise"
    assert out["subcategory"] == "Research/Technical Reports"
    assert out["abstract"].startswith("The proposed Curated Data Enterprise")


def test_writing_entry_empty_doi_omits_field():
    entry = dict(SAMPLE_WRITING_ENTRY, DOI="")
    out = writing_entry_to_publication(entry)
    assert "doi" not in out


def test_writing_entry_url_used_when_no_doi():
    entry = dict(SAMPLE_WRITING_ENTRY, DOI="", website="http://example.com/paper.pdf")
    out = writing_entry_to_publication(entry)
    assert out["url"] == "http://example.com/paper.pdf"
    assert "doi" not in out


def test_writing_entry_url_omitted_when_doi_present():
    """RenderCV ignores url if doi is present — don't bother emitting it."""
    out = writing_entry_to_publication(SAMPLE_WRITING_ENTRY)
    assert "url" not in out


def test_writing_entry_empty_optional_strings_omitted():
    """Don't emit empty 'editors', 'pages' as empty strings — omit entirely."""
    out = writing_entry_to_publication(SAMPLE_WRITING_ENTRY)
    assert "editors" not in out
    assert "pages" not in out


from profile_lib import (
    working_entry_to_normal,
    research_entry_to_normal,
    speaking_entry_to_normal,
    teaching_entry_to_normal,
)


def test_working_entry_basic():
    entry = {
        "title": "Associate Research Professor",
        "subtitle": "Research Associate Professor at Social and Decision Analytics Division, Bioinformatics Institute, University of Virginia",
        "dates": "2018-Present",
        "comments": True,
        "ordinal": 1,
        "slug": "associate-research-professor",
        "date": "2000-11-08",
        "abstract": "Dr. Schroeder's overarching research focus...",
    }
    out = working_entry_to_normal(entry)
    assert out["name"] == "Associate Research Professor"
    assert out["date"] == "2018-Present"
    assert out["summary"] == "Research Associate Professor at Social and Decision Analytics Division, Bioinformatics Institute, University of Virginia"
    assert out["slug"] == "associate-research-professor"
    assert out["abstract"].startswith("Dr. Schroeder")
    assert out["ordinal"] == "1"  # int coerced to str to satisfy RenderCV template engine


def test_research_entry_basic():
    entry = {
        "subcategory": "Data Integration & Management",
        "title": "ATIS Implementation Center",
        "date": "2004-05-22",
        "funder": "U.S. DOT Research and Special Programs Administration (RSPA)",
        "award": "$543,000",
        "dates": "2004-2005",
        "role": "Co-PI",
        "website": "",
        "ordinal": 9,
        "slug": "atis_rce",
        "abstract": "",
    }
    out = research_entry_to_normal(entry)
    assert out["name"] == "ATIS Implementation Center"
    assert out["date"] == "2004-2005"
    assert out["summary"] == "U.S. DOT Research and Special Programs Administration (RSPA) — $543,000 (Co-PI)"
    assert out["slug"] == "atis_rce"
    assert out["subcategory"] == "Data Integration & Management"


def test_research_entry_no_award_no_role():
    entry = {
        "title": "Bare project",
        "dates": "2020",
        "funder": "Sponsor X",
    }
    out = research_entry_to_normal(entry)
    assert out["summary"] == "Sponsor X"


def test_speaking_entry_basic():
    entry = {
        "slug": "COPAFS",
        "date": "2023-12-02",
        "title": "The Social Impact Data Commons",
        "subcategory": "Presentations/Workshops",
        "event": "Council of Professional Associations on Federal Statistics (COPAFS)",
        "dates": 2023,
        "role": "Lecture",
    }
    out = speaking_entry_to_normal(entry)
    assert out["name"] == "The Social Impact Data Commons"
    assert out["date"] == "2023-12-02"
    assert out["summary"] == "Lecture at Council of Professional Associations on Federal Statistics (COPAFS)"


def test_teaching_entry_basic():
    entry = {
        "title": "Administrative Data Systems & Technologies",
        "date": "2013-05-22",
        "comments": False,
        "website": "",
        "slug": "data-systems",
    }
    out = teaching_entry_to_normal(entry)
    assert out["name"] == "Administrative Data Systems & Technologies"
    assert out["date"] == "2013-05-22"
    assert out["slug"] == "data-systems"


def test_writing_entry_relative_website_becomes_local_path():
    """Relative paths can't be RenderCV urls — preserve them under 'local_path'."""
    entry = dict(SAMPLE_WRITING_ENTRY, DOI="", website="/downloads/foo.pdf")
    out = writing_entry_to_publication(entry)
    assert "url" not in out
    assert out["local_path"] == "/downloads/foo.pdf"


def test_writing_entry_dotdot_website_becomes_local_path():
    entry = dict(SAMPLE_WRITING_ENTRY, DOI="", website="../../../downloads/foo.pdf")
    out = writing_entry_to_publication(entry)
    assert "url" not in out
    assert out["local_path"] == "../../../downloads/foo.pdf"


def test_research_entry_relative_website_becomes_local_path():
    from profile_lib import research_entry_to_normal
    entry = {"title": "X", "website": "/downloads/x.pdf"}
    out = research_entry_to_normal(entry)
    assert "url" not in out
    assert out["local_path"] == "/downloads/x.pdf"
