#!/usr/bin/env python3
"""
Tests for apache/airflow#64930: Speed up cleanup_python_generated_files by skipping irrelevant dirs.

The fix replaces two rglob calls with a single os.walk that prunes node_modules
and hidden directories (.*) in-place, avoiding unnecessary traversal.
"""

import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
PATH_UTILS_FILE = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "utils" / "path_utils.py"


def extract_cleanup_function(root_path: Path) -> str:
    """
    Extract the cleanup_python_generated_files function from path_utils.py
    and create an executable version that operates on the given root_path.
    """
    source = PATH_UTILS_FILE.read_text()

    # Find the function definition
    match = re.search(
        r'^def cleanup_python_generated_files\(\):(.*?)(?=\n(?:def |class |if __name__)|\Z)',
        source,
        re.MULTILINE | re.DOTALL
    )

    if not match:
        raise ValueError("Could not find cleanup_python_generated_files function")

    func_body = match.group(1)

    # Replace AIRFLOW_ROOT_PATH with Path(str_path)
    func_body = func_body.replace('AIRFLOW_ROOT_PATH', f'Path("{root_path}")')

    # Also replace any console_print and get_verbose calls with no-ops
    func_body = re.sub(r'if get_verbose\(\):', 'if False:', func_body)
    func_body = re.sub(r'console_print\([^)]+\)', 'pass', func_body)

    return f'''
import os
import platform
import shutil
from pathlib import Path

def cleanup_python_generated_files():
{func_body}

cleanup_python_generated_files()
'''


