# Advisor Repo-Summary Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an offline pipeline that produces `advisor/repos.md` and `advisor/repos_index.json` summarizing every dads2busy GitHub repo and every local-only `~/git/*` repo, refreshed weekly via a scheduled GH Action that opens a PR.

**Architecture:** Three-stage pipeline with pure libraries wrapped by entry scripts: `repo_discover_lib.py` + `repo_summarize_lib.py` (pure, fully tested) drive `repo_discover.py` → `repo_summarize.py` → `repo_render.py`. The pipeline writes to `advisor/` at repo root; `advisor/profile.yaml` is a symlink to the existing SSOT. Skip-unchanged caching via `content_hash` keeps re-runs near-zero cost.

**Tech Stack:** Python 3.12, `gh` CLI, `anthropic` SDK (Haiku 4.5), pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-05-05-advisor-repo-pipeline-design.md`

---

## File Structure

**New (pure libraries):**
- `scripts/repo_discover_lib.py` — `RepoMeta` dataclass; `list_github_repos`, `list_local_repos`, `merge_repos`, `is_substantive`, `content_hash`. No I/O beyond what's injected.
- `scripts/repo_summarize_lib.py` — `should_resummarize`, `build_prompt`, `summarize_repo`, README truncation helper.

**New (entry scripts):**
- `scripts/repo_discover.py` — runs discovery, writes `advisor/repos_index.json` atomically.
- `scripts/repo_summarize.py` — loads prior index from git, calls Haiku for changed/new substantive repos, writes paragraphs back atomically.
- `scripts/repo_render.py` — renders index JSON to `advisor/repos.md`.

**New (tests):**
- `scripts/tests/test_repo_discover_lib.py`
- `scripts/tests/test_repo_summarize_lib.py`
- `scripts/tests/test_repo_pipeline_smoke.py`

**New (advisor directory):**
- `advisor/README.md` — explains directory and `cd advisor/ && claude` workflow.
- `advisor/profile.yaml` — symlink → `../site/content/profile.yaml`.
- `advisor/repos.md` — generated, committed.
- `advisor/repos_index.json` — generated, committed.

**New (CI):**
- `.github/workflows/refresh-advisor.yml`

**Modified:**
- None. `scripts/requirements.txt` already has `anthropic>=0.40.0` and `pyyaml`.

---

## Task 1: RepoMeta dataclass + content_hash

**Files:**
- Create: `scripts/repo_discover_lib.py`
- Test: `scripts/tests/test_repo_discover_lib.py`

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_repo_discover_lib.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from repo_discover_lib import RepoMeta, content_hash


def _meta(**overrides) -> RepoMeta:
    defaults = dict(
        name="foo", owner="dads2busy", source="github",
        description="A demo repo", primary_language="Python",
        languages={"Python": 1000}, last_commit_date="2026-04-01",
        last_commit_sha="abc123", commit_count=10, archived=False,
        fork=False, default_branch="main",
        html_url="https://github.com/dads2busy/foo",
        local_path=None, readme_excerpt="hello world " * 50,
        manifest_files=["pyproject.toml"], substantive=True, paragraph=None,
    )
    defaults.update(overrides)
    return RepoMeta(**defaults)


def test_content_hash_stable_across_calls():
    m = _meta()
    assert content_hash(m) == content_hash(m)


def test_content_hash_changes_with_last_commit_sha():
    a = _meta(last_commit_sha="aaa111")
    b = _meta(last_commit_sha="bbb222")
    assert content_hash(a) != content_hash(b)


def test_content_hash_changes_with_readme():
    a = _meta(readme_excerpt="version one")
    b = _meta(readme_excerpt="version two")
    assert content_hash(a) != content_hash(b)


def test_content_hash_changes_with_primary_language():
    a = _meta(primary_language="Python")
    b = _meta(primary_language="JavaScript")
    assert content_hash(a) != content_hash(b)


def test_content_hash_changes_with_name():
    a = _meta(name="foo")
    b = _meta(name="bar")
    assert content_hash(a) != content_hash(b)


def test_content_hash_ignores_unrelated_fields():
    """Description changes shouldn't bust the cache; paragraphs come from README."""
    a = _meta(description="one")
    b = _meta(description="two")
    assert content_hash(a) == content_hash(b)


def test_content_hash_falls_back_to_last_commit_date_when_sha_empty():
    """GitHub-only records have empty last_commit_sha; hash should still vary by push."""
    a = _meta(last_commit_sha="", last_commit_date="2026-04-01T00:00:00Z")
    b = _meta(last_commit_sha="", last_commit_date="2026-04-02T00:00:00Z")
    assert content_hash(a) != content_hash(b)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'repo_discover_lib'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/repo_discover_lib.py
"""Pure library for repo discovery. No network or LLM calls in this module —
all I/O is injected by the caller."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: PASS — 6 tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_discover_lib.py scripts/tests/test_repo_discover_lib.py
git commit -m "feat(advisor): RepoMeta dataclass + content_hash"
```

