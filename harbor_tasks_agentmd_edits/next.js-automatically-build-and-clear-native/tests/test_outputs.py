"""
Task: next.js-automatically-build-and-clear-native
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
def test_agents_md_has_rebuild_section():
    """AGENTS.md must contain the 'Rebuilding Before Running Tests' section."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "## Rebuilding Before Running Tests" in content, \
        "AGENTS.md must retain the 'Rebuilding Before Running Tests' section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_maybe_build_native_skips_in_ci():
    """Running maybe-build-native.mjs with CI=1 must exit 0 and print skip message."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    assert script.exists(), f"Script not found: {script}"
    result = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        text=True,
        timeout=15,
        env={"CI": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/root"},
        cwd=str(Path(REPO) / "packages" / "next-swc"),
    )
    assert result.returncode == 0, f"Script failed (rc={result.returncode}):\n{result.stderr}"
    assert "Skipping swc-build-native in CI" in result.stdout, \
        f"Expected CI skip message, got:\n{result.stdout}"


# [pr_diff] fail_to_pass
def test_maybe_build_native_has_rust_detection():
    """The script must contain logic for detecting Rust file changes."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    content = script.read_text()
    assert "hasRustChanges" in content, \
        "Script must define hasRustChanges function"
    assert "*.rs" in content or "**/*.rs" in content, \
        "Script must check for .rs file changes"
    assert "getVersionBumpCommit" in content, \
        "Script must define getVersionBumpCommit function"


# [pr_diff] fail_to_pass
def test_package_json_build_script():
    """packages/next-swc/package.json must have a 'build' script running maybe-build-native."""
    pkg = Path(REPO) / "packages" / "next-swc" / "package.json"
    data = json.loads(pkg.read_text())
    scripts = data.get("scripts", {})
    assert "build" in scripts, "package.json must have a 'build' script"
    assert "maybe-build-native" in scripts["build"], \
        f"build script must reference maybe-build-native, got: {scripts['build']}"


# [pr_diff] fail_to_pass
def test_turbo_json_build_task():
    """packages/next-swc/turbo.json must define a 'build' task with Rust-relevant inputs."""
    turbo = Path(REPO) / "packages" / "next-swc" / "turbo.json"
    data = json.loads(turbo.read_text())
    tasks = data.get("tasks", {})
    assert "build" in tasks, "turbo.json must define a 'build' task"
    build_task = tasks["build"]
    inputs = build_task.get("inputs", [])
    input_str = " ".join(inputs)
    assert "crates" in input_str, "build task inputs must include crates directory"
    assert "Cargo" in input_str, "build task inputs must include Cargo files"
    assert "CI" in build_task.get("env", []), "build task must include CI in env"


# [pr_diff] fail_to_pass
def test_build_native_uses_stdin_prettier():
    """scripts/build-native.ts must use prettier with --stdin-filepath (not --write)."""
    build_native = Path(REPO) / "scripts" / "build-native.ts"
    content = build_native.read_text()
    assert "--stdin-filepath" in content, \
        "build-native.ts must use --stdin-filepath for prettier"
    assert "'--write'" not in content and '"--write"' not in content, \
        "build-native.ts must not use --write for prettier"


# ---------------------------------------------------------------------------
# Config-edit (pr_diff) — AGENTS.md rebuild instructions simplified
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_simplified_rebuild():
    """AGENTS.md must replace separate Rust/both build commands with unified pnpm build."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    # Old instructions that should be removed
    assert "pnpm swc-build-native" not in content, \
        "AGENTS.md should no longer reference 'pnpm swc-build-native' as a standalone command"
    assert "pnpm turbo build build-native" not in content, \
        "AGENTS.md should no longer reference 'pnpm turbo build build-native'"
    # New simplified instruction should be present
    lines = content.split("\n")
    rebuild_lines = [l for l in lines if "Turbopack" in l and "Rust" in l and "pnpm build" in l]
    assert len(rebuild_lines) >= 1, \
        "AGENTS.md should have a line covering Turbopack/Rust edits pointing to 'pnpm build'"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_maybe_build_native_syntax():
    """maybe-build-native.mjs must exist and be syntactically valid JavaScript."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    if not script.exists():
        raise AssertionError("maybe-build-native.mjs does not exist")
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error:\n{result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates that must pass on base AND after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo JSON validity
def test_repo_package_json_valid():
    """Root package.json must be valid JSON (pass_to_pass)."""
    pkg = Path(REPO) / "package.json"
    try:
        json.loads(pkg.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is not valid JSON: {e}")


# [repo_tests] pass_to_pass — Repo turbo.json validity
def test_repo_turbo_json_valid():
    """Root turbo.json must be valid JSON (pass_to_pass)."""
    turbo = Path(REPO) / "turbo.json"
    try:
        json.loads(turbo.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f"turbo.json is not valid JSON: {e}")


# [repo_tests] pass_to_pass — next-swc package.json validity
def test_repo_next_swc_package_json_valid():
    """packages/next-swc/package.json must be valid JSON (pass_to_pass)."""
    pkg = Path(REPO) / "packages" / "next-swc" / "package.json"
    try:
        json.loads(pkg.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f"packages/next-swc/package.json is not valid JSON: {e}")


# [repo_tests] pass_to_pass — next-swc turbo.json validity
def test_repo_next_swc_turbo_json_valid():
    """packages/next-swc/turbo.json must be valid JSON (pass_to_pass)."""
    turbo = Path(REPO) / "packages" / "next-swc" / "turbo.json"
    try:
        json.loads(turbo.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f"packages/next-swc/turbo.json is not valid JSON: {e}")


# [repo_tests] pass_to_pass — validate-externals-doc.js syntax
def test_repo_validate_externals_doc_syntax():
    """scripts/validate-externals-doc.js must have valid syntax (pass_to_pass)."""
    script = Path(REPO) / "scripts" / "validate-externals-doc.js"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error in validate-externals-doc.js:\n{result.stderr}"


# [repo_tests] pass_to_pass — build-native.ts syntax
def test_repo_build_native_syntax():
    """scripts/build-native.ts must have valid syntax (pass_to_pass)."""
    script = Path(REPO) / "scripts" / "build-native.ts"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error in build-native.ts:\n{result.stderr}"
