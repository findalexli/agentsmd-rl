"""
Task: gradio-absolute-path-windows
Repo: gradio-app/gradio @ e29e1ccd5874cb98b813ed4f7f72d9fef2935016
PR:   12926

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path
import os
import posixpath
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = "/workspace/gradio"
UTILS_PATH = Path(f"{REPO}/gradio/utils.py")

# Shared extraction snippet used by subprocess-based tests.
# Extracts safe_join via AST (avoids importing heavy gradio deps)
# and leaves "safe_join" in scope for the caller to use.
_EXTRACT_AND_TEST_PREFIX = """
import ast, os, posixpath
from unittest.mock import patch

class InvalidPathError(ValueError):
    pass

src = open("gradio/utils.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_src = ast.get_source_segment(src, node)
        break
else:
    raise RuntimeError("safe_join not found")

namespace = {
    "os": os,
    "posixpath": posixpath,
    "InvalidPathError": InvalidPathError,
    "DeveloperPath": str,
    "UserProvidedPath": str,
}
exec(compile(ast.parse(func_src), "<safe_join>", "exec"), namespace)
safe_join = namespace["safe_join"]
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# --- In-process helper for pass_to_pass regression tests ---

class InvalidPathError(ValueError):
    """Mirror of gradio.exceptions.InvalidPathError for extracted function."""
    pass


def _extract_safe_join():
    """Extract safe_join from gradio/utils.py and return a callable.

    AST-only extraction because: gradio.utils imports heavy deps (anyio, httpx,
    orjson, gradio_client, gradio itself) that aren't installed.
    The function itself is pure Python using only os and posixpath.
    """
    src = UTILS_PATH.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
            func_src = ast.get_source_segment(src, node)
            assert func_src, "Could not extract safe_join source"
            break
    else:
        pytest.fail("safe_join function not found in gradio/utils.py")

    namespace = {
        "os": os,
        "posixpath": posixpath,
        "InvalidPathError": InvalidPathError,
        "DeveloperPath": str,
        "UserProvidedPath": str,
    }
    exec(compile(ast.parse(func_src), "<safe_join>", "exec"), namespace)
    return namespace["safe_join"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/utils.py must parse without errors."""
    src = UTILS_PATH.read_text()
    ast.parse(src)


# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Ruff lint check passes on gradio/utils.py (repo CI)."""
    # Install ruff first
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check passes on gradio/utils.py (repo CI)."""
    # Install ruff first (if not already installed by test_repo_ruff)
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_utils_no_syntax_errors():
    """gradio/utils.py can be compiled and has no syntax errors (repo CI)."""
    # Compile the file to check for syntax errors
    r = subprocess.run(
        ["python", "-m", "py_compile", "gradio/utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in gradio/utils.py:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_safe_join_extractable():
    """safe_join function can be extracted and executed from utils.py (repo CI)."""
    # This tests that the function structure is intact and executable
    safe_join = _extract_safe_join()

    # Test that it works for normal relative paths
    result = safe_join("/tmp/uploads", "image.png")
    assert "image.png" in result

    # Test that it rejects traversal attempts
    with pytest.raises(InvalidPathError):
        safe_join("/tmp/uploads", "../etc/passwd")


# [repo_tests] pass_to_pass
def test_repo_is_in_or_equal():
    """is_in_or_equal related security function works correctly (repo CI).

    This function is used alongside safe_join in is_allowed_file and routes_safe_join.
    It validates path containment for security checks.
    """
    # Extract is_in_or_equal and abspath from utils.py using AST
    src = UTILS_PATH.read_text()
    tree = ast.parse(src)

    abspath_src = None
    is_in_or_equal_src = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "abspath":
                abspath_src = ast.get_source_segment(src, node)
            elif node.name == "is_in_or_equal":
                is_in_or_equal_src = ast.get_source_segment(src, node)

    assert is_in_or_equal_src, "is_in_or_equal function not found in gradio/utils.py"
    assert abspath_src, "abspath function not found in gradio/utils.py"

    # Execute both functions in a namespace with required imports
    namespace = {"os": os, "Path": Path}
    exec(compile(ast.parse(abspath_src), "<abspath>", "exec"), namespace)
    exec(compile(ast.parse(is_in_or_equal_src), "<is_in_or_equal>", "exec"), namespace)
    is_in_or_equal = namespace["is_in_or_equal"]

    # Test basic path containment
    assert is_in_or_equal("files/lion.jpg", "files") is True
    assert is_in_or_equal("/home/usr/notes.txt", "/home/usr/") is True

    # Test path traversal detection
    assert is_in_or_equal("/home/usr/../../etc/notes.txt", "/home/usr/") is False
    assert is_in_or_equal("/safe_dir/subdir/../../unsafe_file.txt", "/safe_dir/") is False

# [repo_tests] pass_to_pass
def test_repo_is_in_or_equal_full():
    """Run full test_is_in_or_equal test suite from repo CI (repo CI).

    This runs all assertions from the actual test file test/test_utils.py
    to ensure is_in_or_equal works correctly for all edge cases.
    """
    code = """
import ast
from pathlib import Path
import os
from pathlib import Path

# Read the utils source
utils_src = Path(\"gradio/utils.py\").read_text()
utils_tree = ast.parse(utils_src)

# Extract abspath
abspath_src = None
for node in ast.walk(utils_tree):
    if isinstance(node, ast.FunctionDef) and node.name == \"abspath\":
        abspath_src = ast.get_source_segment(utils_src, node)
        break

# Extract is_in_or_equal
is_in_or_equal_src = None
for node in ast.walk(utils_tree):
    if isinstance(node, ast.FunctionDef) and node.name == \"is_in_or_equal\":
        is_in_or_equal_src = ast.get_source_segment(utils_src, node)
        break

assert abspath_src and is_in_or_equal_src, \"Functions not found\"

# Create namespace and execute
namespace = {\"os\": os, \"Path\": Path}
exec(compile(ast.parse(abspath_src), \"<abspath>\", \"exec\"), namespace)
exec(compile(ast.parse(is_in_or_equal_src), \"<is_in_or_equal>\", \"exec\"), namespace)
is_in_or_equal = namespace[\"is_in_or_equal\"]

# Run the full test_is_in_or_equal test suite
assert is_in_or_equal(\"files/lion.jpg\", \"files/lion.jpg\")
assert is_in_or_equal(\"files/lion.jpg\", \"files\")
assert is_in_or_equal(\"files/lion.._M.jpg\", \"files\")
assert not is_in_or_equal(\"files\", \"files/lion.jpg\")
assert is_in_or_equal(\"/home/usr/notes.txt\", \"/home/usr/\")
assert not is_in_or_equal(\"/home/usr/subdirectory\", \"/home/usr/notes.txt\")
assert not is_in_or_equal(\"/home/usr/../../etc/notes.txt\", \"/home/usr/\")
assert not is_in_or_equal(\"/safe_dir/subdir/../../unsafe_file.txt\", \"/safe_dir/\")

print(\"test_repo_is_in_or_equal_full: PASSED\")
"""
    r = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"
    assert "PASSED" in r.stdout, f"Expected PASSED in output:\n{r.stdout}"



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - paths starting with / must be rejected
# Uses subprocess.run() to execute actual code
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_slash_path_rejected_simulated_win314():
    """Path /etc/passwd rejected even when os.path.isabs returns False (Py3.14 Windows sim)."""
    r = _run_py(_EXTRACT_AND_TEST_PREFIX + """
with patch("os.path.isabs", return_value=False):
    for malicious in ["/etc/passwd", "/root/.ssh/id_rsa", "/var/log/syslog"]:
        try:
            safe_join("/tmp/uploads", malicious)
        except InvalidPathError:
            pass
        else:
            raise AssertionError(f"safe_join allowed malicious path: {malicious!r}")
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_various_slash_paths_rejected_simulated_win314():
    """Multiple /-prefixed paths rejected under Py3.14 Windows simulation."""
    r = _run_py(_EXTRACT_AND_TEST_PREFIX + """
slash_paths = [
    "/home/user/.env",
    "/proc/self/environ",
    "/etc/shadow",
    "/opt/secrets/key.pem",
    "/usr/local/bin/exploit",
]
with patch("os.path.isabs", return_value=False):
    for path in slash_paths:
        try:
            safe_join("/data/files", path)
        except InvalidPathError:
            pass
        else:
            raise AssertionError(f"safe_join allowed: {path!r}")
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass - regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_relative_paths_allowed():
    """Normal relative paths must not be rejected by safe_join."""
    safe_join = _extract_safe_join()

    cases = [
        ("/tmp/uploads", "image.png"),
        ("/tmp/uploads", "subdir/file.txt"),
        ("/tmp/uploads", "a/b/c/d.txt"),
        ("/var/www", "static/style.css"),
        ("/data", "reports/2024/q1.csv"),
    ]
    for directory, rel_path in cases:
        result = safe_join(directory, rel_path)
        assert rel_path.split("/")[-1] in result, (
            f"safe_join({directory!r}, {rel_path!r}) = {result!r} - missing filename"
        )


# [pr_diff] pass_to_pass
def test_traversal_paths_still_rejected():
    """Existing traversal guards (.. and ../) still work."""
    safe_join = _extract_safe_join()

    for malicious in ["..", "../etc/passwd", "../../../root", "../secret.txt"]:
        with pytest.raises(InvalidPathError):
            safe_join("/tmp/uploads", malicious)


# [static] pass_to_pass
def test_not_stub():
    """safe_join has real logic with security checks."""
    src = UTILS_PATH.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
            body = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(body) >= 3, f"safe_join has only {len(body)} statements"
            raises = [n for n in ast.walk(node) if isinstance(n, ast.Raise)]
            assert raises, "safe_join has no raise statements"
            return
    pytest.fail("safe_join function not found")


# [repo_tests] pass_to_pass
def test_repo_abspath():
    """abspath function works correctly for path resolution (repo CI).

    Tests the abspath function which is used by safe_join for path normalization.
    Based on test_abspath_no_symlink from test/test_utils.py.
    """
    code = """
import ast
from pathlib import Path
import os
from pathlib import Path

# Read the utils source
utils_src = Path(\"gradio/utils.py\").read_text()
utils_tree = ast.parse(utils_src)

# Extract abspath
abspath_src = None
for node in ast.walk(utils_tree):
    if isinstance(node, ast.FunctionDef) and node.name == \"abspath\":
        abspath_src = ast.get_source_segment(utils_src, node)
        break

assert abspath_src, \"abspath function not found\"

# Create namespace and execute
namespace = {\"os\": os, \"Path\": Path}
exec(compile(ast.parse(abspath_src), \"<abspath>\", \"exec\"), namespace)
abspath = namespace[\"abspath\"]

# Test: resolved path should not contain .. components
resolved_path = str(abspath(\"../gradio/gradio/test_data/lion.jpg\"))
assert \"..\" not in resolved_path, f\"Resolved path still contains ..: {resolved_path}\"

print(\"test_repo_abspath: PASSED\")
"""
    r = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\\n{r.stderr[-500:]}"
    assert "PASSED" in r.stdout, f"Expected PASSED in output:\\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_safe_join_edge_cases():
    """safe_join handles various edge cases correctly (repo CI).

    Tests edge cases for safe_join including empty paths, dots, and special characters.
    """
    code = """
import ast
from pathlib import Path
import os
import posixpath
from unittest.mock import patch

class InvalidPathError(ValueError):
    pass

# Read the utils source
utils_src = Path(\"gradio/utils.py\").read_text()
utils_tree = ast.parse(utils_src)

# Extract safe_join
safe_join_src = None
for node in ast.walk(utils_tree):
    if isinstance(node, ast.FunctionDef) and node.name == \"safe_join\":
        safe_join_src = ast.get_source_segment(utils_src, node)
        break

assert safe_join_src, \"safe_join function not found\"

# Execute with proper namespace
namespace = {
    \"os\": os,
    \"posixpath\": posixpath,
    \"InvalidPathError\": InvalidPathError,
    \"DeveloperPath\": str,
    \"UserProvidedPath\": str,
}
exec(compile(ast.parse(safe_join_src), \"<safe_join>\", \"exec\"), namespace)
safe_join = namespace[\"safe_join\"]

# Test cases
# 1. Normal relative paths should work
result = safe_join(\"/tmp/uploads\", \"file.txt\")
assert \"file.txt\" in result, f\"Normal path failed: {result}\"

# 2. Subdirectory paths should work
result = safe_join(\"/tmp/uploads\", \"subdir/file.txt\")
assert \"subdir\" in result and \"file.txt\" in result, f\"Subdir path failed: {result}\"

# 3. Dot in filename should work (not a traversal)
result = safe_join(\"/tmp/uploads\", \"file.name.txt\")
assert \"file.name.txt\" in result, f\"Dot filename failed: {result}\"

# 4. Traversal with .. should be rejected
try:
    safe_join(\"/tmp/uploads\", \"../etc/passwd\")
    assert False, \"Traversal path should be rejected\"
except InvalidPathError:
    pass

# 5. Simple .. should be rejected
try:
    safe_join(\"/tmp/uploads\", \"..\")
    assert False, \"Simple .. should be rejected\"
except InvalidPathError:
    pass

print(\"test_repo_safe_join_edge_cases: PASSED\")
"""
    r = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\\n{r.stderr[-500:]}"
    assert "PASSED" in r.stdout, f"Expected PASSED in output:\\n{r.stdout}"
