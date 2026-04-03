"""
Task: areal-config-postinit-validation
Repo: inclusionAI/AReaL @ 03d71153a72581d83df72d69c30586a41ba71665
PR:   #970

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_normconfig():
    """Extract NormConfig class from source and return it."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    match = re.search(
        r"(@dataclass[^\n]*\nclass NormConfig:.*?)(?=\n@dataclass|\nclass \w)",
        src, re.DOTALL,
    )
    assert match, "Could not find NormConfig class in cli_args.py"
    ns = {"__builtins__": __builtins__}
    exec("from dataclasses import dataclass, field\n" + match.group(1), ns)
    return ns["NormConfig"]


def _extract_post_init(classname):
    """Extract __post_init__ from classname, neutralize super() call, return callable."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    lines = src.splitlines(keepends=True)
                    func_src = textwrap.dedent(
                        "".join(lines[item.lineno - 1 : item.end_lineno])
                    )
                    func_src = func_src.replace("super().__post_init__()", "pass")
                    ns = {"__builtins__": __builtins__, "ValueError": ValueError}
                    exec(func_src, ns)
                    return ns["__post_init__"]
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        src = Path(f"{REPO}/{fname}").read_text()
        compile(src, fname, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — NormConfig validation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_normconfig_rejects_invalid_mean_level():
    """NormConfig(mean_level='invalid') raises ValueError at construction."""
    NormConfig = _load_normconfig()
    for bad in ["invalid", "per_sample", 42]:
        try:
            NormConfig(mean_level=bad, std_level="batch", group_size=1)
            raise AssertionError(f"NormConfig accepted mean_level={bad!r}")
        except (ValueError, TypeError):
            pass


# [pr_diff] fail_to_pass
def test_normconfig_rejects_invalid_std_level():
    """NormConfig(std_level='invalid') raises ValueError at construction."""
    NormConfig = _load_normconfig()
    for bad in ["invalid", "per_sample", 99]:
        try:
            NormConfig(mean_level="batch", std_level=bad, group_size=1)
            raise AssertionError(f"NormConfig accepted std_level={bad!r}")
        except (ValueError, TypeError):
            pass


# [pr_diff] fail_to_pass
def test_normconfig_rejects_bad_group_size():
    """NormConfig rejects group_size<=0 when using group normalization."""
    NormConfig = _load_normconfig()
    for bad_size in [0, -1, -10]:
        try:
            NormConfig(mean_level="group", std_level="batch", group_size=bad_size)
            raise AssertionError(f"NormConfig accepted group_size={bad_size}")
        except (ValueError, TypeError):
            pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — PPOActorConfig SAPO validation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ppo_rejects_negative_sapo_temperature():
    """PPOActorConfig rejects negative/zero SAPO temperatures."""
    post_init = _extract_post_init("PPOActorConfig")
    assert post_init is not None, "PPOActorConfig.__post_init__ not found"

    bad_cases = [
        {"sapo_tau_pos": -1.0, "sapo_tau_neg": 0.5},
        {"sapo_tau_pos": 0.0, "sapo_tau_neg": 0.5},
        {"sapo_tau_pos": 1.0, "sapo_tau_neg": 0.0},
        {"sapo_tau_pos": 1.0, "sapo_tau_neg": -0.5},
    ]
    for case in bad_cases:
        mock = SimpleNamespace(
            use_sapo_loss=True,
            use_decoupled_loss=False,
            behave_imp_weight_mode="disabled",
            behave_imp_weight_cap=None,
            **case,
        )
        try:
            post_init(mock)
            raise AssertionError(f"PPOActorConfig accepted SAPO temps {case}")
        except ValueError:
            pass


# [pr_diff] fail_to_pass
def test_ppo_rejects_sapo_with_decoupled_loss():
    """PPOActorConfig rejects use_sapo_loss=True + use_decoupled_loss=True."""
    post_init = _extract_post_init("PPOActorConfig")
    assert post_init is not None, "PPOActorConfig.__post_init__ not found"

    mock = SimpleNamespace(
        use_sapo_loss=True,
        sapo_tau_pos=1.0,
        sapo_tau_neg=1.0,
        use_decoupled_loss=True,
        behave_imp_weight_mode="disabled",
        behave_imp_weight_cap=None,
    )
    try:
        post_init(mock)
        raise AssertionError("PPOActorConfig accepted SAPO + decoupled_loss")
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BaseExperimentConfig validation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_experiment_rejects_bad_epochs():
    """BaseExperimentConfig rejects total_train_epochs <= 0."""
    post_init = _extract_post_init("BaseExperimentConfig")
    assert post_init is not None, "BaseExperimentConfig.__post_init__ not found"

    for bad in [0, -1, -100]:
        mock = SimpleNamespace(total_train_epochs=bad)
        try:
            post_init(mock)
            raise AssertionError(
                f"BaseExperimentConfig accepted total_train_epochs={bad}"
            )
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_normconfig_constructs():
    """Valid NormConfig values construct without error."""
    NormConfig = _load_normconfig()

    c = NormConfig()
    assert c.mean_level == "batch"
    assert c.std_level == "batch"
    assert c.group_size == 1

    c2 = NormConfig(mean_level="group", std_level="batch", group_size=4)
    assert c2.group_size == 4

    c3 = NormConfig(mean_level=None, std_level=None)
    assert c3.mean_level is None


# [pr_diff] fail_to_pass
def test_normalization_init_no_redundant_validation():
    """Normalization.__init__ no longer validates mean_level/std_level itself."""
    src = Path(f"{REPO}/areal/utils/data.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Normalization":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_src = ast.get_source_segment(src, item)
                    for child in ast.walk(item):
                        if isinstance(child, ast.Raise) and child.exc is not None:
                            raise_src = ast.get_source_segment(src, child)
                            assert not (
                                raise_src
                                and (
                                    "mean_level" in raise_src
                                    or "std_level" in raise_src
                                )
                            ), "Normalization.__init__ still has redundant validation"
                    assert "mean_level not in" not in init_src, (
                        "Normalization.__init__ still checks mean_level"
                    )
                    assert "std_level not in" not in init_src, (
                        "Normalization.__init__ still checks std_level"
                    )
                    return
    raise AssertionError("Could not find Normalization.__init__")


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:156 @ 03d71153
def test_validation_uses_valueerror():
    """Config __post_init__ methods raise ValueError (not other exception types)."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    target_classes = {"NormConfig", "PPOActorConfig", "BaseExperimentConfig"}
    checked = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in target_classes:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    for child in ast.walk(item):
                        if isinstance(child, ast.Raise) and child.exc is not None:
                            exc = child.exc
                            if isinstance(exc, ast.Call):
                                exc = exc.func
                            if isinstance(exc, ast.Name):
                                assert exc.id == "ValueError", (
                                    f"{node.name} raises {exc.id}, expected ValueError"
                                )
                            checked.add(node.name)

    assert "NormConfig" in checked, "NormConfig.__post_init__ has no raise statements"


