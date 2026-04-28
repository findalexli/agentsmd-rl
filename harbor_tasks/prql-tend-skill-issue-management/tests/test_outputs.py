"""
Track-1 sanity gate for markdown_authoring task: verifies the agent edited
the running-tend SKILL.md to include guidance about closing bot-opened issues.

The real evaluation signal is Track 2 (Gemini semantic-diff comparison
against config_edits in eval_manifest.yaml). These tests are a structural
nop=0 / gold=1 oracle.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/prql")
SKILL = REPO / ".claude/skills/running-tend/SKILL.md"


def _read_skill() -> str:
    """Read the SKILL.md via subprocess (cat) so the test exercises a real
    binary and surfaces missing-file issues uniformly.
    """
    r = subprocess.run(
        ["cat", str(SKILL)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"cat {SKILL} failed: {r.stderr}"
    return r.stdout


def test_skill_file_exists():
    """SKILL.md must still exist (sanity)."""
    r = subprocess.run(
        ["test", "-f", str(SKILL)],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"{SKILL} not found"


def test_issue_management_section_added():
    """A new top-level section titled 'Issue management' must be present."""
    content = _read_skill()
    assert "## Issue management" in content, (
        "Expected a new '## Issue management' section in "
        f"{SKILL.relative_to(REPO)}; not found."
    )


def test_section_addresses_bot_opened_issues():
    """The new guidance must address closing bot-opened issues."""
    content = _read_skill()
    # Find the Issue management section body.
    idx = content.find("## Issue management")
    assert idx != -1, "Issue management section missing"
    section = content[idx:]
    # Must mention bot-opened issues being closed.
    assert "bot-opened" in section or "prql-bot" in section, (
        "New section should reference bot-opened issues / prql-bot authorship"
    )
    # Must reference a closing/resolution mechanism.
    assert "Resolved by" in section or "closing" in section.lower(), (
        "New section should describe the close-with-comment mechanism "
        "(e.g., 'Resolved by #NNNN — closing')"
    )


def test_pre_existing_sections_preserved():
    """Existing 'PR conventions' and 'CI structure' sections must remain.

    Guards against an agent that wholesale-rewrites the file rather than
    appending the new section.
    """
    content = _read_skill()
    assert "## PR conventions" in content, (
        "Existing '## PR conventions' section was removed"
    )
    assert "## CI structure" in content, (
        "Existing '## CI structure' section was removed"
    )
    # Existing automerge bullet must remain.
    assert "pull-request-target.yaml" in content, (
        "Existing automerge bullet (pull-request-target.yaml) was removed"
    )


def test_skill_markdown_is_well_formed():
    """File must remain readable text and end with a trailing newline."""
    # Decoding via cat must succeed (covered by _read_skill's assert).
    content = _read_skill()
    assert content.endswith("\n"), "SKILL.md should end with a trailing newline"
    # Must not be empty.
    assert len(content.strip()) > 0, "SKILL.md is empty"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_grammars_build_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Build grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_grammars_test_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Test grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run test'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")