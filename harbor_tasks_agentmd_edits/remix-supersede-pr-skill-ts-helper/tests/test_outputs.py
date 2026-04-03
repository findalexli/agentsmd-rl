"""
Task: remix-supersede-pr-skill-ts-helper
Repo: remix-run/remix @ 64b3a160dc25bbb082b96673e12bb55935f3528d
PR:   11088

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"
NODE = "node"
TS_FLAG = "--experimental-strip-types"
SCRIPT = f"{REPO}/skills/supersede-pr/scripts/close_superseded_pr.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_syntax_check():
    """TypeScript files in skills/ parse without errors using node --check."""
    skills_dir = Path(REPO, "skills")
    assert skills_dir.exists(), "skills/ directory not found"
    ts_files = list(skills_dir.rglob("*.ts"))
    assert len(ts_files) > 0, "No TypeScript files found in skills/"
    for ts_file in ts_files:
        r = subprocess.run(
            [NODE, TS_FLAG, "--check", str(ts_file)],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"{ts_file.name} failed syntax check:\n"
            f"{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the TS script
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_script_shows_help():
    """Script outputs usage info when called with --help."""
    r = subprocess.run(
        [NODE, TS_FLAG, SCRIPT, "--help"],
        capture_output=True, timeout=15,
    )
    out = r.stdout.decode()
    assert r.returncode == 0, f"--help exited with code {r.returncode}"
    assert "close_superseded_pr" in out.lower() or "old_pr" in out.lower(), (
        f"--help output missing usage info:\n{out}"
    )
    assert "--repo" in out, "--help should mention --repo flag"
    assert "--dry-run" in out, "--help should mention --dry-run flag"


# [pr_diff] fail_to_pass
def test_script_rejects_no_args():
    """Script exits non-zero when called without arguments."""
    r = subprocess.run(
        [NODE, TS_FLAG, SCRIPT],
        capture_output=True, timeout=15,
    )
    assert r.returncode != 0, "Script should exit non-zero with no arguments"


# [pr_diff] fail_to_pass
def test_script_rejects_non_numeric_pr():
    """Script rejects non-numeric PR number arguments."""
    r = subprocess.run(
        [NODE, TS_FLAG, SCRIPT, "abc", "123"],
        capture_output=True, timeout=15,
    )
    assert r.returncode != 0, "Script should reject non-numeric old_pr"
    stderr = r.stderr.decode()
    assert "numeric" in stderr.lower() or "number" in stderr.lower(), (
        f"Error message should mention numeric requirement:\n{stderr}"
    )


# [pr_diff] fail_to_pass
def test_script_rejects_same_pr_numbers():
    """Script rejects when old_pr and new_pr are the same number."""
    r = subprocess.run(
        [NODE, TS_FLAG, SCRIPT, "100", "100"],
        capture_output=True, timeout=15,
    )
    assert r.returncode != 0, "Script should reject identical PR numbers"
    stderr = r.stderr.decode()
    assert "different" in stderr.lower(), (
        f"Error should say PRs must be different:\n{stderr}"
    )


# [pr_diff] fail_to_pass
def test_script_has_shebang():
    """Script has executable shebang line for node."""
    script_path = Path(SCRIPT)
    assert script_path.exists(), f"Script not found at {SCRIPT}"
    first_line = script_path.read_text().splitlines()[0]
    assert first_line.startswith("#!/usr/bin/env node"), (
        f"Expected shebang '#!/usr/bin/env node', got: {first_line}"
    )


# [pr_diff] fail_to_pass
def test_tsconfig_exists():
    """tsconfig.json exists for the supersede-pr skill with correct settings."""
    import json
    tsconfig_path = Path(REPO, "skills", "supersede-pr", "tsconfig.json")
    assert tsconfig_path.exists(), "skills/supersede-pr/tsconfig.json not found"
    config = json.loads(tsconfig_path.read_text())
    opts = config.get("compilerOptions", {})
    assert opts.get("strict") is True, "tsconfig should enable strict mode"
    assert opts.get("noEmit") is True, "tsconfig should set noEmit"


# ---------------------------------------------------------------------------
# Config/documentation update tests (config_edit)
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
