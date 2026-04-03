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
def test_init_has_deprecation_notice():
    """__init__.py must have a comment pointing to cloudflare/workers-py."""
    init_file = Path(REPO) / "src/pyodide/internal/workers-api/src/workers/__init__.py"
    content = init_file.read_text()
    assert "workers-py" in content or "workers_py" in content, \
        "__init__.py must reference the new workers-py repository"
    # Must be a comment (not functional code change)
    lines = content.split("\n")
    has_comment = any(
        "workers-py" in line and line.strip().startswith("#")
        for line in lines
    )
    assert has_comment, "__init__.py deprecation notice should be a comment"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — AGENTS.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
