#!/usr/bin/env bash
# Verifier for nextjs-turbopack-cache-stats-deadlock
#
# Bug: When print_cache_item_size is enabled, persist_snapshot deadlocks because
# get_task_name acquires a write lock on a DashMap shard already read-locked.
#
# All checks are structural (file-inspection) because:
# - This is Rust code in the turbopack workspace requiring ~200+ crates to compile
# - cargo check would take 10+ minutes, exceeding test timeout
# - The deadlock is a runtime concurrency issue needing the full turbo-tasks runtime
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

MOD_FILE="/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"
CARGO_FILE="/workspace/next.js/turbopack/crates/turbo-tasks-backend/Cargo.toml"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$MOD_FILE" ] || [ ! -f "$CARGO_FILE" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]    (0.30): F2P — deadlock removed AND stats code preserved
#   TEST 2 [pr_diff]    (0.15): F2P — task name still used as stats grouping key
#   TEST 3 [pr_diff]    (0.15): F2P — Cargo feature split (lzzzz decoupled)
#   TEST 4 [pr_diff]    (0.10): F2P — add_counts condition covers data OR meta
#   TEST 5 [pr_diff]    (0.15): P2P — persist_snapshot + TaskCacheStats intact
#   TEST 6 [structural] (0.15): Anti-stub/anti-deletion of instrumentation code
#   TOTAL               = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# TEST 1 [pr_diff] (0.30): Deadlock fix — self.get_task_name must NOT appear
# in stats.entry() calls or anywhere in cfg(print_cache_item_size) blocks,
# AND the stats collection code must still exist (not just deleted).
#
# WHY structural: Rust code requiring full turbopack workspace (~200 crates);
# the deadlock is a runtime concurrency issue that cannot be triggered in isolation.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.30) Deadlock pattern removed, stats code preserved"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Part A: self.get_task_name must NOT appear in stats.entry() calls
entry_calls = re.findall(r'\.entry\(([^)]*self\.get_task_name[^)]*)\)', src)
if entry_calls:
    print(f"FAIL: stats.entry() still calls self.get_task_name (deadlock source): {entry_calls[0][:60]}")
    sys.exit(1)

# Part B: self.get_task_name must NOT appear inside cfg(print_cache_item_size) blocks
in_cfg_block = False
brace_depth = 0
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg_block = True
        brace_depth = 0
        continue
    if in_cfg_block:
        brace_depth += line.count('{') - line.count('}')
        if 'self.get_task_name' in line:
            print(f"FAIL: self.get_task_name at line {i+1} inside cfg-gated block")
            sys.exit(1)
        if brace_depth <= 0 and '{' not in line and '}' not in line:
            in_cfg_block = False
            brace_depth = 0

# Part C: Anti-deletion — the stats .entry() call must still exist somewhere
# in a cfg(print_cache_item_size) block (can't just delete all stats code)
in_cfg_block = False
brace_depth = 0
found_entry = False
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg_block = True
        brace_depth = 0
        continue
    if in_cfg_block:
        brace_depth += line.count('{') - line.count('}')
        if '.entry(' in line:
            found_entry = True
            break
        if brace_depth <= 0 and '{' not in line and '}' not in line:
            in_cfg_block = False
            brace_depth = 0

if not found_entry:
    print("FAIL: No .entry() call found in cfg(print_cache_item_size) blocks — stats code deleted?")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 2 [pr_diff] (0.15): Task name/type still used as stats grouping key.
# The fix must retrieve the task name/type WITHOUT going through self.get_task_name.
# Accept any approach: get_persistent_task_type, task_name(), task_type(),
# pre-collected names, etc. — just not self.get_task_name.
#
# WHY structural: Same — Rust code, can't compile.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.15) Task name/type still used for stats grouping"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# In the cfg(print_cache_item_size) blocks, find .entry() calls and check
# their argument references some form of task name/type lookup.
in_cfg_block = False
brace_depth = 0
entry_args = []
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg_block = True
        brace_depth = 0
        continue
    if in_cfg_block:
        brace_depth += line.count('{') - line.count('}')
        # Collect .entry() call and surrounding context
        match = re.search(r'\.entry\((.+?)(?:\)|\s*$)', line)
        if match:
            # Gather context: the entry arg might span nearby lines
            context = '\n'.join(lines[max(0, i-5):i+3])
            entry_args.append(context)
        if brace_depth <= 0 and '{' not in line and '}' not in line:
            in_cfg_block = False
            brace_depth = 0

if not entry_args:
    print("FAIL: No .entry() call found in cfg blocks — can't verify task name usage")
    sys.exit(1)

# Check that at least one entry call has task-name-related content nearby.
# Accept broad patterns: task_name, task_type, persistent_task_type, get_task,
# TaskCacheStats::task, etc. — anything that references task identification.
task_patterns = [
    r'task_name',
    r'task_type',
    r'persistent_task_type',
    r'get_task',
    r'TaskCacheStats::',
    r'task_desc',
    r'\.name\b',
    r'to_string\(\)',  # common pattern: something.to_string() as key
]

found_task_ref = False
for ctx in entry_args:
    for pat in task_patterns:
        if re.search(pat, ctx):
            found_task_ref = True
            break
    if found_task_ref:
        break

if not found_task_ref:
    print("FAIL: .entry() calls don't reference task name/type — stats not grouped by task")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): Cargo feature split — print_cache_item_size
