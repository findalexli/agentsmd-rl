"""
Task: pytorch-wheel-tag-freethreaded-abi
Repo: pytorch/pytorch @ 8eaba043803b82549bf4fb42d5e03099be2eb1d9
PR:   #177993

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import io
import contextlib
import os
import re
import subprocess
import sys
import sysconfig
import tempfile
import unittest.mock as mock
import zipfile
from pathlib import Path

import pytest

SRC = "/workspace/.ci/pytorch/smoke_test/check_wheel_tags.py"


def _load_module():
    """exec the source file and return its namespace."""
    ns = {}
    exec(Path(SRC).read_text(), ns)
    return ns


def _make_wheel(tmpdir, python_tag, abi_tag, platform_tag):
    """Create a minimal .whl with the given tags."""
    name = f"torch-2.7.0-{python_tag}-{abi_tag}-{platform_tag}.whl"
    path = Path(tmpdir) / name
    tag_line = f"Tag: {python_tag}-{abi_tag}-{platform_tag}"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("torch-2.7.0.dist-info/WHEEL", tag_line)
    return path


def _cleanup_env(*keys):
    """Remove env vars, used in finally blocks."""
    for k in keys:
        os.environ.pop(k, None)


def _with_freethreaded(gil_enabled, env_version=None):
    """Context manager that simulates free-threaded Python detection state."""
    class _Ctx:
        def __enter__(self_):
            self_._orig = getattr(sys, "_is_gil_enabled", None)
            self_._patch = mock.patch.object(sys, "abiflags", "")
            self_._patch.start()
            sys._is_gil_enabled = lambda: gil_enabled
            if env_version:
                os.environ["MATRIX_PYTHON_VERSION"] = env_version
            return self_

        def __exit__(self_, *exc):
            self_._patch.stop()
            if self_._orig is not None:
                sys._is_gil_enabled = self_._orig
            elif hasattr(sys, "_is_gil_enabled"):
                del sys._is_gil_enabled
            if env_version:
                os.environ.pop("MATRIX_PYTHON_VERSION", None)
    return _Ctx()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Source file must parse without syntax errors."""
    source = Path(SRC).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_freethreaded_abi_subprocess():
    """Subprocess: MATRIX_PYTHON_VERSION=X.Yt triggers free-threaded ABI detection."""
    major, minor = sys.version_info.major, sys.version_info.minor
    python_tag = f"cp{major}{minor}"
    abi_tag = f"cp{major}{minor}t"

    with tempfile.TemporaryDirectory() as tmpdir:
        _make_wheel(tmpdir, python_tag, abi_tag, "linux_x86_64")

        script = (
            "import sys\n"
            "from pathlib import Path\n"
            "from unittest.mock import patch\n"
            "\n"
            "with patch.object(sys, 'abiflags', ''):\n"
            "    ns = {}\n"
            f"    exec(Path('{SRC}').read_text(), ns)\n"
            "    ns['check_wheel_platform_tag']()\n"
            "print('PASS')\n"
        )

        env = os.environ.copy()
        env["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
        env["TARGET_OS"] = "linux"
        env["MATRIX_PYTHON_VERSION"] = f"{major}.{minor}t"

        r = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=30,
            env=env, cwd="/workspace",
        )
        assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
        assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_freethreaded_abi_tag_accepted():
    """Free-threaded Python (no GIL) wheel with 't' ABI suffix must pass validation."""
    major, minor = sys.version_info.major, sys.version_info.minor

    with _with_freethreaded(gil_enabled=False):
        ns = _load_module()
        for platform in ("linux_x86_64", "manylinux1_x86_64"):
            with tempfile.TemporaryDirectory() as tmpdir:
                _make_wheel(tmpdir, f"cp{major}{minor}", f"cp{major}{minor}t", platform)
                os.environ["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
                os.environ["TARGET_OS"] = "linux"
                try:
                    ns["check_wheel_platform_tag"]()
                finally:
                    _cleanup_env("PYTORCH_FINAL_PACKAGE_DIR", "TARGET_OS")


# [pr_diff] fail_to_pass
def test_freethreaded_abi_via_env_var():
    """Free-threaded detection via MATRIX_PYTHON_VERSION ending in 't'."""
    major, minor = sys.version_info.major, sys.version_info.minor

    # _is_gil_enabled returns True (not free-threaded by runtime),
    # but MATRIX_PYTHON_VERSION says "X.Yt" → should still detect free-threaded
    with _with_freethreaded(gil_enabled=True, env_version=f"{major}.{minor}t"):
        ns = _load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            _make_wheel(tmpdir, f"cp{major}{minor}", f"cp{major}{minor}t", "linux_x86_64")
            os.environ["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
            os.environ["TARGET_OS"] = "linux"
            try:
                ns["check_wheel_platform_tag"]()
            finally:
                _cleanup_env("PYTORCH_FINAL_PACKAGE_DIR", "TARGET_OS")


# [pr_diff] fail_to_pass
def test_freethreaded_abi_via_sysconfig():
    """Free-threaded detection via sysconfig Py_GIL_DISABLED flag."""
    major, minor = sys.version_info.major, sys.version_info.minor

    # _is_gil_enabled returns True and no env var, but sysconfig says GIL disabled
    with _with_freethreaded(gil_enabled=True):
        with mock.patch("sysconfig.get_config_var", lambda key: 1 if key == "Py_GIL_DISABLED" else sysconfig.get_config_var(key)):
            ns = _load_module()
            with tempfile.TemporaryDirectory() as tmpdir:
                _make_wheel(tmpdir, f"cp{major}{minor}", f"cp{major}{minor}t", "linux_x86_64")
                os.environ["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
                os.environ["TARGET_OS"] = "linux"
                try:
                    ns["check_wheel_platform_tag"]()
                finally:
                    _cleanup_env("PYTORCH_FINAL_PACKAGE_DIR", "TARGET_OS")


# [pr_diff] fail_to_pass
def test_freethreaded_wrong_tag_rejected():
    """A wheel WITHOUT 't' suffix must FAIL under free-threaded Python."""
    major, minor = sys.version_info.major, sys.version_info.minor

    with _with_freethreaded(gil_enabled=False):
        ns = _load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Wheel missing 't' — wrong for free-threaded
            _make_wheel(tmpdir, f"cp{major}{minor}", f"cp{major}{minor}", "linux_x86_64")
            os.environ["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
            os.environ["TARGET_OS"] = "linux"
            try:
                with pytest.raises(RuntimeError, match="(?i)abi|tag|mismatch"):
                    ns["check_wheel_platform_tag"]()
            finally:
                _cleanup_env("PYTORCH_FINAL_PACKAGE_DIR", "TARGET_OS")


# [pr_diff] fail_to_pass
def test_mac_minos_mode2_attempted():
    """check_mac_wheel_minos attempts Mode 2 when PYTORCH_FINAL_PACKAGE_DIR is unset."""
    os.environ.pop("PYTORCH_FINAL_PACKAGE_DIR", None)

    ns = _load_module()
    fn = ns.get("check_mac_wheel_minos")
    assert fn is not None, "check_mac_wheel_minos function not found"

    # Patch sys.platform to darwin so the function doesn't early-return
    with mock.patch("sys.platform", "darwin"):
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f):
                fn()
            output = f.getvalue().lower()
            # Fixed code should NOT just print "skipping wheel minos check" — it should
            # attempt Mode 2 (reading from installed torch).
            # The base code prints "not set, skipping" and returns.
            assert "skipping wheel minos" not in output, (
                f"Function silently skips instead of attempting Mode 2: {output}"
            )
        except Exception as e:
            # Attempting Mode 2 but failing (torch not installed) is acceptable —
            # the key is that it TRIES rather than silently skipping
            err_msg = str(e).lower()
            # Should not be a "skipping" type message even in exceptions
            assert "not set, skipping" not in err_msg


# [pr_diff] fail_to_pass
def test_dead_code_removed():
    """No unreachable 'continue' after 'raise' in tag validation loop."""
    # AST-only because: structural check for dead code removal, not behavioral
    tree = ast.parse(Path(SRC).read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            body = node.body
            for i in range(len(body) - 1):
                if isinstance(body[i], ast.Raise) and isinstance(body[i + 1], ast.Continue):
                    assert False, "Unreachable 'continue' after 'raise' found in loop body"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_standard_wheel_validation():
    """Standard (non-free-threaded) wheels must still validate correctly."""
    major, minor = sys.version_info.major, sys.version_info.minor
    abiflags = getattr(sys, "abiflags", "")
    abi = f"cp{major}{minor}{abiflags}"

    ns = _load_module()
    # Test across multiple platform tags
    for platform, target_os in [
        ("linux_x86_64", "linux"),
        ("manylinux1_x86_64", "linux"),
    ]:
        with tempfile.TemporaryDirectory() as tmpdir:
            _make_wheel(tmpdir, f"cp{major}{minor}", abi, platform)
            os.environ["PYTORCH_FINAL_PACKAGE_DIR"] = tmpdir
            os.environ["TARGET_OS"] = target_os
            try:
                ns["check_wheel_platform_tag"]()
            finally:
                _cleanup_env("PYTORCH_FINAL_PACKAGE_DIR", "TARGET_OS")


# [pr_diff] pass_to_pass
def test_extract_wheel_tags():
    """_extract_wheel_tags correctly parses WHEEL metadata with varying tag counts."""
    ns = _load_module()

    # Case 1: single tag
    with tempfile.TemporaryDirectory() as tmpdir:
        whl_path = Path(tmpdir) / "single.whl"
        with zipfile.ZipFile(whl_path, "w") as zf:
            zf.writestr("pkg-1.0.dist-info/WHEEL", "Tag: cp312-cp312-linux_x86_64")
        tags = ns["_extract_wheel_tags"](whl_path)
        assert len(tags) == 1, f"Expected 1 tag, got {len(tags)}: {tags}"
        assert tags[0] == "cp312-cp312-linux_x86_64"

    # Case 2: two tags
    with tempfile.TemporaryDirectory() as tmpdir:
        whl_path = Path(tmpdir) / "multi.whl"
        with zipfile.ZipFile(whl_path, "w") as zf:
            zf.writestr(
                "pkg-1.0.dist-info/WHEEL",
                "Tag: cp312-cp312-linux_x86_64\nTag: cp312-cp312-manylinux1_x86_64",
            )
        tags = ns["_extract_wheel_tags"](whl_path)
        assert len(tags) == 2, f"Expected 2 tags, got {len(tags)}: {tags}"
        assert tags[0] == "cp312-cp312-linux_x86_64"
        assert tags[1] == "cp312-cp312-manylinux1_x86_64"

    # Case 3: three tags (including free-threaded)
    with tempfile.TemporaryDirectory() as tmpdir:
        whl_path = Path(tmpdir) / "three.whl"
        with zipfile.ZipFile(whl_path, "w") as zf:
            zf.writestr(
                "pkg-1.0.dist-info/WHEEL",
                "Tag: cp313t-cp313t-linux_x86_64\n"
                "Tag: cp313t-cp313t-manylinux1_x86_64\n"
                "Tag: cp313t-cp313t-manylinux2014_x86_64",
            )
        tags = ns["_extract_wheel_tags"](whl_path)
        assert len(tags) == 3, f"Expected 3 tags, got {len(tags)}: {tags}"
        assert all("cp313t" in t for t in tags)


# [pr_diff] pass_to_pass
def test_core_functions_importable():
    """All core public functions exist and are callable."""
    ns = _load_module()
    for name in ["check_wheel_platform_tag", "check_mac_wheel_minos", "_extract_wheel_tags"]:
        fn = ns.get(name)
        assert fn is not None, f"{name} not found"
        assert callable(fn), f"{name} is not callable"


# [static] pass_to_pass
def test_not_stub():
    """Core functions must have real implementations, not stubs."""
    # AST-only because: anti-stub structural check, not behavioral
    tree = ast.parse(Path(SRC).read_text())
    required = {"check_wheel_platform_tag", "check_mac_wheel_minos", "_extract_wheel_tags"}
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in required:
            stmts = node.body
            if stmts and isinstance(stmts[0], ast.Expr) and isinstance(
                stmts[0].value, (ast.Constant,)
            ):
                stmts = stmts[1:]
            real = [s for s in stmts if not isinstance(s, ast.Pass)]
            found[node.name] = len(real)

    missing = required - set(found.keys())
    assert not missing, f"Missing functions: {missing}"
    stubs = {k: v for k, v in found.items() if v < 3}
    assert not stubs, f"Stubbed functions (< 3 real statements): {stubs}"
# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_file_compiles():
    """Source file must compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", SRC],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"File failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_smoke_test_dir_compiles():
    """All Python files in smoke_test directory must compile (pass_to_pass)."""
    smoke_dir = Path("/workspace/.ci/pytorch/smoke_test")
    py_files = list(smoke_dir.glob("*.py"))
    assert py_files, "No Python files found in smoke_test directory"

    for py_file in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(py_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{py_file.name} failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_imports_are_standard_lib():
    """Source file must only use standard library imports (pass_to_pass)."""
    tree = ast.parse(Path(SRC).read_text())

    # Standard library modules that check_wheel_tags.py should use
    stdlib_modules = {
        "os", "platform", "re", "subprocess", "sys", "zipfile",
        "pathlib", "importlib", "importlib.metadata", "tempfile",
        "ast", "io", "contextlib", "unittest", "unittest.mock",
        "sysconfig", "torch"
    }

    non_stdlib = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod not in stdlib_modules:
                    non_stdlib.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod not in stdlib_modules:
                    non_stdlib.append(node.module)

    assert not non_stdlib, f"Non-stdlib imports found: {non_stdlib}"


# [repo_tests] pass_to_pass
def test_repo_shell_scripts_syntax():
    """Shell scripts in .ci/pytorch must have valid syntax (pass_to_pass)."""
    ci_dir = Path("/workspace/.ci/pytorch")
    sh_files = list(ci_dir.glob("*.sh"))
    assert sh_files, "No shell scripts found in .ci/pytorch"

    for sh_file in sh_files[:5]:  # Limit to first 5 to avoid timeout
        r = subprocess.run(
            ["bash", "-n", str(sh_file)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{sh_file.name} has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_binary_symbols_compiles():
    """check_binary_symbols.py must compile without errors (pass_to_pass)."""
    binary_symbols_path = "/workspace/.ci/pytorch/smoke_test/check_binary_symbols.py"
    r = subprocess.run(
        ["python3", "-m", "py_compile", binary_symbols_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"check_binary_symbols.py failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_gomp_compiles():
    """check_gomp.py must compile without errors (pass_to_pass)."""
    gomp_path = "/workspace/.ci/pytorch/smoke_test/check_gomp.py"
    r = subprocess.run(
        ["python3", "-m", "py_compile", gomp_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"check_gomp.py failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_gomp_imports():
    """check_gomp.py must be importable (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import sys; sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test'); import check_gomp; print('OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"check_gomp.py import failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_check_wheel_tags_imports():
    """check_wheel_tags.py must be importable (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import sys; sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test'); import check_wheel_tags; print('OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"check_wheel_tags.py import failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_smoke_test_py_compiles():
    """smoke_test.py must compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "/workspace/.ci/pytorch/smoke_test/smoke_test.py"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"smoke_test.py failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_max_autotune_py_compiles():
    """max_autotune.py must compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "/workspace/.ci/pytorch/smoke_test/max_autotune.py"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"max_autotune.py failed to compile:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_common_sh_syntax():
    """common.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/common.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"common.sh has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_common_build_sh_syntax():
    """common-build.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/common-build.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"common-build.sh has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_binary_populate_env_sh_syntax():
    """binary_populate_env.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/binary_populate_env.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"binary_populate_env.sh has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_binary_sh_syntax():
    """check_binary.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/check_binary.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"check_binary.sh has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_build_sh_syntax():
    """build.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/build.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"build.sh has shell syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_run_tests_sh_syntax():
    """run_tests.sh must have valid shell syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "/workspace/.ci/pytorch/run_tests.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"run_tests.sh has shell syntax errors:\n{r.stderr}"
