#!/usr/bin/env bash
set +e

SCORE=0
add_score() { SCORE=$(python3 -c "print($SCORE + $1)"); }

cd /workspace/bun
FILE="src/bun.js/test/expect.zig"

##############################################################################
# GATE: File exists, is non-empty, and is valid Zig (syntax-level)
##############################################################################
# [pr_diff] (gate): expect.zig must exist and be parseable Zig
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Basic Zig syntax gate: balanced braces, no obvious syntax errors
ZIG_SYNTAX=$(python3 << 'PYEOF'
text = open("src/bun.js/test/expect.zig").read()
import re
# Strip comments and strings for brace counting
clean = re.sub(r'//[^\n]*', '', text)
clean = re.sub(r'"(?:[^"\\]|\\.)*"', '""', clean)
opens = clean.count("{")
closes = clean.count("}")
# Allow small imbalance (nested comptime etc) but not wildly off
if abs(opens - closes) > 5:
    print("FAIL")
else:
    print("PASS")
PYEOF
)
if [ "$ZIG_SYNTAX" != "PASS" ]; then
    echo "GATE FAILED: Zig syntax check (unbalanced braces)"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# HELPER: Extract the extend function body (brace-matched, comments stripped)
##############################################################################
EXTEND_BODY=$(python3 << 'PYEOF'
import re
text = open("src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    print("")
    exit()
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
# Strip single-line comments to prevent comment injection
body = re.sub(r'//[^\n]*', '', body)
# Strip string literals to prevent string injection
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
print(body)
PYEOF
)

if [ -z "$EXTEND_BODY" ]; then
    echo "GATE FAILED: pub fn extend not found in $FILE"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

BEHAVIORAL=0
REGRESSION=0
CONFIG=0

##############################################################################
# CHECK 1 (0.35): FAIL-TO-PASS ANALOG — buggy .put() calls are gone
#
# The bug: expect_proto.put(), expect_constructor.put(), expect_static_proto.put()
# assert !parseIndex(name), crashing on numeric keys.
#
# On the BUGGY commit, these .put() calls exist → this check FAILS.
# On ANY correct fix, they are replaced → this check PASSES.
#
# This is the closest to a fail-to-pass test we can get for non-compilable
# Zig code: verify the specific buggy pattern is absent.
##############################################################################
# [pr_diff] (0.35): Buggy .put() calls on property registration targets are removed
BUGGY_PUT=$(echo "$EXTEND_BODY" | python3 << 'PYEOF'
import re, sys
body = sys.stdin.read()
if not body.strip():
    print("FAIL")
    exit()

# Find all method calls on the three targets
# The bug is specifically: expect_proto.put(, expect_constructor.put(, expect_static_proto.put(
targets = ['expect_proto', 'expect_constructor', 'expect_static_proto']
buggy_calls = []
for target in targets:
    # Match target.put( but NOT target.putMayBeIndex( or target.putNonIndex( etc
    # Use word boundary after 'put' to match exactly .put(
    pattern = re.escape(target) + r'\.put\s*\('
    if re.search(pattern, body):
        buggy_calls.append(target)

if len(buggy_calls) == 0:
    print("PASS")
else:
    print("FAIL:" + ",".join(buggy_calls))
PYEOF
)
if [[ "$BUGGY_PUT" == "PASS" ]]; then
    add_score 0.35
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.35)")
    echo "PASS [0.35]: buggy .put() calls removed from all three registration targets"
else
    echo "FAIL [0.35]: buggy .put() calls still present: ${BUGGY_PUT#FAIL:}"
fi

