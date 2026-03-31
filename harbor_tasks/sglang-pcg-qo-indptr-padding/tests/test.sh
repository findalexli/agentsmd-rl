#!/usr/bin/env bash
# Verifier for sglang-pcg-qo-indptr-padding
# Task: fix piecewise CUDA graph replay crash where qo_indptr[-1] != static_num_tokens
# Files: piecewise_context_manager.py, flashinfer_backend.py, piecewise_cuda_graph_runner.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

CTX_MGR="/workspace/sglang/python/sglang/srt/compilation/piecewise_context_manager.py"
FLASH_BE="/workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py"
PCG_RUN="/workspace/sglang/python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py"

echo "=== sglang pcg qo_indptr padding verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
ALL_OK=true
for F in "$CTX_MGR" "$FLASH_BE" "$PCG_RUN"; do
    python3 << PYEOF
import ast, sys
try:
    with open("$F") as f:
        ast.parse(f.read())
    print(f"  OK: {'/'.join('$F'.split('/')[-2:])}")
except SyntaxError as e:
    print(f"  FAIL: {e}")
    sys.exit(1)
PYEOF
    if [ $? -ne 0 ]; then
        ALL_OK=false
    fi
done
if [ "$ALL_OK" != "true" ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_F2P=0.40    # [pr_diff] (0.40): fail-to-pass — num_tokens propagation through ForwardContext
W_P2P=0.20    # [pr_diff] (0.20): pass-to-pass — existing context manager API still works
W_AST2=0.10   # [pr_diff] (0.10): call_begin_forward PCG padding (AST: needs flashinfer GPU)
W_AST3=0.10   # [pr_diff] (0.10): replay num_tokens + init_forward_metadata ordering (AST: needs CUDA graphs)
W_AST4=0.05   # [pr_diff] (0.05): page_size stored in backend classes (AST: needs flashinfer GPU)
W_ANTI=0.10   # [pr_diff] (0.10): anti-stub — files not hollowed out
W_IMP=0.05    # [pr_diff] (0.05): get_forward_context imported in flashinfer_backend

SCORE="0.0"

# ── Helper: load piecewise_context_manager.py with mocked torch ──────────
# torch is not installed in this CPU-only image, but the module only uses it
# for type hints (torch.cuda.Stream). We mock it to enable real execution.
MOCK_LOADER='
import sys, types

mock_torch = types.ModuleType("torch")
mock_cuda = types.ModuleType("torch.cuda")
class _MockStream: pass
mock_cuda.Stream = _MockStream
mock_torch.cuda = mock_cuda
sys.modules["torch"] = mock_torch
sys.modules["torch.cuda"] = mock_cuda

for pkg in ["sglang", "sglang.srt", "sglang.srt.compilation", "sglang.srt.model_executor"]:
    m = types.ModuleType(pkg)
    m.__path__ = ["/workspace/sglang/python/" + pkg.replace(".", "/")]
    sys.modules[pkg] = m

import importlib.util
spec = importlib.util.spec_from_file_location(
    "sglang.srt.compilation.piecewise_context_manager",
    "/workspace/sglang/python/sglang/srt/compilation/piecewise_context_manager.py",
)
_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = _mod
spec.loader.exec_module(_mod)
'

# ── TEST 1 (BEHAVIORAL F2P): num_tokens propagation through ForwardContext ──
# [pr_diff] (0.40): ForwardContext carries num_tokens; set_forward_context propagates it.
# The buggy code lacks num_tokens support entirely, so this FAILS on the pre-fix commit
# (TypeError from unexpected keyword, or missing attribute).
echo ""
echo "TEST 1: behavioral F2P — num_tokens propagation (weight=$W_F2P)"
T1=$(python3 << PYEOF
${MOCK_LOADER}

import sys

ForwardContext = getattr(_mod, "ForwardContext", None)
set_forward_context = getattr(_mod, "set_forward_context", None)
get_forward_context = getattr(_mod, "get_forward_context", None)

if not all([ForwardContext, set_forward_context, get_forward_context]):
    print("FAIL: missing ForwardContext / set_forward_context / get_forward_context")
    sys.exit(1)

# A) ForwardContext instances must have a num_tokens attribute
fc = ForwardContext()
if not hasattr(fc, "num_tokens"):
    print("FAIL: ForwardContext() has no num_tokens attribute")
    sys.exit(1)

# B) set_forward_context must accept num_tokens keyword
import inspect
sig = inspect.signature(set_forward_context)
if "num_tokens" not in sig.parameters:
    print("FAIL: set_forward_context does not accept num_tokens parameter")
    sys.exit(1)

# C) num_tokens=42 propagates through the context
try:
    with set_forward_context(None, None, None, [], [], num_tokens=42):
        fwd = get_forward_context()
        if fwd is None:
            print("FAIL: get_forward_context() returned None inside context")
            sys.exit(1)
        actual = getattr(fwd, "num_tokens", "MISSING")
        if actual != 42:
            print(f"FAIL: expected num_tokens=42, got {actual}")
            sys.exit(1)
except TypeError as e:
    # Buggy code: set_forward_context rejects the num_tokens keyword
    print(f"FAIL: set_forward_context rejects num_tokens keyword: {e}")
    sys.exit(1)

# D) Different value propagates (not hardcoded)
try:
    with set_forward_context(None, None, None, [], [], num_tokens=256):
        fwd2 = get_forward_context()
        actual2 = getattr(fwd2, "num_tokens", "MISSING")
        if actual2 != 256:
            print(f"FAIL: expected num_tokens=256, got {actual2}")
            sys.exit(1)
except TypeError as e:
    print(f"FAIL: set_forward_context rejects num_tokens=256: {e}")
    sys.exit(1)

# E) num_tokens=None (default) also works
try:
    with set_forward_context(None, None, None, [], []):
        fwd3 = get_forward_context()
        val = getattr(fwd3, "num_tokens", "MISSING")
        if val != None:
            print(f"FAIL: default num_tokens should be None, got {val}")
            sys.exit(1)
except Exception as e:
    print(f"FAIL: set_forward_context without num_tokens raised: {e}")
    sys.exit(1)

print("PASS: num_tokens propagates through ForwardContext correctly")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P)")
fi

# ── TEST 2 (BEHAVIORAL P2P): existing context manager API still works ──
# [pr_diff] (0.20): Original ForwardContext attributes and context manager preserved.
# This passes on both buggy and fixed code — regression guard.
echo ""
echo "TEST 2: behavioral P2P — existing context manager API (weight=$W_P2P)"
T2=$(python3 << PYEOF
${MOCK_LOADER}

import sys
errors = []

# A) Required exports exist
for name in ["set_forward_context", "get_forward_context",
             "is_in_piecewise_cuda_graph", "enable_piecewise_cuda_graph"]:
    if getattr(_mod, name, None) is None:
        errors.append(f"missing export: {name}")

FC = getattr(_mod, "ForwardContext", None)
if FC is None:
    errors.append("missing ForwardContext class")
else:
    # B) ForwardContext retains original attributes
    fc = FC()
    for attr in ["forward_batch", "quant_config", "moe_layers", "moe_fusions"]:
        if not hasattr(fc, attr):
            errors.append(f"ForwardContext missing attr: {attr}")

# C) get_forward_context returns None outside any context
gfc = getattr(_mod, "get_forward_context", None)
if gfc:
    outside = gfc()
    if outside is not None:
        errors.append(f"get_forward_context outside context should be None, got {type(outside)}")

# D) Context manager round-trip works (without num_tokens, backwards compat)
sfc = getattr(_mod, "set_forward_context", None)
if sfc and gfc:
    try:
        with sfc(None, None, None, [], []):
            inside = gfc()
            if inside is None:
                errors.append("get_forward_context returned None inside context")
            elif not hasattr(inside, "forward_batch"):
                errors.append("context object missing forward_batch inside context")
        after = gfc()
        if after is not None:
            errors.append("forward context not cleared after exiting")
    except Exception as e:
        errors.append(f"context manager round-trip failed: {e}")

if errors:
    print(f"FAIL: {'; '.join(errors)}")
    sys.exit(1)

print("PASS: existing context manager API works correctly")
sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P)")
fi

# ── TEST 3 (STRUCTURAL): call_begin_forward PCG padding logic ──
# [pr_diff] (0.10): call_begin_forward extends qo_indptr/kv_indptr for padding tokens
# WHY AST: flashinfer_backend.py imports flashinfer which requires GPU/CUDA.
# Checks are intentionally broad — no specific variable names from gold patch.
echo ""
echo "TEST 3: structural — call_begin_forward PCG padding (weight=$W_AST2)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find ALL call_begin_forward methods (there are multiple in different classes)
func_nodes = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "call_begin_forward":
        func_nodes.append(node)

if not func_nodes:
    print("FAIL: call_begin_forward not found")
    sys.exit(1)

# At least ONE call_begin_forward must have the PCG padding logic
found_padding = False
for func_node in func_nodes:
    func_src = "\n".join(source.splitlines()[func_node.lineno - 1:func_node.end_lineno])

    # 1. Calls get_forward_context() to learn the static token count
    if "get_forward_context" not in func_src:
        continue

    # 2. Extends qo_indptr and kv_indptr (via any concat/cat/append mechanism)
    concat_ops = ["torch.cat", ".cat(", "concat", "torch.concatenate", "append"]
    has_qo = "qo_indptr" in func_src and any(op in func_src for op in concat_ops)
    has_kv = "kv_indptr" in func_src and any(op in func_src for op in concat_ops)
    if not (has_qo and has_kv):
        continue

    # 3. References num_tokens (the static count from the forward context)
    if "num_tokens" not in func_src:
        continue

    # 4. Has conditional logic guarding the padding (only pad when needed)
    has_padding_guard = False
    for inner in ast.walk(func_node):
        if isinstance(inner, ast.If):
            if_src = "\n".join(source.splitlines()[inner.lineno - 1:inner.end_lineno])
            if any(kw in if_src for kw in ["num_tokens", "token", "pad", "pcg"]):
                has_padding_guard = True
                break

    if not has_padding_guard:
        continue

    # Anti-stub: function body must be substantial (not hollowed out)
    func_lines = func_node.end_lineno - func_node.lineno + 1
    if func_lines < 30:
        continue

    found_padding = True
    break

if not found_padding:
    print("FAIL: no call_begin_forward has PCG padding logic (get_forward_context + qo/kv_indptr extension + num_tokens + conditional guard)")
    sys.exit(1)

print("PASS: call_begin_forward has PCG padding logic")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_AST2)")
fi

