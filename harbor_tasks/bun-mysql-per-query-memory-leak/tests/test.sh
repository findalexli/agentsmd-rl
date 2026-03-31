#!/usr/bin/env bash
set +e

REPO="/repo"
REWARD=0
TOTAL=0
DETAILS=""

add_check() {
    local name="$1" weight="$2" pass="$3" comment="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        REWARD=$(python3 -c "print($REWARD + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $comment\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $comment\n"
    fi
}

gate_fail() {
    echo -e "$DETAILS"
    echo "GATE FAILED: $1"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
}

# ============================================================
# GATE: Modified files must exist and have balanced braces
# ============================================================

COLDEF="$REPO/src/sql/mysql/protocol/ColumnDefinition41.zig"
PREPSTMT="$REPO/src/sql/mysql/protocol/PreparedStatement.zig"
MYSTMT="$REPO/src/sql/mysql/MySQLStatement.zig"
MYCONN="$REPO/src/sql/mysql/MySQLConnection.zig"

for f in "$COLDEF" "$PREPSTMT" "$MYSTMT" "$MYCONN"; do
    if [ ! -f "$f" ]; then
        gate_fail "File not found: $f"
    fi
done

for f in "$COLDEF" "$PREPSTMT" "$MYSTMT" "$MYCONN"; do
    OPEN=$(grep -o '{' "$f" | wc -l)
    CLOSE=$(grep -o '}' "$f" | wc -l)
    if [ "$OPEN" -ne "$CLOSE" ]; then
        gate_fail "Unmatched braces in $(basename $f): open=$OPEN close=$CLOSE"
    fi
done

# ============================================================
# Helper: strip Zig single-line comments from source
# This prevents comment-injection gaming
# ============================================================

strip_zig_comments() {
    python3 -c "
import re, sys
src = open(sys.argv[1]).read()
# Remove // comments (but not inside strings)
stripped = re.sub(r'//[^\n]*', '', src)
print(stripped)
" "$1"
}

# ============================================================
# BEHAVIORAL / STRUCTURAL CHECKS (0.65 total)
# Zig code requires full Bun build (WebKit/JSC deps) — cannot
# be executed in test container. All checks are structural but
# designed to test semantic correctness of memory management.
# ============================================================

# [pr_diff] (0.25): ColumnDefinition41.deinit() must free ALL heap-owning fields
# The struct has Data fields (catalog, schema, table, org_table, name, org_name)
# plus name_or_index (ColumnIdentifier). ALL must be freed in deinit.
# This is a semantic check: does deinit free every field? Not just name_or_index.
PASS=0
if python3 -c "
import re

# Strip comments to prevent gaming
src = open('$COLDEF').read()
src_clean = re.sub(r'//[^\n]*', '', src)

# Find deinit function
match = re.search(r'pub fn deinit\(.*?\bColumnDefinition41\b.*?void\s*\{(.*?)\n\s*\}', src_clean, re.DOTALL)
if not match:
    exit(1)
body = match.group(1)

# All 7 heap fields that must be freed (6 Data fields + name_or_index)
required_fields = ['catalog', 'schema', 'table', 'org_table', 'name', 'org_name', 'name_or_index']
freed = set()
for field in required_fields:
    # Accept: this.FIELD.deinit(), self.FIELD.deinit(), or via defer/helper
    if re.search(r'(?:this|self)\.' + field + r'\.deinit\(\)', body):
        freed.add(field)
    elif re.search(r'defer\s+.*' + field + r'.*\.deinit', body):
        freed.add(field)

if freed == set(required_fields):
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "coldef_deinit_all_fields" 0.25 "$PASS" \
    "[pr_diff] (0.25): ColumnDefinition41.deinit() frees ALL heap-owning fields including name_or_index"

# [pr_diff] (0.20): decodeInternal() must free name_or_index before reassignment
# When re-decoding columns, the old ColumnIdentifier must be freed before assigning a new one.
# Accept any mechanism: explicit deinit-before-assign, defer, swap pattern.
PASS=0
if python3 -c "
import re

src = open('$COLDEF').read()
src_clean = re.sub(r'//[^\n]*', '', src)

# Find decodeInternal function body (may span many lines)
match = re.search(r'pub fn decodeInternal\b[^{]*\{(.*?)(?=\npub fn |\n\s*\};)', src_clean, re.DOTALL)
if not match:
    exit(1)
body = match.group(1)

# The function assigns to name_or_index. Before that assignment, the old value must be freed.
# Strategy: find ALL lines, check that some deinit/free of name_or_index occurs before reassignment.
assign_match = re.search(r'name_or_index\s*=\s*(?:try\s+)?(?:ColumnIdentifier|\.)', body)
if not assign_match:
    exit(1)  # No assignment found — either not the right function or already removed

before = body[:assign_match.start()]

# Accept: .deinit(), .free(), defer pattern, or explicit free call
if re.search(r'name_or_index\.deinit\(\)', before):
    exit(0)
if re.search(r'name_or_index\.free\(\)', before):
    exit(0)
if re.search(r'defer\s+.*name_or_index.*\.deinit', before):
    exit(0)

exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "coldef_decode_free_before_reassign" 0.20 "$PASS" \
    "[pr_diff] (0.20): decodeInternal() frees name_or_index before reassigning (prevents per-query leak)"

# [pr_diff] (0.10): Execute.deinit() must free the params slice allocation
# The buggy code frees individual param values but not the slice itself.
# Accept: allocator.free(this.params), bun.default_allocator.free(this.params), etc.
PASS=0
if python3 -c "
import re

src = open('$PREPSTMT').read()
src_clean = re.sub(r'//[^\n]*', '', src)

# Find Execute.deinit
match = re.search(r'pub fn deinit\(.*?\bExecute\b.*?void\s*\{(.*?)\n\s{4}\}', src_clean, re.DOTALL)
if not match:
    # Try broader match
    match = re.search(r'Execute = struct\s*\{(.*?)(?=\n\s{4}pub const|\nconst\s)', src_clean, re.DOTALL)
    if match:
        deinit_match = re.search(r'pub fn deinit\(.*?\) void \{(.*?)\n\s{8}\}', match.group(1), re.DOTALL)
        if deinit_match:
            match = deinit_match
if not match:
    exit(1)
body = match.group(1)

# Must free the params slice (not just iterate and free individual params)
# Accept: .free(this.params), .free(self.params), or similar patterns
if re.search(r'\.free\(\s*(?:this|self)\.params\s*\)', body):
    exit(0)
# Also accept: dealloc pattern
if re.search(r'(?:dealloc|destroy)\(\s*(?:this|self)\.params', body):
    exit(0)

exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "execute_deinit_free_params_slice" 0.10 "$PASS" \
    "[pr_diff] (0.10): Execute.deinit() frees the params slice allocation (not just individual values)"

# [pr_diff] (0.10): checkForDuplicateFields must free name_or_index before overwriting
# When a duplicate column is found, the old name_or_index (heap-allocated) must be
# freed before being replaced with the .duplicate sentinel.
PASS=0
if python3 -c "
import re

src = open('$MYSTMT').read()
src_clean = re.sub(r'//[^\n]*', '', src)

match = re.search(r'(?:pub )?fn checkForDuplicateFields\b[^{]*\{(.*?)(?=\n(?:pub )?fn |\nconst )', src_clean, re.DOTALL)
if not match:
    exit(1)
body = match.group(1)

# Find the block where found_existing leads to .duplicate assignment
# The old name_or_index must be freed before the new value is assigned
dup_assign = re.search(r'name_or_index\s*=\s*\.duplicate', body)
if not dup_assign:
    exit(1)

# Look for deinit/free of name_or_index before the .duplicate assignment
before = body[:dup_assign.start()]
# Find the nearest enclosing block (found_existing check)
block_start = before.rfind('found_existing')
if block_start < 0:
    block_start = max(0, dup_assign.start() - 300)
between = before[block_start:]

if re.search(r'name_or_index\.deinit\(\)', between):
    exit(0)
if re.search(r'name_or_index\.free\(\)', between):
    exit(0)
if re.search(r'defer\s+.*name_or_index.*\.deinit', between):
    exit(0)

exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "check_dup_free_before_duplicate" 0.10 "$PASS" \
    "[pr_diff] (0.10): checkForDuplicateFields frees name_or_index before overwriting with .duplicate"

# ============================================================
# REGRESSION / PASS-TO-PASS (0.15 total)
# Existing cleanup logic must still be present
# ============================================================

# [pr_diff] (0.05): ColumnDefinition41.deinit() still frees all original Data fields
PASS=0
SRC_CLEAN=$(strip_zig_comments "$COLDEF")
if echo "$SRC_CLEAN" | grep -q 'this\.catalog\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q 'this\.schema\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q 'this\.table\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q 'this\.org_table\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q 'this\.name\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q 'this\.org_name\.deinit()'; then
    PASS=1
fi
add_check "coldef_existing_deinit_intact" 0.05 "$PASS" \
    "[pr_diff] (0.05): ColumnDefinition41.deinit() still frees all original Data fields"

# [pr_diff] (0.05): Execute.deinit() still frees individual param values
PASS=0
SRC_CLEAN=$(strip_zig_comments "$PREPSTMT")
if echo "$SRC_CLEAN" | grep -q 'param\.deinit('; then
    PASS=1
fi
add_check "execute_individual_param_deinit" 0.05 "$PASS" \
    "[pr_diff] (0.05): Execute.deinit() still frees individual param values"

# [pr_diff] (0.05): MySQLStatement.deinit() still frees columns and params
PASS=0
SRC_CLEAN=$(strip_zig_comments "$MYSTMT")
if echo "$SRC_CLEAN" | grep -q 'column\.deinit()' && \
   echo "$SRC_CLEAN" | grep -q '\.free(this\.columns)'; then
    PASS=1
fi
add_check "mystmt_deinit_intact" 0.05 "$PASS" \
    "[pr_diff] (0.05): MySQLStatement.deinit() still frees columns array"

# ============================================================
# STRUCTURAL / ANTI-STUB (0.10 total)
# ============================================================

# [static] (0.05): ColumnDefinition41 struct still has name_or_index field
PASS=0
SRC_CLEAN=$(strip_zig_comments "$COLDEF")
if echo "$SRC_CLEAN" | grep -q 'name_or_index:'; then
    PASS=1
fi
add_check "coldef_has_name_or_index_field" 0.05 "$PASS" \
    "[static] (0.05): ColumnDefinition41 still defines name_or_index field"

# [static] (0.05): Fix is not a stub — deinit has real cleanup code (not just comments)
PASS=0
if python3 -c "
import re

src = open('$COLDEF').read()
src_clean = re.sub(r'//[^\n]*', '', src)

match = re.search(r'pub fn deinit\(.*?\bColumnDefinition41\b.*?void\s*\{(.*?)\n\s*\}', src_clean, re.DOTALL)
if not match:
    exit(1)
body = match.group(1)
# Count actual code lines (non-empty, non-comment after stripping)
code_lines = [l.strip() for l in body.split('\n') if l.strip()]
deinit_calls = [l for l in code_lines if '.deinit()' in l]
# Need at least 7 deinit calls on real code lines (6 Data + name_or_index)
if len(deinit_calls) >= 7:
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "not_stub" 0.05 "$PASS" \
    "[static] (0.05): deinit function has full cleanup body (anti-stub, comments stripped)"

# ============================================================
# CONFIG-DERIVED (0.10 total)
# ============================================================

# [agent_config] (0.05): Uses bun.default_allocator for memory ops — src/CLAUDE.md:25-35 @ 9a27ef75
# "Always use bun.* APIs instead of std.*"
PASS=0
if python3 -c "
import re

src = open('$PREPSTMT').read()
src_clean = re.sub(r'//[^\n]*', '', src)

# Find Execute.deinit body
match = re.search(r'pub fn deinit\(.*?\bExecute\b.*?void\s*\{(.*?)\n\s{4}\}', src_clean, re.DOTALL)
if not match:
    match = re.search(r'Execute = struct\s*\{(.*?)(?=\n\s{4}pub const|\nconst\s)', src_clean, re.DOTALL)
    if match:
        dm = re.search(r'pub fn deinit\(.*?\) void \{(.*?)\n\s{8}\}', match.group(1), re.DOTALL)
        if dm: match = dm
if not match:
    exit(1)
body = match.group(1)

# If there's a free of params, it should use bun.default_allocator (not std.heap)
if re.search(r'\.free\(', body):
    # Must use bun allocator, not std
    if 'bun.default_allocator' in body or 'bun.' in body:
        if 'std.heap' not in body:
            exit(0)
else:
    # No free call — might be using a different pattern; just check no std usage
    if 'std.heap' not in body and 'std.mem.Allocator' not in body:
        exit(0)
exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "uses_bun_allocator" 0.05 "$PASS" \
    "[agent_config] (0.05): \"Always use bun.* APIs instead of std.*\" — src/CLAUDE.md:25-35 @ 9a27ef75"

# [agent_config] (0.05): Newly allocated columns are zero-initialized — CLAUDE.md @ 9a27ef75
# After alloc of ColumnDefinition41 array, columns must be initialized to avoid
# undefined name_or_index (which would crash on deinit).
PASS=0
if python3 -c "
import re

src = open('$MYCONN').read()
src_clean = re.sub(r'//[^\n]*', '', src)

# Find all places where ColumnDefinition41 arrays are allocated
matches = list(re.finditer(r'alloc\(\s*ColumnDefinition41\s*,', src_clean))
if not matches:
    exit(1)

all_init = True
for m in matches:
    # Check next ~300 chars for initialization
    after = src_clean[m.end():m.end()+300]
    # Accept: zero-init loop (col.* = .{}), @memset, .init(), std.mem.zeroes
    if not re.search(r'(col\.\*\s*=\s*\.{}|@memset|\.init\(\)|std\.mem\.zeroes|= \.{})', after):
        all_init = False
        break

if all_init:
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS=1
fi
add_check "column_zero_init" 0.05 "$PASS" \
    "[agent_config] (0.05): Newly allocated columns are zero-initialized — CLAUDE.md @ 9a27ef75"

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Total: $REWARD / $TOTAL"

echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
reward = $REWARD
print(json.dumps({
    'reward': round(reward, 2),
    'behavioral': round(reward, 2),
    'regression': 0.0,
    'config': 0.0,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
