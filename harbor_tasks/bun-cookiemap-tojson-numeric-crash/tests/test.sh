#!/usr/bin/env bash
set +e

TOTAL=0
SCORE=0
GATE_PASSED=0

add() {
    SCORE=$(python3 -c "print(round($SCORE + $1, 4))")
    TOTAL=$(python3 -c "print(round($TOTAL + $2, 4))")
}
fail() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

write_reward() {
    local reward="$1"
    echo "$reward" > /logs/verifier/reward.txt
    python3 -c "
import json
r = $reward
json.dump({'reward': r, 'behavioral': round(min(r, 0.60), 4),
           'regression': round(min(max(r - 0.60, 0), 0.20), 4),
           'config': round(min(max(r - 0.80, 0), 0.20), 4),
           'style_rubric': 0.0}, open('/logs/verifier/reward.json', 'w'))
"
}

cd /workspace/bun
FILE="src/bun.js/bindings/CookieMap.cpp"

##############################################################################
# GATE: File exists, is non-trivial, and contains CookieMap::toJSON
##############################################################################
# [pr_diff] (gate): CookieMap.cpp must exist with toJSON method
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE missing or empty"
    write_reward 0.0
    exit 0
fi

GATE_RESULT=$(python3 << 'PYEOF'
import re, sys

text = open("src/bun.js/bindings/CookieMap.cpp").read()

# Must have toJSON method
m = re.search(r'CookieMap::toJSON\b.*?\{(.*?)^\}', text, re.DOTALL | re.MULTILINE)
if not m:
    print("NO_METHOD")
    sys.exit(0)

body = m.group(1)
non_blank = [l for l in body.splitlines() if l.strip() and not l.strip().startswith('//')]

# Anti-stub: real implementation needs meaningful content
if len(non_blank) < 8:
    print("STUB")
    sys.exit(0)

# Must retain other CookieMap methods (not a replacement file)
other_methods = set(re.findall(r'CookieMap::(\w+)', text))
other_methods.discard('toJSON')
if len(other_methods) < 3:
    print("REPLACED")
    sys.exit(0)

# Save body for later checks
open("/tmp/tojson_body.txt", "w").write(body)
open("/tmp/full_file.txt", "w").write(text)
print("OK")
PYEOF
)

if [ "$GATE_RESULT" != "OK" ]; then
    echo "GATE FAILED: $GATE_RESULT"
    write_reward 0.0
    exit 0
fi
GATE_PASSED=1
echo "GATE PASSED: toJSON method found with meaningful implementation"

##############################################################################
# CHECK 1 (0.35): Core bug fix — no bare putDirect in toJSON
# The bug: putDirect asserts !parseIndex(propertyName) and crashes on numeric
# cookie names. ANY index-safe method is acceptable.
# Fail-to-pass: the buggy code has bare putDirect calls, so this check
# FAILS on the base commit and PASSES on a correct fix.
##############################################################################
# [pr_diff] (0.35): putDirect replaced with index-safe property insertion
CHECK1=$(python3 << 'PYEOF'
import re
body = open("/tmp/tojson_body.txt").read()

# The crash pattern: bare ->putDirect( (not putDirectMayBeIndex etc.)
# Use negative lookahead to exclude safe variants
bare_puts = re.findall(r'->putDirect\s*\(', body)
safe_variants = re.findall(r'->putDirect(?:MayBeIndex|Index)\s*\(', body)
# bare_puts includes the safe variants textually, so subtract
unsafe_count = len(bare_puts) - len(safe_variants)

# Accept ANY method that handles index properties:
# putDirectMayBeIndex, putDirectIndex, putByIndex, put, defineOwnProperty
safe_puts = re.findall(
    r'->(?:putDirectMayBeIndex|putDirectIndex|putByIndex|put|defineOwnProperty)\s*\(',
    body
)
# Exclude bare "put" that's part of "putDirect" — already counted above
# Actually the regex already handles this since putDirect won't match "put\s*\("

if unsafe_count > 0:
    print("FAIL:bare_putDirect_found")
elif len(safe_puts) < 1:
    print("FAIL:no_safe_put_found")
else:
    print("PASS")
PYEOF
)
if [ "$CHECK1" = "PASS" ]; then
    add 0.35 0.35
    echo "PASS [0.35]: toJSON uses index-safe property insertion (no bare putDirect)"
