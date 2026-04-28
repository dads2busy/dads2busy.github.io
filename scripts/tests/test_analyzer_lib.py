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


from analyzer_lib import docx_to_markdown


def test_docx_to_markdown_returns_string(tmp_path):
    """Round-trip a tiny generated DOCX and confirm we get its text back."""
    docx_path = tmp_path / "tiny.docx"
    _write_minimal_docx(docx_path, "Hello from DOCX")

    out = docx_to_markdown(docx_path)
    assert "Hello from DOCX" in out


def test_docx_to_markdown_missing_file_raises(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        docx_to_markdown(tmp_path / "nonexistent.docx")


def _write_minimal_docx(path, text):
    """Write a minimal valid DOCX (a zip of the required XML parts)."""
    import zipfile
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("word/document.xml", document_xml)


from analyzer_lib import extract_profile_dois


def test_extract_profile_dois_only_from_publication_sections():
    profile = {
        "cv": {
            "sections": {
                "Refereed Journal Articles": [
                    {"title": "Paper A", "doi": "10.x/a"},
                    {"title": "Paper B", "doi": "10.x/b"},
                    {"title": "Paper C"},
                ],
                "Research / Technical Reports": [
                    {"title": "Report X", "doi": "10.x/x"},
                ],
                "Experience": [
                    {"name": "Position", "doi": "should-not-appear"},
                ],
                "Awards & Honors": [
                    {"label": "Award", "details": "2020"},
                ],
            },
        },
    }
    out = extract_profile_dois(profile)
    assert "10.x/a" in out
    assert "10.x/b" in out
    assert "10.x/x" in out
    assert "should-not-appear" not in out
    assert len(out) == 3


def test_extract_profile_dois_handles_empty_sections():
    profile = {"cv": {"sections": {}}}
    assert extract_profile_dois(profile) == set()
