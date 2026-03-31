#!/usr/bin/env bash
set +e

REPO_DIR="/workspace/AReaL"
cd "$REPO_DIR"

REWARD=0
BEHAVIORAL=0
REGRESSION=0
CONFIG=0

##############################################################################
# GATE: Syntax check — abort on failure
##############################################################################
# [pr_diff] (gate): areal/utils/data.py must be valid Python
python3 -c "
import ast, sys
try:
    ast.parse(open('areal/utils/data.py').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
print('GATE PASS: syntax OK')
"
if [ $? -ne 0 ]; then
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "/logs/verifier/reward.json"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi

##############################################################################
# Fail-to-pass: behavioral tests (0.45 total)
##############################################################################

# [pr_diff] (0.30): pad_length==0 returns data unchanged, no extra cu_seqlens entry
python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

# Build a packed batch where total_length == pad_to_length == 10
cu_seqlens = torch.tensor([0, 4, 10], dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens,
    'max_seqlen': 6,
    'input_ids': torch.arange(10, dtype=torch.long),
}
result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=10)

# pad_length should be 0
assert pad_len == 0, f'Expected pad_length=0, got {pad_len}'

# cu_seqlens should NOT have an extra entry
assert result_data['cu_seqlens'].shape[0] == 3, \
    f'Expected cu_seqlens length 3 (unchanged), got {result_data[\"cu_seqlens\"].shape[0]}'

# No zero-length segment at end
cs = result_data['cu_seqlens']
for i in range(cs.shape[0] - 1):
    seg_len = (cs[i+1] - cs[i]).item()
    assert seg_len > 0, f'Zero-length segment at index {i}: cu_seqlens={cs.tolist()}'

print('PASS: pad_length==0 returns data unchanged')
" 2>&1
r1=$?
if [ $r1 -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.30)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.30)")
fi

# [pr_diff] (0.15): returned data tensors are identical when no padding needed
python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

cu_seqlens = torch.tensor([0, 5, 10], dtype=torch.long)
input_ids = torch.arange(10, dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens,
    'max_seqlen': 5,
    'input_ids': input_ids,
}
result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=10)

assert pad_len == 0, f'Expected pad_length=0, got {pad_len}'
assert torch.equal(result_data['input_ids'], input_ids), \
    f'input_ids changed: {result_data[\"input_ids\"]} vs {input_ids}'
assert result_data['max_seqlen'] == 5, \
    f'max_seqlen changed: {result_data[\"max_seqlen\"]}'

print('PASS: data tensors unchanged when pad_length==0')
" 2>&1
r2=$?
if [ $r2 -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.15)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.15)")
fi

##############################################################################
# Pass-to-pass: regression (0.40)
##############################################################################

# [pr_diff] (0.20): normal padding (pad_length > 0) still works correctly
python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

cu_seqlens = torch.tensor([0, 3, 7], dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens,
    'max_seqlen': 4,
    'input_ids': torch.arange(7, dtype=torch.long),
}
result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=12)

assert pad_len == 5, f'Expected pad_length=5, got {pad_len}'
# cu_seqlens should have one extra entry for the padding segment
assert result_data['cu_seqlens'].shape[0] == 4, \
    f'Expected cu_seqlens length 4, got {result_data[\"cu_seqlens\"].shape[0]}'
assert result_data['cu_seqlens'][-1].item() == 12, \
    f'Expected last cu_seqlens=12, got {result_data[\"cu_seqlens\"][-1].item()}'
# input_ids should be padded to length 12
assert result_data['input_ids'].shape[0] == 12, \
    f'Expected input_ids length 12, got {result_data[\"input_ids\"].shape[0]}'
# max_seqlen should be updated: max(4, 5) = 5
assert result_data['max_seqlen'] >= 5, \
    f'Expected max_seqlen >= 5, got {result_data[\"max_seqlen\"]}'

print('PASS: normal padding (pad_length > 0) works correctly')
" 2>&1
r3=$?
if [ $r3 -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.20)")
    REGRESSION=$(python3 -c "print($REGRESSION + 0.20)")
