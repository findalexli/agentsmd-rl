"""Behavioral checks for lynx-website-update-svg-element-usage-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lynx-website")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/public/AGENTS.md')
    assert '- The `svg` element differs significantly from its web counterpart. Pass the SVG markup through the `content` attribute or SVG url through the `src` attribute on `<svg />`:' in text, "expected to find: " + '- The `svg` element differs significantly from its web counterpart. Pass the SVG markup through the `content` attribute or SVG url through the `src` attribute on `<svg />`:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/public/AGENTS.md')
    assert '<svg content={`<svg ... />`} />;' in text, "expected to find: " + '<svg content={`<svg ... />`} />;'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/public/AGENTS.md')
    assert '<svg src={urlOfYourSvgFile} />;' in text, "expected to find: " + '<svg src={urlOfYourSvgFile} />;'[:80]

