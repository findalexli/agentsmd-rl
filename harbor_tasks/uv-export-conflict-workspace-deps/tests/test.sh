#!/usr/bin/env bash
set +e

SCORE=0
cd /repo

FILE="crates/uv-resolver/src/lock/export/mod.rs"

# ──────────────────────────────────────────────────────────────
# GATE: Syntax check — crate must compile
# ──────────────────────────────────────────────────────────────
# [pr_diff] (gate): Source file must compile
echo "=== GATE: Compile check ==="
if ! cargo check -p uv-resolver 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────────────────────
# Helper: extract section between two patterns, strip Rust comments
# This prevents gaming by inserting comments matching grep patterns.
# ──────────────────────────────────────────────────────────────
section_no_comments() {
    local start="$1" end="$2" file="$3"
    sed -n "/$start/,/$end/p" "$file" | sed 's|//.*||'
}

# Key section: between find_by_name(root_name) and if groups.prod()
# This is where the fix must insert conflict tracking for the root package.
SECTION=$(section_no_comments 'find_by_name(root_name)' 'if groups\.prod()' "$FILE")

# Full from_lock function body, comments stripped
FROM_LOCK_BODY=$(section_no_comments 'fn from_lock' '^    fn ' "$FILE")

# ──────────────────────────────────────────────────────────────
# BEHAVIORAL: Fail-to-pass source checks (0.65 total)
#
# Justification for source inspection: ExportableRequirements::from_lock
# requires the full uv binary (lock resolver, conflict system, package
# graph, IO layer). Building the binary takes 10+ min even with
# pre-fetched deps, exceeding the 120s verifier timeout. All checks
# strip comments first to prevent comment-injection gaming.
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.35): The root package must be inserted into the conflicts
# map between find_by_name and groups.prod(). Without this,
# resolve_conflicts() drops all deps when it sees a package-level
# conflict marker it can't find in known_conflicts.
# Accepts dist.id.name OR root_name (semantically equivalent).
echo "=== TEST: Behavioral — conflicts.insert(ConflictItem) for root package ==="
PASS_INSERT=0
if echo "$SECTION" | grep -qE 'conflicts.*insert.*ConflictItem.*(dist\.id\.name|root_name)'; then
    PASS_INSERT=1
fi
echo "  Result: $PASS_INSERT"

# [pr_diff] (0.15): The ConflictItem must use MarkerTree::TRUE for
# unconditional activation — workspace member is always active when
# exported with --package.
echo "=== TEST: Behavioral — unconditional MarkerTree::TRUE ==="
PASS_MARKER=0
if echo "$SECTION" | grep -q 'MarkerTree::TRUE'; then
    PASS_MARKER=1
fi
echo "  Result: $PASS_MARKER"

# [pr_diff] (0.15): The insert must happen on the conflicts object
# using safe Option handling (if let, match, map, etc.) — not unwrap.
# This also verifies the insert is real code, not just pattern noise.
echo "=== TEST: Behavioral — safe conflicts access + insert ==="
PASS_SAFE_INSERT=0
if echo "$SECTION" | grep -qE '(if let .* conflicts|match.*conflicts|conflicts\.(as_mut|as_ref|map|and_then))' && \
   echo "$SECTION" | grep -qE 'insert.*ConflictItem'; then
    PASS_SAFE_INSERT=1
fi
echo "  Result: $PASS_SAFE_INSERT"

# ──────────────────────────────────────────────────────────────
# REGRESSION: Pass-to-pass (0.10)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): Existing conflict tracking for extras must still work
# (the extras loop already had conflicts.insert — must not be removed)
echo "=== TEST: Regression — extras conflict tracking preserved ==="
PASS_EXTRAS=0
EXTRAS_BLOCK=$(section_no_comments 'for extra in extras\.extra_names' '^                }' "$FILE")
if echo "$EXTRAS_BLOCK" | grep -q 'conflicts.*insert.*ConflictItem'; then
    PASS_EXTRAS=1
fi
echo "  Result: $PASS_EXTRAS"

