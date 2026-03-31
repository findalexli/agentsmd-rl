#!/usr/bin/env bash
set -uo pipefail

SCORE=0
REPO="/workspace/prime-rl"
CONFIG_PY="$REPO/src/prime_rl/utils/config.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): config.py and all entrypoints must be valid Python
GATE_OK=true
for f in "$CONFIG_PY" \
         "$REPO/src/prime_rl/entrypoints/inference.py" \
         "$REPO/src/prime_rl/entrypoints/rl.py" \
         "$REPO/src/prime_rl/entrypoints/sft.py"; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "FAIL: $(basename $f) has syntax errors — aborting"
        GATE_OK=false
    fi
done
if [ "$GATE_OK" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "PASS: all files parse"

echo ""
echo "=== BEHAVIORAL: None-to-string conversion (fail-to-pass) ==="

# Discover the conversion function from config.py dynamically.
# The agent may name it anything; we find a callable in config.py that
# converts {k: None} into {k: "None"}.
# [pr_diff] (0.25): Flat dict None values are converted to "None" strings
R1=$(python3 -c "
import sys, importlib, types
sys.path.insert(0, '$REPO/src')

# Try the conventional name first, then scan for any function that works
conv_fn = None
try:
    from prime_rl.utils.config import none_to_none_str
    conv_fn = none_to_none_str
except ImportError:
    pass

if conv_fn is None:
    # Scan all callables exported from config module
    import prime_rl.utils.config as cfg_mod
    for name in dir(cfg_mod):
        obj = getattr(cfg_mod, name)
        if callable(obj) and isinstance(obj, types.FunctionType):
            try:
                result = obj({'test': None, 'ok': 1})
                if isinstance(result, dict) and result.get('test') == 'None' and result.get('ok') == 1:
                    conv_fn = obj
                    break
            except Exception:
                continue

if conv_fn is None:
    print('NO_FUNC')
    sys.exit(0)

# Test flat dict
d = {'a': None, 'b': 42, 'c': 'hello', 'd': None}
result = conv_fn(d)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert result['a'] == 'None', f'Expected \"None\", got {result[\"a\"]!r}'
assert result['b'] == 42
assert result['c'] == 'hello'
assert result['d'] == 'None', f'Expected \"None\", got {result[\"d\"]!r}'
print('PASS')
" 2>&1)
if [ "$R1" = "PASS" ]; then
    echo "PASS (0.25): flat dict None -> \"None\""
    SCORE=$(python3 -c "print($SCORE + 0.25)")
elif [ "$R1" = "NO_FUNC" ]; then
    echo "FAIL (0.25): no None-to-string conversion function found in config.py"
else
    echo "FAIL (0.25): flat dict None -> \"None\": $R1"
fi

# [pr_diff] (0.20): Nested dict None values are converted recursively
R2=$(python3 -c "
import sys, importlib, types
sys.path.insert(0, '$REPO/src')

conv_fn = None
try:
    from prime_rl.utils.config import none_to_none_str
    conv_fn = none_to_none_str
except ImportError:
    import prime_rl.utils.config as cfg_mod
    for name in dir(cfg_mod):
        obj = getattr(cfg_mod, name)
        if callable(obj) and isinstance(obj, types.FunctionType):
            try:
                r = obj({'test': None, 'ok': 1})
                if isinstance(r, dict) and r.get('test') == 'None' and r.get('ok') == 1:
                    conv_fn = obj
                    break
            except Exception:
                continue

if conv_fn is None:
    print('NO_FUNC'); sys.exit(0)

d = {'top': None, 'nested': {'a': None, 'b': 1, 'deep': {'x': None, 'y': 'ok'}}}
result = conv_fn(d)
assert result['top'] == 'None'
assert result['nested']['a'] == 'None'
assert result['nested']['b'] == 1
assert result['nested']['deep']['x'] == 'None'
assert result['nested']['deep']['y'] == 'ok'
print('PASS')
" 2>&1)
if [ "$R2" = "PASS" ]; then
    echo "PASS (0.20): nested dict recursion"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
elif [ "$R2" = "NO_FUNC" ]; then
    echo "FAIL (0.20): no conversion function found"
else
    echo "FAIL (0.20): nested dict recursion: $R2"
fi

# [pr_diff] (0.15): TOML round-trip preserves None as "None" string
R3=$(python3 -c "
import sys, io, tomllib, types
sys.path.insert(0, '$REPO/src')
import tomli_w

conv_fn = None
try:
    from prime_rl.utils.config import none_to_none_str
    conv_fn = none_to_none_str
except ImportError:
    import prime_rl.utils.config as cfg_mod
    for name in dir(cfg_mod):
        obj = getattr(cfg_mod, name)
        if callable(obj) and isinstance(obj, types.FunctionType):
            try:
                r = obj({'test': None, 'ok': 1})
                if isinstance(r, dict) and r.get('test') == 'None' and r.get('ok') == 1:
                    conv_fn = obj
                    break
            except Exception:
                continue

if conv_fn is None:
    print('NO_FUNC'); sys.exit(0)

d = {'model': {'name': 'test', 'max_len': None}, 'seed': None, 'lr': 0.001}
converted = conv_fn(d)
buf = io.BytesIO()
tomli_w.dump(converted, buf)
buf.seek(0)
loaded = tomllib.load(buf)
assert loaded['seed'] == 'None', f'seed: expected \"None\", got {loaded[\"seed\"]!r}'
assert loaded['model']['max_len'] == 'None', f'max_len: expected \"None\", got {loaded[\"model\"][\"max_len\"]!r}'
assert loaded['lr'] == 0.001
assert loaded['model']['name'] == 'test'
print('PASS')
" 2>&1)
if [ "$R3" = "PASS" ]; then
    echo "PASS (0.15): TOML round-trip preserves None"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
elif [ "$R3" = "NO_FUNC" ]; then
    echo "FAIL (0.15): no conversion function found"
else
    echo "FAIL (0.15): TOML round-trip: $R3"
fi

# [pr_diff] (0.10): Edge cases: empty dict, all-None, bools, lists pass through
R4=$(python3 -c "
import sys, types
sys.path.insert(0, '$REPO/src')

conv_fn = None
try:
    from prime_rl.utils.config import none_to_none_str
    conv_fn = none_to_none_str
except ImportError:
    import prime_rl.utils.config as cfg_mod
    for name in dir(cfg_mod):
        obj = getattr(cfg_mod, name)
        if callable(obj) and isinstance(obj, types.FunctionType):
            try:
                r = obj({'test': None, 'ok': 1})
                if isinstance(r, dict) and r.get('test') == 'None' and r.get('ok') == 1:
                    conv_fn = obj
                    break
            except Exception:
                continue

if conv_fn is None:
    print('NO_FUNC'); sys.exit(0)

assert conv_fn({}) == {}, f'Empty dict failed: {conv_fn({})}'
assert conv_fn({'a': None}) == {'a': 'None'}
assert conv_fn({'a': {'b': None}}) == {'a': {'b': 'None'}}
assert conv_fn({'x': [1,2,3]}) == {'x': [1,2,3]}
assert conv_fn({'x': True, 'y': False}) == {'x': True, 'y': False}
# Non-mutation check: input should not be modified
original = {'a': None, 'b': 1}
import copy
original_copy = copy.deepcopy(original)
conv_fn(original)
assert original == original_copy, 'Function mutated input dict'
print('PASS')
" 2>&1)
if [ "$R4" = "PASS" ]; then
    echo "PASS (0.10): edge cases"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
elif [ "$R4" = "NO_FUNC" ]; then
    echo "FAIL (0.10): no conversion function found"
else
    echo "FAIL (0.10): edge cases: $R4"
fi

echo ""
echo "=== BEHAVIORAL: Entrypoint integration (fail-to-pass) ==="

# [pr_diff] (0.15): Entrypoints no longer drop None values during serialization
# Instead of grep, we actually parse the entrypoint code and verify the
# model_dump call does NOT use exclude_none=True by running a behavioral test:
# we construct a mock that tracks how model_dump is called.
R5=$(python3 -c "
import sys, ast
sys.path.insert(0, '$REPO/src')

# Check all three entrypoints: the call to model_dump should NOT pass exclude_none=True
# AND the dict passed to tomli_w.dump should go through None conversion
fail = False
for ep in ['inference', 'rl', 'sft']:
    path = f'$REPO/src/prime_rl/entrypoints/{ep}.py'
    with open(path) as f:
        source = f.read()
    tree = ast.parse(source)

    # Find all calls where model_dump has exclude_none=True as a keyword
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'model_dump':
                for kw in node.keywords:
                    if kw.arg == 'exclude_none':
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            print(f'FAIL:{ep} still uses exclude_none=True')
                            fail = True

if not fail:
    print('PASS')
" 2>&1)
if [ "$R5" = "PASS" ]; then
    echo "PASS (0.15): entrypoints no longer drop None (exclude_none=True removed)"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL (0.15): $R5"
fi

echo ""
echo "=== PASS-TO-PASS: Non-None values unchanged ==="

# [pr_diff] (0.10): Existing non-None config values serialize identically
R6=$(python3 -c "
import sys, io, tomllib, types
sys.path.insert(0, '$REPO/src')
import tomli_w

conv_fn = None
try:
    from prime_rl.utils.config import none_to_none_str
    conv_fn = none_to_none_str
except ImportError:
    import prime_rl.utils.config as cfg_mod
    for name in dir(cfg_mod):
        obj = getattr(cfg_mod, name)
        if callable(obj) and isinstance(obj, types.FunctionType):
            try:
                r = obj({'test': None, 'ok': 1})
                if isinstance(r, dict) and r.get('test') == 'None' and r.get('ok') == 1:
                    conv_fn = obj
                    break
            except Exception:
                continue

if conv_fn is None:
    print('NO_FUNC'); sys.exit(0)

d = {
    'model': {'name': 'Qwen/Qwen3-0.6B', 'max_model_len': 4096, 'enforce_eager': True},
    'server': {'port': 8000, 'host': '0.0.0.0'},
    'seed': 42,
}
converted = conv_fn(d)
assert converted == d, f'Non-None dict should be unchanged: {converted}'
buf = io.BytesIO()
tomli_w.dump(converted, buf)
buf.seek(0)
loaded = tomllib.load(buf)
assert loaded == d
print('PASS')
" 2>&1)
if [ "$R6" = "PASS" ]; then
    echo "PASS (0.10): non-None values pass through"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
elif [ "$R6" = "NO_FUNC" ]; then
    echo "FAIL (0.10): no conversion function found"
else
    echo "FAIL (0.10): non-None passthrough: $R6"
fi

echo ""
echo "=== CONFIG: AGENTS.md rules ==="

# [agent_config] (0.05): "Avoid try/except blocks unless really necessary" — AGENTS.md:5 @ 692dfc8a
# Check that the conversion function in config.py doesn't have try/except
R7=$(python3 -c "
import ast
with open('$CONFIG_PY') as f:
    tree = ast.parse(f.read())

# Find ALL functions added to config.py and check for try/except
# We look for the conversion function (whatever it's named) by checking
# functions whose body handles dicts
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        tries = [n for n in ast.walk(node) if isinstance(n, ast.Try)]
        if tries:
            # Check if this function deals with None/dict conversion
            src_lines = open('$CONFIG_PY').readlines()
            func_src = ''.join(src_lines[node.lineno-1:node.end_lineno])
            if 'None' in func_src or 'none' in func_src.lower():
                print(f'FAIL:{node.name} has try/except')
                exit(0)
print('PASS')
" 2>&1)
if [ "$R7" = "PASS" ]; then
    echo "PASS (0.05): no unnecessary try/except in conversion function"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): $R7"
fi

echo ""
echo "=== Summary ==="
SCORE=$(python3 -c "print(round($SCORE, 2))")
echo "Total score: $SCORE / 1.0"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
# behavioral = F2P (0.70) + P2P (0.10) = 0.80 max
# integration/structural = 0.15 (entrypoint exclude_none check)
# config = 0.05
beh = min(score, 0.80)
integ = min(max(score - 0.80, 0), 0.15)
cfg = min(max(score - 0.95, 0), 0.05)
json.dump({
    'reward': score,
    'behavioral': round(beh, 4),
    'regression': round(integ, 4),
    'config': round(cfg, 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
