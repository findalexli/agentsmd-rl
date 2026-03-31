#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[f2p_dispatch]=0.30
WEIGHTS[f2p_submit]=0.25
WEIGHTS[f2p_blocks]=0.25
WEIGHTS[p2p_types]=0.10
WEIGHTS[antistub]=0.10

for key in f2p_dispatch f2p_submit f2p_blocks p2p_types antistub; do
    RESULTS[$key]=0
done

SUBMIT_TS="/workspace/gradio/client/js/src/utils/submit.ts"
DEPENDENCY_TS="/workspace/gradio/js/core/src/dependency.ts"
BLOCKS_SVELTE="/workspace/gradio/js/core/src/Blocks.svelte"

# ---------- GATE: All files exist ----------
for f in "$SUBMIT_TS" "$DEPENDENCY_TS" "$BLOCKS_SVELTE"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f not found"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS: all target files exist"

# ---------- FAIL-TO-PASS 1 (30%): DependencyManager prevents event cascade ----------
# Source: instruction.md - "connection_lost flag stops event dispatching"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/gradio/js/core/src/dependency.ts") as f:
    content = f.read()

# Parse TypeScript-ish to find the DependencyManager class and dispatch method
# We'll use regex since we can't import TS, but we verify actual logic flow

import re

# Find the DependencyManager class
class_match = re.search(r'class\s+DependencyManager[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)', content, re.DOTALL)
if not class_match:
    print("F2P_DISPATCH FAIL: DependencyManager class not found")
    sys.exit(1)

class_body = class_match.group(1)

# Check 1: Has a state flag that tracks connection status
state_patterns = [
    r'\bconnection[_\s]lost\s*[=:]',
    r'\bis[_\s](?:disconnected|offline)\s*[=:]',
    r'\b_connection[_\s](?:lost|error)\s*[=:]',
    r'(?:private|public)\s+\w*connection\w*\s*[=:]',
]
has_state = any(re.search(p, class_body, re.IGNORECASE) for p in state_patterns)

if not has_state:
    print("F2P_DISPATCH FAIL: No connection state tracking found")
    sys.exit(1)

# Check 2: dispatch method checks this state before processing
dispatch_match = re.search(r'(?:async\s+)?dispatch\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)', class_body, re.DOTALL)
if not dispatch_match:
    print("F2P_DISPATCH FAIL: dispatch method not found")
    sys.exit(1)

dispatch_body = dispatch_match.group(1)

# Look for early return when connection is lost
early_return_patterns = [
    r'if\s*\([^)]*(?:connection[_\s]lost|is[_\s](?:disconnected|offline))[^)]*\)\s*return',
    r'if\s*\([^)]*this\.\w*(?:connection|disconnect|offline)[^)]*\)\s*return',
    r'if\s*\(\s*this\.\w+\s*\)\s*return[^;]*(?:connection|disconnect)',
]
has_early_return = any(re.search(p, dispatch_body, re.IGNORECASE) for p in early_return_patterns)

if not has_early_return:
    print("F2P_DISPATCH FAIL: dispatch does not short-circuit on connection loss")
    sys.exit(1)

# Check 3: State is settable (not just a const)
setter_patterns = [
    r'(?:this\.)?\w*(?:connection|disconnect)\w*\s*=\s*(?:true|false)',
    r'set\w*(?:Connection|Disconnect)\w*\([^)]*\)',
]
has_setter = any(re.search(p, class_body, re.IGNORECASE) for p in setter_patterns)

if not has_setter:
    print("F2P_DISPATCH FAIL: Connection state cannot be modified")
    sys.exit(1)

print("F2P_DISPATCH PASS: DependencyManager properly gates dispatch on connection state")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[f2p_dispatch]=1
    echo "TEST f2p_dispatch: PASS"
else
    echo "TEST f2p_dispatch: FAIL"
fi

# ---------- FAIL-TO-PASS 2 (25%): submit.ts detects connection errors ----------
# Source: instruction.md - "Detect BROKEN_CONNECTION_MSG and set broken flag"
python3 << 'PYEOF'
import re
import sys

