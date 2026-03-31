#!/usr/bin/env bash
set +e

TOTAL=0
SCORE=0
REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"

add_score() {
    local weight="$1" pass="$2" label="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

cd /repo

# ============================================================
# GATE: Syntax / compilation check
# ============================================================
# [pr_diff] (GATE): Code compiles
echo "=== GATE: Compilation check ==="
if ! cargo check -p uv-distribution 2>/tmp/compile_err.txt; then
    echo "GATE FAIL: Compilation failed"
    cat /tmp/compile_err.txt
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$REWARD_JSON"
    exit 0
fi
echo "GATE PASS: Code compiles"

# ============================================================
# Fail-to-pass: Behavioral — old API compilation test (0.30)
# ============================================================
# [pr_diff] (0.30): python_version type changed from (u8, u8)
# Inject a test that constructs the error with the OLD (u8, u8) type.
# On buggy code: this compiles fine (type is still (u8, u8)).
# On ANY correct fix: this fails to compile (type mismatch).
echo "=== F2P Behavioral: python_version type no longer (u8, u8) ==="
PASS_TYPE=0
ERROR_FILE="crates/uv-distribution/src/error.rs"
cp "$ERROR_FILE" "${ERROR_FILE}.harbor_bak"

cat >> "$ERROR_FILE" << 'HARBOR_INJECT'

#[cfg(test)]
mod harbor_type_check {
    use super::Error;
    use std::str::FromStr;
    use uv_distribution_filename::WheelFilename;
    use uv_platform_tags::{Arch, Os, Platform};

    #[test]
    fn harbor_old_tuple_api() {
        // This constructs the error using the OLD (u8, u8) API.
        // If the agent correctly changed the type, this won't compile.
        let _ = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str(
                "test-1.0-cp315-abi3t-macosx_11_0_arm64.whl",
            ).unwrap(),
            python_platform: Platform::new(
                Os::Macos { major: 11, minor: 0 },
                Arch::Aarch64,
            ),
            python_version: (3u8, 15u8),
        };
    }
}
HARBOR_INJECT

# If cargo check --tests FAILS, the old API is gone → fix is applied
cargo check --tests -p uv-distribution 2>/dev/null
if [ $? -ne 0 ]; then
    PASS_TYPE=1
fi

# Restore original file
mv "${ERROR_FILE}.harbor_bak" "$ERROR_FILE"
add_score 0.30 $PASS_TYPE "python_version type changed from (u8, u8) — old API no longer compiles"

# ============================================================
# Fail-to-pass: Behavioral — crate tests pass (0.25)
# ============================================================
# [pr_diff] (0.25): cargo test -p uv-distribution passes with >0 tests
# Runs the agent's own tests. Verifies fix compiles AND tests pass.
# We check that at least 1 test actually ran (not 0-test false positive).
echo "=== F2P Behavioral: uv-distribution crate tests pass ==="
PASS_CRATE=0
TEST_OUTPUT=$(cargo test -p uv-distribution 2>&1)
# Must have "test result: ok" AND at least one test actually ran
if echo "$TEST_OUTPUT" | grep -q "test result: ok" && \
   echo "$TEST_OUTPUT" | grep -qE 'running [1-9][0-9]* test'; then
    PASS_CRATE=1
fi
add_score 0.25 $PASS_CRATE "uv-distribution crate tests pass (>0 tests verified)"

# ============================================================
# Fail-to-pass: distribution_database passes variant info (0.10)
# ============================================================
# [pr_diff] (0.10): distribution_database.rs references freethreaded/variant
# On buggy code: no variant info passed to error construction
# On ANY correct fix: must check Tags freethreaded status when constructing error
echo "=== F2P: distribution_database passes variant info ==="
PASS_DB=0
if grep -qiE 'is_freethreaded|freethreaded|Freethreaded|variant|Variant' \
     crates/uv-distribution/src/distribution_database.rs; then
    PASS_DB=1
fi
add_score 0.10 $PASS_DB "distribution_database.rs passes freethreaded/variant info to error"

# ============================================================
# Pass-to-pass: Regression tests (0.15)
# ============================================================
# [repo_tests] (0.15): Existing uv-platform-tags tests still pass
echo "=== P2P: uv-platform-tags tests ==="
PASS_TAGS=0
TAGS_OUTPUT=$(cargo test -p uv-platform-tags 2>&1)
if echo "$TAGS_OUTPUT" | grep -q "test result: ok"; then
    PASS_TAGS=1
fi
add_score 0.15 $PASS_TAGS "uv-platform-tags tests still pass"

# ============================================================
# Fail-to-pass: Tags exposes freethreaded status (0.10)
# ============================================================
# [pr_diff] (0.10): Tags has public accessor for is_freethreaded
# On buggy code: is_freethreaded is a private field with no public accessor
# Accepts: pub fn is_freethreaded() OR pub is_freethreaded: bool field
echo "=== F2P: Tags exposes freethreaded status publicly ==="
PASS_ACCESSOR=0
if grep -qE 'pub fn is_freethreaded|pub is_freethreaded\s*:' \
     crates/uv-platform-tags/src/tags.rs; then
    PASS_ACCESSOR=1
fi
add_score 0.10 $PASS_ACCESSOR "Tags exposes is_freethreaded publicly (method or field)"

# ============================================================
# Config-derived checks (0.10)
# ============================================================

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 87da0ce4
echo "=== Config: No unwrap/panic in error.rs (non-test) ==="
PASS_NO_PANIC=0
# Check non-test portion of error.rs for unwrap()/panic!()
if ! sed '/^#\[cfg(test)\]/,$d' crates/uv-distribution/src/error.rs | grep -qE '\.unwrap\(\)|panic!\('; then
    PASS_NO_PANIC=1
fi
add_score 0.05 $PASS_NO_PANIC "No unwrap()/panic!() in error.rs non-test code (CLAUDE.md:7)"

# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:14 @ 87da0ce4
echo "=== Config: No local imports in error.rs ==="
PASS_IMPORTS=0
# Check that no use statements are deeply indented (inside function bodies)
# in the non-test portion of error.rs
if ! sed '/^#\[cfg(test)\]/,$d' crates/uv-distribution/src/error.rs | grep -qE '^\s{8,}use '; then
    PASS_IMPORTS=1
fi
add_score 0.05 $PASS_IMPORTS "No local imports in error.rs functions (CLAUDE.md:14)"

# ============================================================
# Summary
# ============================================================
echo ""
echo "=== SCORE: $SCORE / $TOTAL ==="

REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo "$REWARD" > "$REWARD_FILE"

# Compute category scores for reward.json
BEH=$(python3 -c "
score = $SCORE
# Behavioral F2P: type_check(0.30) + crate_tests(0.25) + db_variant(0.10) + accessor(0.10) = 0.75
beh = min(score, 0.75)
print(round(beh, 4))
")
REG=$(python3 -c "
score = $SCORE
reg = max(min(score - 0.75, 0.15), 0.0)
print(round(reg, 4))
")
CONF=$(python3 -c "
score = $SCORE
conf = max(min(score - 0.90, 0.10), 0.0)
print(round(conf, 4))
")

echo "{\"reward\": $REWARD, \"behavioral\": $BEH, \"regression\": $REG, \"config\": $CONF, \"style_rubric\": 0.0}" > "$REWARD_JSON"

echo "Reward: $REWARD"
cat "$REWARD_JSON"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
