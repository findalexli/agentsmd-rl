#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
AUTH_FILE="packages/opencode/src/provider/auth.ts"
PLUGIN_FILE="packages/plugin/src/index.ts"

award() { SCORE=$(python3 -c "print($SCORE + $1)"); }
add()   { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

mkdir -p /logs/verifier

# ──────────────────────────────────────────────────────────────
# GATE: files exist and are non-empty
# ──────────────────────────────────────────────────────────────
if [ ! -s "$AUTH_FILE" ] || [ ! -s "$PLUGIN_FILE" ]; then
  echo "GATE FAILED: required files missing or empty"
  echo "0.0" > /logs/verifier/reward.txt
  cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
  echo '{"reward":0}' > /logs/verifier/reward.json
  cp /logs/verifier/reward.json reward.json 2>/dev/null || true
  exit 0
fi

# ──────────────────────────────────────────────────────────────
# Helper: extract an if-block body from auth.ts and evaluate it
# with mocked auth.set, capturing what gets stored.
# This is the core behavioral test: we actually EXECUTE the code
# in a generator context, not just inspect the source text.
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.40): Core bug — extra OAuth fields (enterpriseUrl, arbitrary fields) preserved
add 0.40
F2P_CORE=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$AUTH_FILE', 'utf8');

// Locate the 'refresh in result' if-block
const marker = '\"refresh\" in result';
const mIdx = src.indexOf(marker);
if (mIdx === -1) { console.log('FAIL:no_refresh_branch'); process.exit(0); }

// Extract the if-block body by matching braces
const after = src.substring(mIdx);
const bodyStart = after.indexOf('{');
let depth = 0, bodyEnd = -1;
for (let i = bodyStart; i < after.length; i++) {
  if (after[i] === '{') depth++;
  if (after[i] === '}') { depth--; if (depth === 0) { bodyEnd = i; break; } }
}
if (bodyEnd === -1) { console.log('FAIL:no_block_end'); process.exit(0); }

const body = after.substring(bodyStart + 1, bodyEnd).trim();

// Build a generator-based test harness that mocks auth.set
// and captures the object passed to it. yield* works because
// auth.set is a generator function.
let captured = null;
const auth = { set: function*(id, obj) { captured = obj; } };
const input = { providerID: 'test-provider' };
const result = {
  type: 'success', provider: 'github',
  refresh: 'ref_tok', access: 'acc_tok', expires: 9999,
  accountId: 'acct1',
  enterpriseUrl: 'https://enterprise.example.com',
  customField: 42  // arbitrary extra field not in the PR
};

try {
  const fn = new Function('auth', 'input', 'result',
    'const gen = (function*() {' + body + '})();' +
    'let step; do { step = gen.next(); } while (!step.done);'
  );
  fn(auth, input, result);

  if (!captured) { console.log('FAIL:auth_set_not_called'); process.exit(0); }

  const checks = {
    enterpriseUrl: captured.enterpriseUrl === 'https://enterprise.example.com',
    customField: captured.customField === 42,
    type_oauth: captured.type === 'oauth',
    access: captured.access === 'acc_tok',
    refresh: captured.refresh === 'ref_tok',
    expires: captured.expires === 9999,
    accountId: captured.accountId === 'acct1',
  };

  const failed = Object.entries(checks).filter(([,v]) => !v).map(([k]) => k);
  if (failed.length === 0) {
    console.log('PASS');
  } else {
    console.log('FAIL:' + failed.join(','));
  }
} catch(e) {
  console.log('FAIL:eval_error:' + e.message.substring(0, 100));
}
" 2>&1)

if [ "$F2P_CORE" = "PASS" ]; then
  echo "PASS: Extra fields (enterpriseUrl, customField, accountId) preserved through auth.set"
  award 0.40
else
  echo "FAIL: Extra fields not preserved: $F2P_CORE"
fi

# ──────────────────────────────────────────────────────────────
# [pr_diff] (0.15): type and provider excluded from stored auth entry
# The stored object must have type:'oauth', NOT type:'success'
# and must NOT contain provider:'github'
# ──────────────────────────────────────────────────────────────
add 0.15
F2P_EXCLUDE=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$AUTH_FILE', 'utf8');

const marker = '\"refresh\" in result';
const mIdx = src.indexOf(marker);
if (mIdx === -1) { console.log('FAIL:no_refresh_branch'); process.exit(0); }

const after = src.substring(mIdx);
const bodyStart = after.indexOf('{');
let depth = 0, bodyEnd = -1;
for (let i = bodyStart; i < after.length; i++) {
  if (after[i] === '{') depth++;
  if (after[i] === '}') { depth--; if (depth === 0) { bodyEnd = i; break; } }
}
const body = after.substring(bodyStart + 1, bodyEnd).trim();

