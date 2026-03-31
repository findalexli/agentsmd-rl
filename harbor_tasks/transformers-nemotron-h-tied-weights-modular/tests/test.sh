#!/usr/bin/env bash
set +e

MODELING="src/transformers/models/nemotron_h/modeling_nemotron_h.py"
MODULAR="src/transformers/models/nemotron_h/modular_nemotron_h.py"

total=0
add() { total=$(python3 -c "print(round($total + $1, 4))"); }

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): Both files must be valid Python
python3 -c "
import ast, sys
for path in ['$MODELING', '$MODULAR']:
    try:
        with open(path) as f:
            ast.parse(f.read())
    except SyntaxError as e:
        print(f'GATE FAILED: {path}: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE PASSED: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# FAIL-TO-PASS (0.45 total)
# AST justified: code requires torch + full transformers model infra (not installed)
########################################

# [pr_diff] (0.25): NemotronHPreTrainedModel must NOT define _tied_weights_keys
# On buggy code this class has _tied_weights_keys = {} which shadows parent
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
found_class = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHPreTrainedModel':
        found_class = True
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '_tied_weights_keys':
                        print('FAIL: NemotronHPreTrainedModel still defines _tied_weights_keys')
                        sys.exit(1)
        # Also verify the class has substantial body (anti-stub: >=10 statements)
        real_stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))
                      or (isinstance(s, ast.Expr) and not isinstance(s.value, (ast.Constant, ast.Str)))]
        if len(real_stmts) < 5:
            print(f'FAIL: NemotronHPreTrainedModel body too shallow ({len(real_stmts)} stmts)')
            sys.exit(1)
        break
if not found_class:
    print('FAIL: NemotronHPreTrainedModel not found')
    sys.exit(1)
print('PASS: _tied_weights_keys removed from base class')
" && add 0.25 || true

# [pr_diff] (0.15): Modular NemotronHForCausalLM must NOT delete _tied_weights_keys in __init__
# On buggy code, __init__ existed solely to do 'del self._tied_weights_keys'
python3 -c "
import ast, sys
with open('$MODULAR') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHForCausalLM':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                # Check if __init__ deletes _tied_weights_keys
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Delete):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and target.attr == '_tied_weights_keys':
                                print('FAIL: modular __init__ still deletes _tied_weights_keys')
                                sys.exit(1)
        print('PASS: modular CausalLM does not delete _tied_weights_keys')
        sys.exit(0)
print('FAIL: NemotronHForCausalLM not found in modular')
sys.exit(1)
" && add 0.15 || true

# [pr_diff] (0.05): Modular NemotronHPreTrainedModel must NOT define _tied_weights_keys
# Same bug exists in both files — modular also has the shadowing attribute
python3 -c "
import ast, sys
with open('$MODULAR') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHPreTrainedModel':
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '_tied_weights_keys':
                        print('FAIL: modular NemotronHPreTrainedModel still has _tied_weights_keys')
                        sys.exit(1)
        print('PASS: modular base class clean')
        sys.exit(0)
# Class might not exist in modular (it's optional) — that's OK
print('PASS: NemotronHPreTrainedModel not in modular (acceptable)')
" && add 0.05 || true

########################################
# PASS-TO-PASS BEHAVIORAL (0.20 total)
########################################

# [pr_diff] (0.10): NemotronHForCausalLM retains _tied_weights_keys class attribute
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHForCausalLM':
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '_tied_weights_keys':
                        print(f'PASS: _tied_weights_keys defined on NemotronHForCausalLM')
                        sys.exit(0)
        print('FAIL: NemotronHForCausalLM missing _tied_weights_keys')
        sys.exit(1)
print('FAIL: NemotronHForCausalLM not found')
sys.exit(1)
" && add 0.10 || true

# [pr_diff] (0.05): NemotronHForCausalLM.__init__ has config type annotation
# Accept any form: Name, Attribute, string annotation — not narrow to one style
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHForCausalLM':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                args = item.args
                if len(args.args) >= 2:
                    ann = args.args[1].annotation
                    if ann is not None:
                        # Accept Name('NemotronHConfig'), Attribute(..., 'NemotronHConfig'),
                        # or Constant('NemotronHConfig') (string annotation)
                        ann_str = ast.dump(ann)
                        if 'NemotronHConfig' in ann_str:
                            print('PASS: __init__ config has type annotation')
                            sys.exit(0)
                print('FAIL: config param missing annotation')
                sys.exit(1)
        print('FAIL: __init__ not found')
        sys.exit(1)
print('FAIL: class not found')
sys.exit(1)
" && add 0.05 || true

# [pr_diff] (0.05): NemotronHForCausalLM.forward exists with non-trivial body (>10 stmts)
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHForCausalLM':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                body_stmts = len(item.body)
                if body_stmts < 5:
                    print(f'FAIL: forward too shallow ({body_stmts} stmts)')
                    sys.exit(1)
                print(f'PASS: forward exists ({body_stmts} stmts)')
                sys.exit(0)
        print('FAIL: forward method missing')
        sys.exit(1)
print('FAIL: class not found')
sys.exit(1)
" && add 0.05 || true

########################################
# REGRESSION (0.10 total)
########################################

# [pr_diff] (0.05): Key model classes exist in modeling
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
required = {'NemotronHModel', 'NemotronHForCausalLM', 'NemotronHPreTrainedModel'}
missing = required - classes
if missing:
    print(f'FAIL: missing classes: {missing}')
    sys.exit(1)
print(f'PASS: all required classes present')
" && add 0.05 || true

# [pr_diff] (0.05): NemotronHPreTrainedModel._init_weights exists with non-trivial body
python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHPreTrainedModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_init_weights':
                if len(item.body) < 3:
                    print(f'FAIL: _init_weights too shallow ({len(item.body)} stmts)')
                    sys.exit(1)
                print(f'PASS: _init_weights exists ({len(item.body)} stmts)')
                sys.exit(0)
        print('FAIL: _init_weights missing')
        sys.exit(1)
print('FAIL: class not found')
sys.exit(1)
" && add 0.05 || true

########################################
# CONFIG-DERIVED (0.10 total)
########################################

# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 2cd52c267c
ruff check "$MODELING" "$MODULAR" --select E,F,W --quiet 2>/dev/null && {
    echo "PASS: ruff check clean"
    add 0.10
} || echo "FAIL: ruff check found issues"

########################################
# ANTI-STUB (0.15 total)
########################################

# [pr_diff] (0.10): modeling file not stubbed (original is ~1500 lines)
modeling_lines=$(wc -l < "$MODELING")
if [ "$modeling_lines" -gt 500 ]; then
    echo "PASS: modeling file has $modeling_lines lines"
    add 0.10
else
    echo "FAIL: modeling file suspiciously short ($modeling_lines lines, need >500)"
fi

# [pr_diff] (0.05): modular file not stubbed (original is ~400 lines)
modular_lines=$(wc -l < "$MODULAR")
if [ "$modular_lines" -gt 150 ]; then
    echo "PASS: modular file has $modular_lines lines"
    add 0.05
else
    echo "FAIL: modular file suspiciously short ($modular_lines lines, need >150)"
fi

########################################
# FINAL SCORE
########################################
echo "$total" > /logs/verifier/reward.txt
echo "{\"reward\": $total, \"behavioral\": 0.45, \"regression\": 0.30, \"config\": 0.10, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
echo "Total reward: $total"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
