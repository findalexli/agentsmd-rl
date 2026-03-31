#!/usr/bin/env bash
set +e

PASS=0
TOTAL=100
GATE_PASS=true

cd /workspace/next.js
TARGET="packages/next/src/build/templates/app-page.ts"

LOG_DIR="/logs/verifier"
mkdir -p "$LOG_DIR"

##############################################################################
# GATE: File exists and has balanced braces + handler export
##############################################################################
# [pr_diff] (gate): Modified TypeScript file must parse without syntax errors
# WHY STRUCTURAL: app-page.ts is a build template compiled by webpack/turbopack;
# it cannot be imported or called outside the full Next.js build pipeline.
node -e "
const fs = require('fs');
if (!fs.existsSync(process.argv[1])) { console.error('File not found'); process.exit(1); }
const src = fs.readFileSync(process.argv[1], 'utf8');
let depth = 0;
for (const ch of src) {
  if (ch === '{') depth++;
  if (ch === '}') depth--;
  if (depth < 0) { console.error('Unbalanced braces'); process.exit(1); }
}
if (depth !== 0) { console.error('Unbalanced braces: depth=' + depth); process.exit(1); }
if (!/export\s+async\s+function\s+handler/.test(src)) {
  console.error('Missing handler export');
  process.exit(1);
}
" "$TARGET" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "GATE FAIL: $TARGET has syntax/structure errors"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > "$LOG_DIR/reward.txt"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$LOG_DIR/reward.json"
    exit 0
fi
echo "GATE: syntax/structure check passed"

##############################################################################
# Helper function used by all checks below: reads file, strips comments,
# extracts the staticPathKey region. Prevents gaming via comment injection.
##############################################################################
# All node checks below use process.argv[1] for the file path.

##############################################################################
# Fail-to-pass: Behavioral checks (60 points total)
# WHY STRUCTURAL: app-page.ts is a build template. The handler() function
# requires entryBase, routeModule, and the full Next.js bundled runtime.
# It cannot be imported or called. We use comment-stripped source analysis.
##############################################################################

# [pr_diff] (0.30): The staticPathKey assignment must be guarded against server actions.
# On buggy code: no server-action reference in the condition → FAIL
# On fixed code: condition includes a server-action guard → PASS
# Accepts: isPossibleServerAction, isServerAction, isActionRequest,
#          headers containing Next-Action, actionId, etc.
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
// Strip comments to prevent gaming
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');

const idx = src.indexOf('let staticPathKey');
if (idx === -1) { console.error('staticPathKey not found'); process.exit(1); }

// Get generous window from declaration through assignment
const window = src.substring(idx, idx + 1500);

// Check for ANY server-action related token in executable code
const hasRef =
    /[Ss]erver[Aa]ction/.test(window) ||
    (/[Aa]ction/.test(window) && /[Pp]ossible/.test(window)) ||
    /Next-Action/.test(window) ||
    /next-action/.test(window) ||
    /isAction/.test(window) ||
    /actionHeader/.test(window);

if (!hasRef) {
    console.error('FAIL: no server-action guard in staticPathKey condition');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 30))
    echo "PASS [30]: staticPathKey condition includes server action guard"
} || echo "FAIL [30]: staticPathKey condition missing server action guard"

# [pr_diff] (0.20): Server actions must be EXCLUDED (negated) from staticPathKey assignment.
# Accepts: !isPossibleServerAction, !isServerAction, === false, or any negation form
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');

const idx = src.indexOf('let staticPathKey');
if (idx === -1) { process.exit(1); }
const window = src.substring(idx, idx + 1500);

const hasExclusion =
    /!\s*is[A-Za-z]*[Aa]ction/.test(window) ||
    /!\s*isPossible[A-Za-z]*[Aa]ction/.test(window) ||
    /[Aa]ction\s*===?\s*false/.test(window) ||
    /false\s*===?\s*[A-Za-z]*[Aa]ction/.test(window) ||
    /!\s*\w*[Aa]ction[A-Za-z]*/.test(window);

if (!hasExclusion) {
    console.error('FAIL: no exclusion (negation) of server actions');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 20))
    echo "PASS [20]: server actions excluded (negated) from staticPathKey condition"
} || echo "FAIL [20]: server actions not excluded from staticPathKey condition"

# [pr_diff] (0.10): Accept alternative fix patterns — early return or conditional skip.
# This gives credit for a broader class of valid fixes: if the fix prevents
# staticPathKey from being set when handling a server action, via any control flow.
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');

const idx = src.indexOf('let staticPathKey');
if (idx === -1) { process.exit(1); }

// Check 3000 chars BEFORE staticPathKey for early-return on action
const before = src.substring(Math.max(0, idx - 3000), idx);
const hasEarlyReturn =
    /if\s*\([^)]*[Aa]ction[^)]*\)\s*\{[\s\S]{0,200}return/.test(before) ||
    /if\s*\([^)]*[Aa]ction[^)]*\)\s*\{[\s\S]{0,200}continue/.test(before);

// Also accept: condition-based guard (already checked above but separate credit)
const after = src.substring(idx, idx + 1500);
const hasConditionGuard =
    /!\s*is[A-Za-z]*[Aa]ction/.test(after) ||
    /[Aa]ction\s*===?\s*false/.test(after);

if (!hasEarlyReturn && !hasConditionGuard) {
    console.error('FAIL: no action-aware control flow near staticPathKey');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 10))
    echo "PASS [10]: action-aware control flow present"
} || echo "FAIL [10]: no action-aware control flow near staticPathKey"

