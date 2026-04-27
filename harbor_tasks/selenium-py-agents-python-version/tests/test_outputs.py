"""Markdown-authoring task: verify py/AGENTS.md gained Python 3.10+ rules.

This is a structural sanity gate. Track 2 (Gemini semantic-diff over
`config_edits` in eval_manifest.yaml) is the actual evaluation signal.
"""
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/selenium")
TARGET = REPO / "py" / "AGENTS.md"


def _read_target() -> str:
    assert TARGET.exists(), f"Expected {TARGET} to exist in the repo"
    return TARGET.read_text(encoding="utf-8")


def test_target_file_exists_and_nonempty():
    """py/AGENTS.md exists and is non-empty after the agent's edits."""
    content = _read_target()
    assert len(content) > 100, "py/AGENTS.md should not be near-empty"


def test_python_310_requirement_stated():
    """The instructions must call out Python 3.10 (or later) as the minimum."""
    content = _read_target()
    # Tolerant match: 'Python 3.10' optionally followed by '+' or 'or later'.
    assert re.search(r"[Pp]ython\s*3\.10", content), \
        "py/AGENTS.md must mention Python 3.10 as the minimum version"


def test_union_notation_rule_present():
    """The instructions must prefer union notation `|` over `Optional`."""
    content = _read_target()
    # The rule must mention BOTH union notation and Optional, in proximity.
    assert re.search(r"union notation", content, re.I), \
        "py/AGENTS.md must mention 'union notation'"
    assert "Optional" in content, \
        "py/AGENTS.md must reference Optional (the thing being replaced)"
    # Must show the `|` syntax somewhere in a code example (e.g., `str | None`).
    assert re.search(r"\b\w+\s*\|\s*None\b", content), \
        "py/AGENTS.md must show `<type> | None` union syntax in an example"


def test_local_python_version_check_guidance():
    """The instructions must tell the agent how to verify Python version locally."""
    content = _read_target()
    assert "python --version" in content, \
        "py/AGENTS.md must include the literal `python --version` command for local checks"


def test_python_version_section_heading():
    """A dedicated section/heading for the Python version rule must exist."""
    content = _read_target()
    # Must have a heading whose text contains 'Python version' (any heading level).
    assert re.search(r"^#+\s.*[Pp]ython\s+version", content, re.M), \
        "py/AGENTS.md must have a heading containing 'Python version'"


def test_repo_git_sanity():
    """Pass-to-pass: the cloned repo's working tree is intact (git ok)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    assert len(r.stdout.strip()) == 40, "Expected a 40-char SHA from git rev-parse"
