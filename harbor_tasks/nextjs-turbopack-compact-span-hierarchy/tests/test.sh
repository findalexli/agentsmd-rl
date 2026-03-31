#!/usr/bin/env bash
# Verifier for nextjs-turbopack-compact-span-hierarchy
#
# Bug: The "compact database" tracing span lives inside db.rs, inheriting the
# wrong parent and creating one span per compaction iteration.  It should be
# moved to the backend call site (mod.rs) with a shared root span.
#
# All checks are source-inspection because:
#   - Rust code in turbopack workspace (~200+ crates), no Rust toolchain in image
#   - cargo check would take 10+ min, exceeding timeout
#
# Every check is a "structural fail-to-pass": it FAILS on the base commit and
# PASSES on a correct fix.  Checks are written to accept alternative valid
# implementations (different span names, different parent-passing mechanisms).
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

DB_FILE="/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs"
MOD_FILE="/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$DB_FILE" ] || [ ! -f "$MOD_FILE" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff] (0.25): F2P — compact span removed from db.rs
#   TEST 2 [pr_diff] (0.20): F2P — compact-related span added to mod.rs
#   TEST 3 [pr_diff] (0.15): F2P — root span (parent: None) in mod.rs
#   TEST 4 [pr_diff] (0.10): F2P — "sync new files" no longer info-level
#   TEST 5 [pr_diff] (0.10): F2P — snapshot_and_persist not called with None
#   TEST 6 [pr_diff] (0.10): P2P — compact() call still in mod.rs
#   TEST 7 [structural] (0.05): Anti-stub — mod.rs has substantial content
#   TEST 8 [agent_config] (0.05): cargo fmt — CLAUDE.md:414 @ df886d4a
#   TOTAL                 = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# TEST 1 [pr_diff] (0.25): F2P — compact span REMOVED from db.rs
# The compact() method in db.rs must no longer create its own tracing span.
# Accepts: removal, or moving the span elsewhere.  Flexible on naming — checks
# for any tracing span macro (info_span, trace_span, span, debug_span) whose
# name contains "compact" (case-insensitive).
# Base commit: FAILS (has info_span!("compact database"))
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.25) No compact-related tracing span created in db.rs"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs") as f:
    src = f.read()

# Match any tracing span macro whose string argument contains "compact"
# This catches: info_span!("compact database"), trace_span!("compact db"),
#   span!(Level::INFO, "compaction"), debug_span!("compact"), etc.
# Excludes comments (lines starting with //)
span_pattern = re.compile(
    r'^\s*(?!.*//.*compact)'           # not a comment line with "compact"
    r'.*(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)'
    r'\s*\([^)]*"[^"]*compact[^"]*"',  # string arg contains "compact"
    re.IGNORECASE | re.MULTILINE
)

matches = span_pattern.findall(src)
if matches:
    print(f"  FAIL: Found compact-related span(s) still in db.rs:")
    for m in matches[:3]:
        print(f"    {m.strip()[:100]}")
    sys.exit(1)
else:
    print("  PASS: No compact-related tracing span in db.rs")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi

###############################################################################
# TEST 2 [pr_diff] (0.20): F2P — compact-related span ADDED to mod.rs
# The compact span should now be created in mod.rs (the call site).
# Flexible: accepts any span name containing "compact" (case-insensitive),
# created via any tracing macro.  Also accepts a span created near the
# .compact() call (within 15 lines).
# Base commit: FAILS (no compact span in mod.rs)
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.20) Compact-related tracing span exists in mod.rs"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    lines = f.readlines()
    src = "".join(lines)

# Strategy A: span macro with "compact" in its name
span_with_compact = re.compile(
    r'(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)'
    r'\s*\([^)]*"[^"]*compact[^"]*"',
    re.IGNORECASE
)
if span_with_compact.search(src):
    print("  PASS: Found compact-related tracing span in mod.rs")
    sys.exit(0)

# Strategy B: a tracing span macro within 15 lines of a .compact() call
compact_call_lines = [i for i, l in enumerate(lines) if '.compact()' in l]
span_macro = re.compile(r'(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\(')
for cl in compact_call_lines:
    window = "".join(lines[max(0, cl-15):cl+5])
    if span_macro.search(window):
        print("  PASS: Found tracing span near .compact() call in mod.rs")
        sys.exit(0)

print("  FAIL: No compact-related tracing span found in mod.rs")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): F2P — root span in mod.rs
# A shared root span must be created for background work.  Accepts:
#   - parent: None (standard tracing root span)
#   - Span::none() as parent
#   - Any new root span creation near snapshot/persist/compact code
# Flexible on span name — any name is fine.
# Base commit: FAILS (no root span in mod.rs)
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.15) Root span (parent: None) exists in mod.rs"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Check for parent: None in a span macro context
root_span_patterns = [
    r'(?:info_span!|trace_span!|debug_span!|span!)\s*\(\s*parent\s*:\s*None',
    r'parent\s*:\s*None\s*,\s*"',     # parent: None, "some name"
    r'Span::none\(\)',                  # Alternative root span mechanism
]

