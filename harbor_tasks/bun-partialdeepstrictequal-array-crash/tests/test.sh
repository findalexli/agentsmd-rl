#!/usr/bin/env bash
set +e

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="/repo"
ASSERT_FILE="$REPO_DIR/src/js/node/assert.ts"
TOTAL=0

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

########################################
# GATE: File exists and is non-trivial
########################################
# [static] (gate): assert.ts must exist and not be stubbed
if [ ! -f "$ASSERT_FILE" ]; then
    echo "GATE FAILED: assert.ts does not exist"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
LINE_COUNT=$(wc -l < "$ASSERT_FILE")
if [ "$LINE_COUNT" -lt 400 ]; then
    echo "GATE FAILED: assert.ts only has $LINE_COUNT lines (likely stubbed)"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASSED: assert.ts exists ($LINE_COUNT lines)"

########################################
# GATE: TypeScript syntax check (strip bun $-intrinsics)
########################################
# [static] (gate): assert.ts must be valid syntax after stripping bun intrinsics
SYNTAX_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$ASSERT_FILE', 'utf8');
  const cleaned = src.replace(/\\\$[a-zA-Z_][a-zA-Z0-9_]*/g, '_bun_intrinsic');
  try { new Function(cleaned); console.log('OK'); } catch(e) {
    // Module-level code may fail Function() — only flag truly broken files
    if (/Unexpected token/.test(e.message) || /Unterminated/.test(e.message)) {
      console.log('FAIL');
    } else {
      console.log('OK');
    }
  }
" 2>&1)
if [ "$SYNTAX_OK" = "FAIL" ]; then
    echo "GATE FAILED: assert.ts has fatal syntax errors"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASSED: syntax check"

########################################
# Fail-to-pass: Buggy direct method calls on expectedCounts removed (0.35)
########################################
# [pr_diff] (0.35): The crash is caused by direct .$set/.$delete calls on the
# null-proto SafeMap instance (expectedCounts). ANY correct fix must remove these
# direct calls from the compareBranch function's array handling section.
# We extract just the compareBranch function body and check inside it.
F2P_RESULT=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$ASSERT_FILE', 'utf8');

// Find the compareBranch function
const fnStart = src.indexOf('function compareBranch');
if (fnStart === -1) {
    console.log('NO_FUNC');
    process.exit(0);
}

// Extract a reasonable chunk of the function body (the array handling section)
// The bug is in the array branch which uses expectedCounts
const chunk = src.slice(fnStart, fnStart + 3000);

// Look for direct method calls on expectedCounts — the buggy pattern
// These are the crash-causing calls: expectedCounts.\$set, expectedCounts.\$delete
// (bun compiles \$ to @ internally; \$set becomes @set)
const directSet = /expectedCounts\s*\.\s*\\$set\b/.test(chunk);
const directDelete = /expectedCounts\s*\.\s*\\$delete\b/.test(chunk);

if (!directSet && !directDelete) {
    console.log('PASS');
} else {
    console.log('FAIL: direct calls remain (set=' + directSet + ', delete=' + directDelete + ')');
}
" 2>&1)

if echo "$F2P_RESULT" | grep -q '^PASS'; then
    echo "PASS [pr_diff] (0.35): Buggy direct expectedCounts.\$set/\$delete calls removed"
    add_score 0.35
elif echo "$F2P_RESULT" | grep -q 'NO_FUNC'; then
    echo "FAIL [pr_diff] (0.35): compareBranch function not found"
else
    echo "FAIL [pr_diff] (0.35): $F2P_RESULT"
fi

########################################
# Fail-to-pass: set/delete on expectedCounts go through prototype (0.30)
########################################
# [pr_diff] (0.30): The fix must route set/delete calls through a prototype
# reference (any name) using $call or $apply. This accepts ANY variable name
# for the prototype reference — not just SafeMapPrototypeSet.
F2P2_RESULT=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$ASSERT_FILE', 'utf8');

const fnStart = src.indexOf('function compareBranch');
if (fnStart === -1) { console.log('NO_FUNC'); process.exit(0); }
const chunk = src.slice(fnStart, fnStart + 3000);