else
    fail 0.35
    echo "FAIL [0.35]: $CHECK1"
fi

##############################################################################
# CHECK 2 (0.25): Both code paths fixed — toJSON iterates modified AND
# original cookies. Both paths must use safe insertion.
# Accept any structure: two loops, one merged loop, iterator chain, etc.
# Key signal: at least 2 property insertion calls OR a single call inside
# a loop that iterates a merged/combined collection.
##############################################################################
# [pr_diff] (0.25): all property insertion paths are index-safe
CHECK2=$(python3 << 'PYEOF'
import re
body = open("/tmp/tojson_body.txt").read()

# Count ALL put-family calls in the body
all_puts = re.findall(
    r'->(putDirect\w*|putByIndex|put|defineOwnProperty)\s*\(',
    body
)

# Classify
unsafe = [p for p in all_puts if p == 'putDirect']
safe = [p for p in all_puts if p in (
    'putDirectMayBeIndex', 'putDirectIndex', 'putByIndex',
    'put', 'defineOwnProperty'
)]

if len(unsafe) > 0:
    print("FAIL:unsafe_puts_remain")
elif len(safe) >= 2:
    # Two or more safe calls — covers both code paths directly
    print("PASS")
elif len(safe) == 1:
    # One call — acceptable if there's evidence of merged iteration
    # (e.g., iterating a combined map/chain/concat)
    has_merge = bool(re.search(
        r'merge|combine|concat|chain|append|insert.*All|addAll|putAll|forEach',
        body, re.IGNORECASE
    ))
    has_loop = bool(re.search(r'\bfor\s*\(|\bwhile\s*\(', body))
    if has_loop:
        print("PASS")  # Single put in a loop is fine
    else:
        print("FAIL:single_put_no_loop")
else:
    print("FAIL:no_puts_found")
PYEOF
)
if [ "$CHECK2" = "PASS" ]; then
    add 0.25 0.25
    echo "PASS [0.25]: all property insertion paths are index-safe"
else
    fail 0.25
    echo "FAIL [0.25]: $CHECK2"
fi

##############################################################################
# CHECK 3 (0.15): Deduplication logic doesn't use crash-prone hasProperty.
# The buggy code calls hasProperty on the JSObject to check if a cookie name
# already exists. hasProperty with numeric strings also crashes.
# Accept: HashSet/set tracking, restructured iteration, checking the cookie
# map directly, or any approach that avoids hasProperty on the JSObject.
##############################################################################
# [pr_diff] (0.15): deduplication avoids hasProperty crash path
CHECK3=$(python3 << 'PYEOF'
import re
body = open("/tmp/tojson_body.txt").read()

has_property = re.findall(r'->hasProperty\s*\(', body)

if len(has_property) == 0:
    # No hasProperty at all — safe regardless of approach
    print("PASS")
else:
    # hasProperty present — only OK if it's on a native C++ set, not JSObject
    # Check if there's a tracking data structure
    has_native_tracking = bool(re.search(
        r'HashSet|std::set|std::unordered_set|WTF::HashSet|std::unordered_map',
        body
    ))
    if has_native_tracking:
        print("PASS")
    else:
        print("FAIL:hasProperty_on_jsobject")
PYEOF
)
if [ "$CHECK3" = "PASS" ]; then
    add 0.15 0.15
    echo "PASS [0.15]: deduplication does not use crash-prone hasProperty on JSObject"
else
    fail 0.15
    echo "FAIL [0.15]: $CHECK3"
fi

