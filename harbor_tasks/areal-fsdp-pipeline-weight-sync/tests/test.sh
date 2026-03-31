#!/usr/bin/env bash
set +e

TOTAL=0
FILE="/repo/areal/engine/fsdp_engine.py"
CORE_PASSED=0

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "PASS: syntax OK"
else
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== FAIL-TO-PASS: Pipelined async broadcast in main loop (0.35) ==="
# [pr_diff] (0.35): The core bug is that _update_weights_from_distributed processes
# each bucket fully synchronously. A correct fix must overlap the broadcast of
# bucket i with the preparation of bucket i+1 (deferred wait pattern).
# WHY AST: Requires NCCL multi-rank distributed runtime, cannot execute on CPU.
if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

# Find _update_weights_from_distributed in FSDPEngine
main_fn = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_weights_from_distributed':
                main_fn = item
                break

if not main_fn:
    print("_update_weights_from_distributed not found in FSDPEngine")
    sys.exit(1)

# 1. Must have a for loop (iterates over buckets)
for_loops = [n for n in ast.walk(main_fn) if isinstance(n, ast.For)]
if not for_loops:
    print("No for loop — not iterating over buckets")
    sys.exit(1)

main_loop = for_loops[0]

# 2. Pipeline pattern: a variable is assigned from a self.method() call inside
# the loop AND the same variable is read back within the loop (deferred wait).
# This detects the "pending = dispatch(); ... if pending: wait(pending)" pattern
# across iterations — the key behavioral difference from synchronous code.
dispatch_targets = set()
for stmt in ast.walk(main_loop):
    if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
        call = stmt.value
        if isinstance(call.func, ast.Attribute):
            if isinstance(call.func.value, ast.Name) and call.func.value.id == 'self':
                for tgt in stmt.targets:
                    if isinstance(tgt, ast.Name):
                        dispatch_targets.add(tgt.id)

# Check those variables are also READ in the loop (used across iterations)
read_in_loop = set()
for stmt in ast.walk(main_loop):
    if isinstance(stmt, ast.Name) and isinstance(stmt.ctx, ast.Load):
        read_in_loop.add(stmt.id)

pipeline_vars = dispatch_targets & read_in_loop
if not pipeline_vars:
    print("No deferred-wait pipeline pattern: no variable is both dispatched and read across iterations")
    sys.exit(1)

# 3. try/finally for error safety — finally block must have real drain logic
has_try_finally = False
for child in ast.walk(main_fn):
    if isinstance(child, ast.Try) and child.finalbody:
        finally_stmts = [s for s in child.finalbody if not isinstance(s, ast.Pass)]
        if len(finally_stmts) >= 1:
            has_try_finally = True
            break

if not has_try_finally:
    print("No try/finally with drain logic for error safety")
    sys.exit(1)

# 4. Anti-stub: method must be substantial (>=15 meaningful AST nodes)
meaningful = sum(1 for n in ast.walk(main_fn)
                 if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.While,
                                   ast.If, ast.With, ast.Try, ast.Return, ast.Call)))
if meaningful < 15:
    print(f"Method too simple ({meaningful} meaningful nodes, need >=15) — likely stubbed")
    sys.exit(1)

print(f"PASS: pipeline vars={pipeline_vars}, try/finally OK, {meaningful} meaningful nodes")
sys.exit(0)
PYEOF
then
    echo "PASS: main loop has pipelined async broadcast"
    add_score 0.35
    CORE_PASSED=1
else
    echo "FAIL: main loop is still synchronous or missing error safety"
fi

echo ""
echo "=== FAIL-TO-PASS: Async bucket method with broadcast logic (0.15) ==="
# [pr_diff] (0.15): A method must exist that starts a bucket broadcast
# asynchronously and returns a pending state object (not None). Must contain
# real distributed logic (broadcast/async_op) with >=8 meaningful statements.
# WHY AST: Requires NCCL runtime.
if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