for pat in root_span_patterns:
    if re.search(pat, src):
        print("  PASS: Root span found in mod.rs")
        sys.exit(0)

print("  FAIL: No root span (parent: None) found in mod.rs")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): F2P — "sync new files" no longer info-level
# The "sync new files" span should be downgraded from info to trace (or lower),
# or removed entirely.
# Accepts: trace_span!, debug_span!, span!(Level::TRACE, ...), or removal.
# Base commit: FAILS (uses info_span!)
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) 'sync new files' not at info level in db.rs"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs") as f:
    src = f.read()

# If "sync new files" doesn't appear at all, that's fine (removed entirely)
if '"sync new files"' not in src:
    print("  PASS: 'sync new files' span removed entirely")
    sys.exit(0)

# Find lines with "sync new files"
for line in src.split('\n'):
    if '"sync new files"' in line:
        # FAIL if it still uses info_span! or warn_span!
        if re.search(r'info_span!|warn_span!', line):
            print("  FAIL: 'sync new files' still at info level or higher")
            sys.exit(1)
        # PASS if it uses trace_span!, debug_span!, or span! with trace/debug
        if re.search(r'trace_span!|debug_span!|Level::TRACE|Level::DEBUG', line):
            print("  PASS: 'sync new files' downgraded below info")
            sys.exit(0)

# If we found the string but couldn't determine level, check surrounding context
lines = src.split('\n')
for i, line in enumerate(lines):
    if '"sync new files"' in line:
        context = '\n'.join(lines[max(0,i-3):i+1])
        if re.search(r'info_span!|warn_span!', context):
            print("  FAIL: 'sync new files' still at info level")
            sys.exit(1)
        else:
            print("  PASS: 'sync new files' not at info level")
            sys.exit(0)

print("  FAIL: Could not determine 'sync new files' span level")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

###############################################################################
# TEST 5 [pr_diff] (0.10): F2P — snapshot_and_persist not called with None
# The first argument to snapshot_and_persist should pass a span id, not None.
# Accepts any non-None value (variable, method call, expression).
# Also accepts: removing the None parameter entirely, changing the function
# signature to receive span info via struct field or other mechanism.
# Base commit: FAILS (called with None)
###############################################################################
echo ""
echo "TEST 5: [pr_diff] (0.10) snapshot_and_persist not called with None"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Find all snapshot_and_persist calls and check first argument
calls = re.findall(r'snapshot_and_persist\(\s*([^,\)]+)', src)
if not calls:
    # Function might have been renamed or restructured — if there's no call
    # with None, that's acceptable
    if 'snapshot_and_persist' not in src:
        print("  PASS: snapshot_and_persist not found (restructured)")
        sys.exit(0)
    print("  FAIL: snapshot_and_persist exists but no calls found")
    sys.exit(1)

for arg in calls:
    arg = arg.strip()
    if arg == 'None':
        print("  FAIL: snapshot_and_persist still called with None")
        sys.exit(1)

print(f"  PASS: snapshot_and_persist called with non-None arg ({calls[0].strip()[:50]})")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

###############################################################################
# TEST 6 [pr_diff] (0.10): P2P — compact() call still present
# The compaction logic must still invoke compact() on the backing storage.
###############################################################################
echo ""
echo "TEST 6: [pr_diff] (0.10) Pass-to-pass — compact() call still in mod.rs"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Accept .compact() call in any form
if re.search(r'\.compact\(\)', src):
    print("  PASS: compact() call still present in mod.rs")
    sys.exit(0)
else:
    print("  FAIL: compact() call missing from mod.rs")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

###############################################################################
# TEST 7 [structural] (0.05): Anti-stub — mod.rs has substantial content
###############################################################################
echo ""
echo "TEST 7: [structural] (0.05) Anti-stub check on mod.rs"
LINE_COUNT=$(wc -l < "$MOD_FILE")
if [ "$LINE_COUNT" -gt 2000 ]; then
    echo "  PASS: mod.rs has $LINE_COUNT lines (substantial)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "  FAIL: mod.rs has only $LINE_COUNT lines (possible stub)"
fi

###############################################################################
# TEST 8 [agent_config] (0.05): cargo fmt — CLAUDE.md:414 @ df886d4a
# "cargo fmt uses ASCII order" — no tabs, no trailing whitespace in changed files.
# WHY not call cargo fmt: Rust toolchain not installed in test container.
###############################################################################
echo ""
echo "TEST 8: [agent_config] (0.05) No obvious formatting issues (CLAUDE.md:414)"
python3 << 'PYEOF'
import sys

issues = []
for filepath in [
    "/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs",
    "/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"
]:
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if '\t' in line and not line.strip().startswith('//'):
            issues.append(f"{filepath}:{i+1}: tab character")
        if line.rstrip('\n') != line.rstrip('\n').rstrip() and len(line.strip()) > 0:
            issues.append(f"{filepath}:{i+1}: trailing whitespace")

if issues:
    print("  FAIL: Formatting issues found:")
    for issue in issues[:5]:
        print(f"    {issue}")
    sys.exit(1)
else:
    print("  PASS: No obvious formatting issues")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "================================"
echo "FINAL SCORE: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
