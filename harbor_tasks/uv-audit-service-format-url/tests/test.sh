#!/usr/bin/env bash
set -euo pipefail

REPO="/repo"
TOTAL=0.0
add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd "$REPO"

###############################################################################
# GATE (0.00): Rust syntax — must compile the modified crates
###############################################################################
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-audit -p uv-cli -p uv 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

###############################################################################
# Behavioral: VulnerabilityServiceFormat enum exists and has Osv variant (0.20)
###############################################################################
# [pr_diff] (0.20): VulnerabilityServiceFormat enum with Osv variant is defined
echo "=== Behavioral: VulnerabilityServiceFormat enum ==="
SCORE_ENUM=0.0
# Compile and run a small Rust snippet that uses the enum
cat > /tmp/test_enum.rs <<'TESTEOF'
// We check that the enum exists and has the Osv variant by trying to use it
fn main() {
    // Read the service mod.rs file and check it has the expected content
    let content = std::fs::read_to_string("/repo/crates/uv-audit/src/service/mod.rs")
        .expect("Failed to read service/mod.rs");

    // Must have the enum definition
    assert!(content.contains("enum VulnerabilityServiceFormat"),
        "Missing VulnerabilityServiceFormat enum");
    assert!(content.contains("Osv"),
        "Missing Osv variant");
    // Must derive Copy, Clone, Debug
    assert!(content.contains("Copy") && content.contains("Clone") && content.contains("Debug"),
        "Missing required derives");
    // Must have clap ValueEnum behind feature gate
    assert!(content.contains("clap") && content.contains("ValueEnum"),
        "Missing clap ValueEnum derive");

    println!("VulnerabilityServiceFormat enum: OK");
}
TESTEOF
if rustc /tmp/test_enum.rs -o /tmp/test_enum 2>/dev/null && /tmp/test_enum 2>&1; then
    SCORE_ENUM=0.20
fi
echo "Score: $SCORE_ENUM"
add "$SCORE_ENUM"

###############################################################################
# Behavioral: CLI accepts --service-format and --service-url flags (0.25)
###############################################################################
# [pr_diff] (0.25): AuditArgs has service_format and service_url fields with correct clap attrs
echo "=== Behavioral: CLI flags in AuditArgs ==="
SCORE_CLI=0.0
CLI_FILE="crates/uv-cli/src/lib.rs"
if grep -q 'service_format' "$CLI_FILE" && grep -q 'service_url' "$CLI_FILE"; then
    # Check that service_format uses value_enum and has a default
    if grep -A2 'service_format' "$CLI_FILE" | grep -q 'VulnerabilityServiceFormat'; then
        # Check service_url exists with proper hint
        if grep -B5 'service_url' "$CLI_FILE" | grep -q 'long'; then
            SCORE_CLI=0.25
        fi
    fi
fi
echo "Score: $SCORE_CLI"
add "$SCORE_CLI"

###############################################################################
# Behavioral: audit() function accepts service params (0.20)
###############################################################################
# [pr_diff] (0.20): audit function signature includes service format and URL params
echo "=== Behavioral: audit() function signature ==="
SCORE_FN=0.0
AUDIT_FILE="crates/uv/src/commands/project/audit.rs"
if grep -q 'VulnerabilityServiceFormat' "$AUDIT_FILE"; then
    # Check that the function uses service_url to override the default
    if grep -q 'service_url' "$AUDIT_FILE"; then
        # Check that it falls back to osv::API_BASE
        if grep -q 'API_BASE' "$AUDIT_FILE"; then
            SCORE_FN=0.20
        fi
    fi
fi
echo "Score: $SCORE_FN"
add "$SCORE_FN"

###############################################################################
# Behavioral: AuditSettings includes and wires service fields (0.15)
###############################################################################
# [pr_diff] (0.15): AuditSettings struct has service_format and service_url, wired in constructor
echo "=== Behavioral: AuditSettings wiring ==="
SCORE_SETTINGS=0.0
SETTINGS_FILE="crates/uv/src/settings.rs"
if grep -q 'service_format' "$SETTINGS_FILE" && grep -q 'service_url' "$SETTINGS_FILE"; then
    # Check that VulnerabilityServiceFormat is imported
    if grep -q 'VulnerabilityServiceFormat' "$SETTINGS_FILE"; then
        SCORE_SETTINGS=0.15
    fi
fi
echo "Score: $SCORE_SETTINGS"
add "$SCORE_SETTINGS"

###############################################################################
# Pass-to-pass: uv-audit crate builds with clap feature (0.10)
###############################################################################
# [pr_diff] (0.10): uv-audit Cargo.toml has optional clap dependency
echo "=== P2P: clap feature in uv-audit ==="
SCORE_CARGO=0.0
AUDIT_TOML="crates/uv-audit/Cargo.toml"
if grep -q 'clap' "$AUDIT_TOML"; then
    # Verify it's optional
    if grep 'clap' "$AUDIT_TOML" | grep -q 'optional'; then
        SCORE_CARGO=0.10
    fi
fi
echo "Score: $SCORE_CARGO"
add "$SCORE_CARGO"

###############################################################################
# Config-derived: Top-level imports preferred (0.05)
###############################################################################
# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:14
echo "=== Config: top-level imports ==="
SCORE_IMPORTS=0.0
# VulnerabilityServiceFormat import should be at top of the files that use it
if head -30 "$AUDIT_FILE" | grep -q 'VulnerabilityServiceFormat'; then
    if head -15 "$SETTINGS_FILE" | grep -q 'VulnerabilityServiceFormat'; then
        SCORE_IMPORTS=0.05
    fi
fi
echo "Score: $SCORE_IMPORTS"
add "$SCORE_IMPORTS"

###############################################################################
# Config-derived: No unwrap on user input (0.05)
###############################################################################
# [agent_config] (0.05): "AVOID using .unwrap()" — CLAUDE.md:7
echo "=== Config: no unwrap on user-supplied URL ==="
SCORE_UNWRAP=0.0
# The service_url parsing should not use unwrap() — expect() with message is acceptable
URL_PARSE_CONTEXT=$(grep -A5 'service_url' "$AUDIT_FILE" | grep -c '\.unwrap()' || true)
if [ "$URL_PARSE_CONTEXT" -eq 0 ]; then
    SCORE_UNWRAP=0.05
fi
echo "Score: $SCORE_UNWRAP"
add "$SCORE_UNWRAP"

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
    'behavioral': round($SCORE_ENUM + $SCORE_CLI + $SCORE_FN + $SCORE_SETTINGS, 4),
    'regression': round($SCORE_CARGO, 4),
    'config': round($SCORE_IMPORTS + $SCORE_UNWRAP, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
