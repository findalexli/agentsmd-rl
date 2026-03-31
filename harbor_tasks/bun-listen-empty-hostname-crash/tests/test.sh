#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

add() { SCORE=$(python3 -c "print($SCORE + $1)"); }
tot() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd /workspace/bun

ZIG_FILE="src/bun.js/api/bun/socket/Handlers.zig"
TEST_FILE="test/js/bun/net/socket.test.ts"

##############################################################################
# GATE: Source file exists
##############################################################################
# [pr_diff] (gate): Handlers.zig must exist
if [ ! -s "$ZIG_FILE" ]; then
    echo "GATE FAILED: $ZIG_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# FAIL-TO-PASS 1 (0.25): Hostname crashing assertion is removed
# On base commit, bun.assertf(hostname.length() > 0, "truthy bindgen...")
# exists and causes a panic. ANY correct fix must remove/replace this.
# Justification for structural: Zig requires full Bun build toolchain
# (Zig compiler, CMake, JavaScriptCore) — cannot compile in container.
##############################################################################
# [pr_diff] (0.25): Crashing assertf for hostname must be removed
tot 0.25
HOSTNAME_ASSERT=$(python3 << 'PYEOF'
text = open("src/bun.js/api/bun/socket/Handlers.zig").read()

# Find the hostname branch
idx = text.find("generated.hostname.get()")
if idx < 0:
    # Branch might have been restructured — still need the concept
    idx = text.find("hostname.get()")
if idx < 0:
    print("FAIL")
else:
    # Search a generous window (800 chars) for the crashing assert
    window = text[idx:idx+800]
    # The crash pattern: assertf with "truthy bindgen" or assertf checking
    # hostname length > 0 as a hard assertion (any of these = crash still present)
    has_crash = ("assertf" in window and "truthy" in window) or \
                ("assertf" in window and "hostname" in window and "length" in window)
    print("PASS" if not has_crash else "FAIL")
PYEOF
)
if [ "$HOSTNAME_ASSERT" = "PASS" ]; then
    add 0.25
    echo "PASS [0.25]: hostname crashing assertf removed"
else
    echo "FAIL [0.25]: hostname crashing assertf still present"
fi

##############################################################################
# FAIL-TO-PASS 2 (0.20): Unix crashing assertion is removed
# Same pattern — assertf for unix path must be removed.
##############################################################################
# [pr_diff] (0.20): Crashing assertf for unix must be removed
tot 0.20
UNIX_ASSERT=$(python3 << 'PYEOF'
text = open("src/bun.js/api/bun/socket/Handlers.zig").read()

# Find the unix branch — could be unix_ or unix
idx = text.find("generated.unix_.get()")
if idx < 0:
    idx = text.find("generated.unix.get()")
if idx < 0:
    print("FAIL")
else:
    window = text[idx:idx+800]
    has_crash = ("assertf" in window and "truthy" in window) or \
                ("assertf" in window and "unix" in window and "length" in window)
    print("PASS" if not has_crash else "FAIL")
PYEOF
)
if [ "$UNIX_ASSERT" = "PASS" ]; then
    add 0.20
    echo "PASS [0.20]: unix crashing assertf removed"
else
    echo "FAIL [0.20]: unix crashing assertf still present"
fi

##############################################################################
# STRUCTURAL (0.15): Error handling added for empty strings
# The fix must not silently skip — it must return an error to JS.
# Accept any throw/error mechanism: throwInvalidArguments, throwTypeError,
# throwPossiblyInvalidArguments, return.*error, etc.
# Check ONLY in a narrow window around where the assertf WAS, to avoid
# false positives from pre-existing throws elsewhere in the function.
##############################################################################
# [pr_diff] (0.15): Both hostname and unix branches return proper JS errors
tot 0.15
ERROR_HANDLING=$(python3 << 'PYEOF'
text = open("src/bun.js/api/bun/socket/Handlers.zig").read()

def has_error_return(text, start_marker, fallback_marker=None):
    """Check if there's an error return in a tight window after the branch start."""
    idx = text.find(start_marker)
    if idx < 0 and fallback_marker:
        idx = text.find(fallback_marker)
    if idx < 0:
        return False

    # Use a tight window (400 chars) starting right at the branch
    window = text[idx:idx+400].lower()

    # Count error-return indicators — must find a NEW throw near the branch start
    # (not the pre-existing "Missing port" throw which is further down)
    # Look in first 200 chars of the window (close to where assert was)
    near_window = text[idx:idx+200].lower()

    error_patterns = [
        "throwinvalidarguments",
        "throwtypeerror",
        "throwpossiblyinvalidarguments",
        "throw" in near_window and ("empty" in near_window or "hostname" in near_window or "unix" in near_window),
    ]
    # Direct pattern matches (case-insensitive)
    has_throw = any(p in near_window for p in [
        "throwinvalidarguments",
        "throwtypeerror",
        "throwpossiblyinvalidarguments",
    ])
    # Also accept: a throw + descriptive message about empty/invalid
    has_descriptive_throw = ("throw" in near_window and
                            any(w in near_window for w in ["empty", "hostname", "unix", "invalid", "non-empty"]))
    # Also accept: return with error
    has_return_error = "return" in near_window and "error" in near_window

    return has_throw or has_descriptive_throw or has_return_error

hostname_ok = has_error_return(text, "generated.hostname.get()", "hostname.get()")
unix_ok = has_error_return(text, "generated.unix_.get()", "generated.unix.get()")

print("PASS" if hostname_ok and unix_ok else "FAIL")
PYEOF
)
if [ "$ERROR_HANDLING" = "PASS" ]; then
    add 0.15
    echo "PASS [0.15]: both branches return proper JS errors for empty strings"