---

## Task 2: is_substantive heuristic

**Files:**
- Modify: `scripts/repo_discover_lib.py` (add function)
- Modify: `scripts/tests/test_repo_discover_lib.py` (add tests)

- [ ] **Step 1: Write the failing tests**

Append to `scripts/tests/test_repo_discover_lib.py`:

```python
from repo_discover_lib import is_substantive


def test_is_substantive_passes_all_three_thresholds():
    m = _meta(readme_excerpt="x" * 200, commit_count=5)
    # source_file_count is passed in directly, not computed in the lib
    assert is_substantive(m, source_file_count=5) is True


def test_is_substantive_short_readme():
    m = _meta(readme_excerpt="x" * 199, commit_count=10)
    assert is_substantive(m, source_file_count=10) is False


def test_is_substantive_few_commits():
    m = _meta(readme_excerpt="x" * 500, commit_count=4)
    assert is_substantive(m, source_file_count=10) is False


def test_is_substantive_few_source_files():
    m = _meta(readme_excerpt="x" * 500, commit_count=10)
    assert is_substantive(m, source_file_count=4) is False


def test_is_substantive_exact_thresholds_pass():
    """Exactly 200 chars, exactly 5 commits, exactly 5 source files all pass."""
    m = _meta(readme_excerpt="x" * 200, commit_count=5)
    assert is_substantive(m, source_file_count=5) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py::test_is_substantive_passes_all_three_thresholds -v`
Expected: FAIL with `ImportError: cannot import name 'is_substantive'`

- [ ] **Step 3: Implement**

Append to `scripts/repo_discover_lib.py`:

```python
def is_substantive(repo: RepoMeta, source_file_count: int) -> bool:
    """README ≥ 200 chars AND ≥ 5 commits AND ≥ 5 source files."""
    return (
        len(repo.readme_excerpt) >= 200
        and repo.commit_count >= 5
        and source_file_count >= 5
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: PASS — all tests including new is_substantive cases.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_discover_lib.py scripts/tests/test_repo_discover_lib.py
git commit -m "feat(advisor): is_substantive heuristic"
```

---

## Task 3: list_local_repos

**Files:**
- Modify: `scripts/repo_discover_lib.py`
- Modify: `scripts/tests/test_repo_discover_lib.py`

- [ ] **Step 1: Write the failing tests**

Append to `scripts/tests/test_repo_discover_lib.py`:

```python
import subprocess
from repo_discover_lib import list_local_repos, count_source_files


def test_list_local_repos_finds_git_dirs(tmp_path):
    # Make two git repos and one non-git dir
    repo_a = tmp_path / "repo_a"
    repo_a.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo_a, check=True)
    (repo_a / "README.md").write_text("# repo_a\n" + "x" * 300)
    (repo_a / "main.py").write_text("print('hi')")
    subprocess.run(["git", "add", "."], cwd=repo_a, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "-m", "init"], cwd=repo_a, check=True)

    repo_b = tmp_path / "repo_b"
    repo_b.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo_b, check=True)

    plain_dir = tmp_path / "not_a_repo"
    plain_dir.mkdir()
    (plain_dir / "file.txt").write_text("just a file")

    found = list_local_repos([tmp_path])
    names = sorted(r.name for r in found)
    assert names == ["repo_a", "repo_b"]


def test_list_local_repos_one_level_deep_only(tmp_path):
    """A git repo nested two levels deep should NOT be picked up."""
    nested = tmp_path / "wrapper" / "deep_repo"
    nested.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=nested, check=True)

    found = list_local_repos([tmp_path])
    assert found == []


def test_list_local_repos_excludes_self(tmp_path, monkeypatch):
    """A local repo whose origin remote points at this website repo is dropped."""
    self_repo = tmp_path / "dads2busy.github.io"
    self_repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=self_repo, check=True)
    subprocess.run(["git", "remote", "add", "origin",
                    "https://github.com/dads2busy/dads2busy.github.io.git"],
                   cwd=self_repo, check=True)

    found = list_local_repos([tmp_path])
    assert found == []


def test_count_source_files_excludes_known_dirs(tmp_path):
    (tmp_path / "main.py").write_text("a")
    (tmp_path / "lib.py").write_text("b")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.js").write_text("ignored")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")

    # Two source files, ignoring .git, node_modules, and binary png
    assert count_source_files(tmp_path) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v -k "local_repos or count_source_files"`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

