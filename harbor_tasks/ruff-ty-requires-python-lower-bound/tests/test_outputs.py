"""
Task: ruff-ty-requires-python-lower-bound
Repo: ruff @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
PR:   24401

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
PYPROJECT_RS = Path(REPO) / "crates/ty_project/src/metadata/pyproject.rs"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary."""
    global _ty_bin_cache
    if _ty_bin_cache is not None:
        return _ty_bin_cache

    for profile in ["debug", "release"]:
        p = Path(REPO) / "target" / profile / "ty"
        if p.exists():
            _ty_bin_cache = str(p)
            return _ty_bin_cache

    raise RuntimeError(
        "ty binary not found — it should be pre-built in the Docker image. "
        "Run 'cargo build --bin ty' in /workspace/ruff."
    )


def _run_ty_check(pyproject_content: str, python_code: str = "x: int = 1\n"):
    """Create a temp project and run ty check, returning CompletedProcess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pyproject_path = os.path.join(tmpdir, "pyproject.toml")
        with open(pyproject_path, "w") as f:
            f.write(pyproject_content)

        test_py = os.path.join(tmpdir, "test.py")
        with open(test_py, "w") as f:
            f.write(python_code)

        r = subprocess.run(
            [_ty_bin(), "check", test_py],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=tmpdir,
        )
        return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_ty_binary_exists():
    """ty binary was built successfully during Docker build."""
    ty = Path(_ty_bin())
    assert ty.exists(), f"ty binary not found at {ty}"
    assert os.access(ty, os.X_OK), f"ty binary not executable at {ty}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_requires_python_27_no_panic():
    """ty handles requires-python='==2.7' gracefully instead of panicking.

    Before the fix, ty would try to use PythonVersion(2, 7) directly,
    causing panics downstream. After the fix, it finds the first supported
    version >= 2.7 (i.e., 3.7).
    """
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==2.7"\n',
    )
    output = r.stdout + r.stderr
    # Rust panic exit code is 101; normal error exit codes are 1-2
    assert r.returncode != 101, f"ty panicked with exit 101:\n{output}"
    assert "panic" not in output.lower(), (
        f"ty panicked (panic message in output):\n{output}"
    )


# [pr_diff] fail_to_pass
def test_requires_python_future_version_error():
    """ty gives a clear error for requires-python with an unsupported future version.

    Before the fix, requires-python='==44.44' would cause a panic or
    unexpected behavior. After the fix, it returns a proper error message.
    """
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==44.44"\n',
    )
    output = r.stdout + r.stderr
    # Should fail (non-zero) but NOT panic
    assert r.returncode != 0, (
        f"ty should reject unsupported requires-python '==44.44':\n{output}"
    )
    assert "panic" not in output.lower(), (
        f"ty panicked instead of giving a clean error:\n{output}"
    )
    # Should mention that no supported version is included
    assert "supported" in output.lower() or "does not include" in output.lower(), (
        f"Expected error about unsupported version, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + valid cases
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_requires_python_normal_version():
    """ty works normally with a standard requires-python specifier."""
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = ">=3.10"\n',
        python_code="x: int = 1\nprint(x)\n",
    )
    output = r.stdout + r.stderr
    assert "panic" not in output.lower(), f"ty panicked:\n{output}"
    assert "Invalid" not in output or "requires-python" not in output, (
        f"ty reported requires-python error for valid specifier:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_requires_python_310_exact():
    """ty works with exact-version requires-python for a supported version."""
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==3.10"\n',
        python_code="from typing import TypeAlias\nMyInt: TypeAlias = int\n",
    )
    output = r.stdout + r.stderr
    assert "panic" not in output.lower(), f"ty panicked:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:79 @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
def test_no_unwrap_in_resolve_requires_python():
    """resolve_requires_python avoids .unwrap() and panic! per AGENTS.md guidelines.

    AGENTS.md says: 'Try hard to avoid patterns that require panic!,
    unreachable!, or .unwrap().'
    """
    source = PYPROJECT_RS.read_text()
    marker = "fn resolve_requires_python"
    start = source.find(marker)
    assert start != -1, f"Function resolve_requires_python not found in {PYPROJECT_RS}"

    # Find the function body by tracking brace depth
    rest = source[start:]
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    func_body = rest[:end]

    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert ".unwrap()" not in stripped, (
            f".unwrap() found in resolve_requires_python at line {i}: {stripped}"
        )
        assert "panic!(" not in stripped, (
            f"panic! found in resolve_requires_python at line {i}: {stripped}"
        )
        assert "unreachable!(" not in stripped, (
            f"unreachable! found in resolve_requires_python at line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
def test_no_local_imports_in_resolve():
    """No local use/import statements inside functions (AGENTS.md:76).

    AGENTS.md says: 'Rust imports should always go at the top of the file,
    never locally in functions.'
    """
    source = PYPROJECT_RS.read_text()
    marker = "fn resolve_requires_python"
    start = source.find(marker)
    assert start != -1, f"Function resolve_requires_python not found in {PYPROJECT_RS}"

    rest = source[start:]
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    func_body = rest[:end]

    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("use "), (
            f"Local import in resolve_requires_python at line {i}: {stripped}"
        )
