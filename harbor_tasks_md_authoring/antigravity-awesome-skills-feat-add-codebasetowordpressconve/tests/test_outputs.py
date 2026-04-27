"""Behavioral checks for antigravity-awesome-skills-feat-add-codebasetowordpressconve (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codebase-to-wordpress-converter/SKILL.md')
    assert 'This skill is designed for the high-fidelity conversion of static or React-based frontends into fully functional, CMS-driven WordPress themes. It acts as a **Senior WordPress Architect**, **React Expe' in text, "expected to find: " + 'This skill is designed for the high-fidelity conversion of static or React-based frontends into fully functional, CMS-driven WordPress themes. It acts as a **Senior WordPress Architect**, **React Expe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codebase-to-wordpress-converter/SKILL.md')
    assert 'Start by identifying all components in the source code. Create a UI Comparison table comparing the original source output against the target WordPress output.' in text, "expected to find: " + 'Start by identifying all components in the source code. Create a UI Comparison table comparing the original source output against the target WordPress output.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codebase-to-wordpress-converter/SKILL.md')
    assert 'description: "Expert skill for converting any codebase (React/HTML/Next.js) into a pixel-perfect, SEO-optimized, and dynamic WordPress theme."' in text, "expected to find: " + 'description: "Expert skill for converting any codebase (React/HTML/Next.js) into a pixel-perfect, SEO-optimized, and dynamic WordPress theme."'[:80]