Append to `scripts/repo_discover_lib.py`:

```python
import subprocess
from datetime import datetime, timezone
from pathlib import Path

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: PASS — all tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_discover_lib.py scripts/tests/test_repo_discover_lib.py
git commit -m "feat(advisor): list_local_repos + count_source_files"
```

---

## Task 4: list_github_repos

**Files:**
- Modify: `scripts/repo_discover_lib.py`
- Modify: `scripts/tests/test_repo_discover_lib.py`

- [ ] **Step 1: Write the failing tests**

Append to `scripts/tests/test_repo_discover_lib.py`:

```python
import json as _json
from repo_discover_lib import list_github_repos, parse_gh_repo_list


def _gh_payload():
    return _json.dumps([
        {
            "name": "foo", "description": "A demo",
            "primaryLanguage": {"name": "Python"},
            "languages": [{"node": {"name": "Python"}, "size": 1000}],
            "pushedAt": "2026-04-01T10:00:00Z",
            "isArchived": False, "isFork": False,
            "defaultBranchRef": {"name": "main"},
            "url": "https://github.com/dads2busy/foo",
            "owner": {"login": "dads2busy"},
        },
        {
            "name": "fork-of-x", "description": None,
            "primaryLanguage": None,
            "languages": [],
            "pushedAt": "2025-01-01T00:00:00Z",
            "isArchived": False, "isFork": True,
            "defaultBranchRef": {"name": "main"},
            "url": "https://github.com/dads2busy/fork-of-x",
            "owner": {"login": "dads2busy"},
        },
    ])


def test_parse_gh_repo_list_filters_forks():
    parsed = parse_gh_repo_list(_gh_payload())
    names = [r["name"] for r in parsed]
    assert names == ["foo"]


def test_list_github_repos_calls_gh_runner_with_correct_args():
    captured: dict = {}

    def fake_runner(args: list[str]) -> str:
        captured["args"] = args
        return _gh_payload()

    def fake_readme_runner(owner: str, name: str) -> str:
        return "# foo\n" + "x" * 300

    def fake_commit_count(owner: str, name: str) -> int:
        return 12

    repos = list_github_repos(
        "dads2busy",
        gh_runner=fake_runner,
        readme_runner=fake_readme_runner,
        commit_count_runner=fake_commit_count,
    )

    assert captured["args"][0] == "gh"
    assert "repo" in captured["args"]
    assert "list" in captured["args"]
    assert "dads2busy" in captured["args"]
    # Forks filtered, so only one repo
    assert len(repos) == 1
    r = repos[0]
    assert r.name == "foo"
    assert r.owner == "dads2busy"
    assert r.primary_language == "Python"
    assert r.commit_count == 12
    assert r.html_url == "https://github.com/dads2busy/foo"
    assert r.fork is False
    assert "x" * 200 in r.readme_excerpt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v -k "github_repos or gh_repo_list"`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

Append to `scripts/repo_discover_lib.py`:

```python
import json
from typing import Callable

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
            last_commit_sha="",  # gh repo list doesn't return commit sha; use pushedAt for hash
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: PASS — all tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_discover_lib.py scripts/tests/test_repo_discover_lib.py
git commit -m "feat(advisor): list_github_repos via gh CLI"
```

---

## Task 5: merge_repos

**Files:**
- Modify: `scripts/repo_discover_lib.py`
- Modify: `scripts/tests/test_repo_discover_lib.py`

- [ ] **Step 1: Write the failing tests**

Append to `scripts/tests/test_repo_discover_lib.py`:

