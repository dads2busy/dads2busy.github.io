"""Discovery stage: write advisor/repos_index.json from gh + ~/git/* state.

Run from repo root:
    .venv/bin/python scripts/repo_discover.py

Env:
    ADVISOR_LOCAL_ROOTS  Colon-separated list of dirs to scan. Defaults to
                         "$HOME/git" if it exists. Set to empty to disable.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo_discover_lib import (
    RepoMeta,
    content_hash,
    default_commit_count_runner,
    default_gh_runner,
    default_readme_runner,
    list_github_repos,
    list_local_repos,
    merge_repos,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ADVISOR_DIR = REPO_ROOT / "advisor"
INDEX_PATH = ADVISOR_DIR / "repos_index.json"


def _local_roots() -> list[Path]:
    raw = os.environ.get("ADVISOR_LOCAL_ROOTS")
    if raw is None:
        default = Path.home() / "git"
        return [default] if default.exists() else []
    if not raw.strip():
        return []
    return [Path(p) for p in raw.split(":") if p.strip()]


def _atomic_write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".repos_index.", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def main() -> None:
    print(f"discovering repos for owner=dads2busy + local roots={_local_roots()}", file=sys.stderr)

    github = list_github_repos(
        "dads2busy",
        gh_runner=default_gh_runner,
        readme_runner=default_readme_runner,
        commit_count_runner=default_commit_count_runner,
    )
    print(f"  github: {len(github)} repos", file=sys.stderr)

    local = list_local_repos(_local_roots())
    print(f"  local: {len(local)} repos", file=sys.stderr)

    merged = merge_repos(github, local)
    merged.sort(key=lambda r: (r.last_commit_date or ""), reverse=True)

    out: list[dict] = []
    for r in merged:
        d = asdict(r)
        d["content_hash"] = content_hash(r)
        out.append(d)

    _atomic_write_json(INDEX_PATH, out)
    print(f"wrote {INDEX_PATH} with {len(out)} repos", file=sys.stderr)


if __name__ == "__main__":
    main()
