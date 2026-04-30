"""Behavioral checks for vpnhide-chore-publish-claudemd-agentsmd-repo (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vpnhide")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **KPatch-Next KPM:** `kmod/` currently uses kretprobes and requires per-GKI-generation builds (kernel headers + `Module.symvers`). Porting to a [KPatch-Next](https://github.com/KernelSU-Next/KPatch-' in text, "expected to find: " + '- **KPatch-Next KPM:** `kmod/` currently uses kretprobes and requires per-GKI-generation builds (kernel headers + `Module.symvers`). Porting to a [KPatch-Next](https://github.com/KernelSU-Next/KPatch-'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This writes a Markdown fragment to `changelog.d/<type>-<slug>-<hex4>.md` — nothing else. `CHANGELOG.md` is regenerated only at release time (that's what keeps PRs from conflicting on it). Commit just " in text, "expected to find: " + "This writes a Markdown fragment to `changelog.d/<type>-<slug>-<hex4>.md` — nothing else. `CHANGELOG.md` is regenerated only at release time (that's what keeps PRs from conflicting on it). Commit just "[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Don't put `#NN` in commit messages or PR titles to refer to local review notes.** GitHub auto-links `#NN` to PR/issue numbers in this repo, and the cross-reference will almost certainly point at t" in text, "expected to find: " + "- **Don't put `#NN` in commit messages or PR titles to refer to local review notes.** GitHub auto-links `#NN` to PR/issue numbers in this repo, and the cross-reference will almost certainly point at t"[:80]

