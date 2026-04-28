# ORCID Review-Diff (Plan E) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `orcid_works.py` compare the publications it fetches from ORCID against the entries already in `site/content/profile.yaml` (the SSOT) and emit a markdown diff (`orcid_diff.md`) listing publications NOT yet in the SSOT, ready to paste in. The script never edits `profile.yaml` directly — the user is always in the loop.

**Architecture:** Extend the existing `orcid_works.py` (at repo root) with a diff stage. After fetching from ORCID, load `profile.yaml`, extract all publication titles, and bucket each ORCID work into "already-present" / "candidate-new" / "fuzzy-match-on-DOI" using normalized title matching. Re-uses `scripts/analyzer_lib.py`'s `normalize_title` and `extract_profile_titles` (built for Plan G's CV analyzer). Pure functions live in a new `scripts/orcid_diff_lib.py` for testability; the orchestration stays in `orcid_works.py`.

**Tech Stack:** Python 3.14, `pyyaml` (existing), `urllib` (existing in orcid_works.py). No new deps. Re-uses Plan G's `analyzer_lib`.

**Out of scope:**
- LLM-driven extraction — ORCID returns structured JSON; no LLM needed
- Auto-application of new pubs to profile.yaml — the diff is for human review only
- Plan F (LinkedIn paste view)

---

## File Structure

**Create:**
- `scripts/orcid_diff_lib.py` — Pure functions: `orcid_group_to_entry(group)` extracts (title, doi, year, journal, authors, type) from one ORCID work-group dict; `compute_diff(orcid_entries, profile_titles, profile_dois)` returns `(matched, new, fuzzy)` lists.
- `scripts/tests/test_orcid_diff_lib.py` — pytest tests with synthetic ORCID group dicts.

**Modify:**
- `orcid_works.py` (repo root) — Append diff stage after the existing fetch+dump+print: load profile.yaml, compute diff, emit `orcid_diff.md`, print summary counts.
- `.gitignore` — Add `orcid_diff.md`.
- `CLAUDE.md` — Update the "ORCID Integration" section to document the new diff workflow.

---

## Task 1: ORCID extraction + diff functions (TDD)

**Files:**
- Create: `scripts/orcid_diff_lib.py`
- Create: `scripts/tests/test_orcid_diff_lib.py`

