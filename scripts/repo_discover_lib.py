"""Pure library for repo discovery. No network or LLM calls in this module —
all I/O is injected by the caller."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
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


def is_substantive(repo: RepoMeta, source_file_count: int) -> bool:
    """README ≥ 200 chars AND ≥ 5 commits AND ≥ 5 source files."""
    return (
        len(repo.readme_excerpt) >= 200
        and repo.commit_count >= 5
        and source_file_count >= 5
    )


# Files we don't count as "source files" for the substantive check.
_BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz",
    ".woff", ".woff2", ".ttf", ".otf", ".ico", ".mp3", ".mp4", ".mov",
}
_EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".next"}

# Manifest files we surface in RepoMeta.manifest_files
_MANIFEST_NAMES = {
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "package.json", "Cargo.toml", "go.mod", "Gemfile",
    "pom.xml", "build.gradle", "build.gradle.kts", "Dockerfile",
}

# Recognized HTTP forms of this repo's own remote URL — used to drop self.
_SELF_URLS = {
    "https://github.com/dads2busy/dads2busy.github.io",
    "https://github.com/dads2busy/dads2busy.github.io.git",
    "git@github.com:dads2busy/dads2busy.github.io.git",
}


def count_source_files(repo_path: Path) -> int:
    """Count files under repo_path excluding known build/cache dirs and binaries."""
    total = 0
    for p in repo_path.rglob("*"):
        if not p.is_file():
            continue
        if any(part in _EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in _BINARY_SUFFIXES:
            continue
        total += 1
    return total


def _read_readme_excerpt(repo_path: Path) -> str:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        candidate = repo_path / name
        if candidate.exists():
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return ""
            if len(text) > 50_000:
                text = text[:2000] + "\n\n[... truncated ...]\n\n" + text[-500:]
            elif len(text) > 2000:
                text = text[:2000]
            return text
    return ""


def _detect_manifests(repo_path: Path) -> list[str]:
    return sorted(name for name in _MANIFEST_NAMES if (repo_path / name).exists())


def _origin_url(repo_path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path, capture_output=True, text=True, check=False,
        )
        if out.returncode != 0:
            return None
        url = out.stdout.strip()
        return url or None
    except FileNotFoundError:
        return None


def _commit_count(repo_path: Path) -> int:
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=repo_path, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return 0
    try:
        return int(out.stdout.strip())
    except ValueError:
        return 0


def _last_commit(repo_path: Path) -> tuple[str, str]:
    """Return (sha, iso_date). Empty strings if not available."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%H %cI"],
        cwd=repo_path, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0 or not out.stdout.strip():
        return "", ""
    parts = out.stdout.strip().split(" ", 1)
    if len(parts) != 2:
        return parts[0], ""
    return parts[0], parts[1]


def _detect_languages(repo_path: Path) -> tuple[str | None, dict[str, int]]:
    """Lightweight language detection by file extension byte counts."""
    ext_to_lang = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript", ".jsx": "JavaScript", ".rs": "Rust",
        ".go": "Go", ".java": "Java", ".rb": "Ruby", ".cs": "C#",
        ".cpp": "C++", ".c": "C", ".h": "C", ".hpp": "C++",
        ".css": "CSS", ".html": "HTML", ".sh": "Shell", ".sql": "SQL",
        ".r": "R", ".R": "R", ".md": "Markdown", ".yml": "YAML", ".yaml": "YAML",
    }
    counts: dict[str, int] = {}
    for p in repo_path.rglob("*"):
        if not p.is_file() or any(part in _EXCLUDE_DIRS for part in p.parts):
            continue
        lang = ext_to_lang.get(p.suffix)
        if lang:
            try:
                counts[lang] = counts.get(lang, 0) + p.stat().st_size
            except OSError:
                pass
    if not counts:
        return None, {}
    primary = max(counts, key=counts.get)
    return primary, counts


def list_local_repos(roots: list[Path]) -> list[RepoMeta]:
    """Glob each root one level deep; keep dirs with .git/. Drop self-repo."""
    found: list[RepoMeta] = []
    for root in roots:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            if not (child / ".git").exists():
                continue
            origin = _origin_url(child)
            if origin and origin.rstrip("/") in _SELF_URLS:
                continue

            sha, date = _last_commit(child)
            primary_lang, langs = _detect_languages(child)
            readme = _read_readme_excerpt(child)
            commits = _commit_count(child)
            src_count = count_source_files(child)

            html_url = None
            if origin and origin.startswith("https://github.com/"):
                html_url = origin.removesuffix(".git")

            meta = RepoMeta(
                name=child.name,
                owner=None,
                source="local",
                description=None,
                primary_language=primary_lang,
                languages=langs,
                last_commit_date=date,
                last_commit_sha=sha,
                commit_count=commits,
                archived=False,
                fork=False,
                default_branch="main",
                html_url=html_url,
                local_path=str(child.resolve()),
                readme_excerpt=readme,
                manifest_files=_detect_manifests(child),
                substantive=False,  # set by caller after merge
                paragraph=None,
            )
            meta.substantive = is_substantive(meta, src_count)
            found.append(meta)
    return found