```python
from repo_discover_lib import merge_repos


def test_merge_repos_dedupes_by_html_url():
    gh = _meta(name="foo", source="github",
               html_url="https://github.com/dads2busy/foo", local_path=None)
    local = _meta(name="foo", source="local", owner=None,
                  html_url="https://github.com/dads2busy/foo",
                  local_path="/Users/x/git/foo")
    merged = merge_repos([gh], [local])
    assert len(merged) == 1
    m = merged[0]
    assert m.source == "github+local"
    assert m.html_url == "https://github.com/dads2busy/foo"
    assert m.local_path == "/Users/x/git/foo"
    assert m.owner == "dads2busy"  # github wins on owner


def test_merge_repos_keeps_unique_local():
    """Local-only repo with no GitHub match stays as-is."""
    local = _meta(name="orphan", source="local", owner=None,
                  html_url=None, local_path="/Users/x/git/orphan")
    merged = merge_repos([], [local])
    assert len(merged) == 1
    assert merged[0].source == "local"


def test_merge_repos_keeps_unique_github():
    gh = _meta(name="cloud-only", source="github",
               html_url="https://github.com/dads2busy/cloud-only")
    merged = merge_repos([gh], [])
    assert len(merged) == 1
    assert merged[0].source == "github"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v -k merge_repos`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

Append to `scripts/repo_discover_lib.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_discover_lib.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_discover_lib.py scripts/tests/test_repo_discover_lib.py
git commit -m "feat(advisor): merge_repos dedupes github+local"
```

---

## Task 6: repo_discover.py entry script

**Files:**
- Create: `scripts/repo_discover.py`

- [ ] **Step 1: Write the script**

```python
# scripts/repo_discover.py
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
```

- [ ] **Step 2: Verify it imports cleanly**

Run: `.venv/bin/python -c "import scripts.repo_discover" 2>&1 | head`
Note: Since `scripts/` lacks `__init__.py`, instead run:
`.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import repo_discover"`
Expected: no output.

- [ ] **Step 3: Skip live run for now (no advisor/ dir yet, no gh-auth assumption in plan).**

This script is exercised by the smoke test in Task 11.

- [ ] **Step 4: Commit**

```bash
git add scripts/repo_discover.py
git commit -m "feat(advisor): repo_discover.py entry script"
```

---

## Task 7: should_resummarize + build_prompt

**Files:**
- Create: `scripts/repo_summarize_lib.py`
- Create: `scripts/tests/test_repo_summarize_lib.py`

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_repo_summarize_lib.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from repo_summarize_lib import should_resummarize, build_prompt
from repo_discover_lib import RepoMeta, content_hash


def _meta(**overrides) -> RepoMeta:
    defaults = dict(
        name="foo", owner="dads2busy", source="github",
        description="A demo", primary_language="Python",
        languages={"Python": 1000}, last_commit_date="2026-04-01",
        last_commit_sha="abc", commit_count=10, archived=False,
        fork=False, default_branch="main",
        html_url="https://github.com/dads2busy/foo",
        local_path=None, readme_excerpt="x" * 500,
        manifest_files=["pyproject.toml"], substantive=True, paragraph=None,
    )
    defaults.update(overrides)
    return RepoMeta(**defaults)


def test_should_resummarize_non_substantive_returns_false():
    m = _meta(substantive=False)
    assert should_resummarize(m, prior_index={}) is False


def test_should_resummarize_no_prior_entry_returns_true():
    m = _meta()
    assert should_resummarize(m, prior_index={}) is True


def test_should_resummarize_hash_changed_returns_true():
    m = _meta(readme_excerpt="new readme " * 50)
    prior = {"foo": {"content_hash": "olddigest", "paragraph": "old para"}}
    assert should_resummarize(m, prior_index=prior) is True


def test_should_resummarize_hash_match_with_paragraph_returns_false():
    m = _meta()
    prior = {"foo": {"content_hash": content_hash(m), "paragraph": "fine"}}
    assert should_resummarize(m, prior_index=prior) is False


def test_should_resummarize_hash_match_no_paragraph_returns_true():
    m = _meta()
    prior = {"foo": {"content_hash": content_hash(m), "paragraph": None}}
    assert should_resummarize(m, prior_index=prior) is True


def test_build_prompt_includes_readme_lang_manifests():
    m = _meta(readme_excerpt="THE README", primary_language="Python",
              manifest_files=["pyproject.toml", "Dockerfile"])
    prompt = build_prompt(m)
    assert "THE README" in prompt
    assert "Python" in prompt
    assert "pyproject.toml" in prompt
    assert "Dockerfile" in prompt