# ── TEST 4 (STRUCTURAL): replay passes num_tokens inside context ──
# [pr_diff] (0.10): PiecewiseCudaGraphRunner.replay sends num_tokens via set_forward_context
# and calls init_forward_metadata INSIDE the context block (ordering fix).
# WHY AST: piecewise_cuda_graph_runner.py requires CUDA graph infrastructure.
echo ""
echo "TEST 4: structural — replay num_tokens + init ordering (weight=$W_AST3)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py") as f:
    source = f.read()

tree = ast.parse(source)

replay_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "replay":
        replay_func = node
        break

if replay_func is None:
    print("FAIL: replay method not found")
    sys.exit(1)

# 1. set_forward_context called with num_tokens keyword argument
found_kwarg = False
for node in ast.walk(replay_func):
    # Direct call or with-statement context expression
    calls = []
    if isinstance(node, ast.Call):
        calls.append(node)
    if isinstance(node, ast.withitem) and isinstance(node.context_expr, ast.Call):
        calls.append(node.context_expr)
    for call in calls:
        cname = ""
        if isinstance(call.func, ast.Name):
            cname = call.func.id
        elif isinstance(call.func, ast.Attribute):
            cname = call.func.attr
        if cname == "set_forward_context":
            kw_names = [kw.arg for kw in call.keywords]
            if "num_tokens" in kw_names:
                found_kwarg = True

