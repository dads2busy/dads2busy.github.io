# Architecture Cleanup (Plan H) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the data-build layer vs. delivery layer separation explicit and testable.

1. Add a small reusable derivation library (`scripts/profile_derive_lib.py`) with `derive_title_from_content` and `derive_category_from_content` — pure parsing helpers the user invokes intentionally, never as runtime auto-magic.
2. Add a review tool (`scripts/fill_missing_fields.py`) that walks profile.yaml, finds blanks, and emits a markdown diff of proposed derivations for human review — same pattern as Plan G's CV analyzer and Plan E's ORCID diff.
3. Add shape-completeness tests to `scripts/tests/test_json_emitters.py` that catch key-rename regressions like the recent `title` → `name` bug.
4. Document the architecture in `ARCHITECTURE.md` so the data-build / delivery split is visible and the pattern is easy to extend.

**Architecture principle this enforces:** profile.yaml is the SSOT. Helpers that compute derived values run intentionally (for retroactive fills or as candidates during ingest review) and persist their results into profile.yaml. The delivery layer never derives — it only renders what's in the SSOT.

**Tech stack:** No new deps. Python 3.14, pyyaml, pytest — all existing.

**Out of scope:**
- `derive_sponsor_from_content` — too fragile; the venue/sponsor is hard to extract from free-form citation text without false positives. Defer until we hit a concrete need.
- Refactoring Plan G's analyzer or Plan E's ORCID diff to use this library — they use LLM extraction and structured ORCID JSON respectively, neither of which needs prose parsing.
- Per-field delivery template overrides beyond what RenderCV / React components already provide.

---

## File Structure

**Create:**
- `scripts/profile_derive_lib.py` — Pure functions: `derive_title_from_content(text) -> str | None` and `derive_category_from_content(text) -> str | None`.
- `scripts/tests/test_profile_derive_lib.py` — pytest tests.
- `scripts/fill_missing_fields.py` — Walks `site/content/profile.yaml` Presentations section, computes proposed derivations for entries with blank/default fields, writes `profile_fill_diff.md`. Never edits profile.yaml.
- `ARCHITECTURE.md` (repo root) — documents data-build vs delivery layers and where each function lives.

**Modify:**
- `scripts/tests/test_json_emitters.py` — add per-emitter shape-completeness tests.
- `.gitignore` — add `profile_fill_diff.md`.

---

## Task 1: profile_derive_lib (TDD)

**Files:**
- Create: `scripts/profile_derive_lib.py`
- Create: `scripts/tests/test_profile_derive_lib.py`

Two pure functions:
- `derive_title_from_content(content: str) -> str | None` — extract a candidate title from a citation-style content field. Looks for two patterns:
  1. `<Category>: "Quoted Title"` → return the quoted text
  2. `<Category>: Bare Title Text.` → return text between the colon and the next period
  Returns `None` if no candidate found.
- `derive_category_from_content(content: str) -> str | None` — same logic the runtime derivation used (now removed). Looks for `\b<Category>\s*:` for each of the 7 valid speaking categories. Returns the first match, or `None` if no match.

Neither function applies a default — the caller decides what to do with `None` (e.g. `fill_missing_fields.py` reports the blank for manual review).

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_profile_derive_lib.py`:
```python
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
    s = 'Schroeder, A.D. Lecture: “Smart Quote Title” (2023), Venue.'
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