def test_build_prompt_includes_archived_flag():
    m = _meta(archived=True)
    prompt = build_prompt(m)
    assert "archived" in prompt.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_summarize_lib.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'repo_summarize_lib'`.

- [ ] **Step 3: Implement**

```python
# scripts/repo_summarize_lib.py
"""Pure helpers for the summarization stage. Anthropic client is injected."""

from __future__ import annotations

from typing import Any, Callable

from repo_discover_lib import RepoMeta, content_hash

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 400  # ~300 token output cap with headroom


def should_resummarize(meta: RepoMeta, prior_index: dict[str, dict[str, Any]]) -> bool:
    """True iff this repo is substantive AND lacks a usable cached paragraph."""
    if not meta.substantive:
        return False
    prior = prior_index.get(meta.name)
    if prior is None:
        return True
    if prior.get("content_hash") != content_hash(meta):
        return True
    if not prior.get("paragraph"):
        return True
    return False


def build_prompt(meta: RepoMeta) -> str:
    archived = " (ARCHIVED)" if meta.archived else ""
    manifests = ", ".join(meta.manifest_files) if meta.manifest_files else "(none detected)"
    langs = ", ".join(f"{k}: {v}b" for k, v in
                      sorted(meta.languages.items(), key=lambda kv: -kv[1])[:5]) or "(none)"
    return f"""You are summarizing one of Aaron Schroeder's code repositories for a personal career-context document. Aaron is a research scientist who builds tooling alongside his academic work.

Write ONE paragraph (150-300 tokens) describing this repo:
- What it is / what problem it solves
- Status (active / dormant / experimental)
- Notable technical choices or outputs

Be specific. Don't restate metadata I'm already giving you. No headings, no bullets, no preamble — just the paragraph.

---
Repo: {meta.name}{archived}
Description: {meta.description or "(none)"}
Primary language: {meta.primary_language or "(unknown)"}
Languages: {langs}
Manifests: {manifests}
Last commit: {meta.last_commit_date}
Commits: {meta.commit_count}
URL: {meta.html_url or "(local-only)"}

README:
{meta.readme_excerpt}
"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_summarize_lib.py -v`
Expected: PASS — 7 tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_summarize_lib.py scripts/tests/test_repo_summarize_lib.py
git commit -m "feat(advisor): should_resummarize + build_prompt"
```

---

## Task 8: summarize_repo

**Files:**
- Modify: `scripts/repo_summarize_lib.py`
- Modify: `scripts/tests/test_repo_summarize_lib.py`

- [ ] **Step 1: Write the failing tests**

Append to `scripts/tests/test_repo_summarize_lib.py`:

```python
from repo_summarize_lib import summarize_repo


class _FakeClient:
    """Minimal stand-in for anthropic.Anthropic; records the prompt it received."""
    def __init__(self, response_text: str = "A great repo paragraph."):
        self.response_text = response_text
        self.captured_prompt: str | None = None
        self.messages = self  # mimic client.messages.create

    def create(self, *, model, max_tokens, messages, **kwargs):
        # Capture the user prompt
        self.captured_prompt = messages[0]["content"]
        # Mimic anthropic response shape
        class Block:
            def __init__(self, t):
                self.type = "text"
                self.text = t
        class Resp:
            def __init__(self, t):
                self.content = [Block(t)]
        return Resp(self.response_text)


def test_summarize_repo_returns_paragraph_text():
    fake = _FakeClient("Foo is a small Python tool for X.")
    m = _meta()
    result = summarize_repo(m, fake)
    assert result == "Foo is a small Python tool for X."


def test_summarize_repo_passes_built_prompt():
    fake = _FakeClient()
    m = _meta(readme_excerpt="UNIQUE_README_TOKEN content " * 20)
    summarize_repo(m, fake)
    assert "UNIQUE_README_TOKEN" in fake.captured_prompt


def test_summarize_repo_uses_haiku_model():
    fake = _FakeClient()
    captured = {}
    orig_create = fake.create
    def wrapper(**kwargs):
        captured.update(kwargs)
        return orig_create(**kwargs)
    fake.create = wrapper
    summarize_repo(_meta(), fake)
    assert captured["model"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest scripts/tests/test_repo_summarize_lib.py -v -k summarize_repo`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

Append to `scripts/repo_summarize_lib.py`:

```python
def summarize_repo(meta: RepoMeta, claude_client: Any) -> str:
    """Call Haiku via injected client. Returns paragraph text or '' on text-block miss."""
    prompt = build_prompt(meta)
    resp = claude_client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            return block.text.strip()
    return ""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest scripts/tests/test_repo_summarize_lib.py -v`
Expected: PASS — 10 tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_summarize_lib.py scripts/tests/test_repo_summarize_lib.py
git commit -m "feat(advisor): summarize_repo via Haiku"
```

---

## Task 9: repo_summarize.py entry script

**Files:**
- Create: `scripts/repo_summarize.py`

- [ ] **Step 1: Write the script**

```python
# scripts/repo_summarize.py
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
```

- [ ] **Step 2: Verify import**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import repo_summarize"`
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add scripts/repo_summarize.py
git commit -m "feat(advisor): repo_summarize.py with skip-unchanged caching"
```

---

## Task 10: repo_render.py

**Files:**
- Create: `scripts/repo_render.py`

- [ ] **Step 1: Write the script**

```python
# scripts/repo_render.py
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
```

- [ ] **Step 2: Verify import**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import repo_render"`
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add scripts/repo_render.py
git commit -m "feat(advisor): repo_render.py emits repos.md"
```

---

## Task 11: End-to-end smoke test

**Files:**
- Create: `scripts/tests/test_repo_pipeline_smoke.py`

- [ ] **Step 1: Write the test**

```python
# scripts/tests/test_repo_pipeline_smoke.py
"""End-to-end smoke: run discover (with mocks) → summarize (with mock client) → render.
Verifies the three entry scripts compose without crashing and produce expected sections."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def test_render_produces_expected_sections(tmp_path, monkeypatch):
    """Build a fake repos_index.json by hand, run repo_render, inspect repos.md."""
    advisor = tmp_path / "advisor"
    advisor.mkdir()
    (advisor / "profile.yaml").symlink_to(tmp_path / "fake_profile.yaml")
    (tmp_path / "fake_profile.yaml").write_text("# fake profile")

    index = [
        {
            "name": "alpha", "owner": "dads2busy", "source": "github",
            "description": "Substantive thing", "primary_language": "Python",
            "languages": {"Python": 5000}, "last_commit_date": "2026-04-01",
            "last_commit_sha": "aaa", "commit_count": 50, "archived": False,
            "fork": False, "default_branch": "main",
            "html_url": "https://github.com/dads2busy/alpha",
            "local_path": None, "readme_excerpt": "x" * 500,
            "manifest_files": ["pyproject.toml"], "substantive": True,
            "paragraph": "Alpha is a substantive paragraph.",
            "content_hash": "h1",
        },
        {
            "name": "beta", "owner": "dads2busy", "source": "github",
            "description": "Stub", "primary_language": "JavaScript",
            "languages": {"JavaScript": 100}, "last_commit_date": "2024-01-01",
            "last_commit_sha": "bbb", "commit_count": 1, "archived": False,
            "fork": False, "default_branch": "main",
            "html_url": "https://github.com/dads2busy/beta",
            "local_path": None, "readme_excerpt": "tiny", "manifest_files": [],
            "substantive": False, "paragraph": None, "content_hash": "h2",
        },
        {
            "name": "gamma", "owner": "dads2busy", "source": "github",
            "description": "old", "primary_language": "Python",
            "languages": {"Python": 200}, "last_commit_date": "2022-06-15",
            "last_commit_sha": "ccc", "commit_count": 8, "archived": True,
            "fork": False, "default_branch": "main",
            "html_url": "https://github.com/dads2busy/gamma",
            "local_path": None, "readme_excerpt": "y" * 250,
            "manifest_files": ["setup.py"], "substantive": True,
            "paragraph": "Gamma is an archived but substantive thing.",
            "content_hash": "h3",
        },
    ]
    (advisor / "repos_index.json").write_text(json.dumps(index, indent=2))

    monkeypatch.setattr(
        "repo_render.REPO_ROOT", tmp_path,
    )
    monkeypatch.setattr("repo_render.ADVISOR_DIR", advisor)
    monkeypatch.setattr("repo_render.INDEX_PATH", advisor / "repos_index.json")
    monkeypatch.setattr("repo_render.MD_PATH", advisor / "repos.md")

    import repo_render
    repo_render.main()

    md = (advisor / "repos.md").read_text()
    assert "## Substantive projects" in md
    assert "## Other repos" in md
    assert "Alpha is a substantive paragraph." in md
    assert "Gamma is an archived but substantive thing." in md
    # Non-substantive beta lives in the table
    assert "| dads2busy/beta |" in md
    # Substantive list sorted desc by date: alpha (2026) before gamma (2022)
    alpha_idx = md.index("Alpha is a substantive")
    gamma_idx = md.index("Gamma is an archived")
    assert alpha_idx < gamma_idx
