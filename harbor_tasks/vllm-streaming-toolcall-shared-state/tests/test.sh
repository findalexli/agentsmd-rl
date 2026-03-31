#!/usr/bin/env bash
set -euo pipefail

TARGET="/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
REWARD=0

echo "=== vllm-streaming-toolcall-shared-state ==="

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): File must be valid Python
echo "--- GATE: Python syntax check ---"
if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$TARGET').read())
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"; then
    echo "GATE FAILED: syntax error in target file"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"
echo ""

set +e  # Continue through all checks even if individual ones error

########################################
# BEHAVIORAL (fail-to-pass): all_previous_token_ids independence
########################################
# [pr_diff] (0.35): all_previous_token_ids must create independent lists per choice
echo "--- CHECK: all_previous_token_ids independence (0.35) ---"
RESULT=$(python3 << 'PYEOF'
import ast, sys, copy

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Find chat_completion_stream_generator method first
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'chat_completion_stream_generator':
        method_node = node
        break

if not method_node:
    print("FAIL: chat_completion_stream_generator method not found")
    sys.exit(0)

# Find all_previous_token_ids assignment WITHIN the method
expr_code = None
for node in ast.walk(method_node):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == 'all_previous_token_ids':
                expr_code = ast.get_source_segment(source, node.value)
                break
    if expr_code:
        break

if not expr_code:
    print("FAIL: could not find all_previous_token_ids assignment in method")
    sys.exit(0)

# Eval the expression with a broad namespace to support valid alternatives
num_choices = 3
try:
    result = eval(expr_code, {
        "num_choices": num_choices,
        "copy": copy,
        "list": list,
        "range": range,
        "__builtins__": __builtins__,
    })
except Exception as e:
    print(f"FAIL: expression eval error: {e}")
    sys.exit(0)

ok = True

# Must produce a list of exactly num_choices elements
if not isinstance(result, list) or len(result) != num_choices:
    print(f"FAIL: expected list of length {num_choices}, got {type(result).__name__} len={len(result) if isinstance(result, list) else 'N/A'}")
    sys.exit(0)

# Identity check: each element must be a distinct object
for i in range(num_choices):
    for j in range(i + 1, num_choices):
        if result[i] is result[j]:
            print(f"FAIL: result[{i}] is result[{j}] (shared reference)")
            ok = False

# Mutation check: appending to one must not affect others
result[0].append(42)
for i in range(1, num_choices):
    if 42 in result[i]:
        print(f"FAIL: appending to result[0] mutated result[{i}]")
        ok = False

print("OK" if ok else "FAIL")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.35)")
    echo "  +0.35"
fi
echo ""

########################################
# BEHAVIORAL (fail-to-pass): tool_parsers independence
########################################
# [pr_diff] (0.30): tool_parsers must create independent parser instances per choice
echo "--- CHECK: tool_parsers independence (0.30) ---"
RESULT=$(python3 << 'PYEOF'
import ast, sys, copy

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Find chat_completion_stream_generator method
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'chat_completion_stream_generator':
        method_node = node
        break

if not method_node:
    print("FAIL: chat_completion_stream_generator method not found")
    sys.exit(0)

# Find tool_parsers assignment (non-None value) within the method
expr_code = None
for node in ast.walk(method_node):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        if isinstance(node, ast.AnnAssign):
            target = node.target
            value = node.value
        else:
            target = node.targets[0] if node.targets else None
            value = node.value
        if isinstance(target, ast.Name) and target.id == 'tool_parsers' and value is not None:
            seg = ast.get_source_segment(source, value)
            if seg and 'None' not in seg:
                expr_code = seg
                break

if not expr_code:
    print("FAIL: could not find tool_parsers list-of-parsers assignment in method")
    sys.exit(0)

# Fake parser factory that creates distinct objects with mutable state
class FakeParser:
    def __init__(self, tokenizer=None, tools=None):
        self.buffer = []  # mutable state to test independence

class FakeParserFactory:
    def __call__(self, tokenizer=None, tools=None):
        return FakeParser(tokenizer, tools)

class FakeSelf:
    tool_parser = FakeParserFactory()

num_choices = 3
env = {
    'num_choices': num_choices,
    'self': FakeSelf(),
    'tokenizer': None,
    'request': type('R', (), {'tools': []})(),
    'copy': copy,
    'list': list,
    'range': range,
    '__builtins__': __builtins__,
}

try:
    result = eval(expr_code, env)
except Exception as e:
    print(f"FAIL: expression eval error: {e}")
    sys.exit(0)

ok = True

# Must produce a list of exactly num_choices elements
if not isinstance(result, list) or len(result) != num_choices:
    print(f"FAIL: expected list of length {num_choices}, got {type(result).__name__} len={len(result) if isinstance(result, list) else 'N/A'}")
    sys.exit(0)

# Identity check: each parser must be a distinct object
for i in range(num_choices):
    for j in range(i + 1, num_choices):
        if result[i] is result[j]:
            print(f"FAIL: tool_parsers[{i}] is tool_parsers[{j}] (shared reference)")
            ok = False

# Mutation check: mutating one parser's state must not affect others
result[0].buffer.append("token_from_choice_0")
for i in range(1, num_choices):
    if "token_from_choice_0" in result[i].buffer:
        print(f"FAIL: mutating parser[0].buffer affected parser[{i}]")
        ok = False

print("OK" if ok else "FAIL")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.30)")
    echo "  +0.30"
