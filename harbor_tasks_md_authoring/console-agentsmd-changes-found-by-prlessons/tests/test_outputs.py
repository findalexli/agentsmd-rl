"""Behavioral checks for console-agentsmd-changes-found-by-prlessons (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/console")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Hoist static column definitions to module scope; `useMemo` with an empty dependency array is a code smell indicating the value doesn't belong inside the component. More generally, don't reach for `u" in text, "expected to find: " + "- Hoist static column definitions to module scope; `useMemo` with an empty dependency array is a code smell indicating the value doesn't belong inside the component. More generally, don't reach for `u"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset rela" in text, "expected to find: " + "- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset rela"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prefer disabling buttons with `disabledReason` over hiding them so users can discover the action exists. Compute `disabledReason` as a `string | undefined` ternary chain and derive `disabled` from `' in text, "expected to find: " + '- Prefer disabling buttons with `disabledReason` over hiding them so users can discover the action exists. Compute `disabledReason` as a `string | undefined` ternary chain and derive `disabled` from `'[:80]

