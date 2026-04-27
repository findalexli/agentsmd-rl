"""
Task: areal-config-postinit-validation
Repo: inclusionAI/AReaL @ 03d71153a72581d83df72d69c30586a41ba71665
PR:   #970

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/AReaL"


def _stub_problematic_imports():
    """Stub heavy dependencies so cli_args can be imported."""
    import types

    # Basic module stubs
    for mod in ["uvloop", "aiohttp", "y_py", "httpx", "click", "colorlog"]:
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

    # uvloop.install()
    sys.modules["uvloop"].install = lambda: None

    # colorlog
    clog = sys.modules["colorlog"]
    clog.Formatter = type("Formatter", (), {"__init__": lambda *a, **k: None})
    clog.StreamHandler = type("StreamHandler", (), {"__init__": lambda *a, **k: None})
    clog.getLogger = lambda name: types.SimpleNamespace(
        setLevel=lambda l: None,
        addHandler=lambda h: None,
        debug=lambda *a, **k: None,
        info=lambda *a, **k: None,
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
        critical=lambda *a, **k: None,
    )

    # yaml
    if "yaml" not in sys.modules:
        yaml = types.ModuleType("yaml")
        yaml.safe_load = lambda x: {}
        yaml.dump = lambda *a, **k: ""
        sys.modules["yaml"] = yaml

    # hydra
    hydra = types.ModuleType("hydra")
    hydra.compose = lambda *a, **k: types.SimpleNamespace()
    hydra.initialize = lambda *a, **k: types.SimpleNamespace(
        __enter__=lambda: None, __exit__=lambda *a: False
    )
    sys.modules["hydra"] = hydra
    sys.modules["hydra.conf"] = types.ModuleType("hydra.conf")
    sys.modules["hydra.core"] = types.ModuleType("hydra.core")
    sys.modules["hydra.core.global_hydra"] = types.ModuleType("hydra.core.global_hydra")

    class MockGlobalHydra:
        @classmethod
        def instance(cls):
            return types.SimpleNamespace(is_initialized=lambda: False, clear=lambda: None)
    sys.modules["hydra.core.global_hydra"].GlobalHydra = MockGlobalHydra

    # omegaconf
    omega = types.ModuleType("omegaconf")
    omega.MISSING = "???"
    omega.DictConfig = dict
    class MockOmegaConf:
        @staticmethod
        def create(x): return x
        @staticmethod
        def to_container(x, **k): return x
        @staticmethod
        def merge(*a): return a[0] if a else {}
    omega.OmegaConf = MockOmegaConf
    sys.modules["omegaconf"] = omega

    # areal stubs
    for submod in ["areal", "areal.utils", "areal.utils.logging",
                   "areal.utils.name_resolve", "areal.utils.pkg_version",
                   "areal.utils.constants", "areal.infra", "areal.infra.utils",
                   "areal.infra.utils.concurrent", "areal.infra.workflow_context"]:
        if submod not in sys.modules:
            sys.modules[submod] = types.ModuleType(submod)

    # Make areal a package
    sys.modules["areal"].__path__ = [f"{REPO}/areal"]

    # areal.utils.logging
    logger_ns = types.SimpleNamespace(
        debug=lambda *a, **k: None,
        info=lambda *a, **k: None,
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
        critical=lambda *a, **k: None,
    )
    sys.modules["areal.utils.logging"].getLogger = lambda name: logger_ns

    # areal.utils.constants
    const = sys.modules["areal.utils.constants"]
    const.PROX_LOGP_METHOD_RECOMPUTE = "recompute"
    const.PROX_LOGP_METHODS_ALL = ["recompute"]

    # areal.utils.pkg_version - add is_version_less
    sys.modules["areal.utils.pkg_version"].is_version_less = lambda a, b: False


def _load_normconfig():
    """Extract NormConfig class from source and return it."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    match = re.search(
        r"(@dataclass[^\n]*\nclass NormConfig:.*?)(?=\n@dataclass|\nclass \w)",
        src, re.DOTALL,
    )
    assert match, "Could not find NormConfig class"
    ns = {"__builtins__": __builtins__}
    exec("from dataclasses import dataclass, field\n" + match.group(1), ns)
    return ns["NormConfig"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        src = Path(f"{REPO}/{fname}").read_text()
        compile(src, fname, "exec")


def test_repo_ruff_format():
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["python3", "-m", "pip", "install", "-q", "ruff==0.14.9"], check=True)
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/areal/api/cli_args.py", f"{REPO}/areal/utils/data.py"],
        capture_output=True, text=True, timeout=60,
    )
    err_msg = r.stderr + r.stdout
    assert r.returncode == 0, "Ruff format check failed: " + err_msg


