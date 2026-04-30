"""Behavioral checks for gum-improve-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gum")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-property-assignment/SKILL.md')
    assert 'name: gum-property-assignment' in text, "expected to find: " + 'name: gum-property-assignment'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-plugins/SKILL.md')
    assert '`StartUp()` is called once on load — subscribe to events here. `ShutDown(PluginShutDownReason)` is called on unload. Service dependencies are injected via `Locator.GetRequiredService<T>()` (typically ' in text, "expected to find: " + '`StartUp()` is called once on load — subscribe to events here. `ShutDown(PluginShutDownReason)` is called on unload. Service dependencies are injected via `Locator.GetRequiredService<T>()` (typically '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-plugins/SKILL.md')
    assert '**Finding which plugin owns a feature**: Search `StartUp()` methods for the event subscription. E.g., to find what handles `VariableSet`, grep for `VariableSet +=` in `InternalPlugins/`. The subscribi' in text, "expected to find: " + '**Finding which plugin owns a feature**: Search `StartUp()` methods for the event subscription. E.g., to find what handles `VariableSet`, grep for `VariableSet +=` in `InternalPlugins/`. The subscribi'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-plugins/SKILL.md')
    assert "description: Reference guide for the Gum tool's plugin system. Load this when working on plugin registration, PluginBase, InternalPlugin, PluginManager, plugin events, or finding which internal plugin" in text, "expected to find: " + "description: Reference guide for the Gum tool's plugin system. Load this when working on plugin registration, PluginBase, InternalPlugin, PluginManager, plugin events, or finding which internal plugin"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-save-classes/SKILL.md')
    assert 'name: gum-tool-save-classes' in text, "expected to find: " + 'name: gum-tool-save-classes'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-selection/SKILL.md')
    assert 'When a locked instance is selected and the cursor is over one of its polygon verts, `PolygonPointInputHandler.HandlePush` must: detect the vert, set `IsActive = true` (to suppress the rectangle select' in text, "expected to find: " + 'When a locked instance is selected and the cursor is over one of its polygon verts, `PolygonPointInputHandler.HandlePush` must: detect the vert, set `IsActive = true` (to suppress the rectangle select'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-selection/SKILL.md')
    assert '`IsActive = true` signals that a handler owns the current drag gesture. It suppresses the rectangle selector — `SelectionManager` passes `isHandlerActive = true` to `RectangleSelector.HandleDrag`, whi' in text, "expected to find: " + '`IsActive = true` signals that a handler owns the current drag gesture. It suppresses the rectangle selector — `SelectionManager` passes `isHandlerActive = true` to `RectangleSelector.HandleDrag`, whi'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-selection/SKILL.md')
    assert 'The rectangle selector activates on drag when no handler is active and the cursor is not over the element body (or Shift is held for additive selection), after a minimum drag distance is exceeded. `Se' in text, "expected to find: " + 'The rectangle selector activates on drag when no handler is active and the cursor is not over the element body (or Shift is held for additive selection), after a minimum drag distance is exceeded. `Se'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-undo/SKILL.md')
    assert 'name: gum-tool-undo' in text, "expected to find: " + 'name: gum-tool-undo'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-variable-grid/SKILL.md')
    assert '`PropertyGridManager.RefreshDataGrid` tracks the previous display target (element, state, instances, behavior). If unchanged and `force=false`, it calls `Refresh()` to update values without recreating' in text, "expected to find: " + '`PropertyGridManager.RefreshDataGrid` tracks the previous display target (element, state, instances, behavior). If unchanged and `force=false`, it calls `Refresh()` to update values without recreating'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-variable-grid/SKILL.md')
    assert '`DataUiGrid.SetCategories()` captures `{name → IsExpanded}` from existing categories, replaces the list, then re-applies the saved values by name. Category collapse state persists across selection cha' in text, "expected to find: " + '`DataUiGrid.SetCategories()` captures `{name → IsExpanded}` from existing categories, replaces the list, then re-applies the saved values by name. Category collapse state persists across selection cha'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gum-tool-variable-grid/SKILL.md')
    assert 'All members in the Variables tab use `StateReferencingInstanceMember` (subclass of `InstanceMember`), not the generic reflection path. Its `IsReadOnly` returns `true` when `InstanceSave?.Locked == tru' in text, "expected to find: " + 'All members in the Variables tab use `StateReferencingInstanceMember` (subclass of `InstanceMember`), not the generic reflection path. Its `IsReadOnly` returns `true` when `InstanceSave?.Locked == tru'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/variable-grid/SKILL.md')
    assert '.claude/skills/variable-grid/SKILL.md' in text, "expected to find: " + '.claude/skills/variable-grid/SKILL.md'[:80]

