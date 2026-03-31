#!/usr/bin/env bash
set +e

TOTAL=0.0
BEHAVIORAL=0.0
REGRESSION=0.0
FILE="/repo/python/sglang/srt/managers/tokenizer_manager.py"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}
add_behavioral() {
    BEHAVIORAL=$(python3 -c "print(round($BEHAVIORAL + $1, 4))")
    add_score "$1"
}
add_regression() {
    REGRESSION=$(python3 -c "print(round($REGRESSION + $1, 4))")
    add_score "$1"
}

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (gate): Python file must be syntactically valid
if python3 -c "
import ast, sys
try:
    with open('$FILE') as f:
        ast.parse(f.read())
except SyntaxError as e:
    print(f'GATE FAIL: {e}', file=sys.stderr)
    sys.exit(1)
"; then
    echo "GATE: syntax check PASSED"
else
    echo "GATE: syntax check FAILED — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# CHECK 1 (0.35) — F2P behavioral
# Execute any backlog warning code path and verify no
# WARNING-level log is emitted.  Accepts: deletion,
# downgrade to DEBUG/INFO, condition tightening.
########################################
# [pr_diff] (0.35): Streaming with >1 pending chunk must not emit WARNING-level log
python3 << 'PYEOF'
import ast, sys, logging, io, textwrap, types

FILE = "/repo/python/sglang/srt/managers/tokenizer_manager.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Locate _wait_one_response
method = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == '_wait_one_response':
        method = node
        break
if method is None:
    print("FAIL: _wait_one_response not found"); sys.exit(1)

# Guard: method must not be a stub — require functional structure
yields = sum(1 for n in ast.walk(method) if isinstance(n, ast.Yield))
body_lines = method.end_lineno - method.lineno
for_loops = sum(1 for n in ast.walk(method) if isinstance(n, ast.For))
try_blocks = sum(1 for n in ast.walk(method) if isinstance(n, ast.Try))
has_event = any(isinstance(n, ast.Attribute) and n.attr in ('wait','clear') for n in ast.walk(method))
if yields < 2 or body_lines < 25 or for_loops < 1 or try_blocks < 1 or not has_event:
    print(f"FAIL: method looks stubbed (yields={yields}, lines={body_lines}, "
          f"for={for_loops}, try={try_blocks}, event={has_event})"); sys.exit(1)

# Find if-blocks inside method that contain a logger.warning/warn about backlog
found_warning = False
for child in ast.walk(method):
    if not isinstance(child, ast.If):
        continue
    for sub in ast.walk(child):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if not (isinstance(func, ast.Attribute) and func.attr in ('warning', 'warn')):
            continue
        for arg in sub.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                low = arg.value.lower()
                if any(kw in low for kw in ['backlog', 'p99 tbt', 'queued chunks', 'inflate']):
                    # Found it — execute to confirm it fires at WARNING level
                    lines = source.splitlines()
                    block = textwrap.dedent('\n'.join(lines[child.lineno-1:child.end_lineno]))
                    cap = io.StringIO()
                    h = logging.StreamHandler(cap)
                    h.setLevel(logging.WARNING)
                    lg = logging.getLogger('backlog_test')
                    lg.handlers.clear(); lg.addHandler(h); lg.setLevel(logging.DEBUG)
                    ns = {
                        'is_stream': True,
                        'pending': [{"t":"a"},{"t":"b"},{"t":"c"}],
                        'logger': lg, 'obj': types.SimpleNamespace(rid="test"),
                        'len': len,
                    }
                    try:
                        exec(block, ns)
                    except Exception:
                        pass  # restructured code may need vars we don't provide
                    if cap.getvalue().strip():
                        print("FAIL: WARNING-level streaming backlog log still emitted")
                        sys.exit(1)
                    found_warning = True  # block exists but doesn't emit WARNING — OK

if not found_warning:
    print("PASS: Backlog warning block removed entirely")
else:
    print("PASS: Backlog warning block present but not at WARNING level")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "CHECK 1 PASSED: No WARNING-level streaming backlog log"
    add_behavioral 0.35
else
    echo "CHECK 1 FAILED"
fi

########################################
# CHECK 2 (0.25) — F2P behavioral
# Scan ALL logger calls in _wait_one_response for
# WARNING-level calls mentioning backlog/streaming.
# This catches cases outside if-blocks too.
########################################
# [pr_diff] (0.25): No logger.warning about streaming backlog anywhere in method
python3 << 'PYEOF'
import ast, sys, logging, io, textwrap, types

