"""
Task: prime-rl-toml-none-str-removal
Repo: PrimeIntellect-ai/prime-rl @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
PR:   2095

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import tempfile
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

REPO = "/workspace/prime-rl"
CONFIG_PY = f"{REPO}/src/prime_rl/utils/config.py"
RL_PY = f"{REPO}/src/prime_rl/entrypoints/rl.py"
SFT_PY = f"{REPO}/src/prime_rl/entrypoints/sft.py"
INFERENCE_PY = f"{REPO}/src/prime_rl/entrypoints/inference.py"

ENTRYPOINTS = {"rl.py": RL_PY, "sft.py": SFT_PY, "inference.py": INFERENCE_PY}


# ---------------------------------------------------------------------------
# Helpers — AST-extract write_config/write_subconfigs and exec with mocks
# AST-only because: entrypoints import torch/vllm which aren't installed
# ---------------------------------------------------------------------------

def _extract_function(source_path: str, func_name: str) -> str | None:
    """Extract a function's source from a file by name."""
    src = Path(source_path).read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return "".join(src.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])
    return None


def _extract_module_constants(source_path: str) -> dict:
    """Extract top-level string constant assignments (e.g. RL_TOML = 'rl.toml')."""
    src = Path(source_path).read_text()
    tree = ast.parse(src)
    constants = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                constants[target.id] = node.value.value
    return constants


def _get_config_helpers() -> dict:
    """Extract old helper functions from config.py if they still exist (for base-commit compat)."""
    src = Path(CONFIG_PY).read_text()
    tree = ast.parse(src)
    helpers = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("none_to_none_str", "_convert_none"):
            func_src = "".join(src.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])
            exec(func_src, helpers)
    return {k: v for k, v in helpers.items() if callable(v)}


def _build_exec_namespace(source_path: str) -> dict:
    """Build a namespace for executing extracted functions from an entrypoint."""
    import tomli_w

    constants = _extract_module_constants(source_path)
    helpers = _get_config_helpers()

    ns = {
        "tomli_w": tomli_w,
        "Path": Path,
        "set": set,
        "__builtins__": __builtins__,
    }
    ns.update(constants)
    for name in ("SFTConfig", "RLConfig", "InferenceConfig"):
        ns[name] = BaseModel
    ns.update(helpers)
    return ns


