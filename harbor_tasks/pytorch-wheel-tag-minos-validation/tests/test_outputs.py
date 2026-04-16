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

sys.path.insert(0, f"{REPO}/.ci/pytorch/smoke_test")


def _make_wheel(tmpdir, filename, tag_lines):
    whl = Path(tmpdir) / filename
    wheel_content = "Wheel-Version: 1.0\nGenerator: bdist_wheel\nRoot-Is-Purelib: false\n"
    for tag in tag_lines:
        wheel_content += f"Tag: {tag}\n"
    with zipfile.ZipFile(whl, "w") as zf:
        dist_info = filename.split("-")[0] + "-" + filename.split("-")[1] + ".dist-info"
        zf.writestr(f"{dist_info}/WHEEL", wheel_content)
    return whl


def _env_context(**env_vars):
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


def test_syntax_check():
    import py_compile
    assert Path(SRC).exists(), f"check_wheel_tags.py not found at {SRC}"
    py_compile.compile(SRC, doraise=True)


def test_extract_wheel_tags_varied():
    """Verify wheel tag extraction works across multiple wheel configurations."""
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
            assert len(tags) == len(expected_tags)
            for et in expected_tags:
                assert et in tags


def test_extract_wheel_tags_no_wheel_file():
    """Verify extraction returns empty list when WHEEL metadata is missing."""
    from check_wheel_tags import _extract_wheel_tags
    with tempfile.TemporaryDirectory() as td:
        whl = Path(td) / "torch-2.12.0-cp312-cp312-linux_x86_64.whl"
        with zipfile.ZipFile(whl, "w") as zf:
            zf.writestr("torch/version.py", "__version__ = '2.12.0'\n")
        tags = list(_extract_wheel_tags(whl))
        assert tags == []


def test_platform_tag_accepts_valid():
    """Verify check_wheel_platform_tag accepts a wheel with matching platform tags."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-win_amd64.whl", ["cp312-cp312-win_amd64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="windows"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()


def test_platform_tag_rejects_mismatch():
    """Verify check_wheel_platform_tag raises RuntimeError for platform mismatch."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    mismatch_cases = [
        ("torch-2.12.0-cp312-cp312-win_amd64.whl", ["cp312-cp312-win_amd64"], "linux"),
        ("torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"], "windows"),
    ]
    for filename, tags, target_os in mismatch_cases:
        with tempfile.TemporaryDirectory() as td:
            _make_wheel(td, filename, tags)
            with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS=target_os):
                importlib.reload(check_wheel_tags)
                with pytest.raises(RuntimeError):
                    check_wheel_tags.check_wheel_platform_tag()


def test_malformed_tag_rejected():
    """Verify malformed tags (wrong number of dash-separated parts) raise errors."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    malformed_tags = [
        "cp312-linux_x86_64",
        "cp312",
        "cp312-cp312-linux_x86_64-extra",
    ]
    for bad_tag in malformed_tags:
        with tempfile.TemporaryDirectory() as td:
            _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [bad_tag])
            with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
                importlib.reload(check_wheel_tags)
                with pytest.raises((RuntimeError, ValueError, TypeError)):
                    check_wheel_tags.check_wheel_platform_tag()


def test_platform_tag_accepts_macos():
    """Verify macOS platform tags are accepted when TARGET_OS=darwin."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-macosx_11_0_arm64.whl", [
            "cp312-cp312-macosx_11_0_arm64",
            "cp312-cp312-macosx_12_0_x86_64",
        ])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="darwin"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()


def test_platform_tag_rejects_wrong_platform():
    """Verify linux wheel is rejected when TARGET_OS=darwin and vice versa."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    cross_platform_cases = [
        ("torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"], "darwin"),
        ("torch-2.12.0-cp312-cp312-macosx_11_0_arm64.whl", ["cp312-cp312-macosx_11_0_arm64"], "linux"),
    ]
    for filename, tags, target_os in cross_platform_cases:
        with tempfile.TemporaryDirectory() as td:
            _make_wheel(td, filename, tags)
            with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS=target_os):
                importlib.reload(check_wheel_tags)
                with pytest.raises(RuntimeError):
                    check_wheel_tags.check_wheel_platform_tag()


def test_multiple_wheels_rejected():
    """Verify exactly one torch wheel is required; more than one raises RuntimeError."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"])
        _make_wheel(td, "torch-2.13.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            with pytest.raises(RuntimeError):
                check_wheel_tags.check_wheel_platform_tag()


def test_smoke_test_structure():
    import ast
    tree = ast.parse(Path(SMOKE).read_text())
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "main" in funcs


def test_smoke_test_integration():
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
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("check_wheel_platform_tag", "check_mac_wheel_minos"):
                found_call = True
            elif isinstance(func, ast.Attribute) and func.attr in ("check_wheel_platform_tag", "check_mac_wheel_minos"):
                found_call = True
    assert found_import
    assert found_call


def test_check_functions_are_callable():
    """Verify wheel tag functions are actually implemented (not stubs)."""
    import check_wheel_tags
    # Create a minimal wheel for testing
    with tempfile.TemporaryDirectory() as td:
        whl = _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", [
            "cp312-cp312-linux_x86_64",
            "cp312-cp312-manylinux_2_17_x86_64",
        ])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            # These functions should be callable and not raise immediately
            check_wheel_tags.check_wheel_platform_tag()
            # check_mac_wheel_minos should return early on linux without error
            check_wheel_tags.check_mac_wheel_minos()


