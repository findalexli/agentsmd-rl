#!/usr/bin/env bash
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/arguments.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_extract]=0.35
WEIGHTS[behavioral_validate]=0.25
WEIGHTS[behavioral_fallback]=0.15
WEIGHTS[structural]=0.10
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05
WEIGHTS[antistub]=0.05

for key in behavioral_extract behavioral_validate behavioral_fallback structural config_no_wildcard config_no_bare_print antistub; do
    RESULTS[$key]=0
done

# GATE: Code must parse and have _hf_validate_args importable
python3 -c "
import sys
sys.path.insert(0, '/workspace/slime')
import ast
with open('$TARGET') as f:
    src = f.read()
    ast.parse(src)
from slime.backends.megatron_utils.arguments import __hf_validate_args as _hf_validate_args
" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: Code parses and imports"

# ---------- BEHAVIORAL 1 (35%): Extracts rope_theta from rope_parameters dict ----------
# [pr_diff] (0.35): rope_parameters dict is checked and rope_theta extracted
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/slime')

# Extract and test the _hf_validate_args function in isolation
import ast
import textwrap

with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f:
    src = f.read()

tree = ast.parse(src)

# Find the _hf_validate_args function
found_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_hf_validate_args":
        found_func = node
        break

if not found_func:
    print("BEHAVIORAL_EXTRACT FAIL: _hf_validate_args not found")
    sys.exit(1)

# Extract function source and create a testable version
lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[found_func.lineno-1:found_func.end_lineno]))

