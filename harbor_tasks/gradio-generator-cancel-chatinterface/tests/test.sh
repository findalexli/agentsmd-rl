#!/usr/bin/env bash
# Verifier for gradio-generator-cancel-chatinterface
#
# Bug: Generator not properly closed on cancel in ChatInterface;
# SyncToAsyncIterator.aclose() not async; safe_aclose_iterator missing await.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

CHAT="/workspace/gradio/gradio/chat_interface.py"
UTILS="/workspace/gradio/gradio/utils.py"

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
for path in ["/workspace/gradio/gradio/chat_interface.py", "/workspace/gradio/gradio/utils.py"]:
    try:
        with open(path) as f:
            ast.parse(f.read())
    except SyntaxError as e:
        print(f"GATE FAIL: {path}: {e}")
        sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: aclosing used in chat_interface)   = 0.30
#   TEST 2 (fail-to-pass: aclose is async in utils)          = 0.25
#   TEST 3 (fail-to-pass: await aclose in safe_aclose)       = 0.15
#   TEST 4 (pass-to-pass: _stream_fn still exists)           = 0.10
#   TEST 5 (anti-stub)                                       = 0.15
#   TOTAL                                                    = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: aclosing used in chat_interface.py
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] aclosing() used in _stream_fn and _examples_stream_fn"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

# Check for aclosing import
has_aclosing_import = 'aclosing' in src and 'contextlib' in src

# Check for aclosing usage in the streaming methods
has_aclosing_usage = 'aclosing(generator)' in src or 'aclosing( generator)' in src

if has_aclosing_import and has_aclosing_usage:
    # Count usages - should be at least 2 (one in _stream_fn, one in _examples_stream_fn)
    count = src.count('aclosing(generator')
    if count >= 2:
        print(f"PASS: aclosing(generator) used {count} times")
        sys.exit(0)
    elif count >= 1:
        print(f"PASS: aclosing(generator) used {count} time(s)")
        sys.exit(0)

if has_aclosing_import:
    print("PASS: aclosing imported and available")
    sys.exit(0)

print("FAIL: aclosing not imported or not used")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: aclose is async in SyncToAsyncIterator
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] SyncToAsyncIterator.aclose() is async"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the SyncToAsyncIterator class
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SyncToAsyncIterator':
        for item in node.body:
            if isinstance(item, ast.AsyncFunctionDef) and item.name == 'aclose':
                print("PASS: aclose is async (AsyncFunctionDef)")
                sys.exit(0)
            if isinstance(item, ast.FunctionDef) and item.name == 'aclose':
                print("FAIL: aclose is still sync (FunctionDef, not async)")
                sys.exit(1)

# Fallback: check text pattern
lines = source.split('\n')
for i, line in enumerate(lines):
    if 'async def aclose' in line and 'SyncToAsyncIterator' in source[:source.index(line)]:
        print("PASS: async def aclose found")
        sys.exit(0)

print("FAIL: aclose method not found or not async")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: await used in safe_aclose_iterator
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] await used for aclose in safe_aclose_iterator"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/utils.py") as f:
    src = f.read()

# Find safe_aclose_iterator function
if 'safe_aclose_iterator' not in src:
    print("FAIL: safe_aclose_iterator not found")
    sys.exit(1)

# Extract the function body
fn_start = src.index('def safe_aclose_iterator')
# Find next def at same or lower indent
lines = src[fn_start:].split('\n')
fn_body = []
for i, line in enumerate(lines):
    if i > 0 and line and not line[0].isspace() and line.strip():
        break
    fn_body.append(line)

fn_text = '\n'.join(fn_body)

# Check for await iterator.aclose() or await ...aclose()
if 'await iterator.aclose()' in fn_text or 'await iterator.aclose' in fn_text:
    print("PASS: await used with iterator.aclose() in safe_aclose_iterator")
    sys.exit(0)

# The buggy code has: iterator.aclose() without await
if 'iterator.aclose()' in fn_text and 'await' not in fn_text:
    print("FAIL: iterator.aclose() called without await")
    sys.exit(1)

# Alternative check: any await + aclose in the function
if 'await' in fn_text and 'aclose' in fn_text:
    print("PASS: await + aclose found in safe_aclose_iterator")
    sys.exit(0)

print("FAIL: no await aclose pattern found")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: _stream_fn still exists
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] _stream_fn method preserved"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

if '_stream_fn' in src and '_examples_stream_fn' in src:
    print("PASS: _stream_fn and _examples_stream_fn preserved")
    sys.exit(0)

print("FAIL: streaming methods not found")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.15]: Files have substantial content
###############################################################################
echo ""
echo "TEST 5: [anti-stub] files have substantial content"
python3 << 'PYEOF'
import ast, sys

for path, min_lines in [
    ("/workspace/gradio/gradio/chat_interface.py", 300),
    ("/workspace/gradio/gradio/utils.py", 500),
]:
    with open(path) as f:
        source = f.read()
    lines = len(source.splitlines())
    if lines < min_lines:
        print(f"FAIL: {path} has {lines} lines (expected >= {min_lines})")
        sys.exit(1)

print("PASS: both files have substantial content")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit 5c4dc6aca11575cf4fec6704afd48a54664f983f
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/chat_interface.py /workspace/gradio/gradio/utils.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T6=0; echo "TEST 6: config ruff format PASS"; else T6=1; echo "TEST 6: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.15 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: aclosing in chat_interface) = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: aclose is async)            = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: await in safe_aclose)       = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: _stream_fn exists)          = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub)                                = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 6 (config: ruff format)                   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
