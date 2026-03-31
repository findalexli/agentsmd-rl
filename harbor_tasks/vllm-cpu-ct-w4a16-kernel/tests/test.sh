#!/usr/bin/env bash
set +e

TARGET="/repo/vllm/model_executor/kernels/linear/mixed_precision/cpu.py"
SCORE=0
TOTAL=0

log() { echo "  $1"; }
add() { SCORE=$(python3 -c "print(round($SCORE + $1, 2))"); TOTAL=$(python3 -c "print(round($TOTAL + $1, 2))"); }
skip() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 2))"); }

echo "=== CPUWNA16 CT W4A16 Support Tests ==="

# ── GATE: Syntax check ──────────────────────────────────────
# [pr_diff] (gate): File must be valid Python
echo ""
echo "--- GATE: Syntax check ---"
if python3 -c "
import ast, sys
try:
    ast.parse(open('$TARGET').read())
    sys.exit(0)
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"; then
    log "PASS: valid Python syntax"
else
    log "FAIL: syntax error — aborting"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── F2P 1: _process_gptq_weights does not hardcode layer attribute names ──
# [pr_diff] (0.30): Buggy code accesses layer.qweight, layer.scales, layer.qzeros,
# layer.g_idx directly. The fix must use generic accessors (any approach accepted:
# getattr, _get_weight_params, self.w_q_name, etc.)
# WHY AST: vllm requires compiled C++ custom ops (torch._custom_ops) not available in test env
echo ""
echo "--- F2P 1: No hardcoded attrs in _process_gptq_weights ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

HARDCODED_ATTRS = {'qweight', 'scales', 'qzeros', 'g_idx'}

for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef):
        continue
    for node in ast.walk(cls):
        if not (isinstance(node, ast.FunctionDef) and node.name == '_process_gptq_weights'):
            continue
        # Count AST Attribute nodes: layer.qweight, layer.scales, etc.
        hardcoded = []
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr in HARDCODED_ATTRS:
                # Direct access on 'layer' param (Name node)
                if isinstance(child.value, ast.Name) and child.value.id == 'layer':
                    hardcoded.append(child.attr)
        if len(hardcoded) == 0:
            print('PASS: no hardcoded layer.X attribute access')
            sys.exit(0)
        else:
            print(f'FAIL: {len(hardcoded)} hardcoded accesses: {hardcoded}')
            sys.exit(1)

print('FAIL: _process_gptq_weights method not found')
sys.exit(1)
"; then
    log "PASS (0.30)"
    add 0.30
else
    log "FAIL (0.00)"
    skip 0.30
fi

# ── F2P 2: process_weights_after_loading supports CT format ──
# [pr_diff] (0.25): Buggy code only handles GPTQ (no zero_points) and raises
# NotImplementedError for everything else. Fix must handle CT format
# (which HAS zero_points but is NOT AWQ). Test: the method must not have
# an unconditional NotImplementedError as sole non-GPTQ path.
# WHY AST: vllm requires compiled C++ custom ops not available in test env
echo ""
echo "--- F2P 2: CT format supported in process_weights_after_loading ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef):
        continue
    for node in ast.walk(cls):
        if not (isinstance(node, ast.FunctionDef) and node.name == 'process_weights_after_loading'):
            continue

        # Count distinct code paths (If branches) in the method body
        if_count = 0
        has_raise_not_impl = False
        call_count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                if_count += 1
            elif isinstance(child, ast.Raise):
                if child.exc is not None:
                    if isinstance(child.exc, ast.Call):
                        func = child.exc.func
                        if isinstance(func, ast.Name) and func.id == 'NotImplementedError':
                            has_raise_not_impl = True
                    elif isinstance(child.exc, ast.Name) and child.exc.id == 'NotImplementedError':
                        has_raise_not_impl = True
            elif isinstance(child, (ast.Call,)):
                call_count += 1

        # The buggy code has exactly 1 If (zero_points check) and the else
        # is just raise NotImplementedError. A fix needs more logic.
        # Accept any fix that: has >=2 If nodes (more dispatch paths)
        # OR has no unconditional NotImplementedError
        # OR has significantly more calls (processing CT weights)
        if if_count >= 2 or (not has_raise_not_impl) or call_count >= 6:
            print(f'PASS: method has {if_count} conditionals, {call_count} calls, raise_not_impl={has_raise_not_impl}')
            sys.exit(0)
        else:
            print(f'FAIL: only {if_count} conditional(s), {call_count} calls — CT format likely not handled')
            sys.exit(1)

print('FAIL: process_weights_after_loading not found')
sys.exit(1)
"; then
    log "PASS (0.25)"
    add 0.25
else
    log "FAIL (0.00)"
    skip 0.25
fi

# ── F2P 3: apply_weights does not hardcode layer attribute names ──
# [pr_diff] (0.15): Same bug as F2P 1, but in apply_weights. Buggy code passes
# layer.qweight, layer.scales, etc. directly to ops.cpu_gemm_wna16.
# WHY AST: apply_weights calls vllm._custom_ops.cpu_gemm_wna16, a C++ kernel
echo ""
echo "--- F2P 3: No hardcoded attrs in apply_weights ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

HARDCODED_ATTRS = {'qweight', 'scales', 'qzeros', 'g_idx'}

