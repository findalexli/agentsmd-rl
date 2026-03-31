#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
PASS=0

log() { echo "$1"; }
award() {
    local weight=$1 name=$2 result=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$result" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        PASS=$((PASS + 1))
        log "  PASS ($weight): $name"
    else
        log "  FAIL ($weight): $name"
    fi
}

REPO="/workspace/huggingface__transformers"
DEBERTA="$REPO/src/transformers/models/deberta_v2/modeling_deberta_v2.py"
SEW_D="$REPO/src/transformers/models/sew_d/modeling_sew_d.py"

log "=== GATE: Syntax check ==="
# [pr_diff] (gate): Both files must be valid Python
python3 -c "import ast; ast.parse(open('$DEBERTA').read())" 2>/dev/null
GATE1=$?
python3 -c "import ast; ast.parse(open('$SEW_D').read())" 2>/dev/null
GATE2=$?
if [ "$GATE1" != "0" ] || [ "$GATE2" != "0" ]; then
    log "  GATE FAILED: Syntax error in modified files"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log "  GATE PASS"

log ""
log "=== Behavioral: torch.jit.script + inspect.getsource simulation ==="

# [pr_diff] (0.40): FAIL-TO-PASS — Functions decorated with @torch.jit.script parse correctly
# when extracted via inspect.getsource (simulated). On Python 3.13, content between
# @decorator and def causes IndentationError in ast.parse.
BEHAV1=$(python3 -c "
import ast, sys

def test_jit_functions(filepath):
    with open(filepath) as f:
        lines = f.readlines()

    i = 0
    functions_tested = 0
    while i < len(lines):
        if lines[i].strip() == '@torch.jit.script':
            # Collect @decorator through end of function (simulates getsource output)
            block_lines = [lines[i]]
            j = i + 1
            # Gather everything between decorator and def
            while j < len(lines) and not lines[j].strip().startswith('def '):
                block_lines.append(lines[j])
                j += 1
            # Gather def line and body
            if j < len(lines):
                block_lines.append(lines[j])
                j += 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('    ')):
                    block_lines.append(lines[j])
                    j += 1

            source = ''.join(block_lines).strip()
            try:
                ast.parse(source)
                functions_tested += 1
            except SyntaxError as e:
                print(f'FAIL: {filepath} line {i+1}: {e}', file=sys.stderr)
                sys.exit(1)
            i = j
        else:
            i += 1

    if functions_tested < 3:
        print(f'FAIL: expected >=3 @torch.jit.script functions, found {functions_tested}', file=sys.stderr)
        sys.exit(1)
    return functions_tested

n1 = test_jit_functions('$DEBERTA')
n2 = test_jit_functions('$SEW_D')
print(f'OK: tested {n1} + {n2} functions')
" 2>&1 && echo "1" || echo "0")
award 0.40 "F2P: torch.jit.script functions parse via simulated inspect.getsource" "$BEHAV1"