# [pr_diff] (0.05): The from_lock function still adds graph edges and
# queues dependencies for traversal
echo "=== TEST: Regression — graph.add_edge + queue.push_back ==="
PASS_GRAPH=0
PROD_BLOCK=$(section_no_comments 'if groups\.prod()' '^            }' "$FILE")
if echo "$PROD_BLOCK" | grep -q 'graph.*add_edge' && \
   echo "$PROD_BLOCK" | grep -q 'queue.*push_back'; then
    PASS_GRAPH=1
fi
echo "  Result: $PASS_GRAPH"

# ──────────────────────────────────────────────────────────────
# STRUCTURAL: Anti-stub + integrity (0.10)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): No stub/todo/unimplemented macros in the file
echo "=== TEST: Anti-stub ==="
PASS_NOSTUB=0
if ! grep -qE 'todo!\(|unimplemented!\(' "$FILE" 2>/dev/null; then
    PASS_NOSTUB=1
fi
echo "  Result: $PASS_NOSTUB"

# [pr_diff] (0.05): Core data structures in from_lock still intact
echo "=== TEST: Structural — from_lock core data structures ==="
PASS_CORE=0
if grep -q 'let mut graph' "$FILE" && \
   grep -q 'let mut conflicts' "$FILE" && \
   grep -q 'let mut queue' "$FILE"; then
    PASS_CORE=1
fi
echo "  Result: $PASS_CORE"

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.15)
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 3d4cb95c
echo "=== TEST: Config — no unwrap/panic in from_lock ==="
PASS_NOPANIC=0
if ! echo "$FROM_LOCK_BODY" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(' 2>/dev/null; then
    PASS_NOPANIC=1
fi
echo "  Result: $PASS_NOPANIC"

# [agent_config] (0.05): "PREFER if let to handle fallibility" — CLAUDE.md:8 @ 3d4cb95c
# Accept any safe Option pattern: if let, match, .map(), .and_then()
echo "=== TEST: Config — safe Option handling in fix area ==="
PASS_OPTION=0
if echo "$SECTION" | grep -qE '(if let|match|\.map\(|\.and_then\()'; then
    PASS_OPTION=1
fi
echo "  Result: $PASS_OPTION"

# [agent_config] (0.05): "AVOID shortening variable names" — CLAUDE.md:17-18 @ 3d4cb95c
echo "=== TEST: Config — no shortened variable names in fix area ==="
PASS_NAMES=0
if ! echo "$SECTION" | grep -qE '\bvar\b|\bconf\b|\bcf\b|\bcnfl\b' 2>/dev/null; then
    PASS_NAMES=1
fi
echo "  Result: $PASS_NAMES"

# ──────────────────────────────────────────────────────────────
# FINAL SCORE
# ──────────────────────────────────────────────────────────────

echo ""
echo "=== SCORING ==="

REWARD=$(python3 -c "print(round(
    $PASS_INSERT * 0.35 +
    $PASS_MARKER * 0.15 +
    $PASS_SAFE_INSERT * 0.15 +
    $PASS_EXTRAS * 0.05 +
    $PASS_GRAPH * 0.05 +
    $PASS_NOSTUB * 0.05 +
    $PASS_CORE * 0.05 +
    $PASS_NOPANIC * 0.05 +
    $PASS_OPTION * 0.05 +
    $PASS_NAMES * 0.05
, 2))")

echo "$REWARD" > /logs/verifier/reward.txt

B_SCORE=$(python3 -c "print(round($PASS_INSERT * 0.35 + $PASS_MARKER * 0.15 + $PASS_SAFE_INSERT * 0.15, 2))")
R_SCORE=$(python3 -c "print(round($PASS_EXTRAS * 0.05 + $PASS_GRAPH * 0.05, 2))")
S_SCORE=$(python3 -c "print(round($PASS_NOSTUB * 0.05 + $PASS_CORE * 0.05, 2))")
C_SCORE=$(python3 -c "print(round($PASS_NOPANIC * 0.05 + $PASS_OPTION * 0.05 + $PASS_NAMES * 0.05, 2))")

echo "{\"reward\": $REWARD, \"behavioral\": $B_SCORE, \"regression\": $R_SCORE, \"config\": $C_SCORE, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
