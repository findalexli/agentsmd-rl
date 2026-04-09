"""
Task: react-enableViewTransition-rn-fb
Repo: react @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
PR:   36106

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"

FLAG_FILES = [
    "packages/shared/forks/ReactFeatureFlags.native-fb.js",
    "packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js",
    "packages/shared/forks/ReactFeatureFlags.test-renderer.www.js",
]


def _get_flag_value(file_path: str, flag_name: str) -> str | None:
    """Extract the value of a const export from a JS/Flow file."""
    content = Path(f"{REPO}/{file_path}").read_text()
    # Matches: export const enableViewTransition: boolean = false;
    #      or: export const enableViewTransition = false;
    m = re.search(rf"export\s+const\s+{flag_name}[^=]*=\s*(\w+)", content)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — enableViewTransition must be true in all 3 forks
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_enableViewTransition_native_fb():
    """enableViewTransition is enabled in the RN FB build flag file (node subprocess)."""
    r = subprocess.run(
        [
            "node", "-e",
            "const fs = require('fs');"
            "const src = fs.readFileSync(process.argv[1], 'utf8');"
            "const m = src.match(/enableViewTransition[^=]*=\\s*(\\w+)/);"
            "if (!m || m[1] !== 'true') {"
            "  console.error('got: ' + (m ? m[1] : 'null'));"
            "  process.exit(1);"
            "}",
            "--",
            f"{REPO}/{FLAG_FILES[0]}",
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, (
        f"enableViewTransition not 'true' in {FLAG_FILES[0]}: {r.stderr.strip()}"
    )


# [pr_diff] fail_to_pass
def test_enableViewTransition_test_renderer_native_fb():
    """enableViewTransition is enabled in the test-renderer native-fb flag file."""
    val = _get_flag_value(FLAG_FILES[1], "enableViewTransition")
    assert val == "true", (
        f"enableViewTransition should be 'true' in {FLAG_FILES[1]}, got '{val}'"
    )


# [pr_diff] fail_to_pass
def test_enableViewTransition_test_renderer_www():
    """enableViewTransition is enabled in the test-renderer www flag file."""
    val = _get_flag_value(FLAG_FILES[2], "enableViewTransition")
    assert val == "true", (
        f"enableViewTransition should be 'true' in {FLAG_FILES[2]}, got '{val}'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file integrity checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_flag_files_readable():
    """All modified flag files exist and are readable with expected exports."""
    for fp in FLAG_FILES:
        full = Path(f"{REPO}/{fp}")
        assert full.exists(), f"Missing file: {fp}"
        content = full.read_text()
        assert "enableViewTransition" in content, f"No enableViewTransition export in {fp}"
        assert "enableGestureTransition" in content, (
            f"File looks corrupted — missing enableGestureTransition in {fp}"
        )


# [static] pass_to_pass
def test_not_stub():
    """Flag value is a boolean literal, not a placeholder or variable."""
    for fp in FLAG_FILES:
        val = _get_flag_value(fp, "enableViewTransition")
        assert val in ("true", "false"), (
            f"enableViewTransition in {fp} is not a boolean literal, got '{val}'"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — from .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass
def test_all_fork_files_consistent():
    """enableViewTransition has the same value across all three modified fork files.

    The feature-flags skill states: 'Missing fork files — Always add flags to
    ALL fork files, not just the main one.'
    """
    values = [_get_flag_value(fp, "enableViewTransition") for fp in FLAG_FILES]
    assert all(v == "true" for v in values), (
        f"enableViewTransition not consistently enabled across fork files: {values}"
    )