def test_category_workshop():
    s = "Schroeder, A.D. Workshop: ITSVA Annual Conference."
    assert derive_category_from_content(s) == "Workshop"


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
    order wins (Panelist before Presentation, etc.)."""
    s = "Discussed at Panelist: Topic A. Followed by Lecture: Topic B."
    assert derive_category_from_content(s) == "Panelist"
```

`scripts/profile_derive_lib.py` (stubs):
```python
def derive_title_from_content(content: str) -> str | None:
    raise NotImplementedError


def derive_category_from_content(content: str) -> str | None:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 16 fail**

```bash
.venv/bin/pytest scripts/tests/test_profile_derive_lib.py -v
```

Expected: 16 failures.

- [ ] **Step 3: Implement**

Replace stubs in `scripts/profile_derive_lib.py`:
```python
import re

CATEGORIES = (
    "Panelist", "Presentation", "Committee", "Lecture",
    "Expert Forum", "Expert Webinar", "Workshop",
)

# Title: <Category>: <captured>  where captured is either:
#   1. text in straight or smart double quotes
#   2. bare text up to the next period
_TITLE_PATTERNS = [
    # Quoted (straight or smart quotes)
    re.compile(
        r"\b(?:" + "|".join(re.escape(c) for c in CATEGORIES) + r")\s*:\s*[\"“”]([^\"“”]+)[\"“”]",
    ),
    # Bare up to period
    re.compile(
        r"\b(?:" + "|".join(re.escape(c) for c in CATEGORIES) + r")\s*:\s*([^.]+?)\.",
    ),
]


def derive_title_from_content(content: str) -> str | None:
    """Extract a candidate title from a category-prefixed citation string.

    Tries quoted form first, then bare-until-period. Returns None if no match.
    """
    if not content:
        return None
    for pat in _TITLE_PATTERNS:
        m = pat.search(content)
        if m:
            return m.group(1).strip()
    return None


def derive_category_from_content(content: str) -> str | None:
    """Return the first category keyword that appears as `<cat>:` in the content."""
    if not content:
        return None
    for cat in CATEGORIES:
        if re.search(rf"\b{re.escape(cat)}\s*:", content):
            return cat
    return None
```

- [ ] **Step 4: Run tests, confirm all 16 pass**

```bash
.venv/bin/pytest scripts/tests/test_profile_derive_lib.py -v
```

Expected: 16 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_derive_lib.py scripts/tests/test_profile_derive_lib.py
git commit -m "feat(scripts): profile_derive_lib (title + category derivation from content)"
```

---

## Task 2: fill_missing_fields review tool

**Files:**
- Create: `scripts/fill_missing_fields.py`
- Modify: `.gitignore`

A read-only review tool. Walks `site/content/profile.yaml`'s `Presentations` section, finds entries with empty `name` or default-bucket `subcategory: Presentations/Workshops`, and emits `profile_fill_diff.md` listing proposed derivations for human review. The user reads the diff and hand-applies acceptable proposals via Edit. **The script never writes to profile.yaml.**

- [ ] **Step 1: Create the script**

`scripts/fill_missing_fields.py`:
```python
#!/usr/bin/env python3
"""Review tool: propose derived title/category for incomplete profile.yaml entries.

Walks the Presentations section, finds entries with empty `name` or with
`subcategory: Presentations/Workshops` (the legacy default bucket), runs the
derivation library on each entry's `content`, and emits a markdown diff.

The script NEVER writes to profile.yaml. Review the diff and hand-apply
acceptable proposals via your editor.

Run from repo root:
    .venv/bin/python scripts/fill_missing_fields.py