if not found_kwarg:
    print("FAIL: replay does not pass num_tokens keyword to set_forward_context")
    sys.exit(1)

# 2. init_forward_metadata is called INSIDE the set_forward_context with-block
found_inside = False
for node in ast.walk(replay_func):
    if isinstance(node, ast.With):
        for item in node.items:
            ctx = item.context_expr
            if isinstance(ctx, ast.Call):
                cname = ""
                if isinstance(ctx.func, ast.Name):
                    cname = ctx.func.id
                elif isinstance(ctx.func, ast.Attribute):
                    cname = ctx.func.attr
                if cname == "set_forward_context":
                    with_src = "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])
                    if "init_forward_metadata" in with_src:
                        found_inside = True

if not found_inside:
    print("FAIL: init_forward_metadata not inside set_forward_context with-block")
    sys.exit(1)

print("PASS: replay passes num_tokens and calls init_forward_metadata inside context")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_AST3)")
fi

# ── TEST 5 (STRUCTURAL): page_size stored in backend classes ──
# [pr_diff] (0.05): FlashInferAttnBackend and metadata handler store page_size
# WHY AST: requires flashinfer GPU backend to import.
echo ""
echo "TEST 5: structural — page_size in backend classes (weight=$W_AST4)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

classes_with_page_size = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_src = "\n".join(source.splitlines()[item.lineno - 1:item.end_lineno])
                if "self.page_size" in init_src:
                    classes_with_page_size.append(node.name)

