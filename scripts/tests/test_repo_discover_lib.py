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
