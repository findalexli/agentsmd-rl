"""Behavioral checks for ledger-live-support-optimize-cursor-rules-context (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/client-ids.mdc')
    assert 'description: Privacy-protected ID management with @ledgerhq/client-ids — DeviceId, UserId, DatadogId, export-rules.json' in text, "expected to find: " + 'description: Privacy-protected ID management with @ledgerhq/client-ids — DeviceId, UserId, DatadogId, export-rules.json'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/client-ids.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules.mdc')
    assert '- **Prefer smart activation (`description`) over `globs`** — the agent can judge relevance from conversation context better than broad file patterns. Add `globs` only when activation must be strictly ' in text, "expected to find: " + '- **Prefer smart activation (`description`) over `globs`** — the agent can judge relevance from conversation context better than broad file patterns. Add `globs` only when activation must be strictly '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules.mdc')
    assert 'A `description` can be combined with `globs` — the description serves as documentation for human readers and also enables agent-decided activation when no matching file is open. The `description` fiel' in text, "expected to find: " + 'A `description` can be combined with `globs` — the description serves as documentation for human readers and also enables agent-decided activation when no matching file is open. The `description` fiel'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules.mdc')
    assert '- **Never combine `alwaysApply: true` with `description` or `globs`** — it makes the other fields useless since the rule is always injected regardless.' in text, "expected to find: " + '- **Never combine `alwaysApply: true` with `description` or `globs`** — it makes the other fields useless since the rule is always injected regardless.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-workflow.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ldls.mdc')
    assert 'description: LDLS UI React design system rules (@ledgerhq/lumen-ui-react)' in text, "expected to find: " + 'description: LDLS UI React design system rules (@ledgerhq/lumen-ui-react)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ldls.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-general.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-mvvm.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/redux-slice.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rtk-query-api.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'globs: ["*.test.*", "*.spec.*", "**/tests/**", "**/__tests__/**"]' in text, "expected to find: " + 'globs: ["*.test.*", "*.spec.*", "**/tests/**", "**/__tests__/**"]'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript.mdc')
    assert 'globs: ["**/*.ts", "**/*.tsx"]' in text, "expected to find: " + 'globs: ["**/*.ts", "**/*.tsx"]'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/zod-schemas.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]