##############################################################################
# CHECK 4 (0.10): Regression — toJSON still constructs and returns a JS object
# and has exception/scope handling (core functionality preserved).
##############################################################################
# [pr_diff] (0.10): existing functionality preserved
CHECK4=$(python3 << 'PYEOF'
import re
body = open("/tmp/tojson_body.txt").read()

has_obj_create = bool(re.search(
    r'constructEmptyObject|constructObject|JSObject::create|JSFinalObject::create',
    body
))
has_exception = bool(re.search(
    r'RETURN_IF_EXCEPTION|RELEASE_AND_RETURN|throwException|DECLARE_THROW_SCOPE|scope',
    body
))
has_iteration = bool(re.search(r'\bfor\s*\(|\bwhile\s*\(|forEach', body))

passes = sum([has_obj_create, has_exception, has_iteration])
if passes >= 2:
    print("PASS")
else:
    parts = []
    if not has_obj_create: parts.append("no_object_construction")
    if not has_exception: parts.append("no_exception_handling")
    if not has_iteration: parts.append("no_iteration")
    print("FAIL:" + ",".join(parts))
PYEOF
)
if [ "$CHECK4" = "PASS" ]; then
    add 0.10 0.10
    echo "PASS [0.10]: regression — object construction, exception handling, iteration preserved"
else
    fail 0.10
    echo "FAIL [0.10]: $CHECK4"
fi

##############################################################################
# CHECK 5 (0.10): Anti-gaming — function has coherent implementation
# Checks that the function body has iteration over cookie data, property
# insertion, AND scope/exception handling together. A stub that just has
# keywords scattered won't pass because we require logical coherence:
# iteration must contain property insertion.
##############################################################################
# [pr_diff] (0.10): coherent implementation (not keyword-stuffed)
CHECK5=$(python3 << 'PYEOF'
import re

body = open("/tmp/tojson_body.txt").read()
lines = body.splitlines()

# Find lines with loops
loop_lines = []
for i, line in enumerate(lines):
    if re.search(r'\bfor\s*\(|\bwhile\s*\(', line):
        loop_lines.append(i)

# Find lines with put calls
put_lines = []
for i, line in enumerate(lines):
    if re.search(r'->(?:putDirect\w*|putByIndex|put|defineOwnProperty)\s*\(', line):
        put_lines.append(i)

if not loop_lines or not put_lines:
    print("FAIL:missing_loop_or_put")
else:
    # Check that at least one put call is inside a loop (within ~15 lines after loop start)
    found_put_in_loop = False
    for loop_line in loop_lines:
        for put_line in put_lines:
            if 0 < (put_line - loop_line) <= 15:
                found_put_in_loop = True
                break
    if found_put_in_loop:
        print("PASS")
    else:
        print("FAIL:put_not_inside_loop")
PYEOF
)
if [ "$CHECK5" = "PASS" ]; then
    add 0.10 0.10
    echo "PASS [0.10]: coherent implementation — property insertion inside iteration"
else
    fail 0.10
    echo "FAIL [0.10]: $CHECK5"
fi

##############################################################################
# CHECK 6 (0.05): No TODO/FIXME/HACK markers left in modified function
##############################################################################
# [agent_config] (0.05): clean code — no debug markers
CHECK6=$(python3 << 'PYEOF'
import re
body = open("/tmp/tojson_body.txt").read()
if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', body):
    print("FAIL")
else:
    print("PASS")
PYEOF
)
if [ "$CHECK6" = "PASS" ]; then
    add 0.05 0.05
    echo "PASS [0.05]: no TODO/FIXME/HACK markers in toJSON"
else
    fail 0.05
    echo "FAIL [0.05]: TODO/FIXME/HACK found in toJSON"
fi

##############################################################################
# Final scoring
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 4))")
TOTAL_F=$(python3 -c "print(round($TOTAL, 4))")
echo ""
echo "Total: $FINAL / $TOTAL_F"
write_reward "$FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
