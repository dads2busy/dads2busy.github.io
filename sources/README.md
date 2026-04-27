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
