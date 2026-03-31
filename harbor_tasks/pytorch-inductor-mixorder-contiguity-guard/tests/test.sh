#!/usr/bin/env bash
set +e

SCHEDULER="/workspace/torch/_inductor/scheduler.py"
REWARD=0

add_score() {
    REWARD=$(python3 -c "print($REWARD + $1)")
}

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0.00): File must be valid Python
if python3 -c "import ast; ast.parse(open('$SCHEDULER').read())"; then
    echo "GATE PASS: syntax ok"
else
    echo "GATE FAIL: syntax error in scheduler.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

###############################################################################
# BEHAVIORAL FAIL-TO-PASS (0.50)
# Extracts sub_node_can_fuse, calls it with mock objects, checks behavior.
###############################################################################

# [pr_diff] (0.50): sub_node_can_fuse must reject fusion when node1 is contiguous
# but node2 is non-contiguous.
#
# WHY extraction: sub_node_can_fuse references self.scheduler.can_fuse,
# OrderedSet, MixOrderReduction.is_contiguous_node, typing.cast, self.numel —
# all of which require the full Inductor runtime. We extract the function body
# via AST and exec it with lightweight mocks, then CALL it to test behavior.
cat > /tmp/test_f2p_contiguity.py << 'PYEOF'
import ast, sys, textwrap, typing

SCHEDULER = sys.argv[1]
with open(SCHEDULER) as f:
    source = f.read()
lines = source.splitlines(keepends=True)
tree = ast.parse(source)

# --- Extract sub_node_can_fuse ---
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                break

if func_src is None:
    print("FAIL: sub_node_can_fuse not found in FusedMixOrderReductions")
    sys.exit(1)

# --- Minimal mocks ---
class OrderedSet(set):
    """Stand-in for torch.utils._ordered_set.OrderedSet."""
    def union(self, *others):
        out = OrderedSet(self)
        for o in others:
            out.update(o)
        return out

class MockNode:
    def __init__(self, contiguous, is_red=False, ancestors=None, names=None):
        self._contiguous = contiguous
        self._is_red = is_red
        self.ancestors = OrderedSet(ancestors or [])
        self._names = OrderedSet(names or [])
    def is_reduction(self):
        return self._is_red
    def get_operation_names(self):
        return self._names

class MixOrderReduction:
    @classmethod
    def is_contiguous_node(cls, node):
        return getattr(node, "_contiguous", False)

class FusedMixOrderReductions:
    pass

class MockScheduler:
    def can_fuse(self, n1, n2, allow_mix_order_reduction=False):
        return True
    def score_fusion_memory(self, n1, n2, count_bytes=False):
        return 999999

class MockSelf:
    def __init__(self):
        self.scheduler = MockScheduler()
        self.numel = 100

# --- Compile extracted function ---
ns = {
    "MixOrderReduction": MixOrderReduction,
    "FusedMixOrderReductions": FusedMixOrderReductions,
    "OrderedSet": OrderedSet,
    "typing": typing,
    "__builtins__": __builtins__,
}
try:
    exec(func_src, ns)
except Exception as e:
    print(f"FAIL: could not compile sub_node_can_fuse: {e}")
    sys.exit(1)

func = ns["sub_node_can_fuse"]
mock_self = MockSelf()

# TEST: contiguous node1 + non-contiguous node2 → must return False
node1 = MockNode(contiguous=True)
node2 = MockNode(contiguous=False)
result = func(mock_self, node1, node2, ())

if result is False:
    print("PASS: contiguity guard rejects contiguous + non-contiguous fusion")
else:
    print(f"FAIL: expected False for contiguous+non-contiguous, got {result!r}")
    sys.exit(1)
PYEOF

if python3 /tmp/test_f2p_contiguity.py "$SCHEDULER"; then
    add_score 0.50
else
    echo "FAIL: F2P contiguity guard test"
fi

###############################################################################
# BEHAVIORAL PASS-TO-PASS (0.25)
# The contiguity guard must NOT over-reject valid fusions.
###############################################################################

# [pr_diff] (0.15): contiguous + contiguous → fusion allowed
cat > /tmp/test_p2p_both_contiguous.py << 'PYEOF'
import ast, sys, textwrap, typing

SCHEDULER = sys.argv[1]
with open(SCHEDULER) as f:
    source = f.read()
lines = source.splitlines(keepends=True)
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                break

if func_src is None:
    print("FAIL: sub_node_can_fuse not found")
    sys.exit(1)

