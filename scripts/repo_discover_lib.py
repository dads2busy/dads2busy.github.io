"""Pure library for repo discovery. No network or LLM calls in this module —
all I/O is injected by the caller."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal


@dataclass
class RepoMeta:
    name: str
    owner: str | None
    source: Literal["github", "local", "github+local"]
    description: str | None
    primary_language: str | None
    languages: dict[str, int]
    last_commit_date: str
    last_commit_sha: str
    commit_count: int
    archived: bool
    fork: bool
    default_branch: str
    html_url: str | None
    local_path: str | None
    readme_excerpt: str
    manifest_files: list[str]
    substantive: bool
    paragraph: str | None = None


def content_hash(repo: RepoMeta) -> str:
    """Stable hash over fields that warrant re-summarization when changed.

    Uses last_commit_sha when available (local repos) and falls back to
    last_commit_date for GitHub-only records where `gh repo list` doesn't
    return a SHA.
    """
    parts = [
        repo.name,
        repo.last_commit_sha or repo.last_commit_date,
        repo.readme_excerpt,
        repo.primary_language or "",
    ]
    blob = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
