#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun
TARGET="src/bun.js/bindings/BunPlugin.cpp"

##############################################################################
# GATE: Target file and function exist
##############################################################################
# [pr_diff] (gate): BunPlugin.cpp must contain JSMock__jsModuleMock
if [ ! -f "$TARGET" ]; then
    echo "GATE FAILED: $TARGET not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

python3 -c "
code = open('$TARGET').read()
if 'JSMock__jsModuleMock' not in code:
    print('GATE FAILED: JSMock__jsModuleMock not found')
    exit(1)
print('GATE PASS: function exists')
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: JSMock__jsModuleMock not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL P2P: Verify expected mock.module behavior via installed bun (0.15)
# These run on the installed bun binary (latest release with fix).
# They confirm the EXPECTED behavior, not the agent's source changes.
##############################################################################

mkdir -p /tmp/bun-mock-tests

# [pr_diff] (0.10): mock.module(nonString) throws TypeError (not crash)
cat > /tmp/bun-mock-tests/nonstring.test.ts << 'TESTEOF'
import { test, expect, mock } from "bun:test";

test("mock.module throws TypeError for number arg", () => {
  expect(() => mock.module(123 as any, () => ({}))).toThrow(TypeError);
});

test("mock.module throws TypeError for object arg", () => {
  expect(() => mock.module({} as any, () => ({}))).toThrow(TypeError);
});

test("mock.module throws TypeError for symbol arg", () => {
  expect(() => mock.module(Symbol("x") as any, () => ({}))).toThrow(TypeError);
});
TESTEOF

cd /tmp/bun-mock-tests
timeout 30 bun test nonstring.test.ts 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): mock.module throws TypeError for non-string args"
else
    add_total 0.10
    echo "FAIL (0.10): mock.module throws TypeError for non-string args"
fi

# [pr_diff] (0.05): mock.module with valid string does not throw (P2P)
cat > /tmp/bun-mock-tests/string_ok.test.ts << 'TESTEOF'
import { test, expect, mock } from "bun:test";

test("mock.module works with string first arg", () => {
  expect(() => mock.module("some-test-module", () => ({ default: 42 }))).not.toThrow();
});
TESTEOF

timeout 30 bun test string_ok.test.ts 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): mock.module accepts valid string arg"
else
    add_total 0.05
    echo "FAIL (0.05): mock.module accepts valid string arg"
fi
cd /workspace/bun

##############################################################################
# STRUCTURAL F2P-EQUIVALENT: Source code fix validation (0.45 total)
# WHY STRUCTURAL: Bun is compiled Zig/C++ — requires Zig + WebKit/JSC + CMake
# toolchain not available in container. Cannot compile and run agent's changes.
# All source analysis strips C++ comments first to prevent comment injection.
##############################################################################

# [pr_diff] (0.30): Type validation guard added before toString() call
# Accepts: isString, isCell, jsTypeInfo, type()==, toStringOrNull, tryGetString
python3 -c "
import re, sys

code = open('$TARGET').read()
# Strip single-line and multi-line C++ comments
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

fn_match = re.search(r'JSMock__jsModuleMock', stripped)
if not fn_match:
    sys.exit(1)

fn_body = stripped[fn_match.start():fn_match.start()+3000]

# Find toString call position
to_string_pos = fn_body.find('.toString(')
ts_alt = fn_body.find('toWTFString(')
if to_string_pos == -1 and ts_alt == -1:
    # toString was removed/replaced entirely — check for safe alternatives
    safe_alts = ['toStringOrNull', 'tryGetString', 'getString(']
    if any(alt in fn_body for alt in safe_alts):
        print('PASS: toString replaced with safe alternative')
        sys.exit(0)
    print('FAIL: toString not found and no safe alternative')
    sys.exit(1)

checkpoint = min(p for p in [to_string_pos, ts_alt] if p > 0)
before = fn_body[:checkpoint]

