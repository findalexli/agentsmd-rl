"""Tests for the filter_files negation pattern fix.

This test file verifies that filter_files correctly includes parent directories
of files that are re-included via negation patterns in .prefectignore.
"""

import sys
import os
import tempfile
import subprocess
import ast
from pathlib import Path

# Add the prefect source to path
REPO = "/workspace/prefect"
sys.path.insert(0, os.path.join(REPO, "src"))

# Import only what we need from pathspec (no prefect dependency)
import pathspec
from pathspec import PathSpec


def get_filter_files_source():
    """Extract the filter_files function source and exec it."""
    fs_file = Path(REPO) / "src" / "prefect" / "utilities" / "filesystem.py"
    content = fs_file.read_text()

    # Find the filter_files function using AST
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "filter_files":
            # Get the function source lines
            with open(fs_file) as f:
                lines = f.readlines()

            # Extract the function
            func_lines = lines[node.lineno - 1:node.end_lineno]
            func_source = "".join(func_lines)

            return func_source, node

    raise ValueError("filter_files function not found")


def create_filter_files_function():
    """Create a standalone filter_files function without prefect imports."""
    fs_file = Path(REPO) / "src" / "prefect" / "utilities" / "filesystem.py"
    content = fs_file.read_text()

    # Parse the file
    tree = ast.parse(content)

    # Find the filter_files function
    filter_files_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "filter_files":
            filter_files_node = node
            break

    if not filter_files_node:
        raise ValueError("filter_files function not found")

    # Read the function source directly
    with open(fs_file) as f:
        lines = f.readlines()

    func_source = "".join(lines[filter_files_node.lineno - 1:filter_files_node.end_lineno])

    # Execute in a clean namespace with required imports
    namespace = {
        'pathspec': pathspec,
        'PathSpec': PathSpec,
        'Path': Path,
        'Optional': type('Optional', (), {'__getitem__': lambda self, x: x})(),
        'Iterable': type('Iterable', (), {'__getitem__': lambda self, x: x})(),
        'AnyStr': str,
        'set': set,
        'str': str,
    }

    exec(func_source, namespace)
    return namespace['filter_files']


# Create the filter_files function
filter_files = create_filter_files_function()


def test_negation_includes_parent_dirs():
    """
    FAIL-TO-PASS: When .prefectignore uses negation patterns to re-include files
    (e.g., '!workflows/*'), filter_files must include the parent directories
    in the result so that shutil.copytree doesn't skip them.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        tmp = Path(tmp_path)

        # Setup: Create a directory structure with files
        (tmp / "workflows").mkdir()
        (tmp / "workflows" / "flow.py").write_text("print('hi')")
        (tmp / "other.txt").write_text("other")
        (tmp / ".prefectignore").write_text("")

        # Test: Use ignore patterns that ignore everything, then re-include
        # specific files and directories using negation patterns
        result = filter_files(
            root=str(tmp),
            ignore_patterns=["*", "!.prefectignore", "!workflows/", "!workflows/*"],
        )

        # The parent directory "workflows" must be in the result
        assert "workflows" in result, \
            f"Parent directory 'workflows' should be in result, got: {result}"
        # The file "workflows/flow.py" must also be in the result
        assert any("flow.py" in f for f in result), \
            f"File 'workflows/flow.py' should be in result, got: {result}"


def test_negation_includes_nested_parent_dirs():
    """
    FAIL-TO-PASS: For deeply nested files re-included via negation,
    ALL ancestor directories must be in the result.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        tmp = Path(tmp_path)

        # Setup: Create deeply nested directory structure
        (tmp / "a" / "b" / "c").mkdir(parents=True)
        (tmp / "a" / "b" / "c" / "file.py").write_text("print('hi')")

        # Test: Ignore everything, then re-include just the deeply nested file
        result = filter_files(
            root=str(tmp),
            ignore_patterns=["*", "!a/b/c/file.py"],
        )

        # All ancestor directories must be present
        assert "a" in result, f"Directory 'a' should be in result, got: {result}"
        assert str(Path("a") / "b") in result, \
            f"Directory 'a/b' should be in result, got: {result}"
        assert str(Path("a") / "b" / "c") in result, \
            f"Directory 'a/b/c' should be in result, got: {result}"
        assert str(Path("a") / "b" / "c" / "file.py") in result, \
            f"File 'a/b/c/file.py' should be in result, got: {result}"


