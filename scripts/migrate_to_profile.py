#!/usr/bin/env python3
"""One-time migration: existing content JSONs + page.tsx constants -> site/content/profile.yaml.

Run from repo root:
    .venv/bin/python scripts/migrate_to_profile.py
"""

import json
from collections import OrderedDict
from pathlib import Path

import yaml

from profile_lib import (
    research_entry_to_normal,
    speaking_entry_to_normal,
    teaching_entry_to_normal,
    working_entry_to_normal,
    writing_entry_to_publication,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "site" / "content"
OUTPUT_PATH = CONTENT_DIR / "profile.yaml"


# ────────────────────────────────────────────────────────────────────
# Hand-curated constants (sourced from site/src/app/page.tsx).
# ────────────────────────────────────────────────────────────────────

IDENTITY = {
    "name": "Aaron D. Schroeder",
    "email": "aaron.schroeder@virginia.edu",
    "social_networks": [
        {"network": "GitHub", "username": "dads2busy"},
    ],
}

SUMMARY = [
    "Dr. Schroeder's overarching research focus is the enablement of Evidence-Based Policy-Making and Program Evaluation through the secure liberation, integration and analysis of administrative data.",
    "A particular focus has been the integration of education, health, social service and non-profit administrative data streams to support policy analyses and program evaluations across pre-K services, child care, K-12 and adult education, state workforce training, and U.S. veteran services.",
    "High-profile information integration projects in the Commonwealth of Virginia include the USED-funded Statewide Longitudinal Data System, the USHHS-funded Project Child HANDS, and the USDOT-funded design and evaluation of the U.S.'s first statewide travel information system, Virginia 511.",
]

EDUCATION = [
    {
        "institution": "Virginia Tech University",
        "area": "Public Policy & Administration",
        "degree": "PhD",
        "date": "2001",
        "highlights": [
            "Areas: Organization Theory, Data Management, Privacy Law, Implementation",
            "Dissertation: Building Implementation Networks",
        ],
    },
    {
        "institution": "James Madison University",
        "area": "Public Administration",
        "degree": "MPA",
        "date": "1993",
        "highlights": ["Areas: Geographic Information Systems, Administrative Law"],
    },
    {
        "institution": "University of Delaware",
        "area": "Psychology",
        "degree": "BA",
        "date": "1991",
        "highlights": [
            "Areas: Brain & Behavior (incl. graduate-level Neuropsychology)",
            "Minor: Statistics",
        ],
    },
]

AWARDS = [
    {"label": "Member, Arlington County Open Data Advisory Group", "details": "2018-2019"},
    {"label": "COVITS Winner — Cross-Boundary Collaboration on IT (VLDS)", "details": "2013"},
    {"label": "COVITS Finalist — Virginia Longitudinal Data System", "details": "2012"},
    {"label": "Invited, Virginia Governor's Early Childhood Advisory Council", "details": "2010"},
    {"label": "Invited, National Institute of Statistical Sciences Workshop", "details": "2009"},
    {"label": "Invited, National Press Club — intergenerational day care findings", "details": "2008"},
    {"label": "Invited speaker, Florida DOT ITS Conference", "details": "2003"},
    {"label": "Invited workshop lead, Univ. of LaVerne — IT implementation", "details": "2000"},
    {"label": "Invited, Virginia Transportation Conference", "details": "1999-2000"},
    {"label": "Nominee, ASG Award for Innovation in State Government (Travel Shenandoah)", "details": "1999"},
    {"label": "Appointed Member, Congressional Commission on I-81 Truck Safety", "details": "1999"},
    {"label": "Eno Transportation Fellow", "details": "1997"},
    {"label": "Invited Guest Editor, Administration & Society", "details": "1997"},
]

SKILLS = [
    "R", "Python", "PostgreSQL", "Oracle PL/SQL", "MS SQL Server",
    "Linux Admin", "Docker", "JavaEE", "ASP.NET/C#", "SAS", "SPSS",
    "Network Admin", "Photoshop/GIMP", "LLMs/AI",
]

# Subcategory → vita section title. Order here = vita render order.
WRITING_SECTIONS = OrderedDict([
    ("Refereed Journal Articles", "Journal Publications (refereed)"),
    ("Book Chapters", "Book Chapters"),
    ("Conference Proceedings / Presentations", "Conference Proceedings/Presentations"),
    ("Research / Technical Reports", "Research/Technical Reports"),
    ("Editorials", "Editorials"),
    ("Dissertation", "Dissertation"),
])


def load_json(filename: str) -> list:
    return json.loads((CONTENT_DIR / filename).read_text())


def build_publication_sections() -> "OrderedDict[str, list[dict]]":
    """One section per writing.json subcategory, in the order from WRITING_SECTIONS."""
    entries = load_json("writing.json")
    by_sub: dict[str, list[dict]] = {}
    for e in entries:
        by_sub.setdefault(e["subcategory"], []).append(writing_entry_to_publication(e))

    sections: OrderedDict[str, list[dict]] = OrderedDict()
    for vita_title, json_subcategory in WRITING_SECTIONS.items():
        if pubs := by_sub.get(json_subcategory):
            sections[vita_title] = pubs
    return sections


def build_normal_section(filename: str, converter) -> list[dict]:
    return [converter(e) for e in load_json(filename)]


def build_profile() -> dict:
    sections: OrderedDict[str, list] = OrderedDict()
    sections["Summary"] = SUMMARY
    sections["Education"] = EDUCATION
    sections["Experience"] = build_normal_section("working.json", working_entry_to_normal)
    sections["Research Projects"] = build_normal_section("research.json", research_entry_to_normal)
    sections["Presentations"] = build_normal_section("speaking.json", speaking_entry_to_normal)
    sections["Teaching"] = build_normal_section("teaching.json", teaching_entry_to_normal)
    sections.update(build_publication_sections())
    sections["Awards & Honors"] = AWARDS
    sections["Skills"] = SKILLS

    return {
        "cv": {**IDENTITY, "sections": sections},
        "design": {"theme": "classic"},
    }


def represent_ordereddict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def main() -> None:
    yaml.add_representer(OrderedDict, represent_ordereddict)
    profile = build_profile()
    OUTPUT_PATH.write_text(
        yaml.dump(profile, sort_keys=False, allow_unicode=True, width=100)
    )
    counts = {k: len(v) if isinstance(v, list) else "—" for k, v in profile["cv"]["sections"].items()}
    print(f"Wrote {OUTPUT_PATH}")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
