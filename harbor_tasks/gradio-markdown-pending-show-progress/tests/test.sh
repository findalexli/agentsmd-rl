#!/usr/bin/env bash
set +e

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/workspace/gradio"
SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "FAIL ($1): $2"; }

SVELTE_FILE="$REPO/js/markdown/Index.svelte"

# ──────────────────────────────────────────────
# GATE (0.00): File must exist and have class:pending
# ──────────────────────────────────────────────
if [ ! -f "$SVELTE_FILE" ]; then
    echo "GATE FAIL: Index.svelte not found"
    echo "0.0" > /logs/verifier/reward.txt 2>/dev/null || echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASS: Index.svelte exists"

# ──────────────────────────────────────────────
# Helper: extract the class:pending={EXPR} expression and resolve
# reactive variables so we can eval it with mock contexts.
# Handles direct expressions and $: reactive variable indirection.
# ──────────────────────────────────────────────
cat > /tmp/extract_pending_expr.js << 'JSEOF'
const fs = require('fs');
const path = process.argv[2];
const content = fs.readFileSync(path, 'utf8');

// Find class:pending={ and extract balanced-brace expression
const marker = 'class:pending={';
const idx = content.indexOf(marker);
if (idx === -1) {
    console.error('class:pending not found');
    process.exit(2);
}
let start = idx + marker.length;
let depth = 1;
let end = start;
for (let i = start; i < content.length; i++) {
    if (content[i] === '{') depth++;
    if (content[i] === '}') {
        depth--;
        if (depth === 0) { end = i; break; }
    }
}
let expr = content.substring(start, end).replace(/\s+/g, ' ').trim();

// If the expression is a simple identifier (reactive variable pattern),
// resolve it from the script block: $: varName = EXPR or let varName = EXPR
if (/^[a-zA-Z_$]\w*$/.test(expr)) {
    const varName = expr;
    // Match reactive declaration: $: varName = ...  (may span multiple lines, ends at ;)
    const reactiveRe = new RegExp(
        `(?:\\$\\s*:|let|const)\\s+${varName}\\s*=\\s*([\\s\\S]*?)(?:;|\\n\\s*(?:\\$|let|const|export|<))`,
    );
    const defMatch = content.match(reactiveRe);
    if (defMatch) {
        expr = defMatch[1].replace(/\s+/g, ' ').trim();
    } else {
        console.error(`Could not resolve reactive var: ${varName}`);
        process.exit(2);
    }
}

// Output the normalized expression
process.stdout.write(expr);
JSEOF

PENDING_EXPR=$(node /tmp/extract_pending_expr.js "$SVELTE_FILE" 2>/tmp/extract_err.txt)
EXTRACT_RC=$?

if [ $EXTRACT_RC -ne 0 ]; then
    echo "GATE FAIL: Could not extract class:pending expression"
    cat /tmp/extract_err.txt
    echo "0.0" > /logs/verifier/reward.txt 2>/dev/null || echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi

echo "Extracted pending expression: $PENDING_EXPR"

# ──────────────────────────────────────────────
# Helper: evaluate the pending expression with a mock gradio context
# Args: status, show_progress → prints "true" or "false"
# ──────────────────────────────────────────────
cat > /tmp/eval_pending.js << 'JSEOF'
// Usage: node eval_pending.js <expr> <status> <show_progress>
const expr = process.argv[2];
const status = process.argv[3];
const show_progress = process.argv[4];

// Build mock gradio object matching the Svelte component's props
const gradio = {
    shared: {
        loading_status: {
            status: status,
            show_progress: show_progress
        }
    }
};
// Some fixes might destructure loading_status — provide top-level aliases
const loading_status = gradio.shared.loading_status;

try {
    const result = eval(expr);
    process.stdout.write(String(!!result));
} catch (e) {
    console.error('Eval error:', e.message);
    process.exit(1);
}
JSEOF

eval_pending() {
    node /tmp/eval_pending.js "$PENDING_EXPR" "$1" "$2" 2>/tmp/eval_err.txt
}