# Accept ANY type-validation pattern before the toString call
type_guard_patterns = [
    r'isString\s*\(',              # .isString()
    r'isCell\s*\(',                # .isCell()
    r'jsTypeInfo\s*\(',            # jsTypeInfo() type check
    r'JSType::\w*String',          # JSType::StringType
    r'\.type\s*\(\s*\)\s*[!=]=',   # .type() == / !=
    r'isObject\s*\(',              # reject objects
    r'isSymbol\s*\(',              # reject symbols
    r'isNumber\s*\(',              # reject numbers
    r'isUndefinedOrNull\s*\(',     # reject null/undefined
    r'toStringOrNull',             # safe conversion
    r'tryGetString',               # safe accessor
]

found = any(re.search(p, before) for p in type_guard_patterns)
if not found:
    print('FAIL: No type validation found before toString()')
    sys.exit(1)

print('PASS: Type validation guard found before toString()')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.30
    echo "PASS (0.30): Type validation guard before toString (comment-stripped)"
else
    add_total 0.30
    echo "FAIL (0.30): Type validation guard before toString (comment-stripped)"
fi

# [pr_diff] (0.15): Error path exists — throw + return for failed type check
# Accepts: throwException, createTypeError, createError, throwTypeError, etc.
python3 -c "
import re, sys

code = open('$TARGET').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

fn_match = re.search(r'JSMock__jsModuleMock', stripped)
fn_body = stripped[fn_match.start():fn_match.start()+3000]

# Accept any error-throwing pattern
error_patterns = [
    r'throwException',
    r'createTypeError',
    r'createError',
    r'throwTypeError',
    r'TypeError',
    r'createRangeError',
    r'throwSyntaxError',
]

found_error = any(re.search(p, fn_body) for p in error_patterns)
if not found_error:
    print('FAIL: No error thrown for invalid argument type')
    sys.exit(1)

# Check for early return after error path
if not re.search(r'return\s*[\{\};]', fn_body):
    # Also accept return with encoded value
    if not re.search(r'return\s+JSValue', fn_body) and not re.search(r'return\s+js', fn_body):
        print('FAIL: No return/early-exit after error')
        sys.exit(1)

print('PASS: Error handling with early return')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.15
    echo "PASS (0.15): Error handling for type check failure (comment-stripped)"
else
    add_total 0.15
    echo "FAIL (0.15): Error handling for type check failure (comment-stripped)"
fi

##############################################################################
# REGRESSION: Existing behavior preserved (0.10)
##############################################################################

# [pr_diff] (0.10): Existing argumentCount and isEmpty guards not removed
python3 -c "
import re, sys

code = open('$TARGET').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

fn_match = re.search(r'JSMock__jsModuleMock', stripped)
fn_body = stripped[fn_match.start():fn_match.start()+3000]

if 'argumentCount()' not in fn_body:
    print('FAIL: argumentCount check was removed')
    sys.exit(1)
if 'isEmpty()' not in fn_body:
    print('FAIL: isEmpty check was removed')
    sys.exit(1)

print('PASS: Existing validation guards preserved')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): Existing guards preserved"
else
    add_total 0.10
    echo "FAIL (0.10): Existing guards preserved"
fi

##############################################################################
# ANTI-STUB: Verify meaningful source changes (0.15)
##############################################################################

# [pr_diff] (0.10): Source file was actually modified with real code (not just comments)
python3 -c "
import subprocess, sys

