#!/usr/bin/env bash
set +e  # Don't exit on failure — we accumulate scores

cd /src

TOTAL=0.0
REWARD=0.0
DETAILS=""

add_score() {
    local weight=$1 label=$2 pass=$3
    TOTAL=$(python3 -c "print(${TOTAL} + ${weight})")
    if [ "$pass" = "1" ]; then
        REWARD=$(python3 -c "print(${REWARD} + ${weight})")
        DETAILS="${DETAILS}PASS (${weight}): ${label}\n"
    else
        DETAILS="${DETAILS}FAIL (${weight}): ${label}\n"
    fi
}

gate_fail() {
    echo "GATE FAIL: $1"
    echo "0.0" > /logs/verifier/reward.txt
    printf '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}\n' > /logs/verifier/reward.json
    exit 0
}

# ============================================================
# GATE: Compilation check
# ============================================================
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-distribution-types -p uv-client 2>&1; then
    gate_fail "Code does not compile"
fi

# ============================================================
# BEHAVIORAL FAIL-TO-PASS: Invalid cache-control rejected at deserialization
# ============================================================

# [pr_diff] (0.45): Invalid HTTP header values in cache-control are rejected during deserialization
echo "=== F2P: Invalid cache-control values rejected at deserialization ==="
mkdir -p crates/uv-distribution-types/tests
cat > crates/uv-distribution-types/tests/cache_control_validation.rs << 'RUSTTEST'
use uv_distribution_types::Index;

/// Newline character is invalid in HTTP header values.
/// TOML basic strings interpret \n as a literal newline.
/// On buggy code: toml::from_str succeeds (SmallString accepts anything).
/// On fixed code: toml::from_str fails (HeaderValue rejects newlines).
#[test]
fn newline_in_api_cache_control_rejected() {
    let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n\
                    [cache-control]\napi = \"max-age=600\\n\"\n";
    let result = toml::from_str::<Index>(toml_str);
    assert!(
        result.is_err(),
        "Cache-control with newline should be rejected at deserialization, got: {:?}",
        result.unwrap()
    );
}

/// Carriage return is also invalid in HTTP header values.
#[test]
fn carriage_return_in_cache_control_rejected() {
    let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n\
                    [cache-control]\napi = \"max-age=600\\r\"\n";
    let result = toml::from_str::<Index>(toml_str);
    assert!(
        result.is_err(),
        "Cache-control with CR should be rejected at deserialization, got: {:?}",
        result.unwrap()
    );
}

/// Null byte is invalid in HTTP header values.
/// Use \u0000 which is a valid TOML unicode escape that produces a null byte.
#[test]
fn null_byte_in_cache_control_rejected() {
    let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n\
                    [cache-control]\nfiles = \"max-age=3600\\u0000\"\n";
    let result = toml::from_str::<Index>(toml_str);
    assert!(
        result.is_err(),
        "Cache-control with null byte should be rejected at deserialization, got: {:?}",
        result.unwrap()
    );
}

/// Non-visible ASCII (DEL = 0x7F) is invalid in HTTP header values.
#[test]
fn del_byte_in_cache_control_rejected() {
    let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n\
                    [cache-control]\napi = \"max-age=600\\u007f\"\n";
    let result = toml::from_str::<Index>(toml_str);
    assert!(
        result.is_err(),
        "Cache-control with DEL byte should be rejected at deserialization, got: {:?}",
        result.unwrap()
    );
}

/// Valid cache-control values MUST still be accepted (any correct fix must pass this).
#[test]
fn valid_cache_control_accepted() {
    let toml_str = r#"
        name = "test-index"
        url = "https://test.example.com/simple"
        [cache-control]
        api = "max-age=600"
        files = "max-age=3600"
    "#;
    let result = toml::from_str::<Index>(toml_str);
    assert!(result.is_ok(), "Valid cache-control should be accepted, got: {:?}", result.err());
}

