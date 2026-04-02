"""
Task: vllm-sliding-window-zero-config
Repo: vllm-project/vllm @ 7b54f60db0f55d74dac8aa3040c02363b7a9f6ec

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: vLLM cannot be imported directly (requires torch/GPU). Tests extract
ModelConfig methods via AST, bind them to mocks, and execute __post_init__
statement-by-statement. This tests end-state behavior, not code structure.
"""

import ast
import json
import logging
import os
import textwrap
import warnings
from pathlib import Path

TARGET = "/workspace/vllm/vllm/config/model.py"


def _extract_methods():
    """Parse ModelConfig and return {name: source} for all methods."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    mc = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            mc = node
            break
    assert mc is not None, "ModelConfig class not found in model.py"

    methods = {}
    lines = source.splitlines(keepends=True)
    for item in mc.body:
        if isinstance(item, ast.FunctionDef):
            func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
            methods[item.name] = func_src
    return methods, source, tree


def _find_post_init_node(tree):
    """Return the AST node for ModelConfig.__post_init__."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    return item
    return None


def _make_hf_config(sw):
    """Create a mock HF config with given sliding_window value."""
    class HFConfig:
        def __init__(self):
            self.sliding_window = sw
            self.max_position_embeddings = 32768
            self.model_type = "test"
            self.num_attention_heads = 32
            self.num_hidden_layers = 32
            self.hidden_size = 4096
        def __getattr__(self, name):
            return None
    return HFConfig()


def _make_mock(sw):
    """Create a mock ModelConfig-like object with sliding_window=sw."""
    class MockConfig:
        def __init__(self):
            self.disable_sliding_window = False
            self.hf_text_config = _make_hf_config(sw)
            self.max_model_len = None
            self.model = "test-model"
            self.tokenizer = "test-model"
            self.tokenizer_mode = "auto"
            self.trust_remote_code = False
            self.dtype = "auto"
            self.seed = 0
            self.revision = None
            self.code_revision = None
            self.quantization = None
            self.enforce_eager = False
            self.max_logprobs = 5
            self.served_model_name = None
            self.rope_scaling = None
            self.rope_theta = None
            self.config_format = "auto"
            self.hf_config_path = None
            self.generation_config = None
            self.override_neuron_config = None
            self.override_pooler_config = None
            self.logits_processor_pattern = None
            self.task = "auto"
            self.skip_tokenizer_init = False
            self.allowed_local_media_path = ""
        def __getattr__(self, name):
            return None
    return MockConfig()


def _bind_methods(obj, methods):
    """Bind extracted methods (except __post_init__) to mock's class."""
    for mname, msrc in methods.items():
        if mname == "__post_init__":
            continue
        try:
            ns = {"__builtins__": __builtins__}
            exec(msrc, ns)
            if mname in ns and callable(ns[mname]):
                setattr(type(obj), mname, ns[mname])
        except Exception:
            pass


def _run_post_init(obj, source, post_init_node):
    """Execute __post_init__ body statement-by-statement with error tolerance."""
    lines = source.splitlines(keepends=True)
    shared_ns = {
        "self": obj,
        "__builtins__": __builtins__,
        "warnings": warnings,
        "os": os,
        "logger": logging.getLogger("test"),
    }
    for stmt in post_init_node.body:
        stmt_lines = lines[stmt.lineno - 1 : stmt.end_lineno]
        stmt_src = textwrap.dedent("".join(stmt_lines))
        try:
            exec(compile(stmt_src, "<post_init>", "exec"), shared_ns)
        except Exception:
            pass


def _get_sw(obj):
    """Get sliding_window via method or attribute — accepts any fix approach."""
    try:
        return obj.get_sliding_window()
    except Exception:
        return getattr(obj.hf_text_config, "sliding_window", "ERROR")


def _run_with_sw(sw):
    """Build mock with given sw, run __post_init__, return the mock."""
    methods, source, tree = _extract_methods()
    post_init_node = _find_post_init_node(tree)
    assert post_init_node is not None, "__post_init__ not found"
    obj = _make_mock(sw)
    _bind_methods(obj, methods)
    _run_post_init(obj, source, post_init_node)
    return obj


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """vllm/config/model.py must parse without errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)  # raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sw_zero_converted_to_none():
    """sliding_window=0 must be treated as None (disabled)."""
    obj = _run_with_sw(0)
    sw_attr = obj.hf_text_config.sliding_window
    sw_method = _get_sw(obj)
    assert (sw_attr is None) or (sw_method is None), (
        f"sliding_window=0 not converted: attr={sw_attr!r}, method={sw_method!r}"
    )


# [pr_diff] fail_to_pass
def test_sw_zero_sets_disable_flag():
    """disable_sliding_window must be True when sliding_window=0."""
    obj = _run_with_sw(0)
    assert obj.disable_sliding_window is True, (
        f"disable_sliding_window={obj.disable_sliding_window!r}, expected True"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: non-zero / None values preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sw_none_preserved():
    """sliding_window=None must remain None and not trigger disable."""
    obj = _run_with_sw(None)
    assert obj.hf_text_config.sliding_window is None, (
        f"sliding_window=None was modified to {obj.hf_text_config.sliding_window!r}"
    )
    assert obj.disable_sliding_window is not True, (
        "disable_sliding_window incorrectly set for sliding_window=None"
    )


# [pr_diff] pass_to_pass
def test_sw_positive_preserved():
    """sliding_window=128 must be preserved (not zeroed or set to None)."""
    obj = _run_with_sw(128)
    sw_attr = obj.hf_text_config.sliding_window
    sw_method = _get_sw(obj)
    assert (sw_attr == 128) or (sw_method == 128), (
        f"sliding_window=128 not preserved: attr={sw_attr!r}, method={sw_method!r}"
    )


# [pr_diff] pass_to_pass
def test_sw_large_positive_preserved():
    """sliding_window=4096 must be preserved."""
    obj = _run_with_sw(4096)
    sw_attr = obj.hf_text_config.sliding_window
    sw_method = _get_sw(obj)
    assert (sw_attr == 4096) or (sw_method == 4096), (
        f"sliding_window=4096 not preserved: attr={sw_attr!r}, method={sw_method!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_model_config_methods_preserved():
    """ModelConfig must still have get_sliding_window, get_and_verify_max_len, __post_init__."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    expected = {"get_sliding_window", "get_and_verify_max_len", "__post_init__"}
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in expected:
                    found.add(item.name)
            break
    missing = expected - found
    assert not missing, f"ModelConfig missing methods: {missing}"


# [static] pass_to_pass
def test_not_stub():
    """__post_init__ must have real logic and a sliding_window assignment."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    post_init = _find_post_init_node(tree)
    assert post_init is not None, "__post_init__ not found"

    # Must have substantial logic (original has 40+ statements)
    meaningful = sum(
        1 for stmt in post_init.body
        if not isinstance(stmt, ast.Pass)
        and not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
    )
    assert meaningful >= 5, f"__post_init__ has only {meaningful} statements (stub?)"

    # Must have at least one assignment touching sliding_window
    has_sw = False
    for node in ast.walk(post_init):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            seg = ast.get_source_segment(source, node)
            if seg and "sliding_window" in seg:
                has_sw = True
                break
    assert has_sw, "No assignment touching sliding_window in __post_init__"
