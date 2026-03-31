#!/usr/bin/env bash
set +e

SCORE=0

add() {
    local weight=$1 pass=$2 label=$3
    echo "  [$label] weight=$weight pass=$pass"
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
    fi
}

cd /repo
FILE="crates/uv-client/src/registry_client.rs"

# ──────────────────────────────────────────────────────────────
# GATE: Compilation — crate must compile (Rust type system enforces correctness)
# ──────────────────────────────────────────────────────────────
# [pr_diff] (gate): Source file must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-client 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────────────────────
# FAIL-TO-PASS (0.65 total)
# Justification for structural checks: flat_single_index is an async method on
# RegistryClient requiring HTTP clients, caches, network, and tokio runtime.
# RegistryClient fields and FlatIndexCache are module-private. Cannot be called
# from a test harness without the full server setup.
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.35): Core bug — cache-level lock NOT held across fetch_index
# The bug: self.flat_indexes.lock().await holds the MutexGuard across the entire
# method, including the network fetch (fetch_index). ANY correct fix ensures the
# cache-level lock is released before the fetch_index call.
# Accepts: scoped blocks, explicit drop(), DashMap, per-index locks, RwLock, etc.
echo "=== F2P: Lock not held across fetch_index ==="
PASS_CORE=$(python3 << 'PYEOF'
import re, sys

with open("crates/uv-client/src/registry_client.rs") as f:
    source = f.read()

# --- Pattern A: DashMap replaces Mutex-based cache (no global lock needed) ---
if "DashMap" in source and "FlatIndexCache" in source:
    print(1)
    sys.exit(0)

# --- Find the flat_single_index method body ---
# Match from fn signature to next method at the same indent level or end of impl
match = re.search(r'(fn flat_single_index\b.*?)(\n    (?:pub\s+)?(?:async\s+)?fn\s)', source, re.DOTALL)
if not match:
    match = re.search(r'(fn flat_single_index\b.*?)(\n\})', source, re.DOTALL)
if not match:
    print(0)
    sys.exit(0)

body = match.group(1)
lines = body.split('\n')

# Find lines with cache-level lock and fetch_index
lock_lines = []
fetch_lines = []
for i, line in enumerate(lines):
    # Cache-level lock: .lock().await on flat_indexes or a cache variable
    if '.lock().await' in line and ('flat_index' in line.lower() or 'cache' in line.lower() or 'self.' in line):
        lock_lines.append(i)
    if 'fetch_index' in line:
        fetch_lines.append(i)

if not fetch_lines:
    # fetch_index removed entirely — likely a major refactor, fail
    print(0)
    sys.exit(0)

if not lock_lines:
    # No cache lock in the method at all — lock moved elsewhere or DashMap used
    # This is a valid fix pattern (e.g., lock in a helper, or concurrent map)
    print(1)
    sys.exit(0)

first_lock = min(lock_lines)
first_fetch = min(fetch_lines)

if first_lock >= first_fetch:
    # Lock comes AFTER fetch — fix pattern: fetch first, then lock to store
    print(1)
    sys.exit(0)

# --- Check if the lock is dropped before fetch_index ---
between = '\n'.join(lines[first_lock:first_fetch])

# Method 1: Check brace depth — if depth returns to 0 or below, lock scope has closed
depth = 0
min_depth = 0
for ch in between:
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        min_depth = min(min_depth, depth)

if min_depth <= 0:
    # Brace depth returned to or below starting point — lock guard dropped
    print(1)
    sys.exit(0)

# Method 2: Explicit drop() call
if re.search(r'drop\s*\(', between):
    print(1)
    sys.exit(0)

# Method 3: Lock result assigned to a variable in a let binding with a block
# e.g., let result = { let cache = ...lock().await; cache.something() };
if re.search(r'let\s+\w+\s*=\s*\{', between):
    print(1)
    sys.exit(0)

# Lock still held across fetch — bug not fixed
print(0)
PYEOF
)
add 0.35 "$PASS_CORE" "f2p-lock-scope"

# [pr_diff] (0.15): FlatIndexCache restructured for per-index concurrency
# The old cache stores entries directly (FxHashMap<IndexUrl, FxHashMap<PackageName, ...>>).
# A correct fix changes the cache to support per-index granularity.
# Accepts: per-index Mutex/RwLock/OnceCell slots, DashMap, entry API with Arc, etc.
echo "=== F2P: Cache restructured for per-index concurrency ==="
PASS_CONCURRENCY=$(python3 << 'PYEOF'
import re, sys

with open("crates/uv-client/src/registry_client.rs") as f:
    source = f.read()

found = False

# Pattern 1: DashMap (inherently concurrent per-key)
if "DashMap" in source:
    found = True

# Pattern 2: Per-index Mutex/RwLock slot (Arc<Mutex<Option<...>>>, etc.)
if re.search(r'Arc<(?:Mutex|RwLock)<Option<', source):
    found = True

# Pattern 3: Per-index OnceCell or Lazy
if "OnceCell" in source:
    found = True

# Pattern 4: The cache struct field type no longer stores entries directly
# Old: FxHashMap<IndexUrl, FxHashMap<PackageName, Vec<FlatIndexEntry>>>
# Any fix changes this inner type
cache_struct = re.search(r'struct FlatIndexCache\s*[\({]([^)}]*)[\)}]', source, re.DOTALL)
if cache_struct:
    fields = cache_struct.group(1)
    # Old pattern stored PackageName directly in the cache field
    if "PackageName" not in fields:
        found = True

# Pattern 5: Type alias for a per-index slot
if re.search(r'type\s+\w*(?:Slot|Entry|Cell)\w*\s*=\s*Arc<', source):
    found = True

print(1 if found else 0)
PYEOF
)
add 0.15 "$PASS_CONCURRENCY" "f2p-cache-restructured"