# [agent_config] pass_to_pass — CLAUDE.md:88 @ 03d71153
def test_no_wildcard_imports():
    """No wildcard imports in modified files."""
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        tree = ast.parse(Path(f"{REPO}/{fname}").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "*" for alias in node.names
            ):
                raise AssertionError(
                    f"Wildcard import in {fname}: from {node.module} import *"
                )


# ---------------------------------------------------------------------------
# Structural — anti-stub + consistency (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normconfig_postinit_not_stub():
    """NormConfig.__post_init__ has real validation logic, not just pass/return."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NormConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    meaningful = sum(
                        1
                        for stmt in ast.walk(item)
                        if isinstance(stmt, (ast.If, ast.Raise, ast.Assert, ast.Assign))
                    )
                    assert meaningful >= 2, (
                        f"NormConfig.__post_init__ has only {meaningful} meaningful stmts"
                    )
                    return
    raise AssertionError("NormConfig missing __post_init__")


# [agent_config] pass_to_pass — AGENTS.md:159-160 @ 03d71153
def test_postinit_methods_have_docstrings():
    """New/modified __post_init__ methods have docstrings (all public configs need docstrings)."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    target_classes = {"NormConfig", "PPOActorConfig", "BaseExperimentConfig"}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in target_classes:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    has_docstring = (
                        item.body
                        and isinstance(item.body[0], ast.Expr)
                        and isinstance(item.body[0].value, ast.Constant)
                        and isinstance(item.body[0].value.value, str)
                    )
                    assert has_docstring, (
                        f"{node.name}.__post_init__ is missing a docstring"
                    )


# [agent_config] pass_to_pass — AGENTS.md:84-86 @ 03d71153
def test_no_print_calls_in_modified_files():
    """No print() calls in modified files (use areal.utils.logging instead)."""
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        src = Path(f"{REPO}/{fname}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise AssertionError(
                        f"print() call found in {fname}; use areal.utils.logging instead"
                    )


# [pr_diff] pass_to_pass
def test_ppo_postinit_calls_super():
    """PPOActorConfig.__post_init__ calls super().__post_init__()."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PPOActorConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    for child in ast.walk(item):
                        if isinstance(child, ast.Call):
                            func = child.func
                            if (
                                isinstance(func, ast.Attribute)
                                and func.attr == "__post_init__"
                                and isinstance(func.value, ast.Call)
                                and isinstance(func.value.func, ast.Name)
                                and func.value.func.id == "super"
                            ):
                                return
                    raise AssertionError(
                        "PPOActorConfig.__post_init__ doesn't call super().__post_init__()"
                    )
    raise AssertionError("PPOActorConfig.__post_init__ not found")
