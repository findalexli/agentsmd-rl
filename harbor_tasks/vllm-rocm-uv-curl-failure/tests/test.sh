#!/usr/bin/env bash
set -uo pipefail

cd /repo

PASS=0
TARGET="docker/Dockerfile.rocm"

award() { PASS=$(python3 -c "print($PASS + $1)"); }

# ── GATE: Target file must exist ─────────────────────────────────────────────
# [pr_diff] (gate): Dockerfile.rocm must exist
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: $TARGET exists"

# ── Helper: extract UV install RUN command from Dockerfile ────────────────────
cat > /tmp/extract_uv_cmd.py << 'PYEOF'
"""Extract the RUN instruction containing astral.sh/uv/install.sh from a Dockerfile."""
import re, sys

with open(sys.argv[1]) as f:
    lines = f.read().split('\n')

result = []
in_run = False

for line in lines:
    stripped = line.strip()
    if not in_run:
        if stripped.startswith('RUN'):
            in_run = True
            result = [re.sub(r'^\s*RUN\s+', '', line)]
    else:
        result.append(line)

    if in_run and not stripped.endswith('\\'):
        full = '\n'.join(result)
        if 'astral.sh/uv/install.sh' in full:
            # Found the UV install command — output it
            print(full)
            sys.exit(0)
        in_run = False
        result = []

# If we exited the loop without finding it
sys.exit(1)
PYEOF

UV_CMD_FILE="/tmp/uv_install_cmd.sh"
python3 /tmp/extract_uv_cmd.py "$TARGET" > "$UV_CMD_FILE" 2>/dev/null
EXTRACT_OK=$?

if [ $EXTRACT_OK -ne 0 ] || [ ! -s "$UV_CMD_FILE" ]; then
    echo "FAIL: Could not extract UV install RUN command containing astral.sh URL"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo "Extracted UV install command:"
cat "$UV_CMD_FILE"
echo ""

# ── F2P Behavioral (0.40): curl failure MUST propagate as non-zero exit ───────
# [pr_diff] (0.40): The core bug — curl|sh masks curl failures
# We mock curl to fail and verify the command exits non-zero.
# Buggy code: curl ... | sh → sh reads empty stdin → exit 0 (MASKED)
# Fixed code: curl ... -o file && sh file → curl fails → && stops → exit != 0
mkdir -p /tmp/mock_fail
cat > /tmp/mock_fail/curl << 'MOCKEOF'
#!/bin/bash
echo "curl: (7) Failed to connect to astral.sh port 443" >&2
exit 7
MOCKEOF
chmod +x /tmp/mock_fail/curl

# Mock uv as missing (not installed since curl failed)
cat > /tmp/mock_fail/uv << 'MOCKEOF'
#!/bin/bash
echo "uv: not installed" >&2
exit 127
MOCKEOF
chmod +x /tmp/mock_fail/uv

PATH_SAVED="$PATH"
export PATH="/tmp/mock_fail:$PATH"
bash "$UV_CMD_FILE" >/dev/null 2>&1
FAIL_EXIT=$?
export PATH="$PATH_SAVED"
rm -rf /tmp/mock_fail

if [ "$FAIL_EXIT" -ne 0 ]; then
    echo "PASS (0.40): curl failure propagates (exit $FAIL_EXIT)"
    award 0.40
else
    echo "FAIL (0.40): curl failure MASKED — command exited 0 despite curl failing"
fi

