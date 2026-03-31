#!/usr/bin/env bash
set +e

ACTOR="/workspace/AReaL/areal/trainer/ppo/actor.py"
CRITIC="/workspace/AReaL/areal/trainer/ppo/critic.py"
STATS="/workspace/AReaL/areal/trainer/ppo/stats.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weight definitions (NOT cumulative - all gates)
declare -A WEIGHTS
WEIGHTS[behavioral_f2p]=0.35      # [pr_diff] infer_token_denominator works correctly
WEIGHTS[behavioral_actor_critic]=0.20  # [pr_diff] Actor/critic use helper correctly
WEIGHTS[regression_p2p]=0.15      # [repo_tests] Upstream test suite passes
WEIGHTS[style_rubric_stub]=0.15   # [static] Anti-stub depth check
WEIGHTS[config_no_wildcard]=0.08  # [agent_config] AGENTS.md style rules
WEIGHTS[config_no_bare_print]=0.07 # [agent_config] AGENTS.md style rules

# Results tracking
declare -A RESULTS
for key in behavioral_f2p behavioral_actor_critic regression_p2p style_rubric_stub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE 1: Syntax check ----------
for f in "$ACTOR" "$CRITIC"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: Syntax error in $(basename $f)"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS: Syntax OK"

# ---------- GATE 2: Can import function ----------
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')
try:
    from areal.trainer.ppo.stats import infer_token_denominator
    print("IMPORT PASS")
except Exception as e:
    print(f"IMPORT FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: Function importable"

# ---------- BEHAVIORAL 1 (35%): Fail-to-Pass: Function returns correct tensor shapes ----------
# [pr_diff] (0.35): infer_token_denominator correctly infers full token counts from metadata
python3 << 'PYEOF'
import sys
import torch
sys.path.insert(0, '/workspace/AReaL')

from areal.trainer.ppo.stats import infer_token_denominator

# Test 1: Prefer attention_mask (full batch metadata, not sliced)
input_data = {"attention_mask": torch.tensor([[1, 1, 0], [1, 1, 1]])}
fallback = torch.zeros(5)
result = infer_token_denominator(input_data, fallback)
if result.shape != torch.Size([2, 3]):
    print(f"F2P FAIL: attention_mask test expected [2,3], got {result.shape}")
    sys.exit(1)
if result.dtype != torch.bool:
    print(f"F2P FAIL: expected bool dtype, got {result.dtype}")
    sys.exit(1)

# Test 2: Fall back to cu_seqlens (for packed sequences)
input_data = {"cu_seqlens": torch.tensor([0, 4], dtype=torch.int32)}
fallback = torch.zeros(2)
result = infer_token_denominator(input_data, fallback)
if result.shape != torch.Size([4]):
    print(f"F2P FAIL: cu_seqlens test expected [4], got {result.shape}")
    sys.exit(1)

# Test 3: Fall back to input_ids when shapes match
input_data = {"input_ids": torch.tensor([[11, 12], [13, 14]])}
fallback = torch.zeros(2, 2)
result = infer_token_denominator(input_data, fallback)
if result.shape != torch.Size([2, 2]):
    print(f"F2P FAIL: input_ids test expected [2,2], got {result.shape}")
    sys.exit(1)

# Test 4: Final fallback to ones_like(fallback)
input_data = {"logprobs": torch.zeros(3)}
fallback = torch.zeros(4)
result = infer_token_denominator(input_data, fallback)
if result.shape != torch.Size([4]):
    print(f"F2P FAIL: fallback test expected [4], got {result.shape}")
    sys.exit(1)

print("BEHAVIORAL_F2P PASS")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_f2p]=1
    echo "TEST behavioral_f2p: PASS"
else
    echo "TEST behavioral_f2p: FAIL"
fi

# ---------- BEHAVIORAL 2 (20%): Actor/Critic integration ----------
# [pr_diff] (0.20): Actor and critic use infer_token_denominator in stats logging
python3 << 'PYEOF'
import sys
import ast
import re
sys.path.insert(0, '/workspace/AReaL')

# Check that actor calls infer_token_denominator with correct arguments
with open('/workspace/AReaL/areal/trainer/ppo/actor.py') as f:
    actor_src = f.read()

tree = ast.parse(actor_src)

# Find call to infer_token_denominator
found_call = False
old_pattern_present = False

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'infer_token_denominator':
            found_call = True
        # Check for attribute access like stats.infer_token_denominator
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'infer_token_denominator':
            found_call = True

# Check for old buggy pattern (would indicate bug not fixed)
if 'torch.ones_like(loss_mask, dtype=torch.bool)' in actor_src:
    old_pattern_present = True

if not found_call:
    print("BEHAVIORAL_ACTOR FAIL: No call to infer_token_denominator in actor")
    sys.exit(1)

if old_pattern_present:
    print("BEHAVIORAL_ACTOR FAIL: Old buggy pattern still present")
    sys.exit(1)

# Check critic
with open('/workspace/AReaL/areal/trainer/ppo/critic.py') as f:
    critic_src = f.read()

found_call_critic = False
for node in ast.walk(ast.parse(critic_src)):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'infer_token_denominator':
            found_call_critic = True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'infer_token_denominator':
            found_call_critic = True

if not found_call_critic:
    print("BEHAVIORAL_CRITIC FAIL: No call to infer_token_denominator in critic")
    sys.exit(1)

