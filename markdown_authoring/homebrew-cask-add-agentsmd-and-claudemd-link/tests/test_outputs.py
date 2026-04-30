"""Behavioral checks for homebrew-cask-add-agentsmd-and-claudemd-link (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/homebrew-cask")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [ ] Submission is for a [stable version](https://docs.brew.sh/Acceptable-Casks#stable-versions) or [documented exception](https://docs.brew.sh/Acceptable-Casks#but-there-is-no-stable-version)' in text, "expected to find: " + '- [ ] Submission is for a [stable version](https://docs.brew.sh/Acceptable-Casks#stable-versions) or [documented exception](https://docs.brew.sh/Acceptable-Casks#but-there-is-no-stable-version)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Check if previously refused**: [closed unmerged PRs](https://github.com/search?q=repo%3AHomebrew%2Fhomebrew-cask+is%3Aclosed+is%3Aunmerged+&type=pullrequests)' in text, "expected to find: " + '2. **Check if previously refused**: [closed unmerged PRs](https://github.com/search?q=repo%3AHomebrew%2Fhomebrew-cask+is%3Aclosed+is%3Aunmerged+&type=pullrequests)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [ ] Checked cask was not [already refused](https://github.com/search?q=repo%3AHomebrew%2Fhomebrew-cask+is%3Aclosed+is%3Aunmerged+&type=pullrequests)' in text, "expected to find: " + '- [ ] Checked cask was not [already refused](https://github.com/search?q=repo%3AHomebrew%2Fhomebrew-cask+is%3Aclosed+is%3Aunmerged+&type=pullrequests)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

