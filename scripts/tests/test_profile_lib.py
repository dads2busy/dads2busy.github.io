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
