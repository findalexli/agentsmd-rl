"""Behavioral checks for maui-add-publicapiunshippedtxt-bom-sort-warning (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/maui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-prefixed: `\ufeff#nullable enable`) on the **first line**. If this line is moved or removed, the analyzer treats it as a decla' in text, "expected to find: " + 'Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-prefixed: `\ufeff#nullable enable`) on the **first line**. If this line is moved or removed, the analyzer treats it as a decla'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Never sort these files with plain `sort`** — the BOM bytes (`0xEF 0xBB 0xBF`) sort after ASCII characters under `LC_ALL=C`, pushing `#nullable enable` to the bottom of the file.' in text, "expected to find: " + '**Never sort these files with plain `sort`** — the BOM bytes (`0xEF 0xBB 0xBF`) sort after ASCII characters under `LC_ALL=C`, pushing `#nullable enable` to the bottom of the file.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'grep -v \'^<<<<<<\\|^======\\|^>>>>>>\\|#nullable enable\' "$f" | LC_ALL=C sort -u | sed \'/^$/d\' > /tmp/api_fix.txt' in text, "expected to find: " + 'grep -v \'^<<<<<<\\|^======\\|^>>>>>>\\|#nullable enable\' "$f" | LC_ALL=C sort -u | sed \'/^$/d\' > /tmp/api_fix.txt'[:80]

