"""Structural checks for markdown_authoring task.

Verifies that the gold markdown additions are present in .claude/rules/code-style.md.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/areal")
TARGET = REPO / ".claude/rules/code-style.md"


def _grep(pattern: str, path: Path) -> bool:
    """Return True if pattern is found in file."""
    r = subprocess.run(
        ["grep", "-qF", pattern, str(path)],
        capture_output=True,
    )
    return r.returncode == 0


def test_per_rank_logger_convention():
    """Gold diff adds per-rank logger format convention."""
    assert _grep("For per-rank loggers:", TARGET), (
        "Missing per-rank logger convention in .claude/rules/code-style.md"
    )


def test_register_new_loggers_instruction():
    """Gold diff adds instruction to register new loggers in logging.py."""
    assert _grep("Register new loggers in", TARGET), (
        "Missing register-new-loggers instruction in .claude/rules/code-style.md"
    )


def test_color_scheme_table():
    """Gold diff adds a Color Scheme table documenting logger colors."""
    assert _grep("Color Scheme", TARGET), (
        "Missing Color Scheme table in .claude/rules/code-style.md"
    )


def test_color_scheme_includes_purple_for_rl():
    """Gold diff adds purple row for RL-specific loggers."""
    assert _grep("purple", TARGET) and _grep("RL-specific", TARGET), (
        "Missing purple/RL-specific row in Color Scheme table"
    )


def test_existing_logging_convention_preserved():
    """Existing PascalCase naming convention must not be removed (regression guard)."""
    assert _grep("PascalCase", TARGET), (
        "Existing PascalCase naming convention was removed from code-style.md"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_the_book():
    """pass_to_pass | CI job 'build' → step 'Build the book'"""
    r = subprocess.run(
        ["bash", "-lc", 'jupyter-book build docs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build the book' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")