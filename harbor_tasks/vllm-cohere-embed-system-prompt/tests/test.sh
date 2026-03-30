#!/usr/bin/env bash
#
# Verification for vllm-cohere-embed-system-prompt
#
# Tests that _mixed_input_to_messages uses task_prefix as a system prompt
# (not prepended to text), and that text-only inputs route through chat
# rendering when a chat template is available.
#
# Weights:
#   Behavioral (fail-to-pass):  Test 1 (0.20) + Test 2 (0.20) = 0.40
#   Pass-to-pass:               Test 3 (0.20)                  = 0.20
#   Structural:                 Test 4 (0.20)                  = 0.20
#   Anti-stub:                  Test 5 (0.10)                  = 0.10
#   Config-derived:             Test 6 (0.10)                  = 0.10
#   Total: 1.00
#
set +e

TARGET="/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

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
# Test 1 (0.20): Behavioral fail-to-pass — _mixed_input_to_messages uses
#   system prompt for task_prefix, not text prepending
#   In the buggy code, task_prefix is prepended: text = task_prefix + item.text
#   In the fix, task_prefix creates a system message.
###############################################################################

echo ""
echo "=== Test 1/5 [0.20]: Behavioral — task_prefix as system prompt ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find _mixed_input_to_messages method
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == "_mixed_input_to_messages":
                    method_node = item
                    break

if method_node is None:
    print("FAIL: _mixed_input_to_messages method not found")
    sys.exit(1)

method_src = ast.get_source_segment(source, method_node) or ""

# Check for the buggy pattern: task_prefix + item.text (prepending to text)
# The old code: text = task_prefix + item.text if task_prefix else item.text
if "task_prefix + item.text" in method_src or "task_prefix + text" in method_src:
    print("FAIL: task_prefix is still being prepended to text content")
    sys.exit(1)

# Check for the fix pattern: system role message with task_prefix
if '"system"' in method_src or "'system'" in method_src or 'role="system"' in method_src:
    print("PASS: task_prefix rendered as system prompt message")
else:
    # Alternative: check for system role in any form
    if "system" in method_src.lower() and "role" in method_src:
        print("PASS: system role message found")
    else:
        print("FAIL: no system prompt message found for task_prefix")
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 2 (0.20): Behavioral fail-to-pass — _has_chat_template helper exists
#   and _pre_process_cohere_online uses it to decide routing
###############################################################################

echo ""
echo "=== Test 2/5 [0.20]: Behavioral — chat template detection ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the EmbedIOProcessor class
embed_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
        embed_class = node
        break

if embed_class is None:
    print("FAIL: EmbedIOProcessor class not found")
    sys.exit(1)

methods = [item.name for item in embed_class.body
           if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]

# Check for _has_chat_template or equivalent
has_template_check = "_has_chat_template" in methods

# Check _pre_process_cohere_online references chat template decision
pre_process = None
for item in embed_class.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if item.name == "_pre_process_cohere_online":
            pre_process = item
            break

if pre_process is None:
    print("FAIL: _pre_process_cohere_online not found")
    sys.exit(1)

pre_process_src = ast.get_source_segment(source, pre_process) or ""

# The fix should check for chat template availability
has_template_ref = ("_has_chat_template" in pre_process_src or
                    "chat_template" in pre_process_src or
                    "resolve_chat_template" in pre_process_src)

if has_template_check and has_template_ref:
    print("PASS: _has_chat_template exists and is used in routing")
elif has_template_ref:
    print("PASS: chat template check present in _pre_process_cohere_online")
else:
    print("FAIL: no chat template detection found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 3 (0.20): Pass-to-pass — image and mixed input paths still work
###############################################################################

echo ""
echo "=== Test 3/5 [0.20]: Pass-to-pass — image/mixed paths intact ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find _pre_process_cohere_online
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
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if item.name == "_pre_process_cohere_online":
            pre_process = item
            break

if pre_process is None:
    print("FAIL: _pre_process_cohere_online not found")
    sys.exit(1)

pre_process_src = ast.get_source_segment(source, pre_process) or ""

# Check that image handling is still present
if "request.images" not in pre_process_src:
    print("FAIL: image handling missing from _pre_process_cohere_online")
    sys.exit(1)

# Check that input handling is still present
if "request.inputs" not in pre_process_src:
    print("FAIL: mixed input handling missing from _pre_process_cohere_online")
    sys.exit(1)

# Check that _batch_render_chat is still called
if "_batch_render_chat" not in pre_process_src:
    print("FAIL: _batch_render_chat call missing")
    sys.exit(1)

print("PASS: image and mixed input paths preserved")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 4 (0.20): Structural — completion fallback for no-template case
###############################################################################

echo ""
echo "=== Test 4/5 [0.20]: Structural — fallback to completion path ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py") as f:
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

class_src = ast.get_source_segment(source, embed_class) or ""

# The fix should have a completion fallback path when no chat template
# Either _preprocess_cohere_text_completion or _preprocess_completion_online
has_completion_path = ("_preprocess_cohere_text_completion" in class_src or
                       "_preprocess_completion_online" in class_src)

if not has_completion_path:
    print("FAIL: no completion fallback path found")
    sys.exit(1)

# Check that _apply_task_instruction is still referenced (for non-template fallback)
if "_apply_task_instruction" not in class_src and "task_prefix" not in class_src:
    print("FAIL: task instruction application missing")
    sys.exit(1)

print("PASS: completion fallback path exists with task instruction support")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 5 (0.10): Anti-stub — file retains full implementation
###############################################################################

echo ""
echo "=== Test 5/6 [0.10]: Anti-stub check ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/pooling/embed/io_processor.py") as f:
    source = f.read()

if len(source.splitlines()) < 200:
    print(f"FAIL: file too short ({len(source.splitlines())} lines)")
    sys.exit(1)

required = ["EmbedIOProcessor", "_pre_process_cohere_online",
            "_mixed_input_to_messages", "CohereEmbedRequest",
            "_batch_render_chat", "engine_inputs"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing identifiers: {missing}")
    sys.exit(1)

print(f"PASS: file has {len(source.splitlines())} lines with all required identifiers")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

###############################################################################
# Test 6 (0.10): Config-derived — "Never use bare pip install"
# Source: AGENTS.md line 27 @ aa4eb0db78ec469438a7a18147b0372fe2eb7cf4
###############################################################################

echo ""
echo "=== Test 6/6 [0.10]: Config-derived — no bare pip install in changed files ==="
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^.*#' | grep -v 'uv pip' > /dev/null 2>&1; then
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
