# Sources Analyzer (Plan G) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scripts/analyze_sources.py` — a one-shot LLM-assisted extractor that reads any DOCX file in `sources/cvs/`, compares the entries it finds against the existing `site/content/profile.yaml`, and emits a human-readable `sources/_diff.md` with three sections: already-present entries, candidate NEW entries (with ready-to-paste YAML), and possibly-modified entries. The user reviews the diff and hand-applies anything they accept. The analyzer NEVER writes to `profile.yaml` directly.

**Architecture:** Python script using the Anthropic SDK with Sonnet 4.6 + adaptive thinking + high effort. DOCX → markdown via `mammoth`. The system prompt + `profile.yaml` are passed as the cached prefix (`cache_control: ephemeral`); the volatile CV text comes after. One API call per run; streamed output to avoid timeouts on the long markdown diff. Pure utility functions (title normalization, profile parsing, DOCX extraction) are TDD'd; the orchestrator is run-and-inspect.

**Tech Stack:** Python 3.14, `anthropic` SDK, `mammoth` (DOCX → markdown), `python-dotenv` (load `ANTHROPIC_API_KEY` from `.env`), `pyyaml` (already installed), `pytest` (already installed).

**Out of scope:**
- PDF / Markdown / plain text source support — DOCX-only for v1
- Auto-application of accepted entries (user pastes by hand)
- Confidence scoring beyond the LLM's own qualitative judgment in the diff text
- Plans B–F (separate plans)

---

## File Structure

**Create:**
- `scripts/analyzer_lib.py` — Pure utility functions: title normalization, `profile.yaml` entry extraction, DOCX → markdown wrapper. No I/O beyond the file-read inside the DOCX wrapper. All testable.
- `scripts/analyze_sources.py` — Orchestrator: loads `.env`, finds a DOCX in `sources/cvs/`, calls Anthropic API, writes `sources/_diff.md`.
- `scripts/tests/test_analyzer_lib.py` — pytest tests for the utility functions.

**Modify:**
- `scripts/requirements.txt` — Add `anthropic`, `mammoth`, `python-dotenv`.
- `.gitignore` — Add `sources/_diff.md`, `sources/_processed/`.
- `sources/README.md` — Document the now-built workflow (replace the "future analyzer" hedge with concrete usage).

**Why this split:** `analyzer_lib.py` holds pure functions so they're trivially testable. `analyze_sources.py` is the orchestrator (I/O + API call) — the API call's correctness is verified by inspecting the actual `_diff.md` output against the real CV, not by unit tests.

---

## Task 1: Add Python deps

**Files:**
- Modify: `scripts/requirements.txt`

- [ ] **Step 1: Update requirements.txt**

Replace the contents of `scripts/requirements.txt` with:
```
pyyaml>=6.0
rendercv[full]>=2.0
pytest>=8.0
anthropic>=0.40.0
mammoth>=1.8.0
python-dotenv>=1.0.0
```

- [ ] **Step 2: Install new deps into existing venv**

```bash
.venv/bin/pip install -r scripts/requirements.txt
```

Expected: `anthropic`, `mammoth`, `python-dotenv` install with no errors. Existing packages stay at current versions.

- [ ] **Step 3: Verify imports**

```bash
.venv/bin/python -c "import anthropic, mammoth, dotenv; print(anthropic.__version__, mammoth.__version__)"
```

Expected: prints two version strings, no ImportError.

- [ ] **Step 4: Commit**

```bash
git add scripts/requirements.txt
git commit -m "chore: add anthropic + mammoth + dotenv for sources analyzer"
```

---

## Task 2: Title normalizer (TDD)

**Files:**
- Create: `scripts/analyzer_lib.py`
- Modify: `scripts/tests/test_analyzer_lib.py` (new file)

The normalizer maps publication titles to a canonical form so that the LLM's extracted-from-CV titles match `profile.yaml`'s titles despite trivial differences (case, punctuation, smart quotes, trailing periods).

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_analyzer_lib.py`:
```python
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
```

`scripts/analyzer_lib.py` (stub):
```python
def normalize_title(s: str) -> str:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 9 fail**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 9 failures, all `NotImplementedError`.

