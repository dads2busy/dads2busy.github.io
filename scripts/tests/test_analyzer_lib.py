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
