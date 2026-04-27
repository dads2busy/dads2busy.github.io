#!/usr/bin/env python3
"""LLM-assisted source analyzer: compare a CV in sources/cvs/ against profile.yaml.

Run from repo root:
    .venv/bin/python scripts/analyze_sources.py

Output: sources/_diff.md (gitignored). Review and hand-apply accepted entries.
The script NEVER writes to site/content/profile.yaml.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

from analyzer_lib import docx_to_markdown, extract_profile_titles

REPO_ROOT = Path(__file__).resolve().parent.parent
CV_DIR = REPO_ROOT / "sources" / "cvs"
PROFILE_PATH = REPO_ROOT / "site" / "content" / "profile.yaml"
OUTPUT_PATH = REPO_ROOT / "sources" / "_diff.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

SYSTEM_PROMPT = """You are a careful research assistant analyzing a CV/vita against an existing structured profile.yaml file.

Your job is to extract every distinct entry from the CV (publications, talks, positions, education, awards, etc.) and compare each one against the entries already in profile.yaml. Output a single Markdown document with three sections:

## Already in profile.yaml
A bulleted list of CV entries that match a title already in profile.yaml. One line per match: `- ✓ "<entry title>" — matched section: <profile section name>`. No body text needed.

## Candidate NEW entries
For each CV entry NOT found in profile.yaml, provide:
- A subheading with the entry type and short title
- A ready-to-paste YAML snippet matching RenderCV's schema. Use `publication_entry` shape (title, authors as a list, date, doi, journal) for publications; use `normal_entry` shape (name, date, summary) for experience/research/talks/teaching; use `OneLineEntry` shape (label, details) for awards. Wrap in a fenced ```yaml block.
- Bold Aaron Schroeder's name in the authors list using **double asterisks** wherever it appears. Other authors are not bolded.

## Possibly modified entries
For CV entries whose title matches profile.yaml but whose details (authors, date, journal, etc.) appear different, briefly describe the discrepancy. Do NOT propose a YAML patch — just flag it for the user's review.

Match titles loosely: ignore case, trailing periods, smart quotes, extra whitespace. If you're unsure whether two titles refer to the same work, err on the side of "possibly modified" rather than "new".

Be honest about uncertainty. If a CV section is hard to parse or you can't tell what type an entry is, say so in a brief preamble before the three sections.

Do NOT include preamble narrative beyond the section headings unless flagging real uncertainty. Be concise."""


def build_user_message(profile_yaml_text: str, profile_titles: list, cv_markdown: str, cv_filename: str) -> list:
    titles_summary = "\n".join(f"- [{section}] {title}" for section, title in profile_titles)
    return [
        {
            "type": "text",
            "text": f"Existing profile.yaml ({PROFILE_PATH.name}):\n\n```yaml\n{profile_yaml_text}\n```\n\nFlat title index of profile.yaml ({len(profile_titles)} entries):\n\n{titles_summary}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"CV source file: `{cv_filename}` (converted from DOCX to Markdown)\n\n---\n\n{cv_markdown}\n\n---\n\nAnalyze this CV against profile.yaml above. Produce the three-section Markdown diff per your instructions.",
        },
    ]


def find_cv() -> Path:
    docx_files = sorted(CV_DIR.glob("*.docx"))
    if not docx_files:
        sys.exit(f"No .docx files found in {CV_DIR}. Drop a CV there and re-run.")
    if len(docx_files) > 1:
        print(f"Multiple .docx files in {CV_DIR}; using the most recent: {docx_files[-1].name}", file=sys.stderr)
    return docx_files[-1]


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Add it to .env at repo root.")

    cv_path = find_cv()
    print(f"Reading CV: {cv_path.name}", file=sys.stderr)
    cv_markdown = docx_to_markdown(cv_path)

    print(f"Loading profile.yaml ({PROFILE_PATH.stat().st_size // 1024} KB)", file=sys.stderr)
    profile_yaml_text = PROFILE_PATH.read_text()
    profile = yaml.safe_load(profile_yaml_text)
    profile_titles = extract_profile_titles(profile)
    print(f"Indexed {len(profile_titles)} existing entries across {len(set(s for s, _ in profile_titles))} sections", file=sys.stderr)

    client = Anthropic()
    print(f"Calling {MODEL} (adaptive thinking, effort=high) — may take 30-90s", file=sys.stderr)

    diff_text_parts: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": build_user_message(profile_yaml_text, profile_titles, cv_markdown, cv_path.name)}],
    ) as stream:
        for text in stream.text_stream:
            diff_text_parts.append(text)
            print(text, end="", flush=True)
        final = stream.get_final_message()

    diff_text = "".join(diff_text_parts)
    header = (
        f"# Source Analysis: {cv_path.name}\n\n"
        f"Generated {datetime.now().isoformat(timespec='seconds')} from `{cv_path.relative_to(REPO_ROOT)}`\n"
        f"Indexed {len(profile_titles)} existing profile.yaml entries.\n"
        f"Model: {MODEL} | input: {final.usage.input_tokens} tokens "
        f"(cache_read: {final.usage.cache_read_input_tokens}, "
        f"cache_creation: {final.usage.cache_creation_input_tokens}) | "
        f"output: {final.usage.output_tokens} tokens\n\n---\n\n"
    )
    OUTPUT_PATH.write_text(header + diff_text + "\n")
    print(f"\n\nWrote {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
