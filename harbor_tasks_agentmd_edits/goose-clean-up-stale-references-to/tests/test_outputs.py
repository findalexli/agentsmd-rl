"""
Task: goose-clean-up-stale-references-to
Repo: block/goose @ f6fdbbdd7e75e7758c4ceced46fd65fb1fc76a42
PR:   8142

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/goose"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_syntax():
    """Modified Rust files compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--package", "goose"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed: {r.stderr}"


# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files have no syntax errors."""
    ui_dir = Path(REPO) / "ui" / "desktop"
    # Check if TypeScript can parse the files (requires npm install first)
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=ui_dir,
    )
    # npm install may have warnings but should succeed
    if r.returncode != 0:
        # Try with --legacy-peer-deps if standard install fails
        r = subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=ui_dir,
        )
    # Type check the modified files
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=ui_dir,
    )
    # Allow some lib check errors, but syntax errors should fail
    assert "error TS" not in r.stdout or "Cannot find name" in r.stdout, f"TypeScript syntax error: {r.stdout}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_log_level_upgraded_to_warn():
    """Extensions config save failure logs at warn level, not debug."""
    extensions_file = Path(REPO) / "crates" / "goose" / "src" / "config" / "extensions.rs"
    content = extensions_file.read_text()

    # In the fixed version, tracing::warn! should be used in save_extensions_map
    # Find the save_extensions_map function and check the log level
    lines = content.split('\n')
    in_save_fn = False
    found_warn = False

    for i, line in enumerate(lines):
        if "fn save_extensions_map" in line:
            in_save_fn = True
        elif in_save_fn and line.strip().startswith("fn "):
            in_save_fn = False
        elif in_save_fn and 'tracing::warn!' in line and 'Failed to save extensions config' in line:
            found_warn = True
            break
        # Old buggy code used tracing::debug! - that would fail this test

    assert found_warn, "save_extensions_map should use tracing::warn! for save failures"


# [pr_diff] fail_to_pass
def test_stale_todo_comment_removed():
    """Stale TODO comment in experiments.rs has been removed."""
    experiments_file = Path(REPO) / "crates" / "goose" / "src" / "config" / "experiments.rs"
    content = experiments_file.read_text()

    # The old TODO comment should be removed
    assert "TODO: keep this up to date with the experimental-features.md" not in content, \
        "Stale TODO comment should be removed from experiments.rs"


# [pr_diff] fail_to_pass
def test_dead_file_interruption_handler_removed():
    """Dead code file InterruptionHandler.tsx has been removed."""
    dead_file = Path(REPO) / "ui" / "desktop" / "src" / "components" / "InterruptionHandler.tsx"
    assert not dead_file.exists(), "InterruptionHandler.tsx dead code file should be removed"


# [pr_diff] fail_to_pass
def test_dead_file_use_recipe_manager_removed():
    """Dead code file useRecipeManager.ts hook has been removed."""
    dead_file = Path(REPO) / "ui" / "desktop" / "src" / "hooks" / "useRecipeManager.ts"
    assert not dead_file.exists(), "useRecipeManager.ts dead code file should be removed"


# [pr_diff] fail_to_pass
def test_debug_console_log_removed_from_app():
    """Debug console.log statements removed from App.tsx."""
    app_file = Path(REPO) / "ui" / "desktop" / "src" / "App.tsx"
    content = app_file.read_text()

    # Check for specific debug logs that were removed
    assert "console.log('Sending reactReady signal to Electron')" not in content, \
        "Debug console.log should be removed from App.tsx"
    assert "console.log('Setting up keyboard shortcuts')" not in content, \
        "Debug console.log should be removed from App.tsx"


# [pr_diff] fail_to_pass
def test_dead_file_waveform_visualizer_removed():
    """Dead code file WaveformVisualizer.tsx has been removed."""
    dead_file = Path(REPO) / "ui" / "desktop" / "src" / "components" / "WaveformVisualizer.tsx"
    assert not dead_file.exists(), "WaveformVisualizer.tsx dead code file should be removed"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_rust_tests_still_pass():
    """Core Rust tests still pass after cleanup."""
    r = subprocess.run(
        ["cargo", "test", "--package", "goose", "--lib", "config::", "--", "--test-threads=1"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Rust tests failed: {r.stderr}"