result = subprocess.run(
    ['git', 'diff', '--no-color', '--', '$TARGET'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
diff = result.stdout

# Count added lines that are not blank, not comments, not just whitespace
added = 0
for line in diff.splitlines():
    if not line.startswith('+'):
        continue
    if line.startswith('+++'):
        continue
    content = line[1:].strip()
    if not content:
        continue
    if content.startswith('//') or content.startswith('/*') or content.startswith('*'):
        continue
    added += 1

if added < 3:
    print(f'FAIL: Only {added} meaningful lines added (need >=3)')
    sys.exit(1)

print(f'PASS: {added} meaningful lines of code added')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): Meaningful source changes detected"
else
    add_total 0.10
    echo "FAIL (0.10): Meaningful source changes detected"
fi

# [pr_diff] (0.05): Type guard is inside a conditional (if/else), not floating code
python3 -c "
import re, sys

code = open('$TARGET').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

fn_match = re.search(r'JSMock__jsModuleMock', stripped)
fn_body = stripped[fn_match.start():fn_match.start()+3000]

# Find the type guard
guard_patterns = [
    r'isString\s*\(', r'isCell\s*\(', r'jsTypeInfo\s*\(',
    r'toStringOrNull', r'tryGetString',
]
guard_pos = -1
for p in guard_patterns:
    m = re.search(p, fn_body)
    if m:
        guard_pos = m.start()
        break

if guard_pos == -1:
    sys.exit(1)

# Check that the guard is inside an if-statement
preceding = fn_body[max(0, guard_pos - 120):guard_pos]
if 'if' not in preceding and 'if' not in fn_body[guard_pos:guard_pos+20]:
    # Also accept: ternary or direct use as condition
    if '?' not in fn_body[guard_pos:guard_pos+60] and 'while' not in preceding:
        print('FAIL: Type guard not inside a conditional')
        sys.exit(1)

print('PASS: Type guard inside conditional')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): Type guard in conditional block"
else
    add_total 0.05
    echo "FAIL (0.05): Type guard in conditional block"
fi

##############################################################################
# CONFIG: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): Descriptive error message — CLAUDE.md:228 @ e94c3035
python3 -c "
import re, sys

code = open('$TARGET').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

fn_match = re.search(r'JSMock__jsModuleMock', stripped)
fn_body = stripped[fn_match.start():fn_match.start()+3000]

# Check that error message mentions module or string (any string literal nearby error)
# Look for quoted strings near the error-creation site
error_region_match = re.search(r'create(?:Type|Range)?Error|throwTypeError|throwException', fn_body)
if not error_region_match:
    sys.exit(1)

region = fn_body[error_region_match.start():error_region_match.start()+300]
# Find string literals in the region
strings = re.findall(r'\"([^\"]+)\"', region)
joined = ' '.join(strings).lower()
if 'module' in joined or 'string' in joined or 'specifier' in joined or 'argument' in joined:
    print('PASS: Error message is descriptive')
else:
    print('FAIL: Error message not descriptive')
    sys.exit(1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): Descriptive error message"
else
    add_total 0.05
    echo "FAIL (0.05): Descriptive error message"
fi

# [agent_config] (0.05): Test file added for mock.module — CLAUDE.md:226 @ e94c3035
python3 -c "
import os, sys, glob

test_dirs = ['test/', 'tests/']
found = False
for td in test_dirs:
    for root, dirs, files in os.walk(td):
        for f in files:
            if not (f.endswith('.test.ts') or f.endswith('.test.js') or f.endswith('.test.mjs')):
                continue
            path = os.path.join(root, f)
            try:
                content = open(path).read()
            except:
                continue
            if 'mock.module' in content and ('TypeError' in content or 'throw' in content.lower() or 'non-string' in content.lower() or 'not a string' in content.lower()):
                found = True
                print(f'PASS: Found test: {path}')
                break
        if found:
            break
    if found:
        break

if not found:
    print('FAIL: No test file for mock.module non-string case')
    sys.exit(1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): Test file for mock.module non-string exists"
else
    add_total 0.05
    echo "FAIL (0.05): Test file for mock.module non-string exists"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo "Total: $SCORE / $TOTAL"

REWARD=$(python3 -c "
total = $TOTAL
score = $SCORE
reward = round(score / total, 4) if total > 0 else 0.0
print(reward)
")

echo "$REWARD" > /logs/verifier/reward.txt

# Compute per-category scores for reward.json
python3 -c "
import json
reward = $REWARD
score = $SCORE
# behavioral = P2P bun tests (0.15 max)
behavioral = min(0.15, score)
remaining = max(0, score - 0.15)
# structural f2p-equivalent (0.45 max)
structural = min(0.45, remaining)
remaining = max(0, remaining - 0.45)
# regression (0.10 max)
regression = min(0.10, remaining)
remaining = max(0, remaining - 0.10)
# config (0.10 max)
config = min(0.10, remaining)
print(json.dumps({
    'reward': reward,
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
