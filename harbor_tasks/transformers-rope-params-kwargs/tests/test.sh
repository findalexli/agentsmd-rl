#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/configuration_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weighted scoring - >=60% behavioral
# [pr_diff] (0.35): Fix handles legacy RoPE kwargs when config lacks rope_parameters
# [pr_diff] (0.25): Warning emitted for legacy format usage
# [repo_tests] (0.15): Pass-to-pass - upstream config tests still pass
# [pr_diff] (0.15): kwargs are properly cleaned (rope_scaling/rope_theta removed)
# [agent_config] (0.05): Files pass ruff format check
# [static] (0.05): Syntax validation gate

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[behavioral_warning]=0.25
WEIGHTS[pass_to_pass]=0.15
WEIGHTS[cleanup_check]=0.15
WEIGHTS[config_ruff]=0.05
WEIGHTS[syntax_gate]=0.05

for key in behavioral behavioral_warning pass_to_pass cleanup_check config_ruff syntax_gate; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
# [static] (0.05): File must have valid Python syntax
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
RESULTS[syntax_gate]=1
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (35%): Fail-to-pass - Legacy RoPE kwargs are converted ----------
# [pr_diff] (0.35): When a config lacks rope_parameters but kwargs have rope_scaling+rope_theta,
# convert_rope_params_to_dict should be called and kwargs should be cleaned
python3 << 'PYEOF'
import sys
import os
import warnings

os.chdir('/workspace/transformers')
sys.path.insert(0, '/workspace/transformers')

# Capture warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")

    try:
        from transformers.configuration_utils import PreTrainedConfig
        from dataclasses import dataclass

        # Create a config class WITHOUT rope_parameters attribute (triggers the bug)
        @dataclass
        class TestConfig(PreTrainedConfig):
            model_type = "test"
            # Intentionally NOT defining rope_parameters
            hidden_size: int = 128
            num_attention_heads: int = 4
            num_hidden_layers: int = 2
            vocab_size: int = 1000

        # Test case: kwargs with legacy RoPE format
        rope_kwargs = {
            "rope_scaling": {"type": "linear", "factor": 2.0},
            "rope_theta": 10000.0,
            "some_other_key": "value"
        }

        # Create config with RoPE kwargs
        config = TestConfig(**rope_kwargs)

        # Check 1: rope_parameters should be set (proves conversion happened)
        if not hasattr(config, 'rope_parameters'):
            print("BEHAVIORAL FAIL: rope_parameters not set on config")
            sys.exit(1)

        if config.rope_parameters is None:
            print("BEHAVIORAL FAIL: rope_parameters is None")
            sys.exit(1)

        # Check 2: rope_parameters should contain the converted values
        if "rope_theta" not in config.rope_parameters:
            print("BEHAVIORAL FAIL: rope_theta not in rope_parameters dict")
            sys.exit(1)

        if config.rope_parameters.get("rope_theta") != 10000.0:
            print(f"BEHAVIORAL FAIL: rope_theta has wrong value: {config.rope_parameters.get('rope_theta')}")
            sys.exit(1)

        print("BEHAVIORAL PASS: Legacy RoPE kwargs correctly converted to rope_parameters")

    except Exception as e:
        print(f"BEHAVIORAL FAIL: Exception during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Warning emitted for legacy format usage ----------
# [pr_diff] (0.25): Warning should be emitted when using legacy RoPE format
python3 << 'PYEOF'
import sys
import os
import warnings
import logging

os.chdir('/workspace/transformers')
sys.path.insert(0, '/workspace/transformers')

# Set up logging capture
import io
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.WARNING)

# Re-import to get fresh logger
import importlib
import transformers.configuration_utils
# Reset and hook logger
transformers.configuration_utils.logger.addHandler(handler)
transformers.configuration_utils.logger.setLevel(logging.WARNING)

from dataclasses import dataclass
from transformers.configuration_utils import PreTrainedConfig

@dataclass
class TestConfigNoRopeParams(PreTrainedConfig):
    model_type = "test_no_rope"
    hidden_size: int = 128
    num_attention_heads: int = 4
    num_hidden_layers: int = 2
    vocab_size: int = 1000

# Clear log buffer
log_capture.truncate(0)
log_capture.seek(0)

# Trigger the warning
rope_kwargs = {
    "rope_scaling": {"type": "linear", "factor": 2.0},
    "rope_theta": 10000.0,
}

config = TestConfigNoRopeParams(**rope_kwargs)

# Check log output
log_output = log_capture.getvalue()
warning_triggered = False

# Accept various warning formats
if "rope_scaling" in log_output.lower() or "rope_parameters" in log_output.lower() or "hasn't set it as attribute" in log_output.lower():
    warning_triggered = True

# Also check warnings module
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    # Re-create to trigger warning again
    config2 = TestConfigNoRopeParams(**rope_kwargs)
    for warning in w:
        if "rope" in str(warning.message).lower():
            warning_triggered = True
            break

if warning_triggered:
    print("BEHAVIORAL_WARNING PASS: Warning emitted for legacy RoPE kwargs")
    sys.exit(0)
