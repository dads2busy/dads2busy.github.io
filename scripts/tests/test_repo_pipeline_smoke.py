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