- [ ] **Step 3: Implement `normalize_title`**

Replace stub in `scripts/analyzer_lib.py`:
```python
import re

_SMART_QUOTES = str.maketrans({
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
    "—": "-", "–": "-",
})


def normalize_title(s: str) -> str:
    """Canonical form of a publication/entry title for cross-source matching."""
    if not s:
        return ""
    s = s.translate(_SMART_QUOTES)
    s = s.strip().strip('"').strip("'").strip()
    s = s.rstrip(".")
    s = re.sub(r"\s+", " ", s)
    return s.lower()
```

- [ ] **Step 4: Run tests, confirm all 9 pass**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/analyzer_lib.py scripts/tests/test_analyzer_lib.py
git commit -m "feat(scripts): add title normalizer for source-vs-profile matching"
```

---

## Task 3: profile.yaml entry extractor (TDD)

**Files:**
- Modify: `scripts/analyzer_lib.py`
- Modify: `scripts/tests/test_analyzer_lib.py`

This walks `profile.yaml`'s sections and extracts a flat list of `(section_name, entry_title)` tuples. The orchestrator passes this list to the LLM so it knows what's already in the SSOT.

- [ ] **Step 1: Write failing tests**

Append to `scripts/tests/test_analyzer_lib.py`:
```python
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
```

`scripts/analyzer_lib.py` (add stub):
```python
def extract_profile_titles(profile: dict) -> list[tuple[str, str]]:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 6 new fail**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 6 new failures (15 total: 9 prior pass + 6 fail).

- [ ] **Step 3: Implement `extract_profile_titles`**

Append to `scripts/analyzer_lib.py`:
```python
def extract_profile_titles(profile: dict) -> list[tuple[str, str]]:
    """Walk profile.yaml's cv.sections; return (section_name, entry_title) tuples.

    Pulls a title from each entry using these field-name preferences:
    publication_entry → 'title', normal_entry → 'name', education → 'institution',
    OneLineEntry → 'label'. Bare-string sections (Summary, Skills) are skipped.
    """
    out: list[tuple[str, str]] = []
    sections = profile.get("cv", {}).get("sections", {})
    for section_name, entries in sections.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            title = (
                entry.get("title")
                or entry.get("name")
                or entry.get("institution")
                or entry.get("label")
            )
            if title:
                out.append((section_name, title))
    return out
```

- [ ] **Step 4: Run tests, confirm all 15 pass**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 15 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/analyzer_lib.py scripts/tests/test_analyzer_lib.py
git commit -m "feat(scripts): extract (section, title) tuples from profile.yaml"
```

---

## Task 4: DOCX → markdown wrapper (TDD)

**Files:**
- Modify: `scripts/analyzer_lib.py`
- Modify: `scripts/tests/test_analyzer_lib.py`

A thin wrapper around `mammoth.convert_to_markdown` that takes a Path and returns the markdown string. Tested with a tiny generated DOCX fixture.

- [ ] **Step 1: Write failing tests**

Append to `scripts/tests/test_analyzer_lib.py`:
```python
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
    """Write a minimal valid DOCX. Uses python-docx if available, else mammoth-readable XML.

    python-docx is not in our requirements; instead we generate a hand-rolled
    minimal DOCX (a zip of the required XML parts).
    """
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
```

`scripts/analyzer_lib.py` (add stub):
```python
from pathlib import Path


def docx_to_markdown(path: Path) -> str:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 2 new fail**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 2 new failures (17 total: 15 pass + 2 fail).

- [ ] **Step 3: Implement `docx_to_markdown`**

Replace stub in `scripts/analyzer_lib.py`:
```python
import mammoth
from pathlib import Path


def docx_to_markdown(path: Path) -> str:
    """Convert a DOCX file to markdown text via mammoth."""
    if not path.exists():
        raise FileNotFoundError(f"DOCX not found: {path}")
    with open(path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value
```

