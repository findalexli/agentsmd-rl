#!/usr/bin/env bash
# Test: sglang-session-mm-leak
# Weights: 0.70 behavioral (F2P) + 0.10 P2P + 0.20 structural = 1.00
set -euo pipefail

BATCH_FILE="/workspace/python/sglang/srt/managers/schedule_batch.py"
SESSION_FILE="/workspace/python/sglang/srt/managers/session_controller.py"
SCHEDULER_FILE="/workspace/python/sglang/srt/managers/scheduler.py"
OUTPUT_PROC_FILE="/workspace/python/sglang/srt/managers/scheduler_output_processor_mixin.py"
REWARD=0

add_score() {
    REWARD=$(python3 -c "print(round($REWARD + $1, 2))")
}

###############################################################################
# GATE: Syntax check — score 0 on failure
###############################################################################
# [pr_diff] (0.00): All modified files must be valid Python
for f in "$BATCH_FILE" "$SESSION_FILE" "$SCHEDULER_FILE" "$OUTPUT_PROC_FILE"; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())"; then
        echo "GATE FAIL: syntax error in $f"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "GATE PASS: all files have valid syntax"

set +e  # Don't abort on individual check failures

###############################################################################
# FAIL-TO-PASS BEHAVIORAL (0.70 total)
###############################################################################

# [pr_diff] (0.30): release_features() method on MultimodalInputs releases all features
# HOW: AST-extract the method, call it with mock objects, verify features are None.
# BUGGY baseline: method doesn't exist → FAIL
# FIXED: method iterates mm_items setting feature=None → PASS
# WHY AST: schedule_batch.py imports torch at module level; can't import on CPU
cat > /tmp/test_release_features.py << 'PYEOF'
import sys, ast, textwrap

BATCH_FILE = "/workspace/python/sglang/srt/managers/schedule_batch.py"
with open(BATCH_FILE) as f:
    source = f.read()

tree = ast.parse(source)

# Find release_features (or any feature-releasing method) in MultimodalInputs
method_node = None
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'MultimodalInputs':
        cls_node = node
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'release_features':
                method_node = item
                break
        break

if cls_node is None:
    print("FAIL: MultimodalInputs class not found")
    sys.exit(1)

if method_node is None:
    print("FAIL: release_features method not found on MultimodalInputs")
    sys.exit(1)

method_source = ast.get_source_segment(source, method_node)
if method_source is None:
    print("FAIL: could not extract release_features source")
    sys.exit(1)

# Build testable class with the extracted method
exec_env = {"__builtins__": __builtins__}
exec(textwrap.dedent(f"""
class MockItem:
    def __init__(self, feature):
        self.feature = feature

class MultimodalInputs:
    def __init__(self, mm_items):
        self.mm_items = mm_items

{textwrap.indent(method_source, '    ')}
"""), exec_env)

MockItem = exec_env['MockItem']
MMInputs = exec_env['MultimodalInputs']

# Test 1: multiple features are released
items = [MockItem("tensor_a"), MockItem("tensor_b"), MockItem("tensor_c")]
inputs = MMInputs(items)
inputs.release_features()
for i, item in enumerate(items):
    feat = getattr(item, 'feature', None)
    if feat is not None:
        print(f"FAIL: item {i} feature not released (got {feat!r})")
        sys.exit(1)

# Test 2: empty list doesn't crash
MMInputs([]).release_features()

# Test 3: single item
single = [MockItem(42)]
MMInputs(single).release_features()
if getattr(single[0], 'feature', None) is not None:
    print("FAIL: single item feature not released")
    sys.exit(1)

# Test 4: calling twice doesn't crash (idempotent)
items2 = [MockItem("x")]
mm2 = MMInputs(items2)
mm2.release_features()
mm2.release_features()

print("PASS: release_features correctly releases all features")
PYEOF

if python3 /tmp/test_release_features.py 2>&1; then
    add_score 0.30
    echo "PASS (0.30): release_features method works"
else
    echo "FAIL (0.30): release_features method"
fi

# [pr_diff] (0.25): _close() releases multimodal features from session requests
# HOW: AST-extract _close method, run with mock objects, verify mm features freed.
# BUGGY baseline: _close doesn't touch multimodal_inputs → features survive → FAIL
# FIXED: _close iterates req_nodes, releases features, clears mm_inputs → PASS
# WHY AST: session_controller.py imports sglang internals; can't import on CPU
cat > /tmp/test_close_releases_mm.py << 'PYEOF'
import sys, ast, textwrap