```

- [ ] **Step 2: Run the test**

Run: `.venv/bin/pytest scripts/tests/test_repo_pipeline_smoke.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/test_repo_pipeline_smoke.py
git commit -m "test(advisor): end-to-end smoke for render"
```

---

## Task 12: advisor/ directory + symlink + README

**Files:**
- Create: `advisor/README.md`
- Create: `advisor/profile.yaml` (symlink)

- [ ] **Step 1: Create the directory and symlink**

```bash
mkdir -p advisor
cd advisor && ln -s ../site/content/profile.yaml profile.yaml && cd ..
ls -la advisor/
```

Expected: `profile.yaml -> ../site/content/profile.yaml`.

- [ ] **Step 2: Verify the symlink resolves**

Run: `head -3 advisor/profile.yaml`
Expected: first lines of the actual `site/content/profile.yaml`.

- [ ] **Step 3: Write advisor/README.md**

```markdown
# Aaron's career-context directory

This directory exists so I can ask Claude Code (or any LLM with prompt
caching) synthesis questions about my career — research, code, teaching —
without having to load every artifact by hand.

## What's here

- `profile.yaml` (symlink → `../site/content/profile.yaml`) — RenderCV SSOT
  covering publications, projects, teaching, speaking, biography.
- `repos.md` — auto-generated per-repo summary covering every dads2busy
  GitHub repo and every local-only repo under `~/git/*`. Tier-1 header for
  every repo; tier-2 paragraph for substantive ones (README ≥ 200 chars,
  ≥ 5 commits, ≥ 5 source files).