##############################################################################
# CHECK 2 (0.25): Replacement method or iterator guard is present
#
# Removing .put() is necessary but not sufficient — the properties still need
# to be registered. Verify either:
#   (a) A different property-setting method is called on all three targets
#       (e.g., putMayBeIndex, putNonIndex, defineProperty, etc.)
#   (b) The iterator is configured to skip index properties AND .put() is
#       still used (safe because indices are filtered out)
#
# NOTE: We do NOT require a specific method name — any non-put setter works.
##############################################################################
# [pr_diff] (0.25): Properties are still registered via a safe method
REPLACEMENT=$(echo "$EXTEND_BODY" | python3 << 'PYEOF'
import re, sys
body = sys.stdin.read()
if not body.strip():
    print("FAIL")
    exit()

targets = ['expect_proto', 'expect_constructor', 'expect_static_proto']
read_only = {'get', 'has', 'contains', 'count', 'next', 'keys', 'iterator',
             'len', 'ptr', 'items', 'reset', 'deinit', 'init', 'format'}

# Approach A: each target calls a non-put setting method
all_have_setter = True
for target in targets:
    # Find all method calls: target.method(
    methods = re.findall(re.escape(target) + r'\.(\w+)\s*\(', body)
    setters = [m for m in methods if m.lower() not in read_only and m != 'put']
    if not setters:
        all_have_setter = False
        break

# Approach B: iterator is configured to skip indices (via initFast flags or explicit guard)
# Must be an ACTUAL iterator configuration, not just a variable name containing "skip"
# Look for specific patterns:
#   - .initFast(...) with skip/no index flag
#   - if (name.isIndex()) continue; or similar guard
approach_b = False
# initFast with explicit flag to skip indices
if re.search(r'\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)', body):
    # initFast has a boolean parameter controlling index iteration
    approach_b = True
# Explicit guard: check if property is an index and skip
if re.search(r'(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)', body):
    approach_b = True

if all_have_setter or approach_b:
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$REPLACEMENT" = "PASS" ]; then
    add_score 0.25
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.25)")
    echo "PASS [0.25]: safe property registration method present"
else
    echo "FAIL [0.25]: no safe replacement for .put() found"
fi

##############################################################################
# CHECK 3 (0.10): All three registration targets are handled
#
# A partial fix that only changes 1 or 2 of the 3 targets leaves the crash
# for the others. Verify all three are addressed.
##############################################################################
# [pr_diff] (0.10): All three targets (expect_proto, constructor, static_proto) modified
ALL_TARGETS=$(echo "$EXTEND_BODY" | python3 << 'PYEOF'
import re, sys
body = sys.stdin.read()
if not body.strip():
    print("FAIL")
    exit()

targets = ['expect_proto', 'expect_constructor', 'expect_static_proto']
read_only = {'get', 'has', 'contains', 'count', 'next', 'keys', 'iterator',
             'len', 'ptr', 'items', 'reset', 'deinit', 'init', 'format'}

# Check each target has a non-put setter OR .put() is safe due to iterator guard
approach_b = bool(
    re.search(r'\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)', body) or
    re.search(r'(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)', body)
)

if approach_b:
    # All targets safe via iterator configuration
    print("PASS")
    exit()

# Approach A: each target must individually use a non-put method
missing = []
for target in targets:
    methods = re.findall(re.escape(target) + r'\.(\w+)\s*\(', body)
    setters = [m for m in methods if m.lower() not in read_only and m != 'put']
    if not setters:
        missing.append(target)

if not missing:
    print("PASS")
else:
    print("FAIL:" + ",".join(missing))
PYEOF
)
if [[ "$ALL_TARGETS" == "PASS" ]]; then
    add_score 0.10
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.10)")
    echo "PASS [0.10]: all three registration targets addressed"
else
    echo "FAIL [0.10]: not all targets addressed: ${ALL_TARGETS#FAIL:}"
fi

##############################################################################
# CHECK 4 (0.10): Pass-to-pass — extend function preserves core logic
#
# The function must still iterate properties and create wrapper functions.
# A correct fix only changes the property-setting method, not the overall
# structure.
##############################################################################
# [pr_diff] (0.10): Extend function preserves iteration + wrapper creation
INTEGRITY=$(echo "$EXTEND_BODY" | python3 << 'PYEOF'
import re, sys
body = sys.stdin.read()
if not body.strip():
    print("FAIL")
    exit()

checks = 0

# Must have property iteration
if re.search(r'while\s*\(', body) or re.search(r'[Ii]terator', body):
    checks += 1

# Must create wrapper functions
if re.search(r'Bun__JSWrappingFunction__create|WrappingFunction|wrapFunction', body):
    checks += 1

# Must reference applyCustomMatcher (the callback for wrapper functions)
if re.search(r'applyCustomMatcher', body):
    checks += 1

# Need all three for pass
print("PASS" if checks == 3 else "FAIL")
PYEOF
)
if [ "$INTEGRITY" = "PASS" ]; then
    add_score 0.10
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
    echo "PASS [0.10]: extend function preserves iteration + wrapper + matcher logic"