# no longer depends on lzzzz; a separate feature enables compressed reporting.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.15) print_cache_item_size decoupled from lzzzz"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/Cargo.toml") as f:
    content = f.read()

# Parse the [features] section
in_features = False
features = {}
for line in content.split('\n'):
    stripped = line.strip()
    if stripped == '[features]':
        in_features = True
        continue
    if in_features and stripped.startswith('[') and stripped != '[features]':
        break
    if in_features and '=' in stripped:
        name, val = stripped.split('=', 1)
        features[name.strip()] = val.strip()

# Check print_cache_item_size does NOT depend on lzzzz
pci = features.get('print_cache_item_size', '')
if 'lzzzz' in pci:
    print("FAIL: print_cache_item_size still depends on lzzzz")
    sys.exit(1)

if 'print_cache_item_size' not in features:
    print("FAIL: print_cache_item_size feature missing entirely")
    sys.exit(1)

# Check that some feature depends on both print_cache_item_size and lzzzz
# (the compressed variant — name doesn't matter)
found_compressed = False
for name, val in features.items():
    if name != 'print_cache_item_size' and 'print_cache_item_size' in val and 'lzzzz' in val:
        found_compressed = True
        break

if not found_compressed:
    print("FAIL: No feature found that extends print_cache_item_size with lzzzz")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): add_counts condition covers encode_data || encode_meta
# Bug: previously only checked encode_meta, missing data-only tasks from stats.
#
# WHY structural: Same — Rust code, can't compile.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) add_counts triggered on data OR meta modified"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Look for add_counts in the file and check that encode_data is part of its
# guarding condition (within 10 lines before or 2 lines after).
lines = src.split('\n')
found = False
for i, line in enumerate(lines):
    if 'add_counts' in line:
        context = '\n'.join(lines[max(0, i-10):i+3])
        if 'encode_data' in context:
            found = True
            break

if not found:
    # Alternative: maybe encode_data was inlined or the condition restructured
    # so add_counts is always called (e.g., unconditionally inside the cfg block)
    # Check if add_counts appears without ANY encode_meta-only guard
    for i, line in enumerate(lines):
        if 'add_counts' in line:
            context = '\n'.join(lines[max(0, i-5):i+1])
            # If there's no "if encode_meta" without encode_data, that's also valid
            if 'encode_meta' not in context:
                found = True  # no gate at all, or different gate
                break
            elif 'encode_data' in context:
                found = True
                break

if not found:
    print("FAIL: add_counts still guarded by encode_meta only — data-only tasks excluded from stats")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 5 [pr_diff] (0.15): Pass-to-pass — persist_snapshot method and
# TaskCacheStats struct are intact with core fields.
###############################################################################
echo ""
echo "TEST 5: [pr_diff] (0.15) P2P — persist_snapshot + TaskCacheStats intact"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

# Check persist_snapshot method exists
if 'fn persist_snapshot' not in src:
    print("FAIL: persist_snapshot method missing")
    sys.exit(1)

# Check TaskCacheStats struct exists
if 'struct TaskCacheStats' not in src:
    print("FAIL: TaskCacheStats struct missing")
    sys.exit(1)

# Check core fields exist within a reasonable scope of the struct declaration
struct_match = re.search(r'struct TaskCacheStats\s*\{', src)
if not struct_match:
    print("FAIL: TaskCacheStats struct declaration not found")
    sys.exit(1)

# Extract struct body (find matching closing brace)
start = struct_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{':
        depth += 1
    elif src[pos] == '}':
        depth -= 1
    pos += 1
struct_body = src[start:pos]

# Core fields that must be present (these exist in base code and should not be removed)
required_fields = ['data:', 'data_count:', 'meta:', 'meta_count:', 'upper_count:']
for field in required_fields:
    if field not in struct_body:
        print(f"FAIL: TaskCacheStats missing required field '{field}'")
        sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 6 [structural] (0.15): Anti-stub and anti-deletion.
# - mod.rs must have substantial content (>500 lines)
# - cfg(print_cache_item_size) blocks must exist with meaningful code (>15 lines)
# - The stats Mutex/HashMap must still exist
###############################################################################
echo ""
echo "TEST 6: [structural] (0.15) Anti-stub and anti-deletion"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs") as f:
    src = f.read()

lines = src.split('\n')

# Check 1: File not stubbed (>500 lines)
if len(lines) < 500:
    print(f"FAIL: mod.rs only {len(lines)} lines — likely stubbed")
    sys.exit(1)

# Check 2: cfg(print_cache_item_size) blocks exist with meaningful content
cfg_lines = 0
in_cfg = False
depth = 0
for line in lines:
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        depth = 0
        continue
    if in_cfg:
        depth += line.count('{') - line.count('}')
        stripped = line.strip()
        if stripped and not stripped.startswith('//'):
            cfg_lines += 1
        if depth <= 0 and '{' not in line and '}' not in line:
            in_cfg = False
            depth = 0

if cfg_lines < 15:
    print(f"FAIL: Only {cfg_lines} non-comment lines in cfg(print_cache_item_size) blocks — instrumentation code deleted?")
    sys.exit(1)

# Check 3: Stats collection infrastructure still exists
if 'Mutex<' not in src or 'TaskCacheStats' not in src:
    print("FAIL: Stats collection infrastructure (Mutex + TaskCacheStats) missing")
    sys.exit(1)

print(f"PASS ({len(lines)} lines, {cfg_lines} cfg-gated lines)")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "========================================="
echo "TOTAL SCORE: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
