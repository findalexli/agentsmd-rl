"""Behavioral checks for ros2_medkit-featdocs-add-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ros2-medkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Keep documentation up to date**: When adding or modifying endpoints, update the corresponding docs in `docs/`, `src/ros2_medkit_gateway/design/`, `src/ros2_medkit_gateway/README.md`, and `postman/` ' in text, "expected to find: " + '**Keep documentation up to date**: When adding or modifying endpoints, update the corresponding docs in `docs/`, `src/ros2_medkit_gateway/design/`, `src/ros2_medkit_gateway/README.md`, and `postman/` '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**ros2_medkit** is a ROS 2 diagnostics gateway that exposes ROS 2 system information via a RESTful HTTP API. It models robots as a **diagnostic entity tree** (Area → Component → Function → App) aligne' in text, "expected to find: " + '**ros2_medkit** is a ROS 2 diagnostics gateway that exposes ROS 2 system information via a RESTful HTTP API. It models robots as a **diagnostic entity tree** (Area → Component → Function → App) aligne'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Modularity & Separation of Concerns**: Separate core business logic from ROS 2 infrastructure and HTTP handling. Logic should be testable in isolation.' in text, "expected to find: " + '- **Modularity & Separation of Concerns**: Separate core business logic from ROS 2 infrastructure and HTTP handling. Logic should be testable in isolation.'[:80]

