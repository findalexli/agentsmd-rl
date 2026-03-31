#!/usr/bin/env bash
set +e

TOTAL=0.0
SCORE=0.0
GATE_PASSED=0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun

ZIG_FILE="src/bundler/barrel_imports.zig"

##############################################################################
# GATE: Source file exists and parses (Zig syntax not checkable without
# compiler, but basic sanity: file exists, has expected structure markers)
##############################################################################
# [pr_diff] (gate): barrel_imports.zig must exist and contain core structures
if [ ! -s "$ZIG_FILE" ]; then
    echo "GATE FAILED: $ZIG_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# CHECK 1 (0.40): CORE FIX — star-import flag is carried through resolution
#
# The bug: scheduleBarrelDeferredImports hardcodes is_star = false after
# resolveBarrelExport, losing the star-import status of namespace re-exports.
#
# The fix MUST: (a) capture the star-import flag from the import record,
# (b) propagate it to the BFS queue's is_star field.
#
# This check accepts ANY implementation approach:
#   - Adding a bool/enum field to BarrelExportResolution struct
#   - Using an out-parameter
#   - Inline computation at the usage site
#   - Any field name (not just alias_is_star)
#
# Bronze structural — Zig requires Bun's custom toolchain (CMake + JSC +
# custom Zig compiler fork), cannot compile or execute in test container.
##############################################################################
# [pr_diff] (0.40): Star-import flag propagated through barrel resolution to BFS
add_total 0.40
CORE_FIX=$(python3 << 'PYEOF'
import re, sys

text = open("src/bundler/barrel_imports.zig").read()

# Find scheduleBarrelDeferredImports function body
bfs_match = re.search(
    r'pub fn scheduleBarrelDeferredImports\b(.*)',
    text, re.DOTALL
)
if not bfs_match:
    print("FAIL:no_bfs_fn")
    sys.exit(0)

bfs_body = bfs_match.group(1)

# Find the section after resolveBarrelExport is called
res_pos = bfs_body.find('resolveBarrelExport')
if res_pos < 0:
    print("FAIL:no_resolve_call")
    sys.exit(0)

# Look at the code after the resolve call (up to ~1200 chars to cover the append)
after_resolve = bfs_body[res_pos:res_pos + 1200]

# CRITICAL CHECK: The buggy code has ".is_star = false" after resolveBarrelExport.
# A correct fix must replace this with a dynamic value.
# We look for queue/append patterns that set is_star to something other than 'false'.

# Find all is_star assignments in this section
is_star_assigns = re.findall(r'\.is_star\s*=\s*([^,}\s]+)', after_resolve)

if not is_star_assigns:
    print("FAIL:no_is_star_assign")
    sys.exit(0)

# Check that at least one is_star assignment uses a dynamic value (not literal false)
has_dynamic = False
all_hardcoded = True
for val in is_star_assigns:
    val = val.strip().rstrip(',')
    if val != 'false':
        has_dynamic = True
    if val not in ('false', 'true'):
        all_hardcoded = False

if not has_dynamic:
    print("FAIL:all_hardcoded_false")
    sys.exit(0)

# The dynamic value should relate to the resolution or import record — not a random literal.
# Accept: resolution.X, res.X, barrel_resolution.X, import_record.X, record.X,
#         or any dotted access, or a function call, or a variable name.
# Reject: literal 'true' (just flipping the hardcode is wrong — it would break non-star cases)
has_meaningful_dynamic = False
for val in is_star_assigns:
    val = val.strip().rstrip(',')
    if val == 'false' or val == 'true':
        continue
    # Must be a dotted field access or variable reference (not a literal)
    if re.match(r'\w+(\.\w+)*', val):
        has_meaningful_dynamic = True
        break

if has_meaningful_dynamic:
    print("PASS")
else:
    print("FAIL:no_meaningful_dynamic")

PYEOF
)
if [ "$CORE_FIX" = "PASS" ]; then
    add_score 0.40
    GATE_PASSED=1
    echo "PASS [0.40]: Core fix — is_star uses dynamic value from resolution (not hardcoded false)"
else
    echo "FAIL [0.40]: Core fix not detected ($CORE_FIX)"
fi