# ── F2P Behavioral (0.20): successful download + install path works ───────────
# [pr_diff] (0.20): The fix must still actually install uv when curl succeeds
# Mock curl to succeed (writes a valid script), verify the command exits 0.
mkdir -p /tmp/mock_ok
cat > /tmp/mock_ok/curl << 'MOCKEOF'
#!/bin/bash
# Parse -o flag to find output file
OUTPUT_FILE=""
for ((i=1; i<=$#; i++)); do
    arg="${!i}"
    if [ "$arg" = "-o" ] || [ "$arg" = "--output" ]; then
        next=$((i+1))
        OUTPUT_FILE="${!next}"
    fi
done

SCRIPT='#!/bin/sh
echo "Detected platform: Linux"
echo "Installing uv to ${UV_INSTALL_DIR:-/usr/local/bin}"
'

if [ -n "$OUTPUT_FILE" ]; then
    echo "$SCRIPT" > "$OUTPUT_FILE"
    chmod +x "$OUTPUT_FILE"
else
    # Piped to stdout
    echo "$SCRIPT"
fi
exit 0
MOCKEOF
chmod +x /tmp/mock_ok/curl

# Mock uv as successfully installed
cat > /tmp/mock_ok/uv << 'MOCKEOF'
#!/bin/bash
if [ "${1:-}" = "--version" ]; then
    echo "uv 0.7.8 (3c1f385e0 2025-03-20)"
fi
exit 0
MOCKEOF
chmod +x /tmp/mock_ok/uv

export PATH="/tmp/mock_ok:$PATH"
bash "$UV_CMD_FILE" >/dev/null 2>&1
OK_EXIT=$?
export PATH="$PATH_SAVED"
rm -rf /tmp/mock_ok

if [ "$OK_EXIT" -eq 0 ]; then
    echo "PASS (0.20): Install succeeds when curl works (exit 0)"
    award 0.20
else
    echo "FAIL (0.20): Install fails even when curl succeeds (exit $OK_EXIT)"
fi

# ── P2P (0.10): UV_INSTALL_DIR must still be set ─────────────────────────────
# [pr_diff] (0.10): Preserve existing UV_INSTALL_DIR=/usr/local/bin
if grep -q 'UV_INSTALL_DIR.*"/usr/local/bin"' "$TARGET" || \
   grep -q "UV_INSTALL_DIR.*'/usr/local/bin'" "$TARGET" || \
   grep -q 'UV_INSTALL_DIR.*/usr/local/bin' "$TARGET"; then
    echo "PASS (0.10): UV_INSTALL_DIR preserved"
    award 0.10
else
    echo "FAIL (0.10): UV_INSTALL_DIR not set to /usr/local/bin"
fi

# ── P2P (0.05): UV_HTTP_TIMEOUT env var must still be present ────────────────
# [pr_diff] (0.05): Preserve UV_HTTP_TIMEOUT setting
if grep -q 'UV_HTTP_TIMEOUT' "$TARGET"; then
    echo "PASS (0.05): UV_HTTP_TIMEOUT preserved"
    award 0.05
else
    echo "FAIL (0.05): UV_HTTP_TIMEOUT missing"
fi

# ── P2P (0.10): astral.sh install URL must still be present ──────────────────
# [pr_diff] (0.10): Preserve the official UV install URL
if grep -q 'astral.sh/uv/install.sh' "$TARGET"; then
    echo "PASS (0.10): astral.sh UV install URL preserved"
    award 0.10
else
    echo "FAIL (0.10): astral.sh UV install URL missing"
fi

# ── Structural (0.15): retry mechanism for transient failures ─────────────────
# [pr_diff] (0.15): curl retries for transient network failures
# Accept: --retry N, retry loop, or any retry mechanism
if grep -qiP '(--retry\s+[1-9]|for\s+\w+\s+in\s+.*[1-9].*do\s*.*curl|while\b.*retry|until\b.*curl|MAX_RETRIES|RETRY_COUNT|retry_count)' "$TARGET"; then
    echo "PASS (0.15): Retry mechanism present"
    award 0.15
else
    echo "FAIL (0.15): No retry mechanism found"
fi

# ── Compute final score ──────────────────────────────────────────────────────
SCORE=$(python3 -c "print(round($PASS, 4))")
echo ""
echo "reward: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

B_SCORE=$(python3 -c "print(round(min($PASS, 0.60), 4))")
R_SCORE=$(python3 -c "print(round(min(max($PASS - 0.60, 0.0), 0.25), 4))")
S_SCORE=$(python3 -c "print(round(max($PASS - 0.85, 0.0), 4))")
echo "{\"reward\": $SCORE, \"behavioral\": $B_SCORE, \"regression\": $R_SCORE, \"config\": 0.0, \"style_rubric\": $S_SCORE}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
