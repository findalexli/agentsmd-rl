#!/usr/bin/env bash
# Verifier for nextjs-otel-span-route-fallback
#
# Bug: When Next.js handler exports are invoked directly (without base-server),
# OpenTelemetry span names only show the HTTP method instead of the full route.
# Fix: Fall back to normalizedSrcPage/srcPage when rootSpanAttributes lacks 'next.route',
# and always set span attributes unconditionally.
#
# Tests 1-5 use Node.js eval to behaviorally test the route expression.
# These are TypeScript build templates that cannot be directly imported
# (they require webpack/turbopack compilation), but we CAN extract and
# eval the route-computation expression with mocked dependencies.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
JSON_FILE="/logs/verifier/reward.json"
mkdir -p "$(dirname "$REWARD_FILE")"

APP_PAGE="/workspace/next.js/packages/next/src/build/templates/app-page.ts"
APP_ROUTE="/workspace/next.js/packages/next/src/build/templates/app-route.ts"
PAGES_API="/workspace/next.js/packages/next/src/build/templates/pages-api.ts"
PAGES_HANDLER="/workspace/next.js/packages/next/src/server/route-modules/pages/pages-handler.ts"

###############################################################################
# GATE: Source files exist
###############################################################################
for f in "$APP_PAGE" "$APP_ROUTE" "$PAGES_API" "$PAGES_HANDLER"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAILED: $f not found"
        echo "0.0" > "$REWARD_FILE"
        echo '{"reward": 0.0}' > "$JSON_FILE"
        exit 0
    fi
done
echo "GATE PASSED: all source files exist"

SCORE=0

###############################################################################
# Helper: Behavioral route-fallback test via Node.js eval
#
# Extracts the route-computation code block from a TypeScript template,
# strips type annotations, and evaluates it with mocked rootSpanAttributes.
# Accepts any valid fallback pattern: ||, ??, ternary, if/else, etc.
###############################################################################
cat > /tmp/test_route.js << 'ENDJS'
const fs = require('fs');
const filePath = process.argv[2];
const mode = process.argv[3] || 'fallback';
const src = fs.readFileSync(filePath, 'utf8');
const lines = src.split('\n');

function stripTS(line) {
    return line.trim()
        // const x: Type = ... → const x = ...
        .replace(/(const|let|var)\s+(\w+)\s*:\s*[^=;]+\s*=/g, '$1 $2 =')
        // expr as Type → expr
        .replace(/\bas\s+[\w|&\s<>,[\]]+/g, '')
        // non-null assertion after ) or identifier: get(...)! → get(...)
        .replace(/(\)|\w)!(?=[.\s;|?&,\n])/g, '$1')
        // line comments
        .replace(/\s*\/\/.*$/, '');
}

