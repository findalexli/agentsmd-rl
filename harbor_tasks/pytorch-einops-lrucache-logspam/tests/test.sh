#!/usr/bin/env bash
set +e

BEHAVIORAL=0
REGRESSION=0
CONFIG=0
TARGET="/workspace/pytorch/torch/_dynamo/decorators.py"

########################################################################
# Helper: extract _allow_in_graph_einops, execute with mocks, collect results
########################################################################
python3 << 'PYEOF'
import ast, sys, types, builtins, json

TARGET = "/workspace/pytorch/torch/_dynamo/decorators.py"
results_path = "/tmp/einops_results.json"

def fail_results():
    return {"found": False, "called": [], "stmt_count": 0,
            "has_einops_import": False, "comment_lines": 0,
            "code_lines": 0, "error": "function not found"}

try:
    with open(TARGET) as f:
        source = f.read()
except FileNotFoundError:
    json.dump(fail_results(), open(results_path, "w"))
    sys.exit(0)

tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_allow_in_graph_einops':
        func_node = node
        break

if func_node is None:
    json.dump(fail_results(), open(results_path, "w"))
    sys.exit(0)

lines = source.splitlines(keepends=True)
func_src = ''.join(lines[func_node.lineno-1:func_node.end_lineno])
func_lines = source.splitlines()[func_node.lineno-1:func_node.end_lineno]

# Structural metrics
stmt_count = sum(1 for n in ast.walk(func_node)
                 if isinstance(n, (ast.Call, ast.Import, ast.ImportFrom, ast.If, ast.Try)))
has_einops_import = any(
    isinstance(n, ast.Import) and any(a.name == 'einops' for a in n.names)
    for n in ast.walk(func_node))
comment_lines = sum(1 for l in func_lines if l.strip().startswith('#'))
code_lines = sum(1 for l in func_lines if l.strip() and not l.strip().startswith('#'))

# Execute with mocks to test behavior
called = []
def mock_allow_in_graph(fn):
    called.append(getattr(fn, '__name__', str(fn)))

torch_mock = types.ModuleType('torch')
try:
    import numpy as np
    torch_mock.randn = lambda *a, **kw: np.random.randn(*a)
except ImportError:
    torch_mock.randn = lambda *a, **kw: None

# Force einops._torch_specific import to fail so we hit the except branch
# (einops 0.8.2 may or may not have this module; mocking ensures consistent test)
orig_import = builtins.__import__
def mock_import(name, *args, **kwargs):
    if '_torch_specific' in str(name):
        raise ImportError("mocked for testing")
    return orig_import(name, *args, **kwargs)
builtins.__import__ = mock_import

ns = {'allow_in_graph': mock_allow_in_graph, 'torch': torch_mock, '__builtins__': builtins}
error = None
try:
    exec(func_src, ns)
    ns['_allow_in_graph_einops']()
except Exception as e:
    error = str(e)
finally:
    builtins.__import__ = orig_import

json.dump({
    "found": True,
    "called": called,
    "stmt_count": stmt_count,
    "has_einops_import": has_einops_import,
    "comment_lines": comment_lines,
    "code_lines": code_lines,
    "error": error,
}, open(results_path, "w"))
PYEOF

########################################################################
# Check 1 (0.45): F2P behavioral — allow_in_graph wraps rearrange + reduce
# [pr_diff] (0.45): Version check must not block allow_in_graph wrapping
########################################################################
python3 -c "
import json, sys
r = json.load(open('/tmp/einops_results.json'))
if not r['found']:
    print('FAIL: _allow_in_graph_einops not found'); sys.exit(1)
if 'rearrange' in r['called'] and 'reduce' in r['called']:
    print(f\"PASS: allow_in_graph called for {r['called']}\"); sys.exit(0)
else:
    print(f\"FAIL: called={r['called']}, need rearrange+reduce\"); sys.exit(1)
"
[ $? -eq 0 ] && BEHAVIORAL=$((BEHAVIORAL + 45))

########################################################################
# Check 2 (0.20): F2P behavioral — >=4 einops functions registered
# [pr_diff] (0.20): All einops ops should be wrapped to prevent warning spam
########################################################################
python3 -c "
import json, sys
r = json.load(open('/tmp/einops_results.json'))
expected = {'rearrange', 'reduce', 'repeat', 'einsum', 'pack', 'unpack'}
found = set(r.get('called', [])) & expected
if len(found) >= 4:
    print(f'PASS: {len(found)} einops functions registered: {sorted(found)}'); sys.exit(0)
else:
    print(f'FAIL: only {len(found)}: {sorted(found)}'); sys.exit(1)
"
[ $? -eq 0 ] && BEHAVIORAL=$((BEHAVIORAL + 20))

########################################################################
# Check 3 (0.15): Anti-stub — function has substantive body
# [pr_diff] (0.15): Must retain full einops registration logic
########################################################################
python3 -c "
import json, sys
r = json.load(open('/tmp/einops_results.json'))
if not r['found']:
    print('FAIL: not found'); sys.exit(1)
if r['stmt_count'] >= 5:
    print(f\"PASS: {r['stmt_count']} substantive AST nodes\"); sys.exit(0)
else:
    print(f\"FAIL: {r['stmt_count']} nodes (need >=5)\"); sys.exit(1)
"
[ $? -eq 0 ] && REGRESSION=$((REGRESSION + 15))

########################################################################
# Check 4 (0.10): P2P regression — function exists and imports einops
# [pr_diff] (0.10): Function signature and einops import preserved
########################################################################
python3 -c "
import json, sys
r = json.load(open('/tmp/einops_results.json'))
if r.get('found') and r.get('has_einops_import'):
    print('PASS: function exists with einops import'); sys.exit(0)
else:
    print('FAIL: function missing or no einops import'); sys.exit(1)
"
[ $? -eq 0 ] && REGRESSION=$((REGRESSION + 10))

########################################################################
# Check 5 (0.10): Config style — concise, self-documenting code
# [agent_config] (0.10): "Minimize comments; be concise" — CLAUDE.md:38 @ 98e35020
########################################################################
python3 -c "
import json, sys
r = json.load(open('/tmp/einops_results.json'))
cl = r.get('comment_lines', 0)
co = r.get('code_lines', 0)
if co > 0 and cl <= co:
    print(f'PASS: {cl} comments / {co} code lines'); sys.exit(0)
else:
    print(f'FAIL: {cl} comments / {co} code lines (too verbose)'); sys.exit(1)
"
[ $? -eq 0 ] && CONFIG=$((CONFIG + 10))

########################################################################
# Final score
########################################################################
REWARD=$((BEHAVIORAL + REGRESSION + CONFIG))
FINAL=$(python3 -c "print($REWARD / 100)")
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
json.dump({
    'reward': $REWARD / 100,
    'behavioral': $BEHAVIORAL / 100,
    'regression': $REGRESSION / 100,
    'config': $CONFIG / 100,
}, open('/logs/verifier/reward.json', 'w'))
"
echo "Total reward: $FINAL (behavioral=$BEHAVIORAL regression=$REGRESSION config=$CONFIG)"
