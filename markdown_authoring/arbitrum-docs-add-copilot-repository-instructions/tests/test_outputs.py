"""Behavioral checks for arbitrum-docs-add-copilot-repository-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/arbitrum-docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The Husky pre-commit hook (`.husky/pre-commit`) runs Prettier, markdownlint, and `yarn typecheck` on staged files. It skips in CI (`HUSKY=0`, `CI=true`, or `GITHUB_ACTIONS=true` disables it). Do not' in text, "expected to find: " + '- The Husky pre-commit hook (`.husky/pre-commit`) runs Prettier, markdownlint, and `yarn typecheck` on staged files. It skips in CI (`HUSKY=0`, `CI=true`, or `GITHUB_ACTIONS=true` disables it). Do not'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. **Format (Prettier).** The `main.yml` workflow runs `yarn format:check`. Always run `yarn format` before committing — the pre-commit hook will reformat staged files but only if you run Prettier on ' in text, "expected to find: " + '4. **Format (Prettier).** The `main.yml` workflow runs `yarn format:check`. Always run `yarn format` before committing — the pre-commit hook will reformat staged files but only if you run Prettier on '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repo is the source for [docs.arbitrum.io](https://docs.arbitrum.io), built with Docusaurus. Content is the product. Trust these instructions; only search the repo when something here is incomplet' in text, "expected to find: " + 'This repo is the source for [docs.arbitrum.io](https://docs.arbitrum.io), built with Docusaurus. Content is the product. Trust these instructions; only search the repo when something here is incomplet'[:80]