class OrderedSet(set):
    def union(self, *others):
        out = OrderedSet(self)
        for o in others:
            out.update(o)
        return out

class MockNode:
    def __init__(self, contiguous, is_red=False, ancestors=None, names=None):
        self._contiguous = contiguous
        self._is_red = is_red
        self.ancestors = OrderedSet(ancestors or [])
        self._names = OrderedSet(names or [])
    def is_reduction(self):
        return self._is_red
    def get_operation_names(self):
        return self._names

class MixOrderReduction:
    @classmethod
    def is_contiguous_node(cls, node):
        return getattr(node, "_contiguous", False)

class FusedMixOrderReductions:
    pass

class MockScheduler:
    def can_fuse(self, n1, n2, allow_mix_order_reduction=False):
        return True
    def score_fusion_memory(self, n1, n2, count_bytes=False):
        return 999999

class MockSelf:
    def __init__(self):
        self.scheduler = MockScheduler()
        self.numel = 100

ns = {
    "MixOrderReduction": MixOrderReduction,
    "FusedMixOrderReductions": FusedMixOrderReductions,
    "OrderedSet": OrderedSet,
    "typing": typing,
    "__builtins__": __builtins__,
}
try:
    exec(func_src, ns)
except Exception as e:
    print(f"FAIL: could not compile: {e}")
    sys.exit(1)

func = ns["sub_node_can_fuse"]
mock_self = MockSelf()

# Both contiguous, non-reduction → should allow fusion (return truthy)
node1 = MockNode(contiguous=True)
node2 = MockNode(contiguous=True)
result = func(mock_self, node1, node2, ())

if result is not False and result:
    print("PASS: contiguous + contiguous fusion allowed")
else:
    print(f"FAIL: contiguous + contiguous should allow fusion, got {result!r}")
    sys.exit(1)
PYEOF

if python3 /tmp/test_p2p_both_contiguous.py "$SCHEDULER"; then
    add_score 0.15
else
    echo "FAIL: P2P both-contiguous test"
fi

# [pr_diff] (0.10): non-contiguous node1 + contiguous node2 → fusion allowed
# (the guard should only trigger when node1 IS contiguous and node2 is NOT)
cat > /tmp/test_p2p_noncontig_contig.py << 'PYEOF'
import ast, sys, textwrap, typing

SCHEDULER = sys.argv[1]
with open(SCHEDULER) as f:
    source = f.read()
lines = source.splitlines(keepends=True)
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                break

if func_src is None:
    print("FAIL: sub_node_can_fuse not found")
    sys.exit(1)

class OrderedSet(set):
    def union(self, *others):
        out = OrderedSet(self)
        for o in others:
            out.update(o)
        return out

class MockNode:
    def __init__(self, contiguous, is_red=False, ancestors=None, names=None):
        self._contiguous = contiguous
        self._is_red = is_red
        self.ancestors = OrderedSet(ancestors or [])
        self._names = OrderedSet(names or [])
    def is_reduction(self):
        return self._is_red
    def get_operation_names(self):
        return self._names

class MixOrderReduction:
    @classmethod
    def is_contiguous_node(cls, node):
        return getattr(node, "_contiguous", False)

class FusedMixOrderReductions:
    pass

class MockScheduler:
    def can_fuse(self, n1, n2, allow_mix_order_reduction=False):
        return True
    def score_fusion_memory(self, n1, n2, count_bytes=False):
        return 999999

class MockSelf:
    def __init__(self):
        self.scheduler = MockScheduler()
        self.numel = 100

ns = {
    "MixOrderReduction": MixOrderReduction,
    "FusedMixOrderReductions": FusedMixOrderReductions,
    "OrderedSet": OrderedSet,
    "typing": typing,
    "__builtins__": __builtins__,
}
try:
    exec(func_src, ns)
except Exception as e:
    print(f"FAIL: could not compile: {e}")
    sys.exit(1)

func = ns["sub_node_can_fuse"]
mock_self = MockSelf()

# Non-contiguous node1 + contiguous node2 → should still allow fusion
node1 = MockNode(contiguous=False)
node2 = MockNode(contiguous=True)
result = func(mock_self, node1, node2, ())

if result is not False and result:
    print("PASS: non-contiguous + contiguous fusion allowed")
else:
    print(f"FAIL: non-contiguous + contiguous should allow fusion, got {result!r}")
    sys.exit(1)
PYEOF

if python3 /tmp/test_p2p_noncontig_contig.py "$SCHEDULER"; then
    add_score 0.10
else
    echo "FAIL: P2P non-contiguous+contiguous test"
