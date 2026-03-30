#!/usr/bin/env bash
#
# Verification for vllm-hermes-parser-stream-interval
#
# The Hermes tool parser must work correctly with stream_interval > 1.
# The old code used a token-by-token buffer that broke with multi-token chunks.
# The fix rewrites the streaming logic to re-parse current_text on each call.
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

TARGET="/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

###############################################################################
# GATE: Python syntax validity
###############################################################################

echo "=== GATE: Python syntax check ==="
python3 -c "
import ast, sys
for f in ['$TARGET', '/workspace/vllm/vllm/tool_parsers/longcat_tool_parser.py']:
    with open(f, 'r') as fh:
        try:
            ast.parse(fh.read())
        except SyntaxError as e:
            print(f'FAIL: syntax error in {f}: {e}')
            sys.exit(1)
print('PASS: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error, scoring 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# Test 1 (0.20): Behavioral fail-to-pass — old buffering approach removed
#   The buggy code has a tool_call_delta_buffer method that breaks with
#   multi-token chunks. The fix removes this method.
###############################################################################

echo ""
echo "=== Test 1/5 [0.20]: Behavioral — tool_call_delta_buffer removed ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find Hermes2ProToolParser class
parser_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
        parser_class = node
        break

if parser_class is None:
    print("FAIL: Hermes2ProToolParser class not found")
    sys.exit(1)

# Check that tool_call_delta_buffer method is NOT present
for item in parser_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "tool_call_delta_buffer":
        print("FAIL: tool_call_delta_buffer method still present (buggy buffering approach)")
        sys.exit(1)

# Also check that buffered_delta_text is not used
if "buffered_delta_text" in source:
    print("FAIL: buffered_delta_text still referenced (buggy buffering state)")
    sys.exit(1)

print("PASS: tool_call_delta_buffer and buffered_delta_text removed")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 2 (0.20): Behavioral fail-to-pass — streaming logic uses current_text
#   The fix re-parses current_text to find <tool_call> regions instead of
#   relying on delta_text buffering. Check that extract_tool_calls_streaming
#   uses current_text to find tool_call tags.
###############################################################################

echo ""
echo "=== Test 2/5 [0.20]: Behavioral — streaming uses current_text parsing ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find extract_tool_calls_streaming method
parser_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
        parser_class = node
        break

if parser_class is None:
    print("FAIL: Hermes2ProToolParser not found")
    sys.exit(1)

streaming_method = None
for item in parser_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "extract_tool_calls_streaming":
        streaming_method = item
        break

if streaming_method is None:
    print("FAIL: extract_tool_calls_streaming not found")
    sys.exit(1)

method_src = ast.get_source_segment(source, streaming_method) or ""

# The fix should NOT call tool_call_delta_buffer on delta_text
if "tool_call_delta_buffer" in method_src:
    print("FAIL: extract_tool_calls_streaming still calls tool_call_delta_buffer")
    sys.exit(1)

# The fix should NOT use partial_json_parser
if "partial_json_parser" in method_src:
    print("FAIL: extract_tool_calls_streaming still uses partial_json_parser")
    sys.exit(1)

# The fix should parse current_text to find tool call regions
# Check for common patterns: find/index/search on current_text with tool_call_start_token
if "current_text" not in method_src:
    print("FAIL: extract_tool_calls_streaming does not reference current_text")
    sys.exit(1)

# Check that the method (or helpers it calls) finds tool_call tags in the text
full_class_src = ast.get_source_segment(source, parser_class) or ""
if ("tool_call_start_token" not in full_class_src or
    "tool_call_end_token" not in full_class_src):
    print("FAIL: parser class doesn't reference tool call delimiters")
    sys.exit(1)

print("PASS: streaming logic re-parses current_text (no buffered delta approach)")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 3 (0.20): Pass-to-pass — extract_tool_calls (non-streaming) intact
###############################################################################

echo ""
echo "=== Test 3/5 [0.20]: Pass-to-pass — non-streaming extract_tool_calls intact ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py") as f:
    source = f.read()

tree = ast.parse(source)

parser_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
        parser_class = node
        break

if parser_class is None:
    print("FAIL: Hermes2ProToolParser not found")
    sys.exit(1)

# Check non-streaming extract_tool_calls still exists
methods = [item.name for item in parser_class.body if isinstance(item, ast.FunctionDef)]

if "extract_tool_calls" not in methods:
    print(f"FAIL: extract_tool_calls method missing. Found: {methods}")
    sys.exit(1)

if "extract_tool_calls_streaming" not in methods:
    print(f"FAIL: extract_tool_calls_streaming method missing. Found: {methods}")
    sys.exit(1)

# Check __init__ still exists and sets up core state
init_method = None
for item in parser_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
        init_method = item
        break

