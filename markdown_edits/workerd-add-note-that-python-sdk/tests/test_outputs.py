"""
Task: workerd-add-note-that-python-sdk
Repo: cloudflare/workerd @ c91cf4910046c3f4eeffa713cc15a5129ac2ad19
PR:   #6329

The Python SDK (internal/workers-api/) has been moved to cloudflare/workers-py.
This PR freezes the in-tree copy: adds a hash-based freeze test, registers it
in BUILD.bazel, adds a deprecation comment to __init__.py, and updates
src/pyodide/AGENTS.md to document the frozen status.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """__init__.py must parse without errors (exists on base and after patch)."""
    init_file = Path(REPO) / "src/pyodide/internal/workers-api/src/workers/__init__.py"
    assert init_file.exists(), f"Expected file missing: {init_file}"
    source = init_file.read_text()
    ast.parse(source, filename=str(init_file))


# [repo_tests] pass_to_pass
def test_repo_introspection():
    """Repo's introspection unit test passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "src/pyodide/internal/test_introspection.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Introspection test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pyodide_syntax():
    """All pyodide Python files compile without syntax errors (pass_to_pass)."""
    pyodide_dir = Path(REPO) / "src/pyodide"
    py_files = [
        "create_vendor_zip.py",
        "make_snapshots.py",
        "tool_utils.py",
        "upload_bundles.py",
        "internal/introspection.py",
        "internal/test_introspection.py",
        "internal/workers-api/src/asgi.py",
        "internal/workers-api/src/workers/__init__.py",
        "internal/workers-api/src/workers/_workers.py",
        "internal/workers-api/src/workers/workflows.py",
    ]
    for rel_path in py_files:
        file_path = pyodide_dir / rel_path
        if file_path.exists():
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert r.returncode == 0, f"Syntax error in {rel_path}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_freeze_test_exists_with_hash_logic():
    """A freeze test must exist that uses cryptographic hashing to detect SDK modifications."""
    test_file = Path(REPO) / "src/pyodide/internal/test_frozen_sdk.py"
    assert test_file.exists(), "Freeze test file must exist at src/pyodide/internal/test_frozen_sdk.py"
    content = test_file.read_text()
    # Must use hash-based verification
    assert "hashlib" in content or "sha256" in content.lower() or "sha1" in content.lower(), \
        "Freeze test must use cryptographic hashing (hashlib/sha256)"
    # Must reference the SDK directory
    assert "workers-api" in content or "workers_api" in content, \
        "Freeze test must reference the workers-api SDK directory"


# [pr_diff] fail_to_pass
def test_freeze_test_passes():
    """The freeze test must run successfully — hashes must match actual SDK files."""
    test_file = Path(REPO) / "src/pyodide/internal/test_frozen_sdk.py"
    assert test_file.exists(), "Freeze test file must exist"
    r = subprocess.run(
        ["python3", str(test_file)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Freeze test failed (hashes may not match actual files):\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_freeze_test_covers_key_files():
    """Freeze test must cover at least pyproject.toml and __init__.py."""
    test_file = Path(REPO) / "src/pyodide/internal/test_frozen_sdk.py"
    assert test_file.exists(), "Freeze test file must exist"
    content = test_file.read_text()
    assert "pyproject.toml" in content, \
        "Freeze test must cover pyproject.toml"
    assert "__init__.py" in content, \
        "Freeze test must cover __init__.py"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — AGENTS.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
