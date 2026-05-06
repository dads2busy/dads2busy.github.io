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
