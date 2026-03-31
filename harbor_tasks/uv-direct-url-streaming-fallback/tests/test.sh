#!/usr/bin/env bash
set +e

TOTAL=0
SCORE=0

add() {
    local w=$1 p=$2
    TOTAL=$(python3 -c "print($TOTAL + $w)")
    if [ "$p" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $w)")
    fi
}

cd /repo
FILE="crates/uv-distribution/src/distribution_database.rs"

# ──────────────────────────────────────────────────────────────
# GATE: Compilation check
# ──────────────────────────────────────────────────────────────
# [pr_diff] (gate): Source must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-distribution 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────────────────────
# Analysis: strip comments, extract match arms
#
# All checks operate on COMMENT-STRIPPED source to prevent
# comment-injection gaming. Rust // and /* */ comments are removed
# before any pattern matching.
#
# Justification for source inspection: The code under test is an
# async method on DistributionDatabase requiring HTTP clients, cache
# infra, and async runtime. It cannot be called in isolation.
# ──────────────────────────────────────────────────────────────
python3 << 'PYEOF' > /tmp/analysis.json
import re, json, sys

with open("crates/uv-distribution/src/distribution_database.rs") as f:
    source = f.read()

# Strip block comments /* ... */ then line comments //
stripped = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
stripped = re.sub(r'//[^\n]*', '', stripped)

# Extract BuiltDist::DirectUrl block (up to BuiltDist::Path)
lines = stripped.split('\n')
in_block = False
direct_url_lines = []
for line in lines:
    if 'BuiltDist::DirectUrl' in line:
        in_block = True
    if in_block:
        direct_url_lines.append(line)
    if in_block and 'BuiltDist::Path' in line:
        break
du = '\n'.join(direct_url_lines)

# Extract BuiltDist::Registry block (up to BuiltDist::DirectUrl)
in_block = False
registry_lines = []
for line in lines:
    if 'BuiltDist::Registry' in line:
        in_block = True
    if in_block:
        registry_lines.append(line)
    if in_block and 'BuiltDist::DirectUrl' in line:
        break
reg = '\n'.join(registry_lines)

results = {
    # Core fix: Err() match arm uses Error::Extract, not Error::Client
    "du_err_pattern_extract": bool(re.search(r'Err\s*\(\s*Error::Extract', du)),
    "du_err_pattern_client": bool(re.search(r'Err\s*\(\s*Error::Client', du)),
    # Error::Extract has proper two-arg destructuring (any var names)
    "du_extract_destructured": bool(re.search(r'Error::Extract\s*\(\s*\w+\s*,\s*\w+\s*\)', du)),
    # Streaming error methods called (in executable code, not comments)
    "du_has_streaming_failed": bool(re.search(r'is_http_streaming_failed', du)),
    "du_has_streaming_unsupported": bool(re.search(r'is_http_streaming_unsupported', du)),
    "du_has_download_wheel": bool(re.search(r'download_wheel', du)),
    "du_has_stream_wheel": bool(re.search(r'stream_wheel', du)),
    # Non-streaming errors re-raised
    "du_return_err_extract": bool(re.search(r'return\s+Err\s*\(\s*Error::Extract', du)),
    # Registry arm intact
    "reg_has_streaming_unsupported": bool(re.search(r'is_http_streaming_unsupported', reg)),
    "reg_has_download_wheel": bool(re.search(r'download_wheel', reg)),
    # Anti-stub: meaningful line count in DirectUrl block
    "du_meaningful_lines": len([l for l in direct_url_lines if l.strip()]),
    # Full-file checks
    "has_fn_stream_wheel": bool(re.search(r'fn\s+stream_wheel', stripped)),
    "has_fn_download_wheel": bool(re.search(r'fn\s+download_wheel', stripped)),
    "du_has_panic_unwrap": bool(re.search(r'\.unwrap\(\)|panic!\(|unreachable!\(', du)),
    "has_todo_unimplemented": bool(re.search(r'todo!\(|unimplemented!\(', stripped)),
}
json.dump(results, sys.stdout)
PYEOF

if [ $? -ne 0 ]; then
    echo "Analysis script failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Helper: read a boolean/int from analysis JSON
val() { python3 -c "import json; print(json.load(open('/tmp/analysis.json'))['$1'])"; }

# ──────────────────────────────────────────────────────────────
# BEHAVIORAL: Fail-to-pass checks on comment-stripped source (0.60)
# These verify the core bug fix. On the buggy base commit, each FAILS.
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.25): DirectUrl Err arm matches Error::Extract, NOT Error::Client
# Bug: old code had Err(Error::Client(err)) — wrong variant, fallback never triggers
echo "=== TEST: Err pattern uses Error::Extract, not Error::Client ==="
P1=0
if [ "$(val du_err_pattern_extract)" = "True" ] && \
   [ "$(val du_err_pattern_client)" = "False" ]; then
    P1=1
