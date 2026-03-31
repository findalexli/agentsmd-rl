#!/usr/bin/env bash
set +e

SCORE=0.0

add() { SCORE=$(python3 -c "print(round($SCORE + $1, 2))"); }

cd /workspace/opencode

##############################################################################
# GATE: Modified files must exist and be non-empty
##############################################################################
# [pr_diff] (gate): Core files must exist
for f in packages/app/src/app.tsx packages/opencode/src/effect/cross-spawn-spawner.ts package.json; do
    if [ ! -s "$f" ]; then
        echo "GATE FAILED: $f missing or empty"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done

##############################################################################
# BEHAVIORAL F2P: Effect runtime API test (0.30)
##############################################################################
# [pr_diff] (0.30): Effect.timeoutOrElse with orElse callback fires on timeout
# On buggy code (beta.37 installed, orElse not recognized): FAILS
# On correct fix (beta.42 installed, orElse works): PASSES
cat > /workspace/opencode/__test_effect_api__.ts << 'EFFECT_TEST'
import { Effect } from "effect"

// Create an effect that will definitely time out (sleeps 5s, timeout at 200ms)
const slow = Effect.sleep("5 seconds").pipe(Effect.as(42))

const program = Effect.timeoutOrElse(slow, {
  duration: "200 millis",
  orElse: () => Effect.succeed(-1),
})

const result = await Effect.runPromise(program)

if (result === -1) {
  console.log("PASS: orElse callback invoked on timeout")
  process.exit(0)
} else {
  console.error("FAIL: expected -1 from orElse, got " + result)
  process.exit(1)
}
EFFECT_TEST

timeout 30 bun run /workspace/opencode/__test_effect_api__.ts 2>&1
if [ $? -eq 0 ]; then
    add 0.30
    echo "  [PASS] effect_api_behavioral (0.30)"
else
    echo "  [FAIL] effect_api_behavioral (0.00/0.30)"
fi
rm -f /workspace/opencode/__test_effect_api__.ts

##############################################################################
# BEHAVIORAL F2P: Package version checks (0.25)
##############################################################################

# [pr_diff] (0.15): effect@4.0.0-beta.42 in package.json catalog
node -e "
const pkg = JSON.parse(require('fs').readFileSync('package.json', 'utf8'));
const cat = pkg.workspaces?.catalog || pkg.catalog || {};
const ver = cat.effect || '';
if (ver === '4.0.0-beta.42') process.exit(0);
console.error('effect version: ' + ver);
process.exit(1);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.15
    echo "  [PASS] effect_version (0.15)"
else
    echo "  [FAIL] effect_version (0.00/0.15)"
fi

# [pr_diff] (0.10): @effect/platform-node@4.0.0-beta.42 in package.json catalog
node -e "
const pkg = JSON.parse(require('fs').readFileSync('package.json', 'utf8'));
const cat = pkg.workspaces?.catalog || pkg.catalog || {};
const ver = cat['@effect/platform-node'] || '';
if (ver === '4.0.0-beta.42') process.exit(0);
console.error('@effect/platform-node version: ' + ver);
process.exit(1);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.10
    echo "  [PASS] platform_node_version (0.10)"
else
    echo "  [FAIL] platform_node_version (0.00/0.10)"
fi

##############################################################################
# BEHAVIORAL F2P: Source code API fix — comment-stripped (0.10)
##############################################################################
# [pr_diff] (0.10): timeoutOrElse calls use orElse, not onTimeout (multiline-aware)
# Strips comments before checking to prevent gaming via comment injection
node -e "
const fs = require('fs');
const files = [
  'packages/app/src/app.tsx',
  'packages/opencode/src/effect/cross-spawn-spawner.ts'
];
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8');
  // Strip single-line and multi-line comments
  const stripped = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  // Split on timeoutOrElse to find each call site
  const parts = stripped.split('timeoutOrElse');
  if (parts.length < 2) {
    console.error(f + ': no timeoutOrElse call found in non-comment code');
    process.exit(1);
  }
  for (let i = 1; i < parts.length; i++) {
    // Examine next 400 chars after each timeoutOrElse occurrence
    const ctx = parts[i].substring(0, 400);
    if (/\bonTimeout\b/.test(ctx)) {
      console.error(f + ': onTimeout still present in timeoutOrElse call');
      process.exit(1);
    }
    if (!/\borElse\b/.test(ctx)) {
      console.error(f + ': orElse missing from timeoutOrElse call');
      process.exit(1);
    }
  }
}
console.log('OK: all timeoutOrElse calls use orElse');
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.10
    echo "  [PASS] source_api_fix (0.10)"
else
    echo "  [FAIL] source_api_fix (0.00/0.10)"
fi

##############################################################################
# PASS-TO-PASS: Regression checks (0.15)
##############################################################################