"""

import sys
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from profile_derive_lib import derive_category_from_content, derive_title_from_content

PROFILE_PATH = REPO_ROOT / "site" / "content" / "profile.yaml"
DIFF_PATH = REPO_ROOT / "profile_fill_diff.md"


def main() -> None:
    profile = yaml.safe_load(PROFILE_PATH.read_text())
    pres = profile["cv"]["sections"]["Presentations"]

    title_props: list[dict] = []
    category_props: list[dict] = []

    for entry in pres:
        content = entry.get("content") or ""
        date = entry.get("date", "?")
        slug = entry.get("slug", "?")

        if not entry.get("name"):
            proposed = derive_title_from_content(content)
            title_props.append({
                "date": date, "slug": slug, "proposed": proposed,
                "content": content[:140],
            })

        if (entry.get("subcategory") or "").strip() == "Presentations/Workshops":
            proposed = derive_category_from_content(content)
            if proposed:
                category_props.append({
                    "date": date, "slug": slug, "current": "Presentations/Workshops",
                    "proposed": proposed, "content": content[:140],
                })

    lines = [
        "# Profile Fill Diff",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        f"Source: {PROFILE_PATH.relative_to(REPO_ROOT)}",
        f"Total Presentations: {len(pres)}",
        "",
        f"## Title proposals ({len(title_props)} entries with empty name)",
        "",
    ]
    if not title_props:
        lines.append("_All entries have a name — nothing to propose._")
    for p in title_props:
        marker = "✓" if p["proposed"] else "?"
        lines.append(f"### {marker} date={p['date']} slug={p['slug']}")
        lines.append("")
        lines.append(f"**Content:** `{p['content']}...`")
        lines.append("")
        if p["proposed"]:
            lines.append(f"**Proposed name:** `{p['proposed']}`")
        else:
            lines.append("**No automatic derivation available.** Manually choose a title.")
        lines.append("")

    lines.extend([
        f"## Category proposals ({len(category_props)} entries currently 'Presentations/Workshops')",
        "",
    ])
    if not category_props:
        lines.append("_No legacy-bucket entries with a derivable category._")
    for p in category_props:
        lines.append(f"- date={p['date']} slug={p['slug']} → **{p['proposed']}**")
        lines.append(f"  `{p['content']}...`")

    DIFF_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {DIFF_PATH.relative_to(REPO_ROOT)}")
    print(f"  Title proposals:    {len(title_props)}")
    print(f"  Category proposals: {len(category_props)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add output to gitignore**

Append to `.gitignore`:
```
# Profile fill review-diff (regenerate via fill_missing_fields.py)
profile_fill_diff.md
```

- [ ] **Step 3: Run the script and inspect the output**

```bash
cd /Users/ads7fg/git/dads2busy.github.io && .venv/bin/python scripts/fill_missing_fields.py
head -30 profile_fill_diff.md
```

Expected: 0 title proposals (we just titled all 30 untitled entries) AND a list of category proposals for any entries still in the legacy "Presentations/Workshops" bucket whose content suggests a more specific category (likely 0–5 entries).

- [ ] **Step 4: Commit**

```bash
git add scripts/fill_missing_fields.py .gitignore
git commit -m "feat(scripts): fill_missing_fields review tool for incomplete profile.yaml entries"
```

---

## Task 3: Shape-completeness tests for json_emitters

**Files:**
- Modify: `scripts/tests/test_json_emitters.py`

Add a test per emitter that asserts the EXACT set of keys in the output. This catches key-rename regressions like the `title` → `name` bug we just shipped.

- [ ] **Step 1: Add tests**

Append to `scripts/tests/test_json_emitters.py`:
```python
# ─── Shape-completeness tests ────────────────────────────────────────
# These tests pin the output key-set for each emitter. A renamed key
# causes a test failure here, catching regressions before the website breaks.

def test_publication_writing_shape_complete():
    """publication_entry_to_writing on a fully-populated entry must produce
    exactly these keys (the writing.json shape the website's content.ts expects)."""
    entry = {
        "title": "X", "authors": ["A", "B"], "date": "2023-01-01",
        "doi": "10.x/y", "journal": "J", "url": "http://example.com",
        "slug": "s", "subcategory": "Refereed Journal Articles",
        "content": "abstract", "editors": "ed", "pages": "1-10", "ordinal": "5",
    }
    out = publication_entry_to_writing(entry)
    expected = {
        "title", "authors", "date", "DOI", "sponsor", "website",
        "ordinal", "slug", "subcategory", "content", "editors", "pages",
    }
    assert set(out.keys()) == expected, (
        f"publication_entry_to_writing key drift: missing={expected - set(out)} extra={set(out) - expected}"
    )


def test_experience_working_shape_complete():
    entry = {
        "name": "X", "date": "2018-Present", "summary": "Role at Org",
        "content": "Description", "slug": "s", "subcategory": "current",
        "ordinal": "1",
    }
    out = experience_entry_to_working(entry)
    expected = {"title", "dates", "subtitle", "content", "ordinal", "slug", "subcategory"}
    assert set(out.keys()) == expected


def test_research_research_shape_complete():
    entry = {
        "name": "X", "date": "2020", "url": "http://x.com", "content": "abstract",
        "slug": "s", "subcategory": "Some Sub", "sponsor": "Sponsor X",
        "award": "$1000", "role": "PI", "ordinal": "3",
    }
    out = project_entry_to_research(entry)
    expected = {
        "title", "dates", "website", "content", "ordinal", "slug",
        "subcategory", "sponsor", "award", "role",
    }
    assert set(out.keys()) == expected


def test_presentation_speaking_shape_complete():
    entry = {
        "name": "X", "date": "2023-12-02", "content": "Speech text",
        "url": "http://x.com", "slug": "s", "subcategory": "Lecture",
        "sponsor": "Venue", "role": "speaker",
    }
    out = presentation_entry_to_speaking(entry)
    expected = {
        "title", "date", "content", "website", "slug", "subcategory",
        "sponsor", "role",
    }
    assert set(out.keys()) == expected, (
        f"presentation_entry_to_speaking key drift: missing={expected - set(out)} extra={set(out) - expected}"
    )


def test_teaching_teaching_shape_complete():
    entry = {
        "name": "X", "date": "2013-05-22", "url": "http://x.com",
        "content": "syllabus", "slug": "s",
    }
    out = teaching_entry_to_teaching(entry)
    expected = {"title", "date", "website", "content", "slug"}
    assert set(out.keys()) == expected
```

- [ ] **Step 2: Run tests**

```bash
.venv/bin/pytest scripts/tests/test_json_emitters.py -v 2>&1 | tail -10
```

Expected: all tests pass (the 5 new shape tests + the existing tests). If any FAIL because a key is unexpectedly present/absent, that's the genuine current emitter shape — update the test's `expected` set to match. The point is to PIN the current shape so future regressions surface.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/test_json_emitters.py
git commit -m "test(json_emitters): pin output key-set per emitter to catch rename regressions"
```

---

## Task 4: ARCHITECTURE.md

**Files:**
- Create: `ARCHITECTURE.md` (repo root)

Document the data-build vs delivery split. Future maintainers (and future-you) need to know which scripts write TO profile.yaml vs which read FROM it.

- [ ] **Step 1: Create the file**

`ARCHITECTURE.md`:
```markdown
# Architecture

This document describes the layered architecture of the website + vita pipeline.
The single source of truth (SSOT) is `site/content/profile.yaml`. Two layers of
code surround it:

- **Data-build layer**: tools that help you populate / curate profile.yaml
- **Delivery layer**: code that consumes profile.yaml to produce outputs
  (website pages, vita PDF)

Both layers are explicit and TESTABLE. Neither layer derives values at runtime
from outside profile.yaml; if a value is needed for an output, it must be
present in profile.yaml. (See "Why no runtime derivation" below.)

```
                                  Data-build layer (writes TO profile.yaml)
                                  ┌─────────────────────────────────────────┐
External sources                  │  scripts/analyze_sources.py     (Plan G) │
  CV / DOCX     ─────────────────▶│  scripts/orcid_works.py         (Plan E) │
  ORCID API                       │  scripts/fill_missing_fields.py (Plan H) │
                                  │                                          │
                                  │  All emit *review diffs* — never edit    │
                                  │  profile.yaml directly. Human reviews    │
                                  │  and pastes accepted entries.            │
                                  └─────────────────────────────────────────┘
                                                    │
                                                    ▼
                       ┌───────────────────────────────────────────┐
                       │       site/content/profile.yaml (SSOT)    │
                       │       site/content/site_extras.yaml        │
                       └───────────────────────────────────────────┘
                                                    │
                                  Delivery layer (reads FROM profile.yaml)
                                  ┌─────────────────────────────────────────┐
                                  │  scripts/profile_to_content_jsons.py    │
                                  │    + scripts/json_emitters.py           │
                                  │      → site/content/{writing,working,    │
                                  │         research,speaking,teaching}.json │
                                  │      → website pages render these       │
                                  │                                          │
                                  │  RenderCV (rendercv render)              │
                                  │      → site/public/vita.pdf              │
                                  │                                          │
                                  │  site/src/app/page.tsx                   │
                                  │      → home page (reads YAML directly)   │
                                  └─────────────────────────────────────────┘
```

## Data-build layer

Scripts that help populate or curate profile.yaml. They emit *review diffs*
(markdown files documenting proposed changes) and never auto-mutate the SSOT.

| Script                              | Purpose                                                           | Output             |
|-------------------------------------|-------------------------------------------------------------------|--------------------|
| `scripts/analyze_sources.py`        | LLM-assisted extractor for `sources/cvs/*.docx` (Plan G)         | `sources/_diff.md` |
| `scripts/orcid_works.py`            | Fetches ORCID API + diffs against profile.yaml (Plan E)          | `orcid_diff.md`    |
| `scripts/fill_missing_fields.py`    | Walks profile.yaml; proposes derivations for blank fields (Plan H)| `profile_fill_diff.md` |

Shared library:
- `scripts/profile_derive_lib.py` — pure title/category derivation from prose
- `scripts/analyzer_lib.py` — title normalization, profile-yaml entry extraction
- `scripts/orcid_diff_lib.py` — ORCID work-group → entry, diff bucketing

## SSOT

| File                               | Contains                                              |
|------------------------------------|-------------------------------------------------------|
| `site/content/profile.yaml`        | Canonical CV data (RenderCV format with custom keys)  |
| `site/content/site_extras.yaml`    | Website-only display fields (tagline, polymath callout)|

profile.yaml is the ONE place to edit a fact. site_extras.yaml is for
website-presentation-only fields that don't belong on a CV.

## Delivery layer

Code that produces outputs from profile.yaml. Each delivery has its own
schema/template — same source data, multiple presentations.

### Vita PDF
- `rendercv render site/content/profile.yaml` → `site/public/vita.pdf`
- Format controlled by RenderCV's theme + entry templates (currently `classic` theme).
- Runs in CI on every push (`.github/workflows/deploy.yml`).

### Website content pages (writing/working/research/speaking/teaching)
- `scripts/profile_to_content_jsons.py` (orchestrator) calls per-section
  emitters in `scripts/json_emitters.py`.
- Each emitter is a PURE FUNCTION that maps one profile.yaml entry to the
  shape the website's content loader (`site/src/lib/content.ts`) expects.
- Emitters: `publication_entry_to_writing`, `experience_entry_to_working`,
  `project_entry_to_research`, `presentation_entry_to_speaking`,
  `teaching_entry_to_teaching`.
- The 5 generated JSONs are gitignored build artifacts. Regenerated by
  `npm run dev` and `npm run build` via `predev` / `prebuild` npm scripts.
- Per-page JSX components (`SpeakingCitation`, `WritingCitation`, etc.)
  format the displayed citation — that's the per-page presentation layer.

### Home page
- `site/src/app/page.tsx` reads profile.yaml + site_extras.yaml directly via
  `js-yaml` at build time (Next.js server component).
- site_extras.yaml is validated by a Zod schema (`site/src/lib/site-extras-schema.ts`).
- Hardcoded JSX renders sections of the loaded YAML.

## Why no runtime derivation

We briefly had a runtime "derive category from content" helper inside the
JSON generator. It made profile.yaml's data state surprising: an entry
that read `subcategory: Presentations/Workshops` in profile.yaml could
appear under "Lecture" on the website because the generator scanned the
prose and re-categorized.

The fix: derive ONCE and persist into profile.yaml. The delivery layer
just renders what's there. If you want a value to show up, it has to be
visible in profile.yaml.

## Adding a new derivation

If you find yourself writing a function that computes a value from another
field, decide where it belongs:

1. **Build-time helper** (writes to profile.yaml after human review):
   add to `scripts/profile_derive_lib.py` and surface it via
   `scripts/fill_missing_fields.py` or one of the ingest scripts.
2. **Delivery-specific format** (transforms a profile.yaml value at output
   time, e.g., italicizing a date for the vita): put it inside the
   delivery's template/schema (RenderCV theme, `WritingCitation.tsx`, etc.).

If neither fits cleanly, the derivation is probably runtime auto-magic and
should be reconsidered.

## Adding a new delivery

To add a third delivery (e.g. LinkedIn paste view, Plan F):
1. Add a new pure function in a new module (or `json_emitters.py` if it
   produces a JSON-ish shape). Read profile.yaml; produce the desired output.
2. Wire it into the appropriate orchestrator (npm script, CI step, manual run).
3. Add shape-completeness tests like the ones in `test_json_emitters.py`.

The delivery's format/schema lives WITH the delivery code, not in
profile.yaml. profile.yaml stays format-neutral.
```

- [ ] **Step 2: Commit**

```bash
git add ARCHITECTURE.md
git commit -m "docs: ARCHITECTURE.md — data-build vs delivery layer split"
```

---

## Task 5: Final sanity sweep

- [ ] **Step 1: All tests pass**

```bash
.venv/bin/pytest scripts/tests/ -v 2>&1 | tail -3
```

Expected: 85 (existing) + 16 (Task 1) + 5 (Task 3) = 106 passed.

- [ ] **Step 2: Full pipeline still works**

```bash
.venv/bin/python scripts/profile_to_content_jsons.py
cd site && npm run build 2>&1 | tail -3
```

Expected: 5 JSONs regenerated; build succeeds with 341+ pages.

- [ ] **Step 3: rendercv still renders**

```bash
.venv/bin/rendercv render site/content/profile.yaml --output-folder rendercv_output 2>&1 | tail -3
```

Expected: PDF generated.

- [ ] **Step 4: Git status clean**

```bash
git status
```

Expected: clean (or only the user's CV file untracked).

---

## Acceptance Criteria

- [ ] `scripts/profile_derive_lib.py` exists with both `derive_title_from_content` and `derive_category_from_content`, all 16 tests passing
- [ ] `scripts/fill_missing_fields.py` runs, produces `profile_fill_diff.md` (gitignored)
- [ ] `scripts/tests/test_json_emitters.py` has shape-completeness tests for all 5 emitters
- [ ] `ARCHITECTURE.md` exists at repo root, accurately describes the layers
- [ ] All 106 pytest tests pass
- [ ] `npm run build` and `rendercv render` still work

After Plan H, the architecture is documented, the data-build/delivery split is enforced by tests, and the user has a reusable workflow for retroactively filling missing profile.yaml fields. Plan F (LinkedIn paste view) remains the last open plan.