# [pr_diff] (0.20): FAIL-TO-PASS — No non-blank non-def content between @torch.jit.script and def.
# This directly checks the root cause pattern that breaks Python 3.13.
BEHAV2=$(python3 -c "
import sys

def check_clean_decorator(filepath):
    with open(filepath) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        if lines[i].strip() == '@torch.jit.script':
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_line = lines[j].strip()
                if not next_line.startswith('def '):
                    print(f'FAIL: {filepath} line {j+1}: non-def content between @torch.jit.script and def: {next_line}', file=sys.stderr)
                    sys.exit(1)
        i += 1
    return True

check_clean_decorator('$DEBERTA')
check_clean_decorator('$SEW_D')
print('OK: no content between @torch.jit.script and def')
" 2>&1 && echo "1" || echo "0")
award 0.20 "F2P: no content between @torch.jit.script decorator and def statement" "$BEHAV2"

log ""
log "=== Regression: Functions preserved with correct signatures and decorator ==="

# [pr_diff] (0.10): PASS-TO-PASS — All three functions exist in both files with correct
# signatures and are still decorated with @torch.jit.script.
REGR1=$(python3 -c "
import ast, sys

EXPECTED = {
    'c2p_dynamic_expand': ['c2p_pos', 'query_layer', 'relative_pos'],
    'p2c_dynamic_expand': ['c2p_pos', 'query_layer', 'key_layer'],
    'pos_dynamic_expand': ['pos_index', 'p2c_att', 'key_layer'],
}

def check_functions(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())

    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in EXPECTED:
            args = [a.arg for a in node.args.args]
            # Check @torch.jit.script decorator is present
            has_jit = False
            for dec in node.decorator_list:
                src = ast.dump(dec)
                if 'torch' in src and 'jit' in src and 'script' in src:
                    has_jit = True
            if not has_jit:
                print(f'FAIL: {filepath}: {node.name} missing @torch.jit.script decorator', file=sys.stderr)
                sys.exit(1)
            found[node.name] = args

    for name, expected_args in EXPECTED.items():
        if name not in found:
            print(f'FAIL: {filepath}: function {name} not found', file=sys.stderr)
            sys.exit(1)
        if found[name] != expected_args:
            print(f'FAIL: {filepath}: {name} has wrong args: {found[name]} != {expected_args}', file=sys.stderr)
            sys.exit(1)

check_functions('$DEBERTA')
check_functions('$SEW_D')
print('OK: all functions present with correct signatures and @torch.jit.script')
" 2>&1 && echo "1" || echo "0")
award 0.10 "P2P: all three jit-scripted functions exist in both files with correct signatures" "$REGR1"

log ""
log "=== Regression: Anti-stub — function bodies contain real tensor operations ==="

# [pr_diff] (0.20): Anti-stub — each function body must contain a Return with a non-trivial
# expression: at least 3 combined Call + Subscript AST nodes. The real implementations
# use .expand([...size()...]) patterns with 4-5 calls each. This rejects trivial stubs
# like return None, return 0, or return x while accepting any correct implementation
# that reshapes/expands tensors.
REGR2=$(python3 -c "
import ast, sys

FUNCS = ['c2p_dynamic_expand', 'p2c_dynamic_expand', 'pos_dynamic_expand']

class NodeCounter(ast.NodeVisitor):
    def __init__(self):
        self.calls = 0
        self.subscripts = 0
    def visit_Call(self, node):
        self.calls += 1
        self.generic_visit(node)
    def visit_Subscript(self, node):
        self.subscripts += 1
        self.generic_visit(node)

def check_nontrivial(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in FUNCS:
            # Must have a return statement
            returns = [n for n in ast.walk(node) if isinstance(n, ast.Return) and n.value is not None]
            if not returns:
                print(f'FAIL: {filepath}: {node.name} has no return with value (stub)', file=sys.stderr)
                sys.exit(1)
            # Count Call + Subscript nodes in entire function body
            counter = NodeCounter()
            for stmt in node.body:
                counter.visit(stmt)
            total = counter.calls + counter.subscripts
            if total < 3:
                print(f'FAIL: {filepath}: {node.name} body too trivial ({total} Call+Subscript nodes, need >=3)', file=sys.stderr)
                sys.exit(1)

check_nontrivial('$DEBERTA')
check_nontrivial('$SEW_D')
print('OK: all function bodies are non-trivial')
" 2>&1 && echo "1" || echo "0")
award 0.20 "anti-stub: function bodies contain real tensor operations (>=3 Call+Subscript nodes)" "$REGR2"

log ""
log "=== Config-derived: Ruff lint check ==="

# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 0e1978c9e
CONF1=$(cd "$REPO" && ruff check \
    src/transformers/models/deberta_v2/modeling_deberta_v2.py \
    src/transformers/models/sew_d/modeling_sew_d.py \
    --select E,W,F --quiet 2>&1 && echo "1" || echo "0")
award 0.10 "ruff lint passes on both files" "$CONF1"

log ""
log "=== Results ==="
log "  Checks passed: $PASS"
log "  Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json with proper category decomposition
python3 -c "
import json
score = float('$SCORE')
# Category breakdown by check weights:
# behavioral (BEHAV1=0.40 + BEHAV2=0.20) = 0.60
# regression (REGR1=0.10 + REGR2=0.20) = 0.30
# config (CONF1=0.10) = 0.10
behavioral = 0.0
regression = 0.0
config = 0.0
remainder = score
# Attribute in order of check execution
for w, cat in [(0.40, 'b'), (0.20, 'b'), (0.10, 'r'), (0.20, 'r'), (0.10, 'c')]:
    take = min(w, remainder)
    if cat == 'b': behavioral += take
    elif cat == 'r': regression += take
    elif cat == 'c': config += take
    remainder = max(0.0, remainder - w)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
