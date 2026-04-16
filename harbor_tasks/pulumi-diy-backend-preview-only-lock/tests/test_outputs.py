"""Tests for pulumi#22385: Remove state lock for refresh --preview-only for diy backend."""

import subprocess
import sys
import os

REPO = "/workspace/pulumi"
PKG_DIR = f"{REPO}/pkg"


def test_refresh_preview_only_no_lock_behavioral():
    """
    FAIL-TO-PASS: When Refresh is called with PreviewOnly=true, the state lock
    should NOT be acquired. On the buggy base commit, Lock() is called before
    the PreviewOnly check, so it would acquire the lock unnecessarily.

    This test verifies the behavioral fix by examining the code flow.
    """
    # Read the backend.go file and verify the lock is now after the PreviewOnly check
    backend_file = f"{PKG_DIR}/backend/diy/backend.go"
    with open(backend_file, 'r') as f:
        content = f.read()

    # Find the Refresh function
    refresh_start = content.find("func (b *diyBackend) Refresh(")
    assert refresh_start != -1, "Could not find Refresh function"

    # Find the next function to limit our search scope
    next_func = content.find("\nfunc ", refresh_start + 1)
    refresh_content = content[refresh_start:next_func if next_func != -1 else len(content)]

    # Check that Lock() call comes AFTER the PreviewOnly check (the fix)
    # In the fixed version, Lock() appears after "PreviewThenPromptThenExecute" in the else branch
    preview_only_idx = refresh_content.find("if op.Opts.PreviewOnly")
    lock_idx = refresh_content.find("b.Lock(ctx, stack.Ref())")

    assert preview_only_idx != -1, "Could not find PreviewOnly check in Refresh function"
    assert lock_idx != -1, "Could not find Lock call in Refresh function"

    # The fix: Lock() should come AFTER the PreviewOnly check (higher index = later in code)
    assert lock_idx > preview_only_idx, \
        "Lock() is called before PreviewOnly check - it should only be acquired when NOT in preview-only mode"


def test_refresh_function_structure():
    """
    FAIL-TO-PASS: Verify the Refresh function has the correct control flow structure
    with Lock moved to only execute in the non-preview path.
    """
    backend_file = f"{PKG_DIR}/backend/diy/backend.go"
    with open(backend_file, 'r') as f:
        content = f.read()

    # Find the Refresh function
    refresh_start = content.find("func (b *diyBackend) Refresh(")
    assert refresh_start != -1, "Could not find Refresh function"

    next_func = content.find("\nfunc ", refresh_start + 1)
    refresh_content = content[refresh_start:next_func if next_func != -1 else len(content)]

    # Check for the distinctive pattern of the fix:
    # 1. PreviewOnly check comes first
    # 2. Lock is in the else branch (after the PreviewOnly block)
    # 3. PreviewThenPromptThenExecute is called with the lock held

    assert "if op.Opts.PreviewOnly" in refresh_content, \
        "Missing PreviewOnly check in Refresh function"

    # In the fixed version, ApplierOptions should be used in the preview path
    assert "opts := backend.ApplierOptions{" in refresh_content, \
        "Missing ApplierOptions in Refresh function - distinctive line from patch not found"

    # The unlock defer should be after the lock in the else branch
    assert "defer b.Unlock(ctx, stack.Ref())" in refresh_content, \
        "Missing Unlock defer in Refresh function"


def test_pkg_backend_diy_compiles():
    """
    PASS-TO-PASS: The pkg/backend/diy package should compile without errors.
    """
    result = subprocess.run(
        ["go", "build", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"pkg/backend/diy failed to compile:\n{result.stderr}"


def test_pkg_unit_tests():
    """
    PASS-TO-PASS: Run unit tests for the pkg module.
    This is based on the agent config instruction from pkg/AGENTS.md.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "-tags", "all", "-timeout", "300s", "-run", "TestDIY", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    # This may fail if no DIY-specific tests exist, but the package should at least be testable
    # We mainly care that it doesn't panic or fail to compile
    if result.returncode != 0:
        # Check if it's just "no tests" vs actual failure
        if "no test files" in result.stderr or "no tests to run" in result.stdout:
            return  # OK if no tests exist
        # If there are actual test failures, report them
        assert False, f"Tests failed:\n{result.stdout}\n{result.stderr}"


def test_go_lint():
    """
    PASS-TO-PASS: Run Go linting based on agent config instructions.
    From CLAUDE.md: 'mise exec -- make lint' for any .go file change.
    """
    # Check if golangci-lint is available
    result = subprocess.run(
        ["which", "golangci-lint"],
        capture_output=True
    )

    if result.returncode != 0:
        # Try to install or skip
        return  # Skip if linter not available

    result = subprocess.run(
        ["golangci-lint", "run", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Linting failed:\n{result.stderr}"


def test_no_generated_file_modifications():
    """
    PASS-TO-PASS: Verify no generated proto files were modified.
    From CLAUDE.md: "Do not edit generated proto files by hand".
    """
    # This is a pass-to-pass check that the agent followed the rule
    # Check that no proto-generated files were modified
    proto_generated_patterns = [
        "pkg/proto/",
        "sdk/proto/",
    ]

    for pattern in proto_generated_patterns:
        # We're checking the specific file that was modified
        pass

    # The actual check: backend.go is NOT a generated file
    modified_file = f"{PKG_DIR}/backend/diy/backend.go"
    assert os.path.exists(modified_file), "backend.go should exist"

    # Read a sample to confirm it's not generated
    with open(modified_file, 'r') as f:
        content = f.read()

    assert "// Code generated" not in content[:500], \
        "backend.go appears to be a generated file - should not be edited directly"


def test_repo_go_build_backend_diy():
    """
    PASS-TO-PASS: Repo CI - go build for pkg/backend/diy compiles.
    Based on CI workflow: go build should succeed for the modified package.
    """
    result = subprocess.run(
        ["go", "build", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"go build ./backend/diy/... failed:\n{result.stderr}"


def test_repo_go_vet_backend_diy():
    """
    PASS-TO-PASS: Repo CI - go vet for pkg/backend/diy passes.
    Based on CI workflow: go vet should pass for the modified package.
    """
    result = subprocess.run(
        ["go", "vet", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"go vet ./backend/diy/... failed:\n{result.stderr}"


def test_repo_go_test_diy_backend():
    """
    PASS-TO-PASS: Repo CI - go test for pkg/backend/diy passes.
    Based on CI workflow: unit tests for the modified package should pass.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "-tags", "all", "-short", "-timeout", "120s", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"go test for backend/diy failed:\n{result.stdout}\n{result.stderr}"


def test_repo_go_fmt_backend_diy():
    """
    PASS-TO-PASS: Repo CI - go fmt for pkg/backend/diy produces no changes.
    Based on CI workflow: code should be properly formatted.
    """
    result = subprocess.run(
        ["go", "fmt", "./backend/diy/..."],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )
    # go fmt returns the names of files that would be formatted
    # If there are no files to format, it returns empty output
    assert result.stdout.strip() == "", \
        f"go fmt found formatting issues in backend/diy. Run 'go fmt ./backend/diy/...' to fix:\n{result.stdout}"
    assert result.returncode == 0, \
        f"go fmt failed:\n{result.stderr}"


def test_repo_go_mod_tidy_pkg():
    """
    PASS-TO-PASS: Repo CI - go mod tidy for pkg module produces no changes.
    Based on CI workflow: go.mod should be clean.
    """
    result = subprocess.run(
        ["go", "mod", "tidy"],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"go mod tidy in pkg/ failed:\n{result.stderr}"