# Find FSDPEngine methods
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            # Skip the original sync method and the main loop method
            if item.name in ('_update_bucket_weights_from_distributed',
                             '_update_weights_from_distributed'):
                continue
            if item.name.startswith('_init'):
                continue

            # Must return a non-None value
            returns_value = False
            for child in ast.walk(item):
                if isinstance(child, ast.Return) and child.value is not None:
                    if not (isinstance(child.value, ast.Constant) and child.value.value is None):
                        returns_value = True

            if not returns_value:
                continue

            # Must have real distributed logic: broadcast call or async_op kwarg
            has_dist_op = False
            for child in ast.walk(item):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in ('broadcast', 'all_reduce', '_broadcast_coalesced',
                                           'broadcast_object_list'):
                        has_dist_op = True
                if isinstance(child, ast.keyword) and child.arg == 'async_op':
                    has_dist_op = True

            if not has_dist_op:
                continue

            # Anti-stub: >=8 meaningful statements
            meaningful = sum(1 for n in ast.walk(item)
                           if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.While,
                                             ast.If, ast.With, ast.Try, ast.Return, ast.Call)))
            if meaningful < 8:
                continue

            print(f"PASS: {item.name} returns value, has dist ops, {meaningful} meaningful nodes")
            sys.exit(0)

print("No async bucket broadcast method found with real distributed logic")
sys.exit(1)
PYEOF
then
    echo "PASS: async bucket method found"
    add_score 0.15
else
    echo "FAIL: no async bucket method"
fi

echo ""
echo "=== BEHAVIORAL: Pending state data structure used in FSDPEngine (0.10) ==="
# [pr_diff] (0.10): A data structure with >=3 fields must track in-flight broadcast
# state, AND it must be actually instantiated/referenced in FSDPEngine methods
# (not just declared but unused).
# WHY AST: dataclass definition inspection.
if [ "$CORE_PASSED" = "1" ]; then
    if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

# Find classes with >=3 annotated fields (pending state candidates)
candidate_classes = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name != 'FSDPEngine':
        fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.add(item.target.id)
        if len(fields) >= 3:
            candidate_classes.append(node.name)

if not candidate_classes:
    print("No data structure with >=3 annotated fields")
    sys.exit(1)

# Check at least one candidate is INSTANTIATED in FSDPEngine
# (not just referenced in a type annotation — must appear as ClassName(...) call)
engine_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        engine_node = node
        break

if not engine_node:
    sys.exit(1)

for call_node in ast.walk(engine_node):
    if isinstance(call_node, ast.Call):
        func = call_node.func
        # ClassName(...) call
        if isinstance(func, ast.Name) and func.id in candidate_classes:
            print(f"PASS: {func.id} is instantiated in FSDPEngine")
            sys.exit(0)
        # module.ClassName(...) call
        if isinstance(func, ast.Attribute) and func.attr in candidate_classes:
            print(f"PASS: {func.attr} is instantiated in FSDPEngine")
            sys.exit(0)

print(f"Candidate classes {candidate_classes} exist but are never instantiated in FSDPEngine")
sys.exit(1)
PYEOF
    then
        echo "PASS: pending state data structure found and used"
        add_score 0.10
    else
        echo "FAIL: no pending state data structure or not used"
    fi
else
    echo "SKIP: gated behind core pipeline test"
fi

echo ""
echo "=== PASS-TO-PASS: Sync wrapper preserved and delegates (0.10) ==="
# [pr_diff] (0.10): _update_bucket_weights_from_distributed must still exist for
# backward compatibility. It should delegate to the async path (call >=1 self method)
# and have a real body (>=3 non-docstring stmts).
# WHY AST: requires distributed runtime.
if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_bucket_weights_from_distributed':
                # Count self.method() calls (delegation)
                self_calls = []
                for child in ast.walk(item):
                    if (isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                        and isinstance(child.func.value, ast.Name)
                        and child.func.value.id == 'self'):
                        self_calls.append(child.func.attr)

                body_stmts = [s for s in item.body
                             if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]

                if len(self_calls) >= 1 and len(body_stmts) >= 2:
                    print(f"PASS: delegates to {self_calls}, {len(body_stmts)} stmts")
                    sys.exit(0)
                else:
                    print(f"FAIL: {len(self_calls)} self calls, {len(body_stmts)} stmts")
                    sys.exit(1)

print("_update_bucket_weights_from_distributed not found")
sys.exit(1)
PYEOF
then
    echo "PASS: sync wrapper preserved and delegates"
    add_score 0.10
else
    echo "FAIL: sync wrapper missing or not delegating"
fi

echo ""
echo "=== PASS-TO-PASS: _init_weight_update_from_distributed preserved (0.05) ==="
# [pr_diff] (0.05): The init method must still exist with real body (>=3 meaningful stmts).
if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == '_init_weight_update_from_distributed':
                meaningful = sum(1 for n in ast.walk(item)
                               if isinstance(n, (ast.Assign, ast.Call, ast.If, ast.For, ast.Return)))
                if meaningful >= 3:
                    print(f"PASS: {meaningful} meaningful nodes")
                    sys.exit(0)
                else:
                    print(f"FAIL: only {meaningful} meaningful nodes — may be stubbed")
                    sys.exit(1)

