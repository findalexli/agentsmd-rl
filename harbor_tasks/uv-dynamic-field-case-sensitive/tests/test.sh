#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    local weight=$1 pass=$2
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
    fi
}

cd /repo

FILE="crates/uv-pypi-types/src/metadata/metadata_resolver.rs"

# ──────────────────────────────────────────────────────────────
# GATE: Syntax check — crate must compile
# ──────────────────────────────────────────────────────────────
# [pr_diff] (gate): Source file must compile
echo "=== GATE: Compile check ==="
if ! cargo check -p uv-pypi-types 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────────────────────
# Inject behavioral tests into the existing test module
# These call parse_pkg_info / parse_metadata directly
# ──────────────────────────────────────────────────────────────

# Save original file for restoration
cp "$FILE" "${FILE}.bak"

# Inject test functions that exercise the case-insensitivity behavior
cat >> "$FILE" <<'INJECT'

#[cfg(test)]
mod injected_case_tests {
    use super::*;
    use std::str::FromStr;
    use uv_normalize::PackageName;

    /// Lowercase "requires-dist" MUST be matched as dynamic (case-insensitive).
    /// On buggy code (case-sensitive match), this returns Ok (fails to detect).
    /// On fixed code (case-insensitive), this returns Err(DynamicField).
    #[test]
    fn test_lowercase_requires_dist_detected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: requires-dist";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'requires-dist' must be detected as Dynamic Requires-Dist");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Dist")));
    }

    /// Lowercase "requires-python" MUST be matched.
    #[test]
    fn test_lowercase_requires_python_detected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: requires-python";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'requires-python' must be detected as Dynamic Requires-Python");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Python")));
    }

    /// Lowercase "provides-extra" MUST be matched.
    #[test]
    fn test_lowercase_provides_extra_detected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: provides-extra";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'provides-extra' must be detected as Dynamic Provides-Extra");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Provides-Extra")));
    }

    /// Lowercase "version" in METADATA Dynamic MUST set dynamic=true.
    #[test]
    fn test_lowercase_version_dynamic_in_metadata() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: version";
        let meta = ResolutionMetadata::parse_metadata(s.as_bytes()).unwrap();
        assert!(meta.dynamic, "lowercase 'version' must set dynamic=true");
    }

    /// UPPER CASE "REQUIRES-DIST" MUST also be matched (full case-insensitivity).
    #[test]
    fn test_uppercase_requires_dist_detected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: REQUIRES-DIST";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "uppercase 'REQUIRES-DIST' must be detected as Dynamic Requires-Dist");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Dist")));
    }

    /// Canonical "Requires-Dist" MUST still be rejected (regression guard).
    #[test]
    fn test_canonical_requires_dist_still_rejected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: Requires-Dist";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "canonical 'Requires-Dist' must still be rejected");
    }

    /// Canonical "Version" MUST still set dynamic=true (regression guard).
    #[test]
    fn test_canonical_version_still_dynamic() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: Version";
        let meta = ResolutionMetadata::parse_metadata(s.as_bytes()).unwrap();
        assert!(meta.dynamic, "canonical 'Version' must still set dynamic=true");
    }
}
INJECT

echo "Injected behavioral tests."

# Build the injected tests
if ! cargo test -p uv-pypi-types --no-run 2>&1; then
    echo "ERROR: injected tests failed to compile, restoring original"
    mv "${FILE}.bak" "$FILE"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ──────────────────────────────────────────────────────────────
# BEHAVIORAL: Fail-to-pass tests (0.75 total)
# These FAIL on buggy code, PASS on the fix
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.20): lowercase "requires-dist" detected as dynamic by parse_pkg_info
echo "=== TEST: Behavioral — lowercase requires-dist detected ==="
PASS_RD=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_lowercase_requires_dist_detected 2>&1 | grep -q "test result: ok"; then
    PASS_RD=1
fi
add_score 0.20 "$PASS_RD"
echo "  Result: $PASS_RD"

# [pr_diff] (0.15): lowercase "requires-python" detected as dynamic
echo "=== TEST: Behavioral — lowercase requires-python detected ==="
PASS_RP=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_lowercase_requires_python_detected 2>&1 | grep -q "test result: ok"; then
    PASS_RP=1
fi
add_score 0.15 "$PASS_RP"
echo "  Result: $PASS_RP"

# [pr_diff] (0.15): lowercase "provides-extra" detected as dynamic
echo "=== TEST: Behavioral — lowercase provides-extra detected ==="
PASS_PE=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_lowercase_provides_extra_detected 2>&1 | grep -q "test result: ok"; then
    PASS_PE=1
