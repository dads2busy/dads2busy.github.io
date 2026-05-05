# Advisor: repo-summary pipeline

**Status:** design approved 2026-05-05; pending implementation plan.

## Purpose

Aaron wants a personal LLM-accessible knowledge base he can point Claude Code at to ask synthesis questions like *"Given everything you know about me, what would be a good direction for my research career?"*. `site/content/profile.yaml` (RenderCV SSOT) already covers his publications, projects, teaching, speaking, and biographical record. What's missing is current and historical engineering work scattered across his GitHub account and local-only project directories.

This spec defines an offline pipeline that produces a stable, cacheable, LLM-friendly summary of every repo Aaron has authored, refreshed weekly. The pipeline emits two artifacts that live alongside `profile.yaml` in an `advisor/` directory; Claude Code reads them as cached context.

## Constraints and decisions

These were settled during brainstorming and are not open for revisitation in the implementation plan unless explicitly noted:

| Decision | Choice |
|---|---|
| **Harness** | Claude Code, run as `cd advisor/ && claude`. No custom app. |
| **Repo scope** | `github.com/dads2busy/*` (public + private + archived) **plus** local-only repos under `~/git/*` (one level deep). Skip forks. Skip other GitHub accounts. |
| **Summary depth** | Tiered — short structured header for every repo; longer free-text paragraph only for substantive repos (README ≥ 200 chars **and** ≥ 5 commits **and** ≥ 5 source files). |
| **Refresh cadence** | Weekly GitHub Action on `0 9 * * 1` (Mondays 9am UTC). Opens a PR with the diff. |
| **Pipeline shape** | Modular: `repo_discover_lib.py` + `repo_summarize_lib.py` (pure libraries) wrapped by `repo_discover.py`, `repo_summarize.py`, `repo_render.py` (entry scripts). Mirrors the existing `profile_lib.py` / `json_emitters.py` / `profile_to_content_jsons.py` separation. |
| **Artifacts** | Both `advisor/repos.md` (LLM context) **and** `advisor/repos_index.json` (machine-readable sidecar). |
| **Location** | `advisor/` subdirectory at repo root in `dads2busy.github.io`. `advisor/profile.yaml` is a symlink to `../site/content/profile.yaml`. |
| **Substantive heuristic** | Fixed (not config-driven): README ≥ 200 chars AND ≥ 5 commits AND ≥ 5 source files. |
| **Summarization model** | Haiku 4.5 (`claude-haiku-4-5-20251001`). |
| **Skip-unchanged caching** | `content_hash = sha256(name + last_commit_sha + readme_excerpt + primary_language)`. Unchanged repos do not call Haiku. |
| **CI handling of local-only repos** | Skipped in CI (the runner has no `~/git/`). Local repos are picked up only when the script runs on Aaron's Mac. |

## Architecture

```
┌─ Discovery ─────────────┐    ┌─ Summarization ─────────┐    ┌─ Render ────┐
│  gh repo list dads2busy │    │  for each substantive   │    │  json →     │
│  glob ~/git/*           │ →  │  repo: Haiku writes a   │ →  │  markdown   │
│  → repos_index.json     │    │  paragraph              │    │             │
│  (raw metadata)         │    │  → repos_index.json     │    │             │
└─────────────────────────┘    └─────────────────────────┘    └─────────────┘
                                                                     │
                                                                     ▼
                                                              advisor/repos.md
                                                              advisor/repos_index.json
```

**Outputs:**
- `advisor/repos.md` — what Claude Code reads. Tier-1 header for every repo; tier-2 paragraph for substantive ones. Estimated ~40K tokens at ~150 repos.
- `advisor/repos_index.json` — full structured data; LLM-paragraph cache key; useful for queries and future tooling.
- `advisor/profile.yaml` — symlink to `../site/content/profile.yaml`.
- `advisor/README.md` — committed; explains the directory's purpose and how to use it with Claude Code.

**Consumption:** `cd advisor/ && claude` loads the directory; SSOT and repo summaries enter context. Drill-down questions use Claude Code's existing tools (`Read`, `Bash`/`gh`, `WebFetch`).

## Components

### `scripts/repo_discover_lib.py` (pure library)

Pure functions. No network, no LLM, no I/O beyond what's passed in. Caller injects runners (subprocess for `gh`, filesystem for local) so tests can substitute fakes.

