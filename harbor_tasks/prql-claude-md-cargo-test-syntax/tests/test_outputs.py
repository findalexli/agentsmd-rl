"""Tests for prql CLAUDE.md cargo-test syntax clarification (PR #5484).

Track 1 (this file) is a structural sanity gate. Track 2 (semantic diff judged
by Gemini against config_edits) is the primary signal for markdown_authoring.
"""
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/prql")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read_claude_md() -> str:
    # Use subprocess to invoke real cat — exercises the file from a process
    r = subprocess.run(
        ["cat", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"cat failed: {r.stderr}"
    return r.stdout


# --- fail_to_pass: these fail at base, pass after the gold edit ---

def test_unit_test_example_uses_dashdash_separator():
    """The unit-test example must use the `--` test-filter separator form."""
    content = _read_claude_md()
    assert "cargo insta test -p prqlc --lib -- resolver" in content, (
        "CLAUDE.md should show the unit-test command using the `-- <filter>` "
        "separator form, e.g. `cargo insta test -p prqlc --lib -- resolver`."
    )


def test_unit_tests_comment_present():
    """A comment labeling the unit-test example by its filter behavior must be present."""
    content = _read_claude_md()
    assert "# Unit tests filtered by test name" in content, (
        "CLAUDE.md should include the comment "
        "`# Unit tests filtered by test name` above the unit-test example."
    )


def test_integration_tests_comment_present():
    """A comment labeling the integration-test example by its filter behavior must be present."""
    content = _read_claude_md()
    assert "# Integration tests filtered by test name" in content, (
        "CLAUDE.md should include the comment "
        "`# Integration tests filtered by test name` above the integration-test example."
    )


def test_old_module_path_form_removed():
    """The misleading `--lib semantic::resolver` (module-path) example must be removed."""
    content = _read_claude_md()
    assert "cargo insta test -p prqlc --lib semantic::resolver" not in content, (
        "The old example `cargo insta test -p prqlc --lib semantic::resolver` "
        "(module-path positional form) should no longer appear in CLAUDE.md."
    )


def test_old_run_specific_tests_comment_removed():
    """The old vague comment `# Or run specific tests you're working on` should be removed."""
    content = _read_claude_md()
    assert "# Or run specific tests you're working on" not in content, (
        "The old vague comment `# Or run specific tests you're working on` "
        "should be replaced with a more specific label."
    )


def test_unit_example_appears_before_integration_example():
    """Unit-test example must appear before the integration-test example (faster first)."""
    content = _read_claude_md()
    unit_idx = content.find("cargo insta test -p prqlc --lib -- resolver")
    integ_idx = content.find("cargo insta test -p prqlc --test integration -- date")
    assert unit_idx != -1, "Unit-test example missing from CLAUDE.md"
    assert integ_idx != -1, "Integration-test example missing from CLAUDE.md"
    assert unit_idx < integ_idx, (
        "The unit-test example should appear before the integration-test "
        "example (faster feedback loop comes first)."
    )


# --- pass_to_pass: stable across the edit ---

def test_claude_md_exists():
    """CLAUDE.md must exist at the repo root."""
    r = subprocess.run(
        ["test", "-f", str(CLAUDE_MD)],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"CLAUDE.md not found at {CLAUDE_MD}"


def test_inner_loop_section_preserved():
    """The 'Inner loop' framing must be preserved."""
    content = _read_claude_md()
    assert "Inner loop" in content, "CLAUDE.md lost the 'Inner loop' framing."


def test_outer_loop_section_preserved():
    """The 'Outer loop' framing must be preserved."""
    content = _read_claude_md()
    assert "Outer loop" in content, "CLAUDE.md lost the 'Outer loop' framing."


def test_task_prqlc_test_command_preserved():
    """The unchanged `task prqlc:test` example must remain."""
    content = _read_claude_md()
    assert "task prqlc:test" in content, (
        "CLAUDE.md must keep the `task prqlc:test` example for fast tests."
    )


def test_task_test_all_command_preserved():
    """The unchanged `task test-all` outer-loop example must remain."""
    content = _read_claude_md()
    assert "task test-all" in content, (
        "CLAUDE.md must keep the `task test-all` example for the outer loop."
    )


def test_markdown_codefence_balanced():
    """Triple-backtick fences must be balanced (even count)."""
    content = _read_claude_md()
    fence_count = content.count("```")
    assert fence_count % 2 == 0, (
        f"CLAUDE.md has unbalanced ``` fences (count={fence_count}); "
        "the agent likely mismatched a code block."
    )


def test_git_repo_clean_outside_claude_md():
    """No tracked file outside CLAUDE.md should be modified."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    modified = [
        line for line in r.stdout.splitlines()
        if line and not line.endswith("CLAUDE.md")
    ]
    assert not modified, (
        "Only CLAUDE.md should be modified by this task. Other changes:\n"
        + "\n".join(modified)
    )

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