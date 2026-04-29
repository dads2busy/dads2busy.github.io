#!/usr/bin/env python3
"""Generator: profile.yaml → site/content/{writing,working,research,speaking,teaching}.json.

Run from repo root:
    .venv/bin/python scripts/profile_to_content_jsons.py

Used as a pre-script by `npm run dev` and `npm run build` so the website's
content pages always reflect the SSOT.
"""

import json
import re
from pathlib import Path

import yaml

from json_emitters import (
    experience_entry_to_working,
    presentation_entry_to_speaking,
    project_entry_to_research,
    publication_entry_to_writing,
    release_entry_to_releases,
    teaching_entry_to_teaching,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "site" / "content"
PROFILE_PATH = CONTENT_DIR / "profile.yaml"


def _slug_from_title(title: str) -> str:
    """Best-effort slug from a title: lowercase, alphanumerics + hyphens, max 60 chars."""
    s = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return s[:60] or "untitled"


def _dedup_slugs(entries: list[dict]) -> list[dict]:
    """Ensure slugs are unique within a list. Empty/missing slugs get derived from title.

    Duplicates get a -2, -3, ... suffix. Modifies entries in place; returns the list.
    """
    seen: dict[str, int] = {}
    for entry in entries:
        base = entry.get("slug") or ""
        # Treat very short generic slugs ('a', 'b') as missing
        if not base or len(base) <= 2:
            base = _slug_from_title(entry.get("title") or entry.get("name") or "")
        if base in seen:
            seen[base] += 1
            entry["slug"] = f"{base}-{seen[base]}"
        else:
            seen[base] = 1
            entry["slug"] = base
    return entries


# Inverse of Plan A's WRITING_SECTIONS — maps profile.yaml's section name to
# the original writing.json subcategory string.
WRITING_SUBCATEGORY = {
    "Refereed Journal Articles": "Journal Publications (refereed)",
    "Book Chapters": "Book Chapters",
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
        "writing.json": _dedup_slugs(emit_writing(sections)),
        "working.json": _dedup_slugs(emit_simple(sections, "Experience", experience_entry_to_working)),
        "research.json": _dedup_slugs(emit_simple(sections, "Research Projects", project_entry_to_research)),
        "speaking.json": _dedup_slugs(emit_simple(sections, "Presentations", presentation_entry_to_speaking)),
        "teaching.json": _dedup_slugs(emit_simple(sections, "Teaching", teaching_entry_to_teaching)),
        "releases.json": _dedup_slugs(emit_simple(sections, "Data & Software", release_entry_to_releases)),
    }

    for name, data in outputs.items():
        path = CONTENT_DIR / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)}: {len(data)} entries")


if __name__ == "__main__":
    main()