# ──────────────────────────────────────────────
# [pr_diff] (0.50): FAIL-TO-PASS — pending must be FALSE when
# status=pending AND show_progress=hidden (core bug)
# ──────────────────────────────────────────────
RESULT=$(eval_pending "pending" "hidden")
if [ "$RESULT" = "false" ]; then
    pass 0.50 "[pr_diff] Pending is FALSE when show_progress=hidden (core bug fix)"
else
    fail 0.50 "[pr_diff] Pending is FALSE when show_progress=hidden (core bug fix)"
fi

# ──────────────────────────────────────────────
# [pr_diff] (0.15): Regression — pending must still be TRUE when
# status=pending AND show_progress=full
# ──────────────────────────────────────────────
RESULT=$(eval_pending "pending" "full")
if [ "$RESULT" = "true" ]; then
    pass 0.15 "[pr_diff] Pending is TRUE when show_progress=full (no regression)"
else
    fail 0.15 "[pr_diff] Pending is TRUE when show_progress=full (no regression)"
fi

# ──────────────────────────────────────────────
# [pr_diff] (0.05): Edge case — pending must be TRUE when
# status=pending AND show_progress=minimal
# ──────────────────────────────────────────────
RESULT=$(eval_pending "pending" "minimal")
if [ "$RESULT" = "true" ]; then
    pass 0.05 "[pr_diff] Pending is TRUE when show_progress=minimal"
else
    fail 0.05 "[pr_diff] Pending is TRUE when show_progress=minimal"
fi

# ──────────────────────────────────────────────
# [pr_diff] (0.10): PASS-TO-PASS — pending must be FALSE when
# status=complete (regardless of show_progress)
# ──────────────────────────────────────────────
RESULT=$(eval_pending "complete" "full")
if [ "$RESULT" = "false" ]; then
    pass 0.10 "[pr_diff] Pending is FALSE when status=complete"
else
    fail 0.10 "[pr_diff] Pending is FALSE when status=complete"
fi

# ──────────────────────────────────────────────
# [pr_diff] (0.10): Anti-gaming — expression differs from buggy original
# The original expression is exactly: gradio.shared.loading_status?.status === "pending"
# Any correct fix must change this expression.
# ──────────────────────────────────────────────
ORIGINAL_EXPR='gradio.shared.loading_status?.status === "pending"'
NORMALIZED_EXPR=$(echo "$PENDING_EXPR" | sed 's/ //g')
NORMALIZED_ORIG=$(echo "$ORIGINAL_EXPR" | sed 's/ //g')
if [ "$NORMALIZED_EXPR" != "$NORMALIZED_ORIG" ]; then
    pass 0.10 "[pr_diff] Expression differs from buggy original"
else
    fail 0.10 "[pr_diff] Expression unchanged from buggy original"
fi

# ──────────────────────────────────────────────
# [agent_config] (0.05): Tab indentation consistent with file — AGENTS.md:45
# ──────────────────────────────────────────────
# Check that lines near class:pending use tabs (matching file convention)
PENDING_LINES=$(grep -n "class:pending\|show_progress" "$SVELTE_FILE" | head -5)
if echo "$PENDING_LINES" | grep -qP "^\d+:\t"; then
    pass 0.05 "[agent_config] Indentation uses tabs — AGENTS.md:45"
else
    fail 0.05 "[agent_config] Indentation inconsistent with file — AGENTS.md:45"
fi

# ──────────────────────────────────────────────
# Final score
# ──────────────────────────────────────────────
echo ""
echo "Total: $SCORE / $TOTAL"

mkdir -p /tests 2>/dev/null || true
mkdir -p /logs/verifier 2>/dev/null || true

REWARD=$(python3 -c "print(f'{$SCORE:.4f}')")
echo "$REWARD" > /logs/verifier/reward.txt 2>/dev/null || echo "$REWARD" > "/logs/verifier/reward.txt"

python3 -c "
import json
reward = $SCORE
data = {
    'reward': round(reward, 4),
    'behavioral': round(min(reward, 0.80), 4),
    'regression': round(min(0.10, reward), 4),
    'config': round(min(0.05, reward), 4),
    'style_rubric': 0.0
}
print(json.dumps(data))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
