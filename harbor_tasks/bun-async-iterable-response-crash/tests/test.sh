#!/usr/bin/env bash
set +e
set -uo pipefail

TOTAL=0
SCORE=0

add_score() {
    SCORE=$(python3 -c "print(round($SCORE + $1, 4))")
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}
add_total() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

cd /workspace/bun

TS_FILE="src/js/builtins/ReadableStream.ts"
INTERNALS_FILE="src/js/builtins/ReadableStreamInternals.ts"
CPP_FILE="src/bun.js/bindings/webcore/ReadableStream.cpp"

##############################################################################
# GATE: Files exist and are non-empty
##############################################################################
# [pr_diff] (gate): Core source files must exist
for f in "$TS_FILE" "$INTERNALS_FILE" "$CPP_FILE"; do
    if [ ! -s "$f" ]; then
        echo "GATE FAILED: $f missing or empty"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done

##############################################################################
# STRUCTURAL: Fail-to-pass equivalent (0.60 total)
# WHY structural: Bun's JS builtins use JSC-specific intrinsics
# ($getByIdDirectPrivate, $isReadableStream, etc.) that cannot be parsed or
# executed by any standard JS engine. C++ requires full Zig/CMake/JSC build.
# All checks are broadened to accept multiple valid fix strategies.
##############################################################################

# [pr_diff] (0.20): readableStreamTo* functions must correctly exclude null
# underlyingSource from the direct-stream path.
# The bug: initializeArrayBufferStream sets underlyingSource to null, but the
# original code uses !== undefined which lets null through.
# Accepts: != null, == null (inverted), !underlyingSource, === null || === undefined,
# == undefined, optional chaining on underlyingSource, or any comparison that
# would exclude both null and undefined.
add_total 0.20
NULL_CHECK=$(python3 << 'PYEOF'
import re

text = open("src/js/builtins/ReadableStream.ts").read()

funcs = ["readableStreamToArray", "readableStreamToText",
         "readableStreamToArrayBuffer", "readableStreamToBytes"]

all_fixed = True
for func in funcs:
    # Extract the function body (up to next function or end)
    pat = r'function\s+' + func + r'\b(.*?)(?=\nfunction\s|\Z)'
    m = re.search(pat, text, re.DOTALL)
    if not m:
        all_fixed = False
        break
    body = m.group(1)

    # Check that the underlyingSource check does NOT use bare !== undefined
    # which is the original bug (lets null through)
    has_bug = bool(re.search(r'underlyingSource\s*!==\s*undefined', body))

    # Accept any of these fix patterns:
    # 1. != null (loose inequality — excludes both null and undefined)
    has_loose_neq_null = bool(re.search(r'underlyingSource\s*!=\s*null', body))
    # 2. == null or === null used in a negation/else branch
    has_eq_null = bool(re.search(r'underlyingSource\s*===?\s*null', body))
    # 3. Truthiness check: if (underlyingSource) or if (!underlyingSource)
    has_truthiness = bool(re.search(r'[(!]\s*underlyingSource\s*[)&|]', body))
    # 4. != undefined (loose — also excludes null)
    has_loose_neq_undef = bool(re.search(r'underlyingSource\s*!=\s*undefined', body))
    # 5. !== null added as additional check
    has_strict_neq_null = bool(re.search(r'underlyingSource\s*!==\s*null', body))
    # 6. typeof check
    has_typeof = bool(re.search(r'typeof\s+underlyingSource\s*[!=]', body))
    # 7. Optional chaining on underlyingSource properties
    has_optional = bool(re.search(r'underlyingSource\?\.\w', body))

    any_fix = (has_loose_neq_null or has_eq_null or has_truthiness or
               has_loose_neq_undef or has_strict_neq_null or has_typeof or
               has_optional)

    if has_bug and not any_fix:
        all_fixed = False
        break
    if not has_bug and not any_fix:
        # The comparison was removed or restructured — also acceptable
        # as long as !== undefined is gone
        pass

print("PASS" if all_fixed else "FAIL")
PYEOF
)
if [ "$NULL_CHECK" = "PASS" ]; then
    add_score 0.20
    echo "PASS [0.20]: underlyingSource checks correctly exclude null"
