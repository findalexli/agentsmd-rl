#!/usr/bin/env bash
# Verifier for nextjs-turbo-persistence-mmap-alignment
#
# Bug: mmap offset not page-aligned; missing error context in open_internal.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

META_FILE="/workspace/next.js/turbopack/crates/turbo-persistence/src/meta_file.rs"
MMAP_HELPER="/workspace/next.js/turbopack/crates/turbo-persistence/src/mmap_helper.rs"

###############################################################################
# GATE: Files exist
###############################################################################
for f in "$META_FILE" "$MMAP_HELPER"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAILED: $f missing"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: mmap offset removed)              = 0.30
#   TEST 2 (fail-to-pass: amqf_data_start field added)      = 0.25
#   TEST 3 (fail-to-pass: error context in mmap_helper)     = 0.10
#   TEST 4 (structural: error context in meta_file)         = 0.20
#   TEST 5 (anti-stub)                                      = 0.10
#   TEST 6 (config-derived: Do NOT add Generated with Claude Code footers)    = 0.05
#   TOTAL                                                      = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: mmap offset removed — no options.offset()
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] mmap offset removed - maps entire file from byte 0"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/meta_file.rs") as f:
    src = f.read()

# The buggy code has: options.offset(offset);
# The fix removes this and uses MmapOptions::new().map(&file) directly
if 'options.offset(offset)' in src or 'options.offset(' in src:
    print("FAIL: options.offset() still present — mmap offset not removed")
    sys.exit(1)

# Verify MmapOptions::new().map is used instead
if 'MmapOptions::new()' in src and '.map(' in src:
    print("PASS: MmapOptions::new().map() used without offset")
    sys.exit(0)

# Alternative: check that offset is not passed to mmap options
if 'offset' not in src.split('fn open_internal')[1].split('fn ')[0] if 'fn open_internal' in src else '':
    print("PASS: no offset usage in open_internal")
    sys.exit(0)

print("FAIL: could not verify mmap offset removal")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: amqf_data_start field added to MetaFile
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] amqf_data_start field added to MetaFile struct"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/meta_file.rs") as f:
    src = f.read()

# Check for the new field
if 'amqf_data_start' in src:
    # Verify it's used in amqf_data() method
    if 'self.amqf_data_start' in src and 'self.mmap[self.amqf_data_start' in src:
        print("PASS: amqf_data_start field exists and used in amqf_data() method")
        sys.exit(0)
    elif 'amqf_data_start' in src:
        print("PASS: amqf_data_start field exists")
        sys.exit(0)

print("FAIL: amqf_data_start field not found")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.10]: Error context in mmap_helper.rs
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] error context added in mmap_helper.rs"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/mmap_helper.rs") as f:
    src = f.read()

# The fix adds .context() calls and imports anyhow::Context
has_context_import = 'Context' in src and 'anyhow' in src
has_dontfork_context = 'DontFork' in src and '.context(' in src
has_unmergeable_context = 'Unmergeable' in src and '.context(' in src

if has_context_import and (has_dontfork_context or has_unmergeable_context):
    print("PASS: error context added in mmap_helper.rs")
    sys.exit(0)

# Count .context( occurrences
context_count = src.count('.context(')
if context_count >= 2:
    print(f"PASS: {context_count} .context() calls found in mmap_helper.rs")
    sys.exit(0)

print("FAIL: error context not found in mmap_helper.rs")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL, 0.20]: Error context in meta_file.rs
###############################################################################
echo ""
echo "TEST 4: [structural] error context added in meta_file.rs"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-persistence/src/meta_file.rs") as f:
    src = f.read()

# Check for context strings
contexts_found = 0
expected = [
    'Failed to open meta file',
    'Failed to get stream position',
    'Failed to mmap',
    'Failed to advise mmap',
]

for ctx in expected:
    if ctx in src:
        contexts_found += 1

if contexts_found >= 3:
    print(f"PASS: {contexts_found}/{len(expected)} error contexts found")
    sys.exit(0)

# Alternative: just count .context( calls in the file
context_count = src.count('.context(')
if context_count >= 3:
    print(f"PASS: {context_count} .context() calls found")
    sys.exit(0)

print(f"FAIL: only {contexts_found} expected contexts and {src.count('.context(')} .context() calls found")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.15]: Files have substantial content
###############################################################################
echo ""
echo "TEST 5: [anti-stub] files have substantial content"
python3 << 'PYEOF'
import sys

for path, min_lines in [
    ("/workspace/next.js/turbopack/crates/turbo-persistence/src/meta_file.rs", 100),
    ("/workspace/next.js/turbopack/crates/turbo-persistence/src/mmap_helper.rs", 5),
]:
    with open(path) as f:
        lines = len(f.readlines())
    if lines < min_lines:
        print(f"FAIL: {path} has {lines} lines (expected >= {min_lines})")
        sys.exit(1)

print("PASS: files have substantial content")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.05]: Do NOT add Generated with Claude Code footers
###############################################################################
echo ""
echo "TEST 6: [config-derived] Do NOT add Generated with Claude Code footers"
# Source: CLAUDE.md line 348 @ bdb2f2ce4dea0c1435af5fa433767d63fca11c0c
node -e "
const {execSync} = require('child_process');
try {
    const log = execSync('git log --format=%B -n5 2>/dev/null || true', {encoding: 'utf8', cwd: '/workspace/next.js'});
    if (log.includes('Generated with Claude') || log.includes('Co-Authored-By: Claude')) {
        console.log('FAIL: commit message contains Claude footer');
        process.exit(1);
    }
} catch(e) {}
console.log('PASS');
"
T6=$?
echo "  -> exit code: $T6"

# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.20 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: mmap offset removed)       = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: amqf_data_start field)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: mmap_helper context)       = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (structural: meta_file context)            = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 5 (anti-stub)                                = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
