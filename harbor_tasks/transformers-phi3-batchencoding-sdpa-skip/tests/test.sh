#!/usr/bin/env bash
set +e  # don't exit on failure — we track scores manually

WORKSPACE="/workspace/transformers"
REWARD=0
TOTAL=0

log() { echo "[test.sh] $*"; }
add_score() {
    local weight=$1 label=$2 pass=$3
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$pass" = "1" ]; then
        REWARD=$(python3 -c "print(round($REWARD + $weight, 4))")
        log "PASS ($weight): $label"
    else
        log "FAIL ($weight): $label"
    fi
}

mkdir -p /logs/verifier

# ============================================================
# GATE: Syntax checks — abort on failure
# ============================================================

# [pr_diff] (GATE): Python syntax check on modified files
log "GATE: Python syntax check"
GATE_OK=1
for f in "$WORKSPACE/tests/models/phi3/test_modeling_phi3.py" \
         "$WORKSPACE/tests/test_modeling_common.py"; do
    if ! python3 -c "
import py_compile, sys
try:
    py_compile.compile('$f', doraise=True)
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log "GATE FAILED: $(basename $f) has syntax errors"
        GATE_OK=0
    fi
done

if [ "$GATE_OK" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE: All syntax checks passed"

# ============================================================
# FAIL-TO-PASS: Bug-detecting checks (0.60)
# ============================================================
# Justification for AST: These tests require multi-GB Phi-3 model weights
# and GPU hardware (SDPA flash attention). Cannot call the code directly.
# AST checks detect the BUG pattern, not a specific fix pattern, so any
# valid fix passes.

# [pr_diff] (0.35): No generate() call passes bare 'inputs' as positional arg
# Buggy: model.generate(inputs, ...) / Phi3MiniWithStaticCache.generate(model, inputs, 64)
# Fixed: model.generate(**inputs, ...) / generate(model, inputs["input_ids"], 64)
# Also accepts: model.generate(input_ids=inputs["input_ids"], ...) or any non-bare-Name
log "F2P: Checking Phi3 generate calls for bare 'inputs' positional arg..."
F2P_PHI3_PASS=0
python3 -c "
import ast, sys

with open('$WORKSPACE/tests/models/phi3/test_modeling_phi3.py') as f:
    source = f.read()
tree = ast.parse(source)

# Find all .generate() calls anywhere in the AST
buggy_calls = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    if not (isinstance(node.func, ast.Attribute) and node.func.attr == 'generate'):
        continue
    # Check every positional arg: is any a bare Name('inputs')?
    for arg in node.args:
        if isinstance(arg, ast.Name) and arg.id == 'inputs':
            # Get approximate location for error message
            buggy_calls.append(f'line {node.lineno}')

if buggy_calls:
    print(f'FAIL: {len(buggy_calls)} generate() call(s) pass bare inputs as positional arg: {buggy_calls}')
    sys.exit(1)

# Sanity: there should still be generate() calls in the file (not deleted)
gen_calls = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'generate':
            gen_calls += 1

if gen_calls < 4:
    print(f'FAIL: expected at least 4 generate() calls in phi3 test, found {gen_calls} (test methods may have been deleted)')
    sys.exit(1)

print(f'PASS: all {gen_calls} generate() calls avoid bare inputs positional arg')
" && F2P_PHI3_PASS=1

add_score 0.35 "F2P: Phi3 generate calls don't pass bare 'inputs'" "$F2P_PHI3_PASS"

# [pr_diff] (0.25): SDPA skip list contains new model entries (AST-verified)
# Checks string LITERALS in the function body (immune to comment injection)
log "F2P: Checking SDPA skip list for new model entries..."
F2P_SDPA_PASS=0
python3 -c "
import ast, sys

with open('$WORKSPACE/tests/test_modeling_common.py') as f:
    source = f.read()
tree = ast.parse(source)

# Find test_sdpa_can_dispatch_on_flash function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'test_sdpa_can_dispatch_on_flash':
            func_node = node
            break

if func_node is None:
    print('FAIL: test_sdpa_can_dispatch_on_flash function not found')
    sys.exit(1)

# Collect all string literals in the function body (AST ensures these are
# actual code, not comments)
string_literals = set()
for child in ast.walk(func_node):
    if isinstance(child, ast.Constant) and isinstance(child.value, str):
        string_literals.add(child.value)

# Check required new entries (case-insensitive substring match in any literal)
required = {
    'evolla': False,       # EvollaModel or evolla
    'parakeet_encoder': False,
    'parakeet_ctc': False,
    'pi0': False,
}

for s in string_literals:
    sl = s.lower()
    for key in required:
        if key in sl:
            required[key] = True

missing = [k for k, found in required.items() if not found]
if missing:
    print(f'FAIL: missing from SDPA skip function (as code literals, not comments): {missing}')
    sys.exit(1)

print(f'PASS: all 4 new model entries found as string literals in test_sdpa_can_dispatch_on_flash')
" && F2P_SDPA_PASS=1

add_score 0.25 "F2P: SDPA skip list has EvollaModel, parakeet_encoder/ctc, pi0" "$F2P_SDPA_PASS"

# ============================================================
# PASS-TO-PASS: Existing behavior preserved (0.25)
# ============================================================

# [pr_diff] (0.15): Existing SDPA skip entries still present (AST-verified)
log "P2P: Checking existing SDPA skip entries preserved..."
P2P_EXISTING_PASS=0
python3 -c "
import ast, sys

with open('$WORKSPACE/tests/test_modeling_common.py') as f:
    source = f.read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'test_sdpa_can_dispatch_on_flash':
            func_node = node
            break

if func_node is None:
    print('FAIL: function not found')
    sys.exit(1)

string_literals = set()
for child in ast.walk(func_node):
    if isinstance(child, ast.Constant) and isinstance(child.value, str):
        string_literals.add(child.value)

# These entries existed before the fix and must still be present
required_existing = ['modernbert', 'gemma3', 'pixtral', 'sam', 'kosmos-2', 'mllama']
missing = [r for r in required_existing if r not in string_literals]

if missing:
    print(f'FAIL: existing skip entries removed: {missing}')
    sys.exit(1)

# PaliGemma skip logic should also still be present
pali_found = False
for s in string_literals:
    if 'paligemma' in s.lower() or 'PaliGemma' in s:
        pali_found = True
        break
# Also check for PaliGemma as a Name reference
for child in ast.walk(func_node):
    if isinstance(child, ast.Name) and 'paligemma' in child.id.lower():
        pali_found = True
    if isinstance(child, ast.Attribute) and 'paligemma' in child.attr.lower():
        pali_found = True

if not pali_found:
    # Check raw source for PaliGemma (could be in a string comparison we missed)
    lines = source.splitlines()
    start = func_node.lineno - 1
    end = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start + 200
    func_text = '\\n'.join(lines[start:end])
    if 'PaliGemma' not in func_text and 'paligemma' not in func_text.lower():
        print('FAIL: PaliGemma skip logic removed')
        sys.exit(1)

print('PASS: existing SDPA skip entries preserved')
" && P2P_EXISTING_PASS=1

add_score 0.15 "P2P: Existing SDPA skip entries preserved" "$P2P_EXISTING_PASS"

# [pr_diff] (0.10): Phi3 test class and methods still defined
log "P2P: Checking Phi3 test structure intact..."
P2P_STRUCTURE_PASS=0
python3 -c "
import ast, sys

with open('$WORKSPACE/tests/models/phi3/test_modeling_phi3.py') as f:
    source = f.read()
tree = ast.parse(source)

# Check that key test methods still exist
required_methods = [
    'test_phi3_mini_4k_instruct_generation',
    'test_phi3_mini_4k_instruct_with_static_cache',
    'test_phi3_mini_128k_instruct_generation',
    'test_phi3_mini_128k_instruct_with_static_cache',
]

found_methods = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name in required_methods:
            # Verify non-trivial body (not just 'pass' or docstring)
            body = [n for n in node.body if not isinstance(n, ast.Expr) or
                    not isinstance(getattr(n, 'value', None), ast.Constant)]
            if len(body) >= 2:
                found_methods.add(node.name)

missing = set(required_methods) - found_methods
if missing:
    print(f'FAIL: test methods missing or stubbed out: {missing}')
    sys.exit(1)

print(f'PASS: all {len(required_methods)} Phi3 test methods still defined with non-trivial bodies')
" && P2P_STRUCTURE_PASS=1

add_score 0.10 "P2P: Phi3 test methods still defined" "$P2P_STRUCTURE_PASS"

# ============================================================
# REGRESSION: Anti-stub checks (0.10)
# ============================================================

# [static] (0.10): Meaningful changes in both target files
log "Regression: Checking for meaningful changes in both files..."
ANTISTUB_PASS=0
python3 -c "
import subprocess, sys

def count_code_changes(filepath):
    \"\"\"Count non-comment, non-whitespace changes via git diff.\"\"\"
    for ref in ['HEAD', '--cached', 'HEAD~1']:
        args = ['git', 'diff']
        if ref == '--cached':
            args.append('--cached')
        else:
            args.append(ref)
        args.extend(['--', filepath])
        result = subprocess.run(args, capture_output=True, text=True, cwd='$WORKSPACE')
        if result.stdout.strip():
            lines = result.stdout.splitlines()
            code = [l for l in lines
                    if (l.startswith('+') or l.startswith('-'))
                    and not l.startswith('+++') and not l.startswith('---')]
            meaningful = [l for l in code
                          if l[1:].strip()
                          and not l[1:].strip().startswith('#')]
            return len(meaningful)
    return 0

phi3_changes = count_code_changes('tests/models/phi3/test_modeling_phi3.py')
common_changes = count_code_changes('tests/test_modeling_common.py')

if phi3_changes < 2:
    print(f'FAIL: only {phi3_changes} meaningful change(s) in phi3 test (need >=2)')
    sys.exit(1)

if common_changes < 1:
    print(f'FAIL: only {common_changes} meaningful change(s) in test_modeling_common.py (need >=1)')
    sys.exit(1)

print(f'PASS: {phi3_changes} phi3 changes, {common_changes} common changes')
" && ANTISTUB_PASS=1

add_score 0.10 "Regression: Meaningful diff in both target files" "$ANTISTUB_PASS"

# ============================================================
# CONFIG-DERIVED: Agent config checks (0.05)
# ============================================================

# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 44686173
log "Config: Checking ruff style..."
STYLE_PASS=0
if command -v ruff &>/dev/null; then
    RUFF_OK=1
    for f in "$WORKSPACE/tests/models/phi3/test_modeling_phi3.py" \
             "$WORKSPACE/tests/test_modeling_common.py"; do
        if ! ruff check "$f" --select E,W --ignore E501 --quiet 2>/dev/null; then
            RUFF_OK=0
        fi
    done
    if [ "$RUFF_OK" = "1" ]; then
        STYLE_PASS=1
    fi
else
    # Fallback: basic indent check (no tabs in Python)
    if python3 -c "
import sys
for path in ['$WORKSPACE/tests/models/phi3/test_modeling_phi3.py',
             '$WORKSPACE/tests/test_modeling_common.py']:
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if '\t' in line and not line.strip().startswith('#'):
                print(f'{path}:{i}: tab indentation')
                sys.exit(1)
" 2>/dev/null; then
        STYLE_PASS=1
    fi
fi
add_score 0.05 "Config: Code style (ruff)" "$STYLE_PASS"

# ============================================================
# FINAL SCORE
# ============================================================

log "Score: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
reward = $REWARD
data = {
    'reward': round(reward, 4),
    'behavioral': round(min(reward, 0.60), 4),
    'regression': round(min(max(0, reward - 0.60), 0.25), 4),
    'config': round(min(max(0, reward - 0.90), 0.05), 4),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
