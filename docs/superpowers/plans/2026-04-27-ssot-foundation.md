# SSOT Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a validated `site/content/profile.yaml` (RenderCV-format SSOT) seeded from existing JSONs and the home page's hardcoded data, plus `site_extras.yaml` and a `sources/` drop-zone — without touching the live website yet.

**Architecture:** A one-time Python migration script (`scripts/migrate_to_profile.py`) reads `writing/working/research/speaking/teaching.json` plus hardcoded constants for identity/summary/education/awards/skills, normalizes the data (author splitting, DOI normalization, Aaron-Schroeder bolding), and emits `profile.yaml` in RenderCV format with arbitrary custom keys preserved per entry. Pure utility functions (parsing/normalization) get pytest coverage. Successful render via `rendercv render` is the acceptance gate. The website continues to read the existing JSONs and hardcoded `page.tsx` data — no behavior changes here. Subsequent plans wire the SSOT to consumers.

**Tech Stack:** Python 3.14 (already installed), PyYAML 6.0.3 (already installed), pytest (to install), rendercv (to install). No JS/Next.js changes in this plan.

**Out of scope (future plans):**
- Reverse generators (profile.yaml → 5 content JSONs) — Plan B
- `page.tsx` reading from YAMLs — Plan C
- RenderCV in CI / `vita.pdf` deployment — Plan D
- ORCID review-diff — Plan E
- LinkedIn Markdown view — Plan F
- `sources/` LLM analyzer — Plan G

---

## File Structure

**Create:**
- `scripts/migrate_to_profile.py` — Main entry point. Imports utility module; reads JSONs; writes YAML.
- `scripts/profile_lib.py` — Pure utility functions (author parsing, name bolding, DOI normalization, JSON-entry-to-RenderCV-entry conversions). No I/O. All testable.
- `scripts/tests/__init__.py` — Empty marker.
- `scripts/tests/test_profile_lib.py` — pytest tests for `profile_lib.py`.
- `scripts/requirements.txt` — pyyaml, rendercv, pytest pinned.
- `site/content/profile.yaml` — Output of migration. RenderCV-format SSOT.
- `site/content/site_extras.yaml` — Hand-authored. Tagline, polymath callout, research focus paragraphs.
- `sources/README.md` — Workflow documentation for the analyzer drop-zone.
- `sources/cvs/.gitkeep`, `sources/publications/.gitkeep`, `sources/talks/.gitkeep`, `sources/raw/.gitkeep` — Folder placeholders.

