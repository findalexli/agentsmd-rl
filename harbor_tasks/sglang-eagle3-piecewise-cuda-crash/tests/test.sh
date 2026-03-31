#!/usr/bin/env bash
# Verifier for sglang-eagle3-piecewise-cuda-crash
# Task: fix AttributeError in init_piecewise_cuda_graphs() when draft model
#        (e.g. eagle3) lacks a 'layers' attribute on language_model.model
# File: python/sglang/srt/model_executor/model_runner.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/sglang/python/sglang/srt/model_executor/model_runner.py"

echo "=== sglang eagle3 piecewise cuda crash verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights — total = 1.0
W_F2P_NO_CRASH=0.35          # fail-to-pass: no AttributeError on missing layers
W_F2P_NO_SIDE_EFFECTS=0.15   # fail-to-pass: no layer-related side effects on layerless model
W_P2P_WITH_LAYERS=0.20       # pass-to-pass: models WITH layers still get their layers extracted
W_ANTISTUB=0.10              # anti-stub: function body is substantive, not gutted
W_STRUCTURAL_GUARD=0.10      # structural: guard exists in function (AST)
W_CONFIG=0.10                # config-derived: new test files have main guard

SCORE="0.0"

# ── Shared helper: extract init_piecewise_cuda_graphs function ───────────
EXTRACT_FUNC='
import ast, sys, textwrap, types

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break

if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))
'

# ── TEST 1 (PRIMARY F2P): model without 'layers' must NOT raise AttributeError ──
# [pr_diff] (0.35): Draft model without layers doesn't crash init_piecewise_cuda_graphs
echo ""
echo "TEST 1: F2P — model without 'layers' does not crash (weight=$W_F2P_NO_CRASH)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap, types

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break
if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# Mock model WITHOUT 'layers' (simulates eagle3 draft model)
class NoLayersInner:
    pass

class MockModelNoLayers:
    def __init__(self):
        self.model = NoLayersInner()

class MockServerArgs:
    piecewise_cuda_graph_tokens = [128, 256]