if init_method is None:
    print("FAIL: __init__ not found")
    sys.exit(1)

init_src = ast.get_source_segment(source, init_method) or ""
if "tool_call_start_token" not in init_src or "tool_call_end_token" not in init_src:
    print("FAIL: __init__ missing tool_call token setup")
    sys.exit(1)

print(f"PASS: parser has methods: {methods}")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 4 (0.20): Structural — content extraction and JSON extraction helpers
#   The fix introduces helper methods/functions for content extraction and
#   tool call JSON extraction. Check that the parser has some form of modular
#   extraction logic.
###############################################################################

echo ""
echo "=== Test 4/5 [0.20]: Structural — modular extraction logic ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py") as f:
    source = f.read()

tree = ast.parse(source)

# Count helper methods/functions for extraction logic
# The fix adds: _extract_content, _extract_tool_call_jsons, _extract_tool_name,
# _extract_tool_args, _compute_args_diff, _partial_tag_overlap, _is_valid_json
# We don't require exact names, but there should be new helper functions/methods.

parser_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
        parser_class = node
        break

if parser_class is None:
    print("FAIL: Hermes2ProToolParser not found")
    sys.exit(1)

methods = [item.name for item in parser_class.body if isinstance(item, ast.FunctionDef)]

# The old code had: __init__, tool_call_delta_buffer, adjust_request,
#   extract_tool_calls, extract_tool_calls_streaming (5 methods)
# The fix should have: __init__, adjust_request, extract_tool_calls,
#   extract_tool_calls_streaming, plus new helpers (>=7 methods total)
# OR the helpers may be module-level functions.

# Count module-level functions too
module_funcs = [n.name for n in ast.iter_child_nodes(tree)
                if isinstance(n, ast.FunctionDef)]

total_helper_count = len(methods) + len(module_funcs)

# Check for key patterns in the source that indicate proper extraction logic
has_content_extraction = ("_extract_content" in source or
                          "_sent_content_idx" in source or
                          "sendable_idx" in source)
has_json_extraction = ("_extract_tool_call_jsons" in source or
                       "tool_call_start_token" in source)
has_args_diff = ("_compute_args_diff" in source or
                 "streamed_args_for_tool" in source)

checks_passed = sum([has_content_extraction, has_json_extraction, has_args_diff])

if checks_passed >= 2:
    print(f"PASS: {checks_passed}/3 extraction patterns found, {len(methods)} class methods, {len(module_funcs)} module functions")
    sys.exit(0)

# Fallback: just check there are enough methods (more than the old 5)
if total_helper_count >= 7:
    print(f"PASS: {total_helper_count} total functions/methods (sufficient for modular rewrite)")
    sys.exit(0)

print(f"FAIL: insufficient modular extraction logic (methods={methods}, module_funcs={module_funcs})")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 5 (0.10): Anti-stub — files retain full implementation
###############################################################################

echo ""
echo "=== Test 5/6 [0.10]: Anti-stub check ==="
python3 << 'PYEOF'
import ast, sys

# Check hermes parser
with open("/workspace/vllm/vllm/tool_parsers/hermes_tool_parser.py") as f:
    hermes_src = f.read()

if len(hermes_src.splitlines()) < 100:
    print(f"FAIL: hermes parser too short ({len(hermes_src.splitlines())} lines)")
    sys.exit(1)

required = ["Hermes2ProToolParser", "extract_tool_calls_streaming",
            "extract_tool_calls", "tool_call_start_token", "DeltaMessage"]
missing = [r for r in required if r not in hermes_src]
if missing:
    print(f"FAIL: hermes parser missing: {missing}")
    sys.exit(1)

# Check longcat parser still exists and inherits
with open("/workspace/vllm/vllm/tool_parsers/longcat_tool_parser.py") as f:
    longcat_src = f.read()

if "Hermes2ProToolParser" not in longcat_src:
    print("FAIL: longcat parser no longer inherits from Hermes2ProToolParser")
    sys.exit(1)

if len(longcat_src.splitlines()) < 10:
    print(f"FAIL: longcat parser too short ({len(longcat_src.splitlines())} lines)")
    sys.exit(1)

print(f"PASS: hermes={len(hermes_src.splitlines())}L, longcat={len(longcat_src.splitlines())}L")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

###############################################################################
# Test 6 (0.10): Config-derived — "Never use bare pip install"
# Source: AGENTS.md line 27 @ 0ae89f18fd75c5fcac48ff711ed84464c3da5d33
###############################################################################

echo ""
echo "=== Test 6/6 [0.10]: Config-derived — no bare pip install in changed files ==="
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^.*#' | grep -v 'uv pip' > /dev/null 2>&1; then
            echo "FAIL: $cf contains bare 'pip install'"
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
