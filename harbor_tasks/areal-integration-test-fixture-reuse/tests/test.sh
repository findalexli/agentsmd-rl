#!/usr/bin/env bash
set +e

CTRL_FILE="/workspace/AReaL/tests/experimental/inference_service/test_controller_integration.py"
PROXY_FILE="/workspace/AReaL/tests/experimental/inference_service/test_data_proxy_integration.py"
GW_FILE="/workspace/AReaL/tests/experimental/inference_service/test_gateway_integration.py"
SCORE=0

# =========================================================================
# GATE: Python syntax check — abort on failure
# =========================================================================
# [pr_diff] (0.00): All three test files must be valid Python
for f in "$CTRL_FILE" "$PROXY_FILE" "$GW_FILE"; do
    if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$f').read())
except SyntaxError as e:
    print(f'GATE FAIL: {e}', file=sys.stderr)
    sys.exit(1)
"; then
        echo "GATE: syntax check FAILED on $(basename $f) — aborting"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "GATE: syntax OK for all files"

# =========================================================================
# Fail-to-pass: Fixtures are module-scoped or higher (0.30)
# =========================================================================
# [pr_diff] (0.30): local_scheduler, gateway_controller, gateway_controller_full_init
# must be scoped broader than function (module or session) to avoid re-creation.
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

source = open('$CTRL_FILE').read()
tree = ast.parse(source)

fixture_scopes = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                is_fixture = False
                if isinstance(func, ast.Attribute) and func.attr == 'fixture':
                    is_fixture = True
                elif isinstance(func, ast.Name) and func.id == 'fixture':
                    is_fixture = True
                if is_fixture:
                    scope = None
                    for kw in dec.keywords:
                        if kw.arg == 'scope' and isinstance(kw.value, ast.Constant):
                            scope = kw.value.value
                    fixture_scopes[node.name] = scope
            # Bare @pytest.fixture with no call → function scope (default)
            elif isinstance(dec, ast.Attribute) and dec.attr == 'fixture':
                fixture_scopes[node.name] = None

required = ['local_scheduler', 'gateway_controller', 'gateway_controller_full_init']
ok = True
for name in required:
    scope = fixture_scopes.get(name)
    # Accept 'module' or 'session' — both fix the per-test re-creation bug
    if scope not in ('module', 'session'):
        print(f'FAIL: {name} has scope={scope!r}, expected module or session', file=sys.stderr)
        ok = False
    else:
        print(f'  {name}: scope={scope} OK')

if not ok:
    sys.exit(1)
"; then
    echo "CHECK: fixtures module-scoped — PASS (0.30)"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "CHECK: fixtures module-scoped — FAIL"
fi

# =========================================================================
# Fail-to-pass: pytestmark includes pytest.mark.sglang in all 3 files (0.10)
# =========================================================================
# [pr_diff] (0.10): Module-level pytestmark replaces per-class @pytest.mark.slow
# Accepts both direct assignment and list form.
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

files = ['$CTRL_FILE', '$PROXY_FILE', '$GW_FILE']
ok = True
for fpath in files:
    source = open(fpath).read()
    tree = ast.parse(source)
    found = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'pytestmark':
                    val = node.value
                    def has_sglang_mark(n):
                        \"\"\"Check if node is or contains pytest.mark.sglang.\"\"\"
                        if isinstance(n, ast.Attribute) and n.attr == 'sglang':
                            return True
                        if isinstance(n, ast.Call):
                            return has_sglang_mark(n.func)
                        return False

                    # Direct: pytestmark = pytest.mark.sglang
                    if has_sglang_mark(val):
                        found = True
                    # List/tuple: pytestmark = [pytest.mark.sglang, ...]
                    elif isinstance(val, (ast.List, ast.Tuple)):
                        for elt in val.elts:
                            if has_sglang_mark(elt):
                                found = True
                                break
    if not found:
        print(f'FAIL: {fpath} missing pytestmark containing pytest.mark.sglang', file=sys.stderr)
        ok = False
    else:
        print(f'  {fpath}: pytestmark OK')

if not ok:
    sys.exit(1)
"; then
    echo "CHECK: pytestmark sglang in all files — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: pytestmark sglang in all files — FAIL"
