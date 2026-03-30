#!/usr/bin/env bash
# Verifier for areal-streaming-response-handler
# Task: fix streaming responses in chat/completions endpoint
# File: areal/experimental/openai/proxy/proxy_rollout_server.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py"

echo "=== areal streaming response handler verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAVIORAL_STREAM_STRIP=0.20
W_BEHAVIORAL_STREAMING_BRANCH=0.25
W_BEHAVIORAL_NONSTREAM=0.15
W_STRUCTURAL_SSE=0.10
W_STRUCTURAL_RESPONSE_MODEL=0.10
W_ANTISTUB=0.10
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- stream kwarg is stripped from request body --
echo ""
echo "TEST 1: behavioral -- stream kwarg stripped from request body (weight=$W_BEHAVIORAL_STREAM_STRIP)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find _call_client_create function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_call_client_create":
        func_node = node
        break

if func_node is None:
    print("FAIL: _call_client_create not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# The fix should pop/remove "stream" from kwargs before conditionally adding it
if 'kwargs.pop("stream"' in func_src or "kwargs.pop('stream'" in func_src:
    print("PASS: stream is popped from kwargs in _call_client_create")
    sys.exit(0)
elif 'del kwargs["stream"]' in func_src or "del kwargs['stream']" in func_src:
    print("PASS: stream is deleted from kwargs in _call_client_create")
    sys.exit(0)
elif '"stream"' in func_src and ('pop' in func_src or 'del ' in func_src or 'remove' in func_src):
    print("PASS: stream appears to be removed from kwargs")
    sys.exit(0)
else:
    print("FAIL: stream is not stripped from request body kwargs")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_STREAM_STRIP)")
fi

# -- TEST 2 (PRIMARY): behavioral -- chat_completions has streaming branch --
echo ""
echo "TEST 2: behavioral -- chat_completions handles stream=true (weight=$W_BEHAVIORAL_STREAMING_BRANCH)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find chat_completions function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "chat_completions":
        func_node = node
        break

if func_node is None:
    print("FAIL: chat_completions function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# Check that there is a streaming branch
has_stream_check = ("stream" in func_src and ("is True" in func_src or "is_streaming" in func_src or "== True" in func_src))
has_streaming_response = "StreamingResponse" in func_src
has_sse = "text/event-stream" in func_src or "event-stream" in func_src

if has_stream_check and has_streaming_response:
    print("PASS: chat_completions has streaming branch with StreamingResponse")
    sys.exit(0)
elif has_stream_check and has_sse:
    print("PASS: chat_completions has streaming branch with SSE")
    sys.exit(0)
else:
    missing = []
    if not has_stream_check:
        missing.append("stream check")
    if not has_streaming_response:
        missing.append("StreamingResponse")
    print(f"FAIL: missing {', '.join(missing)} in chat_completions")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_STREAMING_BRANCH)")
fi

# -- TEST 3 (PRIMARY): behavioral -- SSE format with data: prefix and [DONE] --
echo ""
echo "TEST 3: behavioral -- SSE format produces data: lines and [DONE] (weight=$W_BEHAVIORAL_NONSTREAM)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find chat_completions function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "chat_completions":
        func_node = node
        break

if func_node is None:
    print("FAIL: chat_completions function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

has_data_prefix = 'data: ' in func_src or '"data:' in func_src or "f'data:" in func_src or 'f"data:' in func_src
has_done = '[DONE]' in func_src

# Also check for a generator pattern (yield or async generator)
has_generator = 'yield' in func_src or 'async def' in func_src or '_sse_generator' in func_src or 'sse' in func_src.lower()

if has_data_prefix and has_done:
    print("PASS: SSE format with data: prefix and [DONE] sentinel")
    sys.exit(0)
elif has_data_prefix:
    print("PASS: SSE format with data: prefix (partial - [DONE] may be elsewhere)")
    sys.exit(0)
else:
    print("FAIL: no SSE format (data: prefix) found in chat_completions")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_NONSTREAM)")
fi

# -- TEST 4 (SUPPLEMENTARY): structural -- response_model=None on decorator --
echo ""
echo "TEST 4: structural -- response_model=None on chat_completions decorator (weight=$W_STRUCTURAL_RESPONSE_MODEL)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

# The decorator should have response_model=None to allow StreamingResponse
if "response_model=None" in source or "response_model = None" in source:
    print("PASS: response_model=None found")
    sys.exit(0)
# Also accept if the return type annotation includes StreamingResponse
elif "StreamingResponse" in source and "chat_completions" in source:
    # The decorator might not need response_model=None if handled differently
    print("PASS: StreamingResponse used in chat_completions")
    sys.exit(0)
else:
    print("FAIL: no response_model=None and no StreamingResponse handling")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_RESPONSE_MODEL)")
fi

# -- TEST 5 (SUPPLEMENTARY): structural -- stream=True passed to _call_client_create --
echo ""
echo "TEST 5: structural -- streaming branch calls _call_client_create with stream=True (weight=$W_STRUCTURAL_SSE)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "chat_completions":
        func_node = node
        break

if func_node is None:
    print("FAIL: chat_completions not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# The streaming branch should pass stream=True to _call_client_create
if "stream=True" in func_src:
    print("PASS: stream=True passed in chat_completions")
    sys.exit(0)
else:
    print("FAIL: stream=True not found in chat_completions")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SSE)")
fi

# -- TEST 6: anti-stub check --
echo ""
echo "TEST 6: anti-stub -- file retains original logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py") as f:
    source = f.read()

required = ["_call_client_create", "chat_completions", "_openai_client",
            "StreamingResponse", "ChatCompletion", "CompletionCreateParams",
            "session_id", "HTTPException"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit 421e4e5d9816f9a173374331df96d5d799a40844
echo ""
echo "TEST 7: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit 421e4e5d9816f9a173374331df96d5d799a40844
echo ""
echo "TEST 8: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    echo "PASS"
else
    echo "FAIL: bare print() found"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