**Modify:**
- `.gitignore` — Add `scripts/__pycache__/`, `scripts/tests/__pycache__/`, `rendercv_output/` (RenderCV's default scratch dir).

**Why this split:** `profile_lib.py` holds pure functions so they're trivially testable. `migrate_to_profile.py` is the orchestrator (I/O + assembly) — runs once, gets committed for auditability, then is essentially dormant. Splitting them avoids putting test logic next to large hardcoded constants.

---

## Task 1: Set up Python tooling

**Files:**
- Create: `scripts/requirements.txt`

- [ ] **Step 1: Create requirements file**

`scripts/requirements.txt`:
```
pyyaml>=6.0
rendercv[full]>=2.0
pytest>=8.0
```

(The `[full]` extra installs the CLI binary; bare `rendercv` is library-only.)

- [ ] **Step 2: Install into a venv**

Run from repo root:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

Expected: pip installs all three with no errors. `rendercv --help` works.

- [ ] **Step 3: Verify rendercv is callable**

Run:
```bash
.venv/bin/rendercv --version
```

Expected: prints a version like `2.x.x`. If the binary isn't on PATH, use `.venv/bin/rendercv` throughout this plan.

- [ ] **Step 4: Commit**

```bash
git add scripts/requirements.txt
git commit -m "chore: add Python deps for SSOT migration tooling"
```

---

## Task 2: Author splitter (TDD)

**Files:**
- Create: `scripts/profile_lib.py`
- Create: `scripts/tests/__init__.py`
- Create: `scripts/tests/test_profile_lib.py`

The splitter handles three patterns observed in `writing.json`:
1. `"Lancaster V, Shipp S, Keller S"` — comma-separated, "Last F" format (single comma per name = none internal to a name).
2. `"Schroeder, A.D., Wamsley, G.L., and Ward, R."` — pairs of `Last, First` separated by commas, with `" and "` before the last.
3. `"Schroeder, A. and Shipp, S. and Kang, W."` — `Last, First` chunks separated by `" and "`.

- [ ] **Step 1: Write failing test**

`scripts/tests/__init__.py`: empty file.

`scripts/tests/test_profile_lib.py`:
```python
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
```

`scripts/profile_lib.py` (stub):
```python
def split_authors(s: str) -> list[str]:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm failure**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 7 failures, all `NotImplementedError`.

- [ ] **Step 3: Implement `split_authors`**

Replace the stub in `scripts/profile_lib.py`:
```python
import re


def split_authors(s: str) -> list[str]:
    """Split an author string into a list of individual author names.

    Handles three patterns:
      1. 'Last F, Last F'                               (comma-only, no internal commas per name)
      2. 'Last, First, Last, First, and Last, First'    (Last/First pairs with 'and')
      3. 'Last, F. and Last, F. and Last, F.'           ('and'-separated Last/First pairs)
    """
    if not s or not s.strip():
        return []

    s = s.strip()

    # Patterns 2 and 3: presence of ' and ' or ' & ' disambiguates Last/First pairing.
    if re.search(r"\s+(?:and|&)\s+", s):
        pieces = re.split(r",?\s+(?:and|&)\s+", s)
        result: list[str] = []
        for piece in pieces:
            piece = piece.strip().rstrip(",").strip()
            if not piece:
                continue
            commas = piece.count(",")
            if commas <= 1:
                result.append(piece)
            else:
                parts = [p.strip() for p in piece.split(",") if p.strip()]
                for i in range(0, len(parts), 2):
                    if i + 1 < len(parts):
                        result.append(f"{parts[i]}, {parts[i+1]}")
                    else:
                        result.append(parts[i])
        return result

    # No ' and ': either Pattern 1 (single-token initials) or Pattern 2 with no final 'and'.
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) == 1:
        return parts

    # Pattern 1 heuristic: every part is "Surname Initial(s)" — 2 tokens, second ≤ 2 chars.
    looks_like_pattern1 = all(
        len(p.split()) == 2 and len(p.split()[1]) <= 2
        for p in parts
    )
    if looks_like_pattern1:
        return parts

    # Otherwise pair consecutive parts as (Last, First).
    result = []
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            result.append(f"{parts[i]}, {parts[i+1]}")
        else:
            result.append(parts[i])
    return result
```

- [ ] **Step 4: Run tests, confirm pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_lib.py scripts/tests/__init__.py scripts/tests/test_profile_lib.py
git commit -m "feat(scripts): add author-splitter for profile migration"
```

---

## Task 3: Aaron Schroeder name bolder (TDD)

**Files:**
- Modify: `scripts/profile_lib.py`
- Modify: `scripts/tests/test_profile_lib.py`

- [ ] **Step 1: Add failing tests**

Append to `scripts/tests/test_profile_lib.py`:
```python
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
```

`scripts/profile_lib.py` (add stub at bottom):
```python
def bold_aaron(name: str) -> str:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm new ones fail**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 12 new failures (from `NotImplementedError`), 7 still passing.

- [ ] **Step 3: Implement `bold_aaron`**

Append to `scripts/profile_lib.py`:
```python
_AARON_PATTERN = re.compile(
    r"""
    ^\s*
    (?:
        Schroeder,?\s*
            (?: Aaron (?:\s+D\.?)?
              | A\.?\s*D?\.?
            )?
        |
        (?: Aaron (?:\s+D\.?)?
          | A\.?\s*D?\.?
        )
        \s+ Schroeder
    )
    \.?\s*$
    """,
    re.VERBOSE,
)


def bold_aaron(name: str) -> str:
    """Wrap Aaron Schroeder name variants with **bold**. Pass-through otherwise."""
    if name.startswith("**") and name.endswith("**"):
        return name
    if _AARON_PATTERN.match(name.strip()):
        return f"**{name.strip()}**"
    return name
