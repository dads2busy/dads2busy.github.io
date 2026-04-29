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
- `scripts/profile_derive_lib.py` — pure title/category derivation from prose (maps 7 keywords to 6 canonical categories)
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