def test_repo_ruff_check():
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["python3", "-m", "pip", "install", "-q", "ruff==0.14.9"], check=True)
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/areal/api/cli_args.py", f"{REPO}/areal/utils/data.py"],
        capture_output=True, text=True, timeout=60,
    )
    err_msg = r.stderr + r.stdout
    assert r.returncode == 0, "Ruff check failed: " + err_msg


def test_repo_python_syntax():
    for f in [f"{REPO}/areal/api/cli_args.py", f"{REPO}/areal/utils/data.py"]:
        src = Path(f).read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError("Syntax error in " + f + ": " + str(e))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - NormConfig validation
# ---------------------------------------------------------------------------

def test_normconfig_rejects_invalid_mean_level():
    NormConfig = _load_normconfig()
    for bad in ["invalid", "per_sample", 42]:
        try:
            NormConfig(mean_level=bad, std_level="batch", group_size=1)
            raise AssertionError("NormConfig accepted mean_level=" + repr(bad))
        except (ValueError, TypeError):
            pass


def test_normconfig_rejects_invalid_std_level():
    NormConfig = _load_normconfig()
    for bad in ["invalid", "per_sample", 99]:
        try:
            NormConfig(mean_level="batch", std_level=bad, group_size=1)
            raise AssertionError("NormConfig accepted std_level=" + repr(bad))
        except (ValueError, TypeError):
            pass


def test_normconfig_rejects_bad_group_size():
    NormConfig = _load_normconfig()
    for bad_size in [0, -1, -10]:
        try:
            NormConfig(mean_level="group", std_level="batch", group_size=bad_size)
            raise AssertionError("NormConfig accepted group_size=" + str(bad_size))
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - PPOActorConfig SAPO validation
# ---------------------------------------------------------------------------

def test_ppo_rejects_negative_sapo_temperature():
    """Test that PPOActorConfig raises ValueError when SAPO temps are <= 0."""
    _stub_problematic_imports()
    sys.path.insert(0, REPO)
    from areal.api.cli_args import PPOActorConfig

    # Case 1: negative sapo_tau_pos
    try:
        PPOActorConfig(
            experiment_name='test', trial_name='test',
            use_sapo_loss=True, sapo_tau_pos=-1.0, sapo_tau_neg=0.5
        )
        raise AssertionError("PPOActorConfig accepted sapo_tau_pos=-1.0")
    except ValueError:
        pass

    # Case 2: zero sapo_tau_pos
    try:
        PPOActorConfig(
            experiment_name='test', trial_name='test',
            use_sapo_loss=True, sapo_tau_pos=0.0, sapo_tau_neg=0.5
        )
        raise AssertionError("PPOActorConfig accepted sapo_tau_pos=0.0")
    except ValueError:
        pass

    # Case 3: negative sapo_tau_neg
    try:
        PPOActorConfig(
            experiment_name='test', trial_name='test',
            use_sapo_loss=True, sapo_tau_pos=1.0, sapo_tau_neg=-0.5
        )
        raise AssertionError("PPOActorConfig accepted sapo_tau_neg=-0.5")
    except ValueError:
        pass

    # Case 4: zero sapo_tau_neg
    try:
        PPOActorConfig(
            experiment_name='test', trial_name='test',
            use_sapo_loss=True, sapo_tau_pos=1.0, sapo_tau_neg=0.0
        )
        raise AssertionError("PPOActorConfig accepted sapo_tau_neg=0.0")
    except ValueError:
        pass