# [pr_diff] (0.15): Cache write no longer uses the old global-lock insert pattern
# Bug: cache.insert(index.clone(), entries_by_package) while holding the cache lock
# Fix: writes to a per-index slot, uses DashMap.insert(), or any other pattern
# that doesn't hold the cache lock during the write of fetched data.
echo "=== F2P: Global-lock insert pattern removed ==="
FLAT_METHOD=$(sed -n '/fn flat_single_index/,/^    }/p' "$FILE")
PASS_WRITE=0
# The old pattern: cache.insert(...index...) under a long-held lock
if ! echo "$FLAT_METHOD" | grep -q 'cache\.insert.*index'; then
    PASS_WRITE=1
fi
add 0.15 "$PASS_WRITE" "f2p-global-insert-removed"

# ──────────────────────────────────────────────────────────────
# PASS-TO-PASS REGRESSION (0.10)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): flat_single_index still fetches index data
echo "=== P2P: Fetch logic preserved ==="
PASS_FETCH=0
if echo "$FLAT_METHOD" | grep -q 'fetch_index'; then
    PASS_FETCH=1
fi
add 0.05 "$PASS_FETCH" "p2p-fetch-logic"

# [pr_diff] (0.05): Method still returns entries for the requested package
# Accepts any of: .get(package_name), indexing by package_name, match on package
echo "=== P2P: Package lookup preserved ==="
PASS_LOOKUP=0
if echo "$FLAT_METHOD" | grep -q 'package_name'; then
    PASS_LOOKUP=1
fi
add 0.05 "$PASS_LOOKUP" "p2p-package-lookup"

# ──────────────────────────────────────────────────────────────
# ANTI-GAMING (0.10)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): No stubs or placeholder code
echo "=== Anti-stub: No todo/unimplemented ==="
PASS_NOSTUB=0
if ! echo "$FLAT_METHOD" | grep -qE 'todo!\(|unimplemented!\(' 2>/dev/null; then
    PASS_NOSTUB=1
fi
add 0.05 "$PASS_NOSTUB" "anti-stub"

# [pr_diff] (0.05): Method has substantial implementation (not hollowed out)
echo "=== Anti-stub: Substantive implementation ==="
PASS_SUBSTANCE=0
LINE_COUNT=$(echo "$FLAT_METHOD" | grep -cvE '^\s*$|^\s*//' || true)
if [ "$LINE_COUNT" -ge 15 ]; then
    PASS_SUBSTANCE=1
fi
add 0.05 "$PASS_SUBSTANCE" "anti-stub-substance"

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.15)
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 9d45e7f8
echo "=== Config: No unwrap/panic in flat_single_index ==="
PASS_NOUNWRAP=0
if ! echo "$FLAT_METHOD" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(' 2>/dev/null; then
    PASS_NOUNWRAP=1
fi
add 0.05 "$PASS_NOUNWRAP" "config-no-unwrap"

# [agent_config] (0.05): "AVOID shortening variable names" — CLAUDE.md:17-18 @ 9d45e7f8
echo "=== Config: No shortened variable names ==="
PASS_NAMES=0
if ! echo "$FLAT_METHOD" | grep -qE '\blet\s+(idx|ent|pkg|res|val|ret|tmp|buf)\b' 2>/dev/null; then
    PASS_NAMES=1
fi
add 0.05 "$PASS_NAMES" "config-no-short-names"

# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:16 @ 9d45e7f8
echo "=== Config: No local imports ==="
PASS_IMPORTS=0
if ! echo "$FLAT_METHOD" | grep -qE '^\s+use\s' 2>/dev/null; then
    PASS_IMPORTS=1
fi
add 0.05 "$PASS_IMPORTS" "config-no-local-imports"

# ──────────────────────────────────────────────────────────────
# FINAL SCORE
# ──────────────────────────────────────────────────────────────

echo ""
echo "=== SCORING ==="
echo "Score: $SCORE"

REWARD=$(python3 -c "print(round($SCORE, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

B_SCORE=$(python3 -c "print(round(${PASS_CORE:-0} * 0.35 + ${PASS_CONCURRENCY:-0} * 0.15 + ${PASS_WRITE:-0} * 0.15, 2))")
R_SCORE=$(python3 -c "print(round(${PASS_FETCH:-0} * 0.05 + ${PASS_LOOKUP:-0} * 0.05, 2))")
S_SCORE=$(python3 -c "print(round(${PASS_NOSTUB:-0} * 0.05 + ${PASS_SUBSTANCE:-0} * 0.05, 2))")
C_SCORE=$(python3 -c "print(round(${PASS_NOUNWRAP:-0} * 0.05 + ${PASS_NAMES:-0} * 0.05 + ${PASS_IMPORTS:-0} * 0.05, 2))")

echo "{\"reward\": $REWARD, \"behavioral\": $B_SCORE, \"regression\": $R_SCORE, \"config\": $C_SCORE, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
