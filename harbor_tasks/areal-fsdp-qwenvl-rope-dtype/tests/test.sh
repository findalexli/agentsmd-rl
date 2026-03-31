#!/usr/bin/env bash
set +e

TOTAL=0
BEHAVIORAL_PASSED=0
FILE="areal/engine/fsdp_engine.py"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "PASS: syntax OK"
else
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== F2P Behavioral: Mock execution of Qwen-VL branch ==="
# [pr_diff] (0.60): Extract the is_qwen_vl_model branch from _prepare_mb_list,
# mock torch with lightweight Python objects, exec the extracted code with int32
# input_ids, and verify: (a) dtype gets cast to int64/long, (b) dict is updated,
# (c) get_rope_index is called with keyword arguments including input_ids and
# attention_mask.
# WHY AST-extract + exec (not direct import): The FSDP engine requires distributed
# process groups, device mesh, and multi-GB model weights. We extract just the
# Qwen-VL branch and run it with mock torch tensors on CPU.
python3 << 'PYEOF'
import ast, sys, types, textwrap, json

FILE = 'areal/engine/fsdp_engine.py'
source = open(FILE).read()
tree = ast.parse(source)

results = {'dtype_cast': False, 'dict_updated': False, 'keyword_args': False, 'noop_int64': False}

# ---- Locate _prepare_mb_list ----
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_prepare_mb_list':
        func_node = node
        break
if func_node is None:
    print('FAIL: _prepare_mb_list not found')
    json.dump(results, open('/tmp/behavioral.json', 'w'))
    sys.exit(0)

# ---- Locate the is_qwen_vl_model branch ----
vl_if = None
for child in ast.walk(func_node):
    if isinstance(child, ast.If):
        test_src = ast.get_source_segment(source, child.test)
        if test_src and 'qwen_vl' in test_src.lower().replace('-', '_').replace(' ', '_'):
            vl_if = child
            break
if vl_if is None:
    print('FAIL: is_qwen_vl_model branch not found')
    json.dump(results, open('/tmp/behavioral.json', 'w'))
    sys.exit(0)

# ---- Extract body ----
body_start = vl_if.body[0].lineno
body_end = vl_if.body[-1].end_lineno
raw_lines = source.splitlines()[body_start - 1:body_end]
body_src = textwrap.dedent('\n'.join(raw_lines))

# ---- Mock torch environment ----
class DT:
    """Mock dtype that supports equality comparison."""
    def __init__(self, n): self.n = n
    def __eq__(self, o): return isinstance(o, DT) and self.n == o.n
    def __ne__(self, o): return not self.__eq__(o)
    def __hash__(self): return hash(self.n)
    def __repr__(self): return f'torch.{self.n}'

INT32 = DT('int32')
LONG = DT('long')
INT64 = DT('int64')

class MT:
    """Mock tensor with dtype tracking."""
    def __init__(self, dtype=None):
        self.dtype = dtype or DT('float32')
    def to(self, *a, **kw):
        d = a[0] if a else kw.get('dtype', self.dtype)
        return MT(dtype=d)
    def long(self):
        return MT(dtype=LONG)
    def int(self):
        return MT(dtype=INT32)
    def __getattr__(self, name):
        return MT(dtype=self.dtype)

torch_ns = types.ModuleType('torch')
torch_ns.long = LONG
torch_ns.int64 = INT64
torch_ns.int32 = INT32
torch_ns.float32 = DT('float32')
torch_ns.bfloat16 = DT('bfloat16')
torch_ns.float16 = DT('float16')
torch_ns.Tensor = MT
torch_ns.einsum = lambda *a, **kw: a[1] if len(a) > 1 else MT(LONG)
torch_ns.cat = lambda lst, **kw: lst[0] if lst else MT(LONG)
sys.modules['torch'] = torch_ns

# ---- Mock model with call capture ----
calls = []
class MModel:
    @staticmethod
    def get_rope_index(*args, **kwargs):
        calls.append({'args': args, 'kwargs': kwargs})
        return MT(LONG), None

