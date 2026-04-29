# dads2busy.github.io

Personal academic portfolio website + curriculum vitae for **Aaron D. Schroeder, Ph.D.** — Research Associate Professor, [Social & Decision Analytics Division](https://www.bi.vt.edu/sdal), [University of Virginia Biocomplexity Institute](https://www.bi.vt.edu/).

🔗 **Live site:** [https://dads2busy.github.io](https://dads2busy.github.io)
📄 **Vita PDF:** [https://dads2busy.github.io/vita.pdf](https://dads2busy.github.io/vita.pdf)

---

## Architecture in 60 seconds

One YAML file is the single source of truth. Tooling renders it into multiple outputs.

```
                          Data-build layer (write to SSOT)
                          ┌───────────────────────────────────┐
External sources          │ scripts/analyze_sources.py        │ ← LLM-extracts CV/DOCX
  CV / DOCX     ─────────▶│ scripts/orcid_works.py            │ ← ORCID API + diff
  ORCID API               │ scripts/fill_missing_fields.py    │ ← propose blanks to fill
                          │   (all emit review diffs;          │
                          │    NEVER auto-edit profile.yaml)   │
                          └───────────────────────────────────┘
                                          │ human paste
                                          ▼
                         ┌───────────────────────────────────┐
                         │  site/content/profile.yaml (SSOT) │
                         │  site/content/site_extras.yaml    │
                         └───────────────────────────────────┘
                                          │
                          Delivery layer (read from SSOT)
                          ┌───────────────────────────────────┐
                          │ scripts/profile_to_content_jsons  │
                          │   → 5 site content JSONs           │
                          │   → website pages render            │
                          │                                    │
                          │ rendercv render → vita.pdf         │
                          │                                    │
                          │ site/src/app/page.tsx              │
                          │   → home page (reads YAML directly)│
                          └───────────────────────────────────┘
```

Full architecture details: see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## Where to make common changes

### Add or edit a publication
Edit [`site/content/profile.yaml`](./site/content/profile.yaml) — find the matching publication-style section (`Refereed Journal Articles`, `Book Chapters`, `Research / Technical Reports`, etc.) and add/edit the entry. Use the existing entries' shape as a template.

### Add or edit a presentation/talk
Edit [`site/content/profile.yaml`](./site/content/profile.yaml) — `Presentations:` section. Set `subcategory:` to one of: `Panelist`, `Presentations/Workshops`, `Committee`, `Lecture`, `Expert Forum`, `Expert Webinar`.

### Add or edit a research project
Edit [`site/content/profile.yaml`](./site/content/profile.yaml) — `Research Projects:` section. Fields: `name`, `funder`, `award`, `role`, `date`, `summary`, `slug`.

### Update bio / education / skills / awards (home page)
Edit [`site/content/profile.yaml`](./site/content/profile.yaml) — `Summary`, `Education`, `Skills`, `Awards & Honors` sections. The home page reads these directly via `js-yaml` at build time.

### Update tagline or polymath callout
Edit [`site/content/site_extras.yaml`](./site/content/site_extras.yaml). Validated by a Zod schema at [`site/src/lib/site-extras-schema.ts`](./site/src/lib/site-extras-schema.ts).

### Change presentation category order on `/speaking`
Edit `CATEGORY_ORDER` in [`site/src/app/speaking/page.tsx`](./site/src/app/speaking/page.tsx).

### Change citation rendering
- Publications: [`site/src/components/WritingCitation.tsx`](./site/src/components/WritingCitation.tsx)
- Presentations: [`site/src/components/SpeakingCitation.tsx`](./site/src/components/SpeakingCitation.tsx)
- Research projects: [`site/src/components/ResearchPost.tsx`](./site/src/components/ResearchPost.tsx)

### Change vita PDF look
Edit `design.theme:` in `profile.yaml` (currently `classic`). RenderCV ships several built-in themes; full customization via custom RenderCV themes.

### Bulk-import new entries from a CV/DOCX
Drop the file into `sources/cvs/`, then run:
```bash
.venv/bin/python scripts/analyze_sources.py
```
Review `sources/_diff.md` (gitignored) and hand-paste accepted entries into `profile.yaml`. The script never touches `profile.yaml` directly.

### Sync new publications from ORCID
```bash
.venv/bin/python orcid_works.py
```
Review `orcid_diff.md` (gitignored). Same paste workflow.

### Sync new datasets from Zenodo
```bash
.venv/bin/python scripts/zenodo_works.py
```
Review `zenodo_diff.md` (gitignored). Same paste workflow — proposed entries land in `profile.yaml`'s `Data & Software` section.

### Find missing fields across profile.yaml
```bash
.venv/bin/python scripts/fill_missing_fields.py
```
Reviews `profile.yaml` for blank `name`/category fields, suggests derivations, writes `profile_fill_diff.md`.

---

## Local development

### Setup (one-time)
```bash
# Python venv for build tooling + RenderCV
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt

# Node deps for the website
cd site && npm ci
```

Set up `.env` at the repo root with:
```
ORCID_CLIENT_ID=APP-...           # for orcid_works.py
ORCID_CLIENT_SECRET=...
ORCID_ID=0000-0003-4372-2241
ANTHROPIC_API_KEY=sk-ant-...      # for analyze_sources.py
```

### Run the dev server
```bash
cd site && npm run dev   # http://localhost:3000
```

The `predev` npm script automatically regenerates the 5 content JSONs from `profile.yaml` before starting the dev server, so any YAML change is visible after the next page reload.

### Build the static site locally
```bash
cd site && npm run build
```
Output lands in `site/out/`. The `prebuild` npm script regenerates JSONs first.

### Generate the vita PDF locally
```bash
cd site && npm run gen:vita
```
Output: `site/public/vita.pdf` (gitignored). CI also runs RenderCV on every push.

### Run tests
```bash
.venv/bin/pytest scripts/tests/
```
108 tests cover the data-build/delivery libraries.

---

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | Next.js 16 (App Router, TypeScript, static export), Tailwind CSS v4, Google Fonts (Inter / Instrument Serif / Geist Mono) |
| YAML loading | `js-yaml` + `zod` (validates `site_extras.yaml`) at build time |
| SSOT | `site/content/profile.yaml` (RenderCV-format YAML with custom keys) |
| Vita PDF | [RenderCV](https://docs.rendercv.com) (Python) — `classic` theme |
| CV / source analyzer | [Anthropic Claude API](https://docs.anthropic.com) (`claude-sonnet-4-6`) + `mammoth` for DOCX |
| ORCID sync | Python `urllib` against ORCID Public API v3.0 |
| Tests | pytest (Python side); Next.js build is the implicit test on the JS side |
| Deployment | GitHub Actions → GitHub Pages |

---

## Repository layout

```
.
├── site/                          # Next.js project
│   ├── content/
│   │   ├── profile.yaml           # SSOT — edit this for content
│   │   └── site_extras.yaml       # Site-only display fields
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/            # WritingCitation, SpeakingCitation, etc.
│   │   └── lib/                   # types, content loader, schemas
│   └── public/                    # Static assets, generated vita.pdf
├── scripts/
│   ├── profile_to_content_jsons.py    # SSOT → 5 site JSONs (delivery)
│   ├── json_emitters.py               # Per-section converters
│   ├── analyze_sources.py             # Plan G: CV/DOCX → review diff
│   ├── analyzer_lib.py                # Source analyzer helpers
│   ├── orcid_diff_lib.py              # Plan E: ORCID diff helpers
│   ├── fill_missing_fields.py         # Plan H: blank-field review tool
│   ├── profile_derive_lib.py          # Plan H: title/category derivation
│   └── tests/                         # pytest suite (108 tests)
├── sources/                       # Drop-zone for raw artifacts
│   ├── cvs/                       # Old vitae (DOCX) for analyzer ingest
│   └── README.md                  # Drop-zone workflow
├── orcid_works.py                 # Plan E: ORCID fetcher + diff
├── orcid_works.json               # ORCID snapshot (committed)
├── docs/superpowers/plans/        # Implementation plans (Plans A–H)
├── ARCHITECTURE.md                # Data-build vs delivery layer details
├── SSOT_PLAN.md                   # Higher-level SSOT vision
├── .github/workflows/deploy.yml   # CI: render vita + build + deploy
└── old jekyll site/               # Archived original Jekyll site
```

---

## Contributing / extending

- **Add a new delivery output** (e.g. CSL JSON for Zotero, LinkedIn paste view): write a pure Python emitter in `scripts/`, mirror the `profile_to_content_jsons.py` pattern, add shape-completeness tests.
- **Add a new section to profile.yaml**: append to `cv.sections.<NewSection>`. RenderCV will pick it up automatically. The website's content pages only render sections explicitly mapped in `WRITING_SUBCATEGORY` (in `profile_to_content_jsons.py`).
- **Add a new delivery template**: each delivery has its own format/template — RenderCV theme for the vita, React components for the website. Don't push delivery-specific formatting back into `profile.yaml`.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the design principles, and [`docs/superpowers/plans/`](./docs/superpowers/plans/) for the historical implementation plans (each documents a chunk of the migration from the original Jekyll site).

---

## License

Content is licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode). Code is MIT-licensed where not otherwise noted.