```

- [ ] **Step 4: Run tests, confirm all pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 19 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_lib.py scripts/tests/test_profile_lib.py
git commit -m "feat(scripts): bold Aaron Schroeder name variants in author lists"
```

---

## Task 4: DOI normalizer (TDD)

**Files:**
- Modify: `scripts/profile_lib.py`
- Modify: `scripts/tests/test_profile_lib.py`

- [ ] **Step 1: Add failing tests**

Append to `scripts/tests/test_profile_lib.py`:
```python
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
```

`scripts/profile_lib.py` (add stub):
```python
def normalize_doi(s: str | None) -> str | None:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm new ones fail**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 9 new failures, 19 still passing.

- [ ] **Step 3: Implement `normalize_doi`**

Append to `scripts/profile_lib.py`:
```python
def normalize_doi(s: str | None) -> str | None:
    """Strip URL/label prefixes from a DOI; return None if not a valid bare DOI."""
    if not s or not s.strip():
        return None
    s = s.strip()
    s = re.sub(r"^DOI:\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi\.org/", "", s)
    return s if s.startswith("10.") else None
```

- [ ] **Step 4: Run tests, confirm all pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 28 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_lib.py scripts/tests/test_profile_lib.py
git commit -m "feat(scripts): normalize DOI strings (strip URL/label prefixes)"
```

---

## Task 5: Convert one writing.json entry to a RenderCV publication_entry (TDD)

**Files:**
- Modify: `scripts/profile_lib.py`
- Modify: `scripts/tests/test_profile_lib.py`

This produces a Python dict matching RenderCV's `publication_entry` schema, with custom keys (`slug`, `ordinal`, `editors`, `pages`, `content`, `subcategory`) preserved on the same dict. RenderCV silently accepts the extras; the future generator script reads them.

- [ ] **Step 1: Add failing test**

Append to `scripts/tests/test_profile_lib.py`:
```python
from profile_lib import writing_entry_to_publication


SAMPLE_WRITING_ENTRY = {
    "slug": "census_curated_data_enterprise",
    "date": "2023-01-01",
    "title": "Census Curated Data Enterprise Use Case Demonstration",
    "subcategory": "Research/Technical Reports",
    "sponsor": "Proceedings of the Biocomplexity Institute, TR# 2023-53",
    "dates": 2023,
    "authors": "Lancaster V, Shipp S, Keller S, Schroeder A, Mortveit H, Swarup S, Xie D",
    "editors": "",
    "pages": "",
    "DOI": "https://doi.org/10.18130/ce97-sp05",
    "website": "https://doi.org/10.18130/ce97-sp05",
    "ordinal": "",
    "content": "The proposed Curated Data Enterprise...",
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
    assert out["content"].startswith("The proposed Curated Data Enterprise")


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
```

`scripts/profile_lib.py` (add stub):
```python
def writing_entry_to_publication(entry: dict) -> dict:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm new ones fail**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 7 new failures, 28 still passing.

- [ ] **Step 3: Implement `writing_entry_to_publication`**

Append to `scripts/profile_lib.py`:
```python
def writing_entry_to_publication(entry: dict) -> dict:
    """Convert one writing.json entry to a RenderCV publication_entry dict.

    Preserves custom keys (slug, ordinal, subcategory, content) for the
    site's content-JSON generator; RenderCV ignores them in default rendering.
    """
    out: dict = {
        "title": entry["title"],
        "authors": [bold_aaron(a) for a in split_authors(entry.get("authors", ""))],
    }

    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("sponsor"):
        out["journal"] = entry["sponsor"]

    doi = normalize_doi(entry.get("DOI"))
    if doi:
        out["doi"] = doi
    elif entry.get("website"):
        out["url"] = entry["website"]

    # Custom keys preserved verbatim — only when populated.
    for key in ("slug", "subcategory", "content"):
        val = entry.get(key)
        if val:
            out[key] = val
    for key in ("editors", "pages", "ordinal"):
        val = entry.get(key)
        if val not in (None, "", 0):
            out[key] = val

    return out
```

- [ ] **Step 4: Run tests, confirm all pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 35 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_lib.py scripts/tests/test_profile_lib.py
git commit -m "feat(scripts): convert writing.json entry to RenderCV publication_entry"
```