class SelfMock:
    class model:
        model = MModel()
    class model_config:
        model_type = 'qwen2_5_vl'

# ---- Test 1: int32 input_ids (triggers the bug) ----
original_tensor = MT(INT32)
input_ = {
    'input_ids': original_tensor,
    'attention_mask': MT(LONG),
}

ns = {
    'torch': torch_ns,
    'input_': input_,
    'self': SelfMock(),
    '__builtins__': __builtins__,
}

try:
    exec(body_src, ns)
except Exception as e:
    print(f'Execution error (int32 path): {e}')
    json.dump(results, open('/tmp/behavioral.json', 'w'))
    sys.exit(0)

# Verify dtype cast
final_tensor = input_.get('input_ids', original_tensor)
if final_tensor.dtype in (LONG, INT64):
    results['dtype_cast'] = True
    if final_tensor is not original_tensor:
        results['dict_updated'] = True
        print(f'dtype_cast: PASS (int32 -> {final_tensor.dtype}, dict updated)')
    else:
        print(f'dtype_cast: PASS but dict not updated with cast tensor')
else:
    print(f'dtype_cast: FAIL (final dtype: {final_tensor.dtype})')

# Verify keyword arguments
if calls:
    call = calls[0]
    kw = set(call['kwargs'].keys())
    n_pos = len(call['args'])
    if 'input_ids' in kw and 'attention_mask' in kw:
        results['keyword_args'] = True
        print(f'keyword_args: PASS (kwargs={kw}, positional={n_pos})')
    elif n_pos == 0 and len(kw) >= 2:
        results['keyword_args'] = True
        print(f'keyword_args: PASS (all keyword, keys={kw})')
    else:
        print(f'keyword_args: FAIL (kwargs={kw}, positional={n_pos})')
else:
    print('keyword_args: FAIL (get_rope_index not called)')

# ---- Test 2: int64 input_ids (no-op path — should not crash or change dtype) ----
calls.clear()
original_int64 = MT(INT64)
input2 = {
    'input_ids': original_int64,
    'attention_mask': MT(LONG),
}
ns2 = {
    'torch': torch_ns,
    'input_': input2,
    'self': SelfMock(),
    '__builtins__': __builtins__,
}
try:
    exec(body_src, ns2)
    final2 = input2.get('input_ids', original_int64)
    if final2.dtype in (LONG, INT64):
        results['noop_int64'] = True
        print(f'noop_int64: PASS (int64 input preserved as {final2.dtype})')
    else:
        print(f'noop_int64: FAIL (int64 input became {final2.dtype})')
except Exception as e:
    print(f'noop_int64: FAIL (execution error: {e})')

json.dump(results, open('/tmp/behavioral.json', 'w'))
PYEOF

# Read behavioral results
DTYPE_OK=$(python3 -c "import json; r=json.load(open('/tmp/behavioral.json')); print('1' if r.get('dtype_cast') else '0')" 2>/dev/null || echo "0")
DICT_OK=$(python3 -c "import json; r=json.load(open('/tmp/behavioral.json')); print('1' if r.get('dict_updated') else '0')" 2>/dev/null || echo "0")
KW_OK=$(python3 -c "import json; r=json.load(open('/tmp/behavioral.json')); print('1' if r.get('keyword_args') else '0')" 2>/dev/null || echo "0")
NOOP_OK=$(python3 -c "import json; r=json.load(open('/tmp/behavioral.json')); print('1' if r.get('noop_int64') else '0')" 2>/dev/null || echo "0")

echo ""
echo "=== F2P: input_ids dtype cast to int64 ==="
# [pr_diff] (0.25): input_ids must be cast from int32 to int64/long to prevent
# "Index put requires the source and destination dtypes match" error
if [ "$DTYPE_OK" = "1" ]; then
    echo "PASS: dtype cast verified via mock execution"
    add_score 0.25
    BEHAVIORAL_PASSED=1
else
    echo "FAIL: input_ids not cast to int64"
fi

echo ""
echo "=== F2P: input_ dict updated with cast tensor ==="
# [pr_diff] (0.10): The cast tensor must be written back to input_ dict so
# downstream code sees the corrected dtype
if [ "$DICT_OK" = "1" ]; then
    echo "PASS: dict updated with cast tensor"
    add_score 0.10
