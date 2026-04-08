"""
Task: vllm-sliding-window-zero-config
Repo: vllm-project/vllm @ 7b54f60db0f55d74dac8aa3040c02363b7a9f6ec

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests use subprocess to execute extracted ModelConfig code
against mock objects — the real logic from model.py runs in isolation.
"""

import ast
import json
import subprocess
from pathlib import Path

TARGET = "/workspace/vllm/vllm/config/model.py"

# Script executed in subprocess. Parses ModelConfig from source, creates a
# mock with the given sliding_window, binds extracted methods, runs
# __post_init__ statement-by-statement, outputs results as JSON.
_BEHAVIORAL_SCRIPT = r"""
import ast, json, textwrap, warnings, os, logging
from pathlib import Path

TARGET = "{target}"
SW_VAL = {sw_val}

class HFConfig:
    def __init__(self, sw):
        self.sliding_window = sw
        self.max_position_embeddings = 32768
        self.model_type = "test"
        self.num_attention_heads = 32
        self.num_hidden_layers = 32
        self.hidden_size = 4096
    def __getattr__(self, name):
        return None

class MockConfig:
    def __init__(self, sw):
        self.disable_sliding_window = False
        self.hf_text_config = HFConfig(sw)
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

source = Path(TARGET).read_text()
tree = ast.parse(source)

mc = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        mc = node
        break
if mc is None:
    raise RuntimeError("ModelConfig class not found")

methods = {{}}
lines = source.splitlines(keepends=True)
for item in mc.body:
    if isinstance(item, ast.FunctionDef):
        func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
        methods[item.name] = func_src

post_init = None
for item in mc.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
        post_init = item
        break
if post_init is None:
    raise RuntimeError("__post_init__ not found")

obj = MockConfig(SW_VAL)

# Bind non-post_init methods onto mock's class
for mname, msrc in methods.items():
    if mname == "__post_init__":
        continue
    try:
        ns = {{"__builtins__": __builtins__}}
        exec(msrc, ns)
        if mname in ns and callable(ns[mname]):
            setattr(type(obj), mname, ns[mname])
    except Exception:
        pass

# Execute __post_init__ body statement-by-statement
shared_ns = {{
    "self": obj,
    "__builtins__": __builtins__,
    "warnings": warnings,
    "os": os,
    "logger": logging.getLogger("test"),
}}
for stmt in post_init.body:
    stmt_lines = lines[stmt.lineno - 1 : stmt.end_lineno]
    stmt_src = textwrap.dedent("".join(stmt_lines))
    try:
        exec(compile(stmt_src, "<post_init>", "exec"), shared_ns)
    except Exception:
        pass

sw_attr = obj.hf_text_config.sliding_window
try:
    sw_method = obj.get_sliding_window()
except Exception:
    sw_method = "ERROR"

result = {{
    "sliding_window_attr": sw_attr,
    "sliding_window_method": sw_method,
    "disable_sliding_window": obj.disable_sliding_window,
}}
print(json.dumps(result))
"""


def _run_behavioral(sw_val, timeout=30):
    """Run extracted ModelConfig code in a subprocess with the given sw value."""
    script = _BEHAVIORAL_SCRIPT.format(target=TARGET, sw_val=repr(sw_val))
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd="/workspace/vllm",
    )
    assert r.returncode == 0, f"Script failed (sw={sw_val!r}): {r.stderr}"
    return json.loads(r.stdout.strip().splitlines()[-1])


def _find_post_init_node(tree):
    """Return the AST node for ModelConfig.__post_init__."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    return item
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """vllm/config/model.py must parse without errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_sw_zero_converted_to_none():
    """sliding_window=0 must be treated as None (disabled)."""
    result = _run_behavioral(0)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
    assert (sw_attr is None) or (sw_method is None), (
        f"sliding_window=0 not converted: attr={sw_attr!r}, method={sw_method!r}"
    )


# [pr_diff] fail_to_pass
def test_sw_zero_sets_disable_flag():
    """disable_sliding_window must be True when sliding_window=0."""
    result = _run_behavioral(0)
    assert result["disable_sliding_window"] is True, (
        f"disable_sliding_window={result['disable_sliding_window']!r}, expected True"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: non-zero / None values preserved
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_sw_none_preserved():
    """sliding_window=None must remain None and not trigger disable."""
    result = _run_behavioral(None)
    assert result["sliding_window_attr"] is None, (
        f"sliding_window=None was modified to {result['sliding_window_attr']!r}"
    )
    assert result["disable_sliding_window"] is not True, (
        "disable_sliding_window incorrectly set for sliding_window=None"
    )


# [pr_diff] pass_to_pass
def test_sw_positive_preserved():
    """sliding_window=128 must be preserved (not zeroed or set to None)."""
    result = _run_behavioral(128)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
    assert (sw_attr == 128) or (sw_method == 128), (
        f"sliding_window=128 not preserved: attr={sw_attr!r}, method={sw_method!r}"
    )


# [pr_diff] pass_to_pass
def test_sw_large_positive_preserved():
    """sliding_window=4096 must be preserved."""
    result = _run_behavioral(4096)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
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

    meaningful = sum(
        1 for stmt in post_init.body
        if not isinstance(stmt, ast.Pass)
        and not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
    )
    assert meaningful >= 5, f"__post_init__ has only {meaningful} statements (stub?)"

    has_sw = False
    for node in ast.walk(post_init):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            seg = ast.get_source_segment(source, node)
            if seg and "sliding_window" in seg:
                has_sw = True
                break
    assert has_sw, "No assignment touching sliding_window in __post_init__"
