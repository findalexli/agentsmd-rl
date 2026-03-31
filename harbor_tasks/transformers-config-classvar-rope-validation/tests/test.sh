#!/usr/bin/env bash
set +e
set -uo pipefail

SCORE=0
REPO="/workspace/transformers"

log() { echo "[$1] $2 (weight=$3)"; }

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (GATE): Modified files must parse without syntax errors
GATE_PASS=1
for f in \
    src/transformers/configuration_utils.py \
    src/transformers/modeling_rope_utils.py \
    src/transformers/utils/auto_docstring.py \
    utils/check_config_attributes.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        log GATE "Syntax error in $f" 0
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "GATE FAILED: syntax errors found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log GATE "All modified files parse OK" 0

########################################################################
# BEHAVIORAL: Fail-to-pass tests (weight = 0.75)
########################################################################

# --- Test 1: validate_rope with empty dict does not mutate the dict ---
# [pr_diff] (0.20): empty rope_parameters dict must be handled gracefully
# On buggy code: empty dict gets wrapped and mutated (rope_type added)
# On fix: early return, dict stays empty
# On stub: no-op also leaves dict empty (caught by T2)
T1=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_rope_utils import validate_rope

class Config:
    def __init__(self):
        self.rope_parameters = {}
        self.layer_types = None

config = Config()
original = dict(config.rope_parameters)  # copy
try:
    validate_rope(config)
except Exception as e:
    # Crash on empty dict is also a failure
    print(f'FAIL: crashed: {e}')
    sys.exit(0)

if config.rope_parameters == original:
    print('PASS')
else:
    print(f'FAIL: rope_parameters mutated from {original} to {dict(config.rope_parameters)}')
" 2>&1)

if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    log PASS "validate_rope handles empty dict without mutation" 0.20
else
    log FAIL "validate_rope empty dict: $T1" 0.20
fi

# --- Test 2: validate_rope actually dispatches validation (anti-stub) ---
# [pr_diff] (0.15): validate_rope must still validate non-empty rope configs
# Uses a custom config with a mock validation method to verify dispatch
T2=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_rope_utils import validate_rope

class Config:
    dispatch_count = 0
    def __init__(self):
        self.rope_parameters = {'rope_type': 'test_dispatch', 'factor': 1.0}
        self.layer_types = None
        self.ignore_keys_at_rope_validation = set()
    def _validate_test_dispatch_rope_parameters(self, params, ignore_keys=None):
        Config.dispatch_count += 1

config = Config()
validate_rope(config)
if Config.dispatch_count > 0:
    print('PASS')
else:
    print('FAIL: validation function was never dispatched — validate_rope may be stubbed')
" 2>&1)

if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    log PASS "validate_rope dispatches validation for real configs" 0.15
else
    log FAIL "validate_rope dispatch: $T2" 0.15
fi

