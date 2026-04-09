"""
Test suite for sui-framework build-system-packages fix.

The fix ensures that when UPDATE=1 is set, existing files are only deleted
AFTER the build succeeds, not before. This prevents data loss on build failures.
"""

import subprocess
import os
import tempfile
import shutil
import sys

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-framework/tests/build-system-packages.rs"
FULL_TARGET_PATH = os.path.join(REPO, TARGET_FILE)


def test_compilation_passes():
    """The modified test file should compile successfully (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-framework", "--tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr[-1000:]}"


def test_buggy_pattern_removed():
    """
    Fail-to-pass: The buggy pattern (delete before build) must be removed.
    Verifies the old conditional that deleted files before building is gone.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # The buggy pattern: conditional that deletes BEFORE build in the `if UPDATE` block
    # This should NOT exist in fixed code
    buggy_pattern = """let out_dir = if std::env::var_os("UPDATE").is_some() {
        let crate_root = Path::new(CRATE_ROOT);
        let _ = std::fs::remove_dir_all(crate_root.join(COMPILED_PACKAGES_DIR));
        let _ = std::fs::remove_dir_all(crate_root.join(DOCS_DIR));
        let _ = std::fs::remove_file(crate_root.join(PUBLISHED_API_FILE));
        crate_root"""

    # In fixed code, this pattern should NOT exist
    # This test passes when the fix is applied (buggy pattern gone)
    assert buggy_pattern not in content, "Buggy pattern still present - fix not applied"


def test_fixed_deletes_after_build():
    """
    Fail-to-pass: Fixed code deletes files AFTER build succeeds.
    Verify the fix pattern exists.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # The fix pattern: deletion happens after build_packages().await
    # and checks if path exists before deleting
    fix_patterns = [
        # Build happens first to tempdir
        "let out_dir = tempdir.path();",
        # Deletion happens after build
        "build_packages(",
        ".await;",
        # Check if exists before removing (safe deletion)
        'if p.exists() {',
        'std::fs::remove_dir_all(&p).unwrap();',
        # Copy from tempdir to crate_root after successful build
        "fs_extra::dir::copy(out_dir.join(COMPILED_PACKAGES_DIR)",
    ]

    # All fix patterns should be present in fixed code
    for pattern in fix_patterns:
        assert pattern in content, f"Fix pattern missing: {pattern}"


def test_update_builds_to_tempdir_first():
    """
    Fail-to-pass: In fixed code, out_dir is always tempdir.path().
    The build always happens to a temporary directory first.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # After fix, out_dir is unconditionally set to tempdir.path()
    # and crate_root is used only for deletion/copying after build
    lines = content.split('\n')

    # Find the line with `let out_dir =`
    out_dir_line = None
    for i, line in enumerate(lines):
        if 'let out_dir = tempdir.path();' in line:
            out_dir_line = i
            break

    assert out_dir_line is not None, "Fixed out_dir assignment not found"

    # After finding out_dir = tempdir.path(), verify there's NO conditional
    # assignment to crate_root before the build_packages call
    build_packages_line = None
    for i, line in enumerate(lines):
        if 'build_packages(' in line and i > out_dir_line:
            build_packages_line = i
            break

    assert build_packages_line is not None, "build_packages call not found"

    # Between out_dir assignment and build_packages, there should be NO
    # conditional that changes out_dir to crate_root
    for i in range(out_dir_line + 1, build_packages_line):
        if 'out_dir = ' in lines[i] and 'crate_root' in lines[i]:
            assert False, f"Found out_dir reassignment to crate_root before build at line {i}"


def test_safe_deletion_checks_existence():
    """
    Fail-to-pass: Fixed code checks if paths exist before deleting.
    This prevents errors when files don't exist.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # The fix adds existence checks before deletion
    safe_patterns = [
        'if p.exists() {',
        'std::fs::remove_dir_all(&p).unwrap();',
        'if api_file.exists() {',
        'std::fs::remove_file(&api_file).unwrap();',
    ]

    for pattern in safe_patterns:
        assert pattern in content, f"Safe deletion pattern missing: {pattern}"


def test_copy_from_tempdir_after_build():
    """
    Fail-to-pass: Fixed code copies from tempdir to crate_root after successful build.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Verify the copy operations from out_dir to crate_root exist
    copy_patterns = [
        'fs_extra::dir::copy(out_dir.join(COMPILED_PACKAGES_DIR), crate_root,',
        'fs_extra::dir::copy(out_dir.join(DOCS_DIR), crate_root,',
        'std::fs::copy(',
        'out_dir.join(PUBLISHED_API_FILE),',
        'crate_root.join(PUBLISHED_API_FILE),',
    ]

    for pattern in copy_patterns:
        assert pattern in content, f"Copy pattern missing: {pattern}"


def test_syntax_valid():
    """The Rust file should have valid syntax (pass_to_pass)."""
    result = subprocess.run(
        ["rustfmt", "--check", FULL_TARGET_PATH],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow formatting differences but not syntax errors
    # Actually, let's just check if rustc can parse it
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-framework", "--tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr[-500:]}"


def test_repo_clippy():
    """Repo's clippy lints pass on sui-framework (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-framework", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-500:]}"


def test_repo_rustfmt():
    """Repo's formatting standards pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Rustfmt check failed:\n{r.stdout[-500:]}"
