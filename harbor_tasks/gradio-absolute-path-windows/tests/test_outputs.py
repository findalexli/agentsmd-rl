"""
Task: gradio-absolute-path-windows
Repo: gradio-app/gradio @ e29e1ccd5874cb98b813ed4f7f72d9fef2935016
PR:   12926

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
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
# and leaves `safe_join` in scope for the caller to use.
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — paths starting with / must be rejected
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
# Pass-to-pass — regression
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
            f"safe_join({directory!r}, {rel_path!r}) = {result!r} — missing filename"
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
