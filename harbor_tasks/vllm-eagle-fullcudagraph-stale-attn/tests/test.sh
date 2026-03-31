#!/usr/bin/env bash
set +e

FILE="/repo/vllm/v1/worker/gpu/spec_decode/eagle/speculator.py"
TOTAL=0
EARNED=0

add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }
earn() { EARNED=$(python3 -c "print(round($EARNED + $1, 4))"); }

# ──────────────────────────────────────────────────────────────
# GATE (0.00): Syntax check — abort on failure
# [pr_diff] (0.00): File must be valid Python
# ──────────────────────────────────────────────────────────────
echo "=== GATE: Syntax check ==="
if ! python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────────────────────
# BEHAVIORAL (AST-based): Fail-to-pass tests
# Justified: GPU/CUDA code requiring model weights and CUDA graphs
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.40): The bug: CUDAGraphMode.FULL path has an early return
# that skips attention metadata building. ANY correct fix removes this
# pattern — i.e., there must be no `return` inside a FULL-mode check
# that precedes all attention-metadata-related calls.
echo "=== F2P: No early return in FULL cudagraph path before attn metadata ==="
add 0.40
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

# Find the propose method
propose = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "propose":
        propose = node
        break

if propose is None:
    print("FAIL: propose method not found")
    sys.exit(1)

# Collect ALL call sites that look like attention metadata building.
# Broad matching: any call whose name contains ("attn" or "attention")
# AND ("build" or "metadata" or "prepare" or "setup" or "update" or "create").
# This accepts: build_attn_metadata, _build_draft_attn_metadata,
# prepare_attention, setup_attn_metadata, create_attention_state, etc.
def is_attn_build_call(name):
    if name is None:
        return False
    nl = name.lower()
    has_attn = "attn" in nl or "attention" in nl
    has_action = any(w in nl for w in ("build", "metadata", "prepare", "setup", "update", "create"))
    return has_attn and has_action

attn_build_lines = set()
for node in ast.walk(propose):
    if isinstance(node, ast.Call):
        func = node.func
        name = None
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if is_attn_build_call(name):
            attn_build_lines.add(node.lineno)

# Also count inline build_attn_metadata or similar at top-level assignments
# in propose that reference "attn" + "metadata" in function calls
for node in ast.walk(propose):
    if isinstance(node, ast.Call):
        func = node.func
        # Direct name call like build_attn_metadata(...)
        if isinstance(func, ast.Name) and is_attn_build_call(func.id):
            attn_build_lines.add(node.lineno)
        # Method call like self.attn_builder.build(...)
        if isinstance(func, ast.Attribute):
            # Walk the chain for attn-related names
            chain_parts = []
            n = func
            while isinstance(n, ast.Attribute):
                chain_parts.append(n.attr)
                n = n.value
            if isinstance(n, ast.Name):
                chain_parts.append(n.id)
            chain_str = ".".join(reversed(chain_parts)).lower()
            if ("attn" in chain_str or "attention" in chain_str) and \
               any(w in chain_str for w in ("build", "metadata", "prepare", "setup")):
                attn_build_lines.add(node.lineno)

earliest_attn_build = min(attn_build_lines) if attn_build_lines else float('inf')

# The BUG PATTERN: an if-block checking CUDAGraphMode.FULL (or cg_mode)
# that contains a return statement BEFORE any attn metadata building.
has_early_return = False
for node in ast.walk(propose):
    if isinstance(node, ast.If) and node.lineno < earliest_attn_build:
        # Check if the condition references FULL and cg_mode
        test_src = ast.get_source_segment(src, node.test) or ""
        if "FULL" in test_src and ("cg_mode" in test_src or "cudagraph" in test_src.lower()):
            # Check for return in this if-block body (not nested ifs)
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.lineno < earliest_attn_build:
                    has_early_return = True

if has_early_return:
    print("FAIL: FULL cudagraph check returns before attention metadata is built (BUG PRESENT)")
    sys.exit(1)

if not attn_build_lines:
    print("FAIL: no call to build/prepare attention metadata found in propose()")
    sys.exit(1)

print("PASS: No early return before attention metadata building")
PYCHECK
if [ $? -eq 0 ]; then earn 0.40; fi

# [pr_diff] (0.25): Attention metadata must be built for ALL cudagraph modes.
# The FULL path must also have attn metadata built before it executes.
# Accepts: (a) attn build before run_fullgraph, (b) no run_fullgraph at all
# (restructured to go through generate_draft), (c) fullgraph called AFTER
# attn build in a restructured control flow.
echo "=== F2P: Attention metadata built before any fullgraph execution ==="
add 0.25
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

propose = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "propose":
        propose = node
        break

if propose is None:
    print("FAIL: propose method not found")
    sys.exit(1)

# Broad matching for attn build calls (same as above)
def is_attn_build_call(name):
    if name is None:
        return False
    nl = name.lower()
    has_attn = "attn" in nl or "attention" in nl
    has_action = any(w in nl for w in ("build", "metadata", "prepare", "setup", "update", "create"))
    return has_attn and has_action

def get_call_name(node):
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None

fullgraph_lines = []
attn_build_lines = []

for node in ast.walk(propose):
    if isinstance(node, ast.Call):
        name = get_call_name(node)
        if name and "fullgraph" in name.lower():
            fullgraph_lines.append(node.lineno)
        if is_attn_build_call(name):
            attn_build_lines.append(node.lineno)