##############################################################################
# CHECK 2 (0.20): Star-import information originates from import record
#
# The resolution must read the star-import status from somewhere meaningful —
# import_entry, import_record, named_import, or similar import-related data.
# This prevents gaming by wiring a random unrelated bool.
#
# GATED behind core fix passing.
##############################################################################
# [pr_diff] (0.20): Star flag originates from import-record data
add_total 0.20
if [ "$GATE_PASSED" = "1" ]; then
    STAR_ORIGIN=$(python3 << 'PYEOF'
import re, sys

text = open("src/bundler/barrel_imports.zig").read()

# The fix needs to read star-import status from the import system.
# This could happen in resolveBarrelExport (adding to return struct),
# or directly in scheduleBarrelDeferredImports (reading import_record).
#
# We check: somewhere in the code path between resolveBarrelExport definition
# and the BFS append, there must be an access to a star/namespace-related field
# from an import-related variable.

# Strategy: Look for patterns indicating star-import detection:
#   - .alias_is_star, .is_star (on import entry/record, not on queue item)
#   - star-import detection via name == "" or name.len() == 0
#   - namespace_import or similar naming

# Check resolveBarrelExport body
resolve_match = re.search(
    r'fn resolveBarrelExport\b(.*?)\n\s{4,8}\}',
    text, re.DOTALL
)
resolve_body = resolve_match.group(1) if resolve_match else ""

# Check scheduleBarrelDeferredImports body
bfs_match = re.search(
    r'pub fn scheduleBarrelDeferredImports\b(.*)',
    text, re.DOTALL
)
bfs_body = bfs_match.group(1) if bfs_match else ""

combined = resolve_body + "\n" + bfs_body

# Look for star-import detection patterns (any of these indicate correct origin)
star_patterns = [
    r'alias_is_star',                    # Direct field name
    r'is_star.*import',                  # is_star from import context
    r'import.*is_star',                  # import context with is_star
    r'name\.len\s*[=!]=\s*0',           # Star import detected by empty name
    r'name\.len\(\)\s*[=!]=\s*0',       # Star import detected by empty name (method)
    r'\.name\s*==\s*""',                 # Empty string name check
    r'namespace',                        # Namespace import handling
    r'star',                             # Star-related logic
]

found_patterns = 0
for pat in star_patterns:
    if re.search(pat, combined, re.IGNORECASE):
        found_patterns += 1

# Need at least 2 star-related patterns to confirm meaningful wiring
# (the original code already has some "is_star" references in BFS queue items)
# We need evidence it's being READ from import data, not just written to queue
if found_patterns >= 2:
    print("PASS")
elif found_patterns == 1:
    print("PARTIAL")
else:
    print("FAIL")

PYEOF
    )
    if [ "$STAR_ORIGIN" = "PASS" ]; then
        add_score 0.20
        echo "PASS [0.20]: Star flag originates from import-record data"
    elif [ "$STAR_ORIGIN" = "PARTIAL" ]; then
        add_score 0.10
        echo "PARTIAL [0.10/0.20]: Some star-import origin evidence but weak"
    else
        echo "FAIL [0.20]: No evidence star flag reads from import-record data"
    fi
else
    echo "SKIP [0.20]: Gated behind core fix (check 1 failed)"
fi

##############################################################################
# CHECK 3 (0.15): BarrelExportResolution struct is extended OR alternative
# mechanism carries the flag
#
# The gold-patch approach adds a field to the struct. But alternatives exist:
#   - Out-parameter on resolveBarrelExport
#   - Separate lookup at the BFS usage site
#   - Tuple/multi-value return
#
# We accept ANY of these.
# GATED behind core fix.
##############################################################################
# [pr_diff] (0.15): Resolution carries star-import info (struct field, out-param, or inline)
add_total 0.15
if [ "$GATE_PASSED" = "1" ]; then
    CARRIES_FLAG=$(python3 << 'PYEOF'
import re, sys

text = open("src/bundler/barrel_imports.zig").read()

# Approach A: New field in BarrelExportResolution struct
struct_match = re.search(
    r'const BarrelExportResolution\s*=\s*struct\s*\{(.*?)\};',
    text, re.DOTALL
)
has_new_struct_field = False
if struct_match:
    body = struct_match.group(1)
    # Original fields: import_record_index, original_alias
    # Any additional field = new
    fields = re.findall(r'(\w+)\s*:', body)
    original = {'import_record_index', 'original_alias'}
    new_fields = [f for f in fields if f not in original]
    if new_fields:
        has_new_struct_field = True

# Approach B: resolveBarrelExport has out-parameter
has_out_param = bool(re.search(
    r'fn resolveBarrelExport\([^)]*\*\s*bool', text
))

# Approach C: resolveBarrelExport returns a different/larger type
has_tuple_return = bool(re.search(
    r'fn resolveBarrelExport\([^)]*\)\s*[^{]*(?:struct|tuple)', text
))

# Approach D: Star info computed inline at BFS site from import records
bfs_match = re.search(
    r'pub fn scheduleBarrelDeferredImports\b(.*)',
    text, re.DOTALL
)
has_inline_lookup = False
if bfs_match:
    bfs_body = bfs_match.group(1)
    res_pos = bfs_body.find('resolveBarrelExport')
    if res_pos >= 0:
        after = bfs_body[res_pos:res_pos + 1200]
        # Look for import_record/import_entry field access near is_star assignment
        if re.search(r'import.+\..*star', after, re.IGNORECASE) or \
           re.search(r'import.+\.name.*len', after):
            has_inline_lookup = True

if has_new_struct_field or has_out_param or has_tuple_return or has_inline_lookup:
    print("PASS")
else:
    print("FAIL")

PYEOF
    )
    if [ "$CARRIES_FLAG" = "PASS" ]; then
        add_score 0.15
        echo "PASS [0.15]: Resolution mechanism carries star-import info"
    else
        echo "FAIL [0.15]: No mechanism found to carry star-import info through resolution"
    fi
