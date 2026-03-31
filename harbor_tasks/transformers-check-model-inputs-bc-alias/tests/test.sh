#!/usr/bin/env bash
set +e

REPO="/workspace/transformers"
SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(echo "$TOTAL + $weight" | bc)
    if [ "$pass" -eq 1 ]; then
        SCORE=$(echo "$SCORE + $weight" | bc)
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

# ── GATE: Syntax check ──────────────────────────────────────────────────
# [pr_diff] (gate): File must be valid Python
python3 -c "
import ast, sys
try:
    ast.parse(open('$REPO/src/transformers/utils/generic.py').read())
except SyntaxError as e:
    print(f'Syntax error: {e}', file=sys.stderr)
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error in generic.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── F2P 1: check_model_inputs as decorator produces same behavior as merge_with_config_defaults ──
# [pr_diff] (0.40): Decorated method merges config defaults identically to merge_with_config_defaults
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.utils.generic import check_model_inputs, merge_with_config_defaults

class FakeConfig:
    use_cache = True
    output_attentions = False

class Model1:
    def __init__(self):
        self.config = FakeConfig()
        self.training = False

    @check_model_inputs
    def forward(self, use_cache=None, output_attentions=None):
        return {'use_cache': use_cache, 'output_attentions': output_attentions}

class Model2:
    def __init__(self):
        self.config = FakeConfig()
        self.training = False

    @merge_with_config_defaults
    def forward(self, use_cache=None, output_attentions=None):
        return {'use_cache': use_cache, 'output_attentions': output_attentions}

m1 = Model1()
m2 = Model2()

# Test 1: no kwargs — should pull from config
r1 = m1.forward()
r2 = m2.forward()
assert r1 == r2, f'No-args results differ: {r1} vs {r2}'
assert r1['use_cache'] == True, f'Expected use_cache=True from config, got {r1}'
assert r1['output_attentions'] == False, f'Expected output_attentions=False from config, got {r1}'

# Test 2: explicit kwargs should override config
r1 = m1.forward(use_cache=False)
r2 = m2.forward(use_cache=False)
assert r1 == r2, f'Explicit kwarg results differ: {r1} vs {r2}'
assert r1['use_cache'] == False, f'Expected use_cache=False (explicit), got {r1}'

# Test 3: mixed — some explicit, some from config
r1 = m1.forward(output_attentions=True)
r2 = m2.forward(output_attentions=True)
assert r1 == r2, f'Mixed results differ: {r1} vs {r2}'
assert r1['use_cache'] == True, f'Expected use_cache=True from config'
assert r1['output_attentions'] == True, f'Expected output_attentions=True (explicit)'

print('OK: check_model_inputs delegates correctly — all scenarios match merge_with_config_defaults')
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.40 1 "pr_diff" "check_model_inputs delegates to merge_with_config_defaults (multi-arg, mixed scenarios)"
else
    add_result 0.40 0 "pr_diff" "check_model_inputs delegates to merge_with_config_defaults (multi-arg, mixed scenarios)"
fi

# ── F2P 3: the decorated function actually wraps (not passthrough or None) ──
# [pr_diff] (0.25): check_model_inputs returns a working wrapper, not the original or None
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.utils.generic import check_model_inputs, merge_with_config_defaults

class Cfg:
    val = 42

class M:
    def __init__(self):
        self.config = Cfg()
        self.training = False

    @check_model_inputs
    def forward(self, val=None):
        return val

m = M()
# Must be callable (not None from a stub)
result = m.forward()
assert result == 42, f'Expected 42 from config default, got {result}'
# Explicit override
result2 = m.forward(val=99)
assert result2 == 99, f'Expected 99 from explicit kwarg, got {result2}'
print('OK: wrapper is functional, not a stub or None')
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.25 1 "pr_diff" "check_model_inputs wrapper is functional (pulls config defaults, accepts overrides)"
else
    add_result 0.25 0 "pr_diff" "check_model_inputs wrapper is functional (pulls config defaults, accepts overrides)"
fi

# ── F2P 4: deprecation warning is emitted ────────────────────────────────
# [pr_diff] (0.15): check_model_inputs emits a deprecation/rename warning
python3 -c "
import sys, warnings, logging, io
sys.path.insert(0, '$REPO/src')

