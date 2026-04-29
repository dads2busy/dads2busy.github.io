"""
Fetch datasets/software from Zenodo published by Aaron Schroeder, diff against
profile.yaml's Data & Software section, emit zenodo_diff.md.

Usage:
    .venv/bin/python scripts/zenodo_works.py
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# Re-use Plan E/G lib pattern
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyzer_lib import extract_profile_titles  # noqa: E402
from zenodo_diff_lib import zenodo_record_to_entry, compute_diff  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = REPO_ROOT / "site" / "content" / "profile.yaml"
DIFF_PATH = REPO_ROOT / "zenodo_diff.md"
ZENODO_API = "https://zenodo.org/api/records"


def load_dotenv(path: str = ".env") -> None:
    """Same simple .env loader pattern as orcid_works.py."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def fetch_records(creator_name: str, token: str) -> list[dict]:
    """Fetch all Zenodo records by the given creator name.

    Zenodo's legacy metadata stores creators as {"name": "Last, First"} without
    ORCID identifiers in the indexed fields, so we query by creator name.
    Set ZENODO_CREATOR_NAME in .env to override the default "Schroeder, Aaron".
    """
    q = f'creators.name:"{creator_name}"'
    url = f"{ZENODO_API}?q={urllib.parse.quote(q)}&size=100"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data.get("hits", {}).get("hits", [])


def extract_data_software_section(profile: dict) -> tuple[set, set]:
    """Return (title_tuples, dois) from profile.yaml's Data & Software section."""
    titles, dois = set(), set()
    section = profile.get("cv", {}).get("sections", {}).get("Data & Software") or []
    for entry in section:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or entry.get("title")
        if name:
            titles.add(("Data & Software", name))
        if entry.get("doi"):
            dois.add(entry["doi"])
    return titles, dois


def write_diff(records: list[dict], profile_path: Path, diff_path: Path) -> tuple[int, int, int]:
    import yaml
    profile = yaml.safe_load(profile_path.read_text())
    profile_titles, profile_dois = extract_data_software_section(profile)

    entries = [e for r in records if (e := zenodo_record_to_entry(r)) is not None]
    matched, new, fuzzy = compute_diff(entries, profile_titles, profile_dois)

    lines = [
        "# Zenodo Sync Diff",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        f"Source: Zenodo ({len(entries)} records)",
        f"SSOT: {profile_path.relative_to(REPO_ROOT)} Data & Software ({len(profile_titles)} titles, {len(profile_dois)} DOIs)",
        "",
        "## Summary",
        f"- ✓ {len(matched)} entries already in profile.yaml",
        f"- + {len(new)} candidate NEW entries (proposed YAML below)",
        f"- ~ {len(fuzzy)} fuzzy matches (DOI matches but title differs)",
        "",
        f"## Already in profile.yaml ({len(matched)})",
    ]
    for e in matched:
        lines.append(f"- ✓ \"{e['title']}\"" + (f" (DOI: {e['doi']})" if e['doi'] else ""))

    lines.extend(["", f"## Candidate NEW entries ({len(new)})", ""])
    for e in new:
        lines.append(f"### {e['title']} ({e['year'] or 'n.d.'})")
        lines.append("")
        lines.append("```yaml")
        lines.append(f"- name: \"{e['title']}\"")
        # Zenodo resource_type → Data & Software subcategory.
        # Software stays Software; everything else (Dataset, Image, Publication, …) → Dataset.
        rtype = (e.get("resource_type") or "").strip().lower()
        subcat = "Software" if rtype == "software" else "Dataset"
        lines.append(f"  subcategory: {subcat}")
        if e.get("authors"):
            lines.append("  authors:")
            for a in e["authors"]:
                escaped = a.replace('"', '\\"')
                lines.append(f'    - "{escaped}"')
        if e['year']:
            lines.append(f"  date: \"{e['year']}\"")
        if e['doi']:
            lines.append(f"  doi: {e['doi']}")
        if e.get('html_url'):
            lines.append(f"  url: {e['html_url']}")
        if e.get('resource_type'):
            lines.append(f"  summary: \"{e['resource_type']}\"")
        if e.get('description'):
            # Description from Zenodo is HTML; do a quick strip for the abstract
            desc = e['description']
            lines.append("  abstract: |")
            for ln in desc.splitlines()[:5]:  # first 5 lines as preview
                lines.append(f"    {ln.strip()}")
        lines.append("```")
        lines.append("")

    lines.extend([f"## Fuzzy matches ({len(fuzzy)})", ""])
    for e in fuzzy:
        lines.append(f"- DOI `{e['doi']}` is in profile.yaml but the Zenodo title differs:")
        lines.append(f"  - Zenodo: \"{e['title']}\"")
        lines.append("")

    diff_path.write_text("\n".join(lines) + "\n")
    return len(matched), len(new), len(fuzzy)


def main() -> None:
    load_dotenv(str(REPO_ROOT / ".env"))
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        sys.exit("ZENODO_ACCESS_TOKEN not set in .env")

    # Zenodo legacy metadata stores creators as {"name": "Last, First"} without
    # indexable ORCID fields, so we query by creator name.
    creator_name = os.environ.get("ZENODO_CREATOR_NAME", "Schroeder, Aaron")

    print(f"Fetching Zenodo records for creator \"{creator_name}\"...", file=sys.stderr)
    records = fetch_records(creator_name, token)
    print(f"Got {len(records)} records", file=sys.stderr)

    matched, new, fuzzy = write_diff(records, PROFILE_PATH, DIFF_PATH)
    print(f"Wrote {DIFF_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"  Already in SSOT: {matched}")
    print(f"  Candidate new:   {new}")
    print(f"  Fuzzy matches:   {fuzzy}")


if __name__ == "__main__":
    main()
