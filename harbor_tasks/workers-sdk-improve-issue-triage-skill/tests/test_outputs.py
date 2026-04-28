"""Verifier tests for the workers-sdk issue-review skill rewrite.

The PR rewrites .github/skills/issue-review.md to expand the issue-triage
playbook with explicit closeable-issue categories, GitHub state_reason values,
a "breaking change" keep-open category, an "insufficient information" step,
and an enlarged component-mapping table.

These tests check that the agent's edits land on the same observable
restructure (Track 1 oracle). Track 2 (Gemini config-edit comparison) is the
primary semantic signal; this file is the structural gate.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/workers-sdk")
TARGET = REPO / ".github" / "skills" / "issue-review.md"


def _content() -> str:
    assert TARGET.exists(), f"target file missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass: base commit fails these; gold passes them
# ---------------------------------------------------------------------------


def test_step2_renamed_to_closeable_issues():
    """Step 2 heading should describe 'Closeable Issues' (was 'Empty or Invalid Issues')."""
    text = _content()
    assert "Check for Closeable Issues" in text, (
        "Expected 'Check for Closeable Issues' heading. The Step 2 heading "
        "should be reframed from a narrow empty/invalid check to a broad "
        "closeable-issue triage with multiple categories."
    )
    assert "Check for Empty or Invalid Issues" not in text, (
        "The old 'Check for Empty or Invalid Issues' heading should be removed "
        "in favor of the broader Closeable Issues framing."
    )


def test_state_reason_terminology_present():
    """state_reason (GitHub's close-reason field) should be referenced."""
    text = _content()
    assert "state_reason" in text, (
        "Expected the document to reference `state_reason` — the GitHub "
        "close-reason field that distinguishes `completed` vs `not_planned` "
        "closes."
    )
    # Both close-reason values should appear so the agent has marked which
    # categories close as completed vs not_planned.
    assert "not_planned" in text, "Expected `not_planned` close-reason value"
    assert "completed" in text, "Expected `completed` close-reason value"


def test_breaking_change_is_keep_open_category():
    """Breaking-change category should be a KEEP OPEN recommendation, not a close."""
    text = _content()
    assert "Breaking Change" in text, "Expected a 'Breaking Change' category"
    # The breaking-change section must explicitly recommend KEEP OPEN.
    # Search for KEEP OPEN occurring within ~400 chars after 'Breaking Change'.
    m = re.search(r"Breaking Change[\s\S]{0,500}KEEP OPEN", text)
    assert m is not None, (
        "Breaking-change category must recommend KEEP OPEN (the team hasn't "
        "decided against it; it's deferred to a future major version)."
    )


def test_insufficient_information_step_present():
    """A dedicated 'Insufficient Information' step should follow the closeable-issue check."""
    text = _content()
    assert "Check for Insufficient Information" in text, (
        "Expected a 'Check for Insufficient Information' step that handles "
        "NEEDS MORE INFO recommendations as a separate stage."
    )


def test_component_table_has_new_package_categories():
    """The expanded component-identification table should cover new package categories."""
    text = _content()
    required_signals = [
        "Workers + Assets",
        "containers",
        "workflows",
        "kv-asset-handler",
    ]
    missing = [s for s in required_signals if s not in text]
    assert not missing, (
        f"Component table missing rows for: {missing!r}. The table should be "
        f"expanded to cover containers, workflows, kv-asset-handler, and "
        f"Workers + Assets package mappings."
    )


def test_file_substantially_grew():
    """Skill file should grow substantially (was 163 lines, gold ~360)."""
    r = subprocess.run(
        ["wc", "-l", str(TARGET)], capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"wc failed: {r.stderr}"
    lines = int(r.stdout.split()[0])
    assert lines >= 250, (
        f"Expected the rewritten skill file to be >=250 lines (with "
        f"per-category templates, state_reason notes, and an expanded "
        f"component table), got {lines}."
    )


# ---------------------------------------------------------------------------
# pass_to_pass: hold both at base and gold
# ---------------------------------------------------------------------------


def test_yaml_frontmatter_intact():
    """YAML frontmatter must be preserved (skill name and description)."""
    text = _content()
    assert text.startswith("---\n"), "File must begin with YAML frontmatter"
    # Use python -c via subprocess to parse the frontmatter (verifies the YAML
    # is well-formed enough to extract the skill name).
    script = (
        "import sys, re\n"
        "t = open(sys.argv[1]).read()\n"
        "m = re.match(r'---\\n(.*?)\\n---\\n', t, re.S)\n"
        "assert m, 'no frontmatter'\n"
        "fm = m.group(1)\n"
        "assert 'name: github-issue-review' in fm, 'name field missing'\n"
        "assert 'description:' in fm, 'description field missing'\n"
        "print('ok')\n"
    )
    r = subprocess.run(
        ["python3", "-c", script, str(TARGET)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"frontmatter parse failed: {r.stderr}"


def test_skill_h1_heading_present():
    """The H1 heading should remain '# GitHub Issue Triage Skill'."""
    text = _content()
    assert "# GitHub Issue Triage Skill" in text, (
        "The skill's H1 heading must be preserved"
    )


def test_input_section_references_context_json():
    """The Input section should still describe the pre-fetched context.json source."""
    text = _content()
    assert "context.json" in text, (
        "The skill must still describe its input as a pre-fetched context.json"
    )