let captured = null;
const auth = { set: function*(id, obj) { captured = obj; } };
const input = { providerID: 'test' };
const result = {
  type: 'success', provider: 'github',
  refresh: 'r', access: 'a', expires: 1
};

try {
  const fn = new Function('auth', 'input', 'result',
    'const gen = (function*() {' + body + '})();' +
    'let step; do { step = gen.next(); } while (!step.done);'
  );
  fn(auth, input, result);

  if (!captured) { console.log('FAIL:no_capture'); process.exit(0); }
  if (captured.type !== 'oauth') { console.log('FAIL:type_is_' + captured.type); process.exit(0); }
  if (captured.provider === 'github') { console.log('FAIL:provider_leaked'); process.exit(0); }
  console.log('PASS');
} catch(e) {
  console.log('FAIL:' + e.message.substring(0, 100));
}
" 2>&1)

if [ "$F2P_EXCLUDE" = "PASS" ]; then
  echo "PASS: type='oauth' (not 'success'), provider excluded from stored auth"
  award 0.15
else
  echo "FAIL: type/provider not properly handled: $F2P_EXCLUDE"
fi

# ──────────────────────────────────────────────────────────────
# [pr_diff] (0.10): enterpriseUrl declared in AuthOuathResult type
# Must appear as optional string field in both method branches
# ──────────────────────────────────────────────────────────────
add 0.10
ENTERPRISE_TYPE=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$PLUGIN_FILE', 'utf8');

// Find the AuthOuathResult type definition area
const typeStart = src.indexOf('AuthOuathResult');
if (typeStart === -1) { console.log('FAIL:no_type'); process.exit(0); }

const typeArea = src.substring(typeStart, typeStart + 2000);
const matches = typeArea.match(/enterpriseUrl\s*\??\s*:\s*string/g);

if (matches && matches.length >= 2) {
  console.log('PASS');
} else if (matches && matches.length >= 1) {
  console.log('PARTIAL');
} else {
  console.log('FAIL');
}
" 2>&1)

if [ "$ENTERPRISE_TYPE" = "PASS" ]; then
  echo "PASS: enterpriseUrl declared in both AuthOuathResult branches"
  award 0.10
elif [ "$ENTERPRISE_TYPE" = "PARTIAL" ]; then
  echo "PARTIAL: enterpriseUrl in only one AuthOuathResult branch"
  award 0.05
else
  echo "FAIL: enterpriseUrl not in AuthOuathResult type: $ENTERPRISE_TYPE"
fi

# ──────────────────────────────────────────────────────────────
# PASS-TO-PASS (0.20 total)
# ──────────────────────────────────────────────────────────────

# [pr_diff] (0.10): accountId still forwarded when present
add 0.10
P2P_ACCOUNT=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$AUTH_FILE', 'utf8');

const marker = '\"refresh\" in result';
const mIdx = src.indexOf(marker);
if (mIdx === -1) { console.log('FAIL'); process.exit(0); }

const after = src.substring(mIdx);
const bodyStart = after.indexOf('{');
let depth = 0, bodyEnd = -1;
for (let i = bodyStart; i < after.length; i++) {
  if (after[i] === '{') depth++;
  if (after[i] === '}') { depth--; if (depth === 0) { bodyEnd = i; break; } }
}
const body = after.substring(bodyStart + 1, bodyEnd).trim();

let captured = null;
const auth = { set: function*(id, obj) { captured = obj; } };
const input = { providerID: 'test' };
const result = {
  type: 'success', provider: 'github',
  refresh: 'r', access: 'a', expires: 1,
  accountId: 'acct123'
};

try {
  const fn = new Function('auth', 'input', 'result',
    'const gen = (function*() {' + body + '})();' +
    'let step; do { step = gen.next(); } while (!step.done);'
  );
  fn(auth, input, result);
  console.log(captured && captured.accountId === 'acct123' ? 'PASS' : 'FAIL');
} catch(e) { console.log('FAIL:' + e.message.substring(0, 60)); }
" 2>&1)

if [ "$P2P_ACCOUNT" = "PASS" ]; then
  echo "PASS: accountId still forwarded"
  award 0.10
else
  echo "FAIL: accountId broken: $P2P_ACCOUNT"
fi

# [pr_diff] (0.10): key-based auth branch still functional
add 0.10
P2P_KEY=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$AUTH_FILE', 'utf8');

