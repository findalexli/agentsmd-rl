#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
SCORE=0.0
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
BACKEND_RS="crates/uv-torch/src/backend.rs"
ACCEL_RS="crates/uv-torch/src/accelerator.rs"

# ============================================================
# GATE: Compilation check
# ============================================================
# [pr_diff] (GATE): Code compiles
echo "=== GATE: Compilation check ==="
if ! cargo check -p uv-torch 2>/tmp/compile_err.txt; then
    echo "GATE FAIL: cargo check -p uv-torch failed"
    cat /tmp/compile_err.txt
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$REWARD_JSON"
    exit 0
fi
echo "GATE PASS: uv-torch crate compiles"

# ============================================================
# Fail-to-pass: Behavioral tests (0.65 total)
# ============================================================
# Rust code requires compilation to call. cargo test with inline
# integration tests is the behavioral equivalent of calling the code.

mkdir -p crates/uv-torch/tests

# [pr_diff] (0.30): TorchBackend parses "rocm7.2" string
echo "=== Behavioral: TorchBackend FromStr parses rocm7.2 ==="
PASS_PARSE=0
cat > crates/uv-torch/tests/test_rocm72.rs <<'TESTEOF'
use std::str::FromStr;
use uv_torch::TorchBackend;

#[test]
fn test_rocm72_fromstr() {
    let backend = TorchBackend::from_str("rocm7.2");
    assert!(backend.is_ok(), "Failed to parse 'rocm7.2' as TorchBackend");
}
TESTEOF
if cargo test -p uv-torch --test test_rocm72 2>&1 | grep -q "test result: ok"; then
    PASS_PARSE=1
fi
rm -f crates/uv-torch/tests/test_rocm72.rs
add_score 0.30 $PASS_PARSE "TorchBackend::from_str(\"rocm7.2\") succeeds"

# [pr_diff] (0.15): ROCm version accessor returns 7.2 for the new backend
echo "=== Behavioral: ROCm version returns 7.2 ==="
PASS_VER=0
cat > crates/uv-torch/tests/test_rocm72_ver.rs <<'TESTEOF'
use std::str::FromStr;
use uv_torch::TorchBackend;

#[test]
fn test_rocm72_version() {
    let backend = TorchBackend::from_str("rocm7.2").unwrap();
    let rocm_ver = backend.rocm_version();
    assert!(rocm_ver.is_some(), "Rocm72 should return Some rocm_version");
    let ver = rocm_ver.unwrap();
    assert_eq!(ver.to_string(), "7.2", "ROCm version should be 7.2, got {ver}");
}

#[test]
fn test_rocm72_no_cuda_version() {
    let backend = TorchBackend::from_str("rocm7.2").unwrap();
    assert!(backend.cuda_version().is_none(), "Rocm72 should have no CUDA version");
}
TESTEOF
cp /dev/null /dev/null  # noop
if cargo test -p uv-torch --test test_rocm72_ver 2>&1 | grep -q "test result: ok"; then
    PASS_VER=1
fi
rm -f crates/uv-torch/tests/test_rocm72_ver.rs
add_score 0.15 $PASS_VER "ROCm version for rocm7.2 backend is 7.2 and CUDA version is None"

# [pr_diff] (0.15): New AMD GPU architectures gfx1150 and gfx1151 parse correctly
echo "=== Behavioral: AmdGpuArchitecture parses gfx1150/gfx1151 ==="
PASS_ARCH=0
cat > crates/uv-torch/tests/test_arch.rs <<'TESTEOF'
use std::str::FromStr;
use uv_torch::AmdGpuArchitecture;

#[test]
fn test_gfx1150_parse() {
    let arch = AmdGpuArchitecture::from_str("gfx1150");
    assert!(arch.is_ok(), "Failed to parse 'gfx1150'");
    assert_eq!(arch.unwrap().to_string(), "gfx1150");
}

#[test]
fn test_gfx1151_parse() {
    let arch = AmdGpuArchitecture::from_str("gfx1151");
    assert!(arch.is_ok(), "Failed to parse 'gfx1151'");
    assert_eq!(arch.unwrap().to_string(), "gfx1151");
}
TESTEOF
if cargo test -p uv-torch --test test_arch 2>&1 | grep -q "test result: ok"; then
    PASS_ARCH=1
fi
rm -f crates/uv-torch/tests/test_arch.rs
add_score 0.15 $PASS_ARCH "AmdGpuArchitecture parses gfx1150 and gfx1151"