---

## Task 6: Convert working/research/speaking/teaching JSON entries

**Files:**
- Modify: `scripts/profile_lib.py`
- Modify: `scripts/tests/test_profile_lib.py`

These four converters produce RenderCV `normal_entry` dicts (RenderCV's most permissive entry type — `name` required, everything else optional). Custom keys ride along.

- [ ] **Step 1: Add failing tests**

Append to `scripts/tests/test_profile_lib.py`:
```python
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
        "content": "Dr. Schroeder's overarching research focus...",
    }
    out = working_entry_to_normal(entry)
    assert out["name"] == "Associate Research Professor"
    assert out["date"] == "2018-Present"
    assert out["summary"] == "Research Associate Professor at Social and Decision Analytics Division, Bioinformatics Institute, University of Virginia"
    assert out["slug"] == "associate-research-professor"
    assert out["content"].startswith("Dr. Schroeder")
    assert out["ordinal"] == 1


def test_research_entry_basic():
    entry = {
        "subcategory": "Data Integration & Management",
        "title": "ATIS Implementation Center",
        "date": "2004-05-22",
        "sponsor": "U.S. DOT Research and Special Programs Administration (RSPA)",
        "award": "$543,000",
        "dates": "2004-2005",
        "role": "Co-PI",
        "website": "",
        "ordinal": 9,
        "slug": "atis_rce",
        "content": "",
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
        "sponsor": "Sponsor X",
    }
    out = research_entry_to_normal(entry)
    assert out["summary"] == "Sponsor X"


def test_speaking_entry_basic():
    entry = {
        "slug": "COPAFS",
        "date": "2023-12-02",
        "title": "The Social Impact Data Commons",
        "subcategory": "Presentations/Workshops",
        "sponsor": "Council of Professional Associations on Federal Statistics (COPAFS)",
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
```

`scripts/profile_lib.py` (add four stubs):
```python
def working_entry_to_normal(entry: dict) -> dict:
    raise NotImplementedError


def research_entry_to_normal(entry: dict) -> dict:
    raise NotImplementedError


def speaking_entry_to_normal(entry: dict) -> dict:
    raise NotImplementedError


def teaching_entry_to_normal(entry: dict) -> dict:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm new ones fail**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 5 new failures, 35 still passing.

- [ ] **Step 3: Implement the four converters**

Replace the four stubs in `scripts/profile_lib.py`:
```python
def _passthrough_custom(entry: dict, out: dict, keys: tuple[str, ...]) -> None:
    """Copy non-empty custom keys from entry into out."""
    for key in keys:
        val = entry.get(key)
        if val not in (None, "", 0, False):
            out[key] = val


def working_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("dates"):
        out["date"] = entry["dates"]
    if entry.get("subtitle"):
        out["summary"] = entry["subtitle"]
    if entry.get("content"):
        out["content"] = entry["content"]
    _passthrough_custom(entry, out, ("slug", "subcategory", "ordinal"))
    return out


def research_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("dates"):
        out["date"] = str(entry["dates"])

    summary = entry.get("sponsor") or ""
    if entry.get("award"):
        summary = f"{summary} — {entry['award']}" if summary else entry["award"]
    if entry.get("role"):
        summary = f"{summary} ({entry['role']})" if summary else f"({entry['role']})"
    if summary:
        out["summary"] = summary

    if entry.get("website"):
        out["url"] = entry["website"]
    if entry.get("content"):
        out["content"] = entry["content"]

    _passthrough_custom(
        entry, out,
        (
            "slug", "subcategory", "ordinal",
            "report", "report2", "report3", "report4", "report5", "report6",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def speaking_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("date"):
        out["date"] = entry["date"]

    summary_parts = []
    if entry.get("role"):
        summary_parts.append(entry["role"])
    if entry.get("sponsor"):
        if summary_parts:
            summary_parts[0] = f"{summary_parts[0]} at {entry['sponsor']}"
        else:
            summary_parts.append(entry["sponsor"])
    if summary_parts:
        out["summary"] = summary_parts[0]

    if entry.get("website"):
        out["url"] = entry["website"]
    if entry.get("content"):
        out["content"] = entry["content"]

    _passthrough_custom(
        entry, out,
        (
            "slug", "subcategory",
            "report",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def teaching_entry_to_normal(entry: dict) -> dict:
    out: dict = {"name": entry["title"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("website"):
        out["url"] = entry["website"]
    if entry.get("content"):
        out["content"] = entry["content"]
    _passthrough_custom(entry, out, ("slug",))
    return out
```

- [ ] **Step 4: Run tests, confirm all pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_lib.py -v
```

Expected: 40 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_lib.py scripts/tests/test_profile_lib.py
git commit -m "feat(scripts): convert working/research/speaking/teaching entries to normal_entry"
```

---

## Task 7: Migration orchestrator script

**Files:**
- Create: `scripts/migrate_to_profile.py`

This is pure orchestration: read JSONs, call lib functions, build sections dict in correct order, dump YAML. Identity/summary/education/awards/skills are encoded as constants here (small, hand-curated from current `site/src/app/page.tsx`).

- [ ] **Step 1: Write the orchestrator**

`scripts/migrate_to_profile.py`:
```python
#!/usr/bin/env python3
"""One-time migration: existing content JSONs + page.tsx constants -> site/content/profile.yaml.

Run from repo root:
    .venv/bin/python scripts/migrate_to_profile.py
"""

import json
from collections import OrderedDict
from pathlib import Path

import yaml

from profile_lib import (
    research_entry_to_normal,
    speaking_entry_to_normal,
    teaching_entry_to_normal,
    working_entry_to_normal,
    writing_entry_to_publication,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "site" / "content"
OUTPUT_PATH = CONTENT_DIR / "profile.yaml"


# ────────────────────────────────────────────────────────────────────
# Hand-curated constants (sourced from site/src/app/page.tsx).
# ────────────────────────────────────────────────────────────────────

IDENTITY = {
    "name": "Aaron D. Schroeder",
    "email": "aaron.schroeder@virginia.edu",
    "social_networks": [
        {"network": "GitHub", "username": "dads2busy"},
    ],
}

SUMMARY = [
    "Dr. Schroeder's overarching research focus is the enablement of Evidence-Based Policy-Making and Program Evaluation through the secure liberation, integration and analysis of administrative data.",
    "A particular focus has been the integration of education, health, social service and non-profit administrative data streams to support policy analyses and program evaluations across pre-K services, child care, K-12 and adult education, state workforce training, and U.S. veteran services.",
    "High-profile information integration projects in the Commonwealth of Virginia include the USED-funded Statewide Longitudinal Data System, the USHHS-funded Project Child HANDS, and the USDOT-funded design and evaluation of the U.S.'s first statewide travel information system, Virginia 511.",
]

EDUCATION = [
    {
        "institution": "Virginia Tech University",
        "area": "Public Policy & Administration",
        "degree": "PhD",
        "date": "2001",
        "highlights": [
            "Areas: Organization Theory, Data Management, Privacy Law, Implementation",
            "Dissertation: Building Implementation Networks",
        ],
    },
    {
        "institution": "James Madison University",
        "area": "Public Administration",
        "degree": "MPA",
        "date": "1993",
        "highlights": ["Areas: Geographic Information Systems, Administrative Law"],
    },
    {
        "institution": "University of Delaware",
        "area": "Psychology",
        "degree": "BA",
        "date": "1991",
        "highlights": [
            "Areas: Brain & Behavior (incl. graduate-level Neuropsychology)",
            "Minor: Statistics",
        ],
    },
]

AWARDS = [
    {"label": "Member, Arlington County Open Data Advisory Group", "date": "2018-2019"},
    {"label": "COVITS Winner — Cross-Boundary Collaboration on IT (VLDS)", "date": "2013"},
    {"label": "COVITS Finalist — Virginia Longitudinal Data System", "date": "2012"},
    {"label": "Invited, Virginia Governor's Early Childhood Advisory Council", "date": "2010"},
    {"label": "Invited, National Institute of Statistical Sciences Workshop", "date": "2009"},
    {"label": "Invited, National Press Club — intergenerational day care findings", "date": "2008"},
    {"label": "Invited speaker, Florida DOT ITS Conference", "date": "2003"},
    {"label": "Invited workshop lead, Univ. of LaVerne — IT implementation", "date": "2000"},
    {"label": "Invited, Virginia Transportation Conference", "date": "1999-2000"},
    {"label": "Nominee, ASG Award for Innovation in State Government (Travel Shenandoah)", "date": "1999"},
    {"label": "Appointed Member, Congressional Commission on I-81 Truck Safety", "date": "1999"},
    {"label": "Eno Transportation Fellow", "date": "1997"},
    {"label": "Invited Guest Editor, Administration & Society", "date": "1997"},
]

SKILLS = [
    "R", "Python", "PostgreSQL", "Oracle PL/SQL", "MS SQL Server",
    "Linux Admin", "Docker", "JavaEE", "ASP.NET/C#", "SAS", "SPSS",
    "Network Admin", "Photoshop/GIMP", "LLMs/AI",
]

# Subcategory → vita section title. Order here = vita render order.
WRITING_SECTIONS = OrderedDict([
    ("Refereed Journal Articles", "Journal Publications (refereed)"),
    ("Book Chapters", "Book Chapters"),
    ("Conference Proceedings / Presentations", "Conference Proceedings/Presentations"),
    ("Research / Technical Reports", "Research/Technical Reports"),
    ("Editorials", "Editorials"),
    ("Dissertation", "Dissertation"),
])


def load_json(filename: str) -> list:
    return json.loads((CONTENT_DIR / filename).read_text())


def build_publication_sections() -> "OrderedDict[str, list[dict]]":
    """One section per writing.json subcategory, in the order from WRITING_SECTIONS."""
    entries = load_json("writing.json")
    by_sub: dict[str, list[dict]] = {}
    for e in entries:
        by_sub.setdefault(e["subcategory"], []).append(writing_entry_to_publication(e))

    sections: OrderedDict[str, list[dict]] = OrderedDict()
    for vita_title, json_subcategory in WRITING_SECTIONS.items():
        if pubs := by_sub.get(json_subcategory):
            sections[vita_title] = pubs
    return sections


def build_normal_section(filename: str, converter) -> list[dict]:
    return [converter(e) for e in load_json(filename)]


def build_profile() -> dict:
    sections: OrderedDict[str, list] = OrderedDict()
    sections["Summary"] = SUMMARY
    sections["Education"] = EDUCATION
    sections["Experience"] = build_normal_section("working.json", working_entry_to_normal)
    sections["Research Projects"] = build_normal_section("research.json", research_entry_to_normal)
    sections["Presentations"] = build_normal_section("speaking.json", speaking_entry_to_normal)
    sections["Teaching"] = build_normal_section("teaching.json", teaching_entry_to_normal)
    sections.update(build_publication_sections())
    sections["Awards & Honors"] = AWARDS
    sections["Skills"] = SKILLS

    return {
        "cv": {**IDENTITY, "sections": sections},
        "design": {"theme": "classic"},
    }


def represent_ordereddict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def main() -> None:
    yaml.add_representer(OrderedDict, represent_ordereddict)
    profile = build_profile()
    OUTPUT_PATH.write_text(
        yaml.dump(profile, sort_keys=False, allow_unicode=True, width=100)
    )
    counts = {k: len(v) if isinstance(v, list) else "—" for k, v in profile["cv"]["sections"].items()}
    print(f"Wrote {OUTPUT_PATH}")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the migration**

```bash
.venv/bin/python scripts/migrate_to_profile.py
```

Expected output (counts):
```
Wrote site/content/profile.yaml
  Summary: 3
  Education: 3
  Experience: 8
  Research Projects: 35
  Presentations: 34
  Teaching: 4
  Refereed Journal Articles: 20
  Book Chapters: 1
  Conference Proceedings / Presentations: 3
  Research / Technical Reports: 35
  Editorials: 1
  Dissertation: 1
  Awards & Honors: 13
  Skills: 14
```

If counts differ from these, investigate the source JSON before proceeding.

- [ ] **Step 3: Spot-check the YAML**

```bash
head -80 site/content/profile.yaml
grep -c '^    - title:' site/content/profile.yaml
grep -c '\*\*Schroeder' site/content/profile.yaml
```

Expected:
- `head` shows `cv:` then `name:` then `email:` then `sections:` then `Summary:`.
- The first `grep` count = 61 (total publications across all 6 publication sections, matching writing.json entry count).
- The second `grep` count is positive (Aaron should appear bolded in most publication author lists; some malformed source entries — e.g. `"Schroeder, A.D. Amanna, A."` with a missing comma — won't bold cleanly and get manual review later).
- Output file size is roughly 200–400 KB (long abstracts in `content` fields make this larger than a typical CV YAML).

- [ ] **Step 4: Commit**

```bash
git add scripts/migrate_to_profile.py site/content/profile.yaml
git commit -m "feat: migrate content JSONs + page.tsx constants to profile.yaml SSOT"
```

---

## Task 8: Validate profile.yaml renders via RenderCV

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add rendercv scratch dir to gitignore**

Append to `.gitignore`:
```
# Python
scripts/__pycache__/
scripts/tests/__pycache__/
.venv/

# RenderCV scratch output
rendercv_output/
```

- [ ] **Step 2: Render the vita**

```bash
.venv/bin/rendercv render site/content/profile.yaml --output-folder rendercv_output
```

Expected: command exits 0; `rendercv_output/Aaron_D_Schroeder_CV.pdf` exists. No schema validation errors.

If you see "extra fields not permitted" or any other schema validation error, check the current RenderCV docs at https://docs.rendercv.com for the installed version and adjust profile.yaml accordingly. The expected behavior (verified at plan-write time) is that arbitrary custom keys are accepted silently on entries.

- [ ] **Step 3: Open the PDF and skim for sanity**

```bash
open rendercv_output/Aaron_D_Schroeder_CV.pdf
```

Visual check (no automation):
- Name, email, GitHub at top
- Summary paragraphs
- Education with all 3 degrees
- Experience listing 8 positions
- Publication sections in declared order
- Aaron Schroeder's name appears bolded in author lists

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore python + rendercv scratch dirs"
```

---

## Task 9: Hand-author site_extras.yaml

**Files:**
- Create: `site/content/site_extras.yaml`

Small, ~30 lines. Holds the website-only fields that don't belong in a CV.

- [ ] **Step 1: Write the file**

`site/content/site_extras.yaml`:
```yaml
# Website-only fields not modeled by RenderCV.
# Consumed by the Next.js build (Plan C will wire page.tsx to read this).

tagline: "Libération de Données!"

description: >
  The entirely too-many activities of Aaron David Schroeder —
  Epistemologist, Methodologist, Technologist, Musicologist,
  Research Scientist, Coach[ologist], Dad[ologist], Husband (amateur),
  Fisherman (rank amateur)

# Order of sections rendered on the home page.
homepage_sections:
  - hero
  - research_focus
  - education_skills
  - honors
  - polymath

# Polymath callout (left-bordered box on home page).
polymath_callout:
  wikipedia_def: >
    A person whose expertise spans a significant number of subject areas.
    From the Greek polymathēs (πολυμαθής), "having learned much."
  schroeder_def: >
    A highly functioning person with A.D.D. who hangs around universities
    long enough to be awarded various degrees, ostensibly to entice the
    person to go away (unless, of course, they are good at bringing in
    grant money).

# The three Research Focus paragraphs displayed on the home page panel.
# These are the same as cv.sections.Summary in profile.yaml — kept here
# for now as a website-display copy; future Plan C may dedupe by reading
# Summary directly from profile.yaml instead.
research_focus_paragraphs:
  - "Dr. Schroeder's overarching research focus is the enablement of Evidence-Based Policy-Making and Program Evaluation through the secure liberation, integration and analysis of administrative data."
  - "A particular focus has been the integration of education, health, social service and non-profit administrative data streams to support policy analyses and program evaluations across pre-K services, child care, K-12 and adult education, state workforce training, and U.S. veteran services."
  - "High-profile information integration projects in the Commonwealth of Virginia include the USED-funded Statewide Longitudinal Data System, the USHHS-funded Project Child HANDS, and the USDOT-funded design and evaluation of the U.S.'s first statewide travel information system, Virginia 511."
```

- [ ] **Step 2: Verify YAML parses**

```bash
.venv/bin/python -c "import yaml; print(yaml.safe_load(open('site/content/site_extras.yaml')).keys())"
```

Expected: `dict_keys(['tagline', 'description', 'homepage_sections', 'polymath_callout', 'research_focus_paragraphs'])`

- [ ] **Step 3: Commit**

```bash
git add site/content/site_extras.yaml
git commit -m "feat: add site_extras.yaml for website-only display fields"
```

---

## Task 10: Sources drop-zone + README

**Files:**
- Create: `sources/README.md`
- Create: `sources/cvs/.gitkeep`
- Create: `sources/publications/.gitkeep`
- Create: `sources/talks/.gitkeep`
- Create: `sources/raw/.gitkeep`

- [ ] **Step 1: Create the folders**

```bash
mkdir -p sources/cvs sources/publications sources/talks sources/raw
touch sources/cvs/.gitkeep sources/publications/.gitkeep sources/talks/.gitkeep sources/raw/.gitkeep
```

- [ ] **Step 2: Write README**

`sources/README.md`:
```markdown
# sources/ — Drop-zone for raw artifacts

Drop old vitae, publication PDFs, talk decks, etc. into the appropriate
subfolder. A future analyzer (`scripts/analyze_sources.py`, Plan G) reads
these and emits proposed YAML diffs against `site/content/profile.yaml`
for human review.

The analyzer NEVER edits `profile.yaml` directly — you are always in the
loop reviewing extracted facts before they enter the SSOT.

## Subfolders

- `cvs/` — old vitae (PDF, DOC) — for cross-checking that profile.yaml
  hasn't lost prior content
- `publications/` — publication PDFs / preprints — for extracting metadata
  (title, authors, DOI, abstract) when adding new entries
- `talks/` — slide decks, abstracts — for extracting presentation entries
- `raw/` — anything else / unsorted

## Workflow (once the analyzer exists)

1. Drop a file into the correct subfolder
2. Run: `.venv/bin/python scripts/analyze_sources.py`
3. Review the proposed YAML diff
4. Manually paste accepted entries into `site/content/profile.yaml`
5. Move the source file out of `sources/` (or into a `sources/_processed/`
   subfolder once we add one)
```

- [ ] **Step 3: Commit**

```bash
git add sources/
git commit -m "feat: add sources/ drop-zone for future LLM-assisted profile updates"
```

---

## Task 11: Final sanity sweep

- [ ] **Step 1: Run all tests one more time**

```bash
.venv/bin/pytest scripts/tests/ -v
```

Expected: 40 passed.

- [ ] **Step 2: Re-run migration to confirm idempotence**

```bash
.venv/bin/python scripts/migrate_to_profile.py
git diff --stat site/content/profile.yaml
```

Expected: no changes (script is deterministic; same input → same output).

- [ ] **Step 3: Re-render vita to confirm clean state**

```bash
.venv/bin/rendercv render site/content/profile.yaml --output-folder rendercv_output
```

Expected: exit 0; PDF generated.

- [ ] **Step 4: Verify the website still builds (untouched)**

```bash
cd site && npm run build
```

Expected: 295 static pages, no errors. (We haven't touched any site code.)

- [ ] **Step 5: Final commit (only if anything new)**

If `git status` shows nothing, skip. Otherwise:
```bash
git add -A
git commit -m "chore: SSOT foundation final state"
```

---

## Acceptance Criteria

After completing all tasks:

- [ ] `site/content/profile.yaml` exists and parses as valid YAML.
- [ ] `.venv/bin/rendercv render site/content/profile.yaml` succeeds.
- [ ] All 40 pytest tests pass.
- [ ] `npm run build` in `site/` still succeeds (zero website behavior change).
- [ ] `sources/` folder exists with README and 4 subfolders.
- [ ] `site/content/site_extras.yaml` exists.

After this plan, the SSOT data files exist and are validated, but no consumer code has been wired up to them yet. **Plan B** (reverse generators) and **Plan C** (page.tsx wiring) are the next two plans to make the SSOT the actual source of truth in production.
