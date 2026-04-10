"""
Task: prime-rl-ckpt-skip-optimizer-load
Repo: PrimeIntellect-ai/prime-rl @ d8030652042f38a019beffecd8aa5e07cfefe4c4
PR:   #2087

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"
CONFIG_PY = f"{REPO}/src/prime_rl/configs/trainer.py"
CKPT_PY = f"{REPO}/src/prime_rl/trainer/ckpt.py"


def _load_checkpoint_config():
    """Load CheckpointConfig by exec'ing trainer.py with stubbed imports.

    prime-rl depends on torch.distributed which isn't available in the test
    environment, so we strip internal imports and exec the config module
    with stubs for all internally-defined types.
    """
    from pydantic import BaseModel, Field, model_validator
    from typing import Annotated, Any, Literal, TypeAlias

    class BaseConfig(BaseModel):
        class Config:
            arbitrary_types_allowed = True

    class BaseModelConfig(BaseConfig):
        name: str = "stub"
        trust_remote_code: bool = False

    # Stubs for types imported from prime_rl.configs.shared
    class TransportConfig(BaseConfig):
        pass

    class FileSystemTransportConfig(TransportConfig):
        pass

    class HeartbeatConfig(BaseConfig):
        pass

    class LogConfig(BaseConfig):
        pass

    class MetricsServerConfig(BaseConfig):
        pass

    class WandbConfig(BaseConfig):
        pass

    ns = {
        "BaseModel": BaseModel, "BaseConfig": BaseConfig,
        "BaseModelConfig": BaseModelConfig, "Field": Field,
        "Annotated": Annotated, "Literal": Literal, "Any": Any,
        "TypeAlias": TypeAlias, "Path": Path, "model_validator": model_validator,
        "TransportConfig": TransportConfig,
        "FileSystemTransportConfig": FileSystemTransportConfig,
        "HeartbeatConfig": HeartbeatConfig,
        "LogConfig": LogConfig,
        "MetricsServerConfig": MetricsServerConfig,
        "WandbConfig": WandbConfig,
        "__name__": "__main__",
    }
    src = Path(CONFIG_PY).read_text()
    lines = src.split("\n")
    clean = []
    skip = False
    for line in lines:
        if "from prime_rl." in line:
            skip = True
            continue
        if skip and (line.startswith("    ") or line.startswith(")")):
            if line.strip() == ")":
                skip = False
            continue
        skip = False
        clean.append(line)
    exec(compile("\n".join(clean), "trainer.py", "exec"), ns)
    return ns.get("CheckpointConfig")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for fpath in [CONFIG_PY, CKPT_PY]:
        src = Path(fpath).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", CONFIG_PY, CKPT_PY],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", CONFIG_PY, CKPT_PY],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pathing_unit_tests():
    """Repo's pathing unit tests pass (pass_to_pass).

    These tests verify output directory validation logic used by checkpointing.
    We copy the test to a temp location to bypass conftest.py which requires
    additional dependencies not available in the test environment.
    """
    import tempfile
    import shutil

    # Ensure loguru is installed (required by pathing module)
    subprocess.run(
        ["pip", "install", "-q", "loguru"],
        capture_output=True, timeout=60,
    )

    # Create temp directory and copy test file there to bypass conftest.py
    with tempfile.TemporaryDirectory() as tmpdir:
        test_src = f"{REPO}/tests/unit/utils/test_pathing.py"
        test_dst = f"{tmpdir}/test_pathing.py"
        shutil.copy(test_src, test_dst)

        # Run the test from temp directory (avoids conftest.py in tests/)
        r = subprocess.run(
            ["python", "-m", "pytest", test_dst, "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=tmpdir,
            env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/src"},
        )
        assert r.returncode == 0, f"Pathing unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_field_exists():
    """CheckpointConfig must have a boolean skip_optimizer field."""
    Cfg = _load_checkpoint_config()
    assert Cfg is not None, "CheckpointConfig not found"

    fields = Cfg.model_fields
    assert "skip_optimizer" in fields, (
        f"skip_optimizer not in fields: {list(fields.keys())}"
    )

    ann = fields["skip_optimizer"].annotation
    origin = getattr(ann, "__origin__", None)
    if ann is not bool:
        if origin is not None:
            args = getattr(ann, "__args__", ())
            assert args and args[0] is bool, (
                f"skip_optimizer base type is not bool, got {ann}"
            )
        else:
            assert False, f"skip_optimizer is not bool, got {ann}"


# [pr_diff] fail_to_pass
def test_config_default_false():
    """skip_optimizer must default to False so existing behavior is preserved."""
    Cfg = _load_checkpoint_config()
    assert Cfg is not None, "CheckpointConfig not found"

    cfg = Cfg()
    assert hasattr(cfg, "skip_optimizer"), "no skip_optimizer attr on instance"
    assert cfg.skip_optimizer is False, (
        f"default is {cfg.skip_optimizer}, expected False"
    )


# [pr_diff] fail_to_pass
def test_config_accepts_true_and_roundtrips():
    """CheckpointConfig(skip_optimizer=True) must work and round-trip through model_dump."""
    Cfg = _load_checkpoint_config()
    assert Cfg is not None, "CheckpointConfig not found"

    # True round-trip
    cfg_true = Cfg(skip_optimizer=True)
    assert cfg_true.skip_optimizer is True
    dumped = cfg_true.model_dump()
    assert dumped.get("skip_optimizer") is True
    cfg_rt = Cfg(**dumped)
    assert cfg_rt.skip_optimizer is True

    # False round-trip (explicit)
    cfg_false = Cfg(skip_optimizer=False)
    assert cfg_false.skip_optimizer is False
    dumped_f = cfg_false.model_dump()
    assert dumped_f.get("skip_optimizer") is False
    cfg_rt_f = Cfg(**dumped_f)
    assert cfg_rt_f.skip_optimizer is False

    # JSON round-trip
    json_str = cfg_true.model_dump_json()
    cfg_json = Cfg.model_validate_json(json_str)
    assert cfg_json.skip_optimizer is True


# [pr_diff] fail_to_pass
def test_config_consistent_with_siblings():
    """skip_optimizer follows same pattern as skip_progress, skip_scheduler, skip_dataloader."""
    Cfg = _load_checkpoint_config()
    assert Cfg is not None, "CheckpointConfig not found"

    skip_fields = [
        "skip_progress", "skip_scheduler", "skip_dataloader", "skip_optimizer",
    ]
    cfg_default = Cfg()
    for fname in skip_fields:
        assert fname in Cfg.model_fields, f"{fname} missing from CheckpointConfig"
        assert getattr(cfg_default, fname) is False, f"{fname} default is not False"

    # All True at once
    cfg_all = Cfg(**{f: True for f in skip_fields})
    for fname in skip_fields:
        assert getattr(cfg_all, fname) is True, f"{fname} not True after setting"

    # Each field independently settable
    for target in skip_fields:
        cfg = Cfg(**{target: True})
        for fname in skip_fields:
            expected = fname == target
            assert getattr(cfg, fname) is expected, (
                f"Setting only {target}=True: {fname} should be {expected}"
            )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - ckpt.py behavioral change
# AST-only because: load_from_path requires torch.distributed (dcp_load,
# AppState, get_world) - cannot call on CPU.
# ---------------------------------------------------------------------------

def _is_empty_collection(node):
    """Check if AST node is an empty collection: [], (), or list()."""
    if isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) == 0:
        return True
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == "list" and not node.args:
            return True
    return False


def _has_skip_optimizer_ref(node):
    """Check if any descendant references .skip_optimizer attribute."""
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and n.attr == "skip_optimizer":
            return True
    return False


def _subtree_has_empty_collection(node):
    """Walk subtree for any empty collection node."""
    for n in ast.walk(node):
        if _is_empty_collection(n):
            return True
    return False


# [pr_diff] fail_to_pass
def test_ckpt_conditional_skip():
    """load_from_path must conditionally pass empty optimizers when skip_optimizer is set."""
    src = Path(CKPT_PY).read_text()
    tree = ast.parse(src)

    # Find load_from_path
    load_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "load_from_path":
            load_func = node
            break
    assert load_func is not None, "load_from_path not found in ckpt.py"

    # Must reference skip_optimizer somewhere in the function
    assert _has_skip_optimizer_ref(load_func), (
        "load_from_path does not reference skip_optimizer"
    )

    # Must have a conditional (IfExp or If) that:
    #   1. Tests skip_optimizer
    #   2. Contains an empty collection ([] or list()) in one branch
    found = False
    for child in ast.walk(load_func):
        if isinstance(child, ast.IfExp):
            if _has_skip_optimizer_ref(child.test):
                if _subtree_has_empty_collection(child.body) or \
                   _subtree_has_empty_collection(child.orelse):
                    found = True
                    break
        elif isinstance(child, ast.If):
            if _has_skip_optimizer_ref(child.test):
                if _subtree_has_empty_collection(child):
                    found = True
                    break

    if not found:
        # Fallback: check source text for pattern like "[] if ... skip_optimizer"
        # or "if ... skip_optimizer ... = []"
        func_src = ast.get_source_segment(src, load_func) or ""
        has_conditional = ("skip_optimizer" in func_src and
                          ("[]" in func_src or "list()" in func_src))
        assert has_conditional, (
            "load_from_path has no conditional skip_optimizer logic with empty optimizers list"
        )


# [pr_diff] fail_to_pass
def test_ckpt_stores_skip_optimizer():
    """CheckpointManager.__init__ must store skip_optimizer from config.

    # AST-only because: __init__ requires torch.distributed (get_world, get_logger)
    """
    src = Path(CKPT_PY).read_text()
    tree = ast.parse(src)

    # Find CheckpointManager class
    cm_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CheckpointManager":
            cm_class = node
            break
    assert cm_class is not None, "CheckpointManager class not found"

    # Find __init__ method
    init_func = None
    for node in cm_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            init_func = node
            break
    assert init_func is not None, "CheckpointManager.__init__ not found"

    # Must store skip_optimizer (self.skip_optimizer = ... or self.config used later)
    stores_skip = False
    for node in ast.walk(init_func):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "skip_optimizer":
                    stores_skip = True
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Attribute) and node.target.attr == "skip_optimizer":
                stores_skip = True

    # Also accept if config is stored and skip_optimizer is accessed via self.config later
    if not stores_skip:
        stores_config = False
        for node in ast.walk(init_func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and target.attr == "config":
                        stores_config = True
        if stores_config and _has_skip_optimizer_ref(cm_class):
            stores_skip = True

    assert stores_skip, (
        "CheckpointManager.__init__ does not store skip_optimizer from config"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_fields_work():
    """Existing CheckpointConfig fields unchanged after adding skip_optimizer."""
    Cfg = _load_checkpoint_config()
    assert Cfg is not None, "CheckpointConfig not found"

    cfg = Cfg(skip_progress=True, skip_scheduler=True, skip_dataloader=True)
    assert cfg.skip_progress is True, "skip_progress broken"
    assert cfg.skip_scheduler is True, "skip_scheduler broken"
    assert cfg.skip_dataloader is True, "skip_dataloader broken"

    cfg2 = Cfg(interval=5, keep_last=3)
    assert cfg2.interval == 5, "interval field broken"
    assert cfg2.keep_last == 3, "keep_last field broken"


# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be stubbed out."""
    checks = [
        (CONFIG_PY, 50, ["CheckpointConfig", "skip_progress", "skip_scheduler"]),
        (CKPT_PY, 50, ["CheckpointManager", "load_from_path", "AppState"]),
    ]
    for fpath, min_lines, must_contain in checks:
        content = Path(fpath).read_text()
        lines = [l for l in content.strip().split("\n") if l.strip()]
        assert len(lines) >= min_lines, (
            f"{fpath} has only {len(lines)} non-blank lines (stubbed)"
        )
        for token in must_contain:
            assert token in content, f"{fpath} missing {token} (stubbed)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - AGENTS.md:5 @ d8030652042f38a019beffecd8aa5e07cfefe4c4
def test_no_try_except_in_config():
    """Avoid try/except blocks unless really necessary (AGENTS.md:5)."""
    src = Path(CONFIG_PY).read_text()
    tree = ast.parse(src)
    try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    assert try_count == 0, f"trainer.py has {try_count} try/except blocks"
