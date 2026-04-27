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
