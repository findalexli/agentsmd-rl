"""
Task: prime-rl-bench-flag-orchestrator-trainer
Repo: prime-rl @ 6a122196c2696fa971bcd9da5a92da739df5c9cf
PR: 572

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"


def _check_syntax(filepath: str) -> None:
    """Check that a Python file parses without errors."""
    src = Path(filepath).read_text()
    ast.parse(src)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    files = [
        f"{REPO}/src/prime_rl/orchestrator/config.py",
        f"{REPO}/src/prime_rl/orchestrator/orchestrator.py",
        f"{REPO}/src/prime_rl/orchestrator/utils.py",
        f"{REPO}/src/prime_rl/rl.py",
        f"{REPO}/src/prime_rl/trainer/config.py",
        f"{REPO}/src/prime_rl/trainer/train.py",
        f"{REPO}/src/prime_rl/trainer/utils.py",
    ]
    for f in files:
        _check_syntax(f)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for code changes
# -----------------------------------------------------------------------------

def test_trainer_config_has_bench_field():
    """TrainerConfig must have bench field with auto_setup_bench validator."""
    src = Path(f"{REPO}/src/prime_rl/trainer/config.py").read_text()
    tree = ast.parse(src)

    found_bench_field = False
    found_auto_setup_bench = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TrainerConfig":
            # Look for bench field annotation
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if hasattr(item.target, 'id') and item.target.id == "bench":
                        found_bench_field = True
                elif isinstance(item, ast.FunctionDef) and item.name == "auto_setup_bench":
                    found_auto_setup_bench = True

    assert found_bench_field, "TrainerConfig must have 'bench' field"
    assert found_auto_setup_bench, "TrainerConfig must have 'auto_setup_bench' validator method"


def test_orchestrator_config_validator_renamed():
    """OrchestratorConfig validator must be renamed from validate_bench to auto_setup_bench."""
    src = Path(f"{REPO}/src/prime_rl/orchestrator/config.py").read_text()
    tree = ast.parse(src)

    found_auto_setup = False
    found_old_name = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "auto_setup_bench":
            found_auto_setup = True
        if isinstance(node, ast.FunctionDef) and node.name == "validate_bench":
            found_old_name = True

    assert found_auto_setup, "OrchestratorConfig must have 'auto_setup_bench' validator method"
    assert not found_old_name, "OrchestratorConfig should not have 'validate_bench' (should be renamed)"


def test_rl_config_bench_propagation():
    """RLConfig must have bench field that propagates to trainer and orchestrator."""
    src = Path(f"{REPO}/src/prime_rl/rl.py").read_text()
    tree = ast.parse(src)

    found_bench_field = False
    found_auto_setup_bench = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RLConfig":
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if hasattr(item.target, 'id') and item.target.id == "bench":
                        found_bench_field = True
                elif isinstance(item, ast.FunctionDef) and item.name == "auto_setup_bench":
                    found_auto_setup_bench = True

    assert found_bench_field, "RLConfig must have 'bench' field"
    assert found_auto_setup_bench, "RLConfig must have 'auto_setup_bench' validator method"


def test_trainer_utils_print_benchmark():
    """Trainer utils module must have print_benchmark function."""
    src = Path(f"{REPO}/src/prime_rl/trainer/utils.py").read_text()
    tree = ast.parse(src)

    found_print_benchmark = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "print_benchmark":
            found_print_benchmark = True

    assert found_print_benchmark, "trainer/utils.py must have 'print_benchmark' function"


def test_orchestrator_utils_column_rename():
    """Orchestrator utils must use 'time/orchestrator' not 'time/infer' in print_benchmark."""
    src = Path(f"{REPO}/src/prime_rl/orchestrator/utils.py").read_text()

    # Should have time/orchestrator
    assert "time/orchestrator" in src, "Should use 'time/orchestrator' column name"


def test_orchestrator_imports_format_num():
    """Orchestrator must import format_num from utils."""
    src = Path(f"{REPO}/src/prime_rl/orchestrator/orchestrator.py").read_text()

    assert "format_num" in src, "orchestrator.py must import format_num"


# -----------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# -----------------------------------------------------------------------------

def test_readme_documents_bench_flag():
    """README.md must document the --bench flag for benchmarking."""
    readme = Path(f"{REPO}/README.md").read_text()

    # Check for Benchmarking section
    assert "### Benchmarking" in readme, "README must have '### Benchmarking' section"

    # Check for --bench flag mentions
    assert "--bench" in readme, "README must document the --bench flag"

    # Check for the three use cases mentioned in PR
    assert "orchestrator" in readme.lower() or "inference" in readme.lower(), \
        "README should document orchestrator/inference benchmarking"
    assert "trainer" in readme.lower(), \
        "README should document trainer benchmarking"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# -----------------------------------------------------------------------------

def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    # Check trainer/utils.py print_benchmark has real logic
    src = Path(f"{REPO}/src/prime_rl/trainer/utils.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "print_benchmark":
            # Count non-trivial statements (not just pass, docstring, or imports)
            stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))  # Skip pass and docstrings
            ]
            assert len(stmts) >= 5, "print_benchmark should have meaningful implementation"
