"""Behavioral checks for full-stack-skills-update-ant-design-react-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/full-stack-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/SKILL.md')
    assert 'This skill is organized to match the Ant Design React official documentation structure (https://6x-ant-design.antgroup.com/docs/react/introduce-cn, https://6x-ant-design.antgroup.com/components/overvi' in text, "expected to find: " + 'This skill is organized to match the Ant Design React official documentation structure (https://6x-ant-design.antgroup.com/docs/react/introduce-cn, https://6x-ant-design.antgroup.com/components/overvi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/SKILL.md')
    assert '- See guide files in `examples/guide/` or `examples/getting-started/` → https://6x-ant-design.antgroup.com/docs/react/introduce-cn' in text, "expected to find: " + '- See guide files in `examples/guide/` or `examples/getting-started/` → https://6x-ant-design.antgroup.com/docs/react/introduce-cn'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/SKILL.md')
    assert '- See component files in `examples/components/` → https://6x-ant-design.antgroup.com/components/overview-cn/' in text, "expected to find: " + '- See component files in `examples/components/` → https://6x-ant-design.antgroup.com/components/overview-cn/'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/templates/project-setup.md')
    assert '"react-dom": "^19.0.0",' in text, "expected to find: " + '"react-dom": "^19.0.0",'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/templates/project-setup.md')
    assert '"react": "^19.0.0",' in text, "expected to find: " + '"react": "^19.0.0",'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ant-design-react/templates/project-setup.md')
    assert '"antd": "^6.3.0"' in text, "expected to find: " + '"antd": "^6.3.0"'[:80]

