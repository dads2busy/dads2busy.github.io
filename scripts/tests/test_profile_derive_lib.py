import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from profile_derive_lib import derive_title_from_content, derive_category_from_content


# ─── derive_title_from_content ───────────────────────────────────────

def test_title_quoted_after_lecture():
    s = 'Schroeder, A.D. Lecture: "The Social Impact Data Commons" (2023), COPAFS.'
    assert derive_title_from_content(s) == "The Social Impact Data Commons"


def test_title_quoted_after_presentation():
    s = 'Schroeder, A.D. Presentation: "Data Re-Use in Action" (2022), MASN.'
    assert derive_title_from_content(s) == "Data Re-Use in Action"


def test_title_bare_after_colon_until_period():
    s = "Schroeder, A.D. Panelist: Federated and Centralized Models. 26th Annual MIS Conference."
    assert derive_title_from_content(s) == "Federated and Centralized Models"


def test_title_bare_after_workshop_colon():
    s = "Schroeder, A.D. Workshop: Intelligent Transportation Systems of Virginia Annual Conference."
    assert derive_title_from_content(s) == "Intelligent Transportation Systems of Virginia Annual Conference"


def test_title_returns_none_when_no_keyword():
    s = "Some unstructured citation with no recognizable category prefix"
    assert derive_title_from_content(s) is None


def test_title_returns_none_for_empty_string():
    assert derive_title_from_content("") is None


def test_title_handles_smart_quotes():
    s = 'Schroeder, A.D. Lecture: "Smart Quote Title" (2023), Venue.'
    assert derive_title_from_content(s) == "Smart Quote Title"


def test_title_strips_whitespace():
    s = 'Schroeder, A.D. Presentation:   "Trimmed Title"   (2023), Venue.'
    assert derive_title_from_content(s) == "Trimmed Title"


# ─── derive_category_from_content ────────────────────────────────────

def test_category_lecture():
    s = 'Schroeder, A.D. Lecture: "X" (2023), Venue.'
    assert derive_category_from_content(s) == "Lecture"


def test_category_panelist():
    s = "Schroeder, A.D. Panelist: Federated Models. Venue."
    assert derive_category_from_content(s) == "Panelist"


def test_category_presentation():
    s = 'Schroeder, A.D. Presentation: "Data Re-Use in Action" (2022), MASN.'
    assert derive_category_from_content(s) == "Presentations/Workshops"


def test_category_workshop():
    s = "Schroeder, A.D. Workshop: ITSVA Annual Conference."
    assert derive_category_from_content(s) == "Presentations/Workshops"


def test_category_expert_forum_two_word():
    s = 'Schroeder, A.D. Expert Forum: "X" (2023), Venue.'
    assert derive_category_from_content(s) == "Expert Forum"


def test_category_expert_webinar_two_word():
    s = 'Schroeder, A.D. Expert Webinar: "X" (2023), Venue.'
    assert derive_category_from_content(s) == "Expert Webinar"


def test_category_committee():
    s = "Schroeder, A.D. Committee: Pre-Summit Workshop. Venue."
    assert derive_category_from_content(s) == "Committee"


def test_category_returns_none_when_no_match():
    s = "Some unstructured citation text"
    assert derive_category_from_content(s) is None


def test_category_returns_none_for_empty():
    assert derive_category_from_content("") is None


def test_category_first_match_wins_when_multiple():
    """If content somehow has multiple keywords, the first one in the canonical
    order wins (Panelist before Presentation, etc.). Mapped to 6 canonical categories."""
    s = "Discussed at Panelist: Topic A. Followed by Lecture: Topic B."
    assert derive_category_from_content(s) == "Panelist"
