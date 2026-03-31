#!/usr/bin/env bash
set +e

SCORE=0
TARGET="/workspace/vllm/vllm/config/model.py"

echo "=== vllm-sliding-window-zero-config ==="
echo ""

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): File must be valid Python
echo "--- GATE: Python syntax check ---"
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())"; then
    echo "GATE FAILED: syntax error in target file"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"
echo ""

########################################
# BEHAVIORAL: Run __post_init__ with mocks, check end state
########################################
# Justification for AST extraction: ModelConfig.__post_init__ has deep
# torch/transformers dependencies that cannot run on CPU-only python:3.12-slim.
# We extract methods via AST, bind them to a mock, and exec __post_init__
# statement-by-statement with error tolerance. This tests BEHAVIOR (end state)
# not code structure, and accepts ANY valid fix location/style.

BEHAVIORAL_JSON=$(python3 << 'PYEOF'
import ast, sys, textwrap, json

TARGET = "/workspace/vllm/vllm/config/model.py"

with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Find ModelConfig class
mc = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        mc = node
        break
if mc is None:
    print(json.dumps({"error": "ModelConfig class not found"}))
    sys.exit(0)

# Extract all methods from ModelConfig
methods = {}
for item in mc.body:
    if isinstance(item, ast.FunctionDef):
        lines = source.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
        methods[item.name] = func_src

if "__post_init__" not in methods:
    print(json.dumps({"error": "__post_init__ not found"}))
    sys.exit(0)

# Find __post_init__ AST node for statement-by-statement exec
post_init_node = None
for item in mc.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
        post_init_node = item
        break

def make_hf_config(sw):
    """Create a mock HF config with sliding_window set."""
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

def make_mock(sw):
    """Create a mock ModelConfig-like object."""
    class MockConfig:
        def __init__(self):
            self.disable_sliding_window = False
            self.hf_text_config = make_hf_config(sw)
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

def bind_methods(obj):
    """Bind all extracted methods (except __post_init__) to the mock's class."""
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

def run_post_init(obj):
    """Execute __post_init__ body statement-by-statement with error tolerance."""
    import logging, warnings, os
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

def get_sw(obj):
    """Get sliding_window via method or attribute, accepting either fix approach."""
    try:
        return obj.get_sliding_window()
    except Exception:
        return getattr(obj.hf_text_config, "sliding_window", "ERROR")

results = {}

# --- Test 1: sliding_window=0 → None ---
obj0 = make_mock(sw=0)
bind_methods(obj0)
run_post_init(obj0)
sw_attr_0 = obj0.hf_text_config.sliding_window
sw_method_0 = get_sw(obj0)
# Accept if either the attribute or the method returns None
results["sw0_attr"] = repr(sw_attr_0)
results["sw0_method"] = repr(sw_method_0)
results["sw0_to_none"] = (sw_attr_0 is None) or (sw_method_0 is None)

# --- Test 2: disable_sliding_window set True when sw=0 ---
results["sw0_disable"] = (obj0.disable_sliding_window is True)

# --- Test 3: sliding_window=None stays None, doesn't trigger disable ---
objN = make_mock(sw=None)
bind_methods(objN)
run_post_init(objN)
sw_attr_N = objN.hf_text_config.sliding_window
results["swNone_preserved"] = (sw_attr_N is None)
results["swNone_disable_unchanged"] = (objN.disable_sliding_window is not True)

# --- Test 4: sliding_window=128 preserved (non-zero value) ---
obj128 = make_mock(sw=128)
bind_methods(obj128)
run_post_init(obj128)
sw_attr_128 = obj128.hf_text_config.sliding_window
sw_method_128 = get_sw(obj128)
results["sw128_attr"] = repr(sw_attr_128)
results["sw128_preserved"] = (sw_attr_128 == 128) or (sw_method_128 == 128)

print(json.dumps(results))
PYEOF
)

echo "Behavioral test output: $BEHAVIORAL_JSON"
echo ""

# Parse behavioral results
parse_bool() {
    python3 -c "import json,sys; d=json.loads(sys.argv[1]); print('yes' if d.get(sys.argv[2]) else 'no')" "$BEHAVIORAL_JSON" "$1"
}

HAS_ERROR=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print('yes' if 'error' in d else 'no')" "$BEHAVIORAL_JSON" 2>/dev/null || echo "yes")
if [ "$HAS_ERROR" = "yes" ]; then
    echo "ERROR: Could not run behavioral tests"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > /logs/verifier/reward.json
    exit 0
fi

# [pr_diff] (0.35): sliding_window=0 must be converted to None
echo "--- CHECK 1: sliding_window=0 → None (fail-to-pass) ---"
if [ "$(parse_bool sw0_to_none)" = "yes" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.35)")
    echo "  PASS +0.35"
else
    echo "  FAIL: sliding_window=0 was not converted to None"
fi
echo ""

