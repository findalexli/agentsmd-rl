#!/usr/bin/env bash
set +e  # Accumulate partial credit, don't abort on failures

REPO=/workspace/prime-rl
CONFIG_PY="$REPO/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py"
MODELING_PY="$REPO/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py"

BEHAVIORAL=0
REGRESSION=0
CONFIG=0

add() { eval "$1=\$(python3 -c \"print(round(\$$1 + $2, 4))\")"; }

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (0.00): Both changed files must parse
echo "=== GATE: Syntax check ==="
python3 -c "
import ast, sys
for f in ['$CONFIG_PY', '$MODELING_PY']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'GATE FAIL: {f}: {e}')
        sys.exit(1)
print('Syntax OK')
"
if [ $? -ne 0 ]; then
    echo "reward: 0.0"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# BEHAVIORAL: Fail-to-pass tests (0.70)
########################################

# [pr_diff] (0.30): Config mamba_expand correct for Nano-30B dimensions (core bug)
echo "=== F2P: Nano-30B dimension invariant ==="
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('configuration_nemotron_h', '$CONFIG_PY')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
NemotronHConfig = mod.NemotronHConfig

# Nemotron-3-Nano-30B: mamba_num_heads=64, mamba_head_dim=64, hidden_size=2688
# Bug: raw mamba_expand=2 gives int(2*2688)=5376, expected 64*64=4096
config = NemotronHConfig(hidden_size=2688, mamba_num_heads=64, mamba_head_dim=64, mamba_expand=2)
expected = 64 * 64  # 4096
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f'intermediate_size={actual}, expected {expected}'
print(f'PASS: intermediate_size={actual}')
" && add BEHAVIORAL 0.30 || echo "FAIL: Nano-30B invariant"

# [pr_diff] (0.25): Config mamba_expand correct for multiple dimension combos
echo "=== F2P: Multiple dimension combos ==="
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('configuration_nemotron_h', '$CONFIG_PY')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
NemotronHConfig = mod.NemotronHConfig

# Each case: (hidden_size, mamba_num_heads, mamba_head_dim, raw_mamba_expand)
# All chosen so raw_expand * hidden_size != heads * head_dim (except case 3 which coincides)
cases = [
    (1024, 32, 48, 3),   # expected 1536, raw gives 3072
    (512,  16, 48, 2),   # expected  768, raw gives 1024
    (2048, 64, 64, 1),   # expected 4096, raw gives 2048
]
for hs, nh, hd, me in cases:
    config = NemotronHConfig(hidden_size=hs, mamba_num_heads=nh, mamba_head_dim=hd, mamba_expand=me)
    expected = nh * hd
    actual = int(config.mamba_expand * config.hidden_size)
    assert actual == expected, f'hs={hs} nh={nh} hd={hd}: got {actual}, expected {expected}'
print('PASS: All combos correct')
" && add BEHAVIORAL 0.25 || echo "FAIL: Multiple combos"

# [pr_diff] (0.15): Fractional expand precision — no off-by-one from float truncation
echo "=== F2P: Fractional expand precision ==="
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('configuration_nemotron_h', '$CONFIG_PY')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
NemotronHConfig = mod.NemotronHConfig

# Dimensions where heads*head_dim / hidden_size is not a clean fraction
# 3840 / 2688 = 1.42857142857... (repeating)
config = NemotronHConfig(hidden_size=2688, mamba_num_heads=80, mamba_head_dim=48, mamba_expand=2)
expected = 80 * 48  # 3840
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f'Fractional case: got {actual}, expected {expected}'

# 3072 / 1536 = 2.0 (clean fraction, should still work)
config2 = NemotronHConfig(hidden_size=1536, mamba_num_heads=48, mamba_head_dim=64, mamba_expand=4)
expected2 = 48 * 64  # 3072
actual2 = int(config2.mamba_expand * config2.hidden_size)
assert actual2 == expected2, f'Clean fraction case: got {actual2}, expected {expected2}'
print('PASS: Precision OK')
" && add BEHAVIORAL 0.15 || echo "FAIL: Fractional precision"

########################################
# REGRESSION: Pass-to-pass (0.10)
########################################

# [pr_diff] (0.10): 120B default config still produces correct mamba_expand
echo "=== P2P: 120B default config ==="
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('configuration_nemotron_h', '$CONFIG_PY')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
NemotronHConfig = mod.NemotronHConfig

# Default config (120B): hidden_size=4096, mamba_num_heads=128, mamba_head_dim=64
config = NemotronHConfig()
expected = 128 * 64  # 8192
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f'120B: got {actual}, expected {expected}'
assert config.mamba_expand > 0, 'mamba_expand must be positive'
print(f'PASS: 120B intermediate_size={actual}, mamba_expand={config.mamba_expand}')
" && add REGRESSION 0.10 || echo "FAIL: 120B default"

########################################
# STRUCTURAL: Anti-stub (0.05)
########################################

# [pr_diff] (0.05): Config __init__ is not a no-op stub
echo "=== STRUCTURAL: Config not a stub ==="
python3 -c "
import ast, sys

tree = ast.parse(open('$CONFIG_PY').read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                real = [s for s in item.body if not isinstance(s, (ast.Pass, ast.Expr))]
                assert len(real) >= 10, f'Stub detected: only {len(real)} statements'
                print(f'PASS: __init__ has {len(real)} real statements')
                sys.exit(0)
print('FAIL: NemotronHConfig.__init__ not found')
sys.exit(1)
" && add CONFIG 0.05 || echo "FAIL: Anti-stub"

########################################
# CONFIG-DERIVED (0.10)
########################################

# [agent_config] (0.05): No unnecessary try/except — AGENTS.md:5 @ 8a6f4ef
echo "=== CONFIG: No silent try/except ==="
python3 -c "
import ast, sys

for fpath in ['$CONFIG_PY', '$MODELING_PY']:
    tree = ast.parse(open(fpath).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    print(f'FAIL: Silent except/pass in {fpath} at line {node.lineno}')
                    sys.exit(1)
print('PASS: No silent try/except/pass blocks')
" && add CONFIG 0.05 || echo "FAIL: Silent try/except"

# [agent_config] (0.05): No work-process comments — AGENTS.md:7 @ 8a6f4ef
echo "=== CONFIG: No work-process comments ==="
python3 -c "
import sys

bad_patterns = ['used to', 'previously', 'old code', 'was changed', 'we changed', 'refactored from']
for fpath in ['$CONFIG_PY', '$MODELING_PY']:
    for i, line in enumerate(open(fpath), 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            lower = stripped.lower()
            for pat in bad_patterns:
                if pat in lower:
                    print(f'FAIL: Work-process comment in {fpath}:{i}: {stripped}')
                    sys.exit(1)
print('PASS: No work-process comments found')
" && add CONFIG 0.05 || echo "FAIL: Work-process comments"

########################################
# SUMMARY
########################################

TOTAL=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG, 4))")

echo ""
echo "=== TOTAL SCORE: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
print(json.dumps({
    'reward': $TOTAL,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