print("BEHAVIORAL_ACTOR_CRITIC PASS")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_actor_critic]=1
    echo "TEST behavioral_actor_critic: PASS"
else
    echo "TEST behavioral_actor_critic: FAIL"
fi

# ---------- GATE: Behavioral checks must pass before structural ----------
if [ ${RESULTS[behavioral_f2p]} -eq 0 ] || [ ${RESULTS[behavioral_actor_critic]} -eq 0 ]; then
    echo "SKIP: Structural checks gated behind behavioral pass"
    # Only config checks can still run (they're independent)
else
    # ---------- REGRESSION P2P (15%): Upstream test suite ----------
    # [repo_tests] test_ppo_stats.py from the repo validates the implementation
    cd /workspace/AReaL
    python3 -m pytest tests/test_ppo_stats.py -x --timeout=60 -q 2>/dev/null
    if [ $? -eq 0 ]; then
        RESULTS[regression_p2p]=1
        echo "TEST regression_p2p: PASS"
    else
        echo "TEST regression_p2p: FAIL (upstream tests failed)"
    fi

    # ---------- STYLE/RUBRIC STUB CHECK (15%): Function has meaningful implementation ----------
    # [static] Body depth > 3 statements AND uses conditional logic
    python3 << 'PYEOF'
import sys
import ast

with open('/workspace/AReaL/areal/trainer/ppo/stats.py') as f:
    src = f.read()

tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'infer_token_denominator':
        # Count non-docstring statements
        body = node.body
        non_docstring = [n for n in body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant)]

        if len(non_docstring) < 3:
            print("STUB FAIL: Function body too small")
            sys.exit(1)

        # Check for conditional logic (if statements)
        has_conditional = any(isinstance(n, ast.If) for n in ast.walk(node))
        if not has_conditional:
            print("STUB FAIL: No conditional logic (fallback chain)")
            sys.exit(1)

        print("STYLE_RUBRIC_STUB PASS")
        sys.exit(0)

print("STUB FAIL: Function not found")
sys.exit(1)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[style_rubric_stub]=1
        echo "TEST style_rubric_stub: PASS"
    else
        echo "TEST style_rubric_stub: FAIL"
    fi
fi

# ---------- CONFIG CHECKS (independent, lower weight) ----------
# [agent_config] (0.08): No wildcard imports — AGENTS.md style
python3 << 'PYEOF'
import sys
import ast
import os

files = ['/workspace/AReaL/areal/trainer/ppo/actor.py',
         '/workspace/AReaL/areal/trainer/ppo/critic.py',
         '/workspace/AReaL/areal/trainer/ppo/stats.py']

for f in files:
    if not os.path.isfile(f):
        continue
    with open(f) as file:
        src = file.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == '*' for alias in node.names):
                print(f"CONFIG_FAIL: Wildcard import in {f}")
                sys.exit(1)

print("CONFIG_NO_WILDCARD PASS")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[config_no_wildcard]=1
    echo "TEST config_no_wildcard: PASS"
else
    echo "TEST config_no_wildcard: FAIL"
fi

# [agent_config] (0.07): No bare print() calls — AGENTS.md line 80 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
python3 << 'PYEOF'
import sys
import ast
import os

files = ['/workspace/AReaL/areal/trainer/ppo/actor.py',
         '/workspace/AReaL/areal/trainer/ppo/critic.py',
         '/workspace/AReaL/areal/trainer/ppo/stats.py']

for f in files:
    if not os.path.isfile(f):
        continue
    with open(f) as file:
        src = file.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                # Check if it's just a comment ( shouldn't happen with ast)
                print(f"CONFIG_FAIL: Bare print() in {f}")
                sys.exit(1)

print("CONFIG_NO_BARE_PRINT PASS")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[config_no_bare_print]=1
    echo "TEST config_no_bare_print: PASS"
else
    echo "TEST config_no_bare_print: FAIL"
fi

# ---------- CALCULATE SCORE ----------
SCORE=$(python3 -c "
w={'behavioral_f2p':${WEIGHTS[behavioral_f2p]},'behavioral_actor_critic':${WEIGHTS[behavioral_actor_critic]},'regression_p2p':${WEIGHTS[regression_p2p]},'style_rubric_stub':${WEIGHTS[style_rubric_stub]},'config_no_wildcard':${WEIGHTS[config_no_wildcard]},'config_no_bare_print':${WEIGHTS[config_no_bare_print]}}
r={'behavioral_f2p':${RESULTS[behavioral_f2p]},'behavioral_actor_critic':${RESULTS[behavioral_actor_critic]},'regression_p2p':${RESULTS[regression_p2p]},'style_rubric_stub':${RESULTS[style_rubric_stub]},'config_no_wildcard':${RESULTS[config_no_wildcard]},'config_no_bare_print':${RESULTS[config_no_bare_print]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")

echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# Write detailed JSON report
cat > "$(dirname "$REWARD_FILE")/reward.json" << EOF
{
  "reward": $SCORE,
  "behavioral_f2p": ${RESULTS[behavioral_f2p]},
  "behavioral_actor_critic": ${RESULTS[behavioral_actor_critic]},
  "regression_p2p": ${RESULTS[regression_p2p]},
  "style_rubric_stub": ${RESULTS[style_rubric_stub]},
  "config_no_wildcard": ${RESULTS[config_no_wildcard]},
  "config_no_bare_print": ${RESULTS[config_no_bare_print]}
}
EOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