The two pure functions:
- `orcid_group_to_entry(group: dict) -> dict | None` — pulls one ORCID work-group dict (with `external-ids` + `work-summary`) into a flat dict `{title, doi, year, journal, type}`. Returns `None` if the group has no `work-summary`. (Authors are NOT in ORCID's work-summary; they require a separate API call per work — out of scope for v1.)
- `compute_diff(orcid_entries, profile_titles, profile_dois) -> tuple[list, list, list]` — returns `(matched, new, fuzzy)`. An ORCID entry is "matched" if its normalized title is in `profile_titles` OR its DOI is in `profile_dois`. "fuzzy" if the DOI matches but the title differs (suggests stale metadata in profile.yaml). "new" otherwise.

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_orcid_diff_lib.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orcid_diff_lib import orcid_group_to_entry, compute_diff


SAMPLE_GROUP = {
    "external-ids": {
        "external-id": [
            {"external-id-type": "doi", "external-id-value": "10.18130/foo"},
        ],
    },
    "work-summary": [
        {
            "title": {"title": {"value": "Sample Paper Title"}},
            "type": "journal-article",
            "publication-date": {"year": {"value": "2023"}},
            "journal-title": {"value": "Some Journal"},
        },
    ],
}


def test_orcid_group_extracts_basic_fields():
    out = orcid_group_to_entry(SAMPLE_GROUP)
    assert out["title"] == "Sample Paper Title"
    assert out["doi"] == "10.18130/foo"
    assert out["year"] == "2023"
    assert out["journal"] == "Some Journal"
    assert out["type"] == "journal-article"


def test_orcid_group_handles_missing_doi():
    group = dict(SAMPLE_GROUP, **{"external-ids": {"external-id": []}})
    out = orcid_group_to_entry(group)
    assert out["doi"] is None


def test_orcid_group_handles_missing_journal():
    group_summary = {**SAMPLE_GROUP["work-summary"][0]}
    group_summary.pop("journal-title")
    group = {**SAMPLE_GROUP, "work-summary": [group_summary]}
    out = orcid_group_to_entry(group)
    assert out["journal"] is None


def test_orcid_group_handles_missing_pubdate():
    group_summary = {**SAMPLE_GROUP["work-summary"][0]}
    group_summary.pop("publication-date")
    group = {**SAMPLE_GROUP, "work-summary": [group_summary]}
    out = orcid_group_to_entry(group)
    assert out["year"] is None


def test_orcid_group_returns_none_when_empty_summary():
    group = {**SAMPLE_GROUP, "work-summary": []}
    assert orcid_group_to_entry(group) is None


def test_compute_diff_title_match():
    """Entry whose title is already in profile.yaml → matched."""
    orcid = [{"title": "Sample Paper Title", "doi": "10.x/new", "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Sample Paper Title")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
    assert len(fuzzy) == 0


def test_compute_diff_doi_match():
    """Entry whose DOI is in profile.yaml → matched (title may differ)."""
    orcid = [{"title": "ORCID Title v2", "doi": "10.x/abc", "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Old Title v1")}
    profile_dois = {"10.x/abc"}
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    # DOI match wins — counts as matched (fuzzy is reported separately because title also differs)
    assert len(matched) == 0
    assert len(fuzzy) == 1
    assert fuzzy[0]["title"] == "ORCID Title v2"


def test_compute_diff_new_entry():
    """Entry with neither title nor DOI in profile.yaml → new."""
    orcid = [{"title": "Brand New Paper", "doi": "10.x/new", "year": "2024", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Other Paper")}
    profile_dois = {"10.x/old"}
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 0
    assert len(new) == 1
    assert len(fuzzy) == 0
    assert new[0]["title"] == "Brand New Paper"


def test_compute_diff_title_match_normalizes():
    """Title match should ignore case + punctuation differences."""
    orcid = [{"title": "Sample paper title.", "doi": None, "year": "2023", "journal": "J", "type": "journal-article"}]
    profile_titles = {("Refereed Journal Articles", "Sample Paper Title")}
    profile_dois = set()
    matched, new, fuzzy = compute_diff(orcid, profile_titles, profile_dois)
    assert len(matched) == 1
    assert len(new) == 0
```

`scripts/orcid_diff_lib.py` (stubs):
```python
def orcid_group_to_entry(group: dict) -> dict | None:
    raise NotImplementedError


def compute_diff(orcid_entries, profile_titles, profile_dois):
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm 9 fail**

```bash
.venv/bin/pytest scripts/tests/test_orcid_diff_lib.py -v
```

Expected: 9 failures.

- [ ] **Step 3: Implement the functions**

Replace stubs in `scripts/orcid_diff_lib.py`:
```python
import sys
from pathlib import Path

# Re-use Plan G's analyzer_lib
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyzer_lib import normalize_title


def orcid_group_to_entry(group: dict) -> dict | None:
    """Extract {title, doi, year, journal, type} from one ORCID work-group dict.

    Returns None if the group has no work-summary.
    """
    summaries = group.get("work-summary", [])
    if not summaries:
        return None

    work = summaries[0]
    title_obj = work.get("title") or {}
    title = (title_obj.get("title") or {}).get("value") or ""

    pub_date = work.get("publication-date") or {}
    year_obj = pub_date.get("year") or {} if pub_date else {}
    year = year_obj.get("value") if year_obj else None

    journal_obj = work.get("journal-title")
    journal = journal_obj.get("value") if journal_obj else None

    ext_ids = (group.get("external-ids") or {}).get("external-id") or []
    doi = next(
        (eid["external-id-value"] for eid in ext_ids if eid.get("external-id-type") == "doi"),
        None,
    )

    return {
        "title": title,
        "doi": doi,
        "year": year,
        "journal": journal,
        "type": work.get("type", "unknown"),
    }


def compute_diff(orcid_entries, profile_titles, profile_dois):
    """Bucket ORCID entries against the SSOT.

    profile_titles: set of (section, title) tuples — Plan G's extract_profile_titles output
    profile_dois: set of bare DOI strings present in profile.yaml

    Returns (matched, new, fuzzy):
      - matched: title found in profile.yaml AND (no DOI OR DOI matches)
      - fuzzy:   DOI matches but title differs — stale metadata to flag for review
      - new:     neither title nor DOI in profile.yaml
    """
    profile_norm_titles = {normalize_title(t) for _, t in profile_titles}
    matched, new, fuzzy = [], [], []
    for entry in orcid_entries:
        title_in_profile = normalize_title(entry["title"]) in profile_norm_titles
        doi_in_profile = bool(entry["doi"]) and entry["doi"] in profile_dois

        if doi_in_profile and not title_in_profile:
            fuzzy.append(entry)
        elif title_in_profile or doi_in_profile:
            matched.append(entry)
        else:
            new.append(entry)
    return matched, new, fuzzy
```

- [ ] **Step 4: Run tests, confirm all 9 pass**

```bash
.venv/bin/pytest scripts/tests/test_orcid_diff_lib.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/orcid_diff_lib.py scripts/tests/test_orcid_diff_lib.py
git commit -m "feat(scripts): orcid_diff_lib — extract ORCID work-group + bucket vs SSOT"
```

---

## Task 2: Helper to extract profile.yaml DOIs

**Files:**
- Modify: `scripts/analyzer_lib.py` (append)
- Modify: `scripts/tests/test_analyzer_lib.py` (append)

`extract_profile_titles` (already in analyzer_lib) gives us titles. We also need a set of DOIs from the publication sections so `compute_diff` can match by DOI when titles differ.

- [ ] **Step 1: Add failing tests**

Append to `scripts/tests/test_analyzer_lib.py`:
```python
from analyzer_lib import extract_profile_dois


def test_extract_profile_dois_only_from_publication_sections():
    profile = {
        "cv": {
            "sections": {
                "Refereed Journal Articles": [
                    {"title": "Paper A", "doi": "10.x/a"},
                    {"title": "Paper B", "doi": "10.x/b"},
                    {"title": "Paper C"},  # no doi
                ],
                "Research / Technical Reports": [
                    {"title": "Report X", "doi": "10.x/x"},
                ],
                "Experience": [
                    # Has no doi field; extractor should skip
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
```

Add stub to `scripts/analyzer_lib.py`:
```python
def extract_profile_dois(profile: dict) -> set[str]:
    raise NotImplementedError
```

- [ ] **Step 2: Run tests, confirm new ones fail**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: 2 new failures (existing tests still pass).

- [ ] **Step 3: Implement**

Replace stub:
```python
_PUBLICATION_SECTIONS = {
    "Refereed Journal Articles",
    "Book Chapters",
    "Conference Proceedings / Presentations",
    "Research / Technical Reports",
    "Editorials",
    "Dissertation",
}


def extract_profile_dois(profile: dict) -> set[str]:
    """Set of bare DOI strings from profile.yaml's publication sections."""
    out: set[str] = set()
    sections = profile.get("cv", {}).get("sections", {})
    for section_name, entries in sections.items():
        if section_name not in _PUBLICATION_SECTIONS or not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("doi"):
                out.add(entry["doi"])
    return out
```

- [ ] **Step 4: Run tests, confirm all pass**

```bash
.venv/bin/pytest scripts/tests/test_analyzer_lib.py -v
```

Expected: total count goes up by 2 (was 17 + Plan G's; check whatever the current count was before).

- [ ] **Step 5: Commit**

```bash
git add scripts/analyzer_lib.py scripts/tests/test_analyzer_lib.py
git commit -m "feat(analyzer_lib): extract_profile_dois for ORCID DOI matching"
```

---

## Task 3: Wire orcid_works.py to emit the diff

**Files:**
- Modify: `orcid_works.py` (repo root)

Add a diff stage after the existing fetch+dump+print. The new code:
1. Loads `site/content/profile.yaml`
2. Extracts profile titles (analyzer_lib) and DOIs (Task 2)
3. Maps each ORCID work-group through `orcid_group_to_entry`
4. Calls `compute_diff` to bucket
5. Writes `orcid_diff.md` (markdown with three sections + ready-to-paste YAML for new entries)
6. Prints summary counts to stdout

- [ ] **Step 1: Read current orcid_works.py + plan exact insertion points**

Note: the existing `main()` ends with `print_works(data)`. The diff stage runs AFTER that.

- [ ] **Step 2: Add the diff logic**

At the top of `orcid_works.py`, add (after the existing imports):

```python
from datetime import datetime

# Re-use Plan G's analyzer_lib + Plan E's diff lib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from analyzer_lib import extract_profile_dois, extract_profile_titles  # noqa: E402
from orcid_diff_lib import compute_diff, orcid_group_to_entry  # noqa: E402
```

Add a new function before `main()`:

```python
def write_diff(orcid_data: dict, profile_path: str = "site/content/profile.yaml",
               diff_path: str = "orcid_diff.md") -> tuple[int, int, int]:
    """Compare ORCID works against profile.yaml; write markdown diff.

    Returns (matched_count, new_count, fuzzy_count).
    """
    import yaml
    profile = yaml.safe_load(open(profile_path).read())
    profile_titles = set(extract_profile_titles(profile))
    profile_dois = extract_profile_dois(profile)

    orcid_entries = [
        e for g in orcid_data.get("group", [])
        if (e := orcid_group_to_entry(g)) is not None
    ]
    matched, new, fuzzy = compute_diff(orcid_entries, profile_titles, profile_dois)

    lines = [
        f"# ORCID Sync Diff",
        f"",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        f"Source: ORCID ({len(orcid_entries)} work-groups)",
        f"SSOT: {profile_path} ({len(profile_titles)} titled entries, {len(profile_dois)} DOIs)",
        f"",
        f"## Summary",
        f"- ✓ {len(matched)} entries already in profile.yaml",
        f"- + {len(new)} candidate NEW entries (proposed YAML below)",
        f"- ~ {len(fuzzy)} fuzzy matches (DOI matches but title differs — review for stale metadata)",
        f"",
        f"## Already in profile.yaml ({len(matched)})",
    ]
    for e in matched:
        lines.append(f"- ✓ \"{e['title']}\"" + (f" (DOI: {e['doi']})" if e['doi'] else ""))

    lines.extend([f"", f"## Candidate NEW entries ({len(new)})", ""])
    for e in new:
        lines.append(f"### {e['title']} ({e['year'] or 'n.d.'})")
        lines.append(f"")
        lines.append(f"```yaml")
        lines.append(f"- title: \"{e['title']}\"")
        lines.append(f"  authors: []  # ORCID work-summary doesn't include authors; add by hand")
        if e['year']:
            lines.append(f"  date: \"{e['year']}\"")
        if e['doi']:
            lines.append(f"  doi: {e['doi']}")
        if e['journal']:
            lines.append(f"  journal: \"{e['journal']}\"")
        lines.append(f"```")
        lines.append(f"")

    lines.extend([f"## Fuzzy matches ({len(fuzzy)})", ""])
    for e in fuzzy:
        lines.append(f"- DOI `{e['doi']}` is in profile.yaml but the ORCID title differs:")
        lines.append(f"  - ORCID: \"{e['title']}\"")
        lines.append(f"")

    open(diff_path, "w").write("\n".join(lines) + "\n")
    return len(matched), len(new), len(fuzzy)
```

In `main()`, after the existing `print_works(data)` line, add:

```python
    matched, new, fuzzy = write_diff(data)
    print(f"\nWrote orcid_diff.md")
    print(f"  Already in SSOT: {matched}")
    print(f"  Candidate new:   {new}")
    print(f"  Fuzzy matches:   {fuzzy}")
```

- [ ] **Step 3: Verify import works**

```bash
.venv/bin/python -c "import orcid_works; print('OK')"
```

Expected: prints `OK` (no ImportError).

- [ ] **Step 4: Commit (no run yet — Task 4 runs end-to-end)**

```bash
git add orcid_works.py
git commit -m "feat(orcid): emit orcid_diff.md comparing ORCID works against profile.yaml SSOT"
```

---

## Task 4: Run end-to-end against real ORCID + gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add `orcid_diff.md` to gitignore (and orcid_works.json — ensure it's still committed because it's the live ORCID snapshot, but the new diff is throwaway)**

Actually `orcid_works.json` IS currently committed and acts as a record of the last ORCID sync. Leave it tracked. Just gitignore `orcid_diff.md`.

Append to `.gitignore`:
```
# ORCID review-diff (regenerate via orcid_works.py)
orcid_diff.md
```

- [ ] **Step 2: Run the script**

```bash
cd /Users/ads7fg/git/dads2busy.github.io && .venv/bin/python orcid_works.py
```

Expected:
- Authenticates with ORCID
- Fetches works (95 groups)
- Updates `orcid_works.json` (likely no change if ORCID hasn't been updated since last fetch)
- Prints `print_works` output (existing behavior)
- Writes `orcid_diff.md`
- Prints summary counts: matched, new, fuzzy

If ORCID auth fails (`ORCID_CLIENT_ID` / `ORCID_CLIENT_SECRET` issue), STOP — credentials may have changed.

- [ ] **Step 3: Inspect orcid_diff.md**

```bash
head -30 /Users/ads7fg/git/dads2busy.github.io/orcid_diff.md
wc -l /Users/ads7fg/git/dads2busy.github.io/orcid_diff.md
```

Expected: 3 sections (Already, NEW, Fuzzy). Total lines vary based on how many ORCID entries are missing from SSOT.

Sanity check: `matched` count should be substantial (most ORCID entries are already in SSOT after Plans A and the CV-review additions). `new` could be small (ORCID may have a few entries SSOT doesn't have, or vice versa).

- [ ] **Step 4: Commit gitignore (orcid_works.json may be modified if ORCID had updates; commit if so)**

```bash
git add .gitignore
git commit -m "chore: gitignore orcid_diff.md"

# If orcid_works.json was modified (ORCID had new data since last sync):
git diff --stat orcid_works.json
# if there are changes:
# git add orcid_works.json && git commit -m "chore: refresh orcid_works.json snapshot"
```

---

## Task 5: Document the workflow

**Files:**
- Modify: `CLAUDE.md`

The "ORCID Integration" section in CLAUDE.md currently describes only the fetch behavior. Update it to describe the new diff workflow.

- [ ] **Step 1: Find the ORCID Integration section**

```bash
grep -n "ORCID Integration" /Users/ads7fg/git/dads2busy.github.io/CLAUDE.md
```

- [ ] **Step 2: Replace the section**

Replace whatever is in the current "ORCID Integration" section with:

```markdown
## ORCID Integration

`orcid_works.py` (at repo root) does two things:

1. **Fetches** publications from the ORCID Public API using credentials in `.env`:
   ```
   ORCID_CLIENT_ID=APP-...
   ORCID_CLIENT_SECRET=...
   ORCID_ID=0000-0003-4372-2241   # or pass on CLI
   ```
   Output: `orcid_works.json` (committed snapshot of the last sync).

2. **Diffs** the fetched works against `site/content/profile.yaml` (the SSOT) and writes `orcid_diff.md` (gitignored) with three sections:
   - **Already in profile.yaml** — entries the SSOT and ORCID agree on
   - **Candidate NEW entries** — ORCID entries not yet in the SSOT, with ready-to-paste YAML
   - **Fuzzy matches** — DOI matches but title differs (stale SSOT metadata to review)

   Run: `.venv/bin/python orcid_works.py`
   
   Review `orcid_diff.md` and hand-paste accepted entries into `site/content/profile.yaml`. The script never edits `profile.yaml` directly.

Pure functions are in `scripts/orcid_diff_lib.py` with pytest coverage (`scripts/tests/test_orcid_diff_lib.py`).
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE): document ORCID review-diff workflow"
```

---

## Acceptance Criteria

- [ ] `.venv/bin/python orcid_works.py` runs end-to-end without error
- [ ] `orcid_diff.md` exists with three labeled sections
- [ ] Summary counts (matched / new / fuzzy) printed to stdout
- [ ] `scripts/tests/test_orcid_diff_lib.py` (9 tests) and the 2 new tests in `test_analyzer_lib.py` pass
- [ ] `orcid_diff.md` is gitignored
- [ ] CLAUDE.md describes the new workflow
- [ ] `npm run build` and `rendercv render` still work (no regression — Plan E doesn't touch the website or vita pipeline)

After Plan E: ORCID becomes a low-friction source of new publications. The user runs the script periodically, reviews the diff, and pastes accepted entries into `profile.yaml` — same review-loop pattern as Plan G's CV analyzer. Plan F (LinkedIn paste view) remains.
