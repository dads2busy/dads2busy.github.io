"""Render advisor/repos.md from advisor/repos_index.json.

Run from repo root:
    .venv/bin/python scripts/repo_render.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADVISOR_DIR = REPO_ROOT / "advisor"
INDEX_PATH = ADVISOR_DIR / "repos_index.json"
MD_PATH = ADVISOR_DIR / "repos.md"


def _status(entry: dict) -> str:
    if entry.get("archived"):
        return "archived"
    return "active"


def _header(entry: dict) -> str:
    name = entry["name"]
    owner = entry.get("owner")
    title = f"{owner}/{name}" if owner else name
    lang = entry.get("primary_language") or "—"
    last = (entry.get("last_commit_date") or "—")[:10]
    return f"### {title} · {lang} · {_status(entry)} · last commit {last}"


def render(index: list[dict]) -> str:
    substantive = [e for e in index if e.get("substantive")]
    other = [e for e in index if not e.get("substantive")]

    substantive.sort(key=lambda e: e.get("last_commit_date") or "", reverse=True)
    other.sort(key=lambda e: e.get("last_commit_date") or "", reverse=True)

    lines: list[str] = []
    lines.append(f"# Aaron's repos (auto-generated {date.today().isoformat()})")
    lines.append("")
    lines.append("## Substantive projects")
    lines.append("")
    for e in substantive:
        lines.append(_header(e))
        lines.append("")
        para = e.get("paragraph") or "*(summary pending)*"
        lines.append(para.rstrip())
        lines.append("")

    lines.append("## Other repos")
    lines.append("")
    if other:
        lines.append("| name | language | last commit | status |")
        lines.append("| --- | --- | --- | --- |")
        for e in other:
            n = (e["owner"] + "/" + e["name"]) if e.get("owner") else e["name"]
            lang = e.get("primary_language") or "—"
            last = (e.get("last_commit_date") or "—")[:10]
            lines.append(f"| {n} | {lang} | {last} | {_status(e)} |")
    else:
        lines.append("*(none)*")
    lines.append("")
    return "\n".join(lines)


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".repos.", suffix=".md", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def main() -> None:
    if not INDEX_PATH.exists():
        print(f"ERROR: {INDEX_PATH} not found", file=sys.stderr)
        sys.exit(2)

    profile_link = ADVISOR_DIR / "profile.yaml"
    if profile_link.exists() and profile_link.is_symlink():
        if not profile_link.resolve().exists():
            print("ERROR: advisor/profile.yaml symlink target missing", file=sys.stderr)
            sys.exit(2)

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index = json.load(f)

    text = render(index)
    _atomic_write(MD_PATH, text)
    print(f"wrote {MD_PATH} ({len(text)} chars)", file=sys.stderr)


if __name__ == "__main__":
    main()
