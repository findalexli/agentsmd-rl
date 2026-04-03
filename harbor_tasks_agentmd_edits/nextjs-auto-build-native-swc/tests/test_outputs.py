"""
Task: nextjs-auto-build-native-swc
Repo: vercel/next.js @ def0e3aabfa112ada22ece9297501c52471d34bd
PR:   89819

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """scripts/build-native.ts must parse and contain writeTypes function."""
    ts_file = Path(REPO) / "scripts/build-native.ts"
    assert ts_file.exists(), "scripts/build-native.ts must exist"
    content = ts_file.read_text()
    assert "writeTypes" in content, "build-native.ts must contain writeTypes function"
    assert "buildNative" in content or "export default" in content, (
        "build-native.ts must export a build function"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_maybe_build_native_skips_in_ci():
    """maybe-build-native.mjs must skip the build when CI env var is set."""
    mjs_file = Path(REPO) / "packages/next-swc/maybe-build-native.mjs"
    assert mjs_file.exists(), "maybe-build-native.mjs must exist"

    r = subprocess.run(
        ["node", str(mjs_file)],
        capture_output=True, timeout=15,
        env={"CI": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/root"},
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Script failed with CI=1: {r.stderr.decode()}"
    )
    stdout = r.stdout.decode()
    assert "skipping" in stdout.lower() or "ci" in stdout.lower(), (
        f"Script should indicate it's skipping in CI, got: {stdout}"
    )


# [pr_diff] fail_to_pass
def test_maybe_build_native_has_rust_change_detection():
    """maybe-build-native.mjs must detect Rust source changes via git."""
    mjs_file = Path(REPO) / "packages/next-swc/maybe-build-native.mjs"
    content = mjs_file.read_text()
    content_lower = content.lower()

    # Must use git to detect changes in Rust files
    assert "git" in content_lower, "Script must use git to detect changes"
    assert "diff" in content_lower or "log" in content_lower, (
        "Script must use git diff or git log for change detection"
    )
    # Must look for .rs files or Rust-related paths
    assert ".rs" in content or "rust" in content_lower or "cargo" in content_lower, (
        "Script must check for Rust file changes"
    )
    # Must have version bump detection logic
    assert "version" in content_lower, (
        "Script must reference version bump for change detection baseline"
    )
    # Must handle .node binary files (clear stale or detect existing)
    assert ".node" in content, (
        "Script must manage .node binary files"
    )


# [pr_diff] fail_to_pass
def test_package_json_build_script():
    """packages/next-swc/package.json must have a build script invoking maybe-build-native."""
    pkg_json = Path(REPO) / "packages/next-swc/package.json"
    data = json.loads(pkg_json.read_text())

    scripts = data.get("scripts", {})
    assert "build" in scripts, (
        "package.json must have a 'build' script"
    )
    build_cmd = scripts["build"]
    assert "maybe-build-native" in build_cmd, (
        f"build script must invoke maybe-build-native, got: {build_cmd}"
    )


# [pr_diff] fail_to_pass
def test_turbo_json_build_task():
    """packages/next-swc/turbo.json must define a build task with Rust inputs and CI env."""
    turbo_json = Path(REPO) / "packages/next-swc/turbo.json"
    data = json.loads(turbo_json.read_text())

    tasks = data.get("tasks", {})
    assert "build" in tasks, "turbo.json must have a 'build' task"

    build_task = tasks["build"]

    # Must include Rust-related inputs
    inputs = build_task.get("inputs", [])
    input_str = " ".join(inputs)
    assert "crates" in input_str, "build task inputs must include crates"
    assert "Cargo" in input_str, "build task inputs must include Cargo files"
    assert "rust-toolchain" in input_str, "build task inputs must include rust-toolchain"

    # Must include CI in env for separate cache keys
    env = build_task.get("env", [])
    assert "CI" in env, "build task must include CI in env"

    # Must define outputs
    outputs = build_task.get("outputs", [])
    assert any(".node" in o for o in outputs), (
        "build task outputs must include .node files"
    )


# [pr_diff] fail_to_pass

    # Must use --stdin-filepath pattern for prettier
    assert "--stdin-filepath" in content or "stdin-filepath" in content, (
        "build-native.ts must use prettier with --stdin-filepath"
    )
    # Must NOT use the old --write pattern for prettier in writeTypes
    # (Note: --write may appear in comments or other contexts, so check the
    # specific prettier command construction)
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "prettifyCommand" in line and "--write" in line:
            assert False, (
                f"Line {i+1}: prettifyCommand should use --stdin-filepath, not --write"
            )

    # Must have content comparison to skip unnecessary writes
    assert "existingContent" in content or "existing" in content.lower(), (
        "build-native.ts should compare content before writing to skip no-op writes"
    )


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — AGENTS.md:367-371 @ 9a7733ed83bce9cc1264454ddc7335fdcfb0c1eb

    # The old instructions had separate commands for Rust-only and both edits.
    # After the change, pnpm build handles everything automatically.
    # The old "Edited Turbopack (Rust)? → pnpm swc-build-native" line should be gone.
    assert "swc-build-native" not in content, (
        "AGENTS.md should no longer recommend 'pnpm swc-build-native' directly - "
        "pnpm build now handles Rust changes automatically"
    )

    # The old "Edited both? → pnpm turbo build build-native" line should be gone.
    assert "turbo build build-native" not in content, (
        "AGENTS.md should no longer recommend 'pnpm turbo build build-native' - "
        "pnpm build now handles both cases"
    )

    # There should be a consolidated instruction that mentions pnpm build
    # for the Rust/combined case
    rebuild_section = ""
    in_rebuild = False
    for line in content.splitlines():
        if "rebuild" in line.lower() and "test" in line.lower():
            in_rebuild = True
        elif in_rebuild and line.startswith("## "):
            break
        if in_rebuild:
            rebuild_section += line + "\n"

    assert len(rebuild_section) > 0, (
        "AGENTS.md must have a 'Rebuilding Before Running Tests' section"
    )
    # The section should recommend pnpm build for Rust or combined changes
    assert "pnpm build" in rebuild_section, (
        "Rebuild section must recommend 'pnpm build' for handling changes"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_maybe_build_native_not_stub():
    """maybe-build-native.mjs must have real logic (not a trivial stub)."""
    mjs_file = Path(REPO) / "packages/next-swc/maybe-build-native.mjs"
    content = mjs_file.read_text()
    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("//")]

    # Must have substantial logic (at least 40 non-empty, non-comment lines)
    assert len(lines) >= 40, (
        f"maybe-build-native.mjs has only {len(lines)} non-empty lines, expected >= 40"
    )

    # Must have Rust change detection logic
    content_lower = content.lower()
    assert "rust" in content_lower or ".rs" in content or "cargo" in content_lower, (
        "Script must have Rust change detection logic"
    )
    # Must reference building native binaries
    assert "build" in content_lower and "native" in content_lower, (
        "Script must have native build logic"
    )
    # Must check CI environment
    assert "ci" in content_lower or "CI" in content, (
        "Script must check CI environment variable"
    )
