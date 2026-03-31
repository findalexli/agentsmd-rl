#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/slime"
export TARGET="$REPO/tools/convert_hf_to_fp8.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null; then
    echo "FAIL: Syntax error in convert_hf_to_fp8.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: Syntax OK"

# ---------------------------------------------------------------
# Helper: mock torch/safetensors, exec the file, call process_file
# with synthetic keys, and report which keys were quantized vs excluded.
#
# This approach works regardless of implementation style (inline AND,
# set-based, helper function, early-continue, etc.).
# ---------------------------------------------------------------

MOCK_HARNESS=$(cat <<'PYEOF'
import sys, types, os, json

# --- Mock heavy dependencies so we can exec the file on CPU ---
# Mock torch
mock_torch = types.ModuleType('torch')
mock_torch.float8_e4m3fn = 'fake_dtype'
mock_torch.float16 = 'fake_f16'
mock_torch.bfloat16 = 'fake_bf16'
mock_torch.float32 = 'fake_f32'
class FakeTensor:
    def __init__(self, shape=(1,)):
        self._shape = shape
    def to(self, *a, **kw): return self
    def float(self): return self
    def half(self): return self
    def reshape(self, *a): return self
    def view(self, *a): return self
    def contiguous(self): return self
    def clone(self): return self
    def abs(self): return self
    def max(self): return FakeTensor()
    def item(self): return 1.0
    @property
    def shape(self): return self._shape
    @property
    def dtype(self): return 'fake_dtype'
    def __truediv__(self, other): return self
    def __mul__(self, other): return self
mock_torch.Tensor = FakeTensor
mock_torch.zeros = lambda *a, **kw: FakeTensor()
mock_torch.ones = lambda *a, **kw: FakeTensor()
mock_torch.tensor = lambda *a, **kw: FakeTensor()
mock_torch.empty = lambda *a, **kw: FakeTensor()
mock_torch.amax = lambda *a, **kw: FakeTensor()

mock_cuda = types.ModuleType('torch.cuda')
mock_cuda.memory_allocated = lambda: 0
mock_torch.cuda = mock_cuda

# Mock torch.nn and torch.nn.functional
mock_nn = types.ModuleType('torch.nn')
mock_nn_functional = types.ModuleType('torch.nn.functional')
mock_nn_functional.pad = lambda *a, **kw: FakeTensor()
mock_nn.functional = mock_nn_functional
mock_nn.F = mock_nn_functional
mock_torch.nn = mock_nn

# Mock torch.finfo
class FakeFinfo:
    def __init__(self, dtype=None):
        self.max = 448.0
        self.min = -448.0
mock_torch.finfo = FakeFinfo

sys.modules['torch'] = mock_torch
sys.modules['torch.cuda'] = mock_cuda
sys.modules['torch.nn'] = mock_nn
sys.modules['torch.nn.functional'] = mock_nn_functional

# Mock tqdm
mock_tqdm = types.ModuleType('tqdm')
mock_tqdm.tqdm = lambda x, **kw: x
sys.modules['tqdm'] = mock_tqdm

# Mock safetensors
mock_sf = types.ModuleType('safetensors')
# TEST_KEYS will be set before calling process_file
_test_weights = {}
class FakeSafeOpen:
    def __init__(self, path, framework=None, device=None):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass
    def keys(self):
        return list(_test_weights.keys())
    def get_tensor(self, k):
        return _test_weights[k]
mock_sf.safe_open = FakeSafeOpen
mock_sf_torch = types.ModuleType('safetensors.torch')
_saved_data = {}
def _fake_save(data, path, **kw):
    _saved_data.clear()
    _saved_data.update(data)
mock_sf_torch.save_file = _fake_save
mock_sf.torch = mock_sf_torch
sys.modules['safetensors'] = mock_sf
sys.modules['safetensors.torch'] = mock_sf_torch

# --- Read and exec the target file ---
source = open(os.environ['TARGET']).read()
ns = {'__builtins__': __builtins__, '__name__': '__not_main__', '__file__': os.environ['TARGET']}
exec(compile(source, os.environ['TARGET'], 'exec'), ns)

process_file = ns.get('process_file')
if process_file is None:
    print("FAIL: process_file not found")
    sys.exit(1)

# Override quant_fp8 in the namespace so it returns mock data
_quantized_keys = []
def mock_quant_fp8(tensor, strategy, block_size):
    _quantized_keys.append('__current_key__')  # placeholder
    return FakeTensor(), FakeTensor()
ns['quant_fp8'] = mock_quant_fp8

# Re-exec just process_file to pick up the mock quant_fp8
# Actually, since process_file references module-level quant_fp8 via its globals (ns),
# we need to make sure ns has the mock. It does since we set ns['quant_fp8'].

# --- Mock result collector ---
class FakeCollector:
    def __init__(self):
        self.q_weights = {}
        self.modules = []
    def add_result(self, filename, q_weights, module_names):
        self.q_weights.update(q_weights)
        self.modules.extend(module_names)

# --- Helper to run process_file and return quantized/excluded keys ---
def run_with_keys(test_keys):
    """Run process_file with given keys and return (quantized_keys, excluded_keys)."""
    _test_weights.clear()
    for k in test_keys:
        _test_weights[k] = FakeTensor()
    _saved_data.clear()
    collector = FakeCollector()

    # Track which keys get quantized by patching quant_fp8
    quantized = set()
    def tracking_quant(tensor, strategy, block_size):
        # We track via the saved data afterward
        return FakeTensor(), FakeTensor()
    ns['quant_fp8'] = tracking_quant

    try:
        process_file('/fake/input', '/fake/output', 'test.safetensors', 'tensor', None, collector)
    except Exception as e:
        print(f"ERROR calling process_file: {e}")
        sys.exit(2)

    # Determine quantized vs excluded from saved data
    # Quantized keys get a scale companion key; excluded keys are passed through as-is
    quantized_keys = set()
    excluded_keys = set()
    for k in test_keys:
        # If a scale key exists (and differs from k), the weight was quantized
        scale_key_a = k.replace(".weight", ".weight_scale_inv")
        scale_key_b = k.replace(".weight", ".weight_scale")
        has_scale = (scale_key_a != k and scale_key_a in _saved_data) or \
                    (scale_key_b != k and scale_key_b in _saved_data)
        if has_scale:
            quantized_keys.add(k)
        elif k in _saved_data:
            excluded_keys.add(k)

    return quantized_keys, excluded_keys

# Export for tests
import json as _json
results = {}

PYEOF
)

