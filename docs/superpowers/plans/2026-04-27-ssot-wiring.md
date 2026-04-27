# SSOT Wiring (Plan B + C) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `site/content/profile.yaml` the actual SSOT for the live website.

**Two halves, one plan:**

- **Plan B (Tasks 1–7) — Reverse generators.** A new Python script (`scripts/profile_to_content_jsons.py`) reads `profile.yaml` and emits the 5 existing content JSONs (`writing.json`, `working.json`, `research.json`, `speaking.json`, `teaching.json`) in the exact shapes the site's `src/lib/content.ts` already expects. The 5 JSONs become build artifacts: gitignored, removed from git, regenerated on `npm run dev` and `npm run build` via npm pre-scripts.
- **Plan C (Tasks 8–11) — Home page wires to YAMLs.** `site/src/app/page.tsx` reads `profile.yaml` + `site_extras.yaml` at build time (server component) and replaces all hardcoded constants (education, honors, skills, bio paragraphs). A small Zod schema validates `site_extras.yaml`.

**Architecture:** Closes the SSOT loop. Currently `profile.yaml` is canonical but unused by the live site (the JSONs and page.tsx still hold parallel copies). After Plan B+C: the JSONs are derived; page.tsx reads profile.yaml directly. One source for every fact.

**Tech Stack:** Python 3.14 (existing), `pyyaml` (existing), `pytest` (existing). New JS deps: `js-yaml`, `@types/js-yaml`, `zod`. No changes to RenderCV / Anthropic / mammoth.

**Out of scope:**
- New website pages for the "Data & Software" section — that section stays in profile.yaml + vita only for now
- ORCID review-diff (Plan E), LinkedIn paste view (Plan F)
- RenderCV in CI (Plan D)

---

## File Structure

**Create:**
- `scripts/json_emitters.py` — Pure utility functions: per-section converters that turn a profile.yaml entry dict back into a writing.json / working.json / etc. entry dict. The inverse of Plan A's converters in `profile_lib.py`. No I/O. All testable.
- `scripts/profile_to_content_jsons.py` — Orchestrator. Reads `profile.yaml`, calls converters, writes 5 JSONs to `site/content/`.
- `scripts/tests/test_json_emitters.py` — pytest tests for the converters.
- `site/src/lib/site-extras-schema.ts` — Zod schema for `site_extras.yaml`.

**Modify:**
- `site/.gitignore` — Add `content/writing.json`, `content/working.json`, `content/research.json`, `content/speaking.json`, `content/teaching.json`.
- `site/package.json` — Add `predev` and `prebuild` scripts that run the generator, plus deps `js-yaml`/`@types/js-yaml`/`zod`.
- `site/src/app/page.tsx` — Replace `const SKILLS = [...]`, `const HONORS = [...]`, hardcoded education table, hardcoded bio paragraphs with reads from `profile.yaml` + `site_extras.yaml`.
- `site/content/site_extras.yaml` — Remove `research_focus_paragraphs` (now redundant with `cv.sections.Summary`).

**Delete from git (keep on disk regenerated):**
- `site/content/writing.json`, `working.json`, `research.json`, `speaking.json`, `teaching.json`.

---

## Task 1: Per-section JSON emitter utilities (TDD)

**Files:**
- Create: `scripts/json_emitters.py`
- Create: `scripts/tests/test_json_emitters.py`

