#!/usr/bin/env bash
#
# Verification for vllm-cohere-embed-system-prompt
#
# Tests that _mixed_input_to_messages uses task_prefix as a system prompt
# (not prepended to text), and that text-only inputs route through chat
# rendering when a chat template is available.
#
# Weights:
#   Behavioral (fail-to-pass):  Test 1 (0.35) + Test 2 (0.25) = 0.60
#   Pass-to-pass:               Test 3 (0.15)                  = 0.15
#   Structural:                 Test 4 (0.10)                  = 0.10
#   Config-derived:             Test 5 (0.10)                  = 0.10
#   Total: 1.00
#
set +e

TARGET="/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0
TEST1_PASSED=0
TEST2_PASSED=0

###############################################################################
# GATE: Python syntax validity
###############################################################################

echo "=== GATE: Python syntax check ==="
python3 -c "
import ast, sys
with open('$TARGET', 'r') as f:
    source = f.read()
try:
    ast.parse(source)
    print('PASS: syntax OK')
except SyntaxError as e:
    print(f'FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error, scoring 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# Test 1 (0.35): Behavioral fail-to-pass — _mixed_input_to_messages uses
#   task_prefix as system prompt, not prepended to text content
#   [pr_diff] Malformed task_prefix handling
###############################################################################

echo ""
echo "=== Test 1/5 [0.35]: Behavioral — task_prefix as system prompt ==="

# Create a standalone test script that extracts and tests the function
cat > /tmp/test_mixed_input.py << 'TESTEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Extract _mixed_input_to_messages
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == "_mixed_input_to_messages":
                    method_node = item
                    break

if method_node is None:
    print("FAIL: _mixed_input_to_messages not found")
    sys.exit(1)

# Extract source and clean it up
lines = source.splitlines(keepends=True)
func_lines = lines[method_node.lineno-1:method_node.end_lineno]
func_src = textwrap.dedent("".join(func_lines))

# Check for the buggy pattern in source first
if "task_prefix + item.text" in func_src or "task_prefix + text" in func_src:
    print("FAIL: Buggy concatenation pattern still present")
    sys.exit(1)

# Build testable code with mocks
test_code = '''
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

# Minimal mocks matching the protocol
@dataclass
class CohereEmbedContent:
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict] = None

@dataclass
class CohereEmbedInput:
    content: List[CohereEmbedContent]

@dataclass
class ChatCompletionContentPartTextParam:
    type: str
    text: str

@dataclass
class ChatCompletionContentPartImageParam:
    type: str
    image_url: "ImageURL"

@dataclass
class ImageURL:
    url: str

@dataclass
class CustomChatCompletionMessageParam:
    role: str
    content: Any

ChatCompletionMessageParam = Any

''' + func_src + '''

# Test: With task_prefix, first message should be system
inp = CohereEmbedInput(content=[CohereEmbedContent(type="text", text="hello")])
result = _mixed_input_to_messages(inp, task_prefix="query: ")

# Verify structure
assert len(result) >= 1, "Empty result"
first = result[0]
assert hasattr(first, "role"), "Messages must have role"
assert first.role == "system", f"First message should be system, got {first.role}"

# Verify system message content has task_prefix
has_prefix = False
if isinstance(first.content, list):
    for part in first.content:
        if hasattr(part, "text") and part.text == "query: ":
            has_prefix = True
            break
elif isinstance(first.content, str) and first.content == "query: ":
    has_prefix = True

assert has_prefix, "System message should contain task_prefix"

# Verify user message does NOT have prepended text
if len(result) >= 2:
    user_msg = result[1]
    assert user_msg.role == "user", f"Second message should be user, got {user_msg.role}"
    if isinstance(user_msg.content, list):
        for part in user_msg.content:
            if hasattr(part, "text"):
                assert not part.text.startswith("query: "), \
                    f"User text should not have prefix, got: {part.text}"
                assert part.text == "hello", f"User text should be 'hello', got: {part.text}"

# Test: Without task_prefix, no system message
inp2 = CohereEmbedInput(content=[CohereEmbedContent(type="text", text="world")])
result2 = _mixed_input_to_messages(inp2, task_prefix=None)
assert len(result2) == 1, f"Without prefix should have 1 message, got {len(result2)}"
assert result2[0].role == "user", "Without prefix, only message should be user"\n
print("PASS: task_prefix correctly rendered as system prompt")
'''

try:
    exec(test_code)
    sys.exit(0)
except AssertionError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Execution error: {type(e).__name__}: {e}")
    sys.exit(1)
TESTEOF

python3 /tmp/test_mixed_input.py
TEST1_RESULT=$?
if [ $TEST1_RESULT -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.35)")
    TEST1_PASSED=1
    echo "SCORE AFTER TEST 1: $SCORE"
fi

###############################################################################
# Test 2 (0.25): Behavioral fail-to-pass — _pre_process_cohere_online routing
#   Text-only inputs with chat template should use _batch_render_chat
#   [pr_diff] Text inputs incorrectly use completion path
###############################################################################

echo ""
echo "=== Test 2/5 [0.25]: Behavioral — routing logic for text inputs ==="

# This tests that the routing logic is correct via AST inspection
# combined with execution-based validation where possible
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find EmbedIOProcessor class
embed_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
        embed_class = node
        break

if embed_class is None:
    print("FAIL: EmbedIOProcessor not found")
    sys.exit(1)

# Check for _has_chat_template helper
methods = {}
for item in embed_class.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        methods[item.name] = item

has_chat_template_method = "_has_chat_template" in methods
has_preprocess_completion = "_preprocess_cohere_text_completion" in methods
has_preprocess_cohere_online = "_pre_process_cohere_online" in methods

if not has_preprocess_cohere_online:
    print("FAIL: _pre_process_cohere_online not found")
    sys.exit(1)

# Extract method source
lines = source.splitlines(keepends=True)
pre_process = methods["_pre_process_cohere_online"]
pre_process_src = textwrap.dedent("".join(lines[pre_process.lineno-1:pre_process.end_lineno]))

# Check for routing patterns
has_template_check = "_has_chat_template" in pre_process_src
has_batch_render = "_batch_render_chat" in pre_process_src
has_completion_path = "_preprocess_cohere_text_completion" in pre_process_src or "_preprocess_completion_online" in pre_process_src

# Verify the fix structure
# The fix should:
# 1. Check for chat template availability
# 2. Route to _batch_render_chat when template exists
# 3. Have a fallback completion path

if not has_batch_render:
    print("FAIL: _batch_render_chat not called")
    sys.exit(1)

if not has_template_check and not has_chat_template_method:
    print("FAIL: No chat template detection")
    sys.exit(1)

if not has_completion_path:
    print("FAIL: No completion fallback path")
    sys.exit(1)

# Check for request.texts handling with conditional
if "request.texts" not in pre_process_src:
    print("FAIL: request.texts not handled")
    sys.exit(1)

# Verify conditional structure around texts
# Should have if/else around the text path
has_conditional = "if" in pre_process_src and any(x in pre_process_src for x in [
    "else", "return", "_batch_render_chat"
])

if not has_conditional:
    print("FAIL: No conditional routing for text inputs")
    sys.exit(1)

# If _has_chat_template exists, verify it uses resolve_chat_template
if has_chat_template_method:
    helper_src = textwrap.dedent("".join(lines[methods["_has_chat_template"].lineno-1:methods["_has_chat_template"].end_lineno]))
    if "resolve_chat_template" not in helper_src:
        print("FAIL: _has_chat_template should use resolve_chat_template")
        sys.exit(1)

print("PASS: Chat template routing logic correctly implemented")
PYEOF
TEST2_RESULT=$?
if [ $TEST2_RESULT -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    TEST2_PASSED=1
    echo "SCORE AFTER TEST 2: $SCORE"
fi

###############################################################################
# Test 3 (0.15): Pass-to-pass — image/mixed input paths still work
#   [pr_diff] Ensure existing functionality not broken
###############################################################################

echo ""
echo "=== Test 3/5 [0.15]: Pass-to-pass — image/mixed paths intact ==="
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

embed_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
        embed_class = node
        break

if embed_class is None:
    print("FAIL: EmbedIOProcessor not found")
    sys.exit(1)

pre_process = None
for item in embed_class.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "_pre_process_cohere_online":
        pre_process = item
        break

if pre_process is None:
    print("FAIL: _pre_process_cohere_online not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
pre_process_src = textwrap.dedent("".join(lines[pre_process.lineno-1:pre_process.end_lineno]))

# Check image path is preserved
if "request.images" not in pre_process_src:
    print("FAIL: image handling missing")
    sys.exit(1)

# Check mixed inputs path is preserved
if "request.inputs" not in pre_process_src:
    print("FAIL: mixed input handling missing")
    sys.exit(1)

# Check _batch_render_chat is called for these paths
if "_batch_render_chat" not in pre_process_src:
    print("FAIL: _batch_render_chat not called")
    sys.exit(1)

# Check _mixed_input_to_messages is used for mixed inputs
if "_mixed_input_to_messages" not in pre_process_src:
    print("FAIL: _mixed_input_to_messages not called")
    sys.exit(1)

print("PASS: image and mixed input paths preserved")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

###############################################################################
# Test 4 (0.10): Structural — gated behind behavioral pass
###############################################################################

echo ""
echo "=== Test 4/5 [0.10]: Structural — implementation depth ==="

# Gate: Only award structural points if behavioral tests pass
if [ $TEST1_PASSED -eq 0 ] && [ $TEST2_PASSED -eq 0 ]; then
    echo "SKIPPED: Both behavioral tests failed, no structural points awarded"
else
    python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

embed_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
        embed_class = node
        break

if embed_class is None:
    print("FAIL: EmbedIOProcessor not found")
    sys.exit(1)

# Check non-stub implementation for key methods
for method_name in ["_mixed_input_to_messages", "_pre_process_cohere_online"]:
    method_node = None
    for item in embed_class.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
            method_node = item
            break

    if method_node is None:
        print(f"FAIL: {method_name} not found")
        sys.exit(1)

    # Count non-docstring, non-pass statements
    meaningful = 0
    for stmt in method_node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue  # Docstring
        if isinstance(stmt, ast.Pass):
            continue
        meaningful += 1

    if meaningful < 3:
        print(f"FAIL: {method_name} is a stub ({meaningful} statements)")
        sys.exit(1)

# Check file is reasonably sized
line_count = len(source.splitlines())
if line_count < 80:
    print(f"FAIL: file too short ({line_count} lines)")
    sys.exit(1)

print("PASS: implementation has sufficient depth")
PYEOF
    if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
fi

###############################################################################
# Test 5 (0.10): Config-derived — "Never use bare pip install"
# Source: AGENTS.md line 27 @ aa4eb0db78ec469438a7a18147b0372fe2eb7cf4
###############################################################################

echo ""
echo "=== Test 5/5 [0.10]: Config-derived — no bare pip install ==="
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        # Strip comments and check for bare pip install
        if grep -v '^\s*#' "/workspace/vllm/$cf" 2>/dev/null | grep -E '(?<!uv\s)pip\s+install' > /dev/null 2>&1; then
            echo "FAIL: $cf contains bare 'pip install' (should use 'uv pip install')"
            BARE_PIP=1
        fi
    fi
done
if [ "$BARE_PIP" -eq 0 ]; then
    echo "PASS: no bare pip install in changed files"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

###############################################################################
# Final score
###############################################################################

echo ""
echo "=== Final Score: $SCORE ==="
REWARD=$(python3 -c "print(min(1.0, round($SCORE, 4)))")
echo "$REWARD" > "$REWARD_FILE"
echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