echo ""
echo "=== Behavioral (F2P): Mamba-style keys excluded from FP8 ==="

# [pr_diff] (0.30): Core bug — conv1d, A_log, dt_bias, in_proj_a, in_proj_b must be excluded
python3 -c "
$MOCK_HARNESS

test_keys = [
    'model.layers.0.self_attn.q_proj.weight',        # normal — SHOULD be quantized
    'model.layers.0.mamba.conv1d.weight',             # Mamba — must be EXCLUDED
    'model.layers.5.mamba.A_log',                     # Mamba — must be EXCLUDED
    'model.layers.3.mamba.dt_bias',                   # Mamba — must be EXCLUDED
    'model.layers.1.mamba.in_proj_a.weight',          # Mamba — must be EXCLUDED
    'model.layers.2.mamba.in_proj_b.weight',          # Mamba — must be EXCLUDED
]

quantized, excluded = run_with_keys(test_keys)

# The 5 Mamba keys must NOT be quantized
mamba_keys = {
    'model.layers.0.mamba.conv1d.weight',
    'model.layers.5.mamba.A_log',
    'model.layers.3.mamba.dt_bias',
    'model.layers.1.mamba.in_proj_a.weight',
    'model.layers.2.mamba.in_proj_b.weight',
}

failures = []
for k in mamba_keys:
    if k in quantized:
        failures.append(f'  INCORRECTLY quantized: {k}')

# Normal weight SHOULD be quantized
normal = 'model.layers.0.self_attn.q_proj.weight'
if normal not in quantized:
    failures.append(f'  Normal weight NOT quantized: {normal}')

if failures:
    print('FAIL: Mamba key exclusion')
    for f in failures:
        print(f)
    exit(1)
print('PASS: All 5 Mamba key types excluded, normal weight quantized')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.30)"); fi

# [pr_diff] (0.10): Individual Mamba key exclusions work with varied layer indices
echo ""
python3 -c "
$MOCK_HARNESS

# Test with different layer numbers to avoid overfitting to specific indices
test_keys = [
    'model.layers.17.mamba.conv1d.weight',
    'model.layers.42.mamba.A_log',
    'model.layers.99.mamba.dt_bias',
    'model.layers.0.mamba.in_proj_a.weight',
    'model.layers.31.mamba.in_proj_b.weight',
    'model.layers.17.self_attn.v_proj.weight',   # normal — should be quantized
]

quantized, excluded = run_with_keys(test_keys)

mamba_keys = {k for k in test_keys if 'mamba' in k}
for k in mamba_keys:
    if k in quantized:
        print(f'FAIL: {k} was quantized')
        exit(1)

if 'model.layers.17.self_attn.v_proj.weight' not in quantized:
    print('FAIL: normal weight not quantized')
    exit(1)

print('PASS: Mamba exclusions work across varied layer indices')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Behavioral (P2P): Pre-existing exclusions still work ==="

# [pr_diff] (0.15): Pre-existing exclusions (layernorm, embed, gate, lm_head, etc.)
python3 -c "
$MOCK_HARNESS

