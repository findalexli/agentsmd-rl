"""Behavioral checks for antigravity-awesome-skills-merge-branch-main-of-httpsgithubc (markdown_authoring task).

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
    text = _read('skills/nerdzao-elite-gemini-high/SKILL.md')
    assert 'Analise e corrija IMEDIATAMENTE: duplicação de elementos, inconsistência de cores/labels, formatação de moeda (R$ XX,XX com vírgula), alinhamento, spacing, hierarquia visual e responsividade.' in text, "expected to find: " + 'Analise e corrija IMEDIATAMENTE: duplicação de elementos, inconsistência de cores/labels, formatação de moeda (R$ XX,XX com vírgula), alinhamento, spacing, hierarquia visual e responsividade.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nerdzao-elite-gemini-high/SKILL.md')
    assert 'description: "Modo Elite Coder + UX Pixel-Perfect otimizado especificamente para Gemini 3.1 Pro High. Workflow completo com foco em qualidade máxima e eficiência de tokens."' in text, "expected to find: " + 'description: "Modo Elite Coder + UX Pixel-Perfect otimizado especificamente para Gemini 3.1 Pro High. Workflow completo com foco em qualidade máxima e eficiência de tokens."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nerdzao-elite-gemini-high/SKILL.md')
    assert 'Você é um Engenheiro de Software Sênior Elite (15+ anos) + Designer de Produto Senior, operando no modo Gemini 3.1 Pro (High).' in text, "expected to find: " + 'Você é um Engenheiro de Software Sênior Elite (15+ anos) + Designer de Produto Senior, operando no modo Gemini 3.1 Pro (High).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nerdzao-elite/SKILL.md')
    assert '@concise-planning @brainstorming @senior-architect @architecture @test-driven-development @testing-patterns @refactor-clean-code @clean-code @lint-and-validate @ui-visual-validator @ui-ux-pro-max @fro' in text, "expected to find: " + '@concise-planning @brainstorming @senior-architect @architecture @test-driven-development @testing-patterns @refactor-clean-code @clean-code @lint-and-validate @ui-visual-validator @ui-ux-pro-max @fro'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nerdzao-elite/SKILL.md')
    assert '6. Validação visual UX OBRIGATÓRIA (@ui-visual-validator + @ui-ux-pro-max) → corrija imediatamente qualquer duplicação, inconsistência de cor/label, formatação de moeda, alinhamento etc.' in text, "expected to find: " + '6. Validação visual UX OBRIGATÓRIA (@ui-visual-validator + @ui-ux-pro-max) → corrija imediatamente qualquer duplicação, inconsistência de cor/label, formatação de moeda, alinhamento etc.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nerdzao-elite/SKILL.md')
    assert 'Você é um Engenheiro de Software Sênior Elite (15+ anos) + Designer de Produto Senior.' in text, "expected to find: " + 'Você é um Engenheiro de Software Sênior Elite (15+ anos) + Designer de Produto Senior.'[:80]

