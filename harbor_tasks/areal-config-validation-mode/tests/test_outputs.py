"""
Task: areal-config-validation-mode
Repo: inclusionAI/AReaL @ cca5b865b0883f7f6cdb02a01d4929387585d20d
PR:   1134

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import dataclasses
import os
import subprocess
import sys
import types
from pathlib import Path

REPO = "/workspace/areal"


def _get_class_from_source(class_name):
    """Extract a dataclass from cli_args.py and make it instantiable."""
    cli_args_path = Path(f"{REPO}/areal/api/cli_args.py")
    source = cli_args_path.read_text()
    tree = ast.parse(source)

    # Find the class definition
    class_node = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            class_node = node
            break

    if class_node is None:
        raise ValueError(f"Class {class_name} not found in cli_args.py")

    # Build namespace with proper decorators
    import typing
    namespace = {
        "__name__": "cli_args",
        "__file__": str(cli_args_path),
        "dataclasses": __import__("dataclasses"),
        "dataclass": __import__("dataclasses").dataclass,
        "field": __import__("dataclasses").field,
        "os": __import__("os"),
        "Dict": dict,
        "dict": dict,
        "str": str,
        "Optional": typing.Optional,
        "List": list,
        "list": list,
        "Any": typing.Any,
        "Union": typing.Union,
        "Tuple": tuple,
        "Callable": typing.Callable,
        "Type": type,
    }

    # Add typing constructs
    for name in dir(typing):
        if not name.startswith("_"):
            namespace[name] = getattr(typing, name)

    # Handle type annotations like str | None
    try:
        namespace["__future__"] = __import__("__future__")
    except:
        pass

    # Compile and execute the class definition
    class_code = compile(ast.Module(body=[class_node], type_ignores=[]), str(cli_args_path), "exec")

    # Execute in isolated namespace
    exec(class_code, namespace)

    return namespace[class_name]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    ast.parse(src)  # raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wandb_invalid_mode_raises():
    """WandBConfig with invalid mode raises ValueError."""
    WandBConfig = _get_class_from_source("WandBConfig")

    invalid_modes = ["invalid", "test", "cloud", "local", "", "ONLINE"]
    for mode in invalid_modes:
        try:
            cfg = WandBConfig(mode=mode)
            assert False, f"Expected ValueError for mode='{mode}', got no error"
        except ValueError as e:
            assert "Invalid wandb mode" in str(e), f"Expected 'Invalid wandb mode' in error, got: {e}"


# [pr_diff] fail_to_pass
def test_wandb_valid_modes_accepted():
    """WandBConfig with valid modes creates config without error."""
    WandBConfig = _get_class_from_source("WandBConfig")

    valid_modes = ["online", "offline", "disabled", "shared"]
    for mode in valid_modes:
        cfg = WandBConfig(mode=mode)
        assert cfg.mode == mode, f"Expected mode='{mode}', got '{cfg.mode}'"


# [pr_diff] fail_to_pass
def test_swanlab_invalid_mode_raises():
    """SwanlabConfig with invalid mode raises ValueError."""
    SwanlabConfig = _get_class_from_source("SwanlabConfig")

    invalid_modes = ["invalid", "test", "online", "shared", "", "CLOUD"]
    for mode in invalid_modes:
        try:
            cfg = SwanlabConfig(mode=mode)
            assert False, f"Expected ValueError for mode='{mode}', got no error"
        except ValueError as e:
            assert "Invalid swanlab mode" in str(e), f"Expected 'Invalid swanlab mode' in error, got: {e}"


# [pr_diff] fail_to_pass
def test_swanlab_valid_modes_accepted():
    """SwanlabConfig with valid modes creates config without error."""
    SwanlabConfig = _get_class_from_source("SwanlabConfig")

    valid_modes = ["cloud", "local", "disabled", "offline"]
    for mode in valid_modes:
        cfg = SwanlabConfig(mode=mode)
        assert cfg.mode == mode, f"Expected mode='{mode}', got '{cfg.mode}'"


# [pr_diff] pass_to_pass
def test_wandb_default_mode():
    """WandBConfig default mode is 'disabled'."""
    WandBConfig = _get_class_from_source("WandBConfig")

    cfg = WandBConfig()
    assert cfg.mode == "disabled", f"Expected default mode='disabled', got '{cfg.mode}'"


# [pr_diff] pass_to_pass
def test_swanlab_default_mode():
    """SwanlabConfig default mode is 'disabled'."""
    SwanlabConfig = _get_class_from_source("SwanlabConfig")

    cfg = SwanlabConfig()
    assert cfg.mode == "disabled", f"Expected default mode='disabled', got '{cfg.mode}'"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wandb_post_init_validates():
    """WandBConfig validation raises ValueError with all valid options enumerated."""
    WandBConfig = _get_class_from_source("WandBConfig")

    try:
        WandBConfig(mode="bad_mode")
        assert False, "Expected ValueError for invalid mode, got no error"
    except ValueError as e:
        msg = str(e)
        assert "bad_mode" in msg, f"Error must name the invalid value, got: {msg}"
        assert "Invalid wandb mode" in msg, f"Expected 'Invalid wandb mode' in error, got: {msg}"
        for opt in ["online", "offline", "disabled", "shared"]:
            assert opt in msg, f"Error must list valid option '{opt}', got: {msg}"


# [pr_diff] fail_to_pass
def test_swanlab_post_init_validates():
    """SwanlabConfig validation raises ValueError with all valid options enumerated."""
    SwanlabConfig = _get_class_from_source("SwanlabConfig")

    try:
        SwanlabConfig(mode="bad_mode")
        assert False, "Expected ValueError for invalid mode, got no error"
    except ValueError as e:
        msg = str(e)
        assert "bad_mode" in msg, f"Error must name the invalid value, got: {msg}"
        assert "Invalid swanlab mode" in msg, f"Expected 'Invalid swanlab mode' in error, got: {msg}"
        for opt in ["cloud", "local", "disabled", "offline"]:
            assert opt in msg, f"Error must list valid option '{opt}', got: {msg}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ cca5b865b0883f7f6cdb02a01d4929387585d20d
def test_no_wildcard_imports():
    """No wildcard imports in modified file."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.names[0].name != "*", f"Wildcard import found: from {node.module} import *"


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ cca5b865b0883f7f6cdb02a01d4929387585d20d
def test_no_print_statements():
    """No print() calls in modified file — must use logging."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                assert False, "print() call found in cli_args.py — must use areal.utils.logging"


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) — verify repo's own tests pass on base
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_validation():
    """Modified file must have valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Modified file must pass ruff format check (pass_to_pass)."""
    # Install ruff if not present
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120
    )
    # Run format check on modified file
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Modified file must pass ruff lint check (pass_to_pass)."""
    # Install ruff if not present
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120
    )
    # Run lint check with same config as repo's pyproject.toml:
    # select = ["E", "W", "F", "I", "UP"], ignore = ["E501"]
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F,I", "--ignore=E501", f"{REPO}/areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_precommit_hooks():
    """Repo's pre-commit hooks must pass on all files (pass_to_pass)."""
    # Install pre-commit
    r = subprocess.run(
        ["pip", "install", "-q", "pre-commit"],
        capture_output=True, text=True, timeout=120
    )
    # Run pre-commit hooks, skipping generate-cli-docs which requires full package install
    r = subprocess.run(
        ["bash", "-c", "SKIP=generate-cli-docs pre-commit run --all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit hooks failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_yaml_valid():
    """YAML files must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "PyYAML"],
        capture_output=True, text=True, timeout=120
    )
    # Test that pre-commit can validate YAML
    r = subprocess.run(
        ["bash", "-c", "pip install -q pre-commit && pre-commit run check-yaml --all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_trailing_whitespace():
    """No trailing whitespace in source files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install -q pre-commit && pre-commit run trailing-whitespace --all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_install_test_set_up_python():
    """pass_to_pass | CI job 'Install test' → step 'Set up Python'"""
    r = subprocess.run(
        ["python3", "--version"], cwd=REPO,
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (
        f"CI step 'Set up Python' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
    assert "3.12" in r.stdout, f"Expected Python 3.12, got: {r.stdout}"

def test_ci_install_test_verify_package_import():
    """pass_to_pass | CI job 'Install test' → step 'Verify package import'"""
    # Structural check: package __init__.py and version module parse correctly
    repo = Path(REPO)
    init_py = repo / "areal" / "__init__.py"
    version_py = repo / "areal" / "version.py"
    for fp in [init_py, version_py]:
        if not fp.exists():
            raise AssertionError(f"Missing file: {fp}")
        ast.parse(fp.read_text())
    # Verify __version__ is exported from __init__.py
    src = init_py.read_text()
    assert "from .version import __version__" in src or "__version__" in src, (
        f"areal/__init__.py must reference __version__")

def test_ci_install_test_verify_core_modules_are_importable():
    """pass_to_pass | CI job 'Install test' → step 'Verify core modules are importable'"""
    # Structural check: key module files parse as valid Python
    repo = Path(REPO)
    modules = [
        "areal/api/cli_args.py",
        "areal/api/__init__.py",
        "areal/__init__.py",
    ]
    for mod in modules:
        fp = repo / mod
        if not fp.exists():
            raise AssertionError(f"Missing module: {fp}")
        ast.parse(fp.read_text())
    # Verify WandBConfig and SwanlabConfig are defined in cli_args.py
    src = (repo / "areal/api/cli_args.py").read_text()
    assert "class WandBConfig" in src, "WandBConfig class not found"
    assert "class SwanlabConfig" in src, "SwanlabConfig class not found"

def test_ci_install_test_build_wheel():
    """pass_to_pass | CI job 'Install test' → step 'Build wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv build --wheel'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_verify_wheel_artifact():
    """pass_to_pass | CI job 'Install test' → step 'Verify wheel artifact'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m zipfile -l dist/*.whl 2>&1 | awk "NR<=20"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify wheel artifact' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_the_book():
    """pass_to_pass | CI job 'build' → step 'Build the book'"""
    r = subprocess.run(
        ["bash", "-lc", 'cd docs && chmod +x ./build_all.sh && ./build_all.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build the book' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")