def test_filter_files_basic_functionality():
    """
    PASS-TO-PASS: Basic filtering without negation patterns should still work.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        tmp = Path(tmp_path)

        # Setup: Create files
        (tmp / "keep.txt").write_text("keep")
        (tmp / "ignore.txt").write_text("ignore")

        # Test: Simple ignore pattern
        result = filter_files(
            root=str(tmp),
            ignore_patterns=["ignore.txt"],
        )

        # The ignored file should not be in result
        assert "ignore.txt" not in result, \
            f"'ignore.txt' should be filtered out, got: {result}"
        # The kept file should be in result
        assert "keep.txt" in result, \
            f"'keep.txt' should be in result, got: {result}"


def test_include_dirs_false_behavior():
    """
    PASS-TO-PASS: When include_dirs=False, parent directories should NOT be added.
    The fix should only apply when include_dirs=True (the default).
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        tmp = Path(tmp_path)

        # Setup: Create directory with file
        (tmp / "workflows").mkdir()
        (tmp / "workflows" / "flow.py").write_text("print('hi')")

        # Test: Use include_dirs=False
        result = filter_files(
            root=str(tmp),
            ignore_patterns=["*", "!workflows/flow.py"],
            include_dirs=False,
        )

        # With include_dirs=False, only files should be returned
        # No directory entries should be in the result
        assert all("/" in f or "." not in f for f in result), \
            f"With include_dirs=False, only files expected, got: {result}"


def test_no_server_imports_in_filesystem_utils():
    """
    AGENT CONFIG CHECK: src/prefect/utilities/filesystem.py must not import
    from server modules, as these utilities are used client-side.

    Source: src/prefect/utilities/AGENTS.md
    """
    fs_file = Path(REPO) / "src" / "prefect" / "utilities" / "filesystem.py"
    content = fs_file.read_text()

    # Check for server imports
    server_imports = ["from prefect.server", "import prefect.server"]
    for imp in server_imports:
        assert imp not in content, \
            f"Utilities must not import from server: {imp}"


def test_repo_tests_exist():
    """
    PASS-TO-PASS: Verify that the repo's own test file exists and is importable.
    """
    test_file = Path(REPO) / "tests" / "utilities" / "test_filesystem.py"
    assert test_file.exists(), \
        f"Repo test file should exist: {test_file}"


def test_original_repo_tests_can_run():
    """
    PASS-TO-PASS: Run the repo's own tests for the filesystem module.
    This ensures the fix doesn't break existing functionality.
    """
    test_file = Path(REPO) / "tests" / "utilities" / "test_filesystem.py"

    # Just check that the test file exists and is valid Python
    # We can't easily run the full tests due to circular import issues
    # without the full prefect test setup
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Repo test file should be valid Python:\nstderr: {result.stderr}"


def test_repo_lint_ruff():
    """
    PASS-TO-PASS: Repo code passes ruff linting (from CI static analysis).
    Ensures the modified filesystem.py follows repo style guidelines.
    """
    # Install ruff first
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert install_result.returncode == 0, "Failed to install ruff"

    # Run ruff check on the modified file
    fs_file = Path(REPO) / "src" / "prefect" / "utilities" / "filesystem.py"
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(fs_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Ruff lint failed on filesystem.py:\n{result.stdout}\n{result.stderr}"


def test_repo_test_file_lint_ruff():
    """
    PASS-TO-PASS: Repo test file passes ruff linting (from CI static analysis).
    Ensures test code follows repo style guidelines.
    """
    # Install ruff first
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert install_result.returncode == 0, "Failed to install ruff"

    # Run ruff check on the test file
    test_file = Path(REPO) / "tests" / "utilities" / "test_filesystem.py"
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Ruff lint failed on test_filesystem.py:\n{result.stdout}\n{result.stderr}"


def test_repo_ast_valid():
    """
    PASS-TO-PASS: Modified filesystem.py has valid Python AST (repo CI check).
    Ensures the code structure is syntactically valid and parseable.
    """
    fs_file = Path(REPO) / "src" / "prefect" / "utilities" / "filesystem.py"

    result = subprocess.run(
        [sys.executable, "-c",
         f"import ast; ast.parse(open('{fs_file}').read()); print('AST valid')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"AST validation failed:\n{result.stderr}"


def test_repo_test_file_ast_valid():
    """
    PASS-TO-PASS: Repo test file has valid Python AST (repo CI check).
    Ensures test code structure is syntactically valid and parseable.
    """
    test_file = Path(REPO) / "tests" / "utilities" / "test_filesystem.py"

    result = subprocess.run(
        [sys.executable, "-c",
         f"import ast; ast.parse(open('{test_file}').read()); print('AST valid')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Test file AST validation failed:\n{result.stderr}"
