#!/usr/bin/env bash
set +e

TOTAL=0
SCORE=0

add_score() { SCORE=$(python3 -c "print($SCORE + $1)"); }
add_total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd /workspace/bun

ZIG_FILE="src/bundler/linker_context/computeChunks.zig"

##############################################################################
# GATE: Source file exists and is non-empty
##############################################################################
# [pr_diff] (gate): computeChunks.zig must exist
if [ ! -s "$ZIG_FILE" ]; then
    echo "GATE FAILED: $ZIG_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass proxy checks (0.60 total)
# NOTE: Zig code requires the full Bun build toolchain (custom Zig fork,
# CMake, JavaScriptCore, vendor deps) — cannot compile/run in container.
# These checks verify the semantic properties that ANY correct fix must have.
##############################################################################

# [pr_diff] (0.30): Handler.next no longer uses its parameter directly as chunks[] index
# THE BUG: chunks[chunk_id] where chunk_id is the raw entry_point_id.
# ANY correct fix must either: (a) translate the ID through a mapping first,
# (b) guard the access, or (c) restructure to avoid direct indexing.
# Accepts: any variable name for the translated index, any mapping mechanism.
add_total 0.30
F2P_NO_DIRECT=$(python3 -c "
import re

text = open('$ZIG_FILE').read()

# Find the Handler.next function body
# The buggy pattern: fn next(c: *@This(), chunk_id: usize) uses chunks[chunk_id]
# We look for the next function and check if the parameter is used directly

# Extract Handler struct region
handler_re = re.search(r'const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    handler_re = re.search(r'Handler.*=.*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)

if not handler_re:
    print('FAIL: no Handler struct found')
    raise SystemExit

handler_body = handler_re.group(1)

# Find the next function signature to get the parameter name
next_fn = re.search(r'pub fn next\s*\(\s*c\s*:\s*\*@This\(\)\s*,\s*(\w+)\s*:', handler_body)
if not next_fn:
    print('FAIL: no next function found')
    raise SystemExit

param_name = next_fn.group(1)

# Extract the next function body
next_body_match = re.search(r'pub fn next\s*\([^)]*\)[^{]*\{(.*?)\n\s{12}\}', handler_body, re.DOTALL)
if not next_body_match:
    # Try less strict match
    next_body_match = re.search(r'pub fn next[^{]*\{(.*?)\n\s{8,16}\}', handler_body, re.DOTALL)

if not next_body_match:
    print('FAIL: cannot extract next function body')
    raise SystemExit

next_body = next_body_match.group(1)

# THE CRITICAL CHECK: the parameter must NOT be used directly as chunks[param]
# This is the exact bug. The raw entry_point_id was used as chunks[chunk_id].
# A correct fix translates it first (any variable name, any mechanism).
direct_index = re.search(r'c\.chunks\[' + re.escape(param_name) + r'\]', next_body)

if direct_index:
    print('FAIL: parameter still used directly as chunks index (the bug)')
else:
    # Also verify chunks[] IS still accessed (not just deleted)
    has_chunks_access = bool(re.search(r'c\.chunks\[', next_body))
    if has_chunks_access:
        print('PASS')
    else:
        # Might have restructured — check that getOrPut still happens
        if 'getOrPut' in next_body or 'files_with_parts_in_chunk' in next_body:
            print('PASS')
        else:
            print('FAIL: chunks access and core logic removed')
")
if echo "$F2P_NO_DIRECT" | grep -q "^PASS"; then
    add_score 0.30
    echo "PASS [0.30]: Handler.next does not use raw parameter as chunks[] index"
else
    echo "FAIL [0.30]: $F2P_NO_DIRECT"
fi

# [pr_diff] (0.15): Handler.next has a guard/skip for CSS-only entry points
# CSS-only entries don't have JS chunks. ANY fix must handle this — via sentinel
# check, optional unwrap, bounds check, HashMap lookup, or any guard + return.
# Accepts: maxInt sentinel, ?u32 optional, null check, bounds check, HashMap.get, etc.
add_total 0.15
F2P_CSS_SKIP=$(python3 -c "
import re

text = open('$ZIG_FILE').read()

# Extract Handler.next body (same approach)
handler_re = re.search(r'const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    handler_re = re.search(r'Handler.*=.*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    print('FAIL')
    raise SystemExit

handler_body = handler_re.group(1)
next_body_match = re.search(r'pub fn next[^{]*\{(.*?)\n\s{8,16}\}', handler_body, re.DOTALL)
if not next_body_match:
    print('FAIL')
    raise SystemExit

next_body = next_body_match.group(1)

# The buggy code has NO early return and NO guard in next().
# Any fix must add one. Accept many forms:
has_guard = (
    # sentinel check (maxInt, max_int, etc.)
    bool(re.search(r'maxInt|max_int|sentinel', next_body)) or
    # optional unwrap (orelse return, .? access)
    bool(re.search(r'orelse\s+return|\.?\s*\?\s*;|\borelse\b', next_body)) or
    # null check
    bool(re.search(r'==\s*null|!=\s*null', next_body)) or
    # bounds check
    bool(re.search(r'>=\s*c\.chunks\.len|<\s*c\.chunks\.len|bounds', next_body)) or
    # early return on condition
    bool(re.search(r'if\s*\(.*\)\s*return', next_body))
)

if has_guard:
    print('PASS')
else:
    print('FAIL')
")
if [ "$F2P_CSS_SKIP" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: Handler.next has guard/skip for CSS-only entry points"
else
    echo "FAIL [0.15]: Handler.next has no guard for CSS-only entry points"
fi

# [pr_diff] (0.15): A mapping/lookup from entry point IDs to chunk indices exists
# The core fix: some data structure must translate entry_point IDs to JS chunk
# indices. Accepts: flat array, HashMap, ArrayList, optional array, any name.
add_total 0.15
F2P_MAPPING=$(python3 -c "
import re

text = open('$ZIG_FILE').read()

# Check for ANY of these patterns indicating an ID-to-index mapping:
has_mapping = (
    # Flat array allocated with entry_points.len
    bool(re.search(r'alloc\(\s*(?:u32|\?u32)\s*,\s*(?:this\.graph\.)?entry_points\.len\)', text)) or
    # HashMap keyed on entry point IDs
    bool(re.search(r'HashMap\(.*entry.*chunk|AutoHashMap.*u32.*u32', text)) or
    # ArrayList for mapping
    bool(re.search(r'ArrayList\((?:u32|\?u32)\).*entry_point', text)) or
    # Any variable name suggesting entry-to-chunk mapping (allocated with entry_points.len)
    bool(re.search(r'\w+\s*=\s*(?:try\s+)?(?:temp_allocator|this\.allocator|allocator)\w*\.alloc\([^)]*entry_points\.len\)', text)) or
    # Field in Handler that is a slice of u32/optional
    bool(re.search(r'Handler.*struct.*\[\](?:const\s+)?(?:u32|\?u32)', text, re.DOTALL))
)

if has_mapping:
    print('PASS')
else:
    print('FAIL')
")
if [ "$F2P_MAPPING" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: mapping/lookup from entry point IDs to chunk indices exists"
else
    echo "FAIL [0.15]: no mapping from entry point IDs to chunk indices found"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.10): Handler struct retains core functionality
# The Handler.next function must still call getOrPut on files_with_parts_in_chunk.
# This is the core work the function does — any fix that removes it is wrong.
add_total 0.10
P2P_CORE=$(python3 -c "
import re

text = open('$ZIG_FILE').read()

handler_re = re.search(r'const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    handler_re = re.search(r'Handler.*=.*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)

if not handler_re:
    print('FAIL')
    raise SystemExit

h = handler_re.group(1)

# Must retain: chunks field, fn next, and core logic
has_chunks = 'chunks' in h
has_next = 'fn next' in h
has_core_logic = 'files_with_parts_in_chunk' in h and 'getOrPut' in h

if has_chunks and has_next and has_core_logic:
    print('PASS')
else:
    print('FAIL')
")
if [ "$P2P_CORE" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: Handler struct retains chunks, next, and core getOrPut logic"
else
    echo "FAIL [0.10]: Handler struct missing core functionality"
fi

# [pr_diff] (0.05): computeChunks function still creates js_chunks and css_chunks
add_total 0.05
P2P_CHUNKS=$(python3 -c "
text = open('$ZIG_FILE').read()
has_js = 'js_chunks' in text
has_css = 'css_chunks' in text
has_entry_source = 'entry_source_indices' in text
if has_js and has_css and has_entry_source:
    print('PASS')
else:
    print('FAIL')
")
if [ "$P2P_CHUNKS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: computeChunks still creates js_chunks and css_chunks"
else
    echo "FAIL [0.05]: core chunk creation logic missing"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.10)
##############################################################################

# [pr_diff] (0.10): Handler.next is not a stub
# The function must have meaningful body (not just return or pass).
add_total 0.10
ANTI_STUB=$(python3 -c "
import re

text = open('$ZIG_FILE').read()

handler_re = re.search(r'const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    handler_re = re.search(r'Handler.*=.*struct\s*\{(.*?)\n\s{8}\};', text, re.DOTALL)
if not handler_re:
    print('FAIL')
    raise SystemExit

handler_body = handler_re.group(1)
next_body_match = re.search(r'pub fn next[^{]*\{(.*?)\n\s{8,16}\}', handler_body, re.DOTALL)
if not next_body_match:
    print('FAIL')
    raise SystemExit

next_body = next_body_match.group(1)

# Count meaningful lines (non-empty, non-comment, non-brace-only)
lines = [l.strip() for l in next_body.split('\n')]
meaningful = [l for l in lines if l and not l.startswith('//') and l not in ('{', '}', '')]

# A stub would have 0-2 lines. The real function needs at least 4 meaningful lines
# (guard + lookup + getOrPut + initialization).
if len(meaningful) >= 4:
    print('PASS')
else:
    print('FAIL')
")
if [ "$ANTI_STUB" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: Handler.next is not a stub (>=4 meaningful lines)"
else
    echo "FAIL [0.10]: Handler.next appears to be a stub"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.15)
##############################################################################

# [agent_config] (0.10): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16
# Exception: std.math, std.mem, std.AutoArrayHashMap are OK per existing patterns.
add_total 0.10
BUN_API=$(python3 -c "
import re
text = open('$ZIG_FILE').read()
bad_std_usage = re.findall(r'std\.(fs|posix|os|process)\.', text)
if len(bad_std_usage) == 0:
    print('PASS')
else:
    print('FAIL')
")
if [ "$BUN_API" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: no prohibited std.* API usage introduced"
else
    echo "FAIL [0.10]: prohibited std.* API usage found"
fi

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:11
add_total 0.05
NO_INLINE_IMPORT=$(python3 -c "
import re
text = open('$ZIG_FILE').read()
fn_bodies = re.findall(r'pub fn \w+\([^)]*\)[^{]*\{(.*?)\n\s{8}\}', text, re.DOTALL)
has_inline_import = any('@import(' in body for body in fn_bodies)
if not has_inline_import:
    print('PASS')
else:
    print('FAIL')
")
if [ "$NO_INLINE_IMPORT" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: no inline @import() inside functions"
else
    echo "FAIL [0.05]: found @import() inline inside function body"
fi

##############################################################################
# FINAL SCORE
##############################################################################
FINAL=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "=== FINAL SCORE: $FINAL (raw: $SCORE / $TOTAL) ==="
echo "$FINAL" > /logs/verifier/reward.txt

# Compute category breakdowns
python3 -c "
import json
score = $SCORE
total = $TOTAL
final = round(score / total, 4) if total > 0 else 0.0

# Category maximums: behavioral=0.60, regression=0.15, config=0.15, structural=0.10
data = {
    'reward': final,
    'behavioral': round(min(score, 0.60) / total, 4) if total > 0 else 0.0,
    'regression': 0.0,
    'config': 0.0,
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
