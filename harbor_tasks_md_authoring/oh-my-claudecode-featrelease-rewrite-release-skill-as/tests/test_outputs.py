"""Behavioral checks for oh-my-claudecode-featrelease-rewrite-release-skill-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oh-my-claudecode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/AGENTS.md')
    assert '| `release/SKILL.md` | release | Generic release assistant — analyzes repo CI/rules, caches in `.omc/RELEASE_RULE.md`, guides the release |' in text, "expected to find: " + '| `release/SKILL.md` | release | Generic release assistant — analyzes repo CI/rules, caches in `.omc/RELEASE_RULE.md`, guides the release |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert '**If it DOES exist:** Read the file. Then do a quick delta check — scan `.github/workflows/` (or equivalent CI dirs: `.circleci/`, `.travis.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml`, `gitlab-ci.y' in text, "expected to find: " + '**If it DOES exist:** Read the file. Then do a quick delta check — scan `.github/workflows/` (or equivalent CI dirs: `.circleci/`, `.travis.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml`, `gitlab-ci.y'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert 'A thin, repo-aware release assistant. On first run it inspects the project and CI to derive release rules, stores them in `.omc/RELEASE_RULE.md` for future use, then walks you through a release using ' in text, "expected to find: " + 'A thin, repo-aware release assistant. On first run it inspects the project and CI to derive release rules, stores them in `.omc/RELEASE_RULE.md` for future use, then walks you through a release using '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert '- npm (`package.json` with `publishConfig` or `npm publish` in CI), PyPI (`pyproject.toml` + `twine`/`flit`), Cargo (`Cargo.toml`), Docker (`Dockerfile` + push step), GitHub Packages, other.' in text, "expected to find: " + '- npm (`package.json` with `publishConfig` or `npm publish` in CI), PyPI (`pyproject.toml` + `twine`/`flit`), Cargo (`Cargo.toml`), Docker (`Dockerfile` + push step), GitHub Packages, other.'[:80]