Each emitter takes a profile.yaml entry dict and returns the corresponding shape used by the website's content.ts loader. The emitters are the inverse of Plan A's `profile_lib` converters but with three Plan-A-deferred concerns addressed:
- `ordinal` (string in profile.yaml due to RenderCV's int-rejection) → coerced back to int
- `local_path` custom key (added in Plan A's URL-or-local split) → restored to the website's `website` field
- `authors` (list with `**Schroeder, A.**` bolds) → joined to comma-separated string with `**` stripped (the website doesn't render markdown bolds in author lists)

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_json_emitters.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from json_emitters import (
    publication_entry_to_writing,
    experience_entry_to_working,
    project_entry_to_research,
    presentation_entry_to_speaking,
    teaching_entry_to_teaching,
)


def test_publication_basic():
    entry = {
        "title": "Census Curated Data Enterprise",
        "authors": ["Lancaster V", "Shipp S", "**Schroeder A**", "Mortveit H"],
        "date": "2023-01-01",
        "doi": "10.18130/ce97-sp05",
        "journal": "Proceedings of the Biocomplexity Institute",
        "slug": "census_curated_data_enterprise",
        "subcategory": "Research/Technical Reports",
        "ordinal": "0",
        "content": "Abstract...",
    }
    out = publication_entry_to_writing(entry)
    assert out["title"] == "Census Curated Data Enterprise"
    assert out["authors"] == "Lancaster V, Shipp S, Schroeder A, Mortveit H"
    assert out["date"] == "2023-01-01"
    assert out["DOI"] == "https://doi.org/10.18130/ce97-sp05"
    assert out["sponsor"] == "Proceedings of the Biocomplexity Institute"
    assert out["slug"] == "census_curated_data_enterprise"
    assert out["subcategory"] == "Research/Technical Reports"
    assert out["ordinal"] == 0  # int, not string
    assert out["content"] == "Abstract..."


def test_publication_local_path_to_website():
    """Plan A split website→local_path for non-http URLs; reverse here."""
    entry = {
        "title": "Old paper",
        "authors": ["Schroeder A"],
        "local_path": "/downloads/foo.pdf",
    }
    out = publication_entry_to_writing(entry)
    assert out["website"] == "/downloads/foo.pdf"


def test_publication_url_to_website():
    """When the entry has a real http URL, that goes to the 'website' field too."""
    entry = {
        "title": "Modern paper",
        "authors": ["Schroeder A"],
        "url": "https://example.com/paper.pdf",
    }
    out = publication_entry_to_writing(entry)
    assert out["website"] == "https://example.com/paper.pdf"


def test_publication_doi_unchanged_if_already_url():
    """Defensive: if a profile.yaml entry has a fully-qualified DOI, don't double-prefix."""
    entry = {
        "title": "Paper",
        "authors": ["Schroeder A"],
        "doi": "https://doi.org/10.1234/abc",
    }
    out = publication_entry_to_writing(entry)
    assert out["DOI"] == "https://doi.org/10.1234/abc"


def test_publication_omits_doi_field_when_absent():
    entry = {"title": "Paper", "authors": ["Schroeder A"]}
    out = publication_entry_to_writing(entry)
    assert "DOI" not in out or out["DOI"] == ""


def test_experience_basic():
    entry = {
        "name": "Associate Research Professor",
        "date": "2018-Present",
        "summary": "Research Associate Professor at SDAL",
        "slug": "associate-research-professor",
        "ordinal": "1",
        "content": "Description...",
    }
    out = experience_entry_to_working(entry)
    assert out["title"] == "Associate Research Professor"
    assert out["dates"] == "2018-Present"
    assert out["subtitle"] == "Research Associate Professor at SDAL"
    assert out["slug"] == "associate-research-professor"
    assert out["ordinal"] == 1
    assert out["content"] == "Description..."


def test_research_project_basic():
    entry = {
        "name": "ATIS Implementation Center",
        "date": "2004-2005",
        "summary": "U.S. DOT — $543,000 (Co-PI)",
        "slug": "atis_rce",
        "subcategory": "Data Integration & Management",
        "ordinal": "9",
    }
    out = project_entry_to_research(entry)
    assert out["title"] == "ATIS Implementation Center"
    assert out["dates"] == "2004-2005"
    assert out["slug"] == "atis_rce"
    assert out["subcategory"] == "Data Integration & Management"
    assert out["ordinal"] == 9
    # `summary` is a derived field; not preserved as-is on the JSON side.
    # The site shows sponsor + award + role, which are stored as separate fields when present.


def test_research_project_preserves_award_field():
    """Recent CV-review additions added 'award' as a top-level field — preserve it."""
    entry = {
        "name": "VDH Data Commons",
        "date": "2021-2024",
        "award": "$1,150,000",
        "summary": "Phase 1 & 2",
    }
    out = project_entry_to_research(entry)
    assert out["award"] == "$1,150,000"


def test_presentation_basic():
    entry = {
        "name": "The Social Impact Data Commons",
        "date": "2023-12-02",
        "summary": "Lecture at COPAFS",
        "slug": "COPAFS",
        "subcategory": "Presentations/Workshops",
    }
    out = presentation_entry_to_speaking(entry)
    assert out["title"] == "The Social Impact Data Commons"
    assert out["date"] == "2023-12-02"
    assert out["slug"] == "COPAFS"
    assert out["subcategory"] == "Presentations/Workshops"


def test_teaching_basic():
    entry = {
        "name": "Administrative Data Systems & Technologies",
        "date": "2013-05-22",
        "slug": "data-systems",
    }
    out = teaching_entry_to_teaching(entry)
    assert out["title"] == "Administrative Data Systems & Technologies"
    assert out["date"] == "2013-05-22"
    assert out["slug"] == "data-systems"


def test_publication_strips_aaron_bold_in_authors_string():
    entry = {
        "title": "Paper",
        "authors": ["**Schroeder, A.D.**", "**Aaron Schroeder**", "Other, P."],
    }
    out = publication_entry_to_writing(entry)
    assert "**" not in out["authors"]
    assert out["authors"] == "Schroeder, A.D., Aaron Schroeder, Other, P."


def test_publication_ordinal_empty_string_omits_field():
    """profile.yaml may have ordinal="" for many entries; don't emit ordinal=0 by mistake."""
    entry = {"title": "Paper", "authors": ["X"], "ordinal": ""}
    out = publication_entry_to_writing(entry)
    assert "ordinal" not in out or out["ordinal"] == ""
```

`scripts/json_emitters.py` (stubs):
```python
def publication_entry_to_writing(entry: dict) -> dict:
    raise NotImplementedError


def experience_entry_to_working(entry: dict) -> dict:
    raise NotImplementedError


def project_entry_to_research(entry: dict) -> dict:
    raise NotImplementedError


def presentation_entry_to_speaking(entry: dict) -> dict:
    raise NotImplementedError


def teaching_entry_to_teaching(entry: dict) -> dict:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 13 fail**

```bash
.venv/bin/pytest scripts/tests/test_json_emitters.py -v
```

Expected: 13 failures, all `NotImplementedError`.

- [ ] **Step 3: Implement the converters**

Replace stubs in `scripts/json_emitters.py`:
```python
import re


def _strip_bold(s: str) -> str:
    """Remove markdown bold markers from an author name."""
    if s.startswith("**") and s.endswith("**"):
        return s[2:-2]
    return s


def _coerce_ordinal(val):
    """profile.yaml stores ordinal as a string (or empty); website expects int (or absent)."""
    if val in (None, ""):
        return ""
    try:
        return int(val)
    except (ValueError, TypeError):
        return val  # leave unchanged if non-numeric


def _website_field(entry: dict) -> str:
    """Recover the original website field from Plan A's url/local_path split."""
    return entry.get("url") or entry.get("local_path") or ""


def _doi_with_prefix(entry: dict) -> str:
    """profile.yaml stores bare DOI; the original writing.json had full URLs."""
    doi = entry.get("doi", "")
    if not doi:
        return ""
    if doi.startswith("http"):
        return doi
    return f"https://doi.org/{doi}"


def _passthrough(entry: dict, out: dict, keys: tuple) -> None:
    """Copy keys from entry to out only when present and non-None."""
    for k in keys:
        if k in entry and entry[k] is not None:
            out[k] = entry[k]


def publication_entry_to_writing(entry: dict) -> dict:
    """Inverse of profile_lib.writing_entry_to_publication."""
    out: dict = {
        "title": entry["title"],
        "authors": ", ".join(_strip_bold(a) for a in entry.get("authors", [])),
    }
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("journal"):
        out["sponsor"] = entry["journal"]
    doi = _doi_with_prefix(entry)
    if doi:
        out["DOI"] = doi
    website = _website_field(entry)
    if website:
        out["website"] = website
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(entry, out, ("slug", "subcategory", "content", "editors", "pages"))
    return out


def experience_entry_to_working(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["dates"] = entry["date"]
    if entry.get("summary"):
        out["subtitle"] = entry["summary"]
    if entry.get("content"):
        out["content"] = entry["content"]
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(entry, out, ("slug", "subcategory"))
    return out


def project_entry_to_research(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["dates"] = entry["date"]
    if entry.get("content"):
        out["content"] = entry["content"]
    if entry.get("url"):
        out["website"] = entry["url"]
    out["ordinal"] = _coerce_ordinal(entry.get("ordinal"))
    _passthrough(
        entry, out,
        (
            "slug", "subcategory",
            "sponsor", "award", "role",
            "report", "report2", "report3", "report4", "report5", "report6",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def presentation_entry_to_speaking(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("content"):
        out["content"] = entry["content"]
    if entry.get("url"):
        out["website"] = entry["url"]
    _passthrough(
        entry, out,
        (
            "slug", "subcategory",
            "sponsor", "role",
            "report",
            "media1", "media2", "media3",
            "media1title", "media2title", "media3title",
        ),
    )
    return out


def teaching_entry_to_teaching(entry: dict) -> dict:
    out: dict = {"title": entry["name"]}
    if entry.get("date"):
        out["date"] = entry["date"]
    if entry.get("content"):
        out["content"] = entry["content"]
    if entry.get("url"):
        out["website"] = entry["url"]
    _passthrough(entry, out, ("slug",))
    return out
```

- [ ] **Step 4: Run tests, confirm all 13 pass**

```bash
.venv/bin/pytest scripts/tests/test_json_emitters.py -v
```

Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/json_emitters.py scripts/tests/test_json_emitters.py
git commit -m "feat(scripts): per-section JSON emitters (profile.yaml entry → site JSON shape)"
```

---

## Task 2: Generator orchestrator script

**Files:**
- Create: `scripts/profile_to_content_jsons.py`

The orchestrator reads `profile.yaml`, dispatches each section to the appropriate emitter, and writes 5 JSONs. Sections in profile.yaml are mapped:

| profile.yaml section keys | Emitter | Output JSON | Site loader expectation |
|---|---|---|---|
| `Refereed Journal Articles`, `Book Chapters`, `Conference Proceedings / Presentations`, `Research / Technical Reports`, `Editorials`, `Dissertation` | `publication_entry_to_writing` | `writing.json` | flat list, each entry has `subcategory` |
| `Experience` | `experience_entry_to_working` | `working.json` | flat list |
| `Research Projects` | `project_entry_to_research` | `research.json` | flat list, each entry has `subcategory` |
| `Presentations` | `presentation_entry_to_speaking` | `speaking.json` | flat list |
| `Teaching` | `teaching_entry_to_teaching` | `teaching.json` | flat list |

Sections NOT mapped to any JSON (kept in profile.yaml only): `Summary`, `Education`, `Awards & Honors`, `Skills`, `Data & Software`. These are either consumed by `page.tsx` directly (handled in Plan C) or have no website page yet (Data & Software).

When a publication entry's profile.yaml subcategory section is `Refereed Journal Articles`, the generator must restore the original writing.json subcategory string `Journal Publications (refereed)` (Plan A's WRITING_SECTIONS map, inverted). Same for the other subcategory renames:

| profile.yaml section name | writing.json `subcategory` field value |
|---|---|
| `Refereed Journal Articles` | `Journal Publications (refereed)` |
| `Book Chapters` | `Book Chapters` |
| `Conference Proceedings / Presentations` | `Conference Proceedings/Presentations` |
| `Research / Technical Reports` | `Research/Technical Reports` |
| `Editorials` | `Editorials` |
| `Dissertation` | `Dissertation` |

- [ ] **Step 1: Write the orchestrator**

`scripts/profile_to_content_jsons.py`:
```python
#!/usr/bin/env python3
"""Generator: profile.yaml → site/content/{writing,working,research,speaking,teaching}.json.

Run from repo root:
    .venv/bin/python scripts/profile_to_content_jsons.py

Used as a pre-script by `npm run dev` and `npm run build` so the website's
content pages always reflect the SSOT.
"""

import json
from pathlib import Path

import yaml

from json_emitters import (
    experience_entry_to_working,
    presentation_entry_to_speaking,
    project_entry_to_research,
    publication_entry_to_writing,
    teaching_entry_to_teaching,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "site" / "content"
PROFILE_PATH = CONTENT_DIR / "profile.yaml"

# Inverse of Plan A's WRITING_SECTIONS — maps profile.yaml's section name to
# the original writing.json subcategory string.
WRITING_SUBCATEGORY = {
    "Refereed Journal Articles": "Journal Publications (refereed)",
    "Book Chapters": "Book Chapters",
    "Conference Proceedings / Presentations": "Conference Proceedings/Presentations",
    "Research / Technical Reports": "Research/Technical Reports",
    "Editorials": "Editorials",
    "Dissertation": "Dissertation",
}


def emit_writing(sections: dict) -> list[dict]:
    """All 6 publication-style sections flatten into one writing.json list."""
    out: list[dict] = []
    for section_name, json_subcategory in WRITING_SUBCATEGORY.items():
        for entry in sections.get(section_name, []) or []:
            converted = publication_entry_to_writing(entry)
            converted["subcategory"] = json_subcategory
            out.append(converted)
    return out


def emit_simple(sections: dict, profile_section: str, converter) -> list[dict]:
    return [converter(e) for e in sections.get(profile_section, []) or []]


def main() -> None:
    profile = yaml.safe_load(PROFILE_PATH.read_text())
    sections = profile["cv"]["sections"]

    outputs = {
        "writing.json": emit_writing(sections),
        "working.json": emit_simple(sections, "Experience", experience_entry_to_working),
        "research.json": emit_simple(sections, "Research Projects", project_entry_to_research),
        "speaking.json": emit_simple(sections, "Presentations", presentation_entry_to_speaking),
        "teaching.json": emit_simple(sections, "Teaching", teaching_entry_to_teaching),
    }

    for name, data in outputs.items():
        path = CONTENT_DIR / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)}: {len(data)} entries")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the generator (with the existing JSONs still in place; we'll diff against them)**

```bash
.venv/bin/python scripts/profile_to_content_jsons.py
```

Expected output (counts):
```
Wrote site/content/writing.json: ~64 entries  (61 original + 5 new from CV review - some merged)
Wrote site/content/working.json: 8 entries
Wrote site/content/research.json: ~36 entries  (35 original + adjustments)
Wrote site/content/speaking.json: ~56 entries  (34 original + 22 new from CV)
Wrote site/content/teaching.json: 4 entries
```

If counts wildly differ, investigate before proceeding.

- [ ] **Step 3: Diff against the previously committed JSONs**

```bash
git diff --stat site/content/writing.json site/content/working.json site/content/research.json site/content/speaking.json site/content/teaching.json
```

Expected: each JSON shows changes (additions for the new CV entries; possibly key-ordering or formatting differences). Read the diffs briefly to verify nothing important was LOST. Specifically check:
- writing.json still has 61+ entries with subcategory values matching the original strings
- speaking.json has more entries than before (the ~22 CV additions)
- ordinal fields are integers (not strings) where present
- DOI fields have full `https://doi.org/...` URLs (not bare `10.x/...`)

- [ ] **Step 4: Commit the generator**

```bash
git add scripts/profile_to_content_jsons.py
git commit -m "feat: profile_to_content_jsons.py generator (SSOT → 5 site JSONs)"
```

---

## Task 3: Verify website still renders against generated JSONs

This task confirms the generator's output is shape-compatible with `site/src/lib/content.ts` BEFORE we delete the committed JSONs.

- [ ] **Step 1: Build the site against the freshly-generated JSONs**

The generated JSONs are now at `site/content/*.json` (overwriting the previously-committed versions). Build:

```bash
cd site && npm run build 2>&1 | tail -10
```

Expected: 295 static pages, no errors. If a page fails to render or content.ts throws a type error, the generator's output is shape-incompatible — STOP and investigate.

- [ ] **Step 2: Spot-check a generated page**

Open `site/out/writing/index.html` (or any specific writing page) and confirm a recent publication appears.

```bash
grep -c "Census Curated Data Enterprise" site/out/writing/index.html
```

Expected: ≥ 1 (the publication is rendered on the writing index).

- [ ] **Step 3: Check a CV-added entry shows up**

```bash
grep -c "Annual Report: Leveraging Existing DoD Data" site/out/writing/index.html || echo "Not found — check generator output for that entry"
```

Expected: ≥ 1 (one of the 5 new Research/Technical Reports added during the CV review).

- [ ] **Step 4: No commit — this is verification only**

If all three steps pass, the generator output is good. Continue to Task 4.

---

## Task 4: Remove JSONs from git, gitignore, predev/prebuild scripts

**Files:**
- Modify: `site/.gitignore`
- Modify: `site/package.json`

After this task, the JSONs no longer live in git — they are regenerated on every `npm run dev` and `npm run build`.

- [ ] **Step 1: Add JSONs to site/.gitignore**

Append to `site/.gitignore`:
```
# Build artifacts: regenerated from ../site/content/profile.yaml by predev/prebuild
content/writing.json
content/working.json
content/research.json
content/speaking.json
content/teaching.json
```

- [ ] **Step 2: Add npm pre-scripts**

Read `site/package.json`. Find the `"scripts"` block. Add `predev` and `prebuild` entries (and a manual `gen:content` for ad-hoc use):

```json
  "scripts": {
    "predev": "cd .. && .venv/bin/python scripts/profile_to_content_jsons.py",
    "dev": "next dev",
    "prebuild": "cd .. && .venv/bin/python scripts/profile_to_content_jsons.py",
    "build": "next build",
    "gen:content": "cd .. && .venv/bin/python scripts/profile_to_content_jsons.py",
    "start": "next start",
    "lint": "eslint"
  }
```

(Preserve any other scripts that already exist; merge these into the block.)

- [ ] **Step 3: Remove JSONs from git tracking (keep on disk)**

```bash
git rm --cached site/content/writing.json site/content/working.json site/content/research.json site/content/speaking.json site/content/teaching.json
git status --short
```

Expected: 5 files staged for deletion. Filesystem still has the files (they're now gitignored).

- [ ] **Step 4: Verify gitignore catches them**

```bash
git status --short site/content/
```

Expected: ONLY `profile.yaml` and `site_extras.yaml` show as tracked. The 5 JSONs do NOT appear as untracked (gitignore is matching them).

- [ ] **Step 5: Test the pre-scripts work**

Delete the JSONs from disk and confirm `npm run build` regenerates them:

```bash
rm site/content/writing.json site/content/working.json site/content/research.json site/content/speaking.json site/content/teaching.json
cd site && npm run build 2>&1 | tail -5
ls site/content/*.json
```

Expected: prebuild regenerates the 5 JSONs, build succeeds, all 5 JSONs exist after.

- [ ] **Step 6: Commit**

```bash
git add site/.gitignore site/package.json site/content/writing.json site/content/working.json site/content/research.json site/content/speaking.json site/content/teaching.json
git commit -m "feat: content JSONs become build artifacts; npm pre-scripts run generator

The 5 content JSONs (writing, working, research, speaking, teaching) are
now gitignored and regenerated from profile.yaml on every npm run dev
and npm run build. Removes drift surface — profile.yaml is the SSOT.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

(The `git add` of the 5 JSONs records their deletion from the index, since they're now gitignored.)

---

## Task 5: Verify clean state after Plan B

- [ ] **Step 1: All Python tests pass**

```bash
.venv/bin/pytest scripts/tests/ -v 2>&1 | tail -3
```

Expected: 75 passed (62 from prior + 13 new).

- [ ] **Step 2: Build still works**

```bash
cd site && npm run build 2>&1 | tail -3
```

Expected: 295 static pages, no errors.

- [ ] **Step 3: Git is clean**

```bash
git status
```

Expected: clean. `site/content/*.json` are not in tracked-modified, not in untracked. Only `profile.yaml`, `site_extras.yaml`, README.md show in `site/content/`.

End of Plan B. The site now reads from generated JSONs which are derived from `profile.yaml`. Continuing to Plan C.

---

## Task 6: Install JS deps for Plan C

**Files:**
- Modify: `site/package.json` (auto via npm install)

- [ ] **Step 1: Install js-yaml + zod + types**

```bash
cd site && npm install js-yaml zod && npm install --save-dev @types/js-yaml
```

Expected: `package.json` updated with three new entries. `package-lock.json` updated.

- [ ] **Step 2: Verify imports work**

```bash
cd site && npx tsc --noEmit -e "import yaml from 'js-yaml'; import { z } from 'zod'; console.log(typeof yaml.load, typeof z.object);"
```

(If `tsc` invocation is awkward, just confirm `node_modules/js-yaml` and `node_modules/zod` exist.)

- [ ] **Step 3: Commit**

```bash
git add site/package.json site/package-lock.json
git commit -m "chore: add js-yaml + zod for Plan C YAML loading"
```

---

## Task 7: site_extras.yaml Zod schema

**Files:**
- Create: `site/src/lib/site-extras-schema.ts`

A small Zod schema that validates `site_extras.yaml` at build time. Catches typos before they silently break a section.

- [ ] **Step 1: Write the schema**

`site/src/lib/site-extras-schema.ts`:
```ts
import { z } from "zod";

export const siteExtrasSchema = z.object({
  tagline: z.string(),
  description: z.string(),
  homepage_sections: z.array(z.string()),
  polymath_callout: z.object({
    wikipedia_def: z.string(),
    schroeder_def: z.string(),
  }),
});

export type SiteExtras = z.infer<typeof siteExtrasSchema>;
```

Note: `research_focus_paragraphs` is intentionally NOT in this schema. Plan C deletes that field from `site_extras.yaml` because the home page now reads the same content from `profile.yaml`'s `cv.sections.Summary`.

- [ ] **Step 2: Commit**

```bash
git add site/src/lib/site-extras-schema.ts
git commit -m "feat(site): add Zod schema for site_extras.yaml"
```

---

## Task 8: Wire page.tsx to read profile.yaml + site_extras.yaml

**Files:**
- Modify: `site/src/app/page.tsx`

The home page becomes a server component that loads both YAMLs at build time. All hardcoded constants are replaced with reads from these YAMLs.

The current `site/src/app/page.tsx` has:
- `const SKILLS = [14 strings]` → from `profile.cv.sections.Skills`
- `const HONORS = [13 objects with year + label]` → from `profile.cv.sections["Awards & Honors"]` (note: profile.yaml uses `details` not `year`)
- Education table (3 hardcoded `<div>` blocks) → from `profile.cv.sections.Education`
- "Research Focus" paragraphs (3 hardcoded `<p>`) → from `profile.cv.sections.Summary`
- Polymath callout text (2 paragraphs) → from `extras.polymath_callout`
- Tagline (currently in Sidebar's display, not page.tsx — but if anything references "Libération de Données" in page.tsx, drive it from `extras.tagline`)
- Bio header (name, title, email, division) → keep hardcoded (the values are already in `profile.cv.name` / `cv.email` but the surrounding markup is custom)

- [ ] **Step 1: Read current page.tsx**

```bash
wc -l site/src/app/page.tsx
```

(Sanity check that the file exists and is the expected ~220 lines.)

- [ ] **Step 2: Replace page.tsx**

Open `site/src/app/page.tsx` and apply these changes (use Edit tool, not Write, to preserve untouched formatting):

**A. Add imports + load both YAMLs at the top of the file (above the existing component):**

```ts
import fs from "fs";
import path from "path";
import yaml from "js-yaml";
import { siteExtrasSchema } from "@/lib/site-extras-schema";

type ProfileEducationEntry = {
  institution: string;
  area?: string;
  degree?: string;
  date?: string;
  highlights?: string[];
};

type ProfileAward = { label: string; details?: string };

type Profile = {
  cv: {
    name: string;
    email: string;
    sections: {
      Summary: string[];
      Education: ProfileEducationEntry[];
      Skills: string[];
      "Awards & Honors": ProfileAward[];
    };
  };
};

const profile = yaml.load(
  fs.readFileSync(path.join(process.cwd(), "content", "profile.yaml"), "utf8"),
) as Profile;

const extras = siteExtrasSchema.parse(
  yaml.load(
    fs.readFileSync(path.join(process.cwd(), "content", "site_extras.yaml"), "utf8"),
  ),
);

const summaryParagraphs = profile.cv.sections.Summary;
const educationEntries = profile.cv.sections.Education;
const awards = profile.cv.sections["Awards & Honors"];
const skills = profile.cv.sections.Skills;
```

**B. Delete the existing `const SKILLS = [...]` and `const HONORS = [...]` arrays** at the top of the file. They're replaced by `skills` and `awards` from above.

**C. In the JSX:**

- Replace `{SKILLS.map(...)}` with `{skills.map(...)}`.
- Replace `{HONORS.map((h, i) => ...)}` with `{awards.map((a, i) => ...)}` and inside, replace `h.label` with `a.label` and `h.year` with `a.details`.
- Replace the 3 hardcoded `<p className="biosketch">` paragraphs in the "Research Focus" panel with `{summaryParagraphs.map((p, i) => <p key={i} className="biosketch">{p}</p>)}`.
- Replace the hardcoded education `<div>` blocks (Virginia Tech, JMU, Delaware) with `{educationEntries.map(...)}` rendering institution, degree+area+date, and highlights.
- Replace the polymath callout's two hardcoded definitions with `{extras.polymath_callout.wikipedia_def}` and `{extras.polymath_callout.schroeder_def}`.

The exact JSX shape per Education entry should remain visually identical to the current rendering:
```tsx
<div className="p-5">
  <p className="font-semibold" style={{ color: "var(--accent)" }}>
    {edu.institution}
  </p>
  {(edu.degree || edu.area || edu.date) && (
    <p className="text-sm mt-1">
      {edu.degree}{edu.degree && edu.area ? ", " : ""}{edu.area}
      {edu.date ? ` · ${edu.date}` : ""}
    </p>
  )}
  {edu.highlights?.length && (
    <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
      {edu.highlights.join(" · ")}
    </p>
  )}
</div>
```

- [ ] **Step 3: Build and verify**

```bash
cd site && npm run build 2>&1 | tail -5
```

Expected: builds successfully. If TypeScript errors appear (e.g. type mismatch on the Profile shape), fix the type annotations to match the actual profile.yaml contents.

- [ ] **Step 4: Visually inspect the home page**

Start the dev server in the background and open the page:

```bash
cd site && npm run dev &
sleep 5
curl -s http://localhost:3000/ | grep -E "(Schroeder|Political Science|Member, iTHRIV|R · Python)" | head -5
kill %1
```

Expected output should show:
- "Schroeder" in the page (from name)
- "Political Science" (from the corrected education minor)
- "Member, iTHRIV Scientific Advisory Board" (one of the new awards added during CV review)
- Skills rendered (look for "R" or "Python")

If any of these don't appear, the wiring is incomplete or the YAML structure doesn't match what page.tsx expects.

- [ ] **Step 5: Commit**

```bash
git add site/src/app/page.tsx
git commit -m "feat(site): home page reads profile.yaml + site_extras.yaml at build time

Replaces the hardcoded SKILLS/HONORS/education/bio constants with reads
from the SSOT. Education minor correction (Political Science) and the
3 new awards (iTHRIV, Brookings, NSF MMS) now flow to the live site
via profile.yaml.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Drop redundant research_focus_paragraphs from site_extras.yaml

**Files:**
- Modify: `site/content/site_extras.yaml`

The home page's Research Focus panel now reads from `profile.cv.sections.Summary` (Task 8). The `research_focus_paragraphs` field in `site_extras.yaml` is no longer consumed by anything.

- [ ] **Step 1: Remove the section**

Read `site/content/site_extras.yaml`. Delete the entire `research_focus_paragraphs:` block (the key plus its 3-string list and the comment block above it that explains the duplication).

- [ ] **Step 2: Verify schema still validates**

```bash
cd site && .venv/bin/python -c "import yaml; print(list(yaml.safe_load(open('content/site_extras.yaml')).keys()))" || cd /Users/ads7fg/git/dads2busy.github.io && .venv/bin/python -c "import yaml; print(list(yaml.safe_load(open('site/content/site_extras.yaml')).keys()))"
```

Expected: `['tagline', 'description', 'homepage_sections', 'polymath_callout']` (no `research_focus_paragraphs`).

- [ ] **Step 3: Build still works**

```bash
cd site && npm run build 2>&1 | tail -3
```

Expected: 295 static pages, no Zod validation errors.

- [ ] **Step 4: Commit**

```bash
git add site/content/site_extras.yaml
git commit -m "chore(site_extras): drop research_focus_paragraphs (now read from profile.yaml Summary)"
```

---

## Task 10: Verify cv-review additions show on the live site

This is the user-facing acceptance gate. Confirms that the SSOT loop is closed end-to-end: a change to `profile.yaml` (like the CV review additions) flows through the generators to the JSONs to the rendered pages.

- [ ] **Step 1: Check writing page shows new Research/Technical Reports entries**

```bash
cd site && npm run build 2>&1 | tail -3
grep -c "Annual Report: Leveraging Existing DoD Data" site/out/writing/index.html
grep -c "CoreLogic" site/out/writing/index.html
```

Expected: ≥ 1 each (the 2 new reports show).

- [ ] **Step 2: Check speaking page shows new presentations**

```bash
grep -c "BigSurv23" site/out/speaking/index.html
grep -c "JSM 2022" site/out/speaking/index.html
```

Expected: ≥ 1 each.

- [ ] **Step 3: Check home page shows new awards**

```bash
grep -c "iTHRIV Scientific Advisory Board" site/out/index.html
grep -c "Brookings Institute Consulting Scholar" site/out/index.html
grep -c "Political Science" site/out/index.html
```

Expected: ≥ 1 each.

If any of these fail, the SSOT-to-website flow has a bug. Investigate before declaring done.

---

## Task 11: Final sanity sweep

- [ ] **Step 1: All tests pass**

```bash
.venv/bin/pytest scripts/tests/ -v 2>&1 | tail -3
```

Expected: 75 passed.

- [ ] **Step 2: Generators are idempotent**

```bash
.venv/bin/python scripts/profile_to_content_jsons.py
git status site/content/
```

Expected: re-running the generator produces no diff (after the previous prebuild already wrote them). The 5 JSONs do not appear in `git status` because they're gitignored.

- [ ] **Step 3: Build is clean**

```bash
cd site && npm run build 2>&1 | tail -3
```

Expected: 295 static pages.

- [ ] **Step 4: rendercv still renders profile.yaml**

```bash
.venv/bin/rendercv render site/content/profile.yaml --output-folder rendercv_output 2>&1 | tail -5
ls -la rendercv_output/*.pdf
```

Expected: PDF generated, > 200 KB.

- [ ] **Step 5: Final git status check**

```bash
git status
```

Expected: clean (nothing modified, nothing untracked except possibly the user's CV in sources/cvs/).

---

## Acceptance Criteria

- [ ] `scripts/profile_to_content_jsons.py` regenerates all 5 content JSONs from `profile.yaml` deterministically
- [ ] The 5 content JSONs are gitignored and not tracked
- [ ] `npm run dev` and `npm run build` both run the generator before starting (predev/prebuild)
- [ ] `site/src/app/page.tsx` no longer has hardcoded `SKILLS`, `HONORS`, education, or bio constants
- [ ] The live home page shows the 3 new CV-review awards (iTHRIV, Brookings, NSF MMS)
- [ ] The /writing page shows the 5 new Research/Technical Reports
- [ ] The /speaking page shows the ~22 new Presentations
- [ ] University of Delaware shows "Minor in Political Science" (not Statistics)
- [ ] All 75 pytest tests pass
- [ ] `rendercv render` still produces a valid PDF
- [ ] `npm run build` produces 295 static pages with no errors

After Plan B+C, the SSOT loop is closed: a change to `profile.yaml` propagates to BOTH the rendered website (via generators) AND the vita PDF (via RenderCV). Plans D, E, F remain.
