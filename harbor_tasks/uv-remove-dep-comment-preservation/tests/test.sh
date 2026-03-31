#!/usr/bin/env bash
set +e

REPO="/repo"
TOTAL=0.0
add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd "$REPO"

###############################################################################
# GATE (0.00): Rust syntax — must compile the modified crate
###############################################################################
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-workspace 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

###############################################################################
# Build the uv binary (needed for behavioral tests)
###############################################################################
echo "=== Building uv binary ==="
BUILD_OK=0
if cargo build -p uv 2>&1; then
    BUILD_OK=1
    UV="$REPO/target/debug/uv"
    echo "Build succeeded."
else
    echo "Build failed — behavioral CLI tests will be skipped."
fi

###############################################################################
# Behavioral (0.30): Remove last dep — comment preserved AND dep removed
###############################################################################
# [pr_diff] (0.30): End-of-line comment on previous entry survives removal of last entry
echo "=== Behavioral: remove last dep, preserve prev comment ==="
SCORE_LAST=0.0
if [ "$BUILD_OK" = "1" ]; then
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    cat > pyproject.toml <<'TOMLEOF'
[project]
name = "test-comment-preserve"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # this comment is clearly essential
    "typing-extensions>=4.0.0",
]
TOMLEOF
    "$UV" remove typing-extensions --no-sync 2>&1 || true
    PASS_COMMENT=0
    PASS_REMOVED=0
    # Check comment survived
    if grep -q '# this comment is clearly essential' pyproject.toml; then
        PASS_COMMENT=1
    else
        echo "FAIL: comment was lost"
        cat pyproject.toml
    fi
    # Check dependency was actually removed
    if ! grep -qi 'typing-extensions' pyproject.toml; then
        PASS_REMOVED=1
    else
        echo "FAIL: typing-extensions was NOT removed"
        cat pyproject.toml
    fi
    if [ "$PASS_COMMENT" = "1" ] && [ "$PASS_REMOVED" = "1" ]; then
        SCORE_LAST=0.30
        echo "PASS: comment preserved AND dep removed"
    fi
    cd "$REPO"
    rm -rf "$TEST_DIR"
fi
echo "Score: $SCORE_LAST"
add "$SCORE_LAST"

###############################################################################
# Behavioral (0.25): Remove middle dep — comment preserved AND dep removed
###############################################################################
# [pr_diff] (0.25): End-of-line comment on previous entry survives removal of middle entry
echo "=== Behavioral: remove middle dep, preserve prev comment ==="
SCORE_MID=0.0
if [ "$BUILD_OK" = "1" ]; then
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    cat > pyproject.toml <<'TOMLEOF'
[project]
name = "test-comment-middle"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # comment on iniconfig
    "typing-extensions>=4.0.0",
    "sniffio>=1.3.0",
]
TOMLEOF
    "$UV" remove typing-extensions --no-sync 2>&1 || true
    PASS_COMMENT=0
    PASS_REMOVED=0
    PASS_OTHER=0
    if grep -q '# comment on iniconfig' pyproject.toml; then
        PASS_COMMENT=1
    else
        echo "FAIL: comment was lost"
        cat pyproject.toml
    fi
    if ! grep -qi 'typing-extensions' pyproject.toml; then
        PASS_REMOVED=1
    else
        echo "FAIL: typing-extensions was NOT removed"
    fi
    if grep -q 'sniffio' pyproject.toml; then
        PASS_OTHER=1
    else
        echo "FAIL: sniffio was incorrectly removed"
    fi
    if [ "$PASS_COMMENT" = "1" ] && [ "$PASS_REMOVED" = "1" ] && [ "$PASS_OTHER" = "1" ]; then
        SCORE_MID=0.25
        echo "PASS: comment preserved, dep removed, other deps intact"
    fi
    cd "$REPO"
    rm -rf "$TEST_DIR"
fi
echo "Score: $SCORE_MID"
add "$SCORE_MID"

###############################################################################
# Behavioral (0.15): Remove dep that has a comment — comment does NOT transfer
###############################################################################
# [pr_diff] (0.15): When the removed dep itself has a comment, it should vanish with the dep
echo "=== Behavioral: removed dep's own comment does not leak ==="
SCORE_OWN=0.0
if [ "$BUILD_OK" = "1" ]; then
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    cat > pyproject.toml <<'TOMLEOF'
[project]
name = "test-own-comment"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0",
    "typing-extensions>=4.0.0", # remove me entirely
    "sniffio>=1.3.0",
]
TOMLEOF
    "$UV" remove typing-extensions --no-sync 2>&1 || true
    PASS_GONE=0
    PASS_CLEAN=0
    if ! grep -qi 'typing-extensions' pyproject.toml; then
        PASS_GONE=1
    else
        echo "FAIL: typing-extensions not removed"
    fi
    # The removed dep's comment should not appear on another line
    if ! grep -q '# remove me entirely' pyproject.toml; then
        PASS_CLEAN=1
    else
        echo "FAIL: removed dep's comment leaked to another entry"
        cat pyproject.toml
    fi
    if [ "$PASS_GONE" = "1" ] && [ "$PASS_CLEAN" = "1" ]; then
        SCORE_OWN=0.15
        echo "PASS: dep and its comment both removed cleanly"
    fi
    cd "$REPO"
    rm -rf "$TEST_DIR"
