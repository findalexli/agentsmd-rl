#!/usr/bin/env bash
# Verifier for nextjs-ts6-baseurl-deprecation
#
# Bug: getTypeScriptConfiguration does not handle baseUrl inherited via extends
# in TS6, causing TS5101 deprecation errors.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/next.js/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts"

###############################################################################
# GATE: TypeScript syntax validity
###############################################################################
npx -y typescript@5 --noEmit --allowJs --checkJs false --strict false \
  --moduleResolution node --esModuleInterop "$TARGET" 2>/dev/null
# Just check it parses as valid TS — a quick syntax gate
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
if (src.length < 100) { process.exit(1); }
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: file too small or missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: rewritePathAliases helper extracted)   = 0.25
#   TEST 2 (fail-to-pass: TS6 post-parse baseUrl handling)       = 0.35
#   TEST 3 (pass-to-pass: resolvePathAliasTarget still exists)   = 0.10
#   TEST 4 (structural: helper is called in both paths)          = 0.15
#   TEST 5 (anti-stub)                                           = 0.10
#   TEST 6 (config-derived: Do NOT add Generated with Claude Code footers)    = 0.05
#   TOTAL                                                      = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.25]: Extracted helper for path rewriting
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] rewritePathAliasesWithoutBaseUrl helper function exists"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
// The fix extracts the inline path-rewriting code into a function
if (src.includes('rewritePathAliasesWithoutBaseUrl') || src.includes('rewritePathAliases')) {
  // Check it's a function declaration/expression
  if (/function\s+(rewritePathAliases\w*)\s*\(/.test(src)) {
    console.log('PASS: helper function found');
    process.exit(0);
  }
}
console.log('FAIL: no path-rewriting helper function found');
process.exit(1);
"
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.35]: Post-parse handling of inherited baseUrl for TS6
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] TS6 post-parse baseUrl removal for inherited extends"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
// The fix adds a block after parseJsonConfigFileContent that checks for TS >= 6.0.0
// and handles result.options.baseUrl
const hasTS6Check = /(?:semver\.gte|typescript\.version|6\.0\.0)/.test(src) &&
                    /result\.options\.baseUrl/.test(src);
const hasBaseUrlDelete = /delete\s+.*baseUrl/.test(src) || /baseUrl.*=.*undefined/.test(src);
// The fix should both check for TS6 and delete/remove the inherited baseUrl
const hasPostParseBlock = src.includes('result.options.baseUrl') &&
                          (src.includes('6.0.0') || src.includes('6.0'));

if (hasTS6Check && hasBaseUrlDelete) {
  console.log('PASS: TS6 version check + baseUrl deletion found');
  process.exit(0);
}
if (hasPostParseBlock && hasBaseUrlDelete) {
  console.log('PASS: post-parse baseUrl handling found');
  process.exit(0);
}
console.log('FAIL: no TS6 post-parse baseUrl handling');
process.exit(1);
"
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [PASS-TO-PASS, 0.10]: resolvePathAliasTarget still exists
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] resolvePathAliasTarget function preserved"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
if (/function\s+resolvePathAliasTarget/.test(src)) {
  console.log('PASS: resolvePathAliasTarget still exists');
  process.exit(0);
}
console.log('FAIL: resolvePathAliasTarget missing');
process.exit(1);
"
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL, 0.15]: Helper called in both direct-config and post-parse paths
###############################################################################
echo ""
echo "TEST 4: [structural] path-rewriting used in both code paths"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
// Count how many times the helper function is called
const helperMatch = src.match(/function\s+(rewritePathAliases\w*)\s*\(/);
if (!helperMatch) {
  console.log('FAIL: no helper function found');
  process.exit(1);
}
const helperName = helperMatch[1];
const callCount = (src.match(new RegExp(helperName + '\\\\s*\\\\(', 'g')) || []).length;
// Should be at least 3: 1 declaration + 2 calls (direct config + post-parse)
if (callCount >= 3) {
  console.log('PASS: helper called in multiple code paths (' + callCount + ' occurrences)');
  process.exit(0);
}
console.log('FAIL: helper only found ' + callCount + ' times (expected >= 3)');
process.exit(1);
"
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.15]: File is not a stub
###############################################################################
echo ""
echo "TEST 5: [anti-stub] file has substantial content"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
const lines = src.split('\n').length;
if (lines < 50) {
  console.log('FAIL: only ' + lines + ' lines');
  process.exit(1);
}
// Check for key functions
const hasGetConfig = /function\s+getTypeScriptConfiguration/.test(src) ||
                     /async\s+function\s+getTypeScriptConfiguration/.test(src) ||
                     src.includes('getTypeScriptConfiguration');
if (!hasGetConfig) {
  console.log('FAIL: getTypeScriptConfiguration not found');
  process.exit(1);
}
console.log('PASS: ' + lines + ' lines, getTypeScriptConfiguration present');
process.exit(0);
"
T5=$?
echo "  -> exit code: $T5"

###############################################################################

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.05]: Do NOT add Generated with Claude Code footers
###############################################################################
echo ""
echo "TEST 6: [config-derived] Do NOT add Generated with Claude Code footers"
# Source: CLAUDE.md line 348 @ b163a8bf6642c7c849964d1238c13cc91d0c2252
node -e "
const {execSync} = require('child_process');
try {
    const log = execSync('git log --format=%B -n5 2>/dev/null || true', {encoding: 'utf8', cwd: '/workspace/next.js'});
    if (log.includes('Generated with Claude') || log.includes('Co-Authored-By: Claude')) {
        console.log('FAIL: commit message contains Claude footer');
        process.exit(1);
    }
} catch(e) {}
console.log('PASS');
"
T6=$?
echo "  -> exit code: $T6"

# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.25 if $T1 == 0 else 0.0
t2 = 0.35 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: helper extracted)            = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 2 (fail-to-pass: TS6 post-parse handling)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 3 (pass-to-pass: resolvePathAliasTarget)      = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (structural: helper used in both paths)     = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (anti-stub)                                 = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
