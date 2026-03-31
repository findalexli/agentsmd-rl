#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
PASS=0
FAIL_DETAILS=""

log_check() {
    local name="$1" weight="$2" result="$3" tag="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$result" = "pass" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        PASS=$((PASS + 1))
        echo "  PASS ($weight) $tag: $name"
    else
        FAIL_DETAILS="$FAIL_DETAILS\n  FAIL ($weight) $tag: $name"
        echo "  FAIL ($weight) $tag: $name"
    fi
}

cd /workspace/transformers

TARGET="src/transformers/models/nemotron_h/configuration_nemotron_h.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Modified file must parse without syntax errors
if python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"; then
    echo "  GATE PASSED: syntax OK"
else
    echo "  GATE FAILED: syntax error in $TARGET"
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== Fail-to-Pass: Docstring params match class attributes ==="

# [pr_diff] (0.35): Documented params in docstring must correspond to actual class attributes
# The bug: docstring lists old names (mamba_dt_min etc) that aren't real attributes.
# A correct fix renames them to the actual attribute names. This test imports the class,
# extracts docstring param names, and verifies each one exists as a class attribute.
RESULT_F2P=$(python3 -c "
import re, sys, inspect

sys.path.insert(0, 'src')
from transformers.models.nemotron_h.configuration_nemotron_h import NemotronHConfig

with open('$TARGET') as f:
    content = f.read()

# Extract the class docstring
class_match = re.search(r'class NemotronHConfig.*?\"\"\"(.*?)\"\"\"', content, re.DOTALL)
if not class_match:
    print('NO_DOCSTRING')
    sys.exit(1)

docstring = class_match.group(1)

# Extract all documented parameter names (indented name followed by type in parens)
doc_params = re.findall(r'^\s{4,}(\w+)\s*\(', docstring, re.MULTILINE)
if len(doc_params) < 5:
    print(f'TOO_FEW_PARAMS:{len(doc_params)}')
    sys.exit(1)

# Get actual class-level attribute names from annotations + instance attrs
sig = inspect.signature(NemotronHConfig.__init__)
init_params = set(sig.parameters.keys()) - {'self', 'kwargs', 'args'}

# Also include class-level annotations
if hasattr(NemotronHConfig, '__annotations__'):
    init_params.update(NemotronHConfig.__annotations__.keys())

# Every documented param must be an actual parameter
bad = [p for p in doc_params if p not in init_params]
if bad:
    print('MISMATCH:' + ','.join(sorted(set(bad))))
    sys.exit(1)
print('OK')
" 2>&1) || true

if [ "$RESULT_F2P" = "OK" ]; then
    log_check "Documented params match actual class attributes/init params" 0.35 pass "[pr_diff]"
else
    log_check "Documented params match actual class attributes/init params ($RESULT_F2P)" 0.35 fail "[pr_diff]"
fi

echo ""
echo "=== Fail-to-Pass: Required new params documented ==="

# [pr_diff] (0.20): The four mamba attrs (n_groups, expand, use_conv_bias, chunk_size)
# must appear as documented parameters in the docstring.
# These are actual class attributes that were missing because the docstring used old names.
RESULT_NEW=$(python3 -c "
import re, sys

with open('$TARGET') as f:
    content = f.read()

class_match = re.search(r'class NemotronHConfig.*?\"\"\"(.*?)\"\"\"', content, re.DOTALL)
if not class_match:
    print('NO_DOCSTRING')
    sys.exit(1)

docstring = class_match.group(1)

required = ['n_groups', 'expand', 'use_conv_bias', 'chunk_size']
found = []
for param in required:
    pattern = r'^\s+' + re.escape(param) + r'\s*\('
    if re.search(pattern, docstring, re.MULTILINE):
        found.append(param)

missing = set(required) - set(found)
if missing:
    print('MISSING:' + ','.join(sorted(missing)))
    sys.exit(1)
print('OK')
" 2>&1) || true

if [ "$RESULT_NEW" = "OK" ]; then
    log_check "Docstring documents n_groups, expand, use_conv_bias, chunk_size" 0.20 pass "[pr_diff]"
else
    log_check "Docstring documents n_groups, expand, use_conv_bias, chunk_size ($RESULT_NEW)" 0.20 fail "[pr_diff]"
fi

echo ""
echo "=== Fail-to-Pass: Old deprecated names removed ==="

# [pr_diff] (0.15): Old backward-compat alias names must NOT appear as documented params.
# mamba_dt_min → time_step_min, mamba_dt_max → time_step_max, etc.
RESULT_OLD=$(python3 -c "
import re, sys

with open('$TARGET') as f:
    content = f.read()

class_match = re.search(r'class NemotronHConfig.*?\"\"\"(.*?)\"\"\"', content, re.DOTALL)
if not class_match:
    sys.exit(1)

docstring = class_match.group(1)

old_names = ['mamba_dt_min', 'mamba_dt_max', 'mamba_dt_limit', 'mamba_dt_init_floor']
found_old = []
for param in old_names:
    pattern = r'^\s+' + re.escape(param) + r'\s*\('
    if re.search(pattern, docstring, re.MULTILINE):
        found_old.append(param)

if found_old:
    print('FOUND_OLD:' + ','.join(found_old))
    sys.exit(1)
print('OK')
" 2>&1) || true

if [ "$RESULT_OLD" = "OK" ]; then
    log_check "Old backward-compat param names removed from docstring" 0.15 pass "[pr_diff]"
else
    log_check "Old backward-compat param names removed from docstring ($RESULT_OLD)" 0.15 fail "[pr_diff]"
fi

echo ""
echo "=== Pass-to-Pass: Config instantiation ==="

# [pr_diff] (0.10): NemotronHConfig must still be importable and instantiable
RESULT_INST=$(python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.models.nemotron_h.configuration_nemotron_h import NemotronHConfig

config = NemotronHConfig()

# Verify the new attribute names exist with sensible defaults
assert hasattr(config, 'n_groups'), 'Missing n_groups attr'
assert hasattr(config, 'expand'), 'Missing expand attr'
assert hasattr(config, 'use_conv_bias'), 'Missing use_conv_bias attr'
assert hasattr(config, 'chunk_size'), 'Missing chunk_size attr'
assert hasattr(config, 'time_step_min'), 'Missing time_step_min attr'
assert hasattr(config, 'time_step_max'), 'Missing time_step_max attr'

# Verify backward-compat aliases still work via __post_init__
config2 = NemotronHConfig(mamba_dt_min=0.005)
assert config2.time_step_min == 0.005, f'backward compat broken: {config2.time_step_min}'

print('OK')
" 2>&1) || true

if [ "$RESULT_INST" = "OK" ]; then
    log_check "Config instantiation and attribute access works" 0.10 pass "[pr_diff]"
else
    log_check "Config instantiation and attribute access works ($RESULT_INST)" 0.10 fail "[pr_diff]"
fi

echo ""
echo "=== Pass-to-Pass: Existing documented params preserved ==="

# [pr_diff] (0.10): Pre-existing documented params must remain in the docstring
RESULT_P2P=$(python3 -c "
import re, sys

with open('$TARGET') as f:
    content = f.read()

class_match = re.search(r'class NemotronHConfig.*?\"\"\"(.*?)\"\"\"', content, re.DOTALL)
if not class_match:
    sys.exit(1)

docstring = class_match.group(1)

existing_params = [
    'mamba_hidden_act', 'mamba_ssm_cache_dtype',
    'moe_shared_expert_intermediate_size', 'moe_latent_size',
    'use_mamba_kernels', 'ssm_state_size',
    'num_logits_to_keep', 'use_bias', 'residual_in_fp32',
]
missing = []
for param in existing_params:
    pattern = r'^\s+' + re.escape(param) + r'\s*\('
    if not re.search(pattern, docstring, re.MULTILINE):
        missing.append(param)

if missing:
    print('MISSING:' + ','.join(missing))
    sys.exit(1)
print('OK')
" 2>&1) || true

if [ "$RESULT_P2P" = "OK" ]; then
    log_check "Existing documented params preserved" 0.10 pass "[pr_diff]"
else
    log_check "Existing documented params preserved ($RESULT_P2P)" 0.10 fail "[pr_diff]"
fi

echo ""
echo "=== Config-derived: ruff format compliance ==="

# [agent_config] (0.10): "make style runs formatters and linters (ruff)" — CLAUDE.md:2
if python3 -m ruff format --check "$TARGET" >/dev/null 2>&1; then
    log_check "ruff format passes" 0.10 pass "[agent_config]"
else
    log_check "ruff format passes" 0.10 fail "[agent_config]"
fi

echo ""
echo "=== Summary ==="
echo "  Score: $SCORE / $TOTAL"
echo -e "$FAIL_DETAILS"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
data = {
    'reward': score,
    'behavioral': min(score, 0.70),
    'regression': min(max(score - 0.70, 0), 0.20),
    'config': min(max(score - 0.90, 0), 0.10),
    'style_rubric': 0.0
}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
