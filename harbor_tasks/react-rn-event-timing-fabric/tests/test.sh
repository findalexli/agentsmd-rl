#!/bin/bash
set -euo pipefail

# Test script for react-rn-event-timing-fabric
# Grading: behavioral >= 0.60, structural <= 0.40
# Total weight: 1.0

REWARD_FILE="${REWARD_FILE:-/logs/verifier/reward.txt}"
REWARD_JSON="${REWARD_FILE%.txt}.json"
TARGET_FILE="/workspace/react/packages/react-native-renderer/src/ReactFiberConfigFabric.js"

mkdir -p "$(dirname "$REWARD_FILE")"

# Initialize scores
SYNTAX_PASS=0
BEHAVIORAL_SCORE=0
REGRESSION_SCORE=0
STRUCTURAL_SCORE=0
CONFIG_SCORE=0

# [gate] Syntax check - file must be valid JavaScript (Flow-typed but parseable)
# [agent_config] (0.00): File must be syntactically valid - CLAUDE.md:linting section
if node --check "<(sed 's/: [A-Za-z<>|]*//g; s/import type/import/g' "$TARGET_FILE")" 2>/dev/null || \
   node --check "$TARGET_FILE" 2>/dev/null || \
   npx flow check "$TARGET_FILE" --max-workers 1 2>/dev/null || true; then
    SYNTAX_PASS=1
fi

# Check basic syntax by trying to parse with Node
if node -e "
const fs = require('fs');
const code = fs.readFileSync('$TARGET_FILE', 'utf8');
try {
    // Remove flow type annotations for parsing
    const stripped = code.replace(/:\s*[A-Za-z<|>\[\]]+/g, '');
    new Function(stripped);
    process.exit(0);
} catch(e) {
    // Even if parsing fails, check for syntax errors
    if (e.message.includes('SyntaxError')) process.exit(1);
    process.exit(0); // Other errors are fine (imports etc)
}
" 2>/dev/null; then
    SYNTAX_PASS=1
fi

# If syntax check failed entirely, check file exists and has exports
if [ ! -f "$TARGET_FILE" ]; then
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "error": "Target file not found"}' > "$REWARD_JSON"
    exit 0
fi

# Verify the exported functions exist
HAS_TRACK=$(grep -c "export function trackSchedulerEvent" "$TARGET_FILE" || echo "0")
HAS_RESOLVE_TYPE=$(grep -c "export function resolveEventType" "$TARGET_FILE" || echo "0")
HAS_RESOLVE_TS=$(grep -c "export function resolveEventTimeStamp" "$TARGET_FILE" || echo "0")

if [ "$HAS_TRACK" -eq 0 ] || [ "$HAS_RESOLVE_TYPE" -eq 0 ] || [ "$HAS_RESOLVE_TS" -eq 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "error": "Required functions not exported"}' > "$REWARD_JSON"
    exit 0
fi

# [pr_diff] (0.20): trackSchedulerEvent stores global.event
# Check if trackSchedulerEvent sets schedulerEvent
if grep -q "schedulerEvent = global.event" "$TARGET_FILE"; then
    BEHAVIORAL_SCORE=$(echo "$BEHAVIORAL_SCORE + 0.20" | bc -l)
fi

# [pr_diff] (0.20): resolveEventType extracts event type from modern event.type
if grep -q "event.type" "$TARGET_FILE" && grep -q "getEventType" "$TARGET_FILE"; then
    BEHAVIORAL_SCORE=$(echo "$BEHAVIORAL_SCORE + 0.20" | bc -l)
fi

# [pr_diff] (0.15): resolveEventType handles legacy dispatchConfig for RN
if grep -q "dispatchConfig" "$TARGET_FILE" && grep -q "phasedRegistrationNames" "$TARGET_FILE"; then
    BEHAVIORAL_SCORE=$(echo "$BEHAVIORAL_SCORE + 0.15" | bc -l)
fi

# [pr_diff] (0.15): resolveEventTimeStamp extracts event.timeStamp
if grep -q "event.timeStamp" "$TARGET_FILE"; then
    BEHAVIORAL_SCORE=$(echo "$BEHAVIORAL_SCORE + 0.15" | bc -l)
fi

# [pr_diff] (0.10): Both functions filter out schedulerEvent to avoid self-referencing
if grep -q "event !== schedulerEvent" "$TARGET_FILE"; then
    BEHAVIORAL_SCORE=$(echo "$BEHAVIORAL_SCORE + 0.10" | bc -l)
fi

# [regression] (0.10): Functions remain callable (no breaking changes to signature)
# Check exports match expected signatures
if grep -q "export function trackSchedulerEvent(): void" "$TARGET_FILE" && \
   grep -q "export function resolveEventType(): null | string" "$TARGET_FILE" && \
   grep -q "export function resolveEventTimeStamp(): number" "$TARGET_FILE"; then
    REGRESSION_SCORE=$(echo "$REGRESSION_SCORE + 0.10" | bc -l)
fi

# [agent_config] (0.05): Code follows React conventions - avoid wildcard imports
# Check file doesn't use wildcard imports
WILDCARD_COUNT=$(grep -c "import \\*" "$TARGET_FILE" || echo "0")
if [ "$WILDCARD_COUNT" -eq 0 ]; then
    CONFIG_SCORE=$(echo "$CONFIG_SCORE + 0.05" | bc -l)
fi

# [agent_config] (0.05): Proper Flow type annotations maintained
# Check for Flow type annotations in function signatures
FLOW_ANNOTATIONS=$(grep -c ": void\|: null | string\|: number\|: Event" "$TARGET_FILE" || echo "0")
if [ "$FLOW_ANNOTATIONS" -ge 3 ]; then
    CONFIG_SCORE=$(echo "$CONFIG_SCORE + 0.05" | bc -l)
fi

# Calculate total
TOTAL=$(echo "$BEHAVIORAL_SCORE + $REGRESSION_SCORE + $STRUCTURAL_SCORE + $CONFIG_SCORE" | bc -l)

# Cap at 1.0
if (( $(echo "$TOTAL > 1.0" | bc -l) )); then
    TOTAL="1.0"
fi

# Write outputs
echo "$TOTAL" > "$REWARD_FILE"
cat > "$REWARD_JSON" << EOF
{
  "reward": $TOTAL,
  "behavioral": $BEHAVIORAL_SCORE,
  "regression": $REGRESSION_SCORE,
  "structural": $STRUCTURAL_SCORE,
  "config": $CONFIG_SCORE,
  "syntax_pass": $SYNTAX_PASS
}
EOF

echo "Scored: behavioral=$BEHAVIORAL_SCORE, regression=$REGRESSION_SCORE, config=$CONFIG_SCORE, total=$TOTAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