else
    echo "FAIL: input_ dict not updated after cast"
fi

echo ""
echo "=== F2P: get_rope_index called with keyword arguments ==="
# [pr_diff] (0.25): get_rope_index must use keyword args to avoid positional
# binding ambiguity between Qwen2.5-VL and Qwen3-VL signatures
if [ "$KW_OK" = "1" ]; then
    echo "PASS: keyword arguments verified via mock execution"
    add_score 0.25
    BEHAVIORAL_PASSED=1
else
    echo "FAIL: get_rope_index not called with keyword arguments"
fi

echo ""
echo "=== P2P: int64 input_ids no-op path ==="
# [pr_diff] (0.05): When input_ids is already int64, the code must not crash
# or change the dtype to something unexpected
if [ "$NOOP_OK" = "1" ]; then
    echo "PASS: int64 input preserved correctly"
    add_score 0.05
else
    echo "FAIL: int64 no-op path broken"
fi

# ---- Structural checks gated behind behavioral pass ----
if [ "$BEHAVIORAL_PASSED" = "1" ]; then

    echo ""
    echo "=== P2P: is_qwen_vl_model call preserved ==="
    # [pr_diff] (0.10): The is_qwen_vl_model conditional must still exist
    if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == 'is_qwen_vl_model':
            sys.exit(0)
        if isinstance(func, ast.Attribute) and func.attr == 'is_qwen_vl_model':
            sys.exit(0)
sys.exit(1)
"; then
        echo "PASS: is_qwen_vl_model call found (AST)"
        add_score 0.10
    else
        echo "FAIL: is_qwen_vl_model call missing"
    fi

    echo ""
    echo "=== P2P: position_ids einsum preserved ==="
    # [pr_diff] (0.05): The einsum permutation of position_ids must be preserved
    if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'einsum':
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if 'ijk' in arg.value and 'jki' in arg.value:
                        sys.exit(0)
        elif isinstance(func, ast.Name) and func.id == 'einsum':
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if 'ijk' in arg.value and 'jki' in arg.value:
                        sys.exit(0)
sys.exit(1)
"; then
        echo "PASS: einsum permutation preserved (AST)"
        add_score 0.05
    else
        echo "FAIL: einsum permutation missing"
    fi

    echo ""
    echo "=== Anti-gaming: _prepare_mb_list not stubbed ==="
    # [pr_diff] (0.10): Method must have substantial implementation (>=10 meaningful stmts)
    if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_prepare_mb_list':
        meaningful = 0
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                 ast.Return, ast.If, ast.For, ast.While,
                                 ast.Expr)):
                meaningful += 1
        if meaningful >= 10:
            sys.exit(0)
        else:
            print(f'Only {meaningful} meaningful statements (need >=10)')
            sys.exit(1)
print('_prepare_mb_list not found')
sys.exit(1)
"; then
        echo "PASS: method has substantial implementation"
        add_score 0.10
    else
        echo "FAIL: method appears stubbed or too minimal"
    fi

    echo ""
    echo "=== Config: No wildcard imports ==="
    # [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30
    if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names:
        for alias in node.names:
            if alias.name == '*':
                sys.exit(1)
sys.exit(0)
"; then
        echo "PASS: no wildcard imports"
        add_score 0.05
    else
        echo "FAIL: wildcard import found"
    fi

else
    echo ""
    echo "=== SKIPPED: Structural checks gated behind behavioral pass ==="
    echo "No behavioral tests passed — structural checks not awarded"
fi

echo ""
echo "=== Total score: $TOTAL ==="
# Clamp to [0, 1]
TOTAL=$(python3 -c "print(min(1.0, max(0.0, $TOTAL)))")
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
reward = $TOTAL
behavioral = min(reward, 0.65)
regression = min(max(0, reward - 0.65), 0.15)
config = min(max(0, reward - 0.80), 0.05)
structural = max(0, reward - 0.85)
data = {
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'structural': structural,
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