def test_platform_tag_validation_behavior():
    """Verify platform patterns correctly accept/reject tags via actual validation."""
    import check_wheel_tags
    importlib.reload(check_wheel_tags)

    # Test linux patterns
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-linux_x86_64.whl", ["cp312-cp312-linux_x86_64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()

        _make_wheel(td, "torch-2.12.0-cp312-cp312-manylinux_2_17_x86_64.whl", ["cp312-cp312-manylinux_2_17_x86_64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="linux"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()

    # Test windows patterns
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-win_amd64.whl", ["cp312-cp312-win_amd64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="windows"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()

    # Test darwin patterns
    with tempfile.TemporaryDirectory() as td:
        _make_wheel(td, "torch-2.12.0-cp312-cp312-macosx_11_0_arm64.whl", ["cp312-cp312-macosx_11_0_arm64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="darwin"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()

        _make_wheel(td, "torch-2.12.0-cp312-cp312-macosx_14_0_x86_64.whl", ["cp312-cp312-macosx_14_0_x86_64"])
        with _env_context(PYTORCH_FINAL_PACKAGE_DIR=td, TARGET_OS="darwin"):
            importlib.reload(check_wheel_tags)
            check_wheel_tags.check_wheel_platform_tag()


def test_repo_shellcheck():
    import subprocess
    check_binary_sh = Path(REPO) / ".ci" / "pytorch" / "check_binary.sh"
    assert check_binary_sh.exists()
    subprocess.run(["apt-get", "update", "-qq"], capture_output=True, timeout=60)
    subprocess.run(["apt-get", "install", "-y", "-qq", "shellcheck"], capture_output=True, timeout=120)
    r = subprocess.run(["shellcheck", str(check_binary_sh)], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0


def test_smoke_test_py_compile():
    import py_compile
    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    py_files = list(smoke_test_dir.glob("*.py"))
    assert len(py_files) > 0
    for py_file in py_files:
        py_compile.compile(py_file, doraise=True)


_SMOKE_TEST_DIR = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
_SMOKE_TEST_PY_FILES = [f.name for f in _SMOKE_TEST_DIR.glob("*.py")] if _SMOKE_TEST_DIR.exists() else []

@pytest.mark.parametrize("py_file", _SMOKE_TEST_PY_FILES)
def test_smoke_test_py_compile_individual(py_file):
    import py_compile
    py_file_path = Path(REPO) / ".ci" / "pytorch" / "smoke_test" / py_file
    py_compile.compile(py_file_path, doraise=True)


def test_smoke_test_ruff():
    import subprocess
    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    subprocess.run(["python", "-m", "pip", "install", "ruff", "--quiet"], capture_output=True, timeout=120)
    r = subprocess.run(["python", "-m", "ruff", "check", str(smoke_test_dir)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0


def test_smoke_test_flake8():
    import subprocess
    smoke_test_dir = Path(REPO) / ".ci" / "pytorch" / "smoke_test"
    subprocess.run(["python", "-m", "pip", "install", "flake8", "--quiet"], capture_output=True, timeout=120)
    r = subprocess.run(["python", "-m", "flake8", str(smoke_test_dir)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0


def test_repo_shell_scripts_compile():
    import subprocess
    subprocess.run(["apt-get", "update", "-qq"], capture_output=True, timeout=60)
    subprocess.run(["apt-get", "install", "-y", "-qq", "shellcheck"], capture_output=True, timeout=120)
    scripts = [(".ci/pytorch/check_binary.sh", []), (".ci/pytorch/common_utils.sh", ["-e", "SC2317"])]
    for script, extra_args in scripts:
        script_path = Path(REPO) / script
        if script_path.exists():
            cmd = ["shellcheck", "-x"] + extra_args + [str(script_path)]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=REPO)
            assert r.returncode == 0
