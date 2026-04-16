"""
Tests for airflow-skip-node-modules-cleanup task.

These tests verify the actual behavior of cleanup_python_generated_files:
- Skips node_modules directories during traversal
- Skips hidden directories (starting with .)
- Removes .pyc files
- Removes __pycache__ directories
- Handles FileNotFoundError and PermissionError gracefully
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Path to the airflow repo
REPO = Path("/workspace/airflow")
TARGET_FILE = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "utils" / "path_utils.py"


def test_syntax_valid():
    """Target file has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in {TARGET_FILE}:\n{result.stderr}"


def cleanup_in_temp_dir(temp_dir: Path):
    """
    Run the cleanup_python_generated_files function against temp_dir.

    This extracts the function source from the target file and executes it
    with mocked dependencies to avoid side effects from module imports.

    Returns a dict with:
    - remaining_files: list of file paths that still exist
    - remaining_dirs: list of directory paths that still exist
    """
    temp_dir = Path(temp_dir)

    # Read the actual source code from the target file
    full_source = TARGET_FILE.read_text()

    # Extract just the cleanup_python_generated_files function
    func_start = full_source.find("def cleanup_python_generated_files()")
    if func_start == -1:
        raise AssertionError("Could not find cleanup_python_generated_files function")

    # Find the end of the function (next function at same indentation level or end of file)
    next_func = full_source.find("\ndef ", func_start + 1)
    if next_func == -1:
        func_source = full_source[func_start:]
    else:
        func_source = full_source[func_start:next_func]

    # Build a standalone test script with mocked dependencies
    test_script = f'''
import os
import shutil
import platform
from pathlib import Path

# Mock all the dependencies that would cause side effects
def console_print(msg):
    pass

def get_verbose():
    return False

# Set up temp directory as the root
AIRFLOW_ROOT_PATH = Path("{temp_dir}")

# Execute the extracted cleanup function
{func_source}

# Run it
cleanup_python_generated_files()
'''

    # Run the test script
    proc = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        cwd=str(temp_dir),
    )

    if proc.returncode != 0:
        raise AssertionError(f"Cleanup script failed: {proc.stderr}")

    # Collect what remains
    remaining_files = []
    remaining_dirs = []
    for root, dirs, files in os.walk(temp_dir):
        for d in dirs:
            remaining_dirs.append(Path(root) / d)
        for f in files:
            remaining_files.append(Path(root) / f)

    return {
        "remaining_files": remaining_files,
        "remaining_dirs": remaining_dirs,
    }


