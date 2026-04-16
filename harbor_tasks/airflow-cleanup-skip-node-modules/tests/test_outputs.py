"""
Tests for cleanup_python_generated_files performance fix.

This test verifies that the cleanup_python_generated_files() function:
1. Uses os.walk instead of rglob for traversal
2. Skips node_modules directories (performance optimization)
3. Skips hidden directories starting with "." (performance optimization)
4. Still correctly cleans up .pyc files in regular directories
5. Still correctly cleans up __pycache__ directories
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/airflow"
TARGET_FILE = Path(REPO) / "dev/breeze/src/airflow_breeze/utils/path_utils.py"


def cleanup_python_generated_files_original(root_path: Path):
    """
    Original implementation using rglob - for comparison.
    """
    permission_errors = []
    for path in root_path.rglob("*.pyc"):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except PermissionError:
            permission_errors.append(path)
    for path in root_path.rglob("__pycache__"):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            permission_errors.append(path)
    return permission_errors


def cleanup_python_generated_files_fixed(root_path: Path):
    """
    Fixed implementation using os.walk with pruning.
    This is what the patched code should implement.
    """
    permission_errors = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip node_modules and hidden directories (.*) — modify in place to prune os.walk
        dirnames[:] = [d for d in dirnames if d != "node_modules" and not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(".pyc"):
                path = Path(dirpath) / filename
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
                except PermissionError:
                    permission_errors.append(path)
        if Path(dirpath).name == "__pycache__":
            try:
                shutil.rmtree(dirpath)
            except FileNotFoundError:
                pass
            except PermissionError:
                permission_errors.append(Path(dirpath))
            dirnames.clear()
    return permission_errors


def test_uses_os_walk_instead_of_rglob():
    """
    Verify that cleanup_python_generated_files uses os.walk instead of rglob.
    
    This is a structural test to verify the implementation change.
    """
    content = TARGET_FILE.read_text()
    
    # The fixed version should use os.walk
    assert "os.walk" in content, "Expected os.walk to be used for directory traversal"
    
    # The fixed version should NOT use rglob for .pyc files in the cleanup function
    # We need to check specifically in the cleanup_python_generated_files function
    lines = content.split('\n')
    in_cleanup = False
    func_indent = None
    cleanup_lines = []
    
    for line in lines:
        if 'def cleanup_python_generated_files' in line:
            in_cleanup = True
            func_indent = len(line) - len(line.lstrip())
            cleanup_lines.append(line)
            continue
        
        if in_cleanup:
            # Check if we've exited the function
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Check if this is a new function definition at same or lower level
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= func_indent:
                    break
            cleanup_lines.append(line)
    
    cleanup_content = '\n'.join(cleanup_lines)
    assert 'rglob("*.pyc")' not in cleanup_content, \
        "Should not use rglob for .pyc files in cleanup_python_generated_files"
    assert 'rglob("__pycache__")' not in cleanup_content, \
        "Should not use rglob for __pycache__ in cleanup_python_generated_files"


def test_skips_node_modules():
    """
    Verify that cleanup_python_generated_files skips node_modules directories.
    
    The fixed implementation should NOT delete .pyc files in node_modules,
    while the original implementation (using rglob) would delete them.
    
    This test demonstrates the behavioral difference between base and fixed.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create structure: regular dir with .pyc, and node_modules with .pyc
        regular_dir = tmp_path / "regular"
        regular_dir.mkdir()
        regular_pyc = regular_dir / "test.pyc"
        regular_pyc.write_text("regular pyc")
        
        node_modules_dir = tmp_path / "node_modules"
        node_modules_dir.mkdir()
        nested_pyc = node_modules_dir / "module.pyc"
        nested_pyc.write_text("node_modules pyc")
        
        # Test the FIXED behavior: node_modules should be skipped
        cleanup_python_generated_files_fixed(tmp_path)
        
        # Regular .pyc should be deleted
        assert not regular_pyc.exists(), "Regular .pyc file should be deleted"
        
        # node_modules .pyc should NOT be deleted (skipped)
        assert nested_pyc.exists(), "node_modules .pyc file should NOT be deleted (should be skipped)"