# --- Test 3: transformers_version is NOT ClassVar ---
# [pr_diff] (0.20): transformers_version must be instance attr, not ClassVar
# On buggy code: ClassVar excludes it from dataclasses.fields()
# On fix: it appears in fields and/or annotation is not ClassVar
T3=$(python3 -c "
import sys, dataclasses
sys.path.insert(0, '$REPO/src')
from transformers.configuration_utils import PreTrainedConfig

# Check 1: Is it in dataclasses.fields?
try:
    field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
    if 'transformers_version' in field_names:
        print('PASS')
        sys.exit(0)
except TypeError:
    pass  # Not a dataclass, check annotation

# Check 2: Annotation must not be ClassVar
ann = PreTrainedConfig.__annotations__.get('transformers_version', '')
ann_str = str(ann)
if 'ClassVar' in ann_str:
    print('FAIL: transformers_version is still ClassVar')
else:
    print('PASS')
" 2>&1)

if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    log PASS "transformers_version is instance attr" 0.20
else
    log FAIL "transformers_version: $T3" 0.20
fi

# --- Test 4: architectures is NOT ClassVar ---
# [pr_diff] (0.20): architectures must be instance attr, not ClassVar
T4=$(python3 -c "
import sys, dataclasses
sys.path.insert(0, '$REPO/src')
from transformers.configuration_utils import PreTrainedConfig

try:
    field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
    if 'architectures' in field_names:
        print('PASS')
        sys.exit(0)
except TypeError:
    pass

ann = PreTrainedConfig.__annotations__.get('architectures', '')
ann_str = str(ann)
if 'ClassVar' in ann_str:
    print('FAIL: architectures is still ClassVar')
else:
    print('PASS')
" 2>&1)

if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    log PASS "architectures is instance attr" 0.20
else
    log FAIL "architectures: $T4" 0.20
fi

########################################################################
# PASS-TO-PASS: Regression checks (weight = 0.15)
########################################################################

# --- Test 5: auto_docstring _process_regular_parameters has filtering capability ---
# [pr_diff] (0.05): docstring generation must support parameter filtering
# The buggy version has 8 parameters; any fix adds at least one filtering param
T5=$(python3 -c "
import sys, inspect
sys.path.insert(0, '$REPO/src')
from transformers.utils.auto_docstring import _process_regular_parameters

sig = inspect.signature(_process_regular_parameters)
param_count = len(sig.parameters)
if param_count > 8:
    print('PASS')
else:
    print(f'FAIL: _process_regular_parameters has {param_count} params (expected >8 with filtering)')
" 2>&1)

if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "auto_docstring has filtering capability" 0.05
else
    log FAIL "auto_docstring: $T5" 0.05
fi

# --- Test 6: validate_rope still returns cleanly for None ---
# [pr_diff] (0.05): validate_rope handles None rope_parameters
T6=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_rope_utils import validate_rope

class Config:
    def __init__(self):
        self.rope_parameters = None

try:
    validate_rope(Config())
    print('PASS')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1)

if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "validate_rope handles None" 0.05
else
    log FAIL "validate_rope None: $T6" 0.05
fi

# --- Test 7: Upstream test ---
# [pr_diff] (0.05): test_config_common_kwargs_is_complete passes
T7=$(cd "$REPO" && python3 -m pytest tests/utils/test_configuration_utils.py::PreTrainedConfigTest::test_config_common_kwargs_is_complete -x --tb=short --no-header -q 2>&1)

if echo "$T7" | grep -q "passed"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "upstream test_config_common_kwargs_is_complete passes" 0.05
else
    log FAIL "upstream test: $T7" 0.05
fi

########################################################################
# CONFIG-DERIVED: Agent config checks (weight = 0.10)
########################################################################

# --- Test 8: check_config_attributes allowlist includes the fields ---
# [agent_config] (0.05): "make check-repo" passes attribute checks — CLAUDE.md:5 @ eb3d67aa
T8=$(python3 -c "
import sys, ast
with open('$REPO/utils/check_config_attributes.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'ATTRIBUTES_TO_ALLOW':
                vals = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                has_tv = 'transformers_version' in vals
                has_arch = 'architectures' in vals
                if has_tv and has_arch:
                    print('PASS')
                else:
                    missing = []
                    if not has_tv: missing.append('transformers_version')
                    if not has_arch: missing.append('architectures')
                    print(f'FAIL: missing from ATTRIBUTES_TO_ALLOW: {missing}')
                sys.exit(0)
print('FAIL: ATTRIBUTES_TO_ALLOW not found')
" 2>&1)

if echo "$T8" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "check_config_attributes allowlist updated" 0.05
else
    log FAIL "check_config_attributes: $T8" 0.05
fi

# --- Test 9: ruff lint check on changed files ---
# [agent_config] (0.05): "make style" runs ruff — CLAUDE.md:2 @ eb3d67aa
T9=$(cd "$REPO" && python3 -m ruff check \
    src/transformers/configuration_utils.py \
    src/transformers/modeling_rope_utils.py \
    src/transformers/utils/auto_docstring.py \
    --select E,W --quiet 2>&1)

if [ $? -eq 0 ] || [ -z "$T9" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "ruff lint clean on changed files" 0.05
else
    log FAIL "ruff issues: $T9" 0.05
fi

########################################################################
# SUMMARY
########################################################################

echo ""
echo "=== Score: $SCORE / 1.00 ==="

FINAL=$(python3 -c "print(round(float('$SCORE'), 4))")

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
echo "{\"reward\": $FINAL}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