# Capture both logger and warnings output
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.DEBUG)

from transformers.utils import generic as gen_mod
gen_logger = logging.getLogger(gen_mod.__name__)
gen_logger.addHandler(handler)
gen_logger.setLevel(logging.DEBUG)

# Clear warning_once cache if present
if hasattr(gen_logger, '_seen_warnings'):
    gen_logger._seen_warnings = set()

from transformers.utils.generic import check_model_inputs

# Capture warnings module too
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    def dummy(self, x=None): return x
    check_model_inputs(dummy)

log_output = log_capture.getvalue().lower()
warn_output = ' '.join(str(x.message).lower() for x in w)
combined = log_output + ' ' + warn_output

# Accept any of: logger warning, warnings.warn, or FutureWarning
has_deprecation = ('deprecat' in combined or 'rename' in combined or
                   'merge_with_config_defaults' in combined or
                   'check_model_inputs' in combined)
assert has_deprecation, f'Expected deprecation/rename warning, got logger={repr(log_output)} warnings={repr(warn_output)}'
print('OK: deprecation warning emitted')
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.15 1 "pr_diff" "check_model_inputs emits deprecation/rename warning"
else
    add_result 0.15 0 "pr_diff" "check_model_inputs emits deprecation/rename warning"
fi

# ── P2P: merge_with_config_defaults still works ──────────────────────────
# [pr_diff] (0.10): merge_with_config_defaults is unaffected by the alias addition
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.utils.generic import merge_with_config_defaults

class FakeConfig:
    use_cache = False

class FakeModel:
    def __init__(self):
        self.config = FakeConfig()
        self.training = False

    @merge_with_config_defaults
    def forward(self, use_cache=None):
        return {'use_cache': use_cache}

m = FakeModel()
# Explicit kwarg should take precedence
result = m.forward(use_cache=True)
assert result['use_cache'] == True, f'Expected True, got {result}'
# Config default should be used when not passed
result2 = m.forward()
assert result2['use_cache'] == False, f'Expected False from config, got {result2}'
print('OK: merge_with_config_defaults still works correctly')
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.10 1 "pr_diff" "merge_with_config_defaults still works correctly"
else
    add_result 0.10 0 "pr_diff" "merge_with_config_defaults still works correctly"
fi

# ── Config: ruff lint check ───────────────────────────────────────────────
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 2620c4d
if command -v ruff &>/dev/null; then
    ruff check "$REPO/src/transformers/utils/generic.py" --select E,W --quiet 2>&1
    if [ $? -eq 0 ]; then
        add_result 0.05 1 "agent_config" "ruff lint passes on generic.py"
    else
        add_result 0.05 0 "agent_config" "ruff lint passes on generic.py"
    fi
else
    python3 -c "
import ast
code = open('$REPO/src/transformers/utils/generic.py').read()
ast.parse(code)
print('OK')
" 2>&1
    if [ $? -eq 0 ]; then
        add_result 0.05 1 "agent_config" "basic lint check passes (ruff not available)"
    else
        add_result 0.05 0 "agent_config" "basic lint check passes (ruff not available)"
    fi
fi

# ── P2P: upstream test for generic.py utilities ──────────────────────────
# [repo_tests] (0.05): Existing upstream tests for utils.generic still pass
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
# Smoke-test a few utilities from the same module to ensure nothing is broken
from transformers.utils.generic import (
    merge_with_config_defaults,
    ExplicitEnum,
    PaddingStrategy,
)
# ExplicitEnum should work
assert PaddingStrategy('longest') == PaddingStrategy.LONGEST
print('OK: upstream generic.py utilities still functional')
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.05 1 "repo_tests" "upstream generic.py utilities still work"
else
    add_result 0.05 0 "repo_tests" "upstream generic.py utilities still work"
fi

# ── Summary ─────────────────────────────────────────────────────────────
echo ""
echo "===== TEST RESULTS ====="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt

# Compute component breakdowns
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.80), 2))")
REGRESSION=$(python3 -c "
s = $SCORE
b = min(s, 0.80)
print(round(min(s - b, 0.15), 2))
")
CONFIG=$(python3 -c "
s = $SCORE
print(round(max(s - 0.95, 0.0), 2))
")
echo "{\"reward\": $SCORE, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
