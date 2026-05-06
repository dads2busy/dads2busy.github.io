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