test_keys = [
    'model.layers.0.input_layernorm.weight',   # excluded (layernorm)
    'model.embed_tokens.weight',                # excluded (embed)
    'model.layers.0.mlp.gate.weight',           # excluded (mlp.gate.)
    'lm_head.weight',                           # excluded (lm_head)
    'model.layers.0.post_attention_layernorm.weight',  # excluded (norm/layernorm)
    'model.layers.0.self_attn.k_proj.weight',   # normal — SHOULD be quantized
    'model.layers.0.mlp.up_proj.weight',        # normal — SHOULD be quantized
]

quantized, excluded = run_with_keys(test_keys)

must_exclude = [
    'model.layers.0.input_layernorm.weight',
    'model.embed_tokens.weight',
    'model.layers.0.mlp.gate.weight',
    'lm_head.weight',
    'model.layers.0.post_attention_layernorm.weight',
]
must_quantize = [
    'model.layers.0.self_attn.k_proj.weight',
    'model.layers.0.mlp.up_proj.weight',
]

fail = False
for k in must_exclude:
    if k in quantized:
        print(f'FAIL: {k} should be excluded but was quantized')
        fail = True
for k in must_quantize:
    if k not in quantized:
        print(f'FAIL: {k} should be quantized but was not')
        fail = True

if fail:
    exit(1)
print('PASS: Pre-existing exclusions work, normal weights quantized')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

echo ""
echo "=== Behavioral (P2P): Non-weight keys skipped ==="

# [pr_diff] (0.05): Keys without 'weight' must not be quantized (pre-existing logic)
python3 -c "
$MOCK_HARNESS

test_keys = [
    'model.layers.0.self_attn.q_proj.bias',     # non-weight — excluded
    'model.layers.0.self_attn.q_proj.weight',    # weight — quantized
]

quantized, excluded = run_with_keys(test_keys)

if 'model.layers.0.self_attn.q_proj.bias' in quantized:
    print('FAIL: bias key was quantized')
    exit(1)
if 'model.layers.0.self_attn.q_proj.weight' not in quantized:
    print('FAIL: weight key was not quantized')
    exit(1)
print('PASS: Non-weight keys correctly skipped')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

echo ""
echo "=== Behavioral: Excluded keys preserved in output ==="

# [pr_diff] (0.10): Excluded keys should still appear in output (passed through unchanged)
python3 -c "
$MOCK_HARNESS

test_keys = [
    'model.layers.0.mamba.conv1d.weight',
    'model.layers.0.input_layernorm.weight',
    'model.layers.0.self_attn.q_proj.weight',
]

quantized, excluded = run_with_keys(test_keys)

# All keys should appear in saved data (either quantized or excluded)
for k in test_keys:
    if k not in _saved_data:
        print(f'FAIL: key {k} missing from output')
        exit(1)
print('PASS: All keys (quantized and excluded) preserved in output')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Regression: Required functions exist ==="

# [pr_diff] (0.10): All expected functions must still be defined
python3 -c "
import ast
source = open('$TARGET').read()
tree = ast.parse(source)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {'process_file', 'convert_fp8', 'quant_fp8'}
missing = required - funcs
if missing:
    print(f'FAIL: Missing functions: {missing}')
    exit(1)
print(f'PASS: Required functions present')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Structural: Anti-stub (process_file has non-trivial body) ==="

# [pr_diff] (0.05): process_file must have meaningful implementation, not a stub
python3 -c "
import ast
source = open('$TARGET').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'process_file':
        # Count meaningful statements (not docstrings, not pass, not bare expressions)
        stmts = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                  ast.For, ast.If, ast.With, ast.Return, ast.Call)):
                stmts += 1
        if stmts < 8:
            print(f'FAIL: process_file too simple ({stmts} statements), likely a stub')
            exit(1)
        print(f'PASS: process_file has {stmts} meaningful statements')
        exit(0)
print('FAIL: process_file not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

echo ""
echo "=== Config: Changes contained ==="

# [agent_config] (0.05): "Keep test scope small and behavior-focused" — .claude/skills/add-tests-and-ci/SKILL.md:25
CHANGED_FILES=$(cd "$REPO" && git diff --name-only HEAD 2>/dev/null | wc -l)
if [ "$CHANGED_FILES" -le 3 ]; then
    echo "PASS: Changes contained ($CHANGED_FILES files modified)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: Too many files changed ($CHANGED_FILES)"
fi

echo ""
echo "==================================="
echo "Total: $SCORE / 1.00"
echo "==================================="

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
behavioral = min(score, 0.70)
regression = min(max(score - 0.70, 0), 0.10)
structural = min(max(score - 0.80, 0), 0.05)
config = min(max(score - 0.85, 0), 0.05)
json.dump({
    'reward': score,
    'behavioral': behavioral,
    'regression': regression,
    'structural': structural,
    'config': config,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