fi

# =========================================================================
# Fail-to-pass: @pytest.mark.slow removed from test classes (0.10)
# =========================================================================
# [pr_diff] (0.10): No test class should have @pytest.mark.slow decorator
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

files = ['$CTRL_FILE', '$PROXY_FILE', '$GW_FILE']
ok = True
for fpath in files:
    source = open(fpath).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for dec in node.decorator_list:
                is_slow = False
                # @pytest.mark.slow
                if (isinstance(dec, ast.Attribute) and dec.attr == 'slow'
                    and isinstance(dec.value, ast.Attribute)
                    and dec.value.attr == 'mark'):
                    is_slow = True
                # @pytest.mark.slow(reason=...)
                if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == 'slow'):
                    is_slow = True
                if is_slow:
                    print(f'FAIL: {fpath} class {node.name} has @pytest.mark.slow', file=sys.stderr)
                    ok = False

if not ok:
    sys.exit(1)
print('No @pytest.mark.slow on test classes')
"; then
    echo "CHECK: @pytest.mark.slow removed — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: @pytest.mark.slow removed — FAIL"
fi

# =========================================================================
# Fail-to-pass: should_accept_fn tests removed (0.15)
# =========================================================================
# [pr_diff] (0.15): Tests referencing should_accept_fn must be removed from
# controller integration tests (incompatible with module-scoped fixtures).
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

source = open('$CTRL_FILE').read()
tree = ast.parse(source)

found_methods = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if 'should_accept_fn' in node.name:
            found_methods.append(node.name)

if found_methods:
    for m in found_methods:
        print(f'FAIL: found test method {m}', file=sys.stderr)
    sys.exit(1)
print('No should_accept_fn test methods found')
"; then
    echo "CHECK: should_accept_fn tests removed — PASS (0.15)"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "CHECK: should_accept_fn tests removed — FAIL"
fi

# =========================================================================
# Config-derived: Module-scoped fixture does not use tmp_path (0.05)
# =========================================================================
# [agent_config] (0.05): "Scope expensive fixtures appropriately"
# — .claude/rules/testing.md:55 @ dfeab639
# tmp_path is function-scoped; module-scoped fixtures must use tmp_path_factory
# or another approach (tempfile.mkdtemp, etc.).
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

