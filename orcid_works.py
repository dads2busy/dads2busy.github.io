"""
Fetch works from an ORCID record using the Public API (v3.0).

Usage:
    # Set ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, and optionally ORCID_ID in .env or environment
    python3 orcid_works.py [ORCID-ID]

Example:
    python3 orcid_works.py 0000-0003-4372-2241
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

# Re-use Plan G's analyzer_lib + Plan E's diff lib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from analyzer_lib import extract_profile_dois, extract_profile_titles  # noqa: E402
from orcid_diff_lib import compute_diff, orcid_group_to_entry  # noqa: E402

API_BASE = "https://pub.orcid.org/v3.0"
TOKEN_URL = "https://orcid.org/oauth/token"


def load_dotenv(path: str = ".env") -> None:
    """Load environment variables from a .env file if present."""
    if not os.path.exists(path):
        return

    with open(path, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def get_access_token(client_id: str, client_secret: str) -> str:
    """Exchange client credentials for a read-public access token."""
    data = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "/read-public",
        }
    ).encode()

    req = urllib.request.Request(TOKEN_URL, data=data)
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def get_works(orcid_id: str, token: str) -> dict:
    """Fetch the works summary for an ORCID record."""
    url = f"{API_BASE}/{orcid_id}/works"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def print_works(data: dict) -> None:
    """Print a human-readable summary of each work."""
    groups = data.get("group", [])
    print(f"\nTotal work groups: {len(groups)}\n")
    print("=" * 80)

    for i, group in enumerate(groups, 1):
        summaries = group.get("work-summary", [])
        if not summaries:
            continue

        work = summaries[0]
        title_obj = work.get("title", {})
        title = (
            title_obj.get("title", {}).get("value", "Untitled")
            if title_obj
            else "Untitled"
        )

        work_type = work.get("type", "unknown")
        pub_date = work.get("publication-date") or {}
        year = pub_date.get("year", {}).get("value", "n/a") if pub_date else "n/a"
        journal = work.get("journal-title", {})
        journal_name = journal.get("value", "") if journal else ""

        ext_ids = work.get("external-ids", {}).get("external-id", [])
        doi = next(
            (
                eid["external-id-value"]
                for eid in ext_ids
                if eid["external-id-type"] == "doi"
            ),
            None,
        )

        print(f"{i}. {title}")
        print(f"   Type: {work_type}  |  Year: {year}")
        if journal_name:
            print(f"   Journal: {journal_name}")
        if doi:
            print(f"   DOI: https://doi.org/{doi}")
        print("-" * 80)


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
        "# ORCID Sync Diff",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        f"Source: ORCID ({len(orcid_entries)} work-groups)",
        f"SSOT: {profile_path} ({len(profile_titles)} titled entries, {len(profile_dois)} DOIs)",
        "",
        "## Summary",
        f"- ✓ {len(matched)} entries already in profile.yaml",
        f"- + {len(new)} candidate NEW entries (proposed YAML below)",
        f"- ~ {len(fuzzy)} fuzzy matches (DOI matches but title differs — review for stale metadata)",
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
        lines.append(f"- title: \"{e['title']}\"")
        lines.append("  authors: []  # ORCID work-summary doesn't include authors; add by hand")
        if e['year']:
            lines.append(f"  date: \"{e['year']}\"")
        if e['doi']:
            lines.append(f"  doi: {e['doi']}")
        if e['journal']:
            lines.append(f"  journal: \"{e['journal']}\"")
        lines.append("```")
        lines.append("")

    lines.extend([f"## Fuzzy matches ({len(fuzzy)})", ""])
    for e in fuzzy:
        lines.append(f"- DOI `{e['doi']}` is in profile.yaml but the ORCID title differs:")
        lines.append(f"  - ORCID: \"{e['title']}\"")
        lines.append("")

    open(diff_path, "w").write("\n".join(lines) + "\n")
    return len(matched), len(new), len(fuzzy)


def main():
    load_dotenv()

    orcid_id = os.environ.get("ORCID_ID") or (
        sys.argv[1] if len(sys.argv) > 1 else None
    )
    if not orcid_id:
        print("Usage: python3 orcid_works.py [ORCID-ID]")
        print("Example: python3 orcid_works.py 0000-0003-4372-2241")
        print("Tip: Set ORCID_ID in .env to avoid passing it on the command line.")
        sys.exit(1)

    client_id = os.environ.get("ORCID_CLIENT_ID")
    client_secret = os.environ.get("ORCID_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(
            "Error: Set ORCID_CLIENT_ID and ORCID_CLIENT_SECRET environment variables."
        )
        sys.exit(1)

    print("Authenticating with ORCID API...")
    token = get_access_token(client_id, client_secret)
    print(f"Fetching works for {orcid_id}...")

    data = get_works(orcid_id, token)

    output_file = "orcid_works.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Full JSON saved to {output_file}")

    print_works(data)

    matched, new, fuzzy = write_diff(data)
    print(f"\nWrote orcid_diff.md")
    print(f"  Already in SSOT: {matched}")
    print(f"  Candidate new:   {new}")
    print(f"  Fuzzy matches:   {fuzzy}")


if __name__ == "__main__":
    main()