# [pr_diff] (0.20): disable_sliding_window must be set True when sliding_window=0
echo "--- CHECK 2: disable_sliding_window=True when sw=0 (fail-to-pass) ---"
if [ "$(parse_bool sw0_disable)" = "yes" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    echo "  PASS +0.20"
else
    echo "  FAIL: disable_sliding_window not set to True"
fi
echo ""

# [pr_diff] (0.10): sliding_window=None and sliding_window=128 must be preserved
echo "--- CHECK 3: Non-zero / None sliding_window preserved (pass-to-pass) ---"
C3_PASS=true
if [ "$(parse_bool swNone_preserved)" != "yes" ]; then
    echo "  FAIL: sliding_window=None was modified"
    C3_PASS=false
fi
if [ "$(parse_bool swNone_disable_unchanged)" != "yes" ]; then
    echo "  FAIL: disable_sliding_window incorrectly set for sliding_window=None"
    C3_PASS=false
fi
if [ "$(parse_bool sw128_preserved)" != "yes" ]; then
    echo "  FAIL: sliding_window=128 was not preserved"
    C3_PASS=false
fi
if [ "$C3_PASS" = true ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  PASS +0.10"
fi
echo ""

########################################
# PASS-TO-PASS: Key methods and class structure
########################################

# [pr_diff] (0.15): Core methods and class structure preserved
echo "--- CHECK 4: ModelConfig methods preserved (pass-to-pass) ---"
P2P_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

expected_methods = {'get_sliding_window', 'get_and_verify_max_len', '__post_init__'}
found_methods = set()
found_class = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ModelConfig':
        found_class = True
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in expected_methods:
                found_methods.add(item.name)

if not found_class:
    print('FAIL: ModelConfig class not found')
else:
    missing = expected_methods - found_methods
    if missing:
        for m in sorted(missing):
            print(f'  MISSING: {m}')
        print('FAIL')
    else:
        print('OK')
" 2>&1)
echo "$P2P_RESULT"
if echo "$P2P_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  +0.15"
fi
echo ""

########################################
# STRUCTURAL: Fix ordering + anti-stub
########################################

# [pr_diff] (0.10): sliding_window normalization must happen before get_and_verify_max_len
echo "--- CHECK 5: Fix ordering (before get_and_verify_max_len) ---"
ORDER_RESULT=$(python3 -c "
import ast, sys

with open('$TARGET') as f:
    source = f.read()
tree = ast.parse(source)

# Find __post_init__
post_init = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ModelConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                post_init = item
                break
        break

if post_init is None:
    print('FAIL: __post_init__ not found')
    sys.exit(0)

# Find earliest line that touches sliding_window with an assignment/modification
# (broader than looking for specific If pattern — accepts any normalization code)
fix_line = None
verify_line = None

for node in ast.walk(post_init):
    # Any assignment touching sliding_window or disable_sliding_window
    if isinstance(node, ast.Assign):
        src = ast.get_source_segment(source, node)
        if src and ('sliding_window' in src):
            if fix_line is None or node.lineno < fix_line:
                fix_line = node.lineno
    # Also check If blocks that mention sliding_window and contain assignments
    if isinstance(node, ast.If):
        src = ast.get_source_segment(source, node)
        if src and 'sliding_window' in src:
            # Check if it contains any assignment
            for child in ast.walk(node):
                if isinstance(child, (ast.Assign, ast.AugAssign)):
                    if fix_line is None or node.lineno < fix_line:
                        fix_line = node.lineno
                    break
    # Find get_and_verify_max_len call
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'get_and_verify_max_len':
            verify_line = node.lineno

if fix_line is None:
    print('FAIL: no sliding_window normalization found in __post_init__')
elif verify_line is None:
    # get_and_verify_max_len might have been refactored — pass if fix exists
    print('OK')
elif fix_line >= verify_line:
    print(f'FAIL: sliding_window fix at line {fix_line} must come before get_and_verify_max_len at line {verify_line}')
else:
    print('OK')
" 2>&1)
echo "$ORDER_RESULT"
if echo "$ORDER_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.10): Anti-stub — __post_init__ has meaningful sliding_window handling
echo "--- CHECK 6: Anti-stub ---"
STUB_RESULT=$(python3 -c "
import ast, sys

with open('$TARGET') as f:
    source = f.read()
tree = ast.parse(source)

post_init = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ModelConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                post_init = item
                break
        break

if post_init is None:
    print('FAIL: no __post_init__')
    sys.exit(0)

# Count meaningful statements (not pass, not bare expressions/comments)
meaningful = 0
for stmt in post_init.body:
    if isinstance(stmt, ast.Pass):
        continue
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
        continue  # docstring or string expression
    meaningful += 1

# __post_init__ should have substantial logic (original has 40+ statements)
if meaningful < 5:
    print(f'FAIL: __post_init__ has only {meaningful} meaningful statements (stub?)')
else:
    # Also verify there's at least one assignment touching sliding_window
    has_sw_assign = False
    for node in ast.walk(post_init):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            src = ast.get_source_segment(source, node)
            if src and 'sliding_window' in src:
                has_sw_assign = True
                break
    if has_sw_assign:
        print('OK')
    else:
        print('FAIL: no assignment touching sliding_window in __post_init__')
" 2>&1)
echo "$STUB_RESULT"
if echo "$STUB_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
echo "Score: $SCORE / 1.00"

FINAL=$(python3 -c "print(f'{float($SCORE):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
behavioral = min(score, 0.65)
regression = min(max(score - 0.65, 0), 0.15)
structural = min(max(score - 0.80, 0), 0.20)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
