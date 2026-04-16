"""
Task: areal-megatron-tree-training-scope
Repo: AReaL @ 933218365af85d5488a554367d9fbe5071442b49
PR:   1135

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path
from unittest import mock

REPO = "/workspace/AReaL"
TARGET = "areal/engine/megatron_engine.py"


def _ensure_ruff():
    """Ensure ruff is installed for repo CI/CD checks."""
    try:
        subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
            timeout=30,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--break-system-packages", "ruff"],
            capture_output=True,
            timeout=120,
            check=True,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must parse without errors."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_tree_training_scope_behavior():
    """Verify that make_mcore_model executes within the patch_bridge_for_tree_training context.
    
    This test verifies behavior by:
    1. Attempting to instrument and execute the module with mocks
    2. Falling back to AST control-flow analysis if execution fails
    
    The behavioral requirement is: when enable_tree_training=True and bridge_type="mbridge",
    the make_mcore_model() call must be inside the patch_bridge_for_tree_training context.
    """
    # First try: instrumented execution
    if _try_instrumented_execution():
        return
    
    # Second try: AST-based control flow verification
    _verify_control_flow_behavior()


def _try_instrumented_execution():
    """Try to execute the code with instrumentation. Returns True if successful."""
    context_stack = []
    make_mcore_calls = []
    
    class SpyContextManager:
        def __init__(self, name):
            self.name = name
        def __call__(self, *args, **kwargs):
            return self
        def __enter__(self):
            context_stack.append(self.name)
            return self
        def __exit__(self, *args):
            if context_stack and context_stack[-1] == self.name:
                context_stack.pop()
            return False
    
    def tracked_make_mcore(*args, **kwargs):
        current_context = context_stack[-1] if context_stack else None
        make_mcore_calls.append(current_context)
        return []
    
    # Pre-populate mocks before any imports
    megatron_mock = mock.MagicMock()
    megatron_mock.core = mock.MagicMock()
    megatron_mock.core.parallel_state = mock.MagicMock()
    megatron_mock.core.tensor_parallel = mock.MagicMock()
    megatron_mock.bridge = mock.MagicMock()
    megatron_mock.core.distributed = mock.MagicMock()
    megatron_mock.core.distributed.DistributedDataParallel = mock.MagicMock()
    megatron_mock.core.distributed.finalize_model_grads = mock.MagicMock()
    megatron_mock.core.optimizer = mock.MagicMock()
    megatron_mock.core.transformer = mock.MagicMock()
    megatron_mock.core.utils = mock.MagicMock()
    megatron_mock.core.pipeline_parallel = mock.MagicMock()
    
    sys.modules["megatron"] = megatron_mock
    sys.modules["megatron.core"] = megatron_mock.core
    sys.modules["megatron.bridge"] = megatron_mock.bridge
    sys.modules["megatron.core.parallel_state"] = megatron_mock.core.parallel_state
    sys.modules["megatron.core.tensor_parallel"] = megatron_mock.core.tensor_parallel
    sys.modules["megatron.core.distributed"] = megatron_mock.core.distributed
    sys.modules["megatron.core.optimizer"] = megatron_mock.core.optimizer
    sys.modules["megatron.core.transformer"] = megatron_mock.core.transformer
    sys.modules["megatron.core.utils"] = megatron_mock.core.utils
    sys.modules["megatron.core.pipeline_parallel"] = megatron_mock.core.pipeline_parallel
    
    sys.modules["mbridge"] = mock.MagicMock()
    
    torch_mock = mock.MagicMock()
    torch_mock.device = mock.MagicMock(return_value=mock.MagicMock())
    torch_mock.distributed = mock.MagicMock()
    torch_mock.distributed.is_initialized = mock.MagicMock(return_value=True)
    sys.modules["torch"] = torch_mock
    sys.modules["torch.distributed"] = torch_mock.distributed
    
    sys.modules["torchdata"] = mock.MagicMock()
    sys.modules["torchdata.stateful_dataloader"] = mock.MagicMock()
    sys.modules["transformers"] = mock.MagicMock()
    
    # Tree attn with spy
    tree_mock = mock.MagicMock()
    tree_mock.patch_bridge_for_tree_training = SpyContextManager("patch_bridge_for_tree_training")
    for attr in ['build_tree_attn_kwargs', '_gather_packed_tree_logprobs', 
                 'gather_packed_tree_logprobs_entropy', 'gather_packed_tree_vocab_stats',
                 'merge_packed_tree_results']:
        setattr(tree_mock, attr, mock.MagicMock())
    
    for mod_name in ['areal.models.tree_attn', 'areal.models.tree_attn.module',
                     'areal.models.tree_attn.functional', 'areal.models.tree_attn.tree']:
        sys.modules[mod_name] = tree_mock
    
    # Areal mocks
    areal_mock = mock.MagicMock()
    registry_mock = mock.MagicMock()
    registry_mock.make_mcore_model = tracked_make_mcore
    registry_mock.make_hf_and_mcore_config = mock.MagicMock(return_value=(mock.MagicMock(), mock.MagicMock()))
    
    for mod_path in ['areal', 'areal.models', 'areal.models.mcore', 
                     'areal.models.mcore.registry', 'areal.models.mcore.hf_load',
                     'areal.models.mcore.hf_save']:
        sys.modules[mod_path] = areal_mock if mod_path == 'areal' else mock.MagicMock()
    
    sys.modules["areal.models.mcore.registry"] = registry_mock
    
    # Other mocks
    for mod_base in ['areal.engine', 'areal.engine.core', 'areal.engine.megatron_utils',
                     'areal.infra', 'areal.utils', 'areal.api']:
        sys.modules[mod_base] = mock.MagicMock()
        for sub in ['distributed', 'model', 'checkpointer', 'deterministic', 'fp8',
                    'megatron', 'packed_context_parallel', 'pipeline_parallel',
                    'dist_rollout', 'platforms', 'constants', 'data', 'functional',
                    'hf_utils', 'lock', 'logging', 'name_resolve', 'cli_args', 'io_struct']:
            sys.modules[f"{mod_base}.{sub}"] = mock.MagicMock()
    
    sys.modules["areal.api"].InferenceEngine = object
    sys.modules["areal.api"].TrainEngine = object
    
    import os
    orig_env = {k: os.environ.get(k) for k in ["LOCAL_RANK", "RANK", "WORLD_SIZE"]}
    os.environ.update({"LOCAL_RANK": "0", "RANK": "0", "WORLD_SIZE": "1"})
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("megatron_engine", f"{REPO}/{TARGET}")
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
        except Exception:
            return False  # Fall back to AST
        
        MegatronEngine = getattr(module, "MegatronEngine", None)
        if not MegatronEngine:
            return False
        
        engine = mock.MagicMock()
        engine.config = mock.MagicMock()
        engine.config.enable_tree_training = True
        engine.config.path = "test"
        engine.config.is_critic = False
        engine.mcore_config = mock.MagicMock()
        engine.mcore_config.bridge_type = "mbridge"
        engine.mcore_config.fp8_config = None
        engine.dtype = "bf16"
        engine.parallel_strategy = mock.MagicMock()
        for attr in ['tensor_parallel_size', 'pipeline_parallel_size', 
                     'virtual_pipeline_parallel_size', 'context_parallel_size',
                     'expert_parallel_size', 'expert_tensor_parallel_size']:
            setattr(engine.parallel_strategy, attr, 1)
        
        try:
            MegatronEngine.initialize(engine, None, mock.MagicMock())
        except Exception:
            pass
        
        if make_mcore_calls:
            assert all(c == "patch_bridge_for_tree_training" for c in make_mcore_calls), (
                f"make_mcore_model called outside tree training context. Contexts: {make_mcore_calls}"
            )
            return True
        return False
    finally:
        for k, v in orig_env.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)


def _verify_control_flow_behavior():
    """Verify control flow structure supports correct behavior using AST.
    
    This is behavioral because we verify the control flow enables the correct
    runtime behavior (make_mcore_model inside tree context), not just text.
    """
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)
    
    # Find initialize method
    init_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "initialize":
                    init_method = item
                    break
            if init_method:
                break
    
    assert init_method is not None, "initialize method not found"
    
    # Find patch_bridge_for_tree_training block
    tree_ctx_block = None
    for stmt in init_method.body:
        if isinstance(stmt, ast.With):
            for item in stmt.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call):
                    func = ctx.func
                    name = getattr(func, "id", None) or getattr(func, "attr", None)
                    if name == "patch_bridge_for_tree_training":
                        tree_ctx_block = stmt
                        break
    
    assert tree_ctx_block is not None, "patch_bridge_for_tree_training context not found"
    
    # Check if make_mcore_model is in tree context (directly or in nested with self.device)
    def find_mcore_calls(node):
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                name = getattr(func, "id", None) or getattr(func, "attr", None)
                if name == "make_mcore_model":
                    calls.append(child)
        return calls
    
    mcore_calls_in_tree = find_mcore_calls(tree_ctx_block)
    
    # Check for nested with self.device inside tree context
    for stmt in tree_ctx_block.body:
        if isinstance(stmt, ast.With):
            for item in stmt.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Attribute) and ctx.attr == "device":
                    mcore_calls_in_tree.extend(find_mcore_calls(stmt))
    
    # Verify no make_mcore_model at direct body level (outside tree context)
    for stmt in init_method.body:
        if isinstance(stmt, ast.With) and stmt is not tree_ctx_block:
            for item in stmt.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Attribute) and ctx.attr == "device":
                    if find_mcore_calls(stmt):
                        raise AssertionError(
                            "Bug: make_mcore_model called at body level inside 'with self.device'. "
                            "Should be nested inside patch_bridge_for_tree_training context."
                        )
    
    assert mcore_calls_in_tree, (
        "No make_mcore_model calls found inside patch_bridge_for_tree_training context. "
        "The control flow does not support correct tree training behavior."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_initialize_not_stub():
    """The initialize method must contain real logic, not just pass/return."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "initialize":
                body = [
                    s for s in item.body
                    if not isinstance(s, (ast.Pass, ast.Expr))
                    or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                ]
                assert len(body) >= 10, (
                    f"initialize() body has only {len(body)} meaningful statements — "
                    "expected substantial logic, not a stub"
                )
                return

    assert False, "initialize method not found in any class"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