def test_ppo_rejects_sapo_with_decoupled_loss():
    """Test that PPOActorConfig raises ValueError when SAPO + decoupled_loss are both True."""
    _stub_problematic_imports()
    sys.path.insert(0, REPO)
    from areal.api.cli_args import PPOActorConfig

    try:
        PPOActorConfig(
            experiment_name='test', trial_name='test',
            use_sapo_loss=True, use_decoupled_loss=True
        )
        raise AssertionError("PPOActorConfig accepted use_sapo_loss + use_decoupled_loss")
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - BaseExperimentConfig validation
# ---------------------------------------------------------------------------

def test_base_experiment_rejects_bad_epochs():
    """Test that BaseExperimentConfig raises ValueError when total_train_epochs <= 0."""
    _stub_problematic_imports()
    sys.path.insert(0, REPO)
    from areal.api.cli_args import BaseExperimentConfig

    for val in [0, -1, -100]:
        try:
            BaseExperimentConfig(
                experiment_name='test', trial_name='test',
                total_train_epochs=val
            )
            raise AssertionError(f"BaseExperimentConfig accepted total_train_epochs={val}")
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - Normalization redundant validation removed
# ---------------------------------------------------------------------------

def test_normalization_init_no_redundant_validation():
    src = Path(f"{REPO}/areal/utils/data.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Normalization":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    raise_count = sum(
                        1 for child in ast.walk(item)
                        if isinstance(child, ast.Raise)
                    )
                    assert raise_count == 0, (
                        "Normalization.__init__ still contains " + str(raise_count) +
                        " raise statement(s) - validation appears to remain"
                    )
                    return
    raise AssertionError("Could not find Normalization.__init__")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression
# ---------------------------------------------------------------------------

def test_valid_normconfig_constructs():
    NormConfig = _load_normconfig()
    c = NormConfig()
    assert c.mean_level == "batch"
    assert c.std_level == "batch"
    assert c.group_size == 1
    c2 = NormConfig(mean_level="group", std_level="batch", group_size=4)
    assert c2.group_size == 4
    c3 = NormConfig(mean_level=None, std_level=None)
    assert c3.mean_level is None


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_validation_uses_valueerror():
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
                                    node.name + " raises " + exc.id + ", expected ValueError"
                                )
                            checked.add(node.name)
    assert "NormConfig" in checked, "NormConfig.__post_init__ has no raise statements"


def test_no_wildcard_imports():
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        tree = ast.parse(Path(f"{REPO}/{fname}").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "*" for alias in node.names
            ):
                raise AssertionError(
                    "Wildcard import in " + fname + ": from " + str(node.module) + " import *"
                )


# ---------------------------------------------------------------------------
# Structural - anti-stub + consistency (pr_diff)
# ---------------------------------------------------------------------------

def test_normconfig_postinit_not_stub():
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
                        "NormConfig.__post_init__ has only " + str(meaningful) + " meaningful stmts"
                    )
                    return
    raise AssertionError("NormConfig missing __post_init__")


def test_postinit_methods_have_docstrings():
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
                        node.name + ".__post_init__ is missing a docstring"
                    )


def test_no_print_calls_in_modified_files():
    for fname in ["areal/api/cli_args.py", "areal/utils/data.py"]:
        src = Path(f"{REPO}/{fname}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise AssertionError(
                        "print() call found in " + fname + "; use areal.utils.logging instead"
                    )


def test_ppo_postinit_calls_super():
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