- `repos_index.json` — machine-readable companion to repos.md.

## How to use

```bash
cd advisor
claude
```

Then ask things like:

- *"Given everything you know about me, what's a good direction for my research career?"*
- *"Which of my repos most closely relate to the publications listed in profile.yaml?"*
- *"Are there obvious gaps between my published work and the tooling I've built?"*

For drill-down (e.g., "tell me more about repo X"), Claude Code's `Read`,
`Bash`/`gh`, and `WebFetch` tools work out of the box.

## Refresh

A weekly GitHub Action (`.github/workflows/refresh-advisor.yml`,
Mondays 9am UTC) regenerates `repos.md` and `repos_index.json` and opens
a PR with the diff. Manually:

```bash
.venv/bin/python scripts/repo_discover.py
.venv/bin/python scripts/repo_summarize.py    # needs ANTHROPIC_API_KEY
.venv/bin/python scripts/repo_render.py
```
```

- [ ] **Step 4: Commit**

```bash
git add advisor/README.md advisor/profile.yaml
git commit -m "feat(advisor): create advisor/ directory with profile.yaml symlink"
```

---

## Task 13: First real run — populate repos_index.json and repos.md

**Files:**
- Create: `advisor/repos_index.json` (generated)
- Create: `advisor/repos.md` (generated)

- [ ] **Step 1: Verify gh auth**

Run: `gh auth status`
Expected: logged in as the dads2busy account (or another account with access). If not, run `gh auth login`.

- [ ] **Step 2: Run discovery**

Run: `.venv/bin/python scripts/repo_discover.py`
Expected: stderr shows `github: N repos`, `local: M repos`, `wrote .../advisor/repos_index.json with K repos`.

- [ ] **Step 3: Sanity check the index**

Run: `.venv/bin/python -c "import json; d=json.load(open('advisor/repos_index.json')); print(f'{len(d)} repos, {sum(1 for e in d if e[\"substantive\"])} substantive')"`
Expected: a non-zero count.

- [ ] **Step 4: Run summarization**

Run: `ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY .venv/bin/python scripts/repo_summarize.py`
Expected: stderr shows `summarizing N of M repos` followed by per-repo `done: name (X chars)`. Cost ≈ $0.05–0.10 on the first run.

- [ ] **Step 5: Run render**

Run: `.venv/bin/python scripts/repo_render.py`
Expected: `wrote .../advisor/repos.md (X chars)`.

- [ ] **Step 6: Eyeball the output**

Run: `head -80 advisor/repos.md`
Expected: heading, "Substantive projects" section with at least one paragraph, "Other repos" table.

- [ ] **Step 7: Commit**

```bash
git add advisor/repos_index.json advisor/repos.md
git commit -m "feat(advisor): initial repos.md + repos_index.json snapshot"
```

---

## Task 14: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/refresh-advisor.yml`