FILE = "/repo/python/sglang/srt/managers/tokenizer_manager.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if node.name != '_wait_one_response':
        continue
    # Guard: must be functional (not a stub that trivially has no warning)
    yields = sum(1 for n in ast.walk(node) if isinstance(n, ast.Yield))
    for_loops = sum(1 for n in ast.walk(node) if isinstance(n, ast.For))
    body_lines = node.end_lineno - node.lineno
    if yields < 2 or for_loops < 1 or body_lines < 25:
        print(f"FAIL: method looks stubbed (yields={yields}, for={for_loops}, lines={body_lines})")
        sys.exit(1)
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if not (isinstance(func, ast.Attribute) and func.attr in ('warning', 'warn')):
            continue
        for arg in child.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                low = arg.value.lower()
                if any(kw in low for kw in ['backlog', 'queued chunks', 'p99 tbt', 'inflate p99']):
                    # Execute the call to confirm level
                    lines = source.splitlines()
                    call_src = '\n'.join(lines[child.lineno-1:child.end_lineno])
                    call_src = textwrap.dedent(call_src)
                    cap = io.StringIO()
                    h = logging.StreamHandler(cap)
                    h.setLevel(logging.WARNING)
                    lg = logging.getLogger('scan_test')
                    lg.handlers.clear(); lg.addHandler(h); lg.setLevel(logging.DEBUG)
                    ns = {
                        'logger': lg, 'obj': types.SimpleNamespace(rid="x"),
                        'pending': [1,2,3], 'len': len,
                    }
                    try:
                        exec(call_src, ns)
                    except Exception:
                        pass
                    if cap.getvalue().strip():
                        print("FAIL: WARNING-level backlog log found outside if-block")
                        sys.exit(1)
    print("PASS: No WARNING-level backlog log calls in method")
    sys.exit(0)

print("FAIL: _wait_one_response not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "CHECK 2 PASSED"
    add_behavioral 0.25
else
    echo "CHECK 2 FAILED"
fi

########################################
# CHECK 3 (0.20) — P2P regression
# _wait_one_response must be an async generator with
# drain-loop and async event coordination.
########################################
# [pr_diff] (0.20): Drain loop + async generator + event handling preserved
python3 << 'PYEOF'
import ast, sys

FILE = "/repo/python/sglang/srt/managers/tokenizer_manager.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, ast.AsyncFunctionDef):
        continue
    if node.name != '_wait_one_response':
        continue

    # Must have yield (async generator)
    yields = sum(1 for n in ast.walk(node) if isinstance(n, ast.Yield))
    if yields < 2:
        print(f"FAIL: {yields} yield(s), need >=2"); sys.exit(1)

    # Must have a for-loop (drain loop over pending chunks)
    for_loops = sum(1 for n in ast.walk(node) if isinstance(n, ast.For))
    if for_loops < 1:
        print("FAIL: no for-loop (drain loop missing)"); sys.exit(1)

    # Must reference event coordination (.wait or .clear or .set on an attribute)
    has_event = any(
        isinstance(n, ast.Attribute) and n.attr in ('wait', 'clear')
        for n in ast.walk(node)
    )
    if not has_event:
        print("FAIL: no event.wait/clear (async coordination missing)"); sys.exit(1)

    print("PASS: async generator with drain loop and event handling")
    sys.exit(0)

print("FAIL: _wait_one_response not found as async def")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "CHECK 3 PASSED"
    add_regression 0.20
else
    echo "CHECK 3 FAILED"
fi

########################################
# CHECK 4 (0.10) — P2P regression
# Method handles completion and errors properly.
########################################
# [pr_diff] (0.10): Must handle finished state and have error handling
python3 << 'PYEOF'
import ast, sys

FILE = "/repo/python/sglang/srt/managers/tokenizer_manager.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if node.name != '_wait_one_response':
        continue

    has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
    has_finished = any(
        (isinstance(n, ast.Name) and n.id == 'finished') or
        (isinstance(n, ast.Attribute) and n.attr == 'finished')
        for n in ast.walk(node)
    )

    if not has_try:
        print("FAIL: no try/except (error handling missing)"); sys.exit(1)
    if not has_finished:
        print("FAIL: no 'finished' reference (completion detection missing)"); sys.exit(1)

    print("PASS: error handling and completion detection present")
    sys.exit(0)

print("FAIL: _wait_one_response not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "CHECK 4 PASSED"
    add_regression 0.10
else
    echo "CHECK 4 FAILED"
fi

########################################
# CHECK 5 (0.10) — Anti-stub
# Method body must be substantial.
########################################
# [pr_diff] (0.10): Method must not be stubbed out
python3 << 'PYEOF'
import ast, sys

FILE = "/repo/python/sglang/srt/managers/tokenizer_manager.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if node.name != '_wait_one_response':
        continue

    line_count = node.end_lineno - node.lineno
    if line_count < 25:
        print(f"FAIL: only {line_count} lines (need >25)"); sys.exit(1)

    # Count meaningful statement types
    meaningful = sum(1 for n in ast.walk(node)
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.If, ast.For, ast.While,
                          ast.Try, ast.Yield, ast.Delete, ast.Raise)))
    if meaningful < 15:
        print(f"FAIL: only {meaningful} meaningful stmts (need >15)"); sys.exit(1)

    print(f"PASS: {line_count} lines, {meaningful} meaningful statements")
    sys.exit(0)

print("FAIL: _wait_one_response not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "CHECK 5 PASSED"
    add_regression 0.10
else
    echo "CHECK 5 FAILED"
fi

########################################
# Write results
########################################
echo "$TOTAL" > /logs/verifier/reward.txt
echo "{\"reward\": $TOTAL, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION}" > /logs/verifier/reward.json
echo "Total reward: $TOTAL (behavioral=$BEHAVIORAL, regression=$REGRESSION)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
