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

MPC="src/bun.js/bindings/webcore/MessagePortChannel.cpp"
JAC="src/bun.js/bindings/webcore/JSAbortController.cpp"
BCC="src/bun.js/bindings/webcore/BroadcastChannel.cpp"
ELM_CPP="src/bun.js/bindings/webcore/EventListenerMap.cpp"
ELM_H="src/bun.js/bindings/webcore/EventListenerMap.h"

##############################################################################
# Shared: C++ comment stripper (removes // and /* */ comments before analysis)
##############################################################################
cat > /tmp/strip_cpp_comments.py << 'PYEOF'
import re, sys

def strip_comments(code):
    """Remove C/C++ comments, preserving string literals."""
    result = []
    i = 0
    in_string = None
    while i < len(code):
        c = code[i]
        # Track string literals to avoid stripping inside them
        if in_string:
            result.append(c)
            if c == '\\' and i + 1 < len(code):
                result.append(code[i+1])
                i += 2
                continue
            if c == in_string:
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            result.append(c)
            i += 1
            continue
        # Line comment
        if c == '/' and i + 1 < len(code) and code[i+1] == '/':
            # Skip to end of line
            while i < len(code) and code[i] != '\n':
                i += 1
            continue
        # Block comment
        if c == '/' and i + 1 < len(code) and code[i+1] == '*':
            i += 2
            while i + 1 < len(code) and not (code[i] == '*' and code[i+1] == '/'):
                i += 1
            i += 2
            continue
        result.append(c)
        i += 1
    return ''.join(result)

if __name__ == '__main__':
    print(strip_comments(open(sys.argv[1]).read()))
PYEOF

##############################################################################
# GATE: All five source files must exist and be non-empty
##############################################################################
# [pr_diff] (gate): Source files must exist
for f in "$MPC" "$JAC" "$BCC" "$ELM_CPP" "$ELM_H"; do
    if [ ! -s "$f" ]; then
        echo "GATE FAILED: $f missing or empty"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done

##############################################################################
# BEHAVIORAL: Fail-to-pass checks (0.65 total)
# WHY STRUCTURAL: C++ code requires the full bun build system (Zig compiler,
# JavaScriptCore, cmake, etc.) — cannot be compiled/run in test container.
# All checks strip comments first to prevent comment-injection gaming.
##############################################################################

# [pr_diff] (0.15): MessagePortChannel::postMessageToRemote must check
# m_isClosed before appending to m_pendingMessages.
add_total 0.15
CLOSED_CHECK=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/MessagePortChannel.cpp").read())
# Find postMessageToRemote function body
fn = re.search(r'postMessageToRemote[^{]*\{(.*?)^\}', text, re.DOTALL | re.MULTILINE)
if fn:
    body = fn.group(1)
    closed_pos = body.find('m_isClosed')
    append_pos = body.find('m_pendingMessages')
    if closed_pos >= 0 and append_pos >= 0 and closed_pos < append_pos:
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$CLOSED_CHECK" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: postMessageToRemote checks m_isClosed before queuing"
else
    echo "FAIL [0.15]: postMessageToRemote does not guard against closed ports"
fi

# [pr_diff] (0.10): The m_isClosed check must cause early return (false)
# to prevent message from being queued to a closed port.
add_total 0.10
EARLY_RETURN=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/MessagePortChannel.cpp").read())
fn = re.search(r'postMessageToRemote[^{]*\{(.*?)^\}', text, re.DOTALL | re.MULTILINE)
if fn:
    body = fn.group(1)
    # Accept m_isClosed[...] followed eventually by return false (any index expr)
    if re.search(r'm_isClosed\s*\[.*?\].*?return\s+false', body, re.DOTALL):
        print('PASS')
    # Also accept: if (m_isClosed...) return false without array indexing
    # (e.g., a bool member check)
    elif re.search(r'm_isClosed\b.*?return\s+false', body, re.DOTALL):
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$EARLY_RETURN" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: m_isClosed check returns false to drop the message"
else
    echo "FAIL [0.10]: m_isClosed check does not return false"
fi