for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef):
        continue
    for node in ast.walk(cls):
        if not (isinstance(node, ast.FunctionDef) and node.name == 'apply_weights'):
            continue
        hardcoded = []
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr in HARDCODED_ATTRS:
                if isinstance(child.value, ast.Name) and child.value.id == 'layer':
                    hardcoded.append(child.attr)
        if len(hardcoded) == 0:
            print('PASS: no hardcoded layer.X attribute access')
            sys.exit(0)
        else:
            print(f'FAIL: {len(hardcoded)} hardcoded accesses: {hardcoded}')
            sys.exit(1)

print('FAIL: apply_weights method not found')
sys.exit(1)
"; then
    log "PASS (0.15)"
    add 0.15
else
    log "FAIL (0.00)"
    skip 0.15
fi

# ── Behavioral: Weight transposition for CT format ──
# [pr_diff] (0.10): CT format has different dimension ordering (input_dim=1 vs 0).
# The fix must include transposition logic (.t(), .transpose, .permute, or
# reshape-based) in weight processing methods. Check for Call nodes with
# transpose-related method names in _process_gptq_weights OR process_weights_after_loading.
# WHY AST: tensor operations require torch, not available in test env
echo ""
echo "--- Behavioral: Transpose handling for CT layout ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

TRANSPOSE_METHODS = {'t', 'transpose', 'permute', 'contiguous'}
WEIGHT_METHODS = {'_process_gptq_weights', 'process_weights_after_loading'}

found_transpose_in_processing = False
for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef):
        continue
    for node in ast.walk(cls):
        if not (isinstance(node, ast.FunctionDef) and node.name in WEIGHT_METHODS):
            continue
        # Look for method calls like tensor.t(), tensor.transpose(...)
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                if child.func.attr in TRANSPOSE_METHODS:
                    found_transpose_in_processing = True
                    break
        if found_transpose_in_processing:
            break
    if found_transpose_in_processing:
        break

if found_transpose_in_processing:
    print('PASS: transpose operations found in weight processing')
    sys.exit(0)
else:
    print('FAIL: no transpose operations in weight processing methods')
    sys.exit(1)
"; then
    log "PASS (0.10)"
    add 0.10
else
    log "FAIL (0.00)"
    skip 0.10
fi

# ── Regression: can_implement classmethod preserved ──
# [pr_diff] (0.10): can_implement must remain a classmethod with substantive
# validation logic (platform check, quant type check, size check).
# Check AST: is classmethod decorator, body has >=3 If nodes, >=3 Return nodes.
echo ""
echo "--- Regression: can_implement preserved ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef) or cls.name != 'CPUWNA16LinearKernel':
        continue
    for node in ast.walk(cls):
        if not (isinstance(node, ast.FunctionDef) and node.name == 'can_implement'):
            continue
        # Check it's a classmethod
        is_classmethod = any(
            (isinstance(d, ast.Name) and d.id == 'classmethod') or
            (isinstance(d, ast.Attribute) and d.attr == 'classmethod')
            for d in node.decorator_list
        )
        # Count If and Return nodes for substantive validation
        if_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
        return_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
        if is_classmethod and if_count >= 3 and return_count >= 3:
            print(f'PASS: classmethod with {if_count} checks, {return_count} returns')
            sys.exit(0)
        else:
            print(f'FAIL: classmethod={is_classmethod}, ifs={if_count}, returns={return_count}')
            sys.exit(1)

print('FAIL: CPUWNA16LinearKernel.can_implement not found')
sys.exit(1)
"; then
    log "PASS (0.10)"
    add 0.10
else
    log "FAIL (0.00)"
    skip 0.10
fi

# ── Anti-stub: substantive implementation ──
# [static] (0.10): Class must have required methods with non-trivial bodies
echo ""
echo "--- Anti-stub: substantive implementation ---"
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

REQUIRED = {'can_implement', 'process_weights_after_loading', 'apply_weights'}

for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef) or cls.name != 'CPUWNA16LinearKernel':
        continue
    methods = {}
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Count non-docstring, non-pass statements
            stmts = 0
            for child in ast.walk(node):
                if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                    ast.Return, ast.If, ast.For, ast.While, ast.Call,
                    ast.Expr, ast.Raise)):
                    stmts += 1
            methods[node.name] = stmts

    missing = REQUIRED - set(methods.keys())
    if missing:
        print(f'FAIL: missing methods: {missing}')
        sys.exit(1)

    # Each required method must have >3 meaningful statements (reject stubs)
    shallow = {m: c for m, c in methods.items() if m in REQUIRED and c < 4}
    if shallow:
        print(f'FAIL: stub methods (< 4 stmts): {shallow}')
        sys.exit(1)

    line_count = len(source.splitlines())
    if line_count < 60:
        print(f'FAIL: only {line_count} lines — likely a stub')
        sys.exit(1)

    print(f'PASS: {len(methods)} methods, all required have substantive bodies, {line_count} lines')
    sys.exit(0)

print('FAIL: CPUWNA16LinearKernel class not found')
sys.exit(1)
"; then
    log "PASS (0.10)"
    add 0.10
else
    log "FAIL (0.00)"
    skip 0.10
fi

# ── Summary ──
echo ""
echo "=== Score: $SCORE / 1.00 ==="

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
# F2P checks: 0.30 + 0.25 + 0.15 = 0.70 behavioral
# Transpose + can_implement + anti-stub = 0.30 structural
behavioral = min(score, 0.70)
remainder = max(0, score - 0.70)
json.dump({
    'reward': round(score, 2),
    'behavioral': round(behavioral, 2),
    'regression': round(min(0.10, remainder), 2),
    'structural': round(max(0, score - 0.80), 2),
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