else
    echo "SKIP [0.15]: Gated behind core fix (check 1 failed)"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.10)
##############################################################################

# [pr_diff] (0.05): Core structures preserved — resolveBarrelExport and
# scheduleBarrelDeferredImports both still exist with their key logic
add_total 0.05
P2P_CORE=$(python3 << 'PYEOF'
import re
text = open("src/bundler/barrel_imports.zig").read()
has_resolve = 'fn resolveBarrelExport' in text
has_bfs = 'fn scheduleBarrelDeferredImports' in text
has_queue = 'queue' in text and 'append' in text
has_loop = bool(re.search(r'while\s*\(', text))
if has_resolve and has_bfs and has_queue and has_loop:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$P2P_CORE" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Core functions and BFS loop preserved"
else
    echo "FAIL [0.05]: Core functions or BFS loop missing"
fi

# [pr_diff] (0.05): BarrelExportResolution retains original fields
add_total 0.05
P2P_FIELDS=$(python3 << 'PYEOF'
import re
text = open("src/bundler/barrel_imports.zig").read()
struct_match = re.search(
    r'const BarrelExportResolution\s*=\s*struct\s*\{(.*?)\};',
    text, re.DOTALL
)
if struct_match:
    body = struct_match.group(1)
    if 'import_record_index' in body and 'original_alias' in body:
        print('PASS')
    else:
        print('FAIL')
else:
    # Struct might have been refactored — check if the fields exist elsewhere
    # in the resolve function's return
    if 'import_record_index' in text and 'original_alias' in text:
        print('PASS')
    else:
        print('FAIL')
PYEOF
)
if [ "$P2P_FIELDS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Original fields (import_record_index, original_alias) preserved"
else
    echo "FAIL [0.05]: Original resolution fields missing"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16
# Only check CHANGED/NEW lines, not the entire file (existing code may have std.*)
add_total 0.05
BUN_API=$(python3 << 'PYEOF'
import subprocess, re

# Get the diff of what the agent changed
result = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/bundler/barrel_imports.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
diff = result.stdout

# Extract only added lines (agent's new code)
added_lines = [line[1:] for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++')]

# Check for prohibited std.* usage in NEW code only
bad = []
for line in added_lines:
    found = re.findall(r'std\.(fs|posix|os|process)\.', line)
    bad.extend(found)

print('PASS' if len(bad) == 0 else 'FAIL')
PYEOF
)
if [ "$BUN_API" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: No prohibited std.* API usage in new code"
else
    echo "FAIL [0.05]: Prohibited std.* API usage in agent's new code"
fi

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:8
# Only check agent's new/changed code
add_total 0.05
NO_INLINE=$(python3 << 'PYEOF'
import subprocess, re

result = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/bundler/barrel_imports.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
diff = result.stdout

added_lines = [line[1:] for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++')]
has_inline = any('@import(' in line for line in added_lines)
print('PASS' if not has_inline else 'FAIL')
PYEOF
)
if [ "$NO_INLINE" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: No inline @import() in agent's new code"
else
    echo "FAIL [0.05]: Found @import() inline in agent's new code"
fi

##############################################################################
# FINAL SCORE
##############################################################################
FINAL=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "=== FINAL SCORE: $FINAL (raw: $SCORE / $TOTAL) ==="
echo "$FINAL" > /logs/verifier/reward.txt

python3 << PYEOF
import json
score = $SCORE
total = $TOTAL
final = round(score / total, 4) if total > 0 else 0.0

data = {
    "reward": final,
    "behavioral": round(min(0.75, score) / total, 4) if total > 0 else 0.0,
    "regression": round(min(0.10, max(0, score - 0.75)) / total, 4) if total > 0 else 0.0,
    "config": round(min(0.10, max(0, score - 0.85)) / total, 4) if total > 0 else 0.0,
    "style_rubric": 0.0
}
json.dump(data, open("/logs/verifier/reward.json", "w"))
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