class MockLogger:
    def error(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

resolve_called = []

mock_self = types.SimpleNamespace(
    model=MockModelNoLayers(),
    server_args=MockServerArgs(),
    attention_layers=[],
    moe_layers=[],
    moe_fusions=[],
)

def mock_resolve(m):
    resolve_called.append(True)
    return m.model

exec_globals = {
    "resolve_language_model": mock_resolve,
    "logger": MockLogger(),
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

try:
    exec_globals["init_piecewise_cuda_graphs"](mock_self)
except AttributeError as e:
    if "layers" in str(e):
        print(f"FAIL: AttributeError on 'layers': {e}")
        sys.exit(1)
    else:
        print(f"FAIL: unexpected AttributeError: {e}")
        sys.exit(1)
except Exception as e:
    pass  # Other errors acceptable — key is no AttributeError on 'layers'

if not resolve_called:
    print("FAIL: resolve_language_model was never called — function is likely stubbed")
    sys.exit(1)

print("PASS: no crash when model lacks 'layers' attribute")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_NO_CRASH)")
fi

# ── TEST 2 (F2P): no layer-related side effects on layerless model ──────
# [pr_diff] (0.15): Function does not produce spurious layer lists for layerless model
# Accepts ANY fix approach: hasattr+return, try/except, getattr default, etc.
# Checks that attention_layers does NOT contain real layer objects (it shouldn't
# since there are no layers to iterate).
echo ""
echo "TEST 2: F2P — no spurious layer extraction on layerless model (weight=$W_F2P_NO_SIDE_EFFECTS)"
T2=$(python3 << 'PYEOF'
import ast, sys, textwrap, types

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break
if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

class NoLayersInner:
    pass

class MockModelNoLayers:
    def __init__(self):
        self.model = NoLayersInner()

class MockServerArgs:
    piecewise_cuda_graph_tokens = [128, 256]

class MockLogger:
    messages = []
    def error(self, *a, **kw): MockLogger.messages.append(("error", a))
    def info(self, *a, **kw): MockLogger.messages.append(("info", a))
    def warning(self, *a, **kw): MockLogger.messages.append(("warning", a))
    def debug(self, *a, **kw): MockLogger.messages.append(("debug", a))

# Track whether resolve_language_model was called (stubs won't call it)
resolve_called = []

SENTINEL = object()
mock_self = types.SimpleNamespace(
    model=MockModelNoLayers(),
    server_args=MockServerArgs(),
    attention_layers=SENTINEL,
    moe_layers=SENTINEL,
    moe_fusions=SENTINEL,
)

def mock_resolve(m):
    resolve_called.append(True)
    return m.model

exec_globals = {
    "resolve_language_model": mock_resolve,
    "logger": MockLogger(),
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

try:
    exec_globals["init_piecewise_cuda_graphs"](mock_self)
except AttributeError:
    print("FAIL: crashed with AttributeError")
    sys.exit(1)
except Exception:
    pass  # Other errors OK

# Anti-stub: resolve_language_model must have been called
if not resolve_called:
    print("FAIL: resolve_language_model was never called — function is likely stubbed")
    sys.exit(1)

# The function should NOT have extracted real attention layers from a layerless model.
# Valid outcomes:
#   - attention_layers is still SENTINEL (early return before assignment)
#   - attention_layers is [] or None (initialized but nothing to iterate)
# Invalid:
#   - attention_layers contains actual layer objects (shouldn't be possible)
attn = mock_self.attention_layers
if attn is SENTINEL:
    print("PASS: function returned early after resolving model, no layer extraction attempted")
    sys.exit(0)
elif attn is None:
    print("PASS: attention_layers set to None (no layers found)")
    sys.exit(0)
elif isinstance(attn, list) and len(attn) == 0:
    print("PASS: attention_layers is empty list (no layers to extract)")
    sys.exit(0)
elif isinstance(attn, list) and len(attn) > 0:
    print(f"FAIL: attention_layers has {len(attn)} entries but model has no layers")
    sys.exit(1)
else:
    print(f"PASS: attention_layers={attn!r} — no spurious layers extracted")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_NO_SIDE_EFFECTS)")
fi

# ── TEST 3 (P2P): model WITH layers still gets layers extracted properly ─
# [pr_diff] (0.20): Models with standard layers attribute still work correctly
echo ""
echo "TEST 3: P2P — model with 'layers' gets attention layers extracted (weight=$W_P2P_WITH_LAYERS)"
T3=$(python3 << 'PYEOF'
import ast, sys, textwrap, types

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break
if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# Mock model WITH standard layers (should still work after fix)
class FakeAttn:
    pass

class FakeLayer:
    def __init__(self):
        self.self_attn = types.SimpleNamespace(attn=FakeAttn())

class WithLayersInner:
    def __init__(self):
        self.layers = [FakeLayer(), FakeLayer(), FakeLayer()]

class MockModelWithLayers:
    def __init__(self):
        self.model = WithLayersInner()

class MockServerArgs:
    piecewise_cuda_graph_tokens = [128, 256]

class MockLogger:
    def error(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

mock_self = types.SimpleNamespace(
    model=MockModelWithLayers(),
    server_args=MockServerArgs(),
    attention_layers=None,
    moe_layers=None,
    moe_fusions=None,
)

exec_globals = {
    "resolve_language_model": lambda m: m.model,
    "logger": MockLogger(),
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

try:
    exec_globals["init_piecewise_cuda_graphs"](mock_self)
except Exception:
    pass  # May fail on later CUDA parts; we check layer extraction

attn = mock_self.attention_layers
if attn is None:
    print("FAIL: model with layers did not proceed to layer extraction (attention_layers is None)")
    sys.exit(1)
elif isinstance(attn, list) and len(attn) == 3:
    print(f"PASS: all 3 attention layers extracted correctly")
    sys.exit(0)
elif isinstance(attn, list) and len(attn) > 0:
    print(f"PASS: {len(attn)} attention layers extracted (model has 3 layers)")
    sys.exit(0)
elif isinstance(attn, list) and len(attn) == 0:
    # Could mean iteration happened but layer structure not matched — still OK
    # as long as the function didn't bail out early
    print(f"PASS: layer iteration happened (attention_layers initialized to empty)")
    sys.exit(0)
else:
    print(f"FAIL: unexpected attention_layers value: {attn!r}")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_WITH_LAYERS)")
fi

# ── TEST 4: anti-stub — function body is substantive ────────────────────
# [pr_diff] (0.10): File is not stubbed out; function has real logic
echo ""
echo "TEST 4: anti-stub — function is substantive, not gutted (weight=$W_ANTISTUB)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()

# File-level anti-stub
required_symbols = ["init_piecewise_cuda_graphs", "resolve_language_model",
                    "language_model", "attention_layers", "moe_layers",
                    "piecewise_cuda_graph_tokens", "ModelRunner"]
missing = [r for r in required_symbols if r not in source]
if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

# Function-level anti-stub: init_piecewise_cuda_graphs must have meaningful body
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break

if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)

# Count non-docstring, non-pass statements
meaningful = 0
for child in ast.walk(func_node):
    if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                          ast.For, ast.While, ast.If, ast.With,
                          ast.Try, ast.Return, ast.Call)):
        meaningful += 1

if meaningful < 5:
    print(f"FAIL: init_piecewise_cuda_graphs has only {meaningful} meaningful statements — looks stubbed")
    sys.exit(1)

print(f"PASS: file has {line_count} lines, function has {meaningful} meaningful statements")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── TEST 5: structural — guard for missing layers in function ────────────
# [pr_diff] (0.10): Function guards against missing layers attribute
# WHY AST: Complements behavioral tests — verifies defensive pattern exists.
# Accepts: hasattr, getattr-with-default, try/except AttributeError, or any
# conditional that references 'layers' before the iteration loop.
echo ""
echo "TEST 5: structural — function has guard for missing 'layers' (weight=$W_STRUCTURAL_GUARD)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/model_executor/model_runner.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
        func_node = node
        break

if func_node is None:
    print("FAIL: init_piecewise_cuda_graphs not found")
    sys.exit(1)

func_text = "\n".join(source.splitlines()[func_node.lineno - 1:func_node.end_lineno])

has_guard = False

# 1. hasattr(..., "layers") or hasattr(..., 'layers')
if "hasattr" in func_text and "layers" in func_text:
    has_guard = True

# 2. getattr(..., "layers", <default>) — any default
if "getattr" in func_text and "layers" in func_text:
    # Check it's a 3-arg getattr (has a default)
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 3:
                # Check one arg references 'layers'
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "layers":
                        has_guard = True

# 3. try/except AttributeError around layers access
for node in ast.walk(func_node):
    if isinstance(node, ast.Try):
        try_text = "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])
        if "layers" in try_text:
            for handler in node.handlers:
                if handler.type is None:
                    has_guard = True
                elif isinstance(handler.type, ast.Name) and handler.type.id == "AttributeError":
                    has_guard = True
                elif isinstance(handler.type, ast.Tuple):
                    for elt in handler.type.elts:
                        if isinstance(elt, ast.Name) and elt.id == "AttributeError":
                            has_guard = True

# 4. isinstance check or type check referencing layers
if "isinstance" in func_text and "layers" in func_text:
    has_guard = True

if has_guard:
    print("PASS: function has guard for missing 'layers' attribute")
    sys.exit(0)
else:
    print("FAIL: no guard found for missing 'layers' attribute")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_GUARD)")
fi

# ── TEST 6: Config-derived — new test files have main guard ──────────────
# [agent_config] (0.10): "Has `if __name__ == '__main__': unittest.main()`" — .claude/skills/write-sglang-test/SKILL.md @ aa9177152ec7
echo ""
echo "TEST 6: config-derived — new test files have main guard (weight=$W_CONFIG)"
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
T6="PASS"
if [ -z "$NEW_TEST_FILES" ]; then
    echo "PASS (no new test files added)"
else
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "FAIL: $tf missing main guard"
            T6="FAIL"
        fi
    done
    echo "$T6"
fi
if [ "$T6" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
