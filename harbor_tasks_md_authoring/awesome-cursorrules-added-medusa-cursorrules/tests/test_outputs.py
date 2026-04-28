"""Behavioral checks for awesome-cursorrules-added-medusa-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/medusa.mdc')
    assert 'You are an expert senior software engineer specializing in modern web development, with deep expertise in TypeScript, Medusa, React.js, and TailwindCSS.' in text, "expected to find: " + 'You are an expert senior software engineer specializing in modern web development, with deep expertise in TypeScript, Medusa, React.js, and TailwindCSS.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/medusa.mdc')
    assert "- When creating a workflow or step, always use Medusa's Workflow SDK `@medusajs/framework/workflows-sdk` to define it." in text, "expected to find: " + "- When creating a workflow or step, always use Medusa's Workflow SDK `@medusajs/framework/workflows-sdk` to define it."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/medusa.mdc')
    assert 'description: Medusa rules and best practices. These rules should be used when building applications with Medusa.' in text, "expected to find: " + 'description: Medusa rules and best practices. These rules should be used when building applications with Medusa.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/medusa-cursorrules/.cursorrules')
    assert 'You are an expert senior software engineer specializing in modern web development, with deep expertise in TypeScript, Medusa, React.js, and TailwindCSS.' in text, "expected to find: " + 'You are an expert senior software engineer specializing in modern web development, with deep expertise in TypeScript, Medusa, React.js, and TailwindCSS.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/medusa-cursorrules/.cursorrules')
    assert "- When creating a workflow or step, always use Medusa's Workflow SDK `@medusajs/framework/workflows-sdk` to define it." in text, "expected to find: " + "- When creating a workflow or step, always use Medusa's Workflow SDK `@medusajs/framework/workflows-sdk` to define it."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/medusa-cursorrules/.cursorrules')
    assert '- Data model variables should be camelCase. Data model names as passed to `model.define` should be snake case.' in text, "expected to find: " + '- Data model variables should be camelCase. Data model names as passed to `model.define` should be snake case.'[:80]