with open("/workspace/gradio/client/js/src/utils/submit.ts") as f:
    content = f.read()

# Check 1: Must have some way to identify connection errors
connection_markers = [
    r'BROKEN_CONNECTION_MSG',
    r'fetch.*(?:failed|error)',
    r'network[_\s]error',
    r'connection[_\s](?:error|failed|lost)',
]
has_connection_detection = any(re.search(p, content, re.IGNORECASE) for p in connection_markers)

if not has_connection_detection:
    print("F2P_SUBMIT FAIL: No connection error detection found")
    sys.exit(1)

# Check 2: Must emit error events with a marker distinguishing connection errors
# Look for error event emission with some flag/property
error_emit_patterns = [
    r'error\s*:\s*\{[^}]*broken\s*:\s*(?:true|is_connection_error)',
    r'broken\s*:\s*(?:true|false|!!|Boolean)',
    r'type\s*:\s*["\']connection["\']',
    r'(?:emit|dispatch|postMessage)\s*\([^)]*error[^)]*broken',
]
has_broken_flag = any(re.search(p, content, re.IGNORECASE) for p in error_emit_patterns)

# Alternative: Check for error object with connection-specific properties
error_prop_patterns = [
    r'error\s*[=:]\s*\{[^}]*(?:connection|network)',
    r'\{[^}]*status[^}]*connection',
]
has_error_props = any(re.search(p, content, re.IGNORECASE) for p in error_prop_patterns)

if not (has_broken_flag or has_error_props):
    print("F2P_SUBMIT FAIL: Error events do not mark connection errors distinctly")
    sys.exit(1)

# Check 3: Must handle POST failures (not just SSE)
post_patterns = [
    r'fetch\s*\(',
    r'\.post\s*\(',
    r'response\.ok',
    r'\.catch\s*\(',
    r'try\s*\{[^}]*fetch',
]
handles_post = any(re.search(p, content, re.IGNORECASE) for p in post_patterns)

if not handles_post:
    print("F2P_SUBMIT FAIL: No POST request error handling found")
    sys.exit(1)

print("F2P_SUBMIT PASS: submit.ts properly detects and flags connection errors")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[f2p_submit]=1
    echo "TEST f2p_submit: PASS"
else
    echo "TEST f2p_submit: FAIL"
fi

# ---------- FAIL-TO-PASS 3 (25%): Blocks.svelte handles reconnection ----------
# Source: instruction.md - "show single error modal and start reconnection loop"
python3 << 'PYEOF'
import re
import sys

with open("/workspace/gradio/js/core/src/Blocks.svelte") as f:
    content = f.read()

# Check 1: Has connection lost handler function
handler_patterns = [
    r'(?:function|const)\s+\w*(?:connection[_\s]lost|handle[_\s](?:disconnect|error))\w*',
    r'on\w*(?:Connection|Disconnect|Error)\w*\s*[=:]',
    r'handleConnection\w*\s*\(',
]
has_handler = any(re.search(p, content, re.IGNORECASE) for p in handler_patterns)

if not has_handler:
    print("F2P_BLOCKS FAIL: No connection lost handler found")
    sys.exit(1)

# Check 2: Has reconnection mechanism
reconnect_patterns = [
    r'setInterval',
    r'setTimeout.*reconnect',
    r'reconnect\s*\(',
    r'(?:async\s+)?function\s+reconnect',
]
has_reconnect = any(re.search(p, content, re.IGNORECASE) for p in reconnect_patterns)

if not has_reconnect:
    print("F2P_BLOCKS FAIL: No reconnection mechanism found")
    sys.exit(1)

# Check 3: Has health check or reload logic for recovery
recovery_patterns = [
    r'fetch.*health|ping|/',
    r'location\.reload',
    r'window\.location',
    r'reload\s*\(',
    r'server.*(?:back|up|recover)',
]
has_recovery = any(re.search(p, content, re.IGNORECASE) for p in recovery_patterns)

if not has_recovery:
    print("F2P_BLOCKS FAIL: No server recovery detection found")
    sys.exit(1)