/// Various valid HTTP cache-control directives must all be accepted.
#[test]
fn valid_cache_control_directives_accepted() {
    let directives = vec![
        "no-cache",
        "no-store",
        "max-age=0",
        "private, max-age=3600, must-revalidate",
        "public, s-maxage=31536000",
    ];
    for directive in directives {
        let toml_str = format!(
            "name = \"test\"\nurl = \"https://x.com/simple\"\n\
             [cache-control]\napi = \"{}\"\n",
            directive
        );
        let result = toml::from_str::<Index>(&toml_str);
        assert!(
            result.is_ok(),
            "Valid cache-control directive '{}' should be accepted, got: {:?}",
            directive,
            result.err()
        );
    }
}
RUSTTEST

PASS_F2P_DESER=0
if cargo test -p uv-distribution-types --test cache_control_validation 2>&1; then
    PASS_F2P_DESER=1
fi
rm -f crates/uv-distribution-types/tests/cache_control_validation.rs
add_score 0.45 "Invalid cache-control values rejected at deserialization (F2P)" "$PASS_F2P_DESER"

# ============================================================
# BEHAVIORAL PASS-TO-PASS: Valid cache-control round-trips through serialize/deserialize
# ============================================================

# [pr_diff] (0.10): Valid cache-control survives serialization round-trip
echo "=== P2P: Cache-control round-trip serialization ==="
mkdir -p crates/uv-distribution-types/tests
cat > crates/uv-distribution-types/tests/cache_control_roundtrip.rs << 'RUSTTEST'
use uv_distribution_types::Index;

#[test]
fn cache_control_round_trips() {
    let toml_str = r#"
        name = "test-index"
        url = "https://test.example.com/simple"
        [cache-control]
        api = "max-age=600"
        files = "no-cache, must-revalidate"
    "#;
    let index: Index = toml::from_str(toml_str).expect("Initial parse should succeed");
    let serialized = toml::to_string(&index).expect("Serialization should succeed");
    let index2: Index = toml::from_str(&serialized).expect("Round-trip parse should succeed");
    let serialized2 = toml::to_string(&index2).expect("Second serialization should succeed");
    assert_eq!(serialized, serialized2, "Round-trip serialization should be stable");
}

#[test]
fn cache_control_only_api_round_trips() {
    let toml_str = r#"
        name = "test-index"
        url = "https://test.example.com/simple"
        [cache-control]
        api = "max-age=300"
    "#;
    let index: Index = toml::from_str(toml_str).expect("Parse should succeed");
    let serialized = toml::to_string(&index).expect("Serialization should succeed");
    assert!(serialized.contains("max-age=300"), "Serialized output should preserve the api value");
}
RUSTTEST

PASS_P2P_ROUNDTRIP=0
if cargo test -p uv-distribution-types --test cache_control_roundtrip 2>&1; then
    PASS_P2P_ROUNDTRIP=1
fi
rm -f crates/uv-distribution-types/tests/cache_control_roundtrip.rs
add_score 0.10 "Valid cache-control round-trips through serialize/deserialize (P2P)" "$PASS_P2P_ROUNDTRIP"

# ============================================================
# REGRESSION: Existing upstream cache-control tests still pass
# ============================================================

# [repo_tests] (0.15): Existing cache-control unit tests pass
echo "=== P2P: Existing upstream cache-control tests ==="
PASS_REGRESSION=0
if cargo test -p uv-distribution-types -- test_index_cache_control 2>&1; then
    PASS_REGRESSION=1
fi
add_score 0.15 "Existing upstream cache-control tests pass (P2P)" "$PASS_REGRESSION"

# ============================================================
# STRUCTURAL: IndexCacheControl type safety
# ============================================================

# [pr_diff] (0.15): IndexCacheControl no longer stores raw unvalidated strings
echo "=== Structural: IndexCacheControl validated types ==="
INDEX_RS="crates/uv-distribution-types/src/index.rs"
PASS_STRUCT=0
# WHY STRUCTURAL: We can't instantiate Rust struct fields from bash to check types at runtime.
# Check that the struct no longer uses raw SmallString (unvalidated) for cache-control fields.
# This accepts ANY validated type: HeaderValue, a newtype wrapper, Arc<str> with validation, etc.
# It only rejects the KNOWN-BUGGY type (SmallString) which stores arbitrary strings without validation.
if [ -f "$INDEX_RS" ]; then
    # SmallString is the buggy type — any replacement indicates the fix changed the storage type
    if ! grep -q 'pub api: Option<SmallString>' "$INDEX_RS" 2>/dev/null && \
       ! grep -q 'pub files: Option<SmallString>' "$INDEX_RS" 2>/dev/null; then
        PASS_STRUCT=1
    fi
