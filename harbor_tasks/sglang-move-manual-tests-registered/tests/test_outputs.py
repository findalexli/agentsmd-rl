"""
Task: sglang-move-manual-tests-registered
Repo: sgl-project/sglang @ 4e4b4ac153e7e313bdf26e37f00188acd45c00e0
PR:   22298

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import glob
import os
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"

# Files that should be moved
MOVED_FILES = [
    "test_qwen3_235b.py",
    "test_deepseek_v31.py",
    "test_glm_46_fp8.py",
]

REGISTERED_DIR = f"{REPO}/test/registered/8-gpu-models"
MANUAL_DIR = f"{REPO}/test/manual"


def _file_exists(path: str) -> bool:
    return Path(path).exists()


def _parse_file_for_registrations(filepath: str) -> list:
    """Parse a Python file and extract register_*_ci calls (mimics ci_register.py)."""
    registrations = []
    REGISTER_MAPPING = {
        "register_cpu_ci": "CPU",
        "register_cuda_ci": "CUDA",
        "register_amd_ci": "AMD",
        "register_npu_ci": "NPU",
    }
    try:
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)

        # Look for top-level expression statements that are calls to register_*_ci
        for stmt in tree.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Name) and call.func.id in REGISTER_MAPPING:
                    registrations.append(call.func.id)
    except (SyntaxError, FileNotFoundError):
        pass
    return registrations


def _collect_tests(files: list) -> list:
    """Mimics collect_tests() from ci_register.py - returns list of files with registrations."""
    ci_tests = []
    for file in files:
        registries = _parse_file_for_registrations(file)
        if len(registries) == 0:
            raise ValueError(f"No CI registry found in {file}")
        ci_tests.extend([(file, r) for r in registries])
    return ci_tests


def _import_exists(filepath: str, import_name: str) -> bool:
    """Check if a specific import exists in the file."""
    try:
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and import_name in node.module:
                    return True
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if import_name in alias.name:
                        return True
        return False
    except (SyntaxError, FileNotFoundError):
        return False


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_syntax_check():
    """All modified files must parse without errors."""
    for filename in MOVED_FILES:
        manual_path = f"{MANUAL_DIR}/{filename}"
        if _file_exists(manual_path):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", manual_path],
                capture_output=True,
                timeout=30,
            )
            assert result.returncode == 0, f"Syntax error in {manual_path}: {result.stderr.decode()}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_files_moved_to_manual():
    """Files were moved from test/registered/8-gpu-models/ to test/manual/."""
    for filename in MOVED_FILES:
        manual_path = f"{MANUAL_DIR}/{filename}"
        assert _file_exists(manual_path), f"File should exist in test/manual/: {filename}"


def test_register_cuda_ci_removed_from_manual_files():
    """register_cuda_ci() calls were removed from moved files."""
    for filename in MOVED_FILES:
        manual_path = f"{MANUAL_DIR}/{filename}"
        if _file_exists(manual_path):
            registrations = _parse_file_for_registrations(manual_path)
            assert len(registrations) == 0, f"register_cuda_ci should be removed from {filename}"


def test_import_ci_register_removed():
    """Import of ci_register was removed from moved files."""
    for filename in MOVED_FILES:
        manual_path = f"{MANUAL_DIR}/{filename}"
        if _file_exists(manual_path):
            has_import = _import_exists(manual_path, "ci_register")
            assert not has_import, f"ci_register import should be removed from {filename}"


def test_files_removed_from_registered():
    """Files no longer exist in test/registered/8-gpu-models/."""
    for filename in MOVED_FILES:
        registered_path = f"{REGISTERED_DIR}/{filename}"
        assert not _file_exists(registered_path), f"File should NOT exist in test/registered/8-gpu-models/: {filename}"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression prevention
# -----------------------------------------------------------------------------

def test_collect_tests_does_not_fail():
    """collect_tests() does not raise ValueError for remaining registered files."""
    # Get all files in test/registered/ (excluding the ones we moved)
    script_dir = f"{REPO}/test"
    files = [
        f
        for f in glob.glob(
            os.path.join(script_dir, "registered", "**", "*.py"), recursive=True
        )
        if not f.endswith("/conftest.py") and not f.endswith("/__init__.py")
    ]

    # Exclude the moved files
    files = [f for f in files if os.path.basename(f) not in MOVED_FILES]

    # This should not raise ValueError
    try:
        result = _collect_tests(files)
        # We expect some tests to be found (the remaining files in 8-gpu-models and other dirs)
        assert len(result) > 0, "collect_tests should find registered tests"
    except ValueError as e:
        if "No CI registry found" in str(e):
            raise AssertionError(f"collect_tests raised ValueError for registered files: {e}")
        raise


def test_remaining_registered_files_have_registration():
    """Remaining files in test/registered/8-gpu-models/ have proper CI registration."""
    registered_files = Path(REGISTERED_DIR).glob("*.py")
    for filepath in registered_files:
        if filepath.name in MOVED_FILES:
            continue  # Skip the files that were moved

        # Should have at least one registration
        registrations = _parse_file_for_registrations(str(filepath))
        assert len(registrations) > 0, f"Remaining file {filepath.name} should have CI registration"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression prevention
# -----------------------------------------------------------------------------

def test_repo_precommit():
    """Repo's pre-commit checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True,
        timeout=60,
    )
    # pre-commit run may need network to download hooks; skip if network fails
    r = subprocess.run(
        ["bash", "-c", "SKIP=no-commit-to-branch pre-commit run --all-files --show-diff-on-failure"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit checks failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_ci_register_module():
    """ci_register module parses without errors (pass_to_pass)."""
    ci_register_path = f"{REPO}/python/sglang/test/ci/ci_register.py"
    with open(ci_register_path, "r") as f:
        source = f.read()
    # Should parse without syntax errors
    try:
        ast.parse(source, filename=ci_register_path)
    except SyntaxError as e:
        raise AssertionError(f"ci_register.py has syntax error: {e}")


def test_registered_files_syntax():
    """All registered test files have valid Python syntax (pass_to_pass)."""
    script_dir = f"{REPO}/test"
    registered_files = glob.glob(
        os.path.join(script_dir, "registered", "**", "*.py"), recursive=True
    )
    # Filter out non-test files
    test_files = [f for f in registered_files if not f.endswith(("/conftest.py", "/__init__.py"))]

    errors = []
    for filepath in test_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append(f"{filepath}: {result.stderr.decode()}")

    assert len(errors) == 0, f"Syntax errors found:\n" + "\n".join(errors[:10])


def test_ci_register_ruff():
    """ci_register module passes ruff linting checks (pass_to_pass)."""
    # Install ruff
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=60,
    )
    # Run ruff with same config as pre-commit
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", f"{REPO}/python/sglang/test/ci/ci_register.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff checks failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_ci_register_black():
    """ci_register module passes black formatting check (pass_to_pass)."""
    # Install black
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        timeout=60,
    )
    # Run black check
    r = subprocess.run(
        ["black", "--check", "--diff", f"{REPO}/python/sglang/test/ci/ci_register.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Black formatting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