else
    echo "FAIL [0.10]: extend function missing core logic (iteration/wrapper/matcher)"
fi

##############################################################################
# CHECK 5 (0.05): Pass-to-pass — key functions preserved in file
##############################################################################
# [pr_diff] (0.05): applyCustomMatcher and other key functions still exist
P2P_FUNCS=$(python3 << 'PYEOF'
import re
text = open("src/bun.js/test/expect.zig").read()
required = ['applyCustomMatcher', 'pub fn extend', 'pub fn toBeCloseTo', 'pub fn toEqual']
missing = [fn for fn in required if fn not in text]
print("PASS" if not missing else "FAIL:" + ",".join(missing))
PYEOF
)
if [[ "$P2P_FUNCS" == "PASS" ]]; then
    add_score 0.05
    REGRESSION=$(python3 -c "print($REGRESSION + 0.05)")
    echo "PASS [0.05]: key functions preserved"
else
    echo "FAIL [0.05]: missing functions: ${P2P_FUNCS#FAIL:}"
fi

##############################################################################
# CHECK 6 (0.05): Anti-stub — file has substantial Zig content
##############################################################################
# [pr_diff] (0.05): Anti-stub — meaningful file size + Zig constructs
ANTISTUB=$(python3 << 'PYEOF'
import re
text = open("src/bun.js/test/expect.zig").read()
lines = len(text.strip().split("\n"))
pub_fns = len(re.findall(r'\bpub\s+fn\b', text))
structs = len(re.findall(r'\bstruct\b', text))
consts = len(re.findall(r'\bconst\b', text))
if lines >= 500 and pub_fns >= 5 and structs >= 2 and consts >= 10:
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$ANTISTUB" = "PASS" ]; then
    add_score 0.05
    REGRESSION=$(python3 -c "print($REGRESSION + 0.05)")
    echo "PASS [0.05]: anti-stub (substantial Zig content)"
else
    echo "FAIL [0.05]: file too small or lacks Zig constructs"
fi

##############################################################################
# CHECK 7 (0.05): Agent config — no inline @import in functions
##############################################################################
# [agent_config] (0.05): "Use @import at top-level" — src/CLAUDE.md:11 @ 6034bd82
INLINE_IMPORT=$(python3 << 'PYEOF'
import re
text = open("src/bun.js/test/expect.zig").read()
text_nc = re.sub(r'//[^\n]*', '', text)
in_fn = False
depth = 0
bad = False
for line in text_nc.split("\n"):
    stripped = line.strip()
    if re.match(r'(pub\s+)?fn\s+', stripped) and "{" in stripped:
        in_fn = True
        depth = stripped.count("{") - stripped.count("}")
        continue
    if in_fn:
        depth += stripped.count("{") - stripped.count("}")
        if "@import" in stripped:
            bad = True
            break
        if depth <= 0:
            in_fn = False
print("FAIL" if bad else "PASS")
PYEOF
)
if [ "$INLINE_IMPORT" = "PASS" ]; then
    add_score 0.05
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    echo "PASS [0.05]: no inline @import in functions (src/CLAUDE.md:11)"
else
    echo "FAIL [0.05]: found inline @import inside function body"
fi

##############################################################################
# CHECK 8 (0.05): Agent config — no std.fs / std.posix / std.os usage
##############################################################################
# [agent_config] (0.05): "Use bun.* equivalents" — src/CLAUDE.md:16 @ 6034bd82
if ! grep -qE 'std\.(fs|posix|os)\.' "$FILE"; then
    add_score 0.05
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    echo "PASS [0.05]: no std.fs/posix/os usage (src/CLAUDE.md:16)"
else
    echo "FAIL [0.05]: uses std.fs/posix/os instead of bun.* equivalents"
fi

##############################################################################
# Final scoring
##############################################################################
FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Total: $FINAL / 1.0"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
data = {
    'reward': round($FINAL, 4),
    'behavioral': round($BEHAVIORAL, 4),
    'regression': round($REGRESSION, 4),
    'config': round($CONFIG, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