// Phase 1: Find rootSpanAttributes.get('next.route') line
let getIdx = -1;
for (let i = 0; i < lines.length; i++) {
    if (/rootSpanAttributes\s*\.?\s*get\s*\(\s*['"]next\.route/.test(lines[i])) {
        getIdx = i;
        break;
    }
}
if (getIdx === -1) {
    console.error('FAIL: no rootSpanAttributes.get("next.route") found');
    process.exit(1);
}

// Phase 2: Capture from get-line through route assignment
let block = [];
let routeAssignIdx = -1;
for (let i = getIdx; i < Math.min(getIdx + 10, lines.length); i++) {
    block.push(stripTS(lines[i]));
    if (/\broute\s*=/.test(lines[i])) {
        routeAssignIdx = i;
        break;
    }
}

// Phase 3: Look for subsequent route reassignment (handles: if (!route) route = x)
if (routeAssignIdx >= 0) {
    for (let i = routeAssignIdx + 1; i < Math.min(routeAssignIdx + 8, lines.length); i++) {
        const trimmed = lines[i].trim();
        // Single-line: if (!route) route = ...
        if (/if\s*\(\s*!route\s*\)\s*route\s*=/.test(trimmed)) {
            block.push(stripTS(lines[i]));
            break;
        }
        // Multi-line: if (!route) { \n route = ... \n }
        if (/if\s*\(\s*!route\s*\)\s*\{?\s*$/.test(trimmed)) {
            block.push(stripTS(lines[i]));
            for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
                block.push(stripTS(lines[j]));
                if (/route\s*=/.test(lines[j])) break;
            }
            break;
        }
        // Bare reassignment: route = route || x
        if (/^\s*route\s*=/.test(trimmed) && !/const|let|var/.test(trimmed)) {
            block.push(stripTS(lines[i]));
            break;
        }
    }
}

if (block.length === 0) {
    console.error('FAIL: could not extract route computation');
    process.exit(1);
}

// Build evaluable code: convert const/var route → let route
let code = block.join('\n')
    .replace(/\b(const|var)\s+route\b/g, 'let route');

code += '\nreturn typeof route !== "undefined" ? route : undefined;';

// Mock environment
const rootSpanAttributes = new Map();
if (mode === 'present') {
    rootSpanAttributes.set('next.route', '/expected/dynamic/route');
}
const normalizedSrcPage = '/app/[param]/page';
const srcPage = '/api/test-handler';

try {
    const fn = new Function(
        'rootSpanAttributes', 'normalizedSrcPage', 'srcPage',
        code
    );
    const result = fn(rootSpanAttributes, normalizedSrcPage, srcPage);

    if (mode === 'present') {
        if (result === '/expected/dynamic/route') {
            console.log('PASS');
            process.exit(0);
        }
        console.error('FAIL: expected /expected/dynamic/route, got ' + JSON.stringify(result));
        process.exit(1);
    }

    // fallback mode: route must be a meaningful page identifier (not empty/garbage)
    if (!result || (typeof result === 'string' && result.trim() === '')) {
        console.error('FAIL: route is empty/falsy when next.route missing: ' + JSON.stringify(result));
        process.exit(1);
    }
    // Route should look like a real page path (starts with /)
    if (typeof result === 'string' && result.startsWith('/')) {
        console.log('PASS: route = ' + result);
        process.exit(0);
    }
    console.error('FAIL: route is not a valid path: ' + JSON.stringify(result));
    process.exit(1);
} catch (e) {
    console.error('FAIL: eval error: ' + e.message);
    process.exit(1);
}
ENDJS

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff] (0.16): app-page.ts route fallback — behavioral eval
#   TEST 2 [pr_diff] (0.16): app-route.ts route fallback — behavioral eval
#   TEST 3 [pr_diff] (0.14): pages-api.ts route fallback — behavioral eval
#   TEST 4 [pr_diff] (0.14): pages-handler.ts route fallback — behavioral eval
#   TEST 5 [pr_diff] (0.10): P2P — route uses next.route when present — behavioral eval
#   TEST 6 [pr_diff] (0.08): No bare route assignment without fallback (cross-check)
#   TEST 7 [pr_diff] (0.07): pages-handler.ts wrapped-by-server detection
#   TEST 8 [static]  (0.05): Anti-stub — files contain real span logic
#   TEST 9 [pr_diff] (0.05): parentSpan propagation preserved
#   TEST 10 [agent_config] (0.05): No deprecated check() — AGENTS.md:194 @ 3003e17b
###############################################################################

###############################################################################
# TESTS 1-4 [pr_diff] (0.60): Route fallback — behavioral eval
# Evaluates the actual route-computation expression from each file with
# an empty rootSpanAttributes map (simulating direct handler invocation).
# Route must resolve to a meaningful page identifier path, not undefined/"".
# Accepts any fallback mechanism: ||, ??, ternary, if/else, intermediate var.
###############################################################################

# [pr_diff] (0.16): app-page.ts route falls back to page identifier
echo "--- TEST 1: app-page.ts route fallback (behavioral) ---"
if node /tmp/test_route.js "$APP_PAGE" fallback; then
    SCORE=$(python3 -c "print($SCORE + 0.16)")
fi

# [pr_diff] (0.16): app-route.ts route falls back to page identifier
echo "--- TEST 2: app-route.ts route fallback (behavioral) ---"
if node /tmp/test_route.js "$APP_ROUTE" fallback; then
    SCORE=$(python3 -c "print($SCORE + 0.16)")
fi

# [pr_diff] (0.14): pages-api.ts route falls back to page identifier
echo "--- TEST 3: pages-api.ts route fallback (behavioral) ---"
if node /tmp/test_route.js "$PAGES_API" fallback; then
    SCORE=$(python3 -c "print($SCORE + 0.14)")
fi

# [pr_diff] (0.14): pages-handler.ts route falls back to page identifier
echo "--- TEST 4: pages-handler.ts route fallback (behavioral) ---"
if node /tmp/test_route.js "$PAGES_HANDLER" fallback; then
    SCORE=$(python3 -c "print($SCORE + 0.14)")
fi

###############################################################################
# TEST 5 [pr_diff] (0.10): Pass-to-pass — route uses next.route when present
# When rootSpanAttributes HAS 'next.route', it should be used as route value.
# This ensures the fix doesn't break the normal base-server code path.
###############################################################################
echo "--- TEST 5: P2P route uses next.route when present ---"
P2P_COUNT=0
for f in "$APP_PAGE" "$APP_ROUTE" "$PAGES_API" "$PAGES_HANDLER"; do
    if node /tmp/test_route.js "$f" present 2>/dev/null; then
        P2P_COUNT=$((P2P_COUNT + 1))
    fi
done
if [ "$P2P_COUNT" -eq 4 ]; then
    echo "  PASS: all 4 files use next.route when present"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
elif [ "$P2P_COUNT" -gt 0 ]; then
    echo "  PARTIAL: $P2P_COUNT/4 files pass P2P"
    SCORE=$(python3 -c "print(round($SCORE + 0.10 * $P2P_COUNT / 4, 4))")
else
    echo "  FAIL: no files pass P2P"
fi

###############################################################################
# TEST 6 [pr_diff] (0.08): No bare route assignment without fallback
# Cross-check on tests 1-4. The old buggy pattern is:
#   const route = rootSpanAttributes.get('next.route')
# with nothing after the get() — no ||, ??, ternary, etc.
# Any valid fix must add some fallback mechanism to this line or restructure it.
###############################################################################
echo "--- TEST 6: no bare route assignment without fallback ---"
node -e "
const fs = require('fs');
const files = process.argv.slice(1);
let bareCount = 0;
for (const f of files) {
    const src = fs.readFileSync(f, 'utf8');
    // Matches the exact old pattern: assignment ends right after get() with no fallback
    if (/(?:const|let|var)\s+route\s*(?::\s*\S+)?\s*=\s*rootSpanAttributes\s*\.?\s*get\s*\(\s*['\"]next\.route['\"]\s*\)\s*!?\s*;?\s*$/m.test(src)) {
        console.error('  FAIL: bare route assignment in ' + f.split('/').pop());
        bareCount++;
    }
}
if (bareCount === 0) {
    console.log('  PASS: no bare route assignments found');
    process.exit(0);
} else {
    process.exit(1);
}
" "$APP_PAGE" "$APP_ROUTE" "$PAGES_API" "$PAGES_HANDLER"
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.08)")
fi

###############################################################################
# TEST 7 [pr_diff] (0.07): pages-handler.ts — wrapped-by-server detection
# The fix must distinguish between direct invocation and base-server wrapping.
# The bare 'if (activeSpan)' pattern is insufficient — there must be some
# additional condition or the branching logic must be restructured.
# Accepts: isWrappedByNextServer, combined && condition, or removal of bare check.
###############################################################################
echo "--- TEST 7: pages-handler.ts wrapped-by-server detection ---"
node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
// Bare 'if (activeSpan)' without additional gating is the buggy pattern
const hasBareActiveSpan = /if\s*\(\s*activeSpan\s*\)\s*\{/.test(src);
// Some form of wrapped/server detection exists
const hasWrappedDetection = /isWrapped|wrappedByNextServer|isWrappedByNextServer|baseServerSpan/i.test(src);
// activeSpan combined with another condition via &&
const hasCombinedCondition = /if\s*\([^)]*activeSpan[^)]*&&|if\s*\([^)]*&&[^)]*activeSpan/.test(src);

if (!hasBareActiveSpan || hasWrappedDetection || hasCombinedCondition) {
    console.log('  PASS: activeSpan path properly gated or restructured');
    process.exit(0);
} else {
    console.error('  FAIL: bare if(activeSpan) without wrapped detection');
    process.exit(1);
}
" "$PAGES_HANDLER"
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.07)")
fi

