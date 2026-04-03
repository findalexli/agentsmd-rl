"""
Task: remix-add-script-to-setup-a
Repo: remix-run/remix @ 598a92e3dc3488b02da7e4edafd1ff2498cc4c34
PR:   10964

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without errors."""
    process_ts = Path(f"{REPO}/scripts/utils/process.ts")
    assert process_ts.exists(), "scripts/utils/process.ts not found"
    content = process_ts.read_text()
    assert len(content) > 50, "process.ts suspiciously small"
    assert "export" in content, "Missing exports in process.ts"
    assert "logAndExec" in content, "logAndExec function missing from process.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_log_and_exec_capture_support():
    """logAndExec must accept a capture parameter and return a string."""
    content = Path(f"{REPO}/scripts/utils/process.ts").read_text()

    # Must return string type (not void)
    func_match = re.search(
        r'export\s+function\s+logAndExec\s*\(([^)]*)\)\s*:\s*(\w+)',
        content,
    )
    assert func_match, "logAndExec function declaration not found"
    params = func_match.group(1)
    return_type = func_match.group(2)
    assert return_type == "string", \
        f"logAndExec must return string, got {return_type}"

    # Must accept more than just the command parameter (needs capture toggle)
    assert "," in params, \
        "logAndExec must accept a second parameter to toggle output capture"


# [pr_diff] fail_to_pass
def test_log_and_exec_pipe_stdio():
    """logAndExec must use stdio:'pipe' when capturing output."""
    content = Path(f"{REPO}/scripts/utils/process.ts").read_text()

    # When captureOutput is true, must use pipe mode (not inherit)
    assert "stdio: 'pipe'" in content or 'stdio: "pipe"' in content, \
        "logAndExec must use stdio:'pipe' for capture mode"

    # Must specify encoding for captured output
    assert "encoding:" in content and "utf-8" in content, \
        "logAndExec must specify utf-8 encoding when capturing"


# [pr_diff] fail_to_pass
def test_setup_script_operations():
    """setup-installable-branch.ts must implement git/package update operations."""
    script = Path(f"{REPO}/scripts/setup-installable-branch.ts")
    assert script.exists(), "scripts/setup-installable-branch.ts must exist"
    content = script.read_text()

    # Must handle .gitignore modification (remove dist entries)
    assert "gitignore" in content.lower() or ".gitignore" in content, \
        "Script must modify .gitignore to include dist/ in commits"

    # Must handle package dependency updates
    has_dep_update = (
        "dependencies" in content
        or "package.json" in content
        or "packageJson" in content
    )
    assert has_dep_update, \
        "Script must update package dependencies to use github branch format"

    # Must handle branch name from CLI arguments
    has_arg_parsing = (
        "parseArgs" in content
        or "process.argv" in content
        or "argv" in content
    )
    assert has_arg_parsing, \
        "Script must accept a branch name argument"

    # Must use logAndExec or execSync for git/shell commands
    has_exec = "logAndExec" in content or "execSync" in content
    assert has_exec, \
        "Script must execute shell commands (logAndExec or execSync)"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation/config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — README.md

    # Must have an Installation heading
    assert "## Installation" in content, \
        "README.md must have an '## Installation' section"

    # Must document the nightly branch install method
    has_nightly = "nightly" in content
    assert has_nightly, \
        "README.md must mention the nightly branch"

    # Must show pnpm install command with github syntax
    assert "pnpm install" in content or "pnpm i" in content, \
        "README.md must show the pnpm install command"

    # Must show the github#branch&path: install syntax
    assert "remix-run/remix#" in content and "path:" in content, \
        "README.md must show the github#branch&path: install syntax"


# [config_edit] fail_to_pass — CONTRIBUTING.md

    # Must have a Nightly Builds section
    assert "Nightly" in content, \
        "CONTRIBUTING.md must mention nightly builds"

    # Must reference the setup script
    assert "setup-installable-branch" in content, \
        "CONTRIBUTING.md must reference the setup-installable-branch script"

    # Must show the pnpm install syntax
    assert "pnpm install" in content or "pnpm i" in content, \
        "CONTRIBUTING.md must show the pnpm install command for nightly"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:23 @ 598a92e3
