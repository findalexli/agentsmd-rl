"""Behavioral checks for skills-fix-silent-mode-detection-no (markdown_authoring task).

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
    assert '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists t' in text, "expected to find: " + '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Neither available:** Only if both MCP and a working CLI are missing, tell the user once — concisely — how to connect: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `cu' in text, "expected to find: " + '**Neither available:** Only if both MCP and a working CLI are missing, tell the user once — concisely — how to connect: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `cu'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Two modes, in order of preference. **Mode selection is silent — detect once at the start of the session, pick a mode, and move on.** Never narrate transport choice ("CLI is broken", "switching to MCP"' in text, "expected to find: " + 'Two modes, in order of preference. **Mode selection is silent — detect once at the start of the session, pick a mode, and move on.** Never narrate transport choice ("CLI is broken", "switching to MCP"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/cr' in text, "expected to find: " + '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/cr'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**Neither available:** Only if MCP is unavailable AND the CLI doesn\'t work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.' in text, "expected to find: " + '**Neither available:** Only if MCP is unavailable AND the CLI doesn\'t work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn\'t care how calls are ' in text, "expected to find: " + '**Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn\'t care how calls are '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/cr' in text, "expected to find: " + '**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/cr'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert '**Neither available:** Only if MCP is unavailable AND the CLI doesn\'t work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.' in text, "expected to find: " + '**Neither available:** Only if MCP is unavailable AND the CLI doesn\'t work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert 'Two modes, in order of preference. **Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — t' in text, "expected to find: " + 'Two modes, in order of preference. **Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — t'[:80]

