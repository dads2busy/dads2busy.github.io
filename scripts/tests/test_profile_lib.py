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
