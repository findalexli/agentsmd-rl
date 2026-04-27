"""Behavioral / structural tests for the angular-developer testing-fundamentals
skill reference cleanup task.

The PR removes a "Custom Utilities" section that promoted symbols from the
private package path `packages/private/testing/src/utils.ts`. These tests
verify that:

  * fail_to_pass: distinctive phrases from the removed block are absent
    (these phrases ARE present at the base commit, so each test fails on
    base and passes on a correct fix).
  * pass_to_pass: the file still exists, is non-empty markdown, and
    retains the structural sections that the PR did NOT touch.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/angular")
TARGET = REPO / "skills/dev-skills/angular-developer/references/testing-fundamentals.md"


def _read_target() -> str:
    """Read the target file via subprocess (`cat`) so the test exercises the
    real filesystem the agent edited, not Python's import cache."""
    r = subprocess.run(
        ["cat", str(TARGET)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"`cat {TARGET}` failed (rc={r.returncode}): {r.stderr}"
    )
    return r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass: distinctive phrases from the removed section MUST be absent
# ---------------------------------------------------------------------------

def test_custom_utilities_heading_absent():
    """The `## Custom Utilities` heading should be removed entirely."""
    content = _read_target()
    assert "## Custom Utilities" not in content, (
        "The reference still contains the '## Custom Utilities' heading; "
        "the section that promotes private-package helpers must be removed."
    )


def test_private_testing_utils_path_absent():
    """No reference to the private-package source path may remain."""
    content = _read_target()
    assert "packages/private/testing/src/utils.ts" not in content, (
        "The reference still cites the private path "
        "`packages/private/testing/src/utils.ts`. Skill-facing docs must "
        "not promote symbols from private framework internals."
    )


def test_use_auto_tick_promotion_absent():
    """The closing recommendation that promoted the mock-clock helper must
    no longer appear."""
    content = _read_target()
    # Match the unique sentence from the removed block, allowing for
    # incidental whitespace/punctuation differences.
    pattern = re.compile(
        r"Always\s+prefer\s+`?useAutoTick\(\)`?\s+to\s+keep\s+tests\s+efficient",
        re.IGNORECASE,
    )
    assert not pattern.search(content), (
        "The reference still recommends `useAutoTick()`. The promotion of "
        "private-package helpers must be removed from the file."
    )


def test_use_auto_tick_symbol_absent():
    """The `useAutoTick()` helper itself was only mentioned inside the
    removed block; if the cleanup is complete, the symbol should no longer
    appear anywhere in the file."""
    content = _read_target()
    assert "useAutoTick" not in content, (
        "The symbol `useAutoTick` is still present in the testing "
        "fundamentals reference. The block that documented it must be "
        "removed in full."
    )


def test_timeout_helper_mention_absent():
    """The `await timeout(ms)` helper line was part of the removed block;
    its distinctive form must not remain."""
    content = _read_target()
    pattern = re.compile(r"`await\s+timeout\(ms\)`")
    assert not pattern.search(content), (
        "The reference still documents `await timeout(ms)` as a helper. "
        "All references to the private-package timing helpers must be "
        "removed."
    )


# ---------------------------------------------------------------------------
# pass_to_pass: structural integrity of the file is preserved
# ---------------------------------------------------------------------------

def test_target_file_exists_and_nonempty():
    """The reference file must still exist and remain non-empty."""
    r = subprocess.run(
        ["wc", "-c", str(TARGET)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"`wc -c` on the target failed: {r.stderr}"
    size = int(r.stdout.strip().split()[0])
    assert size > 200, (
        f"The target file is suspiciously small ({size} bytes). The "
        f"unrelated sections of the file should be preserved."
    )


def test_top_heading_preserved():
    """The top-level `# Testing Fundamentals` heading must still be the
    first heading in the file — only the trailing private-utilities
    section was supposed to be removed."""
    content = _read_target()
    assert content.lstrip().startswith("# Testing Fundamentals"), (
        "The top heading `# Testing Fundamentals` is missing or no longer "
        "the first heading. Do not modify the file's overall structure."
    )


def test_unrelated_sections_preserved():
    """Sections that the PR did NOT touch must remain intact."""
    content = _read_target()
    expected_sections = [
        "## Core Philosophy: Zoneless & Async-First",
        "### Basic Test Structure Example",
        "## TestBed and ComponentFixture",
    ]
    missing = [s for s in expected_sections if s not in content]
    assert not missing, (
        f"Expected sections missing from the file: {missing}. Only the "
        f"private-utilities block should have been removed."
    )


def test_testbed_section_is_final_section():
    """The `## TestBed and ComponentFixture` section was the last section
    *before* the removed `## Custom Utilities` block. After the cleanup it
    must be the file's final `##`-level section."""
    content = _read_target()
    h2_headings = re.findall(r"^## .+$", content, flags=re.MULTILINE)
    assert h2_headings, "No `##` headings found in file."
    assert h2_headings[-1].strip() == "## TestBed and ComponentFixture", (
        f"Expected the final `##` section to be "
        f"`## TestBed and ComponentFixture`, but got `{h2_headings[-1]}`. "
        f"The trailing private-utilities section must be removed without "
        f"introducing any new trailing section."
    )


def test_act_wait_assert_guidance_preserved():
    """The Core Philosophy 'Act, Wait, Assert' guidance must remain — it's
    unrelated to the private-utilities cleanup."""
    content = _read_target()
    assert "Act, Wait, Assert" in content, (
        "The 'Act, Wait, Assert' testing guidance has been removed; only "
        "the private-utilities section was supposed to be deleted."
    )


def test_basic_test_structure_example_preserved():
    """The runnable example block must remain in the file."""
    content = _read_target()
    assert "fixture.whenStable()" in content, (
        "The example referencing `fixture.whenStable()` is missing. The "
        "Basic Test Structure Example must be preserved."
    )


# ---------------------------------------------------------------------------
# pass_to_pass: working tree is in a clean / sane state
# ---------------------------------------------------------------------------

def test_working_tree_only_target_modified():
    """A correct fix touches exactly one file; no other files in the repo
    should have been modified."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"`git status` failed: {r.stderr}"
    changed = [
        line[3:] for line in r.stdout.splitlines() if line.strip()
    ]
    expected = "skills/dev-skills/angular-developer/references/testing-fundamentals.md"
    unexpected = [p for p in changed if p != expected]
    assert not unexpected, (
        f"Unexpected modified/untracked files: {unexpected}. Only "
        f"`{expected}` should have been changed."
    )
