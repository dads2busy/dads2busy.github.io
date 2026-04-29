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