backend_found = any("Backend" in c or "Attn" in c for c in classes_with_page_size)
handler_found = any("Extend" in c or "Handler" in c or "Metadata" in c or "Updater" in c or "Prefill" in c for c in classes_with_page_size)

if not backend_found:
    print(f"FAIL: no backend class stores self.page_size (found: {classes_with_page_size})")
    sys.exit(1)
if not handler_found:
    print(f"FAIL: no handler class stores self.page_size (found: {classes_with_page_size})")
    sys.exit(1)

print(f"PASS: page_size stored in {classes_with_page_size}")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_AST4)")
fi

# ── TEST 6 (ANTI-STUB): files retain expected content ──
# [pr_diff] (0.10): Files not stubbed or hollowed out
echo ""
echo "TEST 6: anti-stub — files not hollowed (weight=$W_ANTI)"
T6=$(python3 << 'PYEOF'
import sys

checks = [
    ("/workspace/sglang/python/sglang/srt/compilation/piecewise_context_manager.py",
     50, ["ForwardContext", "set_forward_context", "get_forward_context", "_forward_context"]),
    ("/workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py",
     500, ["FlashInferAttnBackend", "call_begin_forward", "kv_indptr", "qo_indptr", "kv_indices"]),
    ("/workspace/sglang/python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py",
     200, ["PiecewiseCudaGraphRunner", "replay", "set_forward_context", "capture_num_tokens"]),
]

for path, min_lines, required_symbols in checks:
    with open(path) as f:
        content = f.read()
    lines = len(content.splitlines())
    if lines < min_lines:
        print(f"FAIL: {path.split('/')[-1]} has only {lines} lines (min {min_lines})")
        sys.exit(1)
    missing = [s for s in required_symbols if s not in content]
    if missing:
        print(f"FAIL: {path.split('/')[-1]} missing: {missing}")
        sys.exit(1)

print("PASS: all files retain expected content and size")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTI)")
fi

# ── TEST 7 (STRUCTURAL): get_forward_context imported in flashinfer_backend ──
# [pr_diff] (0.05): get_forward_context imported from piecewise_context_manager
echo ""
echo "TEST 7: structural — flashinfer_backend imports get_forward_context (weight=$W_IMP)"
T7=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

found = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module and "piecewise_context_manager" in node.module:
            imported_names = [alias.name for alias in node.names]
            if "get_forward_context" in imported_names:
                found = True
                break

if found:
    print("PASS: get_forward_context imported from piecewise_context_manager")
    sys.exit(0)
else:
    print("FAIL: get_forward_context not imported from piecewise_context_manager")
    sys.exit(1)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_IMP)")
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