SESSION_FILE = "/workspace/python/sglang/srt/managers/session_controller.py"
with open(SESSION_FILE) as f:
    source = f.read()

tree = ast.parse(source)

# Find _close method in SessionController
close_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SessionController':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_close':
                close_node = item
                break
        break

if close_node is None:
    print("FAIL: SessionController._close method not found")
    sys.exit(1)

close_source = ast.get_source_segment(source, close_node)
if close_source is None:
    print("FAIL: could not extract _close source")
    sys.exit(1)

# Build mock environment with everything _close might reference
exec_env = {"__builtins__": __builtins__}
exec(textwrap.dedent("""
import logging

# Provide SessionAwareCache so isinstance() checks work
class SessionAwareCache:
    pass

class MockTreeCache(SessionAwareCache):
    def release_session(self, sid):
        pass

class MockMMItem:
    def __init__(self):
        self.feature = "gpu_tensor_data"

class MockMMInputs:
    def __init__(self, items):
        self.mm_items = items
    def release_features(self):
        for item in self.mm_items:
            item.feature = None

class MockReq:
    def __init__(self, mm_inputs=None):
        self.multimodal_inputs = mm_inputs
        self.session = "active_session"
    def finished(self):
        return True

class MockNode:
    def __init__(self, req):
        self.req = req

class Session:
    def __init__(self, nodes):
        self.req_nodes = nodes
        self.streaming = False

class SessionController:
    def __init__(self, session, sid):
        self.sessions = {sid: session}
        self.tree_cache = MockTreeCache()
"""), exec_env)

# Create a patched class with the extracted _close method
exec(textwrap.dedent(f"""
class SessionControllerTest(SessionController):
{textwrap.indent(close_source, '    ')}
"""), exec_env)

MockMMItem = exec_env['MockMMItem']
MockMMInputs = exec_env['MockMMInputs']
MockReq = exec_env['MockReq']
MockNode = exec_env['MockNode']
Session = exec_env['Session']
TestController = exec_env['SessionControllerTest']

# Setup: session with requests holding multimodal features
shared_items = [MockMMItem(), MockMMItem()]
shared_mm = MockMMInputs(shared_items)
own_items = [MockMMItem()]
own_mm = MockMMInputs(own_items)

nodes = {
    "r1": MockNode(MockReq(shared_mm)),
    "r2": MockNode(MockReq(shared_mm)),   # shares mm with r1
    "r3": MockNode(MockReq(own_mm)),
    "r4": MockNode(MockReq(None)),         # no multimodal
}

session = Session(nodes)
controller = TestController(session, "s1")

# Verify setup: features are alive before _close
assert all(i.feature is not None for i in shared_items + own_items), "Setup broken"

# Call _close — this should release all multimodal features
controller._close("s1")

# Check 1: all features released (accepts both setting None and deleting attr)
for label, items in [("shared", shared_items), ("own", own_items)]:
    for i, item in enumerate(items):
        feat = getattr(item, 'feature', None)
        if feat is not None:
            print(f"FAIL: {label} item {i} feature not released (got {feat!r})")
            sys.exit(1)

# Check 2: multimodal_inputs cleared from all requests
for key, node in nodes.items():
    mm = getattr(node.req, 'multimodal_inputs', None)
    if mm is not None:
        print(f"FAIL: {key} multimodal_inputs not cleared")
        sys.exit(1)

# Check 3: session removed from controller
if "s1" in controller.sessions:
    print("FAIL: session not deleted after _close")
    sys.exit(1)

print("PASS: _close correctly releases multimodal features")
PYEOF

if python3 /tmp/test_close_releases_mm.py 2>&1; then
    add_score 0.25
    echo "PASS (0.25): _close releases multimodal features"
else
    echo "FAIL (0.25): _close multimodal cleanup"
fi

# [pr_diff] (0.15): BOS offset clamping prevents negative offsets in create_req
# HOW: AST-extract the offset adjustment expression from create_req, evaluate it
#      with edge-case inputs (s=0), verify no negative values produced.
# BUGGY baseline: (s-1, e-1) with s=0 → (-1, 4) → FAIL
# FIXED: any correct clamping (max, if/else, clamp) → (0, 4) → PASS
# WHY AST: session_controller.py can't be imported on CPU
cat > /tmp/test_bos_clamping.py << 'PYEOF'
import sys, ast