print("_init_weight_update_from_distributed not found")
sys.exit(1)
PYEOF
then
    echo "PASS: init method preserved"
    add_score 0.05
else
    echo "FAIL: init method missing or stubbed"
fi

echo ""
echo "=== BEHAVIORAL: Error safety drains pending broadcasts (0.10) ==="
# [pr_diff] (0.10): The try/finally in the main method must actually drain pending
# work — the finally block must contain method calls or references to the pipeline
# variable (not just 'pass' or empty).
# WHY AST: requires distributed runtime.
if [ "$CORE_PASSED" = "1" ]; then
    if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_update_weights_from_distributed':
        for child in ast.walk(node):
            if isinstance(child, ast.Try) and child.finalbody:
                # Finally must contain at least one Call or attribute access
                has_action = False
                for stmt in ast.walk(ast.Module(body=child.finalbody, type_ignores=[])):
                    if isinstance(stmt, ast.Call):
                        has_action = True
                    if isinstance(stmt, ast.Attribute):
                        has_action = True

                if has_action:
                    print("PASS: finally block has drain logic")
                    sys.exit(0)

print("No drain logic in finally block")
sys.exit(1)
PYEOF
    then
        echo "PASS: error safety drains pending work"
        add_score 0.10
    else
        echo "FAIL: finally block has no drain logic"
    fi
else
    echo "SKIP: gated behind core pipeline test"
fi

echo ""
echo "=== BEHAVIORAL: CUDA stream for broadcast overlap (0.05) ==="
# [pr_diff] (0.05): When CUDA is available, should create a separate stream for
# overlapping broadcasts with computation. Check for Stream() constructor or
# torch.cuda.stream() context manager in the update methods.
# WHY AST: requires CUDA device.
if [ "$CORE_PASSED" = "1" ]; then
    if python3 << 'PYEOF'
import ast, sys

FILE = "/repo/areal/engine/fsdp_engine.py"
source = open(FILE).read()
tree = ast.parse(source)

# Search in _update_weights_from_distributed and any async bucket method
target_methods = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if 'update' in item.name.lower() and 'weight' in item.name.lower():
                    target_methods.add(item.name)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in target_methods:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                # torch.cuda.Stream() or cuda.Stream()
                if isinstance(func, ast.Attribute) and func.attr == 'Stream':
                    sys.exit(0)
                # torch.cuda.stream(s) context manager
                if isinstance(func, ast.Attribute) and func.attr == 'stream':
                    sys.exit(0)

print("No CUDA Stream usage in weight update methods")
sys.exit(1)
PYEOF
    then
        echo "PASS: CUDA stream for broadcast overlap"
        add_score 0.05
    else
        echo "FAIL: no CUDA stream"
    fi
else
    echo "SKIP: gated behind core pipeline test"
fi

echo ""
echo "=== CONFIG: No wildcard imports (0.05) ==="
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ 61281ba
if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == '*':
                print(f'Wildcard import from {node.module}')
                sys.exit(1)
sys.exit(0)
"; then
    echo "PASS: no wildcard imports"
    add_score 0.05
else
    echo "FAIL: wildcard import found"
fi

echo ""
echo "=== CONFIG: Broadcast uses explicit src (0.05) ==="
# [agent_config] (0.05): "Broadcast: Specify src rank explicitly" — .claude/rules/distributed.md:16 @ 61281ba
if python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
found_any = False
for node in ast.walk(tree):
    if (isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == 'broadcast'):
        found_any = True
        kw_names = [kw.arg for kw in node.keywords]
        if 'src' not in kw_names and len(node.args) < 2:
            print('broadcast() without explicit src')
            sys.exit(1)
if not found_any:
    # Accept: some implementations use broadcast_object_list or _broadcast_coalesced
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and 'broadcast' in node.func.attr.lower()):
            found_any = True
    if not found_any:
        print('No broadcast calls found')
        sys.exit(1)
sys.exit(0)
"; then
    echo "PASS: broadcast calls specify src"
    add_score 0.05
else
    echo "FAIL: broadcast missing explicit src"
fi

echo ""
echo "=== Total score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
reward = $TOTAL
data = {
    'reward': reward,
    'behavioral': round(min(reward, 0.75), 4),
    'regression': round(min(0.15, max(0, reward - 0.60)), 4),
    'config': round(min(0.10, max(0, reward - 0.85)), 4),
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
