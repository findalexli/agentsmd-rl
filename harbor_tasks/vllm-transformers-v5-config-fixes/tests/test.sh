#!/usr/bin/env bash
# Verifier for vllm-transformers-v5-config-fixes
#
# PR fixes: (1) super().__init__() ordering in 5 config classes for transformers v5
#           (2) step3p5 layer_types cropping
#           (3) deepseek_vl2 kwargs.pop + DeepseekVLV2TextConfig
#           (4) AutoConfig registration for non-speculative configs
#
set +e

REPO="/workspace/vllm"
mkdir -p /logs/verifier

# Helper: load a single config module via importlib (avoids importing all of vllm/torch)
load_config_module() {
    python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('mod', '$1')
mod = importlib.util.module_from_spec(spec)
# Ensure vllm.transformers_utils.configs package can resolve
sys.modules.setdefault('vllm', type(sys)('vllm'))
sys.modules.setdefault('vllm.transformers_utils', type(sys)('vllm.transformers_utils'))
sys.modules.setdefault('vllm.transformers_utils.configs', type(sys)('vllm.transformers_utils.configs'))
spec.loader.exec_module(mod)
" 2>&1
}

###############################################################################
# GATE: Python syntax validity on all changed files
###############################################################################
CHANGED_FILES=(
    "$REPO/vllm/transformers_utils/config.py"
    "$REPO/vllm/transformers_utils/configs/colmodernvbert.py"
    "$REPO/vllm/transformers_utils/configs/deepseek_vl2.py"
    "$REPO/vllm/transformers_utils/configs/flex_olmo.py"
    "$REPO/vllm/transformers_utils/configs/isaac.py"
    "$REPO/vllm/transformers_utils/configs/qwen3_next.py"
    "$REPO/vllm/transformers_utils/configs/step3p5.py"
)
echo "=== GATE: Python syntax check ==="
for f in "${CHANGED_FILES[@]}"; do
    if [ -f "$f" ]; then
        python3 -c "import ast; ast.parse(open('$f').read())" 2>&1
        if [ $? -ne 0 ]; then
            echo "GATE FAILED: syntax error in $f"
            echo "0.0" > /logs/verifier/reward.txt
            exit 0
        fi
    fi
done
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: step3p5 layer_types cropping)    = 0.20
#   TEST 2 (fail-to-pass: config instantiation v5)         = 0.20
#   TEST 3 (fail-to-pass: deepseek_vl2 config)             = 0.15
#   TEST 4 (fail-to-pass: config.py AutoConfig separation) = 0.10
#   TEST 5 (pass-to-pass: modules importable)              = 0.10
#   TEST 6 (structural: super().__init__() ordering)        = 0.10
#   TEST 7 (anti-stub)                                     = 0.05
#   TEST 8 (config-derived: no bare pip)                   = 0.10
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [pr_diff] (0.20): Step3p5Config layer_types cropping
# The buggy code doesn't crop layer_types to num_hidden_layers length.
# This test instantiates the config with a layer_types that's too long
# and checks that it gets cropped.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.20) Step3p5Config crops layer_types to num_hidden_layers"
python3 << 'PYEOF'
import importlib.util, sys, types

# Set up minimal vllm package stubs so the module can be loaded
for name in ['vllm', 'vllm.transformers_utils', 'vllm.transformers_utils.configs']:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

