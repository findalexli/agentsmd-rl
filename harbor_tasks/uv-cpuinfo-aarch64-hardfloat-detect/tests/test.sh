#!/usr/bin/env bash
set -euo pipefail

cd /workspace
SCORE=0

# ═══════════════════════════════════════════════════════════════════════════════
# GATE: Syntax check — crate must compile
# [pr_diff] (gate): Modified uv-platform crate compiles
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== GATE: cargo check -p uv-platform ==="
if ! cargo check -p uv-platform 2>&1; then
    echo "GATE FAILED: crate does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt
    exit 0
fi
echo "[GATE] PASSED"

# ═══════════════════════════════════════════════════════════════════════════════
# BEHAVIORAL: Feature detection handles vfp, fp, and rejects false positives
# [pr_diff] (0.70): Hard-float detection works for both ARM and AArch64 features
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "=== BEHAVIORAL: feature detection tests ==="
if python3 /tests/test_behavioral.py; then
    SCORE=$(echo "$SCORE + 0.70" | bc)
    echo "[BEHAVIORAL] PASSED (+0.70)"
else
    echo "[BEHAVIORAL] FAILED"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PASS-TO-PASS: cargo test on the crate
# [pr_diff] (0.10): Existing and new tests in uv-platform pass
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "=== PASS-TO-PASS: cargo test -p uv-platform ==="
if cargo test -p uv-platform 2>&1; then
    SCORE=$(echo "$SCORE + 0.10" | bc)
    echo "[P2P] PASSED (+0.10)"
else
    echo "[P2P] FAILED"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG-DERIVED: No unwrap/panic/unreachable in cpuinfo.rs
# [agent_config] (0.10): "AVOID using panic!, unreachable!, .unwrap(), unsafe code"
#   — CLAUDE.md:7 @ 87950df
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "=== CONFIG: no unwrap/panic in cpuinfo.rs ==="
SRC="crates/uv-platform/src/cpuinfo.rs"
# Check for .unwrap(), .expect(, panic!, unreachable! outside of comments and test modules
VIOLATIONS=$(sed '/#\[cfg(test)\]/,$d' "$SRC" \
    | grep -vE '^\s*//' \
    | grep -cE '\.unwrap\(\)|\.expect\(|panic!|unreachable!' || true)
if [ "$VIOLATIONS" -eq 0 ]; then
    SCORE=$(echo "$SCORE + 0.10" | bc)
    echo "[CONFIG] PASSED (+0.10)"
else
    echo "[CONFIG] FAILED — found $VIOLATIONS violation(s)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# ANTI-STUB: Non-trivial detection logic
# [pr_diff] (0.10): Feature detection is not trivially stubbed
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "=== ANTI-STUB: non-trivial logic ==="
if python3 /tests/test_antistub.py; then
    SCORE=$(echo "$SCORE + 0.10" | bc)
    echo "[ANTISTUB] PASSED (+0.10)"
else
    echo "[ANTISTUB] FAILED"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Final score
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════"
echo "Total reward: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