# Build namespace with minimal mocks
class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockConfig:
    def __init__(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

def equal(x, y):
    return x == y

errors = []

# Simulate the fixed logic: does it extract rope_theta from rope_parameters?
namespace = {
    'args': MockArgs(rotary_base=500000, hidden_size=1024, num_attention_heads=16,
                     num_layers=24, ffn_hidden_size=4096, untie_embeddings_and_output_weights=False,
                     norm_epsilon=1e-6),
    'MockConfig': MockConfig,
    'equal': equal,
    'errors': errors,
}

# Test with config that has rope_theta in dict (the bug scenario)
config_with_dict = MockConfig({
    'hidden_size': 1024,
    'num_attention_heads': 16,
    'num_hidden_layers': 24,
    'intermediate_size': 4096,
    'tie_word_embeddings': True,
    'rms_norm_eps': 1e-6,
    'rope_theta': 10000,  # Stale default
    'rope_parameters': {'rope_theta': 500000},  # Actual value
})

# Execute the function logic
exec(func_src, namespace)
_hf_validate_args = namespace['_hf_validate_args']

try:
    _hf_validate_args(namespace['args'], config_with_dict)
    print("BEHAVIORAL_EXTRACT PASS: No error with matching values")
except AssertionError as e:
    # If it fails, check if it's because we're using stale value (10000 vs 500000)
    if "rope_theta" in str(e) and "10000" in str(e):
        print(f"BEHAVIORAL_EXTRACT FAIL: Using stale rope_theta value: {e}")
        sys.exit(1)
    # Some other error - might be other validation issues
    print(f"BEHAVIORAL_EXTRACT UNEXPECTED: {e}")
    sys.exit(1)

print("BEHAVIORAL_EXTRACT PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_extract]=1 && echo "TEST behavioral_extract: PASS" || echo "TEST behavioral_extract: FAIL"

# ---------- BEHAVIORAL 2 (25%): Validates rope_theta separately from loop (detects mismatch) ----------
# [pr_diff] (0.25): rope_theta removed from generic loop and validated separately
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/slime')

import ast
import textwrap

with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f:
    src = f.read()

tree = ast.parse(src)

found_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_hf_validate_args":
        found_func = node
        break

if not found_func:
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[found_func.lineno-1:found_func.end_lineno]))

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockConfig:
    def __init__(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

def equal(x, y):
    return x == y

errors = []

namespace = {
    'args': MockArgs(rotary_base=10000, hidden_size=1024, num_attention_heads=16,
                     num_layers=24, ffn_hidden_size=4096, untie_embeddings_and_output_weights=False,
                     norm_epsilon=1e-6),
    'MockConfig': MockConfig,
    'equal': equal,
    'errors': errors,
}

# Test with mismatched values - should raise error
config_mismatch = MockConfig({
    'hidden_size': 1024,
    'num_attention_heads': 16,
    'num_hidden_layers': 24,
    'intermediate_size': 4096,
    'tie_word_embeddings': True,
    'rms_norm_eps': 1e-6,
    'rope_theta': 500000,  # Different from rotary_base=10000
})

exec(func_src, namespace)
_hf_validate_args = namespace['_hf_validate_args']

try:
    _hf_validate_args(namespace['args'], config_mismatch)
    print("BEHAVIORAL_VALIDATE FAIL: Should have raised error for mismatched rope_theta")
    sys.exit(1)
except AssertionError as e:
    if "rope_theta" in str(e) or "rotary_base" in str(e):
        print("BEHAVIORAL_VALIDATE PASS: Correctly detected mismatch")
    else:
        print(f"BEHAVIORAL_VALIDATE UNEXPECTED: {e}")
        sys.exit(1)

print("BEHAVIORAL_VALIDATE PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_validate]=1 && echo "TEST behavioral_validate: PASS" || echo "TEST behavioral_validate: FAIL"

# ---------- BEHAVIORAL 3 (15%): Falls back to direct access when rope_parameters missing ----------
# [pr_diff] (0.15): Falls back to hf_config.rope_theta when rope_parameters not present
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/slime')

import ast
import textwrap

with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f:
    src = f.read()

tree = ast.parse(src)

found_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_hf_validate_args":
        found_func = node
        break

if not found_func:
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[found_func.lineno-1:found_func.end_lineno]))

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockConfig:
    def __init__(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

def equal(x, y):
    return x == y

namespace = {
    'args': MockArgs(rotary_base=10000, hidden_size=1024, num_attention_heads=16,
                     num_layers=24, ffn_hidden_size=4096, untie_embeddings_and_output_weights=False,
                     norm_epsilon=1e-6),
    'MockConfig': MockConfig,
    'equal': equal,
    'errors': [],
}

# Test without rope_parameters dict - should use direct attribute
config_no_dict = MockConfig({
    'hidden_size': 1024,
    'num_attention_heads': 16,
    'num_hidden_layers': 24,
    'intermediate_size': 4096,
    'tie_word_embeddings': True,
    'rms_norm_eps': 1e-6,
    'rope_theta': 10000,  # Only direct attribute, matches rotary_base
})

exec(func_src, namespace)
_hf_validate_args = namespace['_hf_validate_args']

try:
    _hf_validate_args(namespace['args'], config_no_dict)
    print("BEHAVIORAL_FALLBACK PASS: Works without rope_parameters")
except AssertionError as e:
    if "rope_theta" in str(e):
        print("BEHAVIORAL_FALLBACK FAIL: Should fall back to direct attribute access")
        sys.exit(1)
    raise

# Also test that it detects mismatch via fallback path
namespace2 = {
    'args': MockArgs(rotary_base=500000, hidden_size=1024, num_attention_heads=16,
                     num_layers=24, ffn_hidden_size=4096, untie_embeddings_and_output_weights=False,
                     norm_epsilon=1e-6),
    'MockConfig': MockConfig,
    'equal': equal,
    'errors': [],
}

config_no_dict_mismatch = MockConfig({
    'hidden_size': 1024,
    'num_attention_heads': 16,
    'num_hidden_layers': 24,
    'intermediate_size': 4096,
    'tie_word_embeddings': True,
    'rms_norm_eps': 1e-6,
    'rope_theta': 10000,  # Different from rotary_base=500000
})

exec(func_src, namespace2)
_hf_validate_args2 = namespace2['_hf_validate_args']

try:
    _hf_validate_args2(namespace2['args'], config_no_dict_mismatch)
    print("BEHAVIORAL_FALLBACK FAIL: Should detect mismatch via fallback")
    sys.exit(1)
except AssertionError as e:
    print("BEHAVIORAL_FALLBACK PASS: Fallback path works correctly")

print("BEHAVIORAL_FALLBACK PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_fallback]=1 && echo "TEST behavioral_fallback: PASS" || echo "TEST behavioral_fallback: FAIL"

# ---------- STRUCTURAL (10%): Function exists with proper structure ----------
# [agent_config] (0.10): _hf_validate_args function exists and has rotary_base validation
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f:
    src = f.read()
tree = ast.parse(src)

found = any(isinstance(n, ast.FunctionDef) and n.name == "_hf_validate_args" for n in ast.walk(tree))
if not found:
    print("STRUCTURAL FAIL: _hf_validate_args not found")
    sys.exit(1)

# Check function has meaningful body (not a stub)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_hf_validate_args":
        # Count non-docstring, non-pass statements
        stmt_count = 0
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                continue  # Skip docstring
            if isinstance(stmt, ast.Pass):
                continue
            stmt_count += 1
        if stmt_count < 5:
            print(f"STRUCTURAL FAIL: Function body too shallow ({stmt_count} meaningful stmts)")
            sys.exit(1)
        break

if "rotary_base" not in src:
    print("STRUCTURAL FAIL: rotary_base not referenced")
    sys.exit(1)

print("STRUCTURAL PASS")
PYEOF
echo "=== Structural check (10%) ==="
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Config-derived (5%): No wildcard imports ----------
# Source: Standard housekeeping check
echo "=== Config: no wildcard imports (5%) ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL"; fi

# ---------- Config-derived (5%): No bare print() in production code ----------
# Source: Standard housekeeping check
echo "=== Config: no bare print() (5%) ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL"; fi

# ---------- Anti-stub (5%): Function has sufficient implementation ----------
# Uses AST to verify non-trivial function body
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f:
    src = f.read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_hf_validate_args":
        # Count actual statements (excluding docstrings)
        real_stmts = []
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            if isinstance(stmt, ast.Pass):
                continue
            real_stmts.append(stmt)

        # Check for specific implementation patterns
        has_loop = any(isinstance(s, (ast.For, ast.While)) for s in real_stmts)
        has_conditional = any(isinstance(s, ast.If) for s in real_stmts)
        has_getattr = "getattr" in src

        score = 0
        if len(real_stmts) >= 5: score += 1
        if has_conditional: score += 1
        if has_getattr: score += 1

        if score >= 2:
            print("ANTI-STUB PASS")
            sys.exit(0)
        else:
            print(f"ANTI-STUB FAIL: insufficient implementation (score {score}/3)")
            sys.exit(1)

print("ANTI-STUB FAIL: function not found")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

SCORE=$(python3 -c "
w={'behavioral_extract':${WEIGHTS[behavioral_extract]},'behavioral_validate':${WEIGHTS[behavioral_validate]},'behavioral_fallback':${WEIGHTS[behavioral_fallback]},'structural':${WEIGHTS[structural]},'config_no_wildcard':${WEIGHTS[config_no_wildcard]},'config_no_bare_print':${WEIGHTS[config_no_bare_print]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral_extract':${RESULTS[behavioral_extract]},'behavioral_validate':${RESULTS[behavioral_validate]},'behavioral_fallback':${RESULTS[behavioral_fallback]},'structural':${RESULTS[structural]},'config_no_wildcard':${RESULTS[config_no_wildcard]},'config_no_bare_print':${RESULTS[config_no_bare_print]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