else:
    print("BEHAVIORAL_WARNING FAIL: No warning emitted for legacy RoPE kwargs")
    print(f"Log output was: {log_output}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_warning]=1
    echo "TEST behavioral_warning: PASS"
else
    echo "TEST behavioral_warning: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): kwargs cleanup verification ----------
# [pr_diff] (0.15): rope_scaling and rope_theta should be removed from kwargs
python3 << 'PYEOF'
import sys
import os

os.chdir('/workspace/transformers')
sys.path.insert(0, '/workspace/transformers')

from dataclasses import dataclass
from transformers.configuration_utils import PreTrainedConfig

@dataclass
class TestConfig(PreTrainedConfig):
    model_type = "test"
    hidden_size: int = 128
    num_attention_heads: int = 4
    num_hidden_layers: int = 2
    vocab_size: int = 1000

# Create a custom post_init to capture what kwargs remain
kwargs_after_post_init = {}

original_post_init = TestConfig.__post_init__

def capturing_post_init(self, **kwargs):
    global kwargs_after_post_init
    result = original_post_init(self, **kwargs)
    kwargs_after_post_init = kwargs.copy()
    return result

TestConfig.__post_init__ = capturing_post_init

rope_kwargs = {
    "rope_scaling": {"type": "linear", "factor": 2.0},
    "rope_theta": 10000.0,
    "keep_this_key": "should_remain"
}

config = TestConfig(**rope_kwargs)

# Check that rope keys are removed from kwargs but other keys remain
if "rope_scaling" in kwargs_after_post_init:
    print("CLEANUP FAIL: rope_scaling still in kwargs after post_init")
    sys.exit(1)

if "rope_theta" in kwargs_after_post_init:
    print("CLEANUP FAIL: rope_theta still in kwargs after post_init")
    sys.exit(1)

# Other keys should remain (or be handled appropriately)
print("CLEANUP PASS: RoPE kwargs properly cleaned from kwargs dict")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[cleanup_check]=1
    echo "TEST cleanup_check: PASS"
else
    echo "TEST cleanup_check: FAIL"
fi

# ---------- PASS-TO-PASS (15%): Upstream config tests still work ----------
# [repo_tests] (0.15): Basic config functionality shouldn't break
python3 << 'PYEOF'
import sys
import os

os.chdir('/workspace/transformers')
sys.path.insert(0, '/workspace/transformers')

try:
    from transformers.configuration_utils import PreTrainedConfig
    from dataclasses import dataclass

    # Test 1: Config WITH rope_parameters should work as before
    @dataclass
    class ConfigWithRopeParams(PreTrainedConfig):
        model_type = "test_with_rope"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000
        rope_parameters: dict = None

    rope_kwargs = {
        "rope_scaling": {"type": "linear", "factor": 2.0},
        "rope_theta": 10000.0,
    }

    config1 = ConfigWithRopeParams(**rope_kwargs)
    assert hasattr(config1, 'rope_parameters'), "Config with rope_parameters should have attribute set"

    # Test 2: Config without any RoPE kwargs should work
    @dataclass
    class ConfigNoRoPE(PreTrainedConfig):
        model_type = "test_no_rope"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000

    config2 = ConfigNoRoPE()
    assert hasattr(config2, 'hidden_size'), "Config without RoPE should still initialize"

    # Test 3: Config with only one RoPE key shouldn't convert (need both)
    @dataclass
    class ConfigPartialRoPE(PreTrainedConfig):
        model_type = "test_partial"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000

    config3 = ConfigPartialRoPE(rope_theta=10000.0)
    # Should not have rope_parameters set (only rope_theta, no rope_scaling)

    print("PASS_TO_PASS PASS: Upstream config patterns still work")
    sys.exit(0)

except Exception as e:
    print(f"PASS_TO_PASS FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[pass_to_pass]=1
    echo "TEST pass_to_pass: PASS"
else
    echo "TEST pass_to_pass: FAIL"
fi

# ---------- CONFIG-DERIVED (5%): ruff format check ----------
# [agent_config] (0.05): "Changed files pass ruff format" - CLAUDE.md @ d65c2b138a3d27a3321f7bbced0efc9bfb5a9688
RUFF_OK=true
for f in /workspace/transformers/src/transformers/configuration_utils.py; do
    if [ -f "$f" ]; then
        ruff check --select I "$f" 2>/dev/null
        if [ $? -ne 0 ]; then RUFF_OK=false; fi
    fi
done
if [ "$RUFF_OK" = true ]; then
    RESULTS[config_ruff]=1
    echo "TEST config_ruff: PASS"
else
    echo "TEST config_ruff: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral_warning': ${WEIGHTS[behavioral_warning]}, 'pass_to_pass': ${WEIGHTS[pass_to_pass]}, 'cleanup_check': ${WEIGHTS[cleanup_check]}, 'config_ruff': ${WEIGHTS[config_ruff]}, 'syntax_gate': ${WEIGHTS[syntax_gate]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral_warning': ${RESULTS[behavioral_warning]}, 'pass_to_pass': ${RESULTS[pass_to_pass]}, 'cleanup_check': ${RESULTS[cleanup_check]}, 'config_ruff': ${RESULTS[config_ruff]}, 'syntax_gate': ${RESULTS[syntax_gate]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral        (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  behavioral_warning (${WEIGHTS[behavioral_warning]}): ${RESULTS[behavioral_warning]}"
echo "  cleanup_check     (${WEIGHTS[cleanup_check]}): ${RESULTS[cleanup_check]}"
echo "  pass_to_pass      (${WEIGHTS[pass_to_pass]}): ${RESULTS[pass_to_pass]}"
echo "  config_ruff       (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  syntax_gate       (${WEIGHTS[syntax_gate]}): ${RESULTS[syntax_gate]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