def _call_write_config(entrypoint_path: str, config_obj) -> str:
    """Extract write_config, exec it, call with config_obj, return TOML content."""
    func_src = _extract_function(entrypoint_path, "write_config")
    assert func_src is not None, f"write_config not found in {entrypoint_path}"

    ns = _build_exec_namespace(entrypoint_path)
    exec(func_src, ns)
    write_config_fn = ns["write_config"]

    tmpdir = tempfile.mkdtemp()
    config_path = Path(tmpdir) / "config.toml"

    # sft.py takes (config, config_path, exclude); rl.py/inference.py take (config, output_dir, exclude)
    if "sft" in entrypoint_path:
        write_config_fn(config_obj, config_path)
    else:
        write_config_fn(config_obj, Path(tmpdir))

    toml_files = list(Path(tmpdir).glob("*.toml"))
    assert len(toml_files) >= 1, f"No TOML file written by write_config in {entrypoint_path}"
    return toml_files[0].read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without errors."""
    # AST-only because: entrypoints can't be imported (torch/vllm deps)
    for path in [CONFIG_PY, RL_PY, SFT_PY, INFERENCE_PY]:
        src = Path(path).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_none_helpers_removed():
    """none_to_none_str and _convert_none must be removed from config.py."""
    # AST-only because: checking function definition existence
    src = Path(CONFIG_PY).read_text()
    tree = ast.parse(src)
    defined = [
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, ast.FunctionDef) and node.name in ("none_to_none_str", "_convert_none")
    ]
    assert not defined, f"Helper functions still defined: {defined}"


# [pr_diff] fail_to_pass
def test_entrypoints_no_import_none_helper():
    """No entrypoint may import or call none_to_none_str."""
    # AST-only because: entrypoints can't be imported (torch/vllm deps)
    for name, path in ENTRYPOINTS.items():
        src = Path(path).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "none_to_none_str", f"{name} still imports none_to_none_str"
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    assert func.id != "none_to_none_str", f"{name} still calls none_to_none_str()"
                if isinstance(func, ast.Attribute):
                    assert func.attr != "none_to_none_str", f"{name} still calls .none_to_none_str()"


# [pr_diff] fail_to_pass
def test_sft_write_config_excludes_none():
    """SFT write_config must omit None-valued fields from TOML output."""

    class SubModel(BaseModel):
        enabled: bool = True
        threshold: Optional[float] = None

    class TestConfig(BaseModel):
        name: str = "experiment"
        batch_size: int = 64
        learning_rate: Optional[float] = None
        warmup_steps: Optional[int] = None
        sub: SubModel = SubModel()

    content = _call_write_config(SFT_PY, TestConfig())

    assert "learning_rate" not in content, f"None-valued 'learning_rate' in TOML:\n{content}"
    assert "warmup_steps" not in content, f"None-valued 'warmup_steps' in TOML:\n{content}"
    assert "threshold" not in content, f"Nested None 'threshold' in TOML:\n{content}"
    assert '"None"' not in content, f"TOML contains '\"None\"' strings:\n{content}"
    assert "name" in content, "Non-None 'name' missing from TOML"
    assert "batch_size" in content, "Non-None 'batch_size' missing from TOML"
    assert "enabled" in content, "Nested non-None 'enabled' missing from TOML"


# [pr_diff] fail_to_pass
def test_rl_write_config_excludes_none():
    """RL write_config must omit None-valued fields from TOML output."""

    class TestConfig(BaseModel):
        run_name: str = "test-run"
        gradient_accumulation: int = 4
        max_grad_norm: Optional[float] = None
        scheduler_type: Optional[str] = None

    content = _call_write_config(RL_PY, TestConfig())

    assert "max_grad_norm" not in content, f"None-valued 'max_grad_norm' in TOML:\n{content}"
    assert "scheduler_type" not in content, f"None-valued 'scheduler_type' in TOML:\n{content}"
    assert '"None"' not in content, f"TOML contains '\"None\"' strings:\n{content}"
    assert "run_name" in content, "Non-None 'run_name' missing from TOML"
    assert "gradient_accumulation" in content, "Non-None 'gradient_accumulation' missing"


# [pr_diff] fail_to_pass
def test_inference_write_config_excludes_none():
    """Inference write_config must omit None-valued fields from TOML output."""

    class TestConfig(BaseModel):
        model_name: str = "test-model"
        max_tokens: int = 2048
        temperature: Optional[float] = None
        stop_sequence: Optional[str] = None

    content = _call_write_config(INFERENCE_PY, TestConfig())

    assert "temperature" not in content, f"None-valued 'temperature' in TOML:\n{content}"
    assert "stop_sequence" not in content, f"None-valued 'stop_sequence' in TOML:\n{content}"
    assert '"None"' not in content, f"TOML contains '\"None\"' strings:\n{content}"
    assert "model_name" in content, "Non-None 'model_name' missing from TOML"
    assert "max_tokens" in content, "Non-None 'max_tokens' missing from TOML"


# [pr_diff] fail_to_pass
def test_rl_write_subconfigs_excludes_none():
    """RL write_subconfigs must omit None-valued fields from all sub-config TOML files."""
    import tomli_w

    func_src = _extract_function(RL_PY, "write_subconfigs")
    assert func_src is not None, "write_subconfigs not found in rl.py"

    ns = _build_exec_namespace(RL_PY)

    class SubConfig(BaseModel):
        lr: float = 0.001
        warmup: Optional[int] = None
        decay: Optional[float] = None

    class TestConfig(BaseModel):
        trainer: SubConfig = SubConfig()
        orchestrator: SubConfig = SubConfig(lr=0.01)
        inference: Optional[SubConfig] = SubConfig(lr=0.05)

    exec(func_src, ns)
    write_subconfigs_fn = ns["write_subconfigs"]

    tmpdir = tempfile.mkdtemp()
    write_subconfigs_fn(TestConfig(), Path(tmpdir))

    toml_files = list(Path(tmpdir).glob("*.toml"))
    assert len(toml_files) >= 2, f"Expected >=2 TOML files, got {len(toml_files)}"

    for f in toml_files:
        content = f.read_text()
        assert '"None"' not in content, f"{f.name} contains '\"None\"' strings:\n{content}"
        assert "warmup" not in content, f"{f.name} has None-valued 'warmup':\n{content}"
        assert "decay" not in content, f"{f.name} has None-valued 'decay':\n{content}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_get_all_fields_preserved():
    """get_all_fields in config.py must still work correctly."""
    # AST-only because: config.py imports pydantic_config which isn't installed
    src = Path(CONFIG_PY).read_text()
    func_src = _extract_function(CONFIG_PY, "get_all_fields")
    assert func_src is not None, "get_all_fields not found in config.py"

    ns = {"BaseModel": BaseModel, "__builtins__": __builtins__}
    exec(func_src, ns)
    get_all_fields = ns["get_all_fields"]

    class MyModel(BaseModel):
        name: str = "test"
        value: int = 42
        optional: Optional[float] = None

    fields_cls = get_all_fields(MyModel)
    assert "name" in fields_cls and "value" in fields_cls, f"get_all_fields(class) = {fields_cls}"

    fields_inst = get_all_fields(MyModel())
    assert "name" in fields_inst and "value" in fields_inst, f"get_all_fields(instance) = {fields_inst}"


# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be stubbed out — write_config and tomli_w.dump must exist."""
    for name, path in ENTRYPOINTS.items():
        src = Path(path).read_text()
        assert "def write_config" in src, f"{name} missing write_config function"
        assert "tomli_w.dump" in src, f"{name} missing tomli_w.dump call"

    config_lines = [l for l in Path(CONFIG_PY).read_text().strip().split("\n") if l.strip()]
    assert len(config_lines) >= 5, f"config.py has only {len(config_lines)} non-blank lines (stubbed)"

    rl_src = Path(RL_PY).read_text()
    assert "def write_subconfigs" in rl_src, "rl.py missing write_subconfigs"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
def test_config_no_try_except():
    """config.py must not have try/except blocks (AGENTS.md: 'Avoid try/except unless really necessary')."""
    # AST-only because: checking for try/except presence, not behavior
    src = Path(CONFIG_PY).read_text()
    tree = ast.parse(src)
    try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    assert try_count == 0, f"config.py has {try_count} try/except blocks"


# [agent_config] pass_to_pass — AGENTS.md:54 @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
def test_no_class_based_tests_in_modified_files():
    """Modified files must not introduce class-based test patterns (AGENTS.md: 'Write tests as plain functions with pytest fixtures')."""
    # AST-only because: checking structural pattern in files that can't be imported
    for path in [CONFIG_PY, RL_PY, SFT_PY, INFERENCE_PY]:
        src = Path(path).read_text()
        tree = ast.parse(src)
        test_classes = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
        ]
        assert not test_classes, f"{Path(path).name} has class-based test pattern: {test_classes}"
