"""Behavioral checks for opik-na-docs-convert-alwaysapplied-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opik")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/api_design.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/api_design.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/architecture.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/architecture.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/business_logic.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/business_logic.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_quality.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_quality.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/db_migration_script.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/error_handling.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/general.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/logging.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/mysql.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/mysql.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/tech_stack.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/tech_stack.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/testing.mdc')
    assert 'globs: apps/opik-backend/**/*' in text, "expected to find: " + 'globs: apps/opik-backend/**/*'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/testing.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/accessibility-testing.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/accessibility-testing.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/api-data-fetching.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/api-data-fetching.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/code-quality.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/code-quality.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/forms.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/forms.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/frontend_rules.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/frontend_rules.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/performance.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/performance.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/state-management.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/state-management.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/tech-stack.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/tech-stack.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/ui-components.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/ui-components.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/unit-testing.mdc')
    assert 'globs: apps/opik-frontend/**/*' in text, "expected to find: " + 'globs: apps/opik-frontend/**/*'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/unit-testing.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/api-design.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/architecture.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/code-structure.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/dependencies.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/design-principles.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/documentation-style.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/error-handling.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/logging.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/method-refactoring-patterns.mdc')
    assert 'globs: sdks/python/src/opik/**/*' in text, "expected to find: " + 'globs: sdks/python/src/opik/**/*'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/method-refactoring-patterns.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/test-best-practices.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/test-implementation.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/python/.cursor/rules/test-organization.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/architecture.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/code-structure.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/integrations.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/logging.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/overview.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/test-best-practices.mdc')
    assert 'globs: sdks/typescript/**/*' in text, "expected to find: " + 'globs: sdks/typescript/**/*'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/typescript/.cursor/rules/test-best-practices.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]

