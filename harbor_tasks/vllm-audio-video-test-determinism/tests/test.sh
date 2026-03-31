#!/usr/bin/env bash
set +e

SCORE=0
TARGET="/workspace/vllm/tests/entrypoints/openai/chat_completion/test_audio_in_video.py"

echo "=== vllm-audio-video-test-determinism ==="
echo ""

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): File must be valid Python
echo "--- GATE: Python syntax check ---"
if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$TARGET').read())
    sys.exit(0)
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"; then
    echo "GATE FAILED: syntax error in test file"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"
echo ""

########################################
# BEHAVIORAL: Core fix verification
# (AST-based because tests require GPU vLLM server with Qwen2.5-Omni-3B)
########################################

# [pr_diff] (0.30): Both flaky test functions set temperature=0.0 for deterministic output
# This is THE core fix — without it, finish_reason is non-deterministic.
echo "--- CHECK: temperature=0.0 in both flaky test functions ---"
TEMP_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
found = {name: False for name in targets}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                for kw in child.keywords:
                    if kw.arg == 'temperature':
                        if isinstance(kw.value, ast.Constant) and kw.value.value == 0.0:
                            found[node.name] = True
                    # Also accept temperature passed via extra_body or **kwargs dict
                    if kw.arg is None and isinstance(kw.value, ast.Dict):
                        for k, v in zip(kw.value.keys, kw.value.values):
                            if isinstance(k, ast.Constant) and k.value == 'temperature':
                                if isinstance(v, ast.Constant) and v.value == 0.0:
                                    found[node.name] = True

for name, ok in found.items():
    status = 'PASS' if ok else 'FAIL'
    print(f'  {name}: {status}')

if all(found.values()):
    print('OK')
else:
    print('FAIL')
" 2>&1)
echo "$TEMP_RESULT"
if echo "$TEMP_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.30)")
    echo "  +0.30"
fi
echo ""

# [pr_diff] (0.20): Both flaky test functions use max_tokens <= 8 to force length cutoff
# Reducing from 16 ensures model can't complete naturally within budget.
echo "--- CHECK: max_tokens reduced (<=8) in both flaky test functions ---"
MAXTOK_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
found = {name: False for name in targets}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                for kw in child.keywords:
                    # Accept both max_tokens and max_completion_tokens
                    if kw.arg in ('max_tokens', 'max_completion_tokens'):
                        if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)) and kw.value.value <= 8:
                            found[node.name] = True

for name, ok in found.items():
    status = 'PASS' if ok else 'FAIL'
    print(f'  {name}: {status}')

if all(found.values()):
    print('OK')
else:
    print('FAIL')
" 2>&1)
echo "$MAXTOK_RESULT"
if echo "$MAXTOK_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    echo "  +0.20"
fi
echo ""

########################################
# REGRESSION: Pass-to-pass checks
########################################

# [pr_diff] (0.10): Third test function (interleaved) still exists and is non-trivial
echo "--- CHECK: interleaved test function preserved ---"
P2P_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'test_online_audio_in_video_interleaved':
        # Must have a real body, not just pass/...
        body_stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr)) or
                       (isinstance(s, ast.Expr) and not isinstance(s.value, ast.Constant))]
        if len(body_stmts) >= 3:
            found = True
        else:
            print('  Function exists but body is too small (stub?)')

print('OK' if found else 'FAIL')
" 2>&1)
echo "  test_online_audio_in_video_interleaved: $P2P_RESULT"
if echo "$P2P_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.10): Original assertions preserved in both flaky test functions
# The tests must still assert finish_reason == "length" and len(choices) == 1
echo "--- CHECK: original assertions preserved ---"
ASSERT_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
found_finish = {name: False for name in targets}
found_choices = {name: False for name in targets}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                cmp = child.test
                if isinstance(cmp, ast.Compare):
                    left_dump = ast.dump(cmp.left)
                    # finish_reason == 'length'
                    if 'finish_reason' in left_dump:
                        for comp in cmp.comparators:
                            if isinstance(comp, ast.Constant) and comp.value == 'length':
                                found_finish[node.name] = True
                    # len(choices) == 1
                    if 'choices' in left_dump:
                        found_choices[node.name] = True