##############################################################################
# Pass-to-pass: Regression checks (15 points total)
##############################################################################

# [pr_diff] (0.10): Dev mode still gets staticPathKey (routeModule.isDev path preserved)
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');
const idx = src.indexOf('let staticPathKey');
if (idx === -1) { process.exit(1); }
const block = src.substring(idx, idx + 1500);
if (!/routeModule\.isDev/.test(block)) {
    console.error('FAIL: routeModule.isDev not in staticPathKey condition');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 10))
    echo "PASS [10]: routeModule.isDev still in staticPathKey condition"
} || echo "FAIL [10]: routeModule.isDev removed from staticPathKey condition"

# [pr_diff] (0.05): SSG + dynamic + fallbackRouteParams path preserved
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');
const idx = src.indexOf('let staticPathKey');
if (idx === -1) { process.exit(1); }
const block = src.substring(idx, idx + 1500);
if (!/isSSG/.test(block) || !/pageIsDynamic/.test(block) || !/fallbackRouteParams/.test(block)) {
    console.error('FAIL: SSG/dynamic/fallback conditions missing');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: isSSG && pageIsDynamic && fallbackRouteParams preserved"
} || echo "FAIL [5]: SSG/dynamic/fallback conditions missing from staticPathKey"

##############################################################################
# Anti-stub checks (10 points total)
##############################################################################

# [pr_diff] (0.05): handler function still exported and non-trivial (>100 lines)
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const m = src.match(/export\s+async\s+function\s+handler/);
if (!m) { process.exit(1); }
const afterHandler = src.substring(m.index);
if (afterHandler.split('\n').length < 100) {
    console.error('FAIL: handler function appears gutted');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: handler function exported and non-trivial"
} || echo "FAIL [5]: handler function missing or gutted"

# [pr_diff] (0.05): File size hasn't changed dramatically (anti-delete)
node -e "
const fs = require('fs');
const stat = fs.statSync(process.argv[1]);
if (stat.size < 30000) {
    console.error('FAIL: file size too small (' + stat.size + ')');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: file size reasonable (not gutted)"
} || echo "FAIL [5]: file appears gutted or truncated"

##############################################################################
# Config-derived checks (15 points total)
##############################################################################

# [agent_config] (0.05): No relative-path require() in build template — AGENTS.md:407 @ 6a8a31a
# "You cannot require internal modules with relative paths because they won't
#  be resolvable from the user's project"
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
// Strip comments to only check executable code
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');
const relativeRequires = src.match(/require\s*\(\s*['\"]\.\.?\//g) || [];
if (relativeRequires.length > 0) {
    console.error('FAIL: relative-path require() found in build template');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: No relative-path require() in build template"
} || echo "FAIL [5]: Relative-path require() found in build template"

# [agent_config] (0.05): No secret values hardcoded — AGENTS.md:306 @ 6a8a31a
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const secrets = /(?:api[_-]?key|secret[_-]?key|password|credential)\s*[:=]\s*['\"][^'\"]+['\"]/i;
if (secrets.test(src)) {
    console.error('FAIL: potential secret value in source');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: No secret values in source"
} || echo "FAIL [5]: Secret values found in source"

# [agent_config] (0.05): Keep require() behind compile-time if/else for DCE — AGENTS.md:396 @ 6a8a31a
node -e "
const fs = require('fs');
let src = fs.readFileSync(process.argv[1], 'utf8');
src = src.replace(/\/\/.*$/gm, '');
src = src.replace(/\/\*[\s\S]*?\*\//g, '');
const handlerIdx = src.indexOf('export async function handler');
if (handlerIdx === -1) { process.exit(1); }
const topLevel = src.substring(0, handlerIdx);
const topRelReqs = topLevel.match(/require\s*\(\s*['\"]\.\.?\//g) || [];
if (topRelReqs.length > 0) {
    console.error('FAIL: unconditional relative require at top level');
    process.exit(1);
}
" "$TARGET" 2>/dev/null && {
    PASS=$((PASS + 5))
    echo "PASS [5]: No unconditional relative require at top level"
} || echo "FAIL [5]: Unconditional relative require found at top level"

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS / $TOTAL" | bc)
echo ""
echo "Total: $PASS / $TOTAL = $REWARD"

echo "$REWARD" > "$LOG_DIR/reward.txt"

# Build reward.json with breakdown
node -e "
const pass = parseInt(process.argv[1]);
const total = parseInt(process.argv[2]);
const reward = pass / total;
const obj = {
    reward: parseFloat(reward.toFixed(2)),
    behavioral: parseFloat((Math.min(pass, 60) / total).toFixed(2)),
    regression: parseFloat((Math.max(0, Math.min(pass, 75) - 60) / total).toFixed(2)),
    config: parseFloat((Math.max(0, pass - 75) / total).toFixed(2)),
    style_rubric: 0.0
};
process.stdout.write(JSON.stringify(obj));
" "$PASS" "$TOTAL" > "$LOG_DIR/reward.json" 2>/dev/null || echo "{\"reward\": $REWARD}" > "$LOG_DIR/reward.json"

# Also write to workspace for backward compatibility
cp "$LOG_DIR/reward.txt" /logs/verifier/reward.txt 2>/dev/null || true
cp "$LOG_DIR/reward.json" /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
