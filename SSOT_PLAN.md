# Single Source of Truth (SSOT) — Professional Information Architecture

**Project**: dads2busy.github.io
**Owner**: Aaron D. Schroeder, Ph.D.
**Created**: 2026-04-27
**Status**: Architecture finalized — implementation pending

---

## Goal

One canonical source of professional data that drives:

1. The personal academic website (dads2busy.github.io)
2. The curriculum vitae PDF, generated via [RenderCV](https://github.com/rendercv/rendercv)
3. A Markdown / text view suitable for hand-copying into LinkedIn (no public LinkedIn write API exists for free profile updates, so this output is for manual paste, not automation)

One edit to `profile.yaml` propagates to all three outputs.

---

## Architectural Pattern

Standard data-as-SSOT discipline:

- Humans own the canonical facts in YAML and the existing content JSONs.
- Tooling (Next.js, RenderCV) renders those facts into outputs.
- LLMs may help draft prose *into* the YAML, but never act as the canonical store.

```
LAYER 0 — Sources (raw artifacts you drop in for analysis)
  sources/
    cvs/                         old vitae (PDF, DOC, etc.)
    publications/                old publication PDFs / preprints
    talks/                       old talk decks, abstracts
    raw/                         unsorted dumps
  scripts/analyze_sources.py     LLM-assisted extractor — reads sources/,
                                 emits proposed YAML diffs for human review
                                 NEVER edits profile.yaml directly.

LAYER 1 — Source of Truth (you edit these)
  site/content/profile.yaml      identity, summary, education, experience,
                                 publications, research projects,
                                 presentations, teaching, awards, skills
                                 (RenderCV format with arbitrary custom keys)
  site/content/site_extras.yaml  website-only fields (homepage section order,
                                 polymath callout, tagline)
  orcid_works.json               STAGING ONLY — produced by orcid_works.py;
                                 review diffs and manually merge new pubs
                                 into profile.yaml. NEVER auto-mutates the SSOT.

LAYER 2 — Outputs (all derived from Layer 1)
  2a. Website:
        pre-build: scripts/profile_to_content_jsons.py
                   reads profile.yaml → emits site/content/{writing,working,
                   research,speaking,teaching}.json
        build:     Next.js reads profile.yaml + site_extras.yaml +
                   the generated content JSONs → static site
  2b. Vita:
        rendercv render site/content/profile.yaml --output-folder site/public
        → site/public/vita.pdf → served at /vita.pdf
  2c. LinkedIn:
        scripts/profile_to_markdown.py → linkedin_view.md
        → manual copy/paste into LinkedIn

LAYER 3 — Automation (GitHub Actions)
  git push master:
    1. python scripts/profile_to_content_jsons.py       # SSOT → 5 content JSONs
    2. rendercv render site/content/profile.yaml ...    # SSOT → vita.pdf
    3. cd site && npm ci && npm run build               # → out/
    4. Deploy out/ to GitHub Pages
  No commits back to the repo. All content JSONs and vita.pdf are build artifacts.
```

---

## File Structure (Target State)

```
dads2busy.github.io/
  CLAUDE.md
  SSOT_PLAN.md                        this file
  orcid_works.py                      existing — fetches publications from ORCID API
  orcid_works.json                    STAGING — review diffs, merge into profile.yaml
  sources/                            NEW — drop-zone for raw artifacts to analyze
    README.md                         workflow explanation
    cvs/        publications/         talks/        raw/
  scripts/
    migrate_to_profile.py             ONE-TIME — seeds profile.yaml from existing JSONs
    profile_to_content_jsons.py       NEW — emits all 5 content JSONs from profile.yaml
    profile_to_markdown.py            NEW — emits LinkedIn-paste view from profile.yaml
    analyze_sources.py                NEW (future) — LLM-assisted extractor for sources/
  site/
    content/
      profile.yaml                    NEW — SSOT (CREATE FIRST via migrate_to_profile.py)
      site_extras.yaml                NEW — site-only fields not modeled by RenderCV
      writing.json                    BUILD ARTIFACT — derived from profile.yaml
      working.json                    BUILD ARTIFACT — derived from profile.yaml
      research.json                   BUILD ARTIFACT — derived from profile.yaml
      speaking.json                   BUILD ARTIFACT — derived from profile.yaml
      teaching.json                   BUILD ARTIFACT — derived from profile.yaml
    src/app/
      page.tsx                        UPDATE — read both YAMLs at build time
    public/
      vita.pdf                        BUILD ARTIFACT — gitignored, regenerated on each deploy
  .github/workflows/deploy.yml        UPDATE — add profile-to-jsons + RenderCV steps
```

---

## Step-by-Step Implementation Plan

### Step 1 — Seed `site/content/profile.yaml` via one-time migration script

`profile.yaml` follows the [RenderCV YAML schema](https://docs.rendercv.com). RenderCV validates it on render, so schema correctness is enforced for free. RenderCV also accepts arbitrary custom keys per entry (`slug`, `ordinal`, `editors`, `pages`, `content`, etc.) — these are preserved on each entry for the website's content-JSON generator and ignored by the default vita rendering.

A one-time `scripts/migrate_to_profile.py` reads ALL existing JSONs and emits the bulk of profile.yaml:
- `writing.json` (61 pubs) → publication sections grouped by subcategory
- `working.json` (8 positions) → `experience` section
- `research.json` (35 projects) → `research_projects` section
- `speaking.json` (34 talks) → `presentations` section
- `teaching.json` (4 courses) → `teaching` section

Identity, summary, education, awards/honors, and skills are encoded as constants in the migration script (small, hand-curated from the current home page).

Author parsing: comma/and-split with heuristics; Aaron Schroeder name variants are bolded with `**...**`. Ambiguous splits get a `# TODO: review` comment in the YAML output.

Section structure:

```yaml
cv:
  name: Aaron D. Schroeder
  email: aaron.schroeder@virginia.edu
  social_networks: [...]
  sections:
    Summary: [...]
    Education: [...]
    Experience: [...]                              # from working.json
    "Research Projects": [...]                     # from research.json
    "Presentations": [...]                         # from speaking.json
    "Teaching": [...]                              # from teaching.json
    "Refereed Journal Articles": [...]             # from writing.json subcat
    "Research / Technical Reports": [...]          #  ...
    "Book Chapters": [...]                         #  ...
    "Conference Proceedings / Presentations": [...] # ...
    "Editorials": [...]                            #  ...
    "Dissertation": [...]                          #  ...
    "Awards & Honors": [...]
    "Skills": [...]
design:
  theme: classic        # final theme TBD via Step 3 preview
```

Migration script is throwaway after Step 1 — but committed to the repo so the migration is reproducible/auditable.

`site_extras.yaml` holds the website-only bits RenderCV doesn't model:

```yaml
tagline: "Libération de Données!"
homepage_sections: [hero, research_focus, education_skills, honors, polymath]
polymath_callout:
  wikipedia_def: "..."
  schroeder_def: "..."
research_focus_paragraphs: [...]
```

Keep it small — anything that *is* CV content goes in profile.yaml.

For `site_extras.yaml`, add a 30-line Zod schema in `site/src/lib/site-extras-schema.ts` so a typo at edit time fails the build with a clear error rather than silently breaking a section.

### Step 2 — Update `site/src/app/page.tsx` to read both YAMLs

```bash
cd site && npm install js-yaml @types/js-yaml zod
```

Server component reads both files at build time:

```ts
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { siteExtrasSchema } from '@/lib/site-extras-schema';

const profile = yaml.load(fs.readFileSync(
  path.join(process.cwd(), 'content', 'profile.yaml'), 'utf8'
)) as RenderCVProfile;

const extras = siteExtrasSchema.parse(yaml.load(fs.readFileSync(
  path.join(process.cwd(), 'content', 'site_extras.yaml'), 'utf8'
)));
```

All hardcoded arrays in `page.tsx` (education, honors, skills, bio paragraphs) are replaced with `profile.cv.sections.*` references; site-chrome bits use `extras.*`.

No `..` path traversal — both YAMLs live inside `site/content/` next to the existing JSONs.

### Step 3 — Wire up RenderCV (replaces "write generate_vita.py")

No custom renderer needed. RenderCV is a mature OSS tool that takes YAML in, emits PDF out, with a half-dozen academic themes built in.

Local check:

```bash
pip install rendercv
rendercv render site/content/profile.yaml --output-folder site/public
# produces site/public/vita.pdf (and .html, .typ if desired — turn off in CLI flags)
```

Decide preferred theme by rendering 2–3 of the built-ins and picking one. Custom theme work is deferred until/unless the built-ins don't cut it.

Add `site/public/vita.pdf` to `site/.gitignore` — it's a build artifact, never committed.

### Step 4 — Update `.github/workflows/deploy.yml`

Add publications-to-writing-json + RenderCV steps before `npm run build`, so both build artifacts exist in `site/` when Next.js runs:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Install Python deps
  run: pip install rendercv pyyaml

- name: Generate writing.json from profile.yaml
  run: python scripts/publications_to_writing_json.py

- name: Render vita PDF
  run: rendercv render site/content/profile.yaml --output-folder site/public --pdf-only

- name: Build site
  working-directory: site
  run: npm ci && npm run build
```

No commit step. No git push from CI. Both `writing.json` and `vita.pdf` exist only inside the deployed `out/` directory.

### Step 5 — `scripts/publications_to_writing_json.py`

Reads `profile.yaml`, extracts the publication-style sections, and emits `site/content/writing.json` in the exact shape `site/src/lib/content.ts` already expects (subcategory + ordinal preserved). Site components don't change.

`writing.json` goes in `site/.gitignore`. Generator runs in CI before `npm run build`, and locally before `npm run dev` (add to a `predev` npm script).

### Step 6 — Update `orcid_works.py` to produce a review-friendly diff

Currently `orcid_works.py` writes `orcid_works.json` as a flat dump. Update it to:
- Compare against publications already in `profile.yaml`
- Emit a `orcid_works_new.json` containing only entries not yet in the SSOT
- Print a human-readable summary so you can review and paste into `profile.yaml`

`orcid_works.py` never edits `profile.yaml` directly. The SSOT is human-curated.

### Step 7 — `scripts/profile_to_markdown.py` (LinkedIn paste view)

Small Python script that reads `profile.yaml` and emits a `linkedin_view.md` formatted for LinkedIn's About / Experience fields. Run manually when you update LinkedIn — no CI step.

---

## Current Status

| Item                           | Status   | Notes                                                |
|--------------------------------|----------|------------------------------------------------------|
| Architecture design            | DONE     | This document                                        |
| `globals.css` redesign         | DONE     | Warm-navy-gold palette                               |
| `layout.tsx`, Navbar, Footer   | DONE     | Shipped 2026-04-27                                   |
| `page.tsx` redesign            | DONE     | Currently has data hardcoded; will move to YAML      |
| Content JSON migration (md→json) | DONE     | All 5 categories                                   |
| `profile.yaml` (RenderCV)        | PENDING  | Step 1 — includes publications as canonical        |
| `site_extras.yaml` + Zod         | PENDING  | Step 1                                             |
| `page.tsx` reads YAMLs           | PENDING  | Step 2                                             |
| RenderCV local rendering         | PENDING  | Step 3                                             |
| GitHub Actions pipeline          | PENDING  | Step 4 — pubs-to-json + RenderCV + build           |
| `publications_to_writing_json`   | PENDING  | Step 5 — generator; gitignore writing.json         |
| `orcid_works.py` review-diff     | PENDING  | Step 6 — emits new-only diff, never edits SSOT     |
| LinkedIn Markdown view script    | PENDING  | Step 7                                             |

---

## Design Decisions

- **profile.yaml uses RenderCV's schema directly** rather than a custom schema with an adapter. RenderCV validates on render; no two-schema drift problem.

- **Both YAMLs live in `site/content/`** alongside the existing content JSONs. Next.js reads them with no `..` traversal. The CI's RenderCV step reaches into `site/content/profile.yaml` — that's a build script, not user-facing, so the path isn't load-bearing UX.

- **`vita.pdf` is a build artifact, not a committed file.** Generated into `site/public/`, copied by Next.js into `out/`, deployed to Pages. No binary churn in git history, no CI commit-loop guards needed.

- **LinkedIn is a manual copy-paste flow.** No public free write API exists. Step 5 emits a Markdown view to make the paste mechanical, but the act is manual.

- **Schema validation:** RenderCV covers `profile.yaml`. A small Zod schema covers `site_extras.yaml`. Both fail the build loudly on typos rather than silently breaking a rendered section.

- **Publications are canonical in `profile.yaml`, not in `writing.json`.** SSOT discipline applies: the canonical source for any fact lives outside any specific publication artifact. `writing.json` becomes a build artifact derived from `profile.yaml`; the website's `/writing` page reads it unchanged. ORCID feeds *into* `profile.yaml` via human review — never auto-mutates the SSOT.

- **`research.json`, `speaking.json`, `teaching.json`, `working.json` remain hand-edited for now.** By the same SSOT logic they should also move into `profile.yaml` and become build artifacts, but each requires deciding which RenderCV section type fits and how the existing JSON shape is preserved. Defer this until after the publications pattern proves out — it's a natural follow-on, not part of this plan.
