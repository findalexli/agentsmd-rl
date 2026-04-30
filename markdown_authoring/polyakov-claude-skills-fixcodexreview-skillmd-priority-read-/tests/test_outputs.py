"""Behavioral checks for polyakov-claude-skills-fixcodexreview-skillmd-priority-read- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/polyakov-claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/codex-review/skills/codex-review/SKILL.md')
    assert 'Все команды ниже используют относительный `scripts/` — подставь полный путь при вызове.' in text, "expected to find: " + 'Все команды ниже используют относительный `scripts/` — подставь полный путь при вызове.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/codex-review/skills/codex-review/SKILL.md')
    assert '- Скрипты: замени `SKILL.md` на `scripts/codex-review.sh` (и `scripts/codex-state.sh`)' in text, "expected to find: " + '- Скрипты: замени `SKILL.md` на `scripts/codex-review.sh` (и `scripts/codex-state.sh`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/codex-review/skills/codex-review/SKILL.md')
    assert 'ВАЖНО: при срабатывании триггера прочитай SKILL.md до любых других шагов.' in text, "expected to find: " + 'ВАЖНО: при срабатывании триггера прочитай SKILL.md до любых других шагов.'[:80]

