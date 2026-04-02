"""
Task: areal-scheduling-literal-omegaconf
Repo: inclusionAI/AReaL @ 6860e70c08eae3014e12d9adf5411d648f7fceac
PR:   #976

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
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
        "from typing import TYPE_CHECKING, Any, ClassVar\n"
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
