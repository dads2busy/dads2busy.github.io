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