fi
echo "Score: $SCORE_OWN"
add "$SCORE_OWN"

###############################################################################
# Pass-to-pass (0.10): Existing unit tests in uv-workspace still pass
###############################################################################
# [pr_diff] (0.10): Existing tests must not regress
echo "=== P2P: cargo test uv-workspace ==="
SCORE_P2P=0.0
if cargo test -p uv-workspace -- split_specifiers reformat_array 2>&1; then
    SCORE_P2P=0.10
    echo "PASS: existing tests pass"
else
    echo "FAIL: existing tests broke"
fi
echo "Score: $SCORE_P2P"
add "$SCORE_P2P"

###############################################################################
# Behavioral (0.10): Remove only dep — comment on removed dep vanishes, array empty
###############################################################################
# [pr_diff] (0.10): Single-element removal leaves clean empty array
echo "=== Behavioral: remove only dep ==="
SCORE_ONLY=0.0
if [ "$BUILD_OK" = "1" ]; then
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    cat > pyproject.toml <<'TOMLEOF'
[project]
name = "test-only-dep"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "typing-extensions>=4.0.0", # sole dep comment
]
TOMLEOF
    "$UV" remove typing-extensions --no-sync 2>&1 || true
    if ! grep -qi 'typing-extensions' pyproject.toml; then
        # dependencies key should still exist but be empty
        if grep -q 'dependencies' pyproject.toml; then
            SCORE_ONLY=0.10
            echo "PASS: only dep removed, dependencies key intact"
        else
            echo "PARTIAL: dep removed but dependencies key also gone"
            SCORE_ONLY=0.05
        fi
    else
        echo "FAIL: typing-extensions not removed"
    fi
    cd "$REPO"
    rm -rf "$TEST_DIR"
fi
echo "Score: $SCORE_ONLY"
add "$SCORE_ONLY"

###############################################################################
# Config-derived (0.05): No .unwrap() on fallible paths in new code
###############################################################################
# [agent_config] (0.05): "AVOID using .unwrap()" — CLAUDE.md:7
echo "=== Config: no unwrap in remove_dependency ==="
SCORE_UNWRAP=0.0
RMFN_FILE="crates/uv-workspace/src/pyproject_mut.rs"
UNWRAP_COUNT=$(sed -n '/fn remove_dependency/,/^fn \|^}/p' "$RMFN_FILE" | grep -c '\.unwrap()' || true)
if [ "$UNWRAP_COUNT" -le 1 ]; then
    SCORE_UNWRAP=0.05
    echo "PASS: unwrap count ($UNWRAP_COUNT) is acceptable"
else
    echo "FAIL: too many unwrap calls ($UNWRAP_COUNT)"
fi
echo "Score: $SCORE_UNWRAP"
add "$SCORE_UNWRAP"

###############################################################################
# Config-derived (0.05): Test case added for changed behavior
###############################################################################
# [agent_config] (0.05): "ALWAYS attempt to add a test case for changed behavior" — CLAUDE.md:2
echo "=== Config: test added ==="
SCORE_TEST=0.0
RMFN_FILE="crates/uv-workspace/src/pyproject_mut.rs"
if grep -q 'fn.*\(comment\|preserve\).*test\|fn test.*\(comment\|preserve\)' "$RMFN_FILE" 2>/dev/null || \
   grep -rq 'comment.*preserv\|preserv.*comment' crates/uv/tests/ 2>/dev/null; then
    SCORE_TEST=0.05
    echo "PASS: test for comment preservation found"
else
    NEW_TESTS=$(git diff HEAD -- "$RMFN_FILE" | grep -c '^\+.*#\[test\]' || true)
    if [ "$NEW_TESTS" -gt 0 ]; then
        SCORE_TEST=0.05
        echo "PASS: new test(s) added"
    else
        echo "FAIL: no test added for changed behavior"
    fi
fi
echo "Score: $SCORE_TEST"
add "$SCORE_TEST"

###############################################################################
# Summary
###############################################################################
echo ""
echo "=== TOTAL ==="
echo "Total: $TOTAL"

# Write reward
echo "$TOTAL" > /logs/verifier/reward.txt

# Build JSON breakdown
python3 -c "
import json
data = {
    'reward': $TOTAL,
    'behavioral': round($SCORE_LAST + $SCORE_MID + $SCORE_OWN + $SCORE_ONLY, 4),
    'regression': round($SCORE_P2P, 4),
    'config': round($SCORE_UNWRAP + $SCORE_TEST, 4),
    'structural': 0.0,
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