fi
add_score 0.15 "$PASS_PE"
echo "  Result: $PASS_PE"

# [pr_diff] (0.15): lowercase "version" sets dynamic=true in parse_metadata
echo "=== TEST: Behavioral — lowercase version dynamic in parse_metadata ==="
PASS_VER=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_lowercase_version_dynamic_in_metadata 2>&1 | grep -q "test result: ok"; then
    PASS_VER=1
fi
add_score 0.15 "$PASS_VER"
echo "  Result: $PASS_VER"

# [pr_diff] (0.10): uppercase "REQUIRES-DIST" detected as dynamic
echo "=== TEST: Behavioral — uppercase REQUIRES-DIST detected ==="
PASS_UC=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_uppercase_requires_dist_detected 2>&1 | grep -q "test result: ok"; then
    PASS_UC=1
fi
add_score 0.10 "$PASS_UC"
echo "  Result: $PASS_UC"

# ──────────────────────────────────────────────────────────────
# REGRESSION: Pass-to-pass (0.15)
# Existing correct behavior must still work
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): canonical "Requires-Dist" still rejected
echo "=== TEST: Regression — canonical Requires-Dist still rejected ==="
PASS_CAN_RD=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_canonical_requires_dist_still_rejected 2>&1 | grep -q "test result: ok"; then
    PASS_CAN_RD=1
fi
add_score 0.05 "$PASS_CAN_RD"
echo "  Result: $PASS_CAN_RD"

# [pr_diff] (0.05): canonical "Version" still sets dynamic=true
echo "=== TEST: Regression — canonical Version still dynamic ==="
PASS_CAN_V=0
if cargo test -p uv-pypi-types -- injected_case_tests::test_canonical_version_still_dynamic 2>&1 | grep -q "test result: ok"; then
    PASS_CAN_V=1
fi
add_score 0.05 "$PASS_CAN_V"
echo "  Result: $PASS_CAN_V"

# [pr_diff] (0.05): existing upstream unit tests still pass
echo "=== TEST: Regression — upstream unit tests pass ==="
PASS_UPSTREAM=0
if cargo test -p uv-pypi-types -- metadata_resolver::tests 2>&1 | grep -q "test result: ok"; then
    PASS_UPSTREAM=1
fi
add_score 0.05 "$PASS_UPSTREAM"
echo "  Result: $PASS_UPSTREAM"

# Restore original file (remove injected tests)
mv "${FILE}.bak" "$FILE"

# ──────────────────────────────────────────────────────────────
# STRUCTURAL: Anti-stub (0.05)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): No stub/todo/unimplemented in the file
echo "=== TEST: Anti-stub ==="
PASS_NOSTUB=0
if ! grep -qE 'todo!\(|unimplemented!\(' "$FILE" 2>/dev/null; then
    PASS_NOSTUB=1
fi
add_score 0.05 "$PASS_NOSTUB"
echo "  Result: $PASS_NOSTUB"

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.05)
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): "AVOID using `panic!`, `unreachable!`, `.unwrap()`" — CLAUDE.md:7
echo "=== TEST: Config — no unwrap/panic in parse_pkg_info ==="
PASS_NOPANIC=0
FUNC_BODY=$(sed -n '/fn parse_pkg_info/,/^    }/p' "$FILE")
if ! echo "$FUNC_BODY" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(' 2>/dev/null; then
    PASS_NOPANIC=1
fi
add_score 0.05 "$PASS_NOPANIC"
echo "  Result: $PASS_NOPANIC"

# ──────────────────────────────────────────────────────────────
# FINAL SCORE
# ──────────────────────────────────────────────────────────────

echo ""
echo "=== SCORING ==="
echo "Total weight: $TOTAL"
echo "Score: $SCORE"

REWARD=$(python3 -c "print(round($SCORE, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

# Per-category breakdown
B_SCORE=$(python3 -c "print(round($PASS_RD * 0.20 + $PASS_RP * 0.15 + $PASS_PE * 0.15 + $PASS_VER * 0.15 + $PASS_UC * 0.10, 2))")
R_SCORE=$(python3 -c "print(round($PASS_CAN_RD * 0.05 + $PASS_CAN_V * 0.05 + $PASS_UPSTREAM * 0.05, 2))")
S_SCORE=$(python3 -c "print(round($PASS_NOSTUB * 0.05, 2))")
C_SCORE=$(python3 -c "print(round($PASS_NOPANIC * 0.05, 2))")

echo "{\"reward\": $REWARD, \"behavioral\": $B_SCORE, \"regression\": $R_SCORE, \"config\": $C_SCORE, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
