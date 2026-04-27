"""Behavioral checks for rtk-featskills-add-prreview-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rtk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'Hey @<author>, good fix on [description spécifique]. One thing to address before merge: the branch has a conflict on [fichier] after recent changes to develop. A `git rebase origin/develop` should res' in text, "expected to find: " + 'Hey @<author>, good fix on [description spécifique]. One thing to address before merge: the branch has a conflict on [fichier] after recent changes to develop. A `git rebase origin/develop` should res'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert "Hey @<author>, thanks for [description spécifique]. The only thing blocking merge is the CLA signature — the CLAassistant bot left the link in the PR. Once that's done, we're good to go." in text, "expected to find: " + "Hey @<author>, thanks for [description spécifique]. The only thing blocking merge is the CLA signature — the CLAassistant bot left the link in the PR. Once that's done, we're good to go."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert "Puis **vérifier que la PR suivante n'est pas passée en CONFLICTING** à cause du merge (surtout si les deux touchent `rules.rs`, `registry.rs`, `main.rs`, ou `CHANGELOG.md`)." in text, "expected to find: " + "Puis **vérifier que la PR suivante n'est pas passée en CONFLICTING** à cause du merge (surtout si les deux touchent `rules.rs`, `registry.rs`, `main.rs`, ou `CHANGELOG.md`)."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Supported ecosystems: git/gh/gt, cargo, go/golangci-lint, npm/pnpm/npx, ruff/pytest/pip/mypy, rspec/rubocop/rake, dotnet, playwright/vitest/jest, docker/kubectl/aws.' in text, "expected to find: " + 'Supported ecosystems: git/gh/gt, cargo, go/golangci-lint, npm/pnpm/npx, ruff/pytest/pip/mypy, rspec/rubocop/rake, dotnet, playwright/vitest/jest, docker/kubectl/aws.'[:80]

