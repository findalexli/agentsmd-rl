"""Behavioral checks for editor-review-architecture-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/editor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-architecture/SKILL.md')
    assert 'Owns: `<Viewer>`, renderers, viewer systems (cutouts, zones, level positions, scans), the viewer store (`useViewer`) *for genuine presentation state only* (selection path, camera/level/wall/view modes' in text, "expected to find: " + 'Owns: `<Viewer>`, renderers, viewer systems (cutouts, zones, level positions, scans), the viewer store (`useViewer`) *for genuine presentation state only* (selection path, camera/level/wall/view modes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-architecture/SKILL.md')
    assert 'Owns: node schemas, the scene store (`useScene`), live transforms store, core systems (wall mitering, slab polygons, space detection), event bus, plain 2D/3D math helpers, `sceneRegistry`. Consumed by' in text, "expected to find: " + 'Owns: node schemas, the scene store (`useScene`), live transforms store, core systems (wall mitering, slab polygons, space detection), event bus, plain 2D/3D math helpers, `sceneRegistry`. Consumed by'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-architecture/SKILL.md')
    assert 'For every new file, new type, new store field, or new exported helper introduced by the diff, answer one question: **which layer does this belong to — core, viewer, or editor?** If the answer is "edit' in text, "expected to find: " + 'For every new file, new type, new store field, or new exported helper introduced by the diff, answer one question: **which layer does this belong to — core, viewer, or editor?** If the answer is "edit'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tools.mdc')
    assert '- **Live-drag exception for direct mesh transforms.** During an active drag a tool may apply a transform offset directly to `sceneRegistry.nodes.get(id).position`/`rotation`/`scale` *when and only whe' in text, "expected to find: " + '- **Live-drag exception for direct mesh transforms.** During an active drag a tool may apply a transform offset directly to `sceneRegistry.nodes.get(id).position`/`rotation`/`scale` *when and only whe'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tools.mdc')
    assert "- **Tools mutate `useScene` for committed changes and `useLiveTransforms` for ephemeral drag state.** A tool's end-of-interaction write (click-to-commit, release-to-commit) goes to `useScene` and is c" in text, "expected to find: " + "- **Tools mutate `useScene` for committed changes and `useLiveTransforms` for ephemeral drag state.** A tool's end-of-interaction write (click-to-commit, release-to-commit) goes to `useScene` and is c"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tools.mdc')
    assert '- **Tools must not import from `@pascal-app/viewer`** — use the scene store and core hooks only. `sceneRegistry` is exported from `@pascal-app/core` and is the allowed door into the Three.js graph for' in text, "expected to find: " + '- **Tools must not import from `@pascal-app/viewer`** — use the scene store and core hooks only. `sceneRegistry` is exported from `@pascal-app/core` and is the allowed door into the Three.js graph for'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/review-architecture/SKILL.md')
    assert '../../../.claude/skills/review-architecture/SKILL.md' in text, "expected to find: " + '../../../.claude/skills/review-architecture/SKILL.md'[:80]