# [pr_diff] (0.15): JSAbortController::visitChildrenImpl must visit
# signal().reason() so it survives GC.
add_total 0.15
VISIT_REASON=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/JSAbortController.cpp").read())
fn = re.search(r'visitChildrenImpl[^{]*\{(.*?)^\}', text, re.DOTALL | re.MULTILINE)
if fn:
    body = fn.group(1)
    # Pattern 1: signal().reason().visit(visitor) — standard JSC GC visit
    if re.search(r'signal\(\)\s*\.\s*reason\(\)\s*\.\s*visit\s*\(', body):
        print('PASS')
    # Pattern 2: reason obtained via signal, then visited (local var pattern)
    # e.g., auto reason = wrapped().signal().reason(); reason.visit(visitor);
    elif re.search(r'signal\(\)', body) and re.search(r'reason\(\)', body) and re.search(r'\.visit\s*\(', body):
        print('PASS')
    # Pattern 3: visitor.append style (for WriteBarrier members)
    # e.g., visitor.append(thisObject->wrapped().signal().reason())
    elif re.search(r'signal\(\)', body) and re.search(r'reason\(\)', body) and re.search(r'visitor\s*\.\s*append', body):
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$VISIT_REASON" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: visitChildrenImpl visits signal().reason()"
else
    echo "FAIL [0.15]: visitChildrenImpl does not visit signal().reason()"
fi

# [pr_diff] (0.15): BroadcastChannel global map must NOT store raw
# BroadcastChannel* pointers — must use weak/safe pointer wrapper.
add_total 0.15
WEAK_PTR=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/BroadcastChannel.cpp").read())

# Find the allBroadcastChannels() function return type — the map value type
map_decl = re.search(
    r'allBroadcastChannels\(\)[^{]*UncheckedKeyHashMap\s*<\s*BroadcastChannelIdentifier\s*,\s*([^>]+)>',
    text
)
if map_decl:
    val_type = map_decl.group(1).strip()
    # FAIL if raw pointer (with or without spaces around *)
    if re.match(r'^BroadcastChannel\s*\*$', val_type):
        print('FAIL')
    # Must actually wrap BroadcastChannel in something (not just remove the *)
    elif 'BroadcastChannel' in val_type and len(val_type) > len('BroadcastChannel'):
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$WEAK_PTR" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: allBroadcastChannels map uses safe pointer wrapper, not raw pointers"
else
    echo "FAIL [0.15]: allBroadcastChannels map still uses raw BroadcastChannel* pointers"
fi

# [pr_diff] (0.10): EventListenerMap mutator methods must call a thread
# affinity check function before acquiring the lock.
add_total 0.10
THREAD_CHECK=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/EventListenerMap.cpp").read())

mutators = [
    'EventListenerMap::clear',
    'EventListenerMap::replace',
    'EventListenerMap::add',
    'EventListenerMap::remove',
    'EventListenerMap::removeFirstEventListenerCreatedFromMarkup',
]
count = 0
for name in mutators:
    # Find function body: starts after opening {, ends at next top-level function
    pat = re.escape(name) + r'\s*\([^)]*\)\s*\{(.*?)(?=\n(?:void|bool|static)\s|\Z)'
    fn = re.search(pat, text, re.DOTALL)
    if fn:
        body = fn.group(1)
        lock_pos = body.find('Locker')
        if lock_pos < 0:
            lock_pos = len(body)
        pre_lock = body[:lock_pos]
        # Must have a function CALL (with parens) related to thread checking
        # before the Locker — not just a keyword mention
        if re.search(r'(releaseAssert|assertThread|checkThread|threadUID|ThreadUID|threadAffinity|ensureThread|verifyThread)\w*\s*\(', pre_lock):
            count += 1