fi
add 0.25 "$P1"
echo "  Result: $P1"

# [pr_diff] (0.20): is_http_streaming_failed() handled in DirectUrl block
# Bug: old code had no handling for mid-stream failures at all
echo "=== TEST: is_http_streaming_failed handled ==="
P2=0
if [ "$(val du_has_streaming_failed)" = "True" ]; then
    P2=1
fi
add 0.20 "$P2"
echo "  Result: $P2"

# [pr_diff] (0.15): Both streaming error types + download_wheel fallback present
# Bug: old code only handled unsupported (and with wrong variant)
echo "=== TEST: Both streaming paths fall through to download_wheel ==="
P3=0
if [ "$(val du_has_streaming_unsupported)" = "True" ] && \
   [ "$(val du_has_streaming_failed)" = "True" ] && \
   [ "$(val du_has_download_wheel)" = "True" ]; then
    P3=1
fi
add 0.15 "$P3"
echo "  Result: $P3"

# ──────────────────────────────────────────────────────────────
# REGRESSION: Pass-to-pass checks (0.20)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): Non-streaming Extract errors must still propagate
echo "=== TEST: Non-streaming errors re-raised ==="
P4=0
if [ "$(val du_return_err_extract)" = "True" ]; then
    P4=1
fi
add 0.05 "$P4"
echo "  Result: $P4"

# [pr_diff] (0.05): Registry arm still handles streaming correctly (unchanged)
echo "=== TEST: Registry arm intact ==="
P5=0
if [ "$(val reg_has_streaming_unsupported)" = "True" ] && \
   [ "$(val reg_has_download_wheel)" = "True" ]; then
    P5=1
fi
add 0.05 "$P5"
echo "  Result: $P5"

# [pr_diff] (0.05): stream_wheel still called first in DirectUrl arm
echo "=== TEST: stream_wheel still called first ==="
P6=0
if [ "$(val du_has_stream_wheel)" = "True" ]; then
    P6=1
fi
add 0.05 "$P6"
echo "  Result: $P6"

# [pr_diff] (0.05): Both core functions still exist in the file
echo "=== TEST: Both stream and download functions exist ==="
P7=0
if [ "$(val has_fn_stream_wheel)" = "True" ] && \
   [ "$(val has_fn_download_wheel)" = "True" ]; then
    P7=1
fi
add 0.05 "$P7"
echo "  Result: $P7"

# ──────────────────────────────────────────────────────────────
# STRUCTURAL: Anti-stub + anti-gaming (0.10)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.05): No todo!/unimplemented! stubs in the file
echo "=== TEST: Anti-stub — no todo/unimplemented ==="
P8=0
if [ "$(val has_todo_unimplemented)" = "False" ]; then
    P8=1
fi
add 0.05 "$P8"
echo "  Result: $P8"

# [pr_diff] (0.05): DirectUrl block has substantial code (>20 meaningful lines)
echo "=== TEST: Anti-stub — block not hollowed out ==="
P9=0
DU_LINES=$(val du_meaningful_lines)
if [ "$DU_LINES" -gt 20 ] 2>/dev/null; then
    P9=1
fi
add 0.05 "$P9"
echo "  Result: $P9 ($DU_LINES lines)"

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10)
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): No unwrap/panic in DirectUrl handler — CLAUDE.md:7 @ 5ad8577
echo "=== TEST: Config — no panic/unwrap ==="
P10=0
if [ "$(val du_has_panic_unwrap)" = "False" ]; then
    P10=1
fi
add 0.05 "$P10"
echo "  Result: $P10"

# [agent_config] (0.05): Error::Extract uses proper destructuring — CLAUDE.md:7 @ 5ad8577
echo "=== TEST: Config — proper error destructuring ==="
P11=0
if [ "$(val du_extract_destructured)" = "True" ]; then
    P11=1
fi
add 0.05 "$P11"
echo "  Result: $P11"

# ──────────────────────────────────────────────────────────────
# FINAL SCORE
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== SCORING ==="
echo "Total weight: $TOTAL"
echo "Score: $SCORE"

REWARD=$(python3 -c "print(round($SCORE, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

B=$(python3 -c "print(round($P1*0.25 + $P2*0.20 + $P3*0.15, 2))")
R=$(python3 -c "print(round($P4*0.05 + $P5*0.05 + $P6*0.05 + $P7*0.05, 2))")
S=$(python3 -c "print(round($P8*0.05 + $P9*0.05, 2))")
C=$(python3 -c "print(round($P10*0.05 + $P11*0.05, 2))")

echo "{\"reward\": $REWARD, \"behavioral\": $B, \"regression\": $R, \"config\": $C, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