- `list_github_repos(owner: str, gh_runner) -> list[RepoMeta]` — wraps `gh repo list <owner> --limit 500 --json name,description,primaryLanguage,languages,pushedAt,isArchived,isFork,defaultBranchRef,url,owner`. Filters out forks. Includes archived.
- `list_local_repos(roots: list[Path]) -> list[RepoMeta]` — globs each root one level deep, keeps directories with a `.git/` child. Excludes the website repo itself (any local repo whose `git remote get-url origin` resolves to `github.com/dads2busy/dads2busy.github.io` is dropped from the local list — it will already appear via the GitHub query).
- `merge_repos(github: list[RepoMeta], local: list[RepoMeta]) -> list[RepoMeta]` — dedupes by remote URL. If a local repo's `git remote get-url origin` matches a GitHub record, the GitHub record wins but `local_path` is preserved.
- `is_substantive(repo: RepoMeta) -> bool` — README ≥ 200 chars AND ≥ 5 commits AND ≥ 5 source files. (Source files: anything under the repo root, recursive, excluding `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `dist/`, `build/`, and binary extensions.)
- `content_hash(repo: RepoMeta) -> str` — `sha256(name + last_commit_sha + readme_excerpt + primary_language)`.

`RepoMeta` is a `@dataclass`:

```python
name: str
owner: str | None              # None for local-only
source: Literal["github", "local", "github+local"]
description: str | None
primary_language: str | None
languages: dict[str, int]      # language → byte count
last_commit_date: str          # ISO-8601
last_commit_sha: str
commit_count: int
archived: bool
fork: bool                     # always False after filtering
default_branch: str
html_url: str | None           # None for local-only without remote
local_path: str | None         # absolute path or None
readme_excerpt: str            # first ≤ 2000 chars; truncation marker if longer
manifest_files: list[str]      # detected: pyproject.toml, package.json, etc.
substantive: bool
content_hash: str
paragraph: str | None          # populated by summarize stage; None on stub repos
```

### `scripts/repo_discover.py` (entry script)

Thin runner. Reads config (owner = `dads2busy`; local roots from env `ADVISOR_LOCAL_ROOTS` defaulting to `~/git/` if it exists, empty in CI). Calls the lib. Atomically writes `advisor/repos_index.json`. **Does not call any LLM.**

### `scripts/repo_summarize_lib.py` (pure library)

- `should_resummarize(meta: RepoMeta, prior_index: dict) -> bool` — true iff `meta.substantive` AND (`prior_index` has no entry for this repo OR prior `content_hash` differs OR prior `paragraph` is missing).
- `build_prompt(meta: RepoMeta) -> str` — assembles README excerpt, manifest list, language breakdown, last-commit date, archived flag, description into a Haiku prompt.
- `summarize_repo(meta: RepoMeta, claude_client) -> str` — calls Haiku 4.5 via injected client; returns a 150–300-token paragraph.
- README handling: if the README is > 50KB, truncate to first 2000 chars + last 500 chars with an explicit `[... truncated ...]` marker.

### `scripts/repo_summarize.py` (entry script)

1. Loads current `advisor/repos_index.json`.
2. Loads prior index from git: `git show HEAD:advisor/repos_index.json` (silently treats `not found` as empty).
3. For each repo with `should_resummarize == True`, calls Haiku. Concurrent with a `Semaphore(5)`.
4. Sanity guard: if the count of repos to resummarize > 200, abort with an explicit error (suggests a hash-computation bug, not a real refresh).
5. Writes `advisor/repos_index.json` atomically (`tmp` + `os.replace`). Idempotent.

### `scripts/repo_render.py` (entry script)

Reads `advisor/repos_index.json`. Emits `advisor/repos.md` with this structure:

```markdown
# Aaron's repos (auto-generated YYYY-MM-DD)

## Substantive projects

### dads2busy/foo · Python · active · last commit 2026-04-12
<paragraph>

### …

## Other repos
| name | language | last commit | status |
| --- | --- | --- | --- |
| … | … | … | … |
```

Substantive repos are sorted by `last_commit_date` descending. Other repos in a compact table, same sort.

### `advisor/`

- `repos.md` (generated, committed)
- `repos_index.json` (generated, committed)
- `profile.yaml` → symlink to `../site/content/profile.yaml` (committed)
- `README.md` (hand-written) — explains what this directory is and how to use `cd advisor/ && claude`.

### Tests

`scripts/tests/test_repo_discover_lib.py`:
- `merge_repos` — github+local with matching remote → single merged record carrying `local_path`.
- `is_substantive` — table-driven over the three thresholds; edge cases at exactly 5 commits, exactly 200 chars, exactly 5 source files.
- `list_local_repos` — pytest `tmp_path` fixture with a mix of git-repos / non-git-dirs / nested dirs; verifies one-level-deep, `.git`-bearing dirs only.
- `list_github_repos` — fake `gh_runner` returning canned JSON; verifies parsing and fork-filter.
- `content_hash` — stable across runs with same inputs; changes when any input field changes.

`scripts/tests/test_repo_summarize_lib.py`:
- `should_resummarize` — full matrix of (paragraph present?, hash match?, substantive?) → expected bool.
- `summarize_repo` — fake `claude_client` returning a canned paragraph; asserts the prompt contains README excerpt, language, manifest list.
- README truncation — 60KB input → head+tail+marker.

`scripts/tests/test_repo_pipeline_smoke.py`:
- End-to-end with three fake repos (one substantive, one stub, one archived). Mocks `gh` and Anthropic. Asserts `repos.md` has expected sections and paragraph counts.

**Not tested:** the GH Action YAML, exact Haiku wording, symlink creation.

## Data flow

1. **Trigger** — GH Action cron `0 9 * * 1`. Locally: `python scripts/repo_discover.py && python scripts/repo_summarize.py && python scripts/repo_render.py`.
2. **Discover** — `repo_discover.py` queries `gh`, optionally globs `~/git/*` if present, computes `content_hash` per repo, writes `advisor/repos_index.json`.
3. **Preserve** — `repo_summarize.py` loads prior `advisor/repos_index.json` from `git show HEAD:advisor/repos_index.json`. Any repo whose new `content_hash` matches the prior one inherits its prior paragraph for free.
4. **Summarize** — Haiku is called only for substantive repos with a stale or missing paragraph. Concurrent with `Semaphore(5)`. Paragraphs are written back into `repos_index.json`.
5. **Render** — `repo_render.py` produces `advisor/repos.md`.
6. **CI commit** — GH Action diffs `advisor/repos.md` and `advisor/repos_index.json`; if either changed, opens a PR titled `chore(advisor): refresh repo index YYYY-MM-DD`.

### Cost estimate

- First full run: ~50 substantive repos × ~3K input tokens + 300 output tokens × Haiku 4.5 pricing ≈ **$0.05–0.10**.
- Subsequent weekly runs: only repos whose hash changed (~5–10 in a typical week) get re-summarized → near-zero.

## Error handling

| Failure | Handling |
|---|---|
| `gh` not authenticated (local) | Hard-fail: `Run 'gh auth login' first`. |
| `GH_TOKEN` missing or invalid (CI) | Hard-fail. Workflow sets `GH_TOKEN` from `secrets.GITHUB_TOKEN` for public; private repos require `secrets.GH_PAT_PRIVATE_REPOS` (PAT with `repo:read`). |
| `gh` rate limit (HTTP 403/429) | Exponential backoff, 3 attempts. Then hard-fail (partial discovery would silently drop repos). |
| `ANTHROPIC_API_KEY` missing | Hard-fail in `repo_summarize.py`. Discovery and render still run independently. |
| Anthropic API transient error | Retry once. On second failure: log warning, leave paragraph empty, continue. |
| Anthropic API quota/auth error | Hard-fail (config problem, not transient). |
| README missing | Skip tier-2 paragraph. Tier-1 entry still appears with `(no README)` marker. |
| README > 50KB | Truncate: first 2000 chars + last 500 chars with explicit marker. |
| Local dir under `~/git/*` not a git repo | Silently skip. |
| Local repo with 0 commits | Skip — `is_substantive()` returns false. |
| `advisor/profile.yaml` symlink target missing | Render hard-fails: `profile.yaml symlink broken — run from repo root`. |
| Unicode / encoding errors in READMEs | Decode with `errors='replace'`; per-repo warning log. |

**Atomic writes:** Each entry script writes its output via `tmp` + `os.replace`. Crashes mid-run leave the prior file intact; on restart, surviving paragraphs are preserved by step 3.

**Cost guard:** `repo_summarize.py` aborts if `len(repos_to_resummarize) > 200`.

## GitHub Action

`.github/workflows/refresh-advisor.yml` (new file):

- Trigger: `schedule: cron: '0 9 * * 1'` plus `workflow_dispatch` for manual runs.
- Steps, in order: checkout → setup Python 3.12 → `pip install -r scripts/requirements.txt` → `python scripts/repo_discover.py` → `python scripts/repo_summarize.py` → `python scripts/repo_render.py` → `peter-evans/create-pull-request@v6` with branch `chore/refresh-advisor`.
- Secrets needed: `GH_PAT_PRIVATE_REPOS` (PAT with `repo:read` for private dads2busy repos), `ANTHROPIC_API_KEY`.

## Out of scope

- Other GitHub accounts beyond `dads2busy/*`.
- Forks.
- The advisor *consuming* the artifacts (that's just `cd advisor/ && claude` — no code).
- Cross-linking publications in `profile.yaml` to specific repos. (Could be a follow-up; for now the LLM does it implicitly from what's in context.)
- Changing or extending `profile.yaml` itself.

## Open questions for the implementation plan

- Exact `gh` JSON field names — verify against current `gh` CLI version when implementing.
- Whether `repo_discover.py` should clone repos to read READMEs, or rely on `gh api repos/{owner}/{repo}/readme` per repo (`gh repo list` does not return README content directly). Implementation detail.
- How to obtain `commit_count` for GitHub-only repos. Local repos use `git rev-list --count HEAD`. GitHub-only options: parse `Link` header from `gh api repos/{owner}/{repo}/commits?per_page=1`, or use a GraphQL `defaultBranchRef.target.history.totalCount` query. The plan should pick one and apply it consistently.
- Concrete `peter-evans/create-pull-request` config (branch naming, labels, draft vs ready).
