"""
Task: pytorch-wheel-tag-minos-validation
Repo: pytorch/pytorch @ 2a86e1131417aa9fa6b860b03308215bfe2be92c
PR:   #177609

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO = "/workspace"
SRC = f"{REPO}/.ci/pytorch/smoke_test/check_wheel_tags.py"
SMOKE = f"{REPO}/.ci/pytorch/smoke_test/smoke_test.py"

# Ensure the smoke_test dir is importable
sys.path.insert(0, f"{REPO}/.ci/pytorch/smoke_test")


def _make_wheel(tmpdir, filename, tag_lines):
    """Helper: create a minimal .whl with given Tag: lines in WHEEL metadata."""
    whl = Path(tmpdir) / filename
    wheel_content = "Wheel-Version: 1.0\nGenerator: bdist_wheel\nRoot-Is-Purelib: false\n"
    for tag in tag_lines:
        wheel_content += f"Tag: {tag}\n"
    with zipfile.ZipFile(whl, "w") as zf:
        # Use the standard dist-info name derived from the wheel filename
        dist_info = filename.split("-")[0] + "-" + filename.split("-")[1] + ".dist-info"
        zf.writestr(f"{dist_info}/WHEEL", wheel_content)
    return whl


def _env_context(**env_vars):
    """Context manager that sets env vars and restores them after."""
    import contextlib

    @contextlib.contextmanager
    def ctx():
        old = {k: os.environ.get(k) for k in env_vars}
        for k, v in env_vars.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        try:
            yield
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    return ctx()


# ---------------------------------------------------------------------------
# Gates (fail_to_pass, static) — file must exist and parse
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_syntax_check():
    """check_wheel_tags.py must exist and parse without syntax errors."""
    import py_compile

    assert Path(SRC).exists(), f"check_wheel_tags.py not found at {SRC}"
    py_compile.compile(SRC, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_extract_wheel_tags_basic():
    """_extract_wheel_tags reads Tag: lines from WHEEL metadata inside a zip."""
    from check_wheel_tags import _extract_wheel_tags

    with tempfile.TemporaryDirectory() as td:
        whl = _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [
            "cp312-cp312-linux_x86_64",
            "cp312-cp312-manylinux_2_17_x86_64",
        ])
        tags = list(_extract_wheel_tags(whl))
        assert "cp312-cp312-linux_x86_64" in tags
        assert "cp312-cp312-manylinux_2_17_x86_64" in tags
        assert len(tags) == 2


# [pr_diff] fail_to_pass
def test_extract_wheel_tags_varied():
    """_extract_wheel_tags works with different wheel content (anti-hardcode)."""
    from check_wheel_tags import _extract_wheel_tags

    test_cases = [
        ("torch-2.11.0-cp311-cp311-win_amd64.whl", ["cp311-cp311-win_amd64"]),
        ("torch-2.13.0-cp310-cp310-macosx_11_0_arm64.whl", ["cp310-cp310-macosx_11_0_arm64"]),
        ("torch-3.0.0-cp313-cp313-linux_x86_64.whl", [
            "cp313-cp313-linux_x86_64",
            "cp313-cp313-manylinux_2_28_x86_64",
            "cp313-cp313-manylinux_2_17_x86_64",
        ]),
    ]
    for filename, expected_tags in test_cases:
        with tempfile.TemporaryDirectory() as td:
            whl = _make_wheel(td, filename, expected_tags)
            tags = list(_extract_wheel_tags(whl))
            assert len(tags) == len(expected_tags), (
                f"Expected {len(expected_tags)} tags for {filename}, got {len(tags)}"
            )
            for et in expected_tags:
                assert et in tags, f"Missing tag {et} in {tags} for {filename}"


# [pr_diff] fail_to_pass
def test_extract_wheel_tags_no_wheel_file():
    """_extract_wheel_tags returns empty list when WHEEL metadata is missing."""
    from check_wheel_tags import _extract_wheel_tags

    with tempfile.TemporaryDirectory() as td:
        whl = Path(td) / "torch-2.12.0-cp312-cp312-linux_x86_64.whl"
        with zipfile.ZipFile(whl, "w") as zf:
            zf.writestr("torch/version.py", "__version__ = '2.12.0'\n")
        tags = list(_extract_wheel_tags(whl))
        assert tags == [], f"Expected empty list for wheel without WHEEL file, got {tags}"


# [pr_diff] fail_to_pass
def test_platform_tag_accepts_valid():
    """check_wheel_platform_tag accepts a valid wheel with matching platform."""
    import check_wheel_tags

    importlib.reload(check_wheel_tags)
    # Test linux x86_64
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [
            "cp312-cp312-linux_x86_64",
        ])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()  # must NOT raise

    # Test windows
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-win_amd64.whl", [
            "cp312-cp312-win_amd64",
        ])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="windows"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()  # must NOT raise


# [pr_diff] fail_to_pass
def test_platform_tag_rejects_mismatch():
    """check_wheel_platform_tag raises RuntimeError for platform mismatch."""
    import check_wheel_tags

    importlib.reload(check_wheel_tags)

    mismatch_cases = [
        # (filename, tags, target_os, description)
        ("torch-2.12.0-cp312-cp312-win_amd64.whl", ["cp312-cp312-win_amd64"], "linux",
         "win_amd64 wheel on linux"),
        ("torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"], "windows",
         "linux wheel on windows"),
    ]

    for filename, tags, target_os, desc in mismatch_cases:
        with tempfile.TemporaryDirectory() as td:
            _make_wheel(td, filename, tags)
            with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS=target_os):
                importlib.reload(check_wheel_tags)
                with pytest.raises(RuntimeError):
                    check_wheel_tags.check_wheel_platform_tag()


# [pr_diff] fail_to_pass
def test_malformed_tag_rejected():
    """Tags with != 3 dash-separated parts must raise an error."""
    import check_wheel_tags

    importlib.reload(check_wheel_tags)

    malformed_tags = [
        "cp312-linux_x86_64",           # only 2 parts
        "cp312",                          # only 1 part
        "cp312-cp312-linux_x86_64-extra", # 4 parts
    ]

    for bad_tag in malformed_tags:
        with tempfile.TemporaryDirectory() as td:
            _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [bad_tag])
            with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
                importlib.reload(check_wheel_tags)
                with pytest.raises((RuntimeError, ValueError, TypeError)):
                    check_wheel_tags.check_wheel_platform_tag()


# [pr_diff] fail_to_pass
def test_platform_patterns_correct():
    """EXPECTED_PLATFORM_TAGS patterns match correct platforms and reject wrong ones."""
    import re

    from check_wheel_tags import EXPECTED_PLATFORM_TAGS

    keys = set(EXPECTED_PLATFORM_TAGS.keys())
    assert "linux" in keys, "Missing 'linux' key"
    win_key = "windows" if "windows" in keys else "win32"
    assert win_key in keys, "Missing 'windows' or 'win32' key"
    assert "darwin" in keys, "Missing 'darwin' key"

    linux_pat = EXPECTED_PLATFORM_TAGS["linux"]
    win_pat = EXPECTED_PLATFORM_TAGS[win_key]
    darwin_pat = EXPECTED_PLATFORM_TAGS["darwin"]

    # Linux must match x86_64 linux platforms
    assert re.search(linux_pat, "linux_x86_64") or re.search(
        linux_pat, "manylinux_2_17_x86_64"
    ), "linux pattern rejects linux_x86_64"
    assert not re.search(linux_pat, "win_amd64"), "linux pattern accepts win_amd64"

    # Windows must match win_amd64
    assert re.search(win_pat, "win_amd64"), "windows pattern rejects win_amd64"
    assert not re.search(win_pat, "linux_x86_64"), "windows pattern accepts linux_x86_64"

    # Darwin must match macosx arm64 and x86_64
    assert re.search(darwin_pat, "macosx_11_0_arm64"), "darwin rejects macosx_11_0_arm64"
    assert re.search(darwin_pat, "macosx_14_0_x86_64"), "darwin rejects macosx_14_0_x86_64"
    assert not re.search(darwin_pat, "linux_x86_64"), "darwin accepts linux_x86_64"
    assert not re.search(darwin_pat, "win_amd64"), "darwin accepts win_amd64"

    # Check linux-aarch64 if present
    if "linux-aarch64" in keys:
        aarch_pat = EXPECTED_PLATFORM_TAGS["linux-aarch64"]
        assert re.search(aarch_pat, "linux_aarch64") or re.search(
            aarch_pat, "manylinux_2_17_aarch64"
        ), "linux-aarch64 pattern rejects aarch64 platforms"


# [pr_diff] fail_to_pass
def test_multiple_wheels_rejected():
    """Having more than one torch wheel in the dir should raise RuntimeError."""
    import check_wheel_tags

    importlib.reload(check_wheel_tags)
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [
            "cp312-cp312-linux_x86_64",
        ])
        _make_wheel(td, "torch-2.13.0-cp312-cp312-linux_x86_64.whl", [
            "cp312-cp312-linux_x86_64",
        ])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            with pytest.raises(RuntimeError):
                check_wheel_tags.check_wheel_platform_tag()


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + integration
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_smoke_test_structure():
    """smoke_test.py must still parse and contain main()."""
    import ast

    tree = ast.parse(Path(SMOKE).read_text())
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "main" in funcs, "main() not found in smoke_test.py"


# [pr_diff] fail_to_pass
def test_smoke_test_integration():
    """smoke_test.py must import check_wheel_tags and call its functions."""
    import ast

    tree = ast.parse(Path(SMOKE).read_text())
    found_import = False
    found_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "check_wheel_tags" in node.module:
            found_import = True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "check_wheel_tags" in alias.name:
                    found_import = True
        # Check for function calls to check_wheel_platform_tag or check_mac_wheel_minos
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in (
                "check_wheel_platform_tag", "check_mac_wheel_minos"
            ):
                found_call = True
            elif isinstance(func, ast.Attribute) and func.attr in (
                "check_wheel_platform_tag", "check_mac_wheel_minos"
            ):
                found_call = True
    assert found_import, "No import of check_wheel_tags found in smoke_test.py"
    assert found_call, "No call to check_wheel_platform_tag or check_mac_wheel_minos in smoke_test.py"


# ---------------------------------------------------------------------------
# Anti-stub (static) — functions must have real logic
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """check_wheel_tags functions have real logic, not empty bodies."""
    # AST-only because: check_wheel_tags imports are side-effect-free but we need
    # to verify function body size independent of runtime behavior
    import ast

    tree = ast.parse(Path(SRC).read_text())
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert len(funcs) >= 2, f"Only {len(funcs)} functions, need >=2"
    for fn in funcs:
        body = fn.body
        # Skip docstring
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0].value, "value", None), str)
        ):
            body = body[1:]
        assert len(body) >= 3, f"{fn.name}() has only {len(body)} non-docstring statements"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_smoke_test_py_compile():
    """Repo's smoke_test Python files compile without syntax errors (pass_to_pass)."""
    import py_compile

    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    py_files = list(smoke_test_dir.glob("*.py"))
    assert len(py_files) > 0, f"No Python files found in {smoke_test_dir}"
    for py_file in py_files:
        py_compile.compile(py_file, doraise=True)


# [repo_tests] pass_to_pass
def test_smoke_test_ruff():
    """Repo's smoke_test Python files pass ruff linting (pass_to_pass)."""
    import subprocess

    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    r = subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["python", "-m", "ruff", "check", str(smoke_test_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_smoke_test_flake8():
    """Repo's smoke_test Python files pass flake8 linting (pass_to_pass)."""
    import subprocess

    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    r = subprocess.run(
        ["python", "-m", "pip", "install", "flake8", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install flake8: {r.stderr}"

    r = subprocess.run(
        ["python", "-m", "flake8", str(smoke_test_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Flake8 check failed:\n{r.stdout}{r.stderr}"