fi

###############################################################################
# PASS-TO-PASS STRUCTURAL (0.05)
###############################################################################

# [pr_diff] (0.05): FusedMixOrderReductions.__init__ still enforces contiguity invariant
cat > /tmp/test_init_invariant.py << 'PYEOF'
import ast, sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                for sub in ast.walk(item):
                    if isinstance(sub, ast.Assert) and "is_contiguous_node" in ast.dump(sub):
                        print("PASS: __init__ contiguity assertion preserved")
                        sys.exit(0)

print("FAIL: __init__ contiguity assertion missing")
sys.exit(1)
PYEOF

if python3 /tmp/test_init_invariant.py "$SCHEDULER"; then
    add_score 0.05
else
    echo "FAIL: init invariant broken"
fi

###############################################################################
# ANTI-STUB (0.10)
###############################################################################

# [pr_diff] (0.05): sub_node_can_fuse has non-trivial body (>= 5 statements)
cat > /tmp/test_antistub.py << 'PYEOF'
import ast, sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                if len(item.body) >= 5:
                    print(f"PASS: sub_node_can_fuse has {len(item.body)} top-level statements")
                    sys.exit(0)
                else:
                    print(f"FAIL: sub_node_can_fuse appears stubbed ({len(item.body)} stmts)")
                    sys.exit(1)

print("FAIL: sub_node_can_fuse not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_antistub.py "$SCHEDULER"; then
    add_score 0.05
else
    echo "FAIL: method stubbed or missing"
fi

# [pr_diff] (0.05): fuse_with method still exists in FusedMixOrderReductions
cat > /tmp/test_fuse_with.py << 'PYEOF'
import ast, sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        methods = [i.name for i in node.body if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if "fuse_with" in methods:
            print("PASS: fuse_with method preserved")
            sys.exit(0)

print("FAIL: fuse_with method missing")
sys.exit(1)
PYEOF

if python3 /tmp/test_fuse_with.py "$SCHEDULER"; then
    add_score 0.05
else
    echo "FAIL: fuse_with missing"
fi

###############################################################################
# CONFIG-DERIVED (0.10)
###############################################################################

# [agent_config] (0.05): "Minimize comments; be concise" — CLAUDE.md:48 @ 63fcbe1040
cat > /tmp/test_concise.py << 'PYEOF'
import ast, sys, re

with open(sys.argv[1]) as f:
    all_lines = f.readlines()
    f.seek(0)
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                method_lines = all_lines[item.lineno - 1 : item.end_lineno]
                comments = sum(1 for l in method_lines if re.match(r'^\s*#', l))
                code = sum(1 for l in method_lines if l.strip() and not re.match(r'^\s*#', l))
                if code > 0 and comments <= code:
                    print(f"PASS: concise ({comments} comments / {code} code)")
                    sys.exit(0)
                else:
                    print(f"FAIL: too many comments ({comments}/{code})")
                    sys.exit(1)

print("FAIL: method not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_concise.py "$SCHEDULER"; then
    add_score 0.05
else
    echo "FAIL: comments not concise"
fi

# [agent_config] (0.05): "Match existing code style" — CLAUDE.md:57 @ 63fcbe1040
# Existing rejection pattern uses `return False`. New guard should follow suit.
cat > /tmp/test_style.py << 'PYEOF'
import ast, sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                count = 0
                for sub in ast.walk(item):
                    if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Constant):
                        if sub.value.value is False:
                            count += 1
                if count >= 2:
                    print(f"PASS: uses return False pattern ({count} instances)")
                    sys.exit(0)
                else:
                    print(f"FAIL: expected >= 2 return False, found {count}")
                    sys.exit(1)

print("FAIL: method not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_style.py "$SCHEDULER"; then
    add_score 0.05
else
    echo "FAIL: style mismatch"
fi

###############################################################################
# FINAL SCORE
###############################################################################
echo ""
echo "=== FINAL SCORE: $REWARD ==="
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
r = float('$REWARD')
# Decompose: F2P behavioral = 0.50, P2P behavioral = 0.25, P2P structural = 0.05,
# anti-stub = 0.10, config = 0.10
behavioral = min(0.50, r)
remainder = max(0.0, r - 0.50)
p2p_beh = min(0.25, remainder)
remainder2 = max(0.0, remainder - 0.25)
json.dump({
    'reward': r,
    'behavioral': min(0.75, behavioral + p2p_beh),
    'regression': min(0.05, remainder2),
    'config': max(0.0, r - 0.90) if r > 0.90 else 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
