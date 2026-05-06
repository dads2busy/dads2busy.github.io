"""Summarization stage: read advisor/repos_index.json, fill paragraphs with Haiku,
preserve unchanged paragraphs from prior committed index.

Run from repo root:
    .venv/bin/python scripts/repo_summarize.py

Env:
    ANTHROPIC_API_KEY  required
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo_discover_lib import RepoMeta
from repo_summarize_lib import should_resummarize, summarize_repo

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "advisor" / "repos_index.json"
MAX_RESUMMARIZE = 200
MAX_CONCURRENT = 5


def _load_prior_index() -> dict[str, dict]:
    """Load prior repos_index.json from the previous git commit. Empty if absent."""
    out = subprocess.run(
        ["git", "show", "HEAD:advisor/repos_index.json"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0 or not out.stdout.strip():
        return {}
    try:
        prior_list = json.loads(out.stdout)
    except json.JSONDecodeError:
        return {}
    return {entry["name"]: entry for entry in prior_list}


def _atomic_write_json(path: Path, data: list[dict]) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".repos_index.", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def _entry_to_meta(entry: dict) -> RepoMeta:
    fields = {k: v for k, v in entry.items() if k != "content_hash"}
    return RepoMeta(**fields)


def _summarize_one(meta: RepoMeta, client) -> tuple[str, str]:
    """Returns (repo_name, paragraph). Empty paragraph on failure after one retry."""
    for attempt in (1, 2):
        try:
            return meta.name, summarize_repo(meta, client)
        except Exception as exc:
            if attempt == 2:
                print(f"  WARN summarize failed for {meta.name}: {exc}", file=sys.stderr)
                return meta.name, ""
            time.sleep(1.5)
    return meta.name, ""


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is required", file=sys.stderr)
        sys.exit(2)

    if not INDEX_PATH.exists():
        print(f"ERROR: {INDEX_PATH} not found — run repo_discover.py first", file=sys.stderr)
        sys.exit(2)

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index = json.load(f)

    prior = _load_prior_index()

    # Carry forward paragraphs whose hash matches prior
    metas: list[RepoMeta] = []
    for entry in index:
        m = _entry_to_meta(entry)
        prior_entry = prior.get(m.name)
        if (prior_entry
                and prior_entry.get("content_hash") == entry["content_hash"]
                and prior_entry.get("paragraph")):
            m.paragraph = prior_entry["paragraph"]
        metas.append(m)

    pending = [m for m in metas if should_resummarize(m, prior)]
    if len(pending) > MAX_RESUMMARIZE:
        print(f"ERROR: {len(pending)} repos to resummarize exceeds MAX={MAX_RESUMMARIZE}; "
              f"likely a hash-computation bug. Aborting.", file=sys.stderr)
        sys.exit(3)

    print(f"summarizing {len(pending)} of {len(metas)} repos", file=sys.stderr)

    if pending:
        from anthropic import Anthropic
        client = Anthropic()

        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as pool:
            futures = {pool.submit(_summarize_one, m, client): m for m in pending}
            for fut in as_completed(futures):
                name, para = fut.result()
                if para:
                    for m in metas:
                        if m.name == name:
                            m.paragraph = para
                            break
                print(f"  done: {name} ({len(para)} chars)", file=sys.stderr)

    out_list = []
    for m, entry in zip(metas, index):
        d = entry.copy()
        d["paragraph"] = m.paragraph
        out_list.append(d)
    _atomic_write_json(INDEX_PATH, out_list)
    print(f"wrote {INDEX_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
