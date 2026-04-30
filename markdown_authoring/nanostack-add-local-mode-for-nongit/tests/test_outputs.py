"""Behavioral checks for nanostack-add-local-mode-for-nongit (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '**Local mode:** Run `source bin/lib/git-context.sh && detect_git_mode`. If result is `local`, adapt language: "implementation plan" → "paso a paso", "files to modify" → "archivos que vamos a crear", "' in text, "expected to find: " + '**Local mode:** Run `source bin/lib/git-context.sh && detect_git_mode`. If result is `local`, adapt language: "implementation plan" → "paso a paso", "files to modify" → "archivos que vamos a crear", "'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '- **Language:** replace all jargon with plain terms. "Revisé N archivos. Encontré X cosas:" instead of "Diff: N files, X findings." Replace "nit" → "detalle menor", "auto-fix" → "ya lo arreglé", "bloc' in text, "expected to find: " + '- **Language:** replace all jargon with plain terms. "Revisé N archivos. Encontré X cosas:" instead of "Diff: N files, X findings." Replace "nit" → "detalle menor", "auto-fix" → "ya lo arreglé", "bloc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '- **Next steps:** do NOT list slash commands. Instead: "¿Querés que revise la seguridad antes de darlo por terminado?"' in text, "expected to find: " + '- **Next steps:** do NOT list slash commands. Instead: "¿Querés que revise la seguridad antes de darlo por terminado?"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '- HTML → run `open index.html` (or the main HTML file) so the user sees it instantly. Then say "Se abrió en tu navegador."' in text, "expected to find: " + '- HTML → run `open index.html` (or the main HTML file) so the user sees it instantly. Then say "Se abrió en tu navegador."'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert 'Never mention PR, CI, branch, merge, deploy, rollback, or slash commands. Output: "Listo. Para verlo: [comando]."' in text, "expected to find: " + 'Never mention PR, CI, branch, merge, deploy, rollback, or slash commands. Output: "Listo. Para verlo: [comando]."'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '3. Detect project type and show the result immediately:' in text, "expected to find: " + '3. Detect project type and show the result immediately:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '**Local mode language:** Run `source bin/lib/git-context.sh && detect_git_mode`. If the result is `local` (no git repo), the user is likely non-technical. Adapt your language throughout the entire spr' in text, "expected to find: " + '**Local mode language:** Run `source bin/lib/git-context.sh && detect_git_mode`. If the result is `local` (no git repo), the user is likely non-technical. Adapt your language throughout the entire spr'[:80]