source = open('$CTRL_FILE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'local_scheduler':
        param_names = [a.arg for a in node.args.args]
        if 'tmp_path' in param_names:
            print('FAIL: local_scheduler uses tmp_path (incompatible with module scope)', file=sys.stderr)
            sys.exit(1)
        # Accept tmp_path_factory, tempfile.mkdtemp, or any other approach
        print(f'local_scheduler params: {param_names} — no tmp_path conflict')
        sys.exit(0)
print('FAIL: local_scheduler fixture not found', file=sys.stderr)
sys.exit(1)
"; then
    echo "CHECK: fixture avoids tmp_path — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: fixture avoids tmp_path — FAIL"
fi

# =========================================================================
# Pass-to-pass: Core test classes still present (0.10)
# =========================================================================
# [pr_diff] (0.10): All non-removed test classes must still exist
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys

ok = True

# Check controller test classes
source = open('$CTRL_FILE').read()
tree = ast.parse(source)
ctrl_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
required_ctrl = [
    'TestControllerLifecycle', 'TestControllerVersioning',
    'TestControllerPauseResume', 'TestControllerRolloutBatch',
    'TestControllerPrepareBatch', 'TestControllerSubmitWait',
    'TestControllerFullInitialization',
]
for cls in required_ctrl:
    if cls not in ctrl_classes:
        print(f'FAIL: missing class {cls} in controller tests', file=sys.stderr)
        ok = False

# Check data proxy test classes
source = open('$PROXY_FILE').read()
tree = ast.parse(source)
proxy_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
for cls in ['TestChatCompletionsIntegration', 'TestPauseResumeIntegration', 'TestConcurrentPauseDuringGeneration']:
    if cls not in proxy_classes:
        print(f'FAIL: missing class {cls} in data proxy tests', file=sys.stderr)
        ok = False

# Check gateway test classes
source = open('$GW_FILE').read()
tree = ast.parse(source)
gw_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
for cls in ['TestGatewayStackHealth', 'TestGatewayChatCompletions', 'TestGatewaySessionLifecycle', 'TestGatewayAuth', 'TestGatewayPauseContinue']:
    if cls not in gw_classes:
        print(f'FAIL: missing class {cls} in gateway tests', file=sys.stderr)
        ok = False

if not ok:
    sys.exit(1)
print('All required test classes present')
"; then
    echo "CHECK: core test classes preserved — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: core test classes preserved — FAIL"
fi

# =========================================================================
# Pass-to-pass: _FakeDataLoader helper still present (0.05)
# =========================================================================
# [pr_diff] (0.05): _FakeDataLoader helper class must not be removed
# WHY AST: test modules import torch, areal.* (GPU-dependent) — cannot import.
if python3 -c "
import ast, sys
source = open('$CTRL_FILE').read()
tree = ast.parse(source)
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
if '_FakeDataLoader' not in classes:
    print('FAIL: _FakeDataLoader removed', file=sys.stderr)
    sys.exit(1)
print('_FakeDataLoader present')
"; then
    echo "CHECK: _FakeDataLoader preserved — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: _FakeDataLoader preserved — FAIL"
fi

# =========================================================================
# Anti-stub: files have substantial content with real test methods (0.10)
# =========================================================================
# [pr_diff] (0.10): Test files must not be stubbed out or emptied
if python3 -c "
import ast, sys

min_lines = 100
min_methods = 3

for fpath in ['$CTRL_FILE', '$PROXY_FILE', '$GW_FILE']:
    source = open(fpath).read()
    lines = len(source.splitlines())
    if lines < min_lines:
        print(f'FAIL: {fpath} has only {lines} lines (min {min_lines})', file=sys.stderr)
        sys.exit(1)

    tree = ast.parse(source)
    test_methods = [n for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name.startswith('test_')]
    if len(test_methods) < min_methods:
        print(f'FAIL: {fpath} has only {len(test_methods)} test methods (min {min_methods})', file=sys.stderr)
        sys.exit(1)

    # Reject files where majority of test methods are stubs (pass or docstring-only)
    stub_count = 0
    for m in test_methods:
        body = m.body
        if len(body) <= 1:
            stmt = body[0] if body else None
            if isinstance(stmt, ast.Pass):
                stub_count += 1
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                stub_count += 1  # docstring-only
    if stub_count > len(test_methods) // 2:
        print(f'FAIL: {fpath} has {stub_count}/{len(test_methods)} stub test methods', file=sys.stderr)
        sys.exit(1)

    print(f'  {fpath}: {lines} lines, {len(test_methods)} test methods ({stub_count} stubs) OK')
"; then
    echo "CHECK: anti-stub — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: anti-stub — FAIL"
fi

# =========================================================================
# Config-derived: No wildcard imports (0.05)
# =========================================================================
# [agent_config] (0.05): "No wildcard imports (from x import *)"
# — AGENTS.md:30 @ dfeab639
if python3 -c "
import ast, sys

for fpath in ['$CTRL_FILE', '$PROXY_FILE', '$GW_FILE']:
    source = open(fpath).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == '*':
                    print(f'FAIL: wildcard import in {fpath}: from {node.module} import *', file=sys.stderr)
                    sys.exit(1)
print('No wildcard imports')
"; then
    echo "CHECK: no wildcard imports — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: no wildcard imports — FAIL"
fi

# =========================================================================
# Final score
# =========================================================================

echo ""
echo "=== TOTAL SCORE: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
# F2P: scope(0.30) + pytestmark(0.10) + slow_removed(0.10) + should_accept(0.15) + tmp_path(0.05) = 0.70
behavioral = min(score, 0.70)
# P2P: classes(0.10) + FakeDataLoader(0.05) + anti-stub(0.10) = 0.25
regression = max(0, min(score - 0.70, 0.25))
# Config: no_wildcards(0.05) = 0.05
config = max(0, min(score - 0.95, 0.05))
print(json.dumps({'reward': round(score, 2), 'behavioral': round(behavioral, 2), 'regression': round(regression, 2), 'config': round(config, 2), 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