else
    echo "FAIL [0.15]: missing proper error return in one or both branches"
fi

##############################################################################
# BEHAVIORAL (0.10): Run a JS snippet to verify expected throw behavior
# Uses the installed bun binary. If it correctly throws (not crashes) on
# empty hostname, this confirms the expected error contract.
##############################################################################
# [pr_diff] (0.10): Bun.listen with empty hostname throws, not crashes
tot 0.10
cat > /tmp/test_empty_hostname.js << 'JSEOF'
// Test 1: Bun.listen with array hostname (truthy, coerces to "")
let passed = 0;
try {
    Bun.listen({
        hostname: [],
        port: 0,
        socket: { data() {}, open() {}, close() {} }
    });
} catch (e) {
    // Should get a TypeError, not a crash
    if (e instanceof TypeError || e instanceof Error) {
        passed++;
    }
}

// Test 2: Bun.listen with new String("") hostname
try {
    Bun.listen({
        hostname: new String(""),
        port: 0,
        socket: { data() {}, open() {}, close() {} }
    });
} catch (e) {
    if (e instanceof TypeError || e instanceof Error) {
        passed++;
    }
}

// Need at least 1 test to pass (installed bun may vary)
if (passed >= 1) {
    process.exit(0);
} else {
    process.exit(1);
}
JSEOF
timeout 10 bun run /tmp/test_empty_hostname.js 2>/dev/null
if [ $? -eq 0 ]; then
    add 0.10
    echo "PASS [0.10]: Bun.listen throws on empty hostname (behavioral)"
else
    echo "FAIL [0.10]: Bun.listen did not throw properly on empty hostname"
fi

##############################################################################
# PASS-TO-PASS (0.15): Regression checks
##############################################################################

# [pr_diff] (0.05): SocketConfig with hostname/unix parsing still exists
tot 0.05
SOCKETCONFIG_OK=$(python3 << 'PYEOF'
text = open("src/bun.js/api/bun/socket/Handlers.zig").read()
has_socketconfig = "SocketConfig" in text or "socketConfig" in text
has_hostname_parsing = "hostname_or_unix" in text or "hostname" in text
print("PASS" if has_socketconfig and has_hostname_parsing else "FAIL")
PYEOF
)
if [ "$SOCKETCONFIG_OK" = "PASS" ]; then
    add 0.05
    echo "PASS [0.05]: SocketConfig with hostname parsing preserved"
else
    echo "FAIL [0.05]: SocketConfig or hostname parsing missing"
fi

# [pr_diff] (0.05): Both hostname and unix branches still exist
# (agent didn't delete the branches to "fix" the crash)
tot 0.05
BRANCHES_OK=$(python3 << 'PYEOF'
text = open("src/bun.js/api/bun/socket/Handlers.zig").read()
has_hostname = "generated.hostname.get()" in text or "hostname.get()" in text
has_unix = "generated.unix_.get()" in text or "generated.unix.get()" in text
print("PASS" if has_hostname and has_unix else "FAIL")
PYEOF
)
if [ "$BRANCHES_OK" = "PASS" ]; then
    add 0.05
    echo "PASS [0.05]: hostname and unix branches preserved"
else
    echo "FAIL [0.05]: hostname or unix branch was deleted"
fi

# [pr_diff] (0.05): Test file preserved (not truncated or deleted)
tot 0.05
if [ -f "$TEST_FILE" ]; then
    LINE_COUNT=$(wc -l < "$TEST_FILE")
    if [ "$LINE_COUNT" -gt 500 ]; then
        add 0.05
        echo "PASS [0.05]: test file preserved ($LINE_COUNT lines)"
    else
        echo "FAIL [0.05]: test file suspiciously small ($LINE_COUNT lines)"
    fi
else
    echo "FAIL [0.05]: test file missing"
fi

##############################################################################
# ANTI-STUB (0.05): Zig file has substantial content
##############################################################################
# [pr_diff] (0.05): Handlers.zig must not be stubbed out
tot 0.05
ZIG_LINES=$(wc -l < "$ZIG_FILE")
if [ "$ZIG_LINES" -gt 200 ]; then
    add 0.05
    echo "PASS [0.05]: anti-stub Handlers.zig ($ZIG_LINES lines)"
else
    echo "FAIL [0.05]: Handlers.zig suspiciously small ($ZIG_LINES lines)"
fi

##############################################################################
# CONFIG-DERIVED (0.05): Agent config rules
##############################################################################
# [agent_config] (0.05): "Always use port: 0 in tests" — CLAUDE.md:97
tot 0.05
if [ -f "$TEST_FILE" ]; then
    PORT_CHECK=$(python3 << 'PYEOF'
import re
text = open("test/js/bun/net/socket.test.ts").read()
lines = text.split("\n")
# Check the last 100 lines (where new tests would be added)
tail = "\n".join(lines[-100:])
# Look for hardcoded non-zero ports in Bun.listen/connect calls
has_hardcoded = bool(re.search(r'port:\s*(?!0\b)\d+', tail))
print("FAIL" if has_hardcoded else "PASS")
PYEOF
    )
    if [ "$PORT_CHECK" = "PASS" ]; then
        add 0.05
        echo "PASS [0.05]: no hardcoded ports in new tests (CLAUDE.md:97)"
    else
        echo "FAIL [0.05]: hardcoded port found in new tests"
    fi
else
    echo "FAIL [0.05]: test file missing"
fi

##############################################################################
# Final scoring
##############################################################################
FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Total: $FINAL / $TOTAL"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
data = {
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(max(min(score - 0.70, 0.15), 0.0), 4),
    'config': round(max(min(score - 0.85, 0.05), 0.0), 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
