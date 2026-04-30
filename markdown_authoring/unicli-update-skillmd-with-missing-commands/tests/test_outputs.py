"""Behavioral checks for unicli-update-skillmd-with-missing-commands (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unicli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude-plugin/unicli/skills/unicli/SKILL.md')
    assert 'unicli exec Prefab.Save --path "Player" --assetPath "Assets/Prefabs/Player.prefab" --json' in text, "expected to find: " + 'unicli exec Prefab.Save --path "Player" --assetPath "Assets/Prefabs/Player.prefab" --json'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude-plugin/unicli/skills/unicli/SKILL.md')
    assert 'unicli exec GameObject.AddComponent --path "Player" --typeName BoxCollider --json' in text, "expected to find: " + 'unicli exec GameObject.AddComponent --path "Player" --typeName BoxCollider --json'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude-plugin/unicli/skills/unicli/SKILL.md')
    assert 'unicli exec Prefab.Instantiate --assetPath "Assets/Prefabs/Enemy.prefab" --json' in text, "expected to find: " + 'unicli exec Prefab.Instantiate --assetPath "Assets/Prefabs/Enemy.prefab" --json'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `.claude-plugin/unicli/skills/unicli/SKILL.md` — Built-in Commands table and Common Workflows section' in text, "expected to find: " + '- `.claude-plugin/unicli/skills/unicli/SKILL.md` — Built-in Commands table and Common Workflows section'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When adding or modifying commands, update the following files to keep them in sync:' in text, "expected to find: " + 'When adding or modifying commands, update the following files to keep them in sync:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `README.md` — Available Commands table and Examples section' in text, "expected to find: " + '- `README.md` — Available Commands table and Examples section'[:80]

