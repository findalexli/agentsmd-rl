"""
Task: beam-gha-workflow-readme-check
Repo: apache/beam @ ae6d624c2b6d1fed15e4e96bf40e707808ad652b
PR:   37883

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/beam"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """build.gradle must be syntactically valid (balanced braces)."""
    build_gradle = Path(REPO) / ".github" / "build.gradle"
    content = build_gradle.read_text()
    # Basic structural check: braces must be balanced
    assert content.count("{") == content.count("}"), \
        "build.gradle has unbalanced braces"
    # Must still contain the existing check task
    assert "task check" in content, "build.gradle must contain 'task check'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: Gradle README check
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass

    This replicates the Gradle check behaviorally: scan for beam_*.yml
    files and verify each filename stem appears in the README.
    """
    workflows_dir = Path(REPO) / ".github" / "workflows"
    readme = workflows_dir / "README.md"
    readme_content = readme.read_text()

    beam_files = sorted(workflows_dir.glob("beam_*.yml"))
    assert len(beam_files) > 0, "Expected beam_*.yml workflow files"

    missing = []
    for yml_file in beam_files:
        fname = yml_file.stem  # e.g. beam_PreCommit_GHA
        if fname not in readme_content:
            missing.append(fname)

    assert not missing, \
        f"Workflows missing from README.md: {missing[:10]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — runner label change
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_precommit_lightweight_jobs_use_small_runner():
    """PreCommit GHA, RAT, and Whitespace jobs should use 'small' runner."""
    workflows_dir = Path(REPO) / ".github" / "workflows"
    for name in [
        "beam_PreCommit_GHA.yml",
        "beam_PreCommit_RAT.yml",
        "beam_PreCommit_Whitespace.yml",
    ]:
        content = (workflows_dir / name).read_text()
        # Check the runs-on line contains 'small' instead of 'main'
        runs_on_lines = [
            line for line in content.splitlines()
            if "runs-on:" in line and "ubuntu-20.04" in line
        ]
        assert runs_on_lines, f"{name}: no runs-on line with ubuntu-20.04 found"
        for line in runs_on_lines:
            assert "small" in line, \
                f"{name}: runs-on should use 'small' runner, got: {line.strip()}"