const marker = '\"key\" in result';
const mIdx = src.indexOf(marker);
if (mIdx === -1) { console.log('FAIL:no_key_branch'); process.exit(0); }

const after = src.substring(mIdx);
const bodyStart = after.indexOf('{');
let depth = 0, bodyEnd = -1;
for (let i = bodyStart; i < after.length; i++) {
  if (after[i] === '{') depth++;
  if (after[i] === '}') { depth--; if (depth === 0) { bodyEnd = i; break; } }
}
const body = after.substring(bodyStart + 1, bodyEnd).trim();

let captured = null;
const auth = { set: function*(id, obj) { captured = obj; } };
const input = { providerID: 'test' };
const result = { type: 'success', provider: 'github', key: 'sk-test-123' };

try {
  const fn = new Function('auth', 'input', 'result',
    'const gen = (function*() {' + body + '})();' +
    'let step; do { step = gen.next(); } while (!step.done);'
  );
  fn(auth, input, result);
  if (captured && captured.key === 'sk-test-123' && captured.type === 'api') {
    console.log('PASS');
  } else {
    console.log('FAIL:' + JSON.stringify(captured));
  }
} catch(e) { console.log('FAIL:' + e.message.substring(0, 60)); }
" 2>&1)

if [ "$P2P_KEY" = "PASS" ]; then
  echo "PASS: API key auth branch intact"
  award 0.10
else
  echo "FAIL: API key auth broken: $P2P_KEY"
fi

# ──────────────────────────────────────────────────────────────
# STRUCTURAL: Anti-stub (0.05)
# ──────────────────────────────────────────────────────────────

# [static] (0.05): No TODO/FIXME/stub markers in modified files
add 0.05
if ! grep -qiE '(TODO|FIXME|HACK|stub|not.?implemented)' "$AUTH_FILE" 2>/dev/null; then
  echo "PASS: No stub markers in auth.ts"
  award 0.05
else
  echo "FAIL: Stub markers found in auth.ts"
fi

# ──────────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10)
# ──────────────────────────────────────────────────────────────

# [agent_config] (0.05): "Avoid the any type" — AGENTS.md:20 @ 2d502d6
# Compare against baseline — only fail if NEW 'any' types were introduced
add 0.05
ANY_NEW=$(node -e "
const fs = require('fs');
const { execSync } = require('child_process');
const current = (fs.readFileSync('$AUTH_FILE','utf8').match(/\\bany\\b/g) || []).length;
let original = 0;
try {
  const orig = execSync('git show HEAD:$AUTH_FILE 2>/dev/null', {encoding:'utf8'});
  original = (orig.match(/\\bany\\b/g) || []).length;
} catch(e) {}
console.log(current <= original ? 'PASS' : 'FAIL');
" 2>&1)
if [ "$ANY_NEW" = "PASS" ]; then
  echo "PASS: No new 'any' types introduced"
  award 0.05
else
  echo "FAIL: New 'any' type usage in auth.ts"
fi

# [agent_config] (0.05): "Keep things in one function" — AGENTS.md:16 @ 2d502d6
# Verify fix didn't extract callback logic to unnecessary new functions
add 0.05
EXTRACT_CHECK=$(node -e "
const fs = require('fs');
const { execSync } = require('child_process');
let origFuncs = 0, newFuncs = 0;
try {
  const orig = execSync('git show HEAD:$AUTH_FILE 2>/dev/null', {encoding:'utf8'});
  origFuncs = (orig.match(/function\s+\w+/g) || []).length;
} catch(e) {}
const current = fs.readFileSync('$AUTH_FILE','utf8');
newFuncs = (current.match(/function\s+\w+/g) || []).length;
// Allow at most 1 new named function (generous)
console.log(newFuncs <= origFuncs + 1 ? 'PASS' : 'FAIL');
" 2>&1)
if [ "$EXTRACT_CHECK" = "PASS" ]; then
  echo "PASS: No gratuitous function extraction"
  award 0.05
else
  echo "FAIL: Unnecessary new functions added"
fi

# ──────────────────────────────────────────────────────────────
# TOTAL
# ──────────────────────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0)")
echo ""
echo "Score: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

python3 -c "
import json
score, total = $SCORE, $TOTAL
r = round(score / total, 4) if total > 0 else 0
print(json.dumps({
    'reward': r,
    'behavioral': round(min(score, 0.75) / total, 4) if total > 0 else 0,
    'regression': round(min(max(score - 0.75, 0), 0.20) / total, 4) if total > 0 else 0,
    'config': round(min(max(score - 0.95, 0), 0.10) / total, 4) if total > 0 else 0,
}))
" > /logs/verifier/reward.json
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