print('PASS' if count >= 4 else 'FAIL')
PYEOF
)
if [ "$THREAD_CHECK" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: EventListenerMap mutators have thread affinity checks"
else
    echo "FAIL [0.10]: EventListenerMap mutators missing thread affinity checks"
fi

##############################################################################
# REGRESSION: Pass-to-pass — existing code must not be broken (0.10 total)
##############################################################################

# [pr_diff] (0.05): BroadcastChannel constructor must still register in
# allBroadcastChannels map (not removed entirely)
add_total 0.05
STILL_REGISTERS=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/BroadcastChannel.cpp").read())
# Must have an .add() call on allBroadcastChannels (code, not comment)
if 'allBroadcastChannels().add' in text or 'allBroadcastChannels() .add' in text:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$STILL_REGISTERS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: BroadcastChannel constructor still registers in global map"
else
    echo "FAIL [0.05]: BroadcastChannel constructor no longer registers — regression"
fi

# [pr_diff] (0.05): JSAbortController::visitChildrenImpl must still call
# Base::visitChildren and addWebCoreOpaqueRoot
add_total 0.05
P2P_VISIT=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/JSAbortController.cpp").read())
has_base = 'Base::visitChildren' in text
has_root = 'addWebCoreOpaqueRoot' in text
print('PASS' if has_base and has_root else 'FAIL')
PYEOF
)
if [ "$P2P_VISIT" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: visitChildrenImpl retains Base::visitChildren and opaqueRoot"
else
    echo "FAIL [0.05]: visitChildrenImpl lost existing GC traversal calls — regression"
fi

##############################################################################
# STRUCTURAL: EventListenerMap.h must have thread UID member (0.10)
# WHY STRUCTURAL: C++ header cannot be compiled in test container.
##############################################################################

# [pr_diff] (0.05): EventListenerMap class must declare a thread UID
# member variable for per-instance thread affinity tracking.
add_total 0.05
HAS_UID_MEMBER=$(python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/EventListenerMap.h").read())
# Check for an integer/ID member related to thread ownership
# Accept: uint32_t m_threadUID, ThreadIdentifier m_threadId, etc.
if re.search(r'(?:uint\d+_t|ThreadIdentifier|Thread::uid_t)\s+m_thread\w*', text):
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$HAS_UID_MEMBER" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: EventListenerMap.h has thread UID member"
else
    echo "FAIL [0.05]: EventListenerMap.h missing thread UID member"
fi

# [pr_diff] (0.05): EventListenerMap.h thread affinity helper must exempt
# GC threads (check for mayBeGCThread or similar).
add_total 0.05
GC_EXEMPT=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/EventListenerMap.h").read())
# Must reference GC thread exemption in actual code, not just comments
if 'mayBeGCThread' in text or 'isGCThread' in text or 'GCThread' in text:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$GC_EXEMPT" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Thread affinity helper exempts GC threads"
else
    echo "FAIL [0.05]: Thread affinity helper does not exempt GC threads"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.05)
##############################################################################

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:228 @ 639bc43
# Verify that BroadcastChannel.cpp still uses Locker pattern (existing style)
add_total 0.05
STYLE_CHECK=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_cpp_comments import strip_comments

text = strip_comments(open("src/bun.js/bindings/webcore/BroadcastChannel.cpp").read())
# Verify the code still uses the Locker pattern with the broadcast channels lock
# Accept variations: Locker locker { ... }, Locker lock { ... }, etc.
import re
if re.search(r'Locker\s+\w+\s*\{\s*allBroadcastChannelsLock\s*\}', text):
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$STYLE_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: BroadcastChannel.cpp follows existing Locker style"
else
    echo "FAIL [0.05]: BroadcastChannel.cpp deviates from existing Locker style"
fi

##############################################################################
# STYLE RUBRIC: LLM judge (0.10)
##############################################################################
add_total 0.10

##############################################################################
# FINAL SCORE
##############################################################################
DET_SCORE=$SCORE
DET_TOTAL=$TOTAL

# Compute deterministic portion (excluding style rubric weight)
DET_FRAC=$(python3 -c "
det = $DET_SCORE
print(f'{det:.4f}')
")

echo ""
echo "=== DETERMINISTIC SCORE: $DET_SCORE / $(python3 -c "print($DET_TOTAL - 0.10)") ==="

# Write reward (deterministic only when LLM_JUDGE!=1)
echo "$DET_FRAC" > /logs/verifier/reward.txt
python3 -c "
import json
det = $DET_SCORE
behavioral = min(det, 0.65)
regression = max(0, min(det - 0.65, 0.10))
config = max(0, min(det - 0.75, 0.05))
structural = max(0, min(det - 0.80, 0.10))
json.dump({
    'reward': round(det, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
