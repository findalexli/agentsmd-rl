#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=100
REPO="/workspace/sglang"

SCRIPT1="$REPO/scripts/ci/amd/amd_ci_start_container.sh"
SCRIPT2="$REPO/scripts/ci/amd/amd_ci_start_container_disagg.sh"

# Helper: extract non-comment, non-empty lines from a shell script
strip_comments() {
    sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$1"
}

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Both scripts must be valid bash
for f in "$SCRIPT1" "$SCRIPT2"; do
    if ! bash -n "$f" 2>/dev/null; then
        echo "FAIL: $f has syntax errors"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "PASS: Both scripts parse correctly"

echo ""
echo "=== Fail-to-pass: Core bug fix ==="

# [pr_diff] (0.25): amd_ci_start_container.sh has a non-comment line setting safe.directory
# Accepts /sglang-checkout or wildcard '*'
if strip_comments "$SCRIPT1" | grep -qE 'safe\.directory'; then
    echo "PASS (0.25): amd_ci_start_container.sh sets safe.directory (non-comment)"
    SCORE=$((SCORE + 25))
else
    echo "FAIL (0.25): amd_ci_start_container.sh missing safe.directory command"
fi

# [pr_diff] (0.25): amd_ci_start_container_disagg.sh has a non-comment line setting safe.directory
if strip_comments "$SCRIPT2" | grep -qE 'safe\.directory'; then
    echo "PASS (0.25): amd_ci_start_container_disagg.sh sets safe.directory (non-comment)"
    SCORE=$((SCORE + 25))
else
    echo "FAIL (0.25): amd_ci_start_container_disagg.sh missing safe.directory command"
fi

# [pr_diff] (0.15): safe.directory is set INSIDE the container (via docker exec or equivalent)
# Accept: docker exec [opts] CONTAINER git config ... safe.directory
#         docker exec [opts] CONTAINER bash -c "... safe.directory ..."
#         docker exec [opts] CONTAINER sh -c "... safe.directory ..."
EXEC_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    if strip_comments "$f" | grep -qE 'docker\s+exec\s+.*safe\.directory'; then
        EXEC_OK=$((EXEC_OK + 1))
    fi
done
if [ "$EXEC_OK" -ge 2 ]; then
    echo "PASS (0.15): Both scripts use docker exec to set safe.directory inside the container"
    SCORE=$((SCORE + 15))
else
    echo "FAIL (0.15): safe.directory must be set via docker exec (inside container)"
fi

# [pr_diff] (0.10): safe.directory command appears AFTER docker run (correct ordering)
# The git config must happen after the container is created
ORDER_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    DOCKER_RUN_LINE=$(strip_comments "$f" | grep -n 'docker run' | tail -1 | cut -d: -f1)
    SAFE_DIR_LINE=$(strip_comments "$f" | grep -n 'safe\.directory' | tail -1 | cut -d: -f1)
    if [ -n "$DOCKER_RUN_LINE" ] && [ -n "$SAFE_DIR_LINE" ] && [ "$SAFE_DIR_LINE" -gt "$DOCKER_RUN_LINE" ]; then
        ORDER_OK=$((ORDER_OK + 1))
    fi
done
if [ "$ORDER_OK" -ge 2 ]; then
    echo "PASS (0.10): safe.directory set after container launch in both scripts"
    SCORE=$((SCORE + 10))
else
    echo "FAIL (0.10): safe.directory must be set after docker run"
fi

echo ""
echo "=== Pass-to-pass: Regression tests ==="

# [pr_diff] (0.10): Container launch command (docker run) is preserved in both scripts
P2P_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    if strip_comments "$f" | grep -q 'docker run' && strip_comments "$f" | grep -q '\-\-name ci_sglang'; then
        P2P_OK=$((P2P_OK + 1))
    fi
done
if [ "$P2P_OK" -ge 2 ]; then
    echo "PASS (0.10): docker run commands preserved in both scripts"
    SCORE=$((SCORE + 10))
else
    echo "FAIL (0.10): docker run commands must not be removed or altered"
fi

# [pr_diff] (0.05): Scripts remain executable and start with shebang
SHEBANG_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    if head -1 "$f" | grep -q '#!/'; then
        SHEBANG_OK=$((SHEBANG_OK + 1))
    fi
done
if [ "$SHEBANG_OK" -ge 2 ]; then
    echo "PASS (0.05): Both scripts retain shebang"
    SCORE=$((SCORE + 5))
else
    echo "FAIL (0.05): Scripts must retain shebang line"
fi

echo ""
echo "=== Structural: Config correctness ==="

# [pr_diff] (0.05): Uses --global flag (applies across repos inside container)
# Also accept --system as a valid alternative
GLOBAL_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    if strip_comments "$f" | grep -qE 'git\s+config\s+(--(global|system))'; then
        GLOBAL_OK=$((GLOBAL_OK + 1))
    fi
done
if [ "$GLOBAL_OK" -ge 2 ]; then
    echo "PASS (0.05): Both scripts use --global/--system for git config"
    SCORE=$((SCORE + 5))
else
    echo "FAIL (0.05): git config should use --global or --system flag"
fi

# [pr_diff] (0.05): The safe.directory value includes sglang-checkout path or wildcard
VALUE_OK=0
for f in "$SCRIPT1" "$SCRIPT2"; do
    if strip_comments "$f" | grep -qE "safe\.directory\s+.*(/sglang-checkout|'\\*'|\"\\\*\"|\\*)"; then
        VALUE_OK=$((VALUE_OK + 1))
    fi
done
if [ "$VALUE_OK" -ge 2 ]; then
    echo "PASS (0.05): safe.directory targets /sglang-checkout or wildcard"
    SCORE=$((SCORE + 5))
else
    echo "FAIL (0.05): safe.directory should target /sglang-checkout or '*'"
fi

echo ""
echo "=== Results ==="

REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 2))")
echo "Score: $REWARD ($SCORE / $TOTAL)"

mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
s = $SCORE / $TOTAL
beh = min(s, 0.75)
reg = min(max(s - 0.75, 0), 0.15)
struct = max(s - 0.90, 0)
json.dump({'reward': round(s, 2), 'behavioral': round(beh, 2), 'regression': round(reg, 2), 'config': 0.0, 'style_rubric': round(struct, 2)}, open('/logs/verifier/reward.json','w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