fi

# [repo_tests] (0.10): pad_packed_tensor_dict with pad_to_length < total raises ValueError
python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

cu_seqlens = torch.tensor([0, 5, 10], dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens,
    'max_seqlen': 5,
    'input_ids': torch.arange(10, dtype=torch.long),
}
try:
    pad_packed_tensor_dict(data, pad_to_length=5)
    print('FAIL: should have raised ValueError')
    sys.exit(1)
except ValueError:
    print('PASS: ValueError raised for pad_to_length < total_length')
" 2>&1
r4=$?
if [ $r4 -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
fi

# [repo_tests] (0.10): old_cu_seqlens return value is correct
python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

cu_seqlens = torch.tensor([0, 3, 7], dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens.clone(),
    'max_seqlen': 4,
    'input_ids': torch.arange(7, dtype=torch.long),
}
result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=12)

# old_cu should match the original cu_seqlens
assert torch.equal(old_cu, cu_seqlens), \
    f'old_cu_seqlens incorrect: {old_cu} vs expected {cu_seqlens}'

print('PASS: old_cu_seqlens correctly returned')
" 2>&1
r5=$?
if [ $r5 -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
fi

##############################################################################
# Config-derived checks (0.15) — gated behind behavioral AND regression pass
##############################################################################

if [ $r1 -eq 0 ] && [ $r3 -eq 0 ]; then

    # [agent_config] (0.05): "No wildcard imports" — CLAUDE.md:89
    python3 -c "
import ast, sys
tree = ast.parse(open('areal/utils/data.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names:
        for alias in node.names:
            if alias.name == '*':
                print(f'FAIL: wildcard import from {node.module}')
                sys.exit(1)
print('PASS: no wildcard imports')
" 2>&1
    r6=$?
    if [ $r6 -eq 0 ]; then
        REWARD=$(python3 -c "print($REWARD + 0.05)")
        CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    fi

    # [agent_config] (0.05): "Follow existing code patterns" — CLAUDE.md:95
    # Verify function still returns the documented 4-tuple signature
    python3 -c "
import torch, sys
sys.path.insert(0, '.')
from areal.utils.data import pad_packed_tensor_dict

cu_seqlens = torch.tensor([0, 4, 10], dtype=torch.long)
data = {
    'cu_seqlens': cu_seqlens,
    'max_seqlen': 6,
    'input_ids': torch.arange(10, dtype=torch.long),
}
result = pad_packed_tensor_dict(data, pad_to_length=10)
assert isinstance(result, tuple), f'Expected tuple, got {type(result)}'
assert len(result) == 4, f'Expected 4-tuple return, got {len(result)}-tuple'

print('PASS: function returns consistent 4-tuple')
" 2>&1
    r7=$?
    if [ $r7 -eq 0 ]; then
        REWARD=$(python3 -c "print($REWARD + 0.05)")
        CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    fi

    # [agent_config] (0.05): "Explicit dtype/device; torch.Size assertions" — AGENTS.md:97
    # Anti-stub: function body is substantive
    python3 -c "
import ast, sys
tree = ast.parse(open('areal/utils/data.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'pad_packed_tensor_dict':
        stmts = [s for s in node.body if not isinstance(s, ast.Expr)]
        assert len(stmts) >= 5, f'Function body too short ({len(stmts)} stmts) — possible stub'
        print('PASS: function is not stubbed')
        sys.exit(0)
print('FAIL: function not found')
sys.exit(1)
" 2>&1
    r8=$?
    if [ $r8 -eq 0 ]; then
        REWARD=$(python3 -c "print($REWARD + 0.05)")
        CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    fi

else
    echo "SKIP: config checks gated behind behavioral + regression pass"
fi

##############################################################################
# Summary
##############################################################################

echo "Behavioral: $BEHAVIORAL | Regression: $REGRESSION | Config: $CONFIG"
echo "Total reward: $REWARD"
echo "$REWARD" > "/logs/verifier/reward.txt"
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > "/logs/verifier/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