# Check 4: Has error modal/showError logic (not just logging)
modal_patterns = [
    r'showError|toast|modal|dialog',
    r'dispatch.*error',
    r'app.*\.\$set',
    r'status.*error',
]
has_modal = any(re.search(p, content, re.IGNORECASE) for p in modal_patterns)

if not has_modal:
    print("F2P_BLOCKS FAIL: No error display mechanism found")
    sys.exit(1)

print("F2P_BLOCKS PASS: Blocks.svelte has proper connection handling and reconnection logic")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[f2p_blocks]=1
    echo "TEST f2p_blocks: PASS"
else
    echo "TEST f2p_blocks: FAIL"
fi

# ---------- PASS-TO-PASS (10%): TypeScript compiles without errors ----------
# Source: repo requirement - fix must not break type checking
if command -v npx &> /dev/null; then
    cd /workspace/gradio

    # Check tsconfig exists
    if [ -f "tsconfig.json" ] || [ -f "js/core/tsconfig.json" ]; then
        # Try type checking the modified files
        npx tsc --noEmit --skipLibCheck js/core/src/dependency.ts 2>/dev/null
        DEP_OK=$?

        npx tsc --noEmit --skipLibCheck client/js/src/utils/submit.ts 2>/dev/null
        SUB_OK=$?

        if [ $DEP_OK -eq 0 ] && [ $SUB_OK -eq 0 ]; then
            RESULTS[p2p_types]=1
            echo "TEST p2p_types: PASS (TypeScript compiles)"
        else
            echo "TEST p2p_types: FAIL (TypeScript errors)"
        fi
    else
        # No type checking available, award points
        RESULTS[p2p_types]=1
        echo "TEST p2p_types: PASS (no tsconfig to check)"
    fi
else
    # No type checking available, award points
    RESULTS[p2p_types]=1
    echo "TEST p2p_types: PASS (npx not available)"
fi

# ---------- Anti-stub check (10%) ----------
# Files must have meaningful implementation (not just comments/strings)
python3 << 'PYEOF'
import re
import sys

files = [
    "/workspace/gradio/client/js/src/utils/submit.ts",
    "/workspace/gradio/js/core/src/dependency.ts",
    "/workspace/gradio/js/core/src/Blocks.svelte"
]

for f in files:
    with open(f) as file:
        content = file.read()

    # Count meaningful code lines (not just comments or string literals)
    lines = content.split('\n')
    meaningful = 0

    for line in lines:
        stripped = line.strip()
        # Skip empty lines, pure comments, and lines that are just string literals
        if not stripped:
            continue
        if stripped.startswith('//') and not stripped.startswith('///'):
            continue
        if stripped.startswith('/*') or stripped.startswith('*'):
            continue
        if re.match(r'^["\'][^"\']*["\']\s*,?\s*$', stripped):
            continue
        meaningful += 1

    if meaningful < 30:
        print(f"ANTISTUB FAIL: {f} has only {meaningful} meaningful lines")
        sys.exit(1)

print("ANTISTUB PASS: All files have substantial implementation")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'f2p_dispatch': ${WEIGHTS[f2p_dispatch]}, 'f2p_submit': ${WEIGHTS[f2p_submit]}, 'f2p_blocks': ${WEIGHTS[f2p_blocks]}, 'p2p_types': ${WEIGHTS[p2p_types]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'f2p_dispatch': ${RESULTS[f2p_dispatch]}, 'f2p_submit': ${RESULTS[f2p_submit]}, 'f2p_blocks': ${RESULTS[f2p_blocks]}, 'p2p_types': ${RESULTS[p2p_types]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  f2p_dispatch    (${WEIGHTS[f2p_dispatch]}): ${RESULTS[f2p_dispatch]}"
echo "  f2p_submit      (${WEIGHTS[f2p_submit]}): ${RESULTS[f2p_submit]}"
echo "  f2p_blocks      (${WEIGHTS[f2p_blocks]}): ${RESULTS[f2p_blocks]}"
echo "  p2p_types       (${WEIGHTS[p2p_types]}): ${RESULTS[p2p_types]}"
echo "  antistub        (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
