import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer_lib import normalize_title


def test_normalize_lowercase():
    assert normalize_title("Hello World") == "hello world"


def test_normalize_strips_trailing_period():
    assert normalize_title("Hello World.") == "hello world"


def test_normalize_collapses_whitespace():
    assert normalize_title("Hello   World") == "hello world"
    assert normalize_title("Hello\t World\n") == "hello world"


def test_normalize_strips_outer_quotes():
    assert normalize_title('"Hello World"') == "hello world"
    assert normalize_title("'Hello World'") == "hello world"


def test_normalize_smart_quotes_to_ascii():
    assert normalize_title("“Hello World”") == "hello world"


def test_normalize_em_dash_to_hyphen():
    assert normalize_title("Hello — World") == "hello - world"


def test_normalize_multiple_punctuation():
    assert normalize_title("Hello, World!") == "hello, world!"


def test_normalize_empty_string():
    assert normalize_title("") == ""


def test_normalize_only_whitespace():
    assert normalize_title("   ") == ""


from analyzer_lib import extract_profile_titles


SAMPLE_PROFILE = {
    "cv": {
        "name": "Aaron D. Schroeder",
        "sections": {
            "Summary": ["paragraph 1", "paragraph 2"],
            "Education": [
                {"institution": "VT", "degree": "PhD"},
            ],
            "Experience": [
                {"name": "Research Associate Professor"},
            ],
            "Refereed Journal Articles": [
                {"title": "First Paper", "authors": ["**Schroeder, A.**"]},
                {"title": "Second Paper", "authors": ["**Schroeder, A.**"]},
            ],
            "Awards & Honors": [
                {"label": "Some Award", "details": "2020"},
            ],
            "Skills": ["Python", "R"],
        },
    },
}


def test_extract_skips_summary_paragraphs():
    """Summary is just strings, no titles to extract."""
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Summary", "paragraph 1") not in out


def test_extract_publication_titles():
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Refereed Journal Articles", "First Paper") in out
    assert ("Refereed Journal Articles", "Second Paper") in out


def test_extract_normal_entry_names():
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Experience", "Research Associate Professor") in out


def test_extract_education_uses_institution():
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Education", "VT") in out


def test_extract_award_labels():
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Awards & Honors", "Some Award") in out


def test_extract_skips_skills_strings():
    """Skills is bare strings, not 'titled' entries."""
    out = extract_profile_titles(SAMPLE_PROFILE)
    assert ("Skills", "Python") not in out