# [pr_diff] (0.10): Index URLs for rocm7.2 are defined (PyTorch + Pyx)
echo "=== Behavioral: Index URLs for rocm7.2 ==="
PASS_URL=0
if grep -q 'download.pytorch.org/whl/rocm7.2' "$BACKEND_RS"; then
    # Verify both PyTorch and Pyx URL statics reference rocm7.2
    PT_COUNT=$(grep -c 'ROCM72_INDEX_URL' "$BACKEND_RS" || true)
    # Need at least 4 refs: 2 static defs + 2 usages in match arms
    if [ "$PT_COUNT" -ge 4 ]; then
        PASS_URL=1
    fi
fi
add_score 0.10 $PASS_URL "PyTorch and Pyx index URLs defined for ROCm 7.2"

# ============================================================
# Pass-to-pass: Regression tests (0.10 total)
# ============================================================

# [pr_diff] (0.10): Existing ROCm 7.1 backend still works
echo "=== Regression: Existing ROCm 7.1 still parses ==="
PASS_REG=0
cat > crates/uv-torch/tests/test_regression.rs <<'TESTEOF'
use std::str::FromStr;
use uv_torch::{TorchBackend, AmdGpuArchitecture};

#[test]
fn test_rocm71_still_parses() {
    let backend = TorchBackend::from_str("rocm7.1");
    assert!(backend.is_ok(), "rocm7.1 should still parse");
}

#[test]
fn test_existing_archs_still_parse() {
    for arch_str in &["gfx900", "gfx1100", "gfx1200"] {
        let arch = AmdGpuArchitecture::from_str(arch_str);
        assert!(arch.is_ok(), "Failed to parse existing arch {arch_str}");
    }
}
TESTEOF
if cargo test -p uv-torch --test test_regression 2>&1 | grep -q "test result: ok"; then
    PASS_REG=1
fi
rm -f crates/uv-torch/tests/test_regression.rs
add_score 0.10 $PASS_REG "Existing ROCm 7.1 and GPU architectures still parse correctly"

# ============================================================
# Structural checks (0.10 total)
# ============================================================

# [pr_diff] (0.05): GPU driver mappings include Rocm72 entries
echo "=== Structural: GPU driver mappings for ROCm 7.2 ==="
PASS_DRIVERS=0
# WHY grep not call: LINUX_AMD_GPU_DRIVERS is a static array used at runtime
# for GPU detection — no way to exercise it without running on AMD hardware.
DRIVER_COUNT=$(grep -c 'Rocm72.*Gfx\|Rocm72.*AmdGpu' "$BACKEND_RS" || true)
if [ "$DRIVER_COUNT" -ge 10 ]; then
    PASS_DRIVERS=1
fi
add_score 0.05 $PASS_DRIVERS "LINUX_AMD_GPU_DRIVERS includes >=10 Rocm72 architecture entries"

# [pr_diff] (0.05): Schema updated with rocm7.2
echo "=== Structural: JSON schema includes rocm7.2 ==="
PASS_SCHEMA=0
if grep -q '"rocm7.2"' uv.schema.json; then
    PASS_SCHEMA=1
fi
add_score 0.05 $PASS_SCHEMA "uv.schema.json includes rocm7.2 as a valid torch mode"

# ============================================================
# Config-derived checks (0.10 total)
# ============================================================

# [agent_config] (0.05): No panic!/unwrap() in new match arms — CLAUDE.md:7
echo "=== Config: No panic/unwrap in new enum handling ==="
PASS_NO_PANIC=0
# Extract Rocm72 lines excluding static URL defs (which use unwrap by convention)
ROCM72_LINES=$(grep -n 'Rocm72' "$BACKEND_RS" | grep -v 'INDEX_URL\|LazyLock\|static\|//\|LINUX_AMD_GPU' || true)
if ! echo "$ROCM72_LINES" | grep -q '\.unwrap()\|panic!'; then
    PASS_NO_PANIC=1
fi
add_score 0.05 $PASS_NO_PANIC "No unwrap()/panic! in Rocm72 match arms (CLAUDE.md:7)"

# [agent_config] (0.05): New GPU arch variants follow naming convention — CLAUDE.md:14
echo "=== Config: Naming convention for new architectures ==="
PASS_NAMING=0
if grep -q 'Gfx1150' "$ACCEL_RS" && grep -q 'Gfx1151' "$ACCEL_RS"; then
    if grep -q '"gfx1150"' "$ACCEL_RS" && grep -q '"gfx1151"' "$ACCEL_RS"; then
        PASS_NAMING=1
    fi
fi
add_score 0.05 $PASS_NAMING "New GPU architectures follow Gfx#### naming convention (CLAUDE.md:14)"

# ============================================================
# Final scoring
# ============================================================
echo ""
echo "==============================="
echo "Score: $SCORE / $TOTAL"
echo "==============================="

FINAL=$(python3 -c "print(min(1.0, max(0.0, round($SCORE, 4))))")
echo "$FINAL" > "$REWARD_FILE"
echo "{\"reward\": $FINAL}" > "$REWARD_JSON"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