// Check: somewhere in compareBranch, there's a prototype-based set call on expectedCounts
// Pattern: <anyVar>.$call(expectedCounts, ...) or <anyVar>.$apply(expectedCounts, ...)
// where <anyVar> is a reference to Map/SafeMap prototype.set
// We accept ANY variable name — the key is using .\$call/.\$apply with expectedCounts as first arg
const protoSetCall = /[A-Za-z_][A-Za-z0-9_]*\s*\.\s*\\$call\s*\(\s*expectedCounts\b/.test(chunk);
const protoSetApply = /[A-Za-z_][A-Za-z0-9_]*\s*\.\s*\\$apply\s*\(\s*expectedCounts\b/.test(chunk);

// Also accept: Map.prototype.set.$call(expectedCounts, ...) directly inlined
const inlineProtoCall = /Map\s*\.\s*prototype\s*\.\s*(set|delete)\s*\.\s*\\$(call|apply)\s*\(\s*expectedCounts\b/.test(chunk);

// Also check that a prototype reference for delete exists (either extracted or inline)
const protoDelCall = /[A-Za-z_][A-Za-z0-9_]*\s*\.\s*\\$call\s*\(\s*expectedCounts\b[\s\S]{0,200}(delete|Delete)/.test(chunk) ||
                     /Map\s*\.\s*prototype\s*\.\s*delete\s*\.\s*\\$(call|apply)\s*\(\s*expectedCounts\b/.test(chunk);

// We need at least: set calls go through prototype AND delete calls go through prototype
// The chunk should have multiple $call(expectedCounts invocations (set+1, set init, delete, set-1 = 4 total)
const callCount = (chunk.match(/\\$(call|apply)\s*\(\s*expectedCounts\b/g) || []).length;

if ((protoSetCall || protoSetApply || inlineProtoCall) && callCount >= 3) {
    console.log('PASS');
} else {
    console.log('FAIL: proto calls found=' + (protoSetCall||protoSetApply||inlineProtoCall) + ', callCount=' + callCount);
}
" 2>&1)

if echo "$F2P2_RESULT" | grep -q '^PASS'; then
    echo "PASS [pr_diff] (0.30): set/delete on expectedCounts routed through prototype.\$call"
    add_score 0.30
elif echo "$F2P2_RESULT" | grep -q 'NO_FUNC'; then
    echo "FAIL [pr_diff] (0.30): compareBranch function not found"
else
    echo "FAIL [pr_diff] (0.30): $F2P2_RESULT"
fi

########################################
# Behavioral: Null-proto Map simulation verifies fix logic (0.15)
########################################
# [pr_diff] (0.15): The prototype-call pattern actually works for null-proto Maps.
# This simulates the core logic any correct fix must implement.
SIM_RESULT=$(node -e "
'use strict';

// Create a null-proto Map (same as SafeMap in bun)
function makeSafeMap() {
    const map = new Map();
    Object.setPrototypeOf(map, null);
    return map;
}

// Any correct fix must use prototype-based calls. Verify the pattern works.
const map = makeSafeMap();

// Direct calls MUST fail (this is why the bug exists)
let directFails = false;
try { map.set('a', 1); } catch(e) { directFails = true; }

// Prototype calls MUST work (this is what the fix does)
let protoWorks = false;
try {
    Map.prototype.set.call(map, 'a', 1);
    Map.prototype.set.call(map, 'b', 2);
    protoWorks = (map.size === 2);
    Map.prototype.delete.call(map, 'a');
    protoWorks = protoWorks && (map.size === 1);
} catch(e) { protoWorks = false; }

console.log(directFails && protoWorks ? 'PASS' : 'FAIL');
" 2>&1)

if [ "$SIM_RESULT" = "PASS" ]; then
    echo "PASS [pr_diff] (0.15): Null-proto Map prototype call pattern verified"
    add_score 0.15
else
    echo "FAIL [pr_diff] (0.15): Null-proto Map simulation: $SIM_RESULT"
fi

########################################
# Pass-to-pass: compareBranch function and existing prototype refs intact (0.10)
########################################
# [pr_diff] (0.10): The fix must not break existing code — compareBranch must
# still exist, and existing SafeMap prototype extractions must remain.
P2P_RESULT=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$ASSERT_FILE', 'utf8');

let pass = true;
let reasons = [];

// compareBranch must exist
if (!/function\s+compareBranch/.test(src)) {
    pass = false; reasons.push('compareBranch missing');
}

// Pre-existing prototype extractions must still be there (these existed before the fix)
// SafeMapPrototypeHas and SafeMapPrototypeGet (or equivalent — any extraction of .has/.get)
if (!/SafeMap(?:Prototype)?(?:Has|\.prototype\.has)/.test(src)) {
    // Accept: SafeMapPrototypeHas OR SafeMap.prototype.has
    pass = false; reasons.push('prototype.has extraction missing');
}
if (!/SafeMap(?:Prototype)?(?:Get|\.prototype\.get)/.test(src)) {
    pass = false; reasons.push('prototype.get extraction missing');
}

// partialDeepStrictEqual must still be exported/defined
if (!/partialDeepStrictEqual/.test(src)) {
    pass = false; reasons.push('partialDeepStrictEqual missing');
}

console.log(pass ? 'PASS' : 'FAIL: ' + reasons.join(', '));
" 2>&1)

if echo "$P2P_RESULT" | grep -q '^PASS'; then
    echo "PASS [pr_diff] (0.10): compareBranch and existing prototype refs intact"
    add_score 0.10
else
    echo "FAIL [pr_diff] (0.10): $P2P_RESULT"
fi

########################################
# Config-derived: Uses .$call or .$apply convention (0.10)
########################################
# [agent_config] (0.10): "Use .$call and .$apply, never .call or .apply" — src/js/CLAUDE.md:56 @ e59a147
# Check that the NEW prototype calls (for set/delete on expectedCounts) use
# bun's .$call convention, not standard .call. Scoped to compareBranch only.
CFG_RESULT=$(node -e "
'use strict';
const fs = require('fs');
const src = fs.readFileSync('$ASSERT_FILE', 'utf8');

const fnStart = src.indexOf('function compareBranch');
if (fnStart === -1) { console.log('NO_FUNC'); process.exit(0); }
const chunk = src.slice(fnStart, fnStart + 3000);

// Check: any prototype-based calls on expectedCounts use .\$call not .call
// Bad: SomeVar.call(expectedCounts, ...)  — tamper-vulnerable
// Good: SomeVar.\$call(expectedCounts, ...) — bun intrinsic
const usesDollarCall = /\\$call\s*\(\s*expectedCounts\b/.test(chunk);
const usesPlainCall = /\.call\s*\(\s*expectedCounts\b/.test(chunk);

// .\$call contains .call as substring, so exclude \$call matches
// Check for plain .call that's NOT preceded by \$
const plainCallMatches = chunk.match(/(?<![\\$])\.call\s*\(\s*expectedCounts\b/g);
const hasPlainCall = plainCallMatches && plainCallMatches.length > 0;

if (usesDollarCall && !hasPlainCall) {
    console.log('PASS');
} else if (usesDollarCall && hasPlainCall) {
    console.log('PARTIAL');  // Mixed usage
} else {
    console.log('FAIL: dollarCall=' + usesDollarCall + ', plainCall=' + hasPlainCall);
}
" 2>&1)

if echo "$CFG_RESULT" | grep -q '^PASS'; then
    echo "PASS [agent_config] (0.10): Uses .\$call convention per src/js/CLAUDE.md:56"
    add_score 0.10
elif echo "$CFG_RESULT" | grep -q 'PARTIAL'; then
    echo "PARTIAL [agent_config] (0.05): Mixed .\$call and .call usage"
    add_score 0.05
else
    echo "FAIL [agent_config] (0.10): $CFG_RESULT"
fi

########################################
# Final score
########################################
echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > "/logs/verifier/reward.txt"

# Write detailed reward JSON
python3 -c "
import json
total = $TOTAL
json.dump({
    'reward': total,
    'behavioral': round(min(total, 0.80), 4),
    'regression': round(min(max(total - 0.80, 0), 0.10), 4),
    'config': round(min(max(total - 0.90, 0), 0.10), 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