SESSION_FILE = "/workspace/python/sglang/srt/managers/session_controller.py"
with open(SESSION_FILE) as f:
    source = f.read()

tree = ast.parse(source)

# Find create_req in Session class
create_req_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Session':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'create_req':
                create_req_node = item
                break
        break

if create_req_node is None:
    print("FAIL: Session.create_req not found")
    sys.exit(1)

# Find assignments to .offsets that contain subtraction (the BOS adjustment)
# We look for any assignment to an attribute named 'offsets' whose RHS involves Sub
offset_assigns = []
for node in ast.walk(create_req_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Attribute) and target.attr == 'offsets':
                # Check if RHS contains subtraction (offset adjustment)
                has_sub = any(isinstance(n, ast.Sub) for n in ast.walk(node.value))
                if has_sub:
                    offset_assigns.append(node)

if not offset_assigns:
    print("FAIL: no offset adjustment (with subtraction) found in create_req")
    sys.exit(1)

# Test each offset assignment expression with edge-case inputs
tested = False
for assign_node in offset_assigns:
    rhs = assign_node.value
    rhs_source = ast.get_source_segment(source, rhs)
    if rhs_source is None:
        continue

    # The RHS should be a comprehension or expression iterating over offsets.
    # We need to evaluate it with test data.
    # Strategy: find the iteration variable source and replace it with test data.
    if isinstance(rhs, ast.ListComp):
        for gen in rhs.generators:
            iter_src = ast.get_source_segment(source, gen.iter)
            if iter_src is None:
                continue
            # Replace the iteration source with our test variable
            test_expr = rhs_source.replace(iter_src, "test_offsets")

            # Edge case inputs: s=0 (BOS position), s=0/e=0, normal case
            test_cases = [
                ([(0, 5), (3, 8)], "BOS edge case"),
                ([(0, 0)], "double-zero edge"),
                ([(1, 10), (5, 20)], "normal offsets"),
            ]

            for test_offsets, label in test_cases:
                try:
                    ns = {"test_offsets": test_offsets, "max": max, "min": min}
                    result = eval(test_expr, ns)
                except Exception as e:
                    print(f"FAIL: could not evaluate offset expr for {label}: {e}")
                    sys.exit(1)

                # Verify: no negative values in any tuple
                for pair in result:
                    for v in pair:
                        if v < 0:
                            print(f"FAIL: negative offset in {label}: {result}")
                            sys.exit(1)

            # Verify the adjustment actually does something (subtracts)
            normal_input = [(5, 10)]
            ns = {"test_offsets": normal_input, "max": max, "min": min}
            normal_result = eval(test_expr, ns)
            if normal_result[0][0] >= normal_input[0][0]:
                print(f"FAIL: offset not adjusted downward: {normal_input} -> {normal_result}")
                sys.exit(1)

            tested = True
            break
    else:
        # Not a listcomp — might be a different valid implementation
        # Try to find a for loop that modifies offsets
        # Fall back: check that the whole create_req source doesn't have the raw
        # (s - 1, e - 1) without clamping by looking for Sub without max/clamp guard
        pass

    if tested:
        break

if not tested:
    # Fallback: check that the offset adjustment doesn't produce negatives
    # by looking at the create_req source for any clamping mechanism
    create_src = ast.get_source_segment(source, create_req_node)
    # Search for any for-loop body that modifies offsets
    for node in ast.walk(create_req_node):
        if isinstance(node, ast.For):
            for_src = ast.get_source_segment(source, node)
            if for_src and 'offsets' in for_src and '-' in for_src:
                # Found a for loop that adjusts offsets with subtraction
                # Check it handles the s=0 case (any clamping mechanism)
                # We can't easily eval arbitrary for-loop code, so check
                # that there's SOME guard against negatives
                has_guard = False
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        func = sub_node.func
                        if isinstance(func, ast.Name) and func.id in ('max', 'clamp'):
                            has_guard = True
                    if isinstance(sub_node, ast.Compare):
                        # e.g. if s > 0 or s == 0
                        has_guard = True
                    if isinstance(sub_node, ast.IfExp):
                        has_guard = True
                if has_guard:
                    tested = True
                    break