# [pr_diff] (0.05): timeoutOrElse calls still present in both files (not deleted)
node -e "
const fs = require('fs');
const app = fs.readFileSync('packages/app/src/app.tsx', 'utf8');
const spawner = fs.readFileSync('packages/opencode/src/effect/cross-spawn-spawner.ts', 'utf8');
// Strip comments to prevent gaming
const a = app.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
const s = spawner.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if ((a.match(/timeoutOrElse/g) || []).length < 1) {
  console.error('app.tsx: timeoutOrElse call removed'); process.exit(1);
}
if ((s.match(/timeoutOrElse/g) || []).length < 1) {
  console.error('spawner: timeoutOrElse call removed'); process.exit(1);
}
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.05
    echo "  [PASS] timeout_calls_preserved (0.05)"
else
    echo "  [FAIL] timeout_calls_preserved (0.00/0.05)"
fi

# [pr_diff] (0.05): SIGKILL escalation preserved in cross-spawn-spawner.ts
node -e "
const src = require('fs').readFileSync('packages/opencode/src/effect/cross-spawn-spawner.ts', 'utf8');
const stripped = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (/SIGKILL/.test(stripped)) process.exit(0);
console.error('SIGKILL not found in non-comment code');
process.exit(1);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.05
    echo "  [PASS] sigkill_preserved (0.05)"
else
    echo "  [FAIL] sigkill_preserved (0.00/0.05)"
fi

# [pr_diff] (0.05): Duration parameters preserved in both files
node -e "
const fs = require('fs');
const app = fs.readFileSync('packages/app/src/app.tsx', 'utf8');
const spawner = fs.readFileSync('packages/opencode/src/effect/cross-spawn-spawner.ts', 'utf8');
const a = app.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
const s = spawner.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (!/duration/.test(a)) { console.error('app.tsx: duration param missing'); process.exit(1); }
if (!/forceKillAfter/.test(s)) { console.error('spawner: forceKillAfter missing'); process.exit(1); }
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.05
    echo "  [PASS] duration_preserved (0.05)"
else
    echo "  [FAIL] duration_preserved (0.00/0.05)"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.05)
##############################################################################
# [pr_diff] (0.05): Files maintain reasonable size (not gutted)
node -e "
const fs = require('fs');
const app = fs.readFileSync('packages/app/src/app.tsx', 'utf8');
const spawner = fs.readFileSync('packages/opencode/src/effect/cross-spawn-spawner.ts', 'utf8');
// Original: app.tsx ~260 lines, spawner ~360 lines
if (app.split('\n').length < 100) { console.error('app.tsx too short: ' + app.split('\n').length + ' lines'); process.exit(1); }
if (spawner.split('\n').length < 200) { console.error('spawner too short: ' + spawner.split('\n').length + ' lines'); process.exit(1); }
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.05
    echo "  [PASS] anti_stub (0.05)"
else
    echo "  [FAIL] anti_stub (0.00/0.05)"
fi

##############################################################################
# CONFIG: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13
node -e "
const fs = require('fs');
const files = ['packages/app/src/app.tsx', 'packages/opencode/src/effect/cross-spawn-spawner.ts'];
for (const f of files) {
  const lines = fs.readFileSync(f, 'utf8').split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].replace(/\/\/.*$/, '').replace(/['\"].*?['\"]/g, '');
    if (/:\s*any\b/.test(line) || /<any>/.test(line)) {
      console.error(f + ':' + (i+1) + ' uses any type');
      process.exit(1);
    }
  }
}
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    add 0.05
    echo "  [PASS] no_any_type (0.05)"
else
    echo "  [FAIL] no_any_type (0.00/0.05)"
fi

# [agent_config] (0.05): "Prefer const over let" + "Avoid try/catch" — AGENTS.md:12,70
DIFF=$(git diff HEAD -- packages/app/src/app.tsx packages/opencode/src/effect/cross-spawn-spawner.ts package.json 2>/dev/null || true)
FAIL_CONFIG=0
if echo "$DIFF" | grep -q '^\+.*\blet\b'; then FAIL_CONFIG=1; fi
if echo "$DIFF" | grep -q '^\+.*\btry\s*{'; then FAIL_CONFIG=1; fi
if [ $FAIL_CONFIG -eq 0 ]; then
    add 0.05
    echo "  [PASS] const_no_trycatch (0.05)"
else
    echo "  [FAIL] const_no_trycatch (0.00/0.05)"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo "Total: $SCORE / 1.00"
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
s = $SCORE
print(json.dumps({
    'reward': round(s, 2),
    'behavioral': round(min(s, 0.80), 2),
    'regression': round(min(max(s - 0.80, 0), 0.05), 2),
    'config': round(min(max(s - 0.85, 0), 0.10), 2),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

source /tests/judge_hook.sh 2>/dev/null || true