spec = importlib.util.spec_from_file_location(
    'step3p5',
    '/workspace/vllm/vllm/transformers_utils/configs/step3p5.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

Step3p5Config = mod.Step3p5Config

# Create config with layer_types longer than num_hidden_layers
# num_hidden_layers defaults to some value; we pass it explicitly
try:
    config = Step3p5Config(num_hidden_layers=4, layer_types=["full", "full", "full", "full", "extra1", "extra2"])
except Exception as e:
    print(f"FAIL: instantiation crashed: {e}")
    sys.exit(1)

if not hasattr(config, 'layer_types') or config.layer_types is None:
    print("FAIL: config.layer_types is None or missing")
    sys.exit(1)

if len(config.layer_types) != 4:
    print(f"FAIL: layer_types has length {len(config.layer_types)}, expected 4 (num_hidden_layers)")
    print(f"  layer_types = {config.layer_types}")
    sys.exit(1)

print(f"PASS: layer_types correctly cropped to length {len(config.layer_types)}")
sys.exit(0)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [pr_diff] (0.20): Config instantiation under transformers v5
# ColModernVBertConfig and FlexOlmoConfig crash on v5 with buggy code
# because super().__init__() validates before attributes are set.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.20) ColModernVBertConfig + FlexOlmoConfig instantiation"
python3 << 'PYEOF'
import importlib.util, sys, types

for name in ['vllm', 'vllm.transformers_utils', 'vllm.transformers_utils.configs']:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

passed = 0
total = 2

# Test ColModernVBertConfig
try:
    spec = importlib.util.spec_from_file_location(
        'colmodernvbert',
        '/workspace/vllm/vllm/transformers_utils/configs/colmodernvbert.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    config = mod.ColModernVBertConfig()
    if hasattr(config, 'embedding_dim') and config.embedding_dim == 128:
        print("  ColModernVBertConfig: PASS")
        passed += 1
    else:
        print(f"  ColModernVBertConfig: FAIL (embedding_dim not set correctly)")
except Exception as e:
    print(f"  ColModernVBertConfig: FAIL ({type(e).__name__}: {e})")

# Test FlexOlmoConfig
try:
    spec = importlib.util.spec_from_file_location(
        'flex_olmo',
        '/workspace/vllm/vllm/transformers_utils/configs/flex_olmo.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    config = mod.FlexOlmoConfig()
    if hasattr(config, 'vocab_size') and hasattr(config, 'hidden_size'):
        print("  FlexOlmoConfig: PASS")
        passed += 1
    else:
        print("  FlexOlmoConfig: FAIL (attributes not set)")
except Exception as e:
    print(f"  FlexOlmoConfig: FAIL ({type(e).__name__}: {e})")

if passed == total:
    print(f"PASS: {passed}/{total} configs instantiated successfully")
    sys.exit(0)
else:
    print(f"FAIL: only {passed}/{total} configs instantiated")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [pr_diff] (0.15): DeepseekVLV2Config instantiation
# Buggy code: kwargs.get doesn't remove sub-configs from kwargs, super()
# called before attributes set, kv_lora_rank=None crashes DeepseekV2Config.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.15) DeepseekVLV2Config instantiation with nested configs"
python3 << 'PYEOF'
import importlib.util, sys, types

for name in ['vllm', 'vllm.transformers_utils', 'vllm.transformers_utils.configs']:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

try:
    spec = importlib.util.spec_from_file_location(
        'deepseek_vl2',
        '/workspace/vllm/vllm/transformers_utils/configs/deepseek_vl2.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Instantiate with nested config dicts (the pattern that triggers the bug)
    config = mod.DeepseekVLV2Config(
        vision_config={"image_size": 384},
        projector_config={},
        language_config={"vocab_size": 32000, "hidden_size": 4096},
    )

    # Verify nested configs were properly converted to config objects
    if not hasattr(config, 'vision_config'):
        print("FAIL: vision_config not set")
        sys.exit(1)
    if not hasattr(config, 'text_config'):
        print("FAIL: text_config not set")
        sys.exit(1)
    if isinstance(config.vision_config, dict):
        print("FAIL: vision_config is still a dict (not converted to config object)")
        sys.exit(1)

    print("PASS: DeepseekVLV2Config instantiated with nested configs")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [pr_diff] (0.10): config.py separates speculative decoding configs
# The fix introduces a set of speculative decoding config types that get
# loaded directly, while other custom configs go through AutoConfig.register.
# We check that config.py has the registration path.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) config.py has AutoConfig registration for custom configs"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/transformers_utils/config.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check 1: There must be a call to AutoConfig.register somewhere in the file
has_autoconfig_register = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'register':
            if isinstance(func.value, ast.Name) and func.value.id == 'AutoConfig':
                has_autoconfig_register = True
                break

if not has_autoconfig_register:
    print("FAIL: AutoConfig.register() not found in config.py")
    print("  Custom configs should be registered with AutoConfig for consistency")
    sys.exit(1)

# Check 2: The parse method should NOT load ALL _CONFIG_REGISTRY entries directly.
# There should be some differentiation between configs that need direct loading
# (speculative decoding) and those that should go through AutoConfig.
# We verify by checking that the first `if model_type in _CONFIG_REGISTRY` condition
# is NOT the one that directly loads the config (or that there's a different set used).

# Find the parse method
parse_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'parse':
        parse_func = node
        break

if parse_func is None:
    print("FAIL: parse() method not found")
    sys.exit(1)

# In the parse method, look for if-statements that check model_type
# The fix changes "if model_type in _CONFIG_REGISTRY" to check a smaller set first
# and moves _CONFIG_REGISTRY to the AutoConfig.register path
source_lines = source.splitlines()
parse_start = parse_func.lineno - 1
parse_end = parse_func.end_lineno
parse_source = '\n'.join(source_lines[parse_start:parse_end])

# The buggy pattern: the FIRST branch that loads config directly checks _CONFIG_REGISTRY
# The fix: the FIRST branch checks a smaller set (speculative decoding only)
# Then _CONFIG_REGISTRY is used for AutoConfig.register in the else branch
if 'AutoConfig.register' in parse_source:
    print("PASS: parse() uses AutoConfig.register for custom configs")
    sys.exit(0)
else:
    print("FAIL: parse() doesn't use AutoConfig.register")
    sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [regression] (0.10): All config modules importable without error
###############################################################################
echo ""
echo "TEST 5: [regression] (0.10) All config modules importable"
python3 << 'PYEOF'
import importlib.util, sys, types

for name in ['vllm', 'vllm.transformers_utils', 'vllm.transformers_utils.configs']:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

modules = [
    ('colmodernvbert', '/workspace/vllm/vllm/transformers_utils/configs/colmodernvbert.py'),
    ('deepseek_vl2', '/workspace/vllm/vllm/transformers_utils/configs/deepseek_vl2.py'),
    ('flex_olmo', '/workspace/vllm/vllm/transformers_utils/configs/flex_olmo.py'),
    ('isaac', '/workspace/vllm/vllm/transformers_utils/configs/isaac.py'),
    ('qwen3_next', '/workspace/vllm/vllm/transformers_utils/configs/qwen3_next.py'),
    ('step3p5', '/workspace/vllm/vllm/transformers_utils/configs/step3p5.py'),
]

passed = 0
for name, path in modules:
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        passed += 1
    except Exception as e:
        print(f"  {name}: FAIL ({type(e).__name__}: {e})")

total = len(modules)
if passed == total:
    print(f"PASS: all {total} config modules importable")
    sys.exit(0)
else:
    print(f"FAIL: {passed}/{total} modules importable")
    sys.exit(1)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [pr_diff] (0.10): super().__init__() at end of __init__ for affected configs
# WHY AST: The validation behavior depends on transformers v5 internals.
# As a structural safety net, verify super().__init__() is called AFTER
# all attribute assignments, not before. This is the core pattern fix.
###############################################################################
echo ""
echo "TEST 6: [pr_diff] (0.10) super().__init__() called after attribute setup"
python3 << 'PYEOF'
import ast, sys

configs_to_check = {
    'ColModernVBertConfig': '/workspace/vllm/vllm/transformers_utils/configs/colmodernvbert.py',
    'FlexOlmoConfig': '/workspace/vllm/vllm/transformers_utils/configs/flex_olmo.py',
    'IsaacConfig': '/workspace/vllm/vllm/transformers_utils/configs/isaac.py',
    'Qwen3NextConfig': '/workspace/vllm/vllm/transformers_utils/configs/qwen3_next.py',
    'DeepseekVLV2Config': '/workspace/vllm/vllm/transformers_utils/configs/deepseek_vl2.py',
}

def check_super_at_end(filepath, classname):
    """Check that super().__init__() is among the last statements in __init__."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    body = item.body
                    if not body:
                        return False, "empty __init__"

                    # Find the position of super().__init__() call
                    super_idx = None
                    for i, stmt in enumerate(body):
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            call = stmt.value
                            if (isinstance(call.func, ast.Attribute) and
                                call.func.attr == '__init__' and
                                isinstance(call.func.value, ast.Call) and
                                isinstance(call.func.value.func, ast.Name) and
                                call.func.value.func.id == 'super'):
                                super_idx = i
                                break

                    if super_idx is None:
                        return False, "no super().__init__() found"

                    total = len(body)
                    # super() should be in the last 25% of __init__ body
                    threshold = total * 0.75
                    if super_idx >= threshold:
                        return True, f"super() at position {super_idx+1}/{total}"
                    else:
                        return False, f"super() at position {super_idx+1}/{total} (too early, should be near end)"
    return False, f"class {classname} not found"

passed = 0
total = len(configs_to_check)
for classname, filepath in configs_to_check.items():
    ok, reason = check_super_at_end(filepath, classname)
    status = "PASS" if ok else "FAIL"
    print(f"  {classname}: {status} — {reason}")
    if ok:
        passed += 1

if passed >= total - 1:  # Allow 1 failure for flexibility
    print(f"PASS: {passed}/{total} configs have super().__init__() near end")
    sys.exit(0)
else:
    print(f"FAIL: only {passed}/{total} configs have correct super() ordering")
    sys.exit(1)
PYEOF
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# TEST 7 [structural] (0.05): Anti-stub — changed files have meaningful content
###############################################################################
echo ""
echo "TEST 7: [structural] (0.05) Anti-stub check"
python3 << 'PYEOF'
import os, sys

files = [
    "/workspace/vllm/vllm/transformers_utils/config.py",
    "/workspace/vllm/vllm/transformers_utils/configs/colmodernvbert.py",
    "/workspace/vllm/vllm/transformers_utils/configs/deepseek_vl2.py",
    "/workspace/vllm/vllm/transformers_utils/configs/flex_olmo.py",
    "/workspace/vllm/vllm/transformers_utils/configs/isaac.py",
    "/workspace/vllm/vllm/transformers_utils/configs/qwen3_next.py",
    "/workspace/vllm/vllm/transformers_utils/configs/step3p5.py",
]

for f in files:
    if not os.path.exists(f):
        print(f"FAIL: {f} does not exist")
        sys.exit(1)
    size = os.path.getsize(f)
    lines = len(open(f).readlines())
    if lines < 20:
        print(f"FAIL: {f} has only {lines} lines (stub?)")
        sys.exit(1)
    if size < 500:
        print(f"FAIL: {f} is only {size} bytes (stub?)")
        sys.exit(1)

# config.py should be substantial
config_lines = len(open("/workspace/vllm/vllm/transformers_utils/config.py").readlines())
if config_lines < 100:
    print(f"FAIL: config.py has only {config_lines} lines")
    sys.exit(1)

print(f"PASS: all files have meaningful content")
sys.exit(0)
PYEOF
T7=$?
echo "  -> exit code: $T7"

###############################################################################
# TEST 8 [agent_config] (0.10): No bare pip install in changed files
# [agent_config] (0.10): "Never use system python3 or bare pip" — AGENTS.md:27
###############################################################################
echo ""
echo "TEST 8: [agent_config] (0.10) no bare pip install in changed files"
cd "$REPO" 2>/dev/null
DIFF_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
T8=0
BARE_PIP=0
for cf in $DIFF_FILES; do
    if [ -f "$REPO/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "$REPO/$cf" 2>/dev/null | grep -v '^\s*#' | grep -v 'uv pip' > /dev/null 2>&1; then
            echo "  FAIL: $cf contains bare 'pip install'"
            BARE_PIP=1
        fi
    fi
done
if [ "$BARE_PIP" -eq 0 ]; then
    echo "  PASS"
    T8=0
else
    T8=1
fi
echo "  -> exit code: $T8"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.20 if $T1 == 0 else 0.0
t2 = 0.20 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.10 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
t8 = 0.10 if ${T8:-1} == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: step3p5 layer_types)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 2 (fail-to-pass: config instantiation)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 3 (fail-to-pass: deepseek_vl2 config)      = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (fail-to-pass: AutoConfig registration)  = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (pass-to-pass: modules importable)       = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (structural: super().__init__ ordering)   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 7 (anti-stub)                              = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 8 (config: no bare pip)                    = $([ ${T8:-1} -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