if not fullgraph_lines:
    # Restructured to not call fullgraph directly — acceptable
    # as long as attn metadata is built somewhere
    if attn_build_lines:
        print("PASS: fullgraph not called directly; attn metadata is built")
        sys.exit(0)
    else:
        # Could also be fully restructured with different naming
        # Accept if propose has >20 statements (not a stub)
        stmts = len(propose.body)
        if stmts > 20:
            print("PASS: fully restructured propose() with substantial logic")
            sys.exit(0)
        print("FAIL: no attn metadata build and no fullgraph — likely incomplete")
        sys.exit(1)

earliest_fullgraph = min(fullgraph_lines)

# At least one attn build must come before fullgraph
if any(l < earliest_fullgraph for l in attn_build_lines):
    print("PASS: attention metadata built before fullgraph execution")
    sys.exit(0)

# Check if a helper method is called before fullgraph that contains attn/build
for node in ast.walk(propose):
    if isinstance(node, ast.Call) and node.lineno < earliest_fullgraph:
        name = get_call_name(node)
        if name and is_attn_build_call(name):
            print("PASS: attn metadata helper called before fullgraph")
            sys.exit(0)

print("FAIL: attention metadata not built before fullgraph execution")
sys.exit(1)
PYCHECK
if [ $? -eq 0 ]; then earn 0.25; fi

# ──────────────────────────────────────────────────────────────
# PASS-TO-PASS (0.10): Existing structure must not break
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.10): Core class and method structure
echo "=== P2P: Core methods and class structure ==="
add 0.10
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

eagle_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EagleSpeculator":
        eagle_class = node
        break

if eagle_class is None:
    print("FAIL: EagleSpeculator class not found")
    sys.exit(1)

methods = {n.name for n in ast.walk(eagle_class) if isinstance(n, ast.FunctionDef)}
# Only check methods that existed BEFORE the fix (not new ones added by fix)
required = {"propose", "generate_draft", "capture_model", "run_model", "load_model", "set_attn"}
missing = required - methods
if missing:
    print(f"FAIL: missing methods: {missing}")
    sys.exit(1)

print("PASS: all required methods present")
PYCHECK
if [ $? -eq 0 ]; then earn 0.10; fi

# ──────────────────────────────────────────────────────────────
# STRUCTURAL (0.15): Anti-stub / anti-trivial checks
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.10): propose() must not be a stub — should have substantial
# logic including conditionals and function calls
echo "=== STRUCTURAL: propose() is not a stub ==="
add 0.10
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "propose":
        body_stmts = len(node.body)
        if body_stmts < 10:
            print(f"FAIL: propose() has only {body_stmts} statements — likely stubbed")
            sys.exit(1)
        # Must have at least some conditionals (if statements)
        ifs = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
        if ifs < 2:
            print(f"FAIL: propose() has only {ifs} if-statements — likely stubbed")
            sys.exit(1)
        # Must have function/method calls
        calls = sum(1 for n in ast.walk(node) if isinstance(n, ast.Call))
        if calls < 5:
            print(f"FAIL: propose() has only {calls} calls — likely stubbed")
            sys.exit(1)
        print(f"PASS: propose() has {body_stmts} stmts, {ifs} ifs, {calls} calls")
        sys.exit(0)

print("FAIL: propose not found")
sys.exit(1)
PYCHECK
if [ $? -eq 0 ]; then earn 0.10; fi

# [pr_diff] (0.05): propose() must reference CUDAGraphMode (needed for dispatch logic)
echo "=== STRUCTURAL: CUDAGraphMode referenced in propose ==="
add 0.05
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

# Check that CUDAGraphMode is imported or referenced
has_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if "CUDAGraphMode" in alias.name:
                has_import = True
    # Also accept attribute access like cudagraph_utils.CUDAGraphMode
    if isinstance(node, ast.Attribute) and node.attr == "CUDAGraphMode":
        has_import = True
    if isinstance(node, ast.Name) and node.id == "CUDAGraphMode":
        has_import = True

if not has_import:
    print("FAIL: CUDAGraphMode not referenced anywhere in file")
    sys.exit(1)

print("PASS: CUDAGraphMode referenced")
PYCHECK
if [ $? -eq 0 ]; then earn 0.05; fi

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10): Rules from AGENTS.md
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): "Never use system python3 or bare pip" — AGENTS.md:51
echo "=== CONFIG: No bare pip in changed file ==="
add 0.05
if ! grep -qE '^\s*(import\s+)?pip\s+install' "$FILE" 2>/dev/null; then
    echo "PASS: no bare pip usage"
    earn 0.05
else
    echo "FAIL: bare pip usage found"
fi

# [agent_config] (0.05): Valid Python with no syntax errors — AGENTS.md:80-84
echo "=== CONFIG: No wildcard imports ==="
add 0.05
python3 - "$FILE" <<'PYCHECK'
import ast, sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "*":
                print(f"FAIL: wildcard import from {node.module}")
                sys.exit(1)

print("PASS: no wildcard imports")
PYCHECK
if [ $? -eq 0 ]; then earn 0.05; fi

# ──────────────────────────────────────────────────────────────
# TOTAL
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== SCORING ==="
echo "Earned: $EARNED / $TOTAL"
REWARD=$(python3 -c "print(round($EARNED / $TOTAL, 4) if $TOTAL > 0 else 0)")
echo "Reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json <<ENDJSON
{"reward": $REWARD, "earned": $EARNED, "total": $TOTAL}
ENDJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
