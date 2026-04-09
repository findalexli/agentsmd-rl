"""
Tests for sui-framework UPDATE ordering fix.

The bug: When UPDATE=1 is set, the test deletes files BEFORE building,
so if the build fails, the files are gone.

The fix: Build to temp dir first, then delete and copy only if build succeeds.
"""

import subprocess
import os
import sys

REPO = "/workspace/sui"
TEST_FILE = "crates/sui-framework/tests/build-system-packages.rs"
FULL_TEST_PATH = f"{REPO}/{TEST_FILE}"

def test_build_happens_before_file_operations():
    """
    Fail-to-pass: The fixed code builds to temp dir first,
    then performs file operations. The buggy code does file
    operations first, then build.
    """
    with open(FULL_TEST_PATH, 'r') as f:
        content = f.read()

    # Find the build_system_packages function
    func_start = content.find("async fn build_system_packages()")
    func_end = content.find("async fn build_packages", func_start)
    func_body = content[func_start:func_end]

    # The fix: out_dir should always be tempdir.path() at the start
    # In the buggy code, out_dir was conditionally set to crate_root when UPDATE is set
    # In the fixed code, out_dir = tempdir.path() unconditionally

    # Find the line where out_dir is set
    lines = func_body.split('\n')
    out_dir_line = None
    for line in lines:
        if 'let out_dir' in line and 'tempdir.path()' in line:
            out_dir_line = line.strip()
            break

    # The fix should have: let out_dir = tempdir.path();
    # (without any conditional around it at the start of the function)
    assert out_dir_line is not None, "out_dir should be set to tempdir.path()"
    assert '= tempdir.path();' in out_dir_line, \
        f"out_dir must be unconditionally set to tempdir.path(), got: {out_dir_line}"


def test_update_file_deletion_happens_after_build():
    """
    Fail-to-pass: In the fixed code, file deletion happens AFTER
    the build_packages() call, not before.
    """
    with open(FULL_TEST_PATH, 'r') as f:
        content = f.read()

    # Find the build_system_packages function
    func_start = content.find("async fn build_system_packages()")
    func_end = content.find("async fn build_packages", func_start)
    func_body = content[func_start:func_end]

    # Find where build_packages is called (it's a call to build_packages, not the fn definition)
    build_call_idx = func_body.find(".await;\n    check_diff")
    assert build_call_idx != -1, "Should find build_packages call followed by check_diff"

    # Find where UPDATE env var is checked for file deletion
    update_check_idx = func_body.find('if std::env::var_os("UPDATE").is_some()')
    assert update_check_idx != -1, "Should find UPDATE env var check for file operations"

    # In the fixed code, UPDATE check comes AFTER the build
    assert update_check_idx > build_call_idx, \
        "UPDATE file deletion must happen AFTER build_packages completes"


def test_update_copies_files_from_temp_dir():
    """
    Pass-to-pass: Verify the fix includes copying files from temp dir
    to crate root when UPDATE is set.
    """
    with open(FULL_TEST_PATH, 'r') as f:
        content = f.read()

    # Should have fs_extra::dir::copy calls for the compiled packages
    assert 'fs_extra::dir::copy(out_dir.join(COMPILED_PACKAGES_DIR)' in content, \
        "Should copy COMPILED_PACKAGES_DIR from temp out_dir to crate_root"
    assert 'fs_extra::dir::copy(out_dir.join(DOCS_DIR)' in content, \
        "Should copy DOCS_DIR from temp out_dir to crate_root"
    assert 'std::fs::copy(\n            out_dir.join(PUBLISHED_API_FILE)' in content or \
           'std::fs::copy(out_dir.join(PUBLISHED_API_FILE)' in content, \
        "Should copy PUBLISHED_API_FILE from temp out_dir to crate_root"


def test_file_deletion_checks_existence():
    """
    Pass-to-pass: The fix includes existence checks before deletion
    to avoid errors if files don't exist.
    """
    with open(FULL_TEST_PATH, 'r') as f:
        content = f.read()

    # Find the UPDATE block
    update_idx = content.find('if std::env::var_os("UPDATE").is_some()')
    assert update_idx != -1, "Should have UPDATE check"

    # Get the block (rough approximation - check for patterns)
    # The fix should check if paths exist before removing
    assert 'if p.exists()' in content, \
        "Should check if directory exists before remove_dir_all"
    assert 'if api_file.exists()' in content, \
        "Should check if api_file exists before remove_file"


def test_compiles_without_errors():
    """
    Pass-to-pass: The modified test file should compile.
    """
    result = subprocess.run(
        ['cargo', 'check', '--test', 'build-system-packages', '-p', 'sui-framework'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes for check
    )

    assert result.returncode == 0, \
        f"cargo check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_repo_cargo_check_sui_framework():
    """
    Pass-to-pass: The sui-framework crate should pass cargo check.
    Verifies the crate compiles without errors on the base commit.
    """
    result = subprocess.run(
        ['cargo', 'check', '-p', 'sui-framework'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120  # 2 minutes for check
    )

    assert result.returncode == 0, \
        f"cargo check -p sui-framework failed:\nstderr: {result.stderr[-1000:]}"


def test_repo_rustfmt_check():
    """
    Pass-to-pass: Rust code should be properly formatted.
    Verifies the repo's formatting standards are met.
    """
    result = subprocess.run(
        ['cargo', 'fmt', '--', '--check'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60  # 1 minute for fmt check
    )

    assert result.returncode == 0, \
        f"cargo fmt --check failed (formatting issues):\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
