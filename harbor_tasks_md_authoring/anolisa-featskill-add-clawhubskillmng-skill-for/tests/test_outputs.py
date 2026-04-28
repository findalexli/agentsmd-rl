"""Behavioral checks for anolisa-featskill-add-clawhubskillmng-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anolisa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/others/clawhub-skill-mng/SKILL.md')
    assert 'description: Search, install, uninstall, update and manage agent skills. Use when the user asks to find/search/install/uninstall/update/list/explore skills, asks "how do I do X" or "find a skill for X' in text, "expected to find: " + 'description: Search, install, uninstall, update and manage agent skills. Use when the user asks to find/search/install/uninstall/update/list/explore skills, asks "how do I do X" or "find a skill for X'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/others/clawhub-skill-mng/SKILL.md')
    assert 'clawhub inspect <slug> --json --dir ~/.copilot-shell/skills --registry https://cn.clawhub-mirror.com             # JSON 格式输出' in text, "expected to find: " + 'clawhub inspect <slug> --json --dir ~/.copilot-shell/skills --registry https://cn.clawhub-mirror.com             # JSON 格式输出'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/others/clawhub-skill-mng/SKILL.md')
    assert 'clawhub inspect <slug> --file SKILL.md --dir ~/.copilot-shell/skills --registry https://cn.clawhub-mirror.com    # 查看指定文件内容' in text, "expected to find: " + 'clawhub inspect <slug> --file SKILL.md --dir ~/.copilot-shell/skills --registry https://cn.clawhub-mirror.com    # 查看指定文件内容'[:80]

