"""Behavioral checks for opik-na-fe-update-cursor-rules (markdown_authoring task).

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
    text = _read('apps/opik-frontend/.cursor/rules/accessibility-testing.mdc')
    assert 'expect(screen.getByRole("alert")).toHaveTextContent("Email is required");' in text, "expected to find: " + 'expect(screen.getByRole("alert")).toHaveTextContent("Email is required");'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/accessibility-testing.mdc')
    assert 'expect(screen.getByRole("button", { name: /save/i })).toBeEnabled();' in text, "expected to find: " + 'expect(screen.getByRole("button", { name: /save/i })).toBeEnabled();'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/accessibility-testing.mdc')
    assert 'useEntityList({ workspaceName: "test", page: 1, size: 10 }),' in text, "expected to find: " + 'useEntityList({ workspaceName: "test", page: 1, size: 10 }),'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/api-data-fetching.mdc')
    assert 'queryFn: ({ pageParam = 1 }) => fetchEntities({ page: pageParam }),' in text, "expected to find: " + 'queryFn: ({ pageParam = 1 }) => fetchEntities({ page: pageParam }),'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/api-data-fetching.mdc')
    assert 'entity.id === newEntity.id ? { ...entity, ...newEntity } : entity,' in text, "expected to find: " + 'entity.id === newEntity.id ? { ...entity, ...newEntity } : entity,'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/api-data-fetching.mdc')
    assert 'const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =' in text, "expected to find: " + 'const { data, fetchNextPage, hasNextPage, isFetchingNextPage } ='[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/code-quality.mdc')
    assert 'When you like the emulation of some functionality, try to isolate it in a way that makes it easy to replace in the future:' in text, "expected to find: " + 'When you like the emulation of some functionality, try to isolate it in a way that makes it easy to replace in the future:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/code-quality.mdc')
    assert 'Use Lodash for complex operations, but **always import methods individually** for optimal tree-shaking and bundle size:' in text, "expected to find: " + 'Use Lodash for complex operations, but **always import methods individually** for optimal tree-shaking and bundle size:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/code-quality.mdc')
    assert 'import { pick, merge, cloneDeep } from "lodash"; // Less efficient than individual imports' in text, "expected to find: " + 'import { pick, merge, cloneDeep } from "lodash"; // Less efficient than individual imports'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/forms.mdc')
    assert 'setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));' in text, "expected to find: " + 'setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/forms.mdc')
    assert 'message: "Admin users must have at least one permission",' in text, "expected to find: " + 'message: "Admin users must have at least one permission",'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/forms.mdc')
    assert 'const isAvailable = await checkEmailAvailability(email);' in text, "expected to find: " + 'const isAvailable = await checkEmailAvailability(email);'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/performance.mdc')
    assert "- Simple object/array literals that don't impact child components" in text, "expected to find: " + "- Simple object/array literals that don't impact child components"[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/performance.mdc')
    assert '.filter((item) => item.category === selectedCategory)' in text, "expected to find: " + '.filter((item) => item.category === selectedCategory)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/performance.mdc')
    assert 'displayName: `${item.firstName} ${item.lastName}`,' in text, "expected to find: " + 'displayName: `${item.firstName} ${item.lastName}`,'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/state-management.mdc')
    assert 'export const useEntityFilters = () => useEntityStore((state) => state.filters);' in text, "expected to find: " + 'export const useEntityFilters = () => useEntityStore((state) => state.filters);'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/state-management.mdc')
    assert 'updateFilters: useEntityStore.getState().updateFilters,' in text, "expected to find: " + 'updateFilters: useEntityStore.getState().updateFilters,'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/state-management.mdc')
    assert 'setPreferences((prev) => ({ ...prev, [key]: value }));' in text, "expected to find: " + 'setPreferences((prev) => ({ ...prev, [key]: value }));'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/tech-stack.mdc')
    assert 'alwaysApply: true' in text, "expected to find: " + 'alwaysApply: true'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/ui-components.mdc')
    assert 'const UserCard: React.FC<{ user: User; onEdit: (user: User) => void }> = ({ user, onEdit }) => {' in text, "expected to find: " + 'const UserCard: React.FC<{ user: User; onEdit: (user: User) => void }> = ({ user, onEdit }) => {'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/ui-components.mdc')
    assert 'Add all new colors to the `main.css` file, along with their alternatives for the dark theme:' in text, "expected to find: " + 'Add all new colors to the `main.css` file, along with their alternatives for the dark theme:'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/ui-components.mdc')
    assert 'When adding a new UI component, remember it should support both light and dark themes:' in text, "expected to find: " + 'When adding a new UI component, remember it should support both light and dark themes:'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/unit-testing.mdc')
    assert 'When in doubt, write the test. Complex functions should have comprehensive test coverage to prevent regressions and ensure reliability.' in text, "expected to find: " + 'When in doubt, write the test. Complex functions should have comprehensive test coverage to prevent regressions and ensure reliability.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/unit-testing.mdc')
    assert 'expect(result).toEqual([{ name: "input", type: "str", optional: false }]);' in text, "expected to find: " + 'expect(result).toEqual([{ name: "input", type: "str", optional: false }]);'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/unit-testing.mdc')
    assert 'isStringMarkdown("This contains an asterisk * but is not markdown."),' in text, "expected to find: " + 'isStringMarkdown("This contains an asterisk * but is not markdown."),'[:80]

