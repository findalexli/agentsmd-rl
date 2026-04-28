"""Behavioral checks for dde-control-center-docs-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dde-control-center")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'DDE Control Center (深度控制中心) v6.0+ is a Qt6/QML-based desktop control panel for Deepin Desktop Environment. It uses a **plugin-based architecture** where the core framework provides infrastructure and ' in text, "expected to find: " + 'DDE Control Center (深度控制中心) v6.0+ is a Qt6/QML-based desktop control panel for Deepin Desktop Environment. It uses a **plugin-based architecture** where the core framework provides infrastructure and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- **Thread safety**: Plugin C++ objects created in worker threads are moved to main thread - all child objects MUST be in the same tree hierarchy or they won't be moved" in text, "expected to find: " + "- **Thread safety**: Plugin C++ objects created in worker threads are moved to main thread - all child objects MUST be in the same tree hierarchy or they won't be moved"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'See complete example in [examples/plugin-example](examples/plugin-example) and [docs/v25-dcc-interface.zh_CN.md](docs/v25-dcc-interface.zh_CN.md)' in text, "expected to find: " + 'See complete example in [examples/plugin-example](examples/plugin-example) and [docs/v25-dcc-interface.zh_CN.md](docs/v25-dcc-interface.zh_CN.md)'[:80]