def test_no_wildcard_imports():
    """Modified file must not use wildcard imports (CLAUDE.md: Never use wildcard imports)."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    wildcards = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    wildcards.append(f"from {node.module} import *")

    assert not wildcards, f"Wildcard imports found: {wildcards}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

def test_repo_ruff_lint():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on modified file (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}{r.stderr}"


def test_repo_ruff_imports():
    """Repo's import sorting check passes on modified file (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "I", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff import check failed:\n{r.stdout}{r.stderr}"


# ---------------------------------------------------------------------------
# Pre-commit hook pass_to_pass gates
# ---------------------------------------------------------------------------

def _ensure_precommit():
    """Ensure pre-commit is installed for repo CI/CD checks."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pre_commit", "--version"],
            capture_output=True,
            timeout=30,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--break-system-packages", "pre-commit"],
            capture_output=True,
            timeout=120,
            check=True,
        )


def test_repo_trailing_whitespace():
    """Repo's trailing whitespace check passes on modified file (pass_to_pass)."""
    _ensure_precommit()
    precommit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
        files: \\.py$
"""
    config_path = "/tmp/trailing_ws_config.yaml"
    Path(config_path).write_text(precommit_config)
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "--config", config_path, 
         "trailing-whitespace", "--files", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stdout}{r.stderr}"


def test_repo_end_of_file():
    """Repo's end-of-file check passes on modified file (pass_to_pass)."""
    _ensure_precommit()
    precommit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
        files: \\.py$
"""
    config_path = "/tmp/eof_config.yaml"
    Path(config_path).write_text(precommit_config)
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "--config", config_path,
         "end-of-file-fixer", "--files", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"End-of-file check failed:\n{r.stdout}{r.stderr}"


def test_repo_no_private_keys():
    """Repo's private key detection check passes on modified file (pass_to_pass)."""
    _ensure_precommit()
    precommit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: detect-private-key
        files: \\.py$
"""
    config_path = "/tmp/private_key_config.yaml"
    Path(config_path).write_text(precommit_config)
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "--config", config_path,
         "detect-private-key", "--files", f"{REPO}/{TARGET}"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Private key detection check failed:\n{r.stdout}{r.stderr}"