def run_cleanup(root_path: Path) -> tuple[int, str, str]:
    """Run the cleanup function on the given root path."""
    import subprocess

    cleanup_code = extract_cleanup_function(root_path)
    result = subprocess.run(
        [sys.executable, "-c", cleanup_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    return result.returncode, result.stdout, result.stderr


class TestCleanupSkipsHiddenDirectories:
    """Test that cleanup_python_generated_files skips hidden directories."""

    def test_hidden_dir_pyc_not_deleted(self, tmp_path: Path):
        """
        F2P: .pyc files inside hidden directories (starting with .) should NOT be deleted.

        The fix uses os.walk with in-place pruning to skip hidden directories entirely.
        The old rglob implementation would traverse and clean these files.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        hidden_dir = test_root / ".hidden_cache"
        hidden_dir.mkdir()
        pyc_file = hidden_dir / "module.pyc"
        pyc_file.write_text("fake pyc content")

        # Also create a regular pyc to verify cleanup still works
        regular_dir = test_root / "regular"
        regular_dir.mkdir()
        regular_pyc = regular_dir / "test.pyc"
        regular_pyc.write_text("regular pyc")

        returncode, stdout, stderr = run_cleanup(test_root)

        # After fix: hidden dir pyc should still exist (was skipped)
        assert pyc_file.exists(), (
            f"Hidden directory .pyc file was incorrectly deleted. "
            f"The fix should skip directories starting with '.'. "
            f"stderr: {stderr}"
        )

        # Regular pyc should be deleted (cleanup still works)
        assert not regular_pyc.exists(), (
            f"Regular .pyc file was NOT deleted. Cleanup may have failed. stderr: {stderr}"
        )

    def test_git_dir_pyc_not_deleted(self, tmp_path: Path):
        """
        F2P: .pyc files inside .git directory should NOT be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        git_dir = test_root / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        pyc_file = git_dir / "pre-commit.pyc"
        pyc_file.write_text("fake pyc in git hooks")

        run_cleanup(test_root)

        assert pyc_file.exists(), (
            ".git directory .pyc file was incorrectly deleted. "
            "The fix should skip the .git directory entirely."
        )

    def test_venv_dir_pyc_not_deleted(self, tmp_path: Path):
        """
        F2P: .pyc files inside .venv directory should NOT be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        venv_dir = test_root / ".venv" / "lib" / "python3.12" / "site-packages"
        venv_dir.mkdir(parents=True)
        pyc_file = venv_dir / "requests.pyc"
        pyc_file.write_text("fake venv pyc")

        run_cleanup(test_root)

        assert pyc_file.exists(), (
            ".venv directory .pyc file was incorrectly deleted. "
            "The fix should skip directories starting with '.'."
        )


class TestCleanupSkipsNodeModules:
    """Test that cleanup_python_generated_files skips node_modules directories."""

    def test_node_modules_pyc_not_deleted(self, tmp_path: Path):
        """
        F2P: .pyc files inside node_modules should NOT be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        node_dir = test_root / "node_modules" / "some-package"
        node_dir.mkdir(parents=True)
        pyc_file = node_dir / "binding.pyc"
        pyc_file.write_text("fake pyc in node_modules")

        # Also regular pyc to verify cleanup works
        regular = test_root / "src" / "test.pyc"
        regular.parent.mkdir(parents=True)
        regular.write_text("regular pyc")

        run_cleanup(test_root)

        assert pyc_file.exists(), (
            "node_modules .pyc file was incorrectly deleted. "
            "The fix should skip node_modules directories."
        )
        assert not regular.exists(), "Regular .pyc should still be cleaned"

    def test_nested_node_modules_pyc_not_deleted(self, tmp_path: Path):
        """
        F2P: .pyc files inside nested node_modules should NOT be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        # ui/node_modules/pkg/test.pyc
        nested = test_root / "ui" / "node_modules" / "webpack" / "lib"
        nested.mkdir(parents=True)
        pyc_file = nested / "compiler.pyc"
        pyc_file.write_text("fake pyc in nested node_modules")

        run_cleanup(test_root)

        assert pyc_file.exists(), "Nested node_modules .pyc file was incorrectly deleted."


class TestCleanupStillWorks:
    """Test that cleanup still works for regular directories (pass-to-pass)."""

    def test_regular_pyc_deleted(self, tmp_path: Path):
        """
        P2P: .pyc files in regular directories should still be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        # Multiple regular .pyc files at various depths
        locations = [
            test_root / "module.pyc",
            test_root / "src" / "test.pyc",
            test_root / "airflow" / "models" / "dag.pyc",
        ]
        for loc in locations:
            loc.parent.mkdir(parents=True, exist_ok=True)
            loc.write_text("fake pyc")

        run_cleanup(test_root)

        for loc in locations:
            assert not loc.exists(), f"Regular .pyc file {loc} was not deleted"

    def test_pycache_dir_deleted(self, tmp_path: Path):
        """
        P2P: __pycache__ directories should still be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        pycache = test_root / "src" / "__pycache__"
        pycache.mkdir(parents=True)
        (pycache / "module.cpython-312.pyc").write_text("compiled")
        (pycache / "other.cpython-312.pyc").write_text("compiled")

        run_cleanup(test_root)

        assert not pycache.exists(), "__pycache__ directory was not deleted"

    def test_nested_pycache_deleted(self, tmp_path: Path):
        """
        P2P: Nested __pycache__ directories should be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        pycaches = [
            test_root / "__pycache__",
            test_root / "pkg" / "__pycache__",
            test_root / "pkg" / "sub" / "__pycache__",
        ]
        for pc in pycaches:
            pc.mkdir(parents=True, exist_ok=True)
            (pc / "mod.cpython-312.pyc").write_text("compiled")

        run_cleanup(test_root)

        for pc in pycaches:
            assert not pc.exists(), f"__pycache__ at {pc} was not deleted"


class TestPruningCombinations:
    """Test pruning behavior with various directory combinations."""

    def test_hidden_pycache_not_deleted(self, tmp_path: Path):
        """
        F2P: __pycache__ inside hidden directories should NOT be deleted.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        # __pycache__ inside .hidden should be skipped
        hidden_pycache = test_root / ".hidden" / "__pycache__"
        hidden_pycache.mkdir(parents=True)
        pyc = hidden_pycache / "mod.cpython-312.pyc"
        pyc.write_text("compiled in hidden")

        run_cleanup(test_root)

        # After fix, hidden __pycache__ should NOT be deleted
        assert hidden_pycache.exists(), (
            "__pycache__ inside hidden directory was incorrectly deleted"
        )

    def test_deep_hidden_not_traversed(self, tmp_path: Path):
        """
        F2P: Deep directories under hidden parent should NOT be traversed.
        """
        test_root = tmp_path / "airflow_test"
        test_root.mkdir()

        # .hidden/deep/nested/file.pyc should be completely skipped
        deep_path = test_root / ".hidden" / "deep" / "nested" / "very" / "deep"
        deep_path.mkdir(parents=True)
        pyc = deep_path / "file.pyc"
        pyc.write_text("very deep hidden pyc")

        run_cleanup(test_root)

        assert pyc.exists(), "Deep hidden .pyc was incorrectly deleted"


class TestRepoCIChecks:
    """Pass-to-pass tests that run actual repo CI commands on path_utils.py."""

    def test_repo_ruff_lint(self):
        """
        P2P: Ruff linting passes on the modified file (pass_to_pass).

        This runs the same ruff check that CI runs on the codebase.
        """
        import subprocess

        # Install ruff first (it's fast and cached after first install)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
            capture_output=True,
            timeout=120,
        )

        r = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(PATH_UTILS_FILE)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_ruff_format(self):
        """
        P2P: Ruff formatting check passes on the modified file (pass_to_pass).

        This runs the same ruff format check that CI runs on the codebase.
        """
        import subprocess

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
            capture_output=True,
            timeout=120,
        )

        r = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--check", str(PATH_UTILS_FILE)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_python_syntax(self):
        """
        P2P: Python syntax check passes on the modified file (pass_to_pass).

        Uses py_compile to verify the file has valid Python syntax.
        """
        import subprocess

        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(PATH_UTILS_FILE)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