fi
add_score 0.15 "IndexCacheControl fields no longer store raw SmallString" "$PASS_STRUCT"

# ============================================================
# CONFIG-DERIVED: CLAUDE.md rules
# ============================================================

# [agent_config] (0.10): "AVOID using panic!, unreachable!, .unwrap(), unsafe code" — CLAUDE.md:7
echo "=== Config: no panicking .expect() on cache-control header ==="
PASS_CONFIG=0
# Check that cached_client.rs does not use .expect() to convert cache-control values.
# This catches the specific bug pattern (.expect on HeaderValue conversion) regardless of message text.
# WHY GREP: We cannot call internal Rust functions from bash to test panic behavior.
CACHED_CLIENT="crates/uv-client/src/cached_client.rs"
if [ -f "$CACHED_CLIENT" ]; then
    # Extract lines related to cache-control/Override handling and check for .expect()
    # Look for any .expect() near HeaderValue or cache.control patterns within 3 lines
    EXPECT_NEAR_HEADER=$(python3 -c "
import re
with open('$CACHED_CLIENT') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    # Look for .expect() calls that are about header value conversion
    if '.expect(' in line:
        context = ''.join(lines[max(0,i-3):i+4]).lower()
        if 'cache' in context or 'header' in context or 'headervalue' in context:
            print('FOUND')
            break
" 2>/dev/null)
    if [ "$EXPECT_NEAR_HEADER" != "FOUND" ]; then
        PASS_CONFIG=1
    fi
fi
add_score 0.10 "No panicking .expect() on cache-control header conversion (config)" "$PASS_CONFIG"

# [agent_config] (0.05): "PREFER if let to handle fallibility" — CLAUDE.md:8
echo "=== Config: proper error handling in deserialization ==="
PASS_CONFIG_STYLE=0
# Check that the deserialization code in index.rs uses proper error propagation.
# Accept any standard Rust error-handling pattern, not just one specific idiom.
if [ -f "$INDEX_RS" ]; then
    # Look for ANY of: serde error propagation, Result handling, map_err, ?, Error::custom, from_str
    HAS_VALIDATION=$(python3 -c "
import re
with open('$INDEX_RS') as f:
    content = f.read()
# Look for evidence of validation during deserialization (any of these patterns)
patterns = [
    r'Error::custom',       # serde custom error
    r'map_err',             # error mapping
    r'HeaderValue::from',   # explicit validation via HeaderValue
    r'from_str.*\.map_err', # parse-and-map pattern
    r'Deserialize.*impl',   # custom Deserialize impl (not derive)
    r'fn deserialize',      # custom deserialize function
]
for p in patterns:
    if re.search(p, content):
        print('FOUND')
        break
" 2>/dev/null)
    if [ "$HAS_VALIDATION" = "FOUND" ]; then
        PASS_CONFIG_STYLE=1
    fi
fi
add_score 0.05 "Proper error handling / validation in deserialization (config)" "$PASS_CONFIG_STYLE"

# ============================================================
# RESULTS
# ============================================================

echo ""
echo "=== RESULTS ==="
printf "$DETAILS"
echo ""
echo "Total: ${REWARD} / ${TOTAL}"

# Compute sub-scores for reward.json
BEHAVIORAL=$(python3 -c "print(round(${PASS_F2P_DESER} * 0.45 + ${PASS_P2P_ROUNDTRIP} * 0.10 + ${PASS_REGRESSION} * 0.15, 2))")
CONFIG=$(python3 -c "print(round(${PASS_CONFIG} * 0.10 + ${PASS_CONFIG_STYLE} * 0.05, 2))")
STRUCTURAL=$(python3 -c "print(round(${PASS_STRUCT} * 0.15, 2))")

echo "${REWARD}" > /logs/verifier/reward.txt
python3 -c "
import json
print(json.dumps({
    'reward': round(${REWARD}, 2),
    'behavioral': ${BEHAVIORAL},
    'regression': 0.0,
    'config': ${CONFIG},
    'style_rubric': ${STRUCTURAL}
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
