"""Pure library for repo discovery. No network or LLM calls in this module —
all I/O is injected by the caller."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal


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


def normalize_github_url(origin: str | None) -> str | None:
    """Return the canonical https://github.com/owner/repo form for any
    recognized github remote, or None for non-github / unrecognized URLs.

    Handles:
      - https://github.com/owner/repo[.git]
      - git@github.com:owner/repo[.git]
      - ssh://git@github.com/owner/repo[.git]
    """
    if not origin:
        return None
    o = origin.strip().rstrip("/")
    # https form
    if o.startswith("https://github.com/"):
        return o.removesuffix(".git")
    # ssh shorthand: git@github.com:owner/repo.git
    if o.startswith("git@github.com:"):
        path = o[len("git@github.com:"):]
        return "https://github.com/" + path.removesuffix(".git")
    # ssh url form
    if o.startswith("ssh://git@github.com/"):
        path = o[len("ssh://git@github.com/"):]
        return "https://github.com/" + path.removesuffix(".git")
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
            html_url = normalize_github_url(origin)
            if html_url and html_url in _SELF_URLS:
                continue

            sha, date = _last_commit(child)
            primary_lang, langs = _detect_languages(child)
            readme = _read_readme_excerpt(child)
            commits = _commit_count(child)
            src_count = count_source_files(child)

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


GH_FIELDS = (
    "name,description,primaryLanguage,languages,pushedAt,"
    "isArchived,isFork,defaultBranchRef,url,owner"
)


def parse_gh_repo_list(payload: str) -> list[dict]:
    """Parse `gh repo list --json` output; drop forks."""
    raw = json.loads(payload)
    return [r for r in raw if not r.get("isFork", False)]


def _truncate_readme(text: str) -> str:
    if len(text) > 50_000:
        return text[:2000] + "\n\n[... truncated ...]\n\n" + text[-500:]
    return text[:2000] if len(text) > 2000 else text


def list_github_repos(
    owner: str,
    *,
    gh_runner: Callable[[list[str]], str],
    readme_runner: Callable[[str, str], str],
    commit_count_runner: Callable[[str, str], int],
) -> list[RepoMeta]:
    """Query gh CLI for owner's repos. Forks are filtered. Archived included.

    Runners are injected so tests can substitute fakes:
      - gh_runner(args)         -> stdout str
      - readme_runner(owner, name) -> README text (or "" if missing)
      - commit_count_runner(owner, name) -> int
    """
    payload = gh_runner([
        "gh", "repo", "list", owner,
        "--limit", "500", "--json", GH_FIELDS,
    ])
    parsed = parse_gh_repo_list(payload)

    repos: list[RepoMeta] = []
    for r in parsed:
        url = r.get("url") or ""
        if normalize_github_url(url) in _SELF_URLS:
            continue
        name = r["name"]
        readme = _truncate_readme(readme_runner(owner, name))
        primary = (r.get("primaryLanguage") or {}).get("name")
        langs = {l["node"]["name"]: l["size"] for l in r.get("languages") or []}
        commits = commit_count_runner(owner, name)

        meta = RepoMeta(
            name=name,
            owner=owner,
            source="github",
            description=r.get("description"),
            primary_language=primary,
            languages=langs,
            last_commit_date=r.get("pushedAt") or "",
            last_commit_sha="",  # gh repo list doesn't return commit sha; content_hash falls back to date
            commit_count=commits,
            archived=bool(r.get("isArchived")),
            fork=False,
            default_branch=(r.get("defaultBranchRef") or {}).get("name") or "main",
            html_url=r.get("url"),
            local_path=None,
            readme_excerpt=readme,
            manifest_files=[],  # not detectable without clone; left empty
            substantive=False,  # caller fills in after; for github-only repos we
                                # approximate "source files" by sum(languages.values()) > 0
            paragraph=None,
        )
        # GitHub-only substantive heuristic: README + commits + at least one tracked language
        meta.substantive = (
            len(readme) >= 200
            and commits >= 5
            and len(langs) >= 1
        )
        repos.append(meta)
    return repos


def default_gh_runner(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def default_readme_runner(owner: str, name: str) -> str:
    """Use `gh api repos/{owner}/{name}/readme` to fetch README content."""
    out = subprocess.run(
        ["gh", "api", f"repos/{owner}/{name}/readme",
         "-H", "Accept: application/vnd.github.raw"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return ""
    return out.stdout


def default_commit_count_runner(owner: str, name: str) -> int:
    """Use GraphQL totalCount of default branch."""
    query = (
        "query($owner:String!,$name:String!){repository(owner:$owner,name:$name){"
        "defaultBranchRef{target{... on Commit{history{totalCount}}}}}}"
    )
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}",
         "-F", f"owner={owner}", "-F", f"name={name}"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return 0
    try:
        data = json.loads(out.stdout)
        return (
            data.get("data", {})
            .get("repository", {})
            .get("defaultBranchRef", {})
            .get("target", {})
            .get("history", {})
            .get("totalCount", 0)
        )
    except (json.JSONDecodeError, AttributeError, TypeError):
        return 0


def merge_repos(github: list[RepoMeta], local: list[RepoMeta]) -> list[RepoMeta]:
    """Dedupe by html_url. When a local repo matches a GitHub repo,
    the GitHub record wins on metadata but local_path is preserved and
    source becomes 'github+local'."""
    by_url: dict[str, RepoMeta] = {}
    out: list[RepoMeta] = []

    for r in github:
        if r.html_url:
            by_url[r.html_url] = r
        out.append(r)

    for r in local:
        if r.html_url and r.html_url in by_url:
            gh_match = by_url[r.html_url]
            gh_match.local_path = r.local_path
            gh_match.source = "github+local"
            # If github lacked manifest detection, take from local
            if not gh_match.manifest_files and r.manifest_files:
                gh_match.manifest_files = r.manifest_files
        else:
            out.append(r)
    return out
