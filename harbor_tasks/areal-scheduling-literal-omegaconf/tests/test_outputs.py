"""
Task: areal-scheduling-literal-omegaconf
Repo: inclusionAI/AReaL @ 6860e70c08eae3014e12d9adf5411d648f7fceac
PR:   #976

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/areal/api/cli_args.py"


def _load_scheduling_spec():
    """Extract and instantiate the SchedulingSpec class from source without full imports."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    exec_globals = {"__builtins__": __builtins__}
    exec(
        "from dataclasses import dataclass, field, fields, asdict\n"
        "from typing import TYPE_CHECKING, Any, ClassVar, Literal\n"
        "from enum import Enum\n",
        exec_globals,
    )

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SchedulingSpec":
            start = (
                (node.decorator_list[0].lineno - 1)
                if node.decorator_list
                else (node.lineno - 1)
            )
            end = node.end_lineno
            class_src = "\n".join(source.splitlines()[start:end])
            exec(class_src, exec_globals)
            return exec_globals["SchedulingSpec"]

    raise RuntimeError("SchedulingSpec class not found in source")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """areal/api/cli_args.py must parse as valid Python."""
    source = Path(FILE).read_text()
    ast.parse(source)  # Raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_omegaconf_structured_works():
    """OmegaConf.structured(SchedulingSpec()) succeeds without ValidationError."""
    from omegaconf import OmegaConf

    S = _load_scheduling_spec()
    cfg = OmegaConf.structured(S())
    assert cfg.ray_placement_strategy == "shared"


# [pr_diff] fail_to_pass
def test_invalid_strategy_rejected():
    """Invalid ray_placement_strategy values must raise an error at runtime."""
    S = _load_scheduling_spec()
    invalid_values = ["invalid_value", "SHARED", "spread", "", "none"]
    for val in invalid_values:
        try:
            S(ray_placement_strategy=val)
            raise AssertionError(f"No error raised for invalid strategy: {val!r}")
        except (ValueError, TypeError):
            pass  # Expected


# [pr_diff] fail_to_pass
def test_omegaconf_roundtrip():
    """OmegaConf structured -> to_yaml -> from_yaml roundtrip preserves strategy values."""
    from omegaconf import OmegaConf

    S = _load_scheduling_spec()
    for strategy in ["shared", "separate", "deferred"]:
        cfg = OmegaConf.structured(S(ray_placement_strategy=strategy))
        yaml_str = OmegaConf.to_yaml(cfg)
        reloaded = OmegaConf.create(yaml_str)
        assert reloaded.ray_placement_strategy == strategy, (
            f"Roundtrip failed: {strategy} -> {reloaded.ray_placement_strategy}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_default_instantiation():
    """SchedulingSpec() default works with ray_placement_strategy='shared'."""
    S = _load_scheduling_spec()
    s = S()
    assert s.ray_placement_strategy == "shared"


# [pr_diff] pass_to_pass
def test_valid_strategies_accepted():
    """All three valid strategies (shared, separate, deferred) are accepted."""
    S = _load_scheduling_spec()
    for strategy in ["shared", "separate", "deferred"]:
        s = S(ray_placement_strategy=strategy)
        assert s.ray_placement_strategy == strategy


# [pr_diff] pass_to_pass
def test_core_fields_present():
    """SchedulingSpec retains all expected dataclass fields."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    required_fields = {
        "cpu", "gpu", "mem", "task_type", "exclude",
        "nodelist", "ray_placement_strategy",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SchedulingSpec":
            found = set()
            for item in ast.walk(node):
                if isinstance(item, ast.AnnAssign) and hasattr(item.target, "id"):
                    found.add(item.target.id)
            missing = required_fields - found
            assert not missing, f"Missing fields: {missing}"
            return

    raise AssertionError("SchedulingSpec class not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass -- AGENTS.md:25 @ 6860e70
def test_no_wildcard_imports():
    """No wildcard imports in cli_args.py."""
    source = Path(FILE).read_text()
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("from ") and "import *" in stripped:
            raise AssertionError(f"Wildcard import found: {stripped}")


# [agent_config] pass_to_pass -- AGENTS.md:94-95 @ 6860e70
def test_unused_literal_cleaned():
    """If Literal is no longer used in type annotations, it should not be imported."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    literal_imported = False
    literal_used_in_annotation = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "typing":
            for alias in node.names:
                if alias.name == "Literal":
                    literal_imported = True
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and node.value.id == "Literal":
                literal_used_in_annotation = True

    if literal_imported and not literal_used_in_annotation:
        raise AssertionError("Literal is imported but unused -- should be removed")


# [agent_config] pass_to_pass -- AGENTS.md:84-86 @ 6860e70
def test_no_print_statements():
    """No bare print() calls in cli_args.py (use areal.utils.logging instead)."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                assert False, f"Bare print() call found at line {node.lineno}"


# [agent_config] fail_to_pass -- AGENTS.md:156 @ 6860e70
def test_validation_raises_valueerror():
    """Validation must raise ValueError (not assert/RuntimeError) with a clear message."""
    import pytest

    S = _load_scheduling_spec()
    # Must be ValueError specifically, per AGENTS.md:156
    for bad in ["bogus", "SHARED", ""]:
        with pytest.raises(ValueError, match=r"ray_placement_strategy"):
            S(ray_placement_strategy=bad)


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Python syntax compilation check on areal/api/cli_args.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linting passes on areal/api/cli_args.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Install errors are not fatal; ruff might already be present

    r = subprocess.run(
        ["ruff", "check", "areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on areal/api/cli_args.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Install errors are not fatal; ruff might already be present

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/api/cli_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_datapack_and_train_controller():
    """Repo's unit tests for datapack and train_controller pass (pass_to_pass)."""
    r = subprocess.run(
        "pip install uv -q && uv pip install --system pytest aiohttp ray httpx -e . -q && pytest tests/test_datapack.py tests/test_train_controller.py",
        shell=True, capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_install_test_set_up_python():
    """pass_to_pass | CI job 'Install test' → step 'Set up Python'"""
    r = subprocess.run(
        ["python3", "--version"],
        capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, (
        f"CI step 'Set up Python' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-500:]}\nstderr: {r.stderr[-500:]}")
    assert "3.12" in r.stdout, (
        f"Expected Python 3.12, got: {r.stdout}")

def test_ci_install_test_verify_package_import():
    """pass_to_pass | CI job 'Install test' → step 'Verify package import'"""
    r = subprocess.run(
        ["python3", "-c",
         "import areal; print(f'areal version: {areal.__version__}')"],
        capture_output=True, text=True, timeout=300, cwd=REPO)
    assert r.returncode == 0, (
        f"CI step 'Verify package import' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_verify_core_modules_are_importable():
    """pass_to_pass | CI job 'Install test' → step 'Verify core modules are importable'"""
    r = subprocess.run(
        ["python3", "-c",
         "from areal import (TrainController, RolloutController, WorkflowExecutor, "
         "StalenessManager, workflow_context, current_platform); "
         "print('All core modules imported successfully')"],
        capture_output=True, text=True, timeout=300, cwd=REPO)
    assert r.returncode == 0, (
        f"CI step 'Verify core modules are importable' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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
        ["bash", "-lc", 'python -m zipfile -l dist/*.whl | head -20'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify wheel artifact' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")