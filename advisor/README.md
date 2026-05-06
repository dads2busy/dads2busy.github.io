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

## Required GitHub secrets (for CI)

- `ANTHROPIC_API_KEY` — Haiku 4.5 calls.
- `GH_PAT_PRIVATE_REPOS` (optional) — PAT with `repo:read` if you want CI
  to discover private dads2busy repos. Without it, CI uses
  `secrets.GITHUB_TOKEN` which only sees public repos.