all_ok = all(found_finish.values()) and all(found_choices.values())
for name in targets:
    fr = 'PASS' if found_finish[name] else 'FAIL'
    ch = 'PASS' if found_choices[name] else 'FAIL'
    print(f'  {name}: finish_reason={fr}, choices_len={ch}')

print('OK' if all_ok else 'FAIL')
" 2>&1)
echo "$ASSERT_RESULT"
if echo "$ASSERT_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# STRUCTURAL: Anti-stub / completeness
########################################

# [pr_diff] (0.15): Both flaky test functions have substantial bodies (not stubs)
# Must have API call with model name, messages, mm_processor_kwargs, and loop
echo "--- CHECK: test functions are not stubs ---"
DEPTH_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    source = f.read()
    tree = ast.parse(source)

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
results = {}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        # Count meaningful statements (excluding pass, docstrings, bare ellipsis)
        meaningful = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                   ast.Assert, ast.Return, ast.For, ast.AsyncFor,
                                   ast.AsyncWith, ast.With)):
                meaningful += 1
            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                meaningful += 1
            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Await):
                meaningful += 1

        # Check for key elements: loop, await call, assert
        has_loop = any(isinstance(c, (ast.For, ast.AsyncFor)) for c in ast.walk(node))
        has_await = any(isinstance(c, ast.Await) for c in ast.walk(node))
        has_assert = any(isinstance(c, ast.Assert) for c in ast.walk(node))

        ok = meaningful >= 8 and has_loop and has_await and has_assert
        results[node.name] = (ok, meaningful, has_loop, has_await, has_assert)

for name in targets:
    if name in results:
        ok, n, loop, aw, asr = results[name]
        status = 'PASS' if ok else 'FAIL'
        print(f'  {name}: {status} (stmts={n}, loop={loop}, await={aw}, assert={asr})')
    else:
        print(f'  {name}: FAIL (function not found)')

print('OK' if all(r[0] for r in results.values()) else 'FAIL')
" 2>&1)
echo "$DEPTH_RESULT"
if echo "$DEPTH_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  +0.15"
fi
echo ""

# [pr_diff] (0.10): mm_processor_kwargs with use_audio_in_video preserved in both functions
# This is the key multimodal config that makes these tests test audio-in-video
echo "--- CHECK: mm_processor_kwargs preserved ---"
MM_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
found = {name: False for name in targets}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        src = ast.dump(node)
        # Check for mm_processor_kwargs reference anywhere in function body
        if 'mm_processor_kwargs' in src and 'use_audio_in_video' in src:
            found[node.name] = True

for name, ok in found.items():
    status = 'PASS' if ok else 'FAIL'
    print(f'  {name}: {status}')

print('OK' if all(found.values()) else 'FAIL')
" 2>&1)
echo "$MM_RESULT"
if echo "$MM_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.05): Some form of debug output added to both flaky test functions
# Accept print(), logging.*, or any call that references finish_reason
echo "--- CHECK: debug output in both flaky functions ---"
DEBUG_RESULT=$(python3 -c "
import ast

with open('$TARGET') as f:
    source = f.read()
    tree = ast.parse(source)

targets = ['test_online_audio_in_video', 'test_online_audio_in_video_multi_videos']
found = {name: False for name in targets}

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name in targets:
        # Get source lines for this function
        func_lines = source.splitlines()[node.lineno-1:node.end_lineno]
        func_src = '\n'.join(func_lines)
        # Accept any form of debug output that mentions finish_reason or content
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_dump = ast.dump(child)
                func_name = ''
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    func_name = child.func.attr
                # Accept print, logging.debug/info/warning, logger.debug/info, etc.
                if func_name in ('print', 'debug', 'info', 'warning', 'log'):
                    if 'finish_reason' in call_dump or 'content' in call_dump:
                        found[node.name] = True
                        break

for name, ok in found.items():
    status = 'PASS' if ok else 'FAIL'
    print(f'  {name}: {status}')

print('OK' if all(found.values()) else 'FAIL')
" 2>&1)
echo "$DEBUG_RESULT"
if echo "$DEBUG_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
FINAL=$(python3 -c "print(f'{float($SCORE):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
# behavioral = temperature + max_tokens = 0.50
# regression = interleaved + assertions = 0.20
# structural = anti-stub + mm_kwargs + debug = 0.30
behavioral = min(score, 0.50)
regression = min(max(score - 0.50, 0), 0.20)
structural = min(max(score - 0.70, 0), 0.30)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
