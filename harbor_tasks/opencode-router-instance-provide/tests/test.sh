#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); }
add_total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd /workspace/opencode

ROUTER="packages/opencode/src/server/router.ts"
INSTANCE="packages/opencode/src/server/instance.ts"
SERVER="packages/opencode/src/server/server.ts"
OLD_MW="packages/opencode/src/control-plane/workspace-router-middleware.ts"
WORKTREE="packages/opencode/src/control-plane/adaptors/worktree.ts"

##############################################################################
# GATE: router.ts must exist
##############################################################################
# [pr_diff] (gate): New router module must exist
if [ ! -f "$ROUTER" ]; then
    echo "GATE FAILED: $ROUTER does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
##############################################################################

# [pr_diff] (0.20): router.ts can be imported and exports WorkspaceRouterMiddleware as function
# This is the strongest check — catches broken imports, type errors, and stubs.
# On buggy code: file doesn't exist → gate fails. On fixed code: exports function.
IMPORT_OK=false
bun -e "
const mod = await import('./$ROUTER');
if (typeof mod.WorkspaceRouterMiddleware !== 'function') {
  console.error('WorkspaceRouterMiddleware is not a function, got: ' + typeof mod.WorkspaceRouterMiddleware);
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && IMPORT_OK=true

if [ "$IMPORT_OK" = true ]; then
    add_score 0.20
    echo "  [PASS] router_exports_middleware_fn (0.20)"
else
    add_total 0.20
    echo "  [FAIL] router_exports_middleware_fn — WorkspaceRouterMiddleware not importable as function (0.00/0.20)"
fi

# [pr_diff] (0.15): Instance.provide call exists in router.ts CODE (not comments)
# On buggy code: router.ts doesn't exist. On fixed code: Instance.provide is in the code.
# Strip comments to prevent gaming via comment injection.
PROVIDE_IN_ROUTER=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
// Strip single-line and multi-line comments
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (!code.includes('Instance.provide')) {
  console.error('Instance.provide not found in code (excluding comments)');
  process.exit(1);
}
if (!code.includes('InstanceBootstrap')) {
  console.error('InstanceBootstrap not found in code (excluding comments)');
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && PROVIDE_IN_ROUTER=true

if [ "$PROVIDE_IN_ROUTER" = true ]; then
    add_score 0.15
    echo "  [PASS] instance_provide_in_router (0.15)"
else
    add_total 0.15
    echo "  [FAIL] instance_provide_in_router — Instance.provide with InstanceBootstrap not in router.ts code (0.00/0.15)"
fi

# [pr_diff] (0.10): Instance.provide middleware removed from instance.ts
# On buggy code: instance.ts has .use() middleware calling Instance.provide → FAILS
# On fixed code: that middleware block is gone → PASSES
PROVIDE_REMOVED=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$INSTANCE', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (code.includes('Instance.provide')) {
  console.error('Instance.provide still in instance.ts code');
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && PROVIDE_REMOVED=true

if [ "$PROVIDE_REMOVED" = true ]; then
    add_score 0.10
    echo "  [PASS] instance_provide_removed (0.10)"
else
    add_total 0.10
    echo "  [FAIL] instance_provide_removed — Instance.provide still in instance.ts (0.00/0.10)"
fi

# [pr_diff] (0.05): Old workspace-router-middleware.ts deleted
# On buggy code: file exists → FAILS. On fixed code: deleted → PASSES.
if [ ! -f "$OLD_MW" ]; then
    add_score 0.05
    echo "  [PASS] old_middleware_deleted (0.05)"
else
    add_total 0.05
    echo "  [FAIL] old_middleware_deleted — workspace-router-middleware.ts still exists (0.00/0.05)"
fi

# [pr_diff] (0.05): server.ts no longer imports from control-plane path
SERVER_IMPORT_OK=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$SERVER', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (code.includes('control-plane/workspace-router-middleware') || code.includes('control-plane/workspace-router')) {
  console.error('Still imports from control-plane');
  process.exit(1);
}
if (!code.includes('WorkspaceRouterMiddleware')) {
  console.error('WorkspaceRouterMiddleware not referenced');
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && SERVER_IMPORT_OK=true

if [ "$SERVER_IMPORT_OK" = true ]; then
    add_score 0.05
    echo "  [PASS] server_import_updated (0.05)"
else
    add_total 0.05
    echo "  [FAIL] server_import_updated — server.ts still imports from control-plane (0.00/0.05)"
fi

# [pr_diff] (0.05): router.ts is substantial — not a stub
# Anti-gaming: require at least 40 non-comment, non-blank lines of actual code
SUBSTANTIAL=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
const lines = src.split('\n').filter(l => {
  const t = l.trim();
  return t && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*') && t !== '*/';
});
if (lines.length < 40) {
  console.error('Only ' + lines.length + ' meaningful lines — likely a stub (need >= 40)');
  process.exit(1);
}
console.log('OK: ' + lines.length + ' lines');
" 2>/dev/null && SUBSTANTIAL=true

if [ "$SUBSTANTIAL" = true ]; then
    add_score 0.05
    echo "  [PASS] router_not_stub (0.05)"
else
    add_total 0.05
    echo "  [FAIL] router_not_stub — router.ts has too few lines of code (0.00/0.05)"
fi

# [pr_diff] (0.05): router.ts handles directory resolution from query/header
# The consolidated middleware must resolve directory — check for query() or header() calls in code
DIR_RESOLUTION=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Must resolve directory from request (query param or header)
const hasQueryOrHeader = code.includes('directory') && (code.includes('query') || code.includes('header'));
if (!hasQueryOrHeader) {
  console.error('No directory resolution from request found');
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && DIR_RESOLUTION=true

if [ "$DIR_RESOLUTION" = true ]; then
    add_score 0.05
    echo "  [PASS] directory_resolution (0.05)"
else
    add_total 0.05
    echo "  [FAIL] directory_resolution — router.ts does not resolve directory from request (0.00/0.05)"
fi

##############################################################################
# REGRESSION: Pass-to-pass tests (0.15 total)
##############################################################################

# [pr_diff] (0.05): InstanceRoutes still exported from instance.ts
if [ -f "$INSTANCE" ] && grep -q 'export.*InstanceRoutes\|InstanceRoutes.*export' "$INSTANCE" 2>/dev/null; then
    add_score 0.05
    echo "  [PASS] instance_routes_exported (0.05)"
else
    add_total 0.05
    echo "  [FAIL] instance_routes_exported — InstanceRoutes export missing from instance.ts (0.00/0.05)"
fi

# [pr_diff] (0.05): WorktreeAdaptor still exported from worktree.ts
if [ -f "$WORKTREE" ] && grep -q 'export.*WorktreeAdaptor\|WorktreeAdaptor.*export' "$WORKTREE" 2>/dev/null; then
    add_score 0.05
    echo "  [PASS] worktree_adaptor_exported (0.05)"
else
    add_total 0.05
    echo "  [FAIL] worktree_adaptor_exported — WorktreeAdaptor export missing (0.00/0.05)"
fi

# [pr_diff] (0.05): Workspace routing logic preserved in router.ts
# Must handle workspace param and have routing rules (forward/local decision)
ROUTING_OK=false
bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Check for workspace parameter handling
if (!code.includes('workspace')) {
  console.error('No workspace handling');
  process.exit(1);
}
// Check for routing decision (forward vs local)
if (!code.includes('forward') && !code.includes('adaptor')) {
  console.error('No forwarding/adaptor logic');
  process.exit(1);
}
console.log('OK');
" 2>/dev/null && ROUTING_OK=true

if [ "$ROUTING_OK" = true ]; then
    add_score 0.05
    echo "  [PASS] workspace_routing_preserved (0.05)"
else
    add_total 0.05
    echo "  [FAIL] workspace_routing_preserved — workspace routing logic missing from router.ts (0.00/0.05)"
fi

##############################################################################
# CONFIG-DERIVED: Agent config checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13
ANY_FOUND=false
if [ -f "$ROUTER" ]; then
    bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (/:\s*any\b|<any>|\bas\s+any\b/.test(code)) {
  process.exit(1);
}
" 2>/dev/null || ANY_FOUND=true
fi
if [ "$ANY_FOUND" = false ]; then
    add_score 0.05
    echo "  [PASS] no_any_type (0.05)"
else
    add_total 0.05
    echo "  [FAIL] no_any_type — found 'any' type usage in router.ts (0.00/0.05)"
fi

# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:70
LET_FOUND=false
if [ -f "$ROUTER" ]; then
    bun -e "
const fs = require('fs');
const src = fs.readFileSync('$ROUTER', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (/^\s*let\s/m.test(code)) {
  process.exit(1);
}
" 2>/dev/null || LET_FOUND=true
fi
if [ "$LET_FOUND" = false ]; then
    add_score 0.05
    echo "  [PASS] const_over_let (0.05)"
else
    add_total 0.05
    echo "  [FAIL] const_over_let — found 'let' in router.ts (0.00/0.05)"
fi

##############################################################################
# STYLE RUBRIC (0.10) — LLM judge
##############################################################################
add_total 0.10

if [ "${LLM_JUDGE:-0}" = "1" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    ICR=$(python3 /tests/judge.py /tests/rubric.yaml /workspace/opencode 2>/dev/null || echo "0.0")
    STYLE_SCORE=$(python3 -c "print(round(0.10 * float('$ICR'), 4))")
    SCORE=$(python3 -c "print($SCORE + $STYLE_SCORE)")
    echo "  [INFO] style_rubric: ICR=$ICR, score=$STYLE_SCORE"
else
    echo "  [SKIP] style_rubric — LLM_JUDGE not enabled"
fi

##############################################################################
# Final score
##############################################################################
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "TOTAL_POSSIBLE=$TOTAL  EARNED=$SCORE  REWARD=$REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores for reward.json
BEH=$(python3 -c "
s=$SCORE; print(round(min(s, 0.65), 4))
")
REG=$(python3 -c "
# regression is checks 8-10 (0.15 max)
print(0.0)
")
echo "{\"reward\": $REWARD, \"behavioral\": $BEH, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge hook
source /tests/judge_hook.sh 2>/dev/null || true
