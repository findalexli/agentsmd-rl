"""
Task: vllm-sliding-window-zero-config
Repo: vllm-project/vllm @ 7b54f60db0f55d74dac8aa3040c02363b7a9f6ec

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests use subprocess to execute actual ModelConfig code
against mock objects.
"""

import ast
import json
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/config/model.py"


def _exec_in_repo(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the vllm repo."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# -----------------------------------------------------------------------------


def test_syntax_check():
    """vllm/config/model.py must parse without errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# -----------------------------------------------------------------------------
# Helper: extract and run ModelConfig logic with a mock
# -----------------------------------------------------------------------------

def _test_sw_behavior(sw_val):
    """
    Run ModelConfig.__post_init__ with a mock hf_text_config having
    the given sliding_window value, and return the state after execution.
    """
    sw_repr = repr(sw_val)
    code = f'''
import ast, json, textwrap, warnings, os, logging, sys
from pathlib import Path

TARGET = "{TARGET}"
SW_VAL = {sw_repr}

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

source = Path(TARGET).read_text()
tree = ast.parse(source)

# Find ModelConfig class
mc = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        mc = node
        break
if mc is None:
    print(json.dumps({{"error": "ModelConfig not found"}}))
    sys.exit(1)

# Extract all methods from ModelConfig
lines = source.splitlines(keepends=True)
methods = {{}}
for item in mc.body:
    if isinstance(item, ast.FunctionDef):
        func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
        methods[item.name] = func_src

# Find __post_init__
post_init_node = None
for item in mc.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
        post_init_node = item
        break
if post_init_node is None:
    print(json.dumps({{"error": "__post_init__ not found"}}))
    sys.exit(1)

# Create mock instance
obj = MockConfig(SW_VAL)

# Bind non-post_init methods to the mock class
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

# Execute __post_init__ statement by statement
shared_ns = {{
    "self": obj,
    "__builtins__": __builtins__,
    "warnings": warnings,
    "os": os,
    "logger": logging.getLogger("test"),
}}
for stmt in post_init_node.body:
    stmt_lines = lines[stmt.lineno - 1 : stmt.end_lineno]
    stmt_src = textwrap.dedent("".join(stmt_lines))
    try:
        exec(compile(stmt_src, "<post_init>", "exec"), shared_ns)
    except Exception:
        pass

# Get results
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
'''
    r = _exec_in_repo(code, timeout=30)
    assert r.returncode == 0, f"Script failed (sw={sw_repr}): {r.stderr}"
    last_line = r.stdout.strip().splitlines()[-1]
    return json.loads(last_line)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------


def test_sw_zero_converted_to_none():
    """sliding_window=0 must be treated as None (disabled)."""
    result = _test_sw_behavior(0)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
    assert (sw_attr is None) or (sw_method is None), (
        f"sliding_window=0 not converted: attr={sw_attr!r}, method={sw_method!r}"
    )


def test_sw_zero_sets_disable_flag():
    """disable_sliding_window must be True when sliding_window=0."""
    result = _test_sw_behavior(0)
    assert result["disable_sliding_window"] is True, (
        f"disable_sliding_window={result['disable_sliding_window']!r}, expected True"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: non-zero / None values preserved
# -----------------------------------------------------------------------------


def test_sw_none_preserved():
    """sliding_window=None must remain None and not trigger disable."""
    result = _test_sw_behavior(None)
    assert result["sliding_window_attr"] is None, (
        f"sliding_window=None was modified to {result['sliding_window_attr']!r}"
    )
    assert result["disable_sliding_window"] is not True, (
        "disable_sliding_window incorrectly set for sliding_window=None"
    )


def test_sw_positive_preserved():
    """sliding_window=128 must be preserved (not zeroed or set to None)."""
    result = _test_sw_behavior(128)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
    assert (sw_attr == 128) or (sw_method == 128), (
        f"sliding_window=128 not preserved: attr={sw_attr!r}, method={sw_method!r}"
    )


def test_sw_large_positive_preserved():
    """sliding_window=4096 must be preserved."""
    result = _test_sw_behavior(4096)
    sw_attr = result["sliding_window_attr"]
    sw_method = result["sliding_window_method"]
    assert (sw_attr == 4096) or (sw_method == 4096), (
        f"sliding_window=4096 not preserved: attr={sw_attr!r}, method={sw_method!r}"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# -----------------------------------------------------------------------------


def _find_post_init_node(tree):
    """Return the AST node for ModelConfig.__post_init__."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    return item
    return None


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