###############################################################################
# TEST 8 [static] (0.05): Anti-stub — files contain real span logic
# Each file must have setAttributes and updateName calls — not just stubs.
###############################################################################
echo "--- TEST 8: anti-stub check ---"
STUB_OK=true
for f in "$APP_PAGE" "$APP_ROUTE" "$PAGES_API" "$PAGES_HANDLER"; do
    if ! grep -q "setAttributes" "$f" || ! grep -q "updateName" "$f"; then
        echo "  FAIL: $(basename "$f") appears stubbed (missing setAttributes/updateName)"
        STUB_OK=false
    fi
done
if [ "$STUB_OK" = "true" ]; then
    echo "  PASS: all files contain real span logic"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

###############################################################################
# TEST 9 [pr_diff] (0.05): parentSpan propagation preserved
# The fix must preserve the logic that propagates http.route to parent span.
###############################################################################
echo "--- TEST 9: parentSpan propagation preserved ---"
P2P_OK=true
for f in "$APP_PAGE" "$APP_ROUTE" "$PAGES_API" "$PAGES_HANDLER"; do
    if ! grep -q "parentSpan" "$f"; then
        echo "  FAIL: parentSpan missing in $(basename "$f")"
        P2P_OK=false
    fi
done
if [ "$P2P_OK" = "true" ]; then
    echo "  PASS: parentSpan propagation preserved"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

###############################################################################
# TEST 10 [agent_config] (0.05): No deprecated check() usage — AGENTS.md:194 @ 3003e17b
###############################################################################
echo "--- TEST 10: no deprecated check() in test files ---"
OTEL_TEST_DIR="/workspace/next.js/test/e2e/opentelemetry"
CONFIG_OK=true
if [ -d "$OTEL_TEST_DIR" ]; then
    if grep -rP "^\s+await check\(" "$OTEL_TEST_DIR" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "^#" | grep -v "// " | head -1 | grep -q .; then
        echo "  FAIL: deprecated check() found in test files"
        CONFIG_OK=false
    fi
fi
if [ "$CONFIG_OK" = "true" ]; then
    echo "  PASS: no deprecated check() usage"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

python3 -c "
score = $SCORE
import json
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'structural': round(max(0, min(score - 0.70, 0.25)), 4),
    'config': round(max(0, min(score - 0.95, 0.05)), 4)
}))
" > "$JSON_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