else
    echo "FAIL [0.20]: underlyingSource checks still let null into direct-stream path"
fi

# [pr_diff] (0.15): onCloseDirectStream must guard against null/undefined sink
# before accessing sink.end().
# Accepts: local var + if-guard, optional chaining (?.end()), try/catch,
# if (this.$sink != null), if (this.$sink), any truthiness/nullish check.
add_total 0.15
CLOSE_GUARD=$(python3 << 'PYEOF'
import re

text = open("src/js/builtins/ReadableStreamInternals.ts").read()

# Find onCloseDirectStream function body
m = re.search(r'function\s+onCloseDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)', text, re.DOTALL)
if not m:
    print("FAIL")
else:
    body = m.group(1)
    # Accept any null-safety pattern for sink:
    # 1. Local variable + guard: var sink = this.$sink; if (!sink)
    has_local_guard = bool(re.search(
        r'(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)', body, re.DOTALL))
    # 2. Direct guard: if (!this.$sink) or if (this.$sink == null) etc.
    has_direct_guard = bool(re.search(
        r'if\s*\(\s*!this\.\$sink\s*\)', body))
    has_null_check = bool(re.search(
        r'if\s*\(\s*this\.\$sink\s*(?:===?\s*(?:null|undefined)|==\s*null)', body))
    has_truthiness = bool(re.search(
        r'if\s*\(\s*this\.\$sink\s*\)', body))
    # 3. Optional chaining: this.$sink?.end()
    has_optional_chain = bool(re.search(r'\.\$sink\?\.\w', body))
    # 4. try/catch around sink access
    has_try = bool(re.search(r'try\s*\{[^}]*\.\$?sink.*?end', body, re.DOTALL))
    # 5. Local var used for .end() (even without explicit guard — safer pattern)
    has_local_end = bool(re.search(
        r'(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink.*?\1\.end', body, re.DOTALL))

    if any([has_local_guard, has_direct_guard, has_null_check, has_truthiness,
            has_optional_chain, has_try, has_local_end]):
        print("PASS")
    else:
        print("FAIL")
PYEOF
)
if [ "$CLOSE_GUARD" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: onCloseDirectStream has null guard for sink"
else
    echo "FAIL [0.15]: onCloseDirectStream missing null guard for sink"
fi

# [pr_diff] (0.15): onFlushDirectStream must guard against null/undefined sink
# before accessing sink.flush(). Same broad acceptance as above.
add_total 0.15
FLUSH_GUARD=$(python3 << 'PYEOF'
import re

text = open("src/js/builtins/ReadableStreamInternals.ts").read()

m = re.search(r'function\s+onFlushDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)', text, re.DOTALL)
if not m:
    print("FAIL")
else:
    body = m.group(1)
    has_local_guard = bool(re.search(
        r'(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)', body, re.DOTALL))
    has_direct_guard = bool(re.search(
        r'if\s*\(\s*!this\.\$sink\s*\)', body))
    has_null_check = bool(re.search(
        r'if\s*\(\s*this\.\$sink\s*(?:===?\s*(?:null|undefined)|==\s*null)', body))
    has_truthiness = bool(re.search(
        r'if\s*\(\s*this\.\$sink\s*\)', body))
    has_optional_chain = bool(re.search(r'\.\$sink\?\.\w', body))
    has_try = bool(re.search(r'try\s*\{[^}]*\.\$?sink.*?flush', body, re.DOTALL))
    has_local_flush = bool(re.search(
        r'(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink.*?\1\.flush', body, re.DOTALL))

    if any([has_local_guard, has_direct_guard, has_null_check, has_truthiness,
            has_optional_chain, has_try, has_local_flush]):
        print("PASS")
    else:
        print("FAIL")
PYEOF
)
if [ "$FLUSH_GUARD" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: onFlushDirectStream has null guard for sink"
else
    echo "FAIL [0.15]: onFlushDirectStream missing null guard for sink"
fi

# [pr_diff] (0.10): readableStreamToArrayBufferDirect must lock the stream
# to prevent double-consumption.
# Accepts: putByIdDirectPrivate with reader/disturbed, acquireReader,
# addReadRequest, setReadableStreamState, or any lock/disturbed mechanism.
add_total 0.10
LOCK_STREAM=$(python3 << 'PYEOF'
import re

text = open("src/js/builtins/ReadableStreamInternals.ts").read()

m = re.search(r'function\s+readableStreamToArrayBufferDirect\b(.*?)(?=\nfunction\s|\nexport\s|\Z)', text, re.DOTALL)
if not m:
    print("FAIL")
else:
    body = m.group(1)
    # Accept any stream-locking mechanism:
    has_reader = bool(re.search(r'putByIdDirectPrivate.*?(?:reader|Reader)', body, re.IGNORECASE))
    has_disturbed = bool(re.search(r'(?:disturbed|Disturbed)', body))
    has_acquire = bool(re.search(r'acquireReadableStream', body))
    has_add_request = bool(re.search(r'addReadRequest', body))
    has_state = bool(re.search(r'(?:setReadableStreamState|readableStreamState)', body))
    has_lock = bool(re.search(r'(?:lock|Lock)', body))

    if any([has_reader, has_disturbed, has_acquire, has_add_request, has_state, has_lock]):
        print("PASS")
    else:
        print("FAIL")
PYEOF
)
if [ "$LOCK_STREAM" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: readableStreamToArrayBufferDirect locks the stream"
else
    echo "FAIL [0.10]: readableStreamToArrayBufferDirect does not lock the stream"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.05): readableStreamToArrayBuffer function still exists
add_total 0.05
if grep -q 'function readableStreamToArrayBuffer' "$TS_FILE"; then
    add_score 0.05
    echo "PASS [0.05]: readableStreamToArrayBuffer function preserved"
else
    echo "FAIL [0.05]: readableStreamToArrayBuffer function missing"
fi

# [pr_diff] (0.05): readableStreamToBytes function still exists
add_total 0.05
if grep -q 'function readableStreamToBytes' "$TS_FILE"; then
    add_score 0.05
    echo "PASS [0.05]: readableStreamToBytes function preserved"
else
    echo "FAIL [0.05]: readableStreamToBytes function missing"
fi

# [pr_diff] (0.05): onCloseDirectStream and onFlushDirectStream still exist
add_total 0.05
CLOSE_EXISTS=$(grep -c 'function onCloseDirectStream' "$INTERNALS_FILE")
FLUSH_EXISTS=$(grep -c 'function onFlushDirectStream' "$INTERNALS_FILE")
if [ "$CLOSE_EXISTS" -ge 1 ] && [ "$FLUSH_EXISTS" -ge 1 ]; then
    add_score 0.05
    echo "PASS [0.05]: onClose/onFlushDirectStream functions preserved"
else
    echo "FAIL [0.05]: onClose/onFlushDirectStream functions missing"
fi

##############################################################################
# STRUCTURAL: C++ exception handling (0.10)
# WHY structural: C++ requires full Bun build toolchain (Zig, CMake, JSC).
##############################################################################

# [pr_diff] (0.10): C++ wrappers must handle exceptions after calling JS builtins.
# Accepts: RETURN_IF_EXCEPTION, scope.exception(), EXCEPTION_GUARD,
# or any exception checking pattern after call().
add_total 0.10
CPP_EXCEPTION=$(python3 << 'PYEOF'
import re

text = open("src/bun.js/bindings/webcore/ReadableStream.cpp").read()

# Look for exception handling in the readableStreamTo* C++ wrappers
# Accept multiple exception-handling patterns
exception_patterns = [
    r'RETURN_IF_EXCEPTION',
    r'scope\.exception\(\)',
    r'EXCEPTION_GUARD',
    r'jsCast.*exception',
    r'throwScope',
    r'DECLARE_THROW_SCOPE',
    r'RELEASE_AND_RETURN.*scope',
]

# Count how many ZigGlobalObject__readableStreamTo* functions have exception handling
target_funcs = ['readableStreamTo']
func_sections = re.split(r'(?=(?:extern\s+"C"|JSC_DEFINE_HOST_FUNCTION))', text)

funcs_with_exception = 0
for section in func_sections:
    if 'readableStreamTo' not in section:
        continue
    for pat in exception_patterns:
        if re.search(pat, section):
            funcs_with_exception += 1
            break

# At least 3 sections with exception handling (flexible threshold)
print("PASS" if funcs_with_exception >= 3 else "FAIL")
PYEOF
)
if [ "$CPP_EXCEPTION" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: C++ wrappers have exception handling after call()"
else
    echo "FAIL [0.10]: C++ wrappers missing exception handling after call()"
fi

##############################################################################
# ANTI-STUB: Files must not be gutted (0.10)
##############################################################################

# [pr_diff] (0.05): ReadableStreamInternals.ts has substantial content and
# retains key stream management functions
add_total 0.05
ANTISTUB_INTERNALS=$(python3 << 'PYEOF'
text = open("src/js/builtins/ReadableStreamInternals.ts").read()
lines = len(text.splitlines())
# Must retain significant content AND key functions
has_close = "onCloseDirectStream" in text
has_flush = "onFlushDirectStream" in text
has_direct = "readableStreamToArrayBufferDirect" in text
has_cancel = "readableStreamCancel" in text
if lines > 1000 and has_close and has_flush and has_direct and has_cancel:
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$ANTISTUB_INTERNALS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub internals"
else
    echo "FAIL [0.05]: ReadableStreamInternals.ts appears gutted"
fi

# [pr_diff] (0.05): ReadableStream.ts has substantial content
add_total 0.05
ANTISTUB_STREAM=$(python3 << 'PYEOF'
text = open("src/js/builtins/ReadableStream.ts").read()
lines = len(text.splitlines())
has_array = "readableStreamToArray" in text
has_text = "readableStreamToText" in text
has_buf = "readableStreamToArrayBuffer" in text
has_bytes = "readableStreamToBytes" in text
if lines > 100 and has_array and has_text and has_buf and has_bytes:
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$ANTISTUB_STREAM" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub stream"
else
    echo "FAIL [0.05]: ReadableStream.ts appears gutted"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.05)
##############################################################################

# [agent_config] (0.05): No bare .call/.apply in JS builtins — src/js/CLAUDE.md:56
# "Use .$call and .$apply, never .call or .apply"
add_total 0.05
CALL_CHECK=$(python3 << 'PYEOF'
import re

bad = False
for f in ["src/js/builtins/ReadableStream.ts",
          "src/js/builtins/ReadableStreamInternals.ts"]:
    text = open(f).read()
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        # Match .call( or .apply( but NOT .$call( or .$apply(
        if re.search(r'(?<!\$)\.call\s*\(', stripped) or \
           re.search(r'(?<!\$)\.apply\s*\(', stripped):
            bad = True
            break
    if bad:
        break
print("FAIL" if bad else "PASS")
PYEOF
)
if [ "$CALL_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: no bare .call/.apply in builtins (src/js/CLAUDE.md:56)"
else
    echo "FAIL [0.05]: found bare .call/.apply usage in builtins"
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
reward = $FINAL
# Structural checks aligned with bug fix: 0.60
# Regression/P2P: 0.15
# C++ structural: 0.10
# Anti-stub: 0.10
# Config: 0.05
data = {
    'reward': round(reward, 4),
    'behavioral': 0.0,
    'regression': round(min(0.15, max(reward - 0.60, 0.0)), 4),
    'config': round(min(0.05, max(reward - 0.85, 0.0)), 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