fi
echo ""

########################################
# REGRESSION: Method preserved with substantial body
########################################
# [pr_diff] (0.10): chat_completion_stream_generator must exist and not be a stub
echo "--- CHECK: method preserved with substantial body (0.10) ---"
RESULT=$(python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'chat_completion_stream_generator':
        # Count meaningful statements (reject stubs)
        stmt_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign,
                                   ast.For, ast.AsyncFor, ast.While, ast.If,
                                   ast.With, ast.AsyncWith, ast.Return,
                                   ast.Yield, ast.YieldFrom, ast.Try)):
                stmt_count += 1
        if stmt_count >= 20:
            print("OK")
        else:
            print(f"FAIL: method body too small ({stmt_count} statements, expected >=20)")
        sys.exit(0)

print("FAIL: chat_completion_stream_generator not found")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# REGRESSION: File not truncated
########################################
# [pr_diff] (0.10): Key sibling methods still present
echo "--- CHECK: file not truncated (0.10) ---"
RESULT=$(python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    tree = ast.parse(f.read())

expected = {'create_chat_completion', 'chat_completion_stream_generator', 'chat_completion_full_generator'}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in expected:
        found.add(node.name)

missing = expected - found
if missing:
    for m in sorted(missing):
        print(f"MISSING: {m}")
    print("FAIL")
else:
    print("OK")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# STRUCTURAL: Anti-stub markers
########################################
# [pr_diff] (0.10): No stubs or placeholders in target file
echo "--- CHECK: no stub markers (0.10) ---"
RESULT=$(python3 << 'PYEOF'
import sys

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    lines = f.readlines()

stubs = ['NotImplementedError', 'FIXME', 'HACK', '# stub', '# placeholder']
issues = []
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#'):
        continue
    for stub in stubs:
        if stub in stripped:
            issues.append(f"  Line {i}: found '{stub}'")

if issues:
    for issue in issues[:5]:
        print(issue)
    print("FAIL")
else:
    print("OK")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# REGRESSION: Sibling initializations preserved
########################################
# [pr_diff] (0.05): Non-mutable sibling vars still assigned in the method
echo "--- CHECK: sibling initializations preserved (0.05) ---"
RESULT=$(python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Find the streaming method
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'chat_completion_stream_generator':
        method_node = node
        break

if not method_node:
    print("FAIL: method not found")
    sys.exit(0)

# Check for sibling variable assignments within the method (AST, not string search)
needed = {'added_content_delta_arr', 'reasoning_end_arr'}
found = set()
for node in ast.walk(method_node):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        if isinstance(node, ast.AnnAssign):
            t = node.target
        else:
            t = node.targets[0] if node.targets else None
        if isinstance(t, ast.Name) and t.id in needed:
            found.add(t.id)

missing = needed - found
if missing:
    for m in sorted(missing):
        print(f"MISSING assignment: {m}")
    print("FAIL")
else:
    print("OK")
PYEOF
)
echo "$RESULT"
if echo "$RESULT" | grep -q "^OK$"; then
    REWARD=$(python3 -c "print($REWARD + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
FINAL=$(python3 -c "print(f'{float($REWARD):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$REWARD')
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.65), 4),
    'regression': round(min(max(score - 0.65, 0), 0.20), 4),
    'structural': round(min(max(score - 0.85, 0), 0.15), 4),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