if not tested:
    print("FAIL: no clamping found for BOS offset edge case in create_req")
    sys.exit(1)

print("PASS: BOS offset clamping prevents negative offsets")
PYEOF

if python3 /tmp/test_bos_clamping.py 2>&1; then
    add_score 0.15
    echo "PASS (0.15): BOS offset clamping"
else
    echo "FAIL (0.15): BOS offset clamping"
fi

###############################################################################
# PASS-TO-PASS (0.10 total)
###############################################################################

# [pr_diff] (0.10): Core class/method structure preserved across all files
cat > /tmp/test_structure_p2p.py << 'PYEOF'
import sys, ast

checks = {
    "/workspace/python/sglang/srt/managers/schedule_batch.py": {
        "MultimodalInputs": None,
        "MultimodalDataItem": None,
    },
    "/workspace/python/sglang/srt/managers/session_controller.py": {
        "SessionReqNode": ["clear_children", "clear", "abort"],
        "Session": ["create_req", "is_timed_out"],
        "SessionController": ["open", "close", "_close", "maybe_reap"],
    },
}

for filepath, classes in checks.items():
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    found_classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes:
            found_classes[node.name] = {
                n.name for n in node.body if isinstance(n, ast.FunctionDef)
            }

    for cls_name, methods in classes.items():
        if cls_name not in found_classes:
            print(f"FAIL: class {cls_name} missing from {filepath}")
            sys.exit(1)
        if methods:
            for m in methods:
                if m not in found_classes[cls_name]:
                    print(f"FAIL: {cls_name}.{m} missing from {filepath}")
                    sys.exit(1)

print("PASS: core class/method structure preserved")
PYEOF

if python3 /tmp/test_structure_p2p.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): class structure preserved"
else
    echo "FAIL (0.10): class structure"
fi

###############################################################################
# STRUCTURAL / ANTI-STUB (0.20 total)
# AST justified: scheduler.py and output_processor import torch; can't import on CPU
###############################################################################

# [pr_diff] (0.10): release_features is non-trivial (rejects stubs)
cat > /tmp/test_antistub.py << 'PYEOF'
import sys, ast

BATCH_FILE = "/workspace/python/sglang/srt/managers/schedule_batch.py"
with open(BATCH_FILE) as f:
    source = f.read()

tree = ast.parse(source)

method = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'MultimodalInputs':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'release_features':
                method = item
                break
        break

if method is None:
    print("FAIL: release_features not found")
    sys.exit(1)

# Count meaningful statements (exclude docstrings, pass, ellipsis)
meaningful = 0
for node in ast.walk(method):
    if isinstance(node, ast.For):
        meaningful += 1
    elif isinstance(node, ast.Assign):
        meaningful += 1
    elif isinstance(node, ast.AugAssign):
        meaningful += 1
    elif isinstance(node, (ast.If, ast.While)):
        meaningful += 1

if meaningful < 2:
    print(f"FAIL: release_features appears to be a stub ({meaningful} meaningful statements)")
    sys.exit(1)

print(f"PASS: release_features has {meaningful} meaningful statements")
PYEOF

if python3 /tmp/test_antistub.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): anti-stub release_features"
else
    echo "FAIL (0.10): anti-stub release_features"
fi

# [pr_diff] (0.10): Callers in scheduler and output_processor call release_features()
# Uses AST to find actual method calls (not string search — comments don't match)
cat > /tmp/test_callers.py << 'PYEOF'
import sys, ast

files = [
    "/workspace/python/sglang/srt/managers/scheduler.py",
    "/workspace/python/sglang/srt/managers/scheduler_output_processor_mixin.py",
]

for filepath in files:
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    # Look for actual method calls: something.release_features()
    found_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == 'release_features':
                found_call = True
                break

    if not found_call:
        print(f"FAIL: {filepath} does not call .release_features() (AST method call)")
        sys.exit(1)

print("PASS: scheduler and output_processor call release_features()")
PYEOF

if python3 /tmp/test_callers.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): callers use release_features"
else
    echo "FAIL (0.10): callers don't use release_features"
fi

###############################################################################
# FINAL SCORE
###############################################################################

echo ""
echo "=== Final Score ==="
echo "Reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
reward = float('$REWARD')
json.dump({'reward': reward}, open('/logs/verifier/reward.json', 'w'))
print(f'reward.json written: {reward}')
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