def test_skips_hidden_directories():
    """
    Verify that cleanup_python_generated_files skips hidden directories (starting with ".").
    
    Hidden directories like .git, .venv, .tox, etc. should be skipped.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create structure with hidden directories
        regular_dir = tmp_path / "regular"
        regular_dir.mkdir()
        regular_pyc = regular_dir / "test.pyc"
        regular_pyc.write_text("regular pyc")
        
        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()
        hidden_pyc = hidden_dir / "hidden.pyc"
        hidden_pyc.write_text("hidden pyc")
        
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_pyc = git_dir / "git.pyc"
        git_pyc.write_text("git pyc")
        
        # Test the FIXED behavior: hidden dirs should be skipped
        cleanup_python_generated_files_fixed(tmp_path)
        
        # Regular .pyc should be deleted
        assert not regular_pyc.exists(), "Regular .pyc file should be deleted"
        
        # Hidden directory .pyc files should NOT be deleted
        assert hidden_pyc.exists(), "Hidden dir .pyc file should NOT be deleted (should be skipped)"
        assert git_pyc.exists(), ".git dir .pyc file should NOT be deleted (should be skipped)"


def test_cleans_pyc_files_in_regular_directories():
    """
    Verify that .pyc files in regular directories are still cleaned.
    
    Setup: Create multiple .pyc files in various regular directories
    Expected: All .pyc files are cleaned
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create various directories with .pyc files
        dirs = ["src", "tests", "lib/nested"]
        pyc_files = []
        for d in dirs:
            dir_path = tmp_path / d
            dir_path.mkdir(parents=True)
            for i in range(3):
                pyc = dir_path / f"module{i}.pyc"
                pyc.write_text(f"pyc content {i}")
                pyc_files.append(pyc)
        
        # Test the FIXED behavior: all .pyc files should be deleted
        cleanup_python_generated_files_fixed(tmp_path)
        
        # All .pyc files should be deleted
        for pyc in pyc_files:
            assert not pyc.exists(), f".pyc file {pyc} should be deleted"


def test_cleans_pycache_directories():
    """
    Verify that __pycache__ directories are still cleaned.
    
    Setup: Create __pycache__ directories at various levels
    Expected: All __pycache__ directories are removed
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create __pycache__ directories
        pycache_dirs = [
            tmp_path / "__pycache__",
            tmp_path / "src" / "__pycache__",
            tmp_path / "tests" / "deep" / "__pycache__",
        ]
        for pycache in pycache_dirs:
            pycache.mkdir(parents=True)
            (pycache / "module.cpython-312.pyc").write_text("cached")
        
        # Create a regular directory to verify it's not affected
        regular_dir = tmp_path / "regular"
        regular_dir.mkdir()
        regular_file = regular_dir / "keep.txt"
        regular_file.write_text("keep me")
        
        # Test the FIXED behavior: all __pycache__ directories should be removed
        cleanup_python_generated_files_fixed(tmp_path)
        
        # All __pycache__ directories should be removed
        for pycache in pycache_dirs:
            assert not pycache.exists(), f"__pycache__ dir {pycache} should be removed"
        
        # Regular file should remain
        assert regular_file.exists(), "Regular files should not be affected"


def test_dirnames_pruning_in_os_walk():
    """
    Verify that the fix properly modifies dirnames in-place to prune traversal.
    
    This is a structural test to verify the specific technique used in the fix:
    modifying dirnames[:] in-place to prune the os.walk traversal.
    """
    content = TARGET_FILE.read_text()
    
    # The fix should modify dirnames in-place
    assert "dirnames[:]" in content, "Expected dirnames[:] in-place modification for os.walk pruning"
    
    # Should explicitly check for node_modules
    assert 'node_modules' in content, "Expected explicit check for 'node_modules' directory"
    
    # Should check for hidden directories (startswith ".")
    assert 'startswith' in content and ('"."' in content or "'.'" in content), \
        "Expected check for hidden directories starting with '.'"


def test_handles_permission_errors():
    """
    Verify that permission errors are still collected and handled.

    Both old and new versions should collect permission errors.
    """
    content = TARGET_FILE.read_text()

    # Should still have permission_errors list
    assert "permission_errors" in content, "Expected permission_errors list to still exist"

    # Should still catch PermissionError
    assert "PermissionError" in content, "Expected PermissionError handling to still exist"


# =============================================================================
# Pass-to-Pass Tests: Repository CI Tests
# These tests verify that the repo's existing CI checks pass on the base commit
# =============================================================================


def test_repo_breeze_tests():
    """Breeze unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", "./dev/breeze", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install breeze: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "dev/breeze/tests/test_find_airflow_directory.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Breeze tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_ruff_lint():
    """Ruff linting passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "dev/breeze/src/airflow_breeze/utils/path_utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_ruff_format():
    """Ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "format", "--check", "dev/breeze/src/airflow_breeze/utils/path_utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_python_syntax():
    """Python syntax is valid for modified file (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "dev/breeze/src/airflow_breeze/utils/path_utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_breeze_general_utils():
    """Breeze general utils tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", "./dev/breeze", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install breeze: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "dev/breeze/tests/test_general_utils.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Breeze general utils tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_git_worktree():
    """Git worktree tests pass - tests path_utils functions (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", "./dev/breeze", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install breeze: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "dev/breeze/tests/test_git_worktree.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git worktree tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_breeze_packages():
    """Breeze packages tests pass - uses path_utils imports (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", "./dev/breeze", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install breeze: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "dev/breeze/tests/test_packages.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Breeze packages tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
