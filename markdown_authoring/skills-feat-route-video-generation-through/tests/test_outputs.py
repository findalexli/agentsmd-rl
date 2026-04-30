"""Behavioral checks for skills-feat-route-video-generation-through (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '1. **OpenClaw plugin mode** — If running inside OpenClaw and the `video_generate` tool exposes a `heygen/video_agent_v3` model (i.e. the user has [`@heygen/openclaw-plugin-heygen`](https://github.com/' in text, "expected to find: " + '1. **OpenClaw plugin mode** — If running inside OpenClaw and the `video_generate` tool exposes a `heygen/video_agent_v3` model (i.e. the user has [`@heygen/openclaw-plugin-heygen`](https://github.com/'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "- **Never cross over.** Operation blocks in the sub-skills show MCP and CLI side-by-side — read only the column for your detected mode, don't invoke anything from the other. If something isn't exposed" in text, "expected to find: " + "- **Never cross over.** Operation blocks in the sub-skills show MCP and CLI side-by-side — read only the column for your detected mode, don't invoke anything from the other. If something isn't exposed"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '2. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access' in text, "expected to find: " + '2. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access'[:80]

