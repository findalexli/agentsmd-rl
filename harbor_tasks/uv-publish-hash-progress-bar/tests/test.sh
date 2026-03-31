#!/usr/bin/env bash
set -euo pipefail

REPO="/repo"
REWARD=0.0
BEHAVIORAL=0.0
REGRESSION=0.0
CONFIG=0.0

cd "$REPO"

########################################
# GATE: Syntax check — code must compile
########################################
# [pr_diff] (gate): Code compiles successfully
echo "=== GATE: cargo check uv-publish ==="
if ! cargo check -p uv-publish 2>&1; then
    echo "GATE FAILED: uv-publish does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "=== GATE: cargo check uv (commands) ==="
if ! cargo check -p uv 2>&1; then
    echo "GATE FAILED: uv crate does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

########################################
# Fail-to-pass: Reporter trait has hash methods
########################################

# [pr_diff] (0.15): Reporter trait defines on_hash_start method
echo "=== CHECK: Reporter trait has on_hash_start ==="
if grep -q 'fn on_hash_start' crates/uv-publish/src/lib.rs; then
    echo "PASS: on_hash_start found in Reporter trait"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.15" | bc)
else
    echo "FAIL: on_hash_start not found"
fi

# [pr_diff] (0.10): Reporter trait defines on_hash_progress and on_hash_complete
echo "=== CHECK: Reporter trait has on_hash_progress and on_hash_complete ==="
if grep -q 'fn on_hash_progress' crates/uv-publish/src/lib.rs && \
   grep -q 'fn on_hash_complete' crates/uv-publish/src/lib.rs; then
    echo "PASS: on_hash_progress and on_hash_complete found"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.10" | bc)
else
    echo "FAIL: hash progress/complete methods missing"
fi

# [pr_diff] (0.15): hash_file accepts reporter parameter
echo "=== CHECK: hash_file accepts reporter ==="
if grep -A5 'async fn hash_file' crates/uv-publish/src/lib.rs | grep -q 'reporter'; then
    echo "PASS: hash_file accepts reporter"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.15" | bc)
else
    echo "FAIL: hash_file does not accept reporter"
fi

# [pr_diff] (0.10): FormMetadata::read_from_file accepts reporter parameter
echo "=== CHECK: FormMetadata::read_from_file accepts reporter ==="
if grep -A5 'pub async fn read_from_file' crates/uv-publish/src/lib.rs | grep -q 'reporter'; then
    echo "PASS: read_from_file accepts reporter"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.10" | bc)
else
    echo "FAIL: read_from_file does not accept reporter"
fi

# [pr_diff] (0.10): check_url accepts reporter parameter
echo "=== CHECK: check_url accepts reporter ==="
if grep -A8 'pub async fn check_url' crates/uv-publish/src/lib.rs | grep -q 'reporter'; then
    echo "PASS: check_url accepts reporter"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.10" | bc)
else
    echo "FAIL: check_url does not accept reporter"
fi

# [pr_diff] (0.10): Direction enum has Hash variant in reporters.rs
echo "=== CHECK: Direction::Hash variant exists ==="
if grep -qP '^\s+Hash' crates/uv/src/commands/reporters.rs; then
    echo "PASS: Hash variant found in Direction"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.10" | bc)
else
    echo "FAIL: Hash variant not found"
fi

########################################
# Fail-to-pass: Publish flow shows Hashing then Uploading
########################################

# [pr_diff] (0.10): Publish command prints "Hashing" before hash computation
echo "=== CHECK: publish.rs prints Hashing status ==="
if grep -q '"Hashing"' crates/uv/src/commands/publish.rs; then
    echo "PASS: Hashing status message found"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.10" | bc)
else
    echo "FAIL: Hashing status not found in publish.rs"
fi

########################################
# Pass-to-pass: PublishReporter still implements upload methods
########################################

# [pr_diff] (0.05): PublishReporter still has on_upload_start
echo "=== CHECK: PublishReporter retains upload methods ==="
if grep -q 'fn on_upload_start' crates/uv/src/commands/reporters.rs; then
    echo "PASS: upload methods preserved"
    REGRESSION=$(echo "$REGRESSION + 0.05" | bc)
else
    echo "FAIL: upload methods missing from reporters.rs"
fi

########################################
# Config-derived checks
########################################

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap(), unsafe code" — CLAUDE.md:6
echo "=== CHECK: No unwrap() in new hash_file code ==="
if python3 -c "
import re
with open('crates/uv-publish/src/lib.rs') as f:
    content = f.read()
# Find the hash_file function body
match = re.search(r'async fn hash_file\b.*?\n\}', content, re.DOTALL)
if match:
    fn_body = match.group(0)
    if '.unwrap()' in fn_body:
        exit(1)
exit(0)
"; then
    echo "PASS: No unwrap() in hash_file"
    CONFIG=$(echo "$CONFIG + 0.05" | bc)
else
    echo "FAIL: unwrap() found in hash_file"
fi

# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:13
echo "=== CHECK: DistFilename import is top-level in reporters.rs ==="
if head -30 crates/uv/src/commands/reporters.rs | grep -q 'DistFilename'; then
    echo "PASS: DistFilename imported at top level"
    CONFIG=$(echo "$CONFIG + 0.05" | bc)
else
    echo "FAIL: DistFilename not imported at top level"
fi

########################################
# Anti-stub: hash methods have real bodies
########################################

# [pr_diff] (0.05): PublishReporter hash methods delegate to inner reporter
echo "=== CHECK: PublishReporter::on_hash_start delegates ==="
if python3 -c "
with open('crates/uv/src/commands/reporters.rs') as f:
    content = f.read()
import re
match = re.search(r'impl uv_publish::Reporter for PublishReporter.*?\n\}', content, re.DOTALL)
if match:
    impl_body = match.group(0)
    if 'on_hash_start' in impl_body and 'on_hash_progress' in impl_body and 'on_hash_complete' in impl_body:
        exit(0)
exit(1)
"; then
    echo "PASS: PublishReporter implements all hash methods"
    BEHAVIORAL=$(echo "$BEHAVIORAL + 0.05" | bc)
else
    echo "FAIL: PublishReporter missing hash method implementations"
fi

########################################
# Summary
########################################

REWARD=$(echo "$BEHAVIORAL + $REGRESSION + $CONFIG" | bc)

echo ""
echo "=== RESULTS ==="
echo "Behavioral: $BEHAVIORAL | Regression: $REGRESSION | Config: $CONFIG"
echo "Total: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json <<ENDJSON
{
  "reward": $REWARD,
  "behavioral": $BEHAVIORAL,
  "regression": $REGRESSION,
  "config": $CONFIG,
  "style_rubric": 0.0
}
ENDJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
