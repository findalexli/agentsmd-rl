"""Behavioral checks for nexent-update-frontend-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nexent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/component_layer_rules.mdc')
    assert '- **Colocate subcomponents**: When a component file grows, extract logically distinct subcomponents into separate files in the same folder. Avoid putting many unrelated components in one file.' in text, "expected to find: " + '- **Colocate subcomponents**: When a component file grows, extract logically distinct subcomponents into separate files in the same folder. Avoid putting many unrelated components in one file.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/component_layer_rules.mdc')
    assert '- **Lean interfaces**: Group related props into objects when they form a cohesive concern (e.g. `user: { email, avatarUrl, role }`) instead of passing many flat props.' in text, "expected to find: " + '- **Lean interfaces**: Group related props into objects when they form a cohesive concern (e.g. `user: { email, avatarUrl, role }`) instead of passing many flat props.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/component_layer_rules.mdc')
    assert '- Component layer contains reusable UI components for `frontend/components/**/*.tsx` and feature-specific components under `frontend/app/**/components/**/*.tsx`' in text, "expected to find: " + '- Component layer contains reusable UI components for `frontend/components/**/*.tsx` and feature-specific components under `frontend/app/**/components/**/*.tsx`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/frontend_overview_rules.mdc')
    assert '- **Avoid over-engineering**: Before abstracting code (extracting hooks, components, utils), confirm there is a concrete need (reuse, testability, or complexity). Prefer simple, inline solutions until' in text, "expected to find: " + '- **Avoid over-engineering**: Before abstracting code (extracting hooks, components, utils), confirm there is a concrete need (reuse, testability, or complexity). Prefer simple, inline solutions until'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/frontend_overview_rules.mdc')
    assert '| `hooks/` | State and side-effects | Shared API data: use TanStack React Query (`useQuery`); client-side filter/sort: `useMemo` on query data; mutations: `useMutation` + `queryClient.invalidateQuerie' in text, "expected to find: " + '| `hooks/` | State and side-effects | Shared API data: use TanStack React Query (`useQuery`); client-side filter/sort: `useMemo` on query data; mutations: `useMutation` + `queryClient.invalidateQuerie'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/frontend_overview_rules.mdc')
    assert '- **No cross-feature imports**: Feature-level code (`components/` under a feature) must not import from other features. Use shared `components/` for cross-feature reuse.' in text, "expected to find: " + '- **No cross-feature imports**: Feature-level code (`components/` under a feature) must not import from other features. Use shared `components/` for cross-feature reuse.'[:80]

