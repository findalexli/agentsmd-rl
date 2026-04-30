"""Behavioral checks for chatgptbox-migrate-github-copilot-instructions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chatgptbox")


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
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Firefox: Go to `about:debugging#/runtime/this-firefox`, click "Load Temporary Add-on", then select the `manifest.json` file inside `build/firefox/` (do not select the folder directly). Note: Tempora' in text, "expected to find: " + '- Firefox: Go to `about:debugging#/runtime/this-firefox`, click "Load Temporary Add-on", then select the `manifest.json` file inside `build/firefox/` (do not select the folder directly). Note: Tempora'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Expected failure modes**: In sandboxed or CI environments, the script may fail due to network restrictions (e.g., DNS errors, timeouts, connection refused), HTTP errors (e.g., 403, 429, 503), or c' in text, "expected to find: " + '- **Expected failure modes**: In sandboxed or CI environments, the script may fail due to network restrictions (e.g., DNS errors, timeouts, connection refused), HTTP errors (e.g., 403, 429, 503), or c'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Successful validation**: For each search engine, the script expects to receive a valid HTTP response (status 200) and to successfully extract and parse search results using the corresponding site ' in text, "expected to find: " + '- **Successful validation**: For each search engine, the script expects to receive a valid HTTP response (status 200) and to successfully extract and parse search results using the corresponding site '[:80]