def test_skips_node_modules_directory():
    """Cleanup skips node_modules directories during traversal (fail_to_pass).

    Creates a directory structure with node_modules containing .pyc files,
    verifies that node_modules is NOT traversed and .pyc files inside remain.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create regular .pyc file
        (tmp / "regular.pyc").write_text("test")

        # Create node_modules directory with .pyc file inside
        node_modules = tmp / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.pyc").write_text("test")

        # Create nested node_modules
        nested = tmp / "src" / "node_modules"
        nested.parent.mkdir()
        nested.mkdir()
        (nested / "nested.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # Regular .pyc should be deleted (not in remaining)
        regular_pyc = tmp / "regular.pyc"
        assert regular_pyc not in result["remaining_files"], \
            f"Should delete .pyc files in regular directories, but {regular_pyc} remains"

        # node_modules .pyc files should remain (not deleted because dir was skipped)
        package_pyc = node_modules / "package.pyc"
        assert package_pyc in result["remaining_files"], \
            f"Should NOT delete .pyc files inside node_modules - directory should be skipped, but {package_pyc} is gone"

        # Nested node_modules .pyc should also remain
        nested_pyc = nested / "nested.pyc"
        assert nested_pyc in result["remaining_files"], \
            f"Should NOT delete .pyc files inside nested node_modules, but {nested_pyc} is gone"


def test_skips_hidden_directories():
    """Cleanup skips hidden directories starting with dot (fail_to_pass).

    Creates a directory structure with hidden directories (.git, .venv) containing .pyc files,
    verifies that hidden directories are NOT traversed and .pyc files inside remain.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create regular .pyc file
        (tmp / "regular.pyc").write_text("test")

        # Create hidden directories with .pyc files
        git_dir = tmp / ".git"
        git_dir.mkdir()
        (git_dir / "index.pyc").write_text("test")

        venv_dir = tmp / ".venv"
        venv_dir.mkdir()
        (venv_dir / "pip.pyc").write_text("test")

        # Create nested hidden directory
        nested_hidden = tmp / "src" / ".tox"
        nested_hidden.parent.mkdir()
        nested_hidden.mkdir()
        (nested_hidden / "tox.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # Regular .pyc should be deleted
        regular_pyc = tmp / "regular.pyc"
        assert regular_pyc not in result["remaining_files"], \
            f"Should delete .pyc files in regular directories, but {regular_pyc} remains"

        # Hidden directory .pyc files should remain
        git_pyc = git_dir / "index.pyc"
        assert git_pyc in result["remaining_files"], \
            f"Should NOT delete .pyc files inside .git - hidden directory should be skipped, but {git_pyc} is gone"

        venv_pyc = venv_dir / "pip.pyc"
        assert venv_pyc in result["remaining_files"], \
            f"Should NOT delete .pyc files inside .venv - hidden directory should be skipped, but {venv_pyc} is gone"

        # Nested hidden directory .pyc should remain
        tox_pyc = nested_hidden / "tox.pyc"
        assert tox_pyc in result["remaining_files"], \
            f"Should NOT delete .pyc files inside nested hidden dirs, but {tox_pyc} is gone"


def test_removes_pyc_files():
    """Cleanup removes .pyc files from regular directories (fail_to_pass).

    Verifies that .pyc files are actually deleted, not just that node_modules is skipped.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create multiple .pyc files in various regular directories
        (tmp / "root.pyc").write_text("test")

        subdir = tmp / "subdir"
        subdir.mkdir()
        (subdir / "module.pyc").write_text("test")

        nested = tmp / "a" / "b" / "c"
        nested.mkdir(parents=True)
        (nested / "deep.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # All .pyc files should be gone
        assert len(result["remaining_files"]) == 0, \
            f"All .pyc files should be deleted, but remaining: {result['remaining_files']}"


def test_removes_pycache_directories():
    """Cleanup removes __pycache__ directories (fail_to_pass).

    Creates __pycache__ directories and verifies they are removed.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create __pycache__ directories
        pycache1 = tmp / "__pycache__"
        pycache1.mkdir()
        (pycache1 / "module.cpython-312.pyc").write_text("test")

        nested = tmp / "subdir" / "__pycache__"
        nested.parent.mkdir()
        nested.mkdir()
        (nested / "nested.cpython-312.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # __pycache__ directories should be gone
        pycache_paths = [p for p in result["remaining_dirs"] if "__pycache__" in str(p)]
        assert len(pycache_paths) == 0, \
            f"All __pycache__ directories should be removed, but remaining: {pycache_paths}"


def test_preserves_other_directories():
    """Cleanup preserves regular directories that are not __pycache__ (pass_to_pass).

    Verifies that we don't accidentally delete directories we shouldn't.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create regular directories with non-pyc files
        src_dir = tmp / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("test")

        data_dir = tmp / "data"
        data_dir.mkdir()
        (data_dir / "config.json").write_text("{}")

        result = cleanup_in_temp_dir(tmp)

        # Regular directories should remain
        assert src_dir in result["remaining_dirs"], \
            f"Regular src directory should be preserved, but it's gone"
        assert data_dir in result["remaining_dirs"], \
            f"Regular data directory should be preserved, but it's gone"


def test_preserves_regular_files():
    """Cleanup preserves regular files that are not .pyc (pass_to_pass).

    Verifies that we don't accidentally delete files we shouldn't.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create regular files alongside .pyc files
        (tmp / "script.py").write_text("test")
        (tmp / "README.md").write_text("# Test")
        (tmp / "regular.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # Regular files should remain
        script_py = tmp / "script.py"
        readme_md = tmp / "README.md"
        assert script_py in result["remaining_files"], \
            f"Regular .py files should be preserved, but {script_py} is gone"
        assert readme_md in result["remaining_files"], \
            f"Regular .md files should be preserved, but {readme_md} is gone"

        # .pyc file should be gone
        regular_pyc = tmp / "regular.pyc"
        assert regular_pyc not in result["remaining_files"], \
            f".pyc files should be deleted, but {regular_pyc} remains"


def test_handles_permission_error_gracefully():
    """Cleanup handles PermissionError gracefully (fail_to_pass).

    Creates a read-only .pyc file and verifies the function completes without crashing.
    The file may or may not be deleted depending on permissions, but the function
    should not raise an exception.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create a .pyc file
        pyc_file = tmp / "protected.pyc"
        pyc_file.write_text("test")

        # Make it read-only
        os.chmod(str(pyc_file), 0o444)

        try:
            # Should not raise an exception
            result = cleanup_in_temp_dir(tmp)

            # Function completed without error - that's the main assertion
            assert True, "Function completed without raising PermissionError"
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(str(pyc_file), 0o644)
            except:
                pass


def test_handles_concurrent_deletion():
    """Cleanup handles FileNotFoundError from concurrent deletion (fail_to_pass).

    Verifies that the function handles the race condition where a file is deleted
    by another process between listing and deletion.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create .pyc files
        (tmp / "a.pyc").write_text("test")
        (tmp / "b.pyc").write_text("test")

        # The function should complete without error even if files disappear
        # We can't easily simulate concurrent deletion, but we can verify
        # the function handles already-deleted files gracefully by running twice
        result1 = cleanup_in_temp_dir(tmp)

        # Second run - all .pyc files already gone
        # Should complete without FileNotFoundError
        result2 = cleanup_in_temp_dir(tmp)

        # Both runs should complete without error
        assert len(result1["remaining_files"]) == 0
        assert len(result2["remaining_files"]) == 0


def test_skips_node_modules_with_pycache_inside():
    """Cleanup skips node_modules even if it contains __pycache__ (fail_to_pass).

    The node_modules directory should be completely skipped, even if someone
    accidentally created a __pycache__ inside it.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create node_modules with __pycache__ inside (edge case)
        node_modules = tmp / "node_modules"
        node_modules.mkdir()
        bad_pycache = node_modules / "__pycache__"
        bad_pycache.mkdir()
        (bad_pycache / "bad.cpython-312.pyc").write_text("test")

        result = cleanup_in_temp_dir(tmp)

        # The __pycache__ inside node_modules should remain (dir was skipped)
        assert bad_pycache in result["remaining_dirs"], \
            f"__pycache__ inside node_modules should not be touched, but {bad_pycache} is gone"


def test_ruff_lint():
    """Target file passes ruff linting (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "check", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_format():
    """Target file passes ruff formatting check (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "format", "--check", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_breeze_utils_lint():
    """Breeze utils directory passes ruff linting (pass_to_pass)."""
    utils_dir = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "utils"
    result = subprocess.run(
        ["ruff", "check", str(utils_dir)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff linting failed on utils directory:\n{result.stdout}\n{result.stderr}"


def test_python_ast_parse():
    """Target file can be parsed by Python AST (pass_to_pass)."""
    import ast
    content = TARGET_FILE.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(f"AST parse failed: {e}")