- [ ] **Step 4: Run tests, confirm all 17 pass**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 17 passed. (mammoth may emit a warning to stderr about unrecognized styles in the minimal DOCX — that's fine, the text content still extracts.)

- [ ] **Step 5: Commit**

```bash
git add scripts/analyzer_lib.py scripts/tests/test_analyzer_lib.py
git commit -m "feat(scripts): add DOCX→markdown wrapper via mammoth"
```

---

## Task 5: Analyzer orchestrator script

**Files:**
- Create: `scripts/analyze_sources.py`

Single-purpose script: find a DOCX in `sources/cvs/`, build the prompt, call the API, write `sources/_diff.md`. No tests — verified end-to-end in Task 6.

- [ ] **Step 1: Write the orchestrator**

`scripts/analyze_sources.py`:
```python
#!/usr/bin/env python3
"""LLM-assisted source analyzer: compare a CV in sources/cvs/ against profile.yaml.

Run from repo root:
    .venv/bin/python scripts/analyze_sources.py

Output: sources/_diff.md (gitignored). Review and hand-apply accepted entries.
The script NEVER writes to site/content/profile.yaml.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

from analyzer_lib import docx_to_markdown, extract_profile_titles

REPO_ROOT = Path(__file__).resolve().parent.parent
CV_DIR = REPO_ROOT / "sources" / "cvs"
PROFILE_PATH = REPO_ROOT / "site" / "content" / "profile.yaml"
OUTPUT_PATH = REPO_ROOT / "sources" / "_diff.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

SYSTEM_PROMPT = """You are a careful research assistant analyzing a CV/vita against an existing structured profile.yaml file.

Your job is to extract every distinct entry from the CV (publications, talks, positions, education, awards, etc.) and compare each one against the entries already in profile.yaml. Output a single Markdown document with three sections:

## Already in profile.yaml
A bulleted list of CV entries that match a title already in profile.yaml. One line per match: `- ✓ "<entry title>" — matched section: <profile section name>`. No body text needed.

## Candidate NEW entries
For each CV entry NOT found in profile.yaml, provide:
- A subheading with the entry type and short title
- A ready-to-paste YAML snippet matching RenderCV's schema. Use `publication_entry` shape (title, authors as a list, date, doi, journal) for publications; use `normal_entry` shape (name, date, summary) for experience/research/talks/teaching; use `OneLineEntry` shape (label, details) for awards. Wrap in a fenced ```yaml block.
- Bold Aaron Schroeder's name in the authors list using **double asterisks** wherever it appears. Other authors are not bolded.

## Possibly modified entries
For CV entries whose title matches profile.yaml but whose details (authors, date, journal, etc.) appear different, briefly describe the discrepancy. Do NOT propose a YAML patch — just flag it for the user's review.

Match titles loosely: ignore case, trailing periods, smart quotes, extra whitespace. If you're unsure whether two titles refer to the same work, err on the side of "possibly modified" rather than "new".

Be honest about uncertainty. If a CV section is hard to parse or you can't tell what type an entry is, say so in a brief preamble before the three sections.

Do NOT include preamble narrative beyond the section headings unless flagging real uncertainty. Be concise."""


def build_user_message(profile_yaml_text: str, profile_titles: list, cv_markdown: str, cv_filename: str) -> list:
    titles_summary = "\n".join(f"- [{section}] {title}" for section, title in profile_titles)
    return [
        {
            "type": "text",
            "text": f"Existing profile.yaml ({PROFILE_PATH.name}):\n\n```yaml\n{profile_yaml_text}\n```\n\nFlat title index of profile.yaml ({len(profile_titles)} entries):\n\n{titles_summary}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"CV source file: `{cv_filename}` (converted from DOCX to Markdown)\n\n---\n\n{cv_markdown}\n\n---\n\nAnalyze this CV against profile.yaml above. Produce the three-section Markdown diff per your instructions.",
        },
    ]


def find_cv() -> Path:
    docx_files = sorted(CV_DIR.glob("*.docx"))
    if not docx_files:
        sys.exit(f"No .docx files found in {CV_DIR}. Drop a CV there and re-run.")
    if len(docx_files) > 1:
        print(f"Multiple .docx files in {CV_DIR}; using the most recent: {docx_files[-1].name}", file=sys.stderr)
    return docx_files[-1]


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Add it to .env at repo root.")

    cv_path = find_cv()
    print(f"Reading CV: {cv_path.name}", file=sys.stderr)
    cv_markdown = docx_to_markdown(cv_path)

    print(f"Loading profile.yaml ({PROFILE_PATH.stat().st_size // 1024} KB)", file=sys.stderr)
    profile_yaml_text = PROFILE_PATH.read_text()
    profile = yaml.safe_load(profile_yaml_text)
    profile_titles = extract_profile_titles(profile)
    print(f"Indexed {len(profile_titles)} existing entries across {len(set(s for s, _ in profile_titles))} sections", file=sys.stderr)

    client = Anthropic()
    print(f"Calling {MODEL} (adaptive thinking, effort=high) — may take 30-90s", file=sys.stderr)

    diff_text_parts: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": build_user_message(profile_yaml_text, profile_titles, cv_markdown, cv_path.name)}],
    ) as stream:
        for text in stream.text_stream:
            diff_text_parts.append(text)
            print(text, end="", flush=True)
        final = stream.get_final_message()

    diff_text = "".join(diff_text_parts)
    header = (
        f"# Source Analysis: {cv_path.name}\n\n"
        f"Generated {datetime.now().isoformat(timespec='seconds')} from `{cv_path.relative_to(REPO_ROOT)}`\n"
        f"Indexed {len(profile_titles)} existing profile.yaml entries.\n"
        f"Model: {MODEL} | input: {final.usage.input_tokens} tokens "
        f"(cache_read: {final.usage.cache_read_input_tokens}, "
        f"cache_creation: {final.usage.cache_creation_input_tokens}) | "
        f"output: {final.usage.output_tokens} tokens\n\n---\n\n"
    )
    OUTPUT_PATH.write_text(header + diff_text + "\n")
    print(f"\n\nWrote {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit (run is the next task)**

```bash
git add scripts/analyze_sources.py
git commit -m "feat: add analyze_sources.py orchestrator (Sonnet 4.6 + cached profile.yaml)"
```

---

## Task 6: Run end-to-end against the real CV

**Files:**
- Modify: `.gitignore`

This is the integration test. It makes a real API call (~$0.40 first run, ~$0.20 cached re-runs).

- [ ] **Step 1: Add output to gitignore BEFORE running**

Append to `.gitignore` at repo root:
```
# Sources analyzer output
sources/_diff.md
sources/_processed/
```

- [ ] **Step 2: Run the analyzer**

```bash
.venv/bin/python scripts/analyze_sources.py
```

Expected:
- Stderr shows `Reading CV: Schroeder_Vita_09_25_2024.docx`, `Loading profile.yaml (~286 KB)`, `Indexed N entries across M sections`, `Calling claude-sonnet-4-6 ...`
- Markdown streams to stdout
- `sources/_diff.md` exists and is > 5 KB
- Token usage line in the output header shows nonzero `input_tokens`

If the API call fails, STOP and report the error. Do not try to silently work around `ANTHROPIC_API_KEY` errors or rate limits.

- [ ] **Step 3: Sanity-check the diff**

Open `sources/_diff.md` and verify:
- Has three top-level sections: "Already in profile.yaml", "Candidate NEW entries", "Possibly modified entries"
- The "already" section is non-empty (the CV almost certainly contains things already in profile.yaml)
- At least one candidate-new entry has a fenced ```yaml block ready to paste
- Aaron Schroeder's name appears bolded with `**...**` somewhere in the YAML snippets

If the model produces something significantly off-spec (no sections, no YAML, garbled content), STOP and report — the system prompt or model choice may need adjustment.

- [ ] **Step 4: Re-run to verify prompt caching works**

```bash
.venv/bin/python scripts/analyze_sources.py
```

Expected: the second run's header shows `cache_read` in the thousands-of-tokens range (the profile.yaml block should hit the cache). If `cache_read` is 0, prompt caching isn't engaging — investigate before declaring done.

- [ ] **Step 5: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore sources/_diff.md and _processed/"
```

---

## Task 7: Update sources/README.md

**Files:**
- Modify: `sources/README.md`

Replace the "future analyzer" hedge with concrete usage now that the analyzer exists.

- [ ] **Step 1: Rewrite README**

Replace `sources/README.md` with:
```markdown
# sources/ — Drop-zone for raw artifacts

Drop old vitae, publication PDFs, talk decks, etc. into the appropriate subfolder.
The analyzer (`scripts/analyze_sources.py`) reads a DOCX from `sources/cvs/` and
emits a proposed YAML diff against `site/content/profile.yaml` for human review.

The analyzer NEVER edits `profile.yaml` directly — you are always in the loop
reviewing extracted facts before they enter the SSOT.

## Subfolders

- `cvs/` — old vitae (DOCX). The analyzer reads the most-recent `*.docx` here.
- `publications/` — publication PDFs / preprints — for future PDF analyzer support
- `talks/` — slide decks, abstracts — for future analyzer support
- `raw/` — anything else / unsorted

## Workflow

1. Drop a `.docx` CV into `sources/cvs/`
2. Ensure `ANTHROPIC_API_KEY` is set in `.env` at repo root
3. Run: `.venv/bin/python scripts/analyze_sources.py`
4. Review `sources/_diff.md` (gitignored) — three sections:
   - **Already in profile.yaml** — entries the CV and SSOT agree on (informational)
   - **Candidate NEW entries** — proposed YAML snippets ready to paste into profile.yaml
   - **Possibly modified entries** — entries whose details differ; flagged for your review
5. Hand-paste accepted entries into `site/content/profile.yaml`
6. (Optional) Move processed sources into `sources/_processed/` (also gitignored)

## Cost & caching

The analyzer uses Sonnet 4.6 with prompt caching on the `profile.yaml` block.
First run: ~$0.40 (full read of profile.yaml). Subsequent runs against the same
profile: ~$0.20 (cache hit on profile.yaml; only the CV input is fresh).

## Format support

Currently DOCX-only. PDF/Markdown support and the publications/talks subfolder
analyzers are future work.
```

- [ ] **Step 2: Commit**

```bash
git add sources/README.md
git commit -m "docs(sources): document analyze_sources.py workflow"
```

---

## Task 8: Final sanity sweep

- [ ] **Step 1: Run all tests**

```bash
.venv/bin/pytest scripts/tests/ -v
```

Expected: 17 + the prior 45 = 62 passed.

- [ ] **Step 2: Confirm clean working tree**

```bash
git status
```

Expected: clean (no untracked or modified files; `sources/_diff.md` gitignored).

- [ ] **Step 3: Verify the analyzer is still callable**

```bash
.venv/bin/python scripts/analyze_sources.py --help 2>&1 || echo "(no --help; that's fine — script has no argparse)"
```

The script doesn't take arguments. This step just confirms it imports cleanly.

- [ ] **Step 4: Verify migration tooling didn't regress**

```bash
.venv/bin/python scripts/migrate_to_profile.py
git diff --stat site/content/profile.yaml
```

Expected: counts print as before; `git diff` shows zero changes (Plan G didn't touch the migration path).

- [ ] **Step 5: Verify website still builds**

```bash
cd site && npm run build 2>&1 | tail -3
```

Expected: builds successfully (Plan G is purely additive — no site code touched).

---

## Acceptance Criteria

- [ ] `scripts/analyze_sources.py` runs end-to-end against `sources/cvs/Schroeder_Vita_09_25_2024.docx` and produces a non-trivial `sources/_diff.md`
- [ ] The diff has three sections; "Candidate NEW entries" has at least one ready-to-paste YAML snippet
- [ ] Aaron Schroeder's name is bolded in proposed author lists
- [ ] Re-running the analyzer hits the prompt cache (verified by header's `cache_read_input_tokens > 0`)
- [ ] All pytest tests still pass (62 total)
- [ ] `npm run build` in `site/` still succeeds (no website behavior change)
- [ ] `sources/_diff.md` and `sources/_processed/` are gitignored
- [ ] `sources/README.md` documents the now-built workflow