- [ ] **Step 1: Write the workflow**

```yaml
# .github/workflows/refresh-advisor.yml
name: Refresh advisor repo index

on:
  schedule:
    - cron: '0 9 * * 1'   # Mondays 09:00 UTC
  workflow_dispatch: {}

permissions:
  contents: write
  pull-requests: write

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # repo_summarize.py reads HEAD:advisor/repos_index.json

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r scripts/requirements.txt

      - name: Discover repos
        env:
          GH_TOKEN: ${{ secrets.GH_PAT_PRIVATE_REPOS || secrets.GITHUB_TOKEN }}
          ADVISOR_LOCAL_ROOTS: ""   # CI: no local-only scan
        run: python scripts/repo_discover.py

      - name: Summarize substantive repos
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/repo_summarize.py

      - name: Render repos.md
        run: python scripts/repo_render.py

      - name: Open PR if changed
        uses: peter-evans/create-pull-request@v6
        with:
          branch: chore/refresh-advisor
          delete-branch: true
          commit-message: "chore(advisor): refresh repo index"
          title: "chore(advisor): refresh repo index"
          body: |
            Weekly auto-refresh of `advisor/repos.md` and `advisor/repos_index.json`.

            Review the diff and merge. If a repo's paragraph reads oddly, that
            repo's `content_hash` will keep firing it back through Haiku next week
            until the README stabilizes.
          add-paths: |
            advisor/repos.md
            advisor/repos_index.json
```

- [ ] **Step 2: Validate the YAML syntax**

Run: `.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh-advisor.yml'))"`
Expected: no output.

- [ ] **Step 3: Document required secrets in advisor/README.md**

Append to `advisor/README.md`:

```markdown

## Required GitHub secrets (for CI)

- `ANTHROPIC_API_KEY` — Haiku 4.5 calls.
- `GH_PAT_PRIVATE_REPOS` (optional) — PAT with `repo:read` if you want CI
  to discover private dads2busy repos. Without it, CI uses
  `secrets.GITHUB_TOKEN` which only sees public repos.
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/refresh-advisor.yml advisor/README.md
git commit -m "ci(advisor): weekly refresh workflow"
```

---

## Task 15: Verify the full pipeline once more, then push

- [ ] **Step 1: Run the full test suite**

Run: `.venv/bin/pytest scripts/tests/ -v`
Expected: all tests pass.

- [ ] **Step 2: Trigger the workflow manually after push**

After pushing master, go to the GitHub Actions tab → "Refresh advisor repo index" → "Run workflow". Watch the run. If a PR is opened titled `chore(advisor): refresh repo index`, merge it. If the run produces no diff, that's expected (the index was already current from Task 13).

- [ ] **Step 3: Try the advisor**

```bash
cd advisor
claude
```

Then ask: *"Given everything you know about me from profile.yaml and repos.md, what's a coherent direction for the next 12 months of my research?"* Verify the answer references both publications and specific repos.

---

## Self-review notes

- Spec coverage: every section of the spec maps to a task. Discovery → Tasks 1–6, summarization → Tasks 7–9, render → Task 10, smoke → Task 11, advisor directory → Task 12, first run → Task 13, CI → Task 14, end-to-end verification → Task 15.
- One spec deviation: the spec's `RepoMeta` includes `last_commit_sha`, but `gh repo list` doesn't return commit SHAs. For GitHub-only records we leave `last_commit_sha = ""` and `content_hash` falls back to `last_commit_date` (the `pushedAt` value), so push events still bust the cache. Local repos populate `last_commit_sha` directly via `git log`. Test `test_content_hash_falls_back_to_last_commit_date_when_sha_empty` covers the fallback.
- One spec extension: `count_source_files()` was added as a public helper in `repo_discover_lib.py` because `is_substantive` needs it for local repos and the GitHub branch approximates "substantive source-file count" via `len(languages) >= 1`. Documented inline.
