#!/usr/bin/env bash
set +e

cd /repo
SCORE=0
mkdir -p /logs/verifier

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Modified crates must compile
cargo check -p uv-platform-tags 2>/tmp/check_err.txt
if [ $? -ne 0 ]; then
    echo "GATE FAILED: cargo check failed"
    cat /tmp/check_err.txt
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

echo ""
echo "=== Behavioral F2P: Injecting verifier tests into error.rs ==="

# Inject fail-to-pass tests that construct error variants and check Display output.
# On buggy code: error shows "macos" / "manylinux" → assertions FAIL.
# On ANY correct fix (regardless of method name): assertions PASS.
cat >> crates/uv-distribution/src/error.rs << 'VERIFIER_TESTS'

#[cfg(test)]
mod verifier_behavioral_tests {
    use super::Error;
    use std::str::FromStr;
    use uv_distribution_filename::WheelFilename;
    use uv_platform_tags::{Arch, Os, Platform};

    #[test]
    fn verifier_host_error_macos_capitalized() {
        let err = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str(
                "cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl",
            )
            .unwrap(),
            python_platform: Platform::new(
                Os::Macos {
                    major: 11,
                    minor: 0,
                },
                Arch::Aarch64,
            ),
            python_version: (3, 15),
        };
        let msg = err.to_string();
        assert!(
            msg.contains("macOS"),
            "Expected 'macOS' (properly capitalized) in error message, got: {msg}"
        );
    }

    #[test]
    fn verifier_target_error_linux_not_manylinux() {
        let err = Error::BuiltWheelIncompatibleTargetPlatform {
            filename: WheelFilename::from_str("foo-1.0.0-py313-none-any.whl").unwrap(),
            python_platform: Platform::new(
                Os::Manylinux {
                    major: 2,
                    minor: 28,
                },
                Arch::X86_64,
            ),
            python_version: (3, 12),
        };
        let msg = err.to_string();
        assert!(
            msg.contains("Linux"),
            "Expected 'Linux' (not raw 'manylinux') in error message, got: {msg}"
        );
        assert!(
            !msg.contains("manylinux"),
            "Should not contain raw 'manylinux' in error message: {msg}"
        );
    }
}
VERIFIER_TESTS

# Compile and run injected behavioral tests
echo "Compiling and running verifier tests..."
DIST_OUTPUT=$(cargo test -p uv-distribution verifier_ 2>&1) || true
echo "$DIST_OUTPUT" | tail -30

# [pr_diff] (0.35): Host platform error message shows "macOS" instead of raw "macos"
if echo "$DIST_OUTPUT" | grep -q "verifier_host_error_macos_capitalized.*ok"; then
    echo "  +0.35 F2P: host error shows 'macOS' (properly capitalized)"
    SCORE=$(python3 -c "print($SCORE + 0.35)")
else
    echo "  +0.00 F2P: host error test FAILED or could not compile"
fi

# [pr_diff] (0.25): Target platform error message shows "Linux" instead of raw "manylinux"
if echo "$DIST_OUTPUT" | grep -q "verifier_target_error_linux_not_manylinux.*ok"; then
    echo "  +0.25 F2P: target error shows 'Linux' (not 'manylinux')"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "  +0.00 F2P: target error test FAILED or could not compile"
fi

echo ""
echo "=== P2P: Existing upstream tests ==="

# [repo_tests] (0.15): All existing uv-platform-tags tests still pass
PTAG_OUTPUT=$(cargo test -p uv-platform-tags 2>&1) || true
echo "$PTAG_OUTPUT" | tail -10
if echo "$PTAG_OUTPUT" | grep -q "test result: ok"; then
    echo "  +0.15 P2P: uv-platform-tags tests pass"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  +0.00 P2P: some uv-platform-tags tests FAILED"
fi

echo ""
echo "=== Structural: anti-stub ==="
PLATFORM_RS="crates/uv-platform-tags/src/platform.rs"

# [pr_diff] (0.15): platform.rs has new OS-to-human-readable mapping logic
# Verify the diff adds string literals for at least 3 different OS names (anti-stub)
DIFF_ADDED=$(git diff HEAD -- "$PLATFORM_RS" 2>/dev/null | grep '^+' | grep -v '^+++')
if [ -z "$DIFF_ADDED" ]; then
    echo "  +0.00 platform.rs not modified"
else
    HAS_MACOS=$(echo "$DIFF_ADDED" | grep -c '"macOS"' || echo 0)
    HAS_LINUX=$(echo "$DIFF_ADDED" | grep -c '"Linux"' || echo 0)
    HAS_WINDOWS=$(echo "$DIFF_ADDED" | grep -c '"Windows"' || echo 0)
    HAS_FREEBSD=$(echo "$DIFF_ADDED" | grep -c '"FreeBSD"' || echo 0)
    MAPPED_COUNT=$((HAS_MACOS + HAS_LINUX + HAS_WINDOWS + HAS_FREEBSD))
    if [ "$MAPPED_COUNT" -ge 3 ]; then
        echo "  +0.15 platform.rs has real OS mapping logic ($MAPPED_COUNT OS name strings)"
        SCORE=$(python3 -c "print($SCORE + 0.15)")
    else
        echo "  +0.00 platform.rs changes look incomplete ($MAPPED_COUNT/3 OS mappings)"
    fi
fi

echo ""
echo "=== Config checks ==="

# Only check config rules if platform.rs was actually modified
NEW_CODE=$(git diff HEAD -- "$PLATFORM_RS" 2>/dev/null | grep '^+' | grep -v '^+++' || echo "")
if [ -n "$NEW_CODE" ]; then
    # [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap(), unsafe code" — CLAUDE.md:7
    if echo "$NEW_CODE" | grep -qE '\bunwrap\(\)|\bpanic!\b|\bunreachable!\b|\bunsafe\b'; then
        echo "  +0.00 new code uses unwrap/panic/unreachable/unsafe"
    else
        echo "  +0.05 new code avoids unwrap/panic/unreachable/unsafe"
        SCORE=$(python3 -c "print($SCORE + 0.05)")
    fi

    # [agent_config] (0.05): "AVOID shortening variable names" — CLAUDE.md:17-18
    if echo "$NEW_CODE" | grep -qE '\blet\s+(ver|rp|plt|plat|hw)\b'; then
        echo "  +0.00 new code uses abbreviated variable names"
    else
        echo "  +0.05 variable names are appropriate"
        SCORE=$(python3 -c "print($SCORE + 0.05)")
    fi
else
    echo "  +0.00 platform.rs not modified, skipping config checks"
fi

echo ""
echo "=== Final Score ==="
SCORE=$(python3 -c "print(min(1.0, max(0.0, $SCORE)))")
echo "Score: $SCORE"

echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
# Decompose into grader buckets
f2p = min(0.60, score)
p2p = 0.15 if score >= 0.70 else (0.15 if '$PTAG_OUTPUT'.find('test result: ok') >= 0 else 0.0)
structural = min(0.15, max(0.0, score - 0.75))
config_score = min(0.10, max(0.0, score - 0.90))
json.dump({
    'reward': score,
    'behavioral': round(f2p + p2p, 2),
    'regression': round(p2p, 2),
    'config': round(config_score, 2),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
