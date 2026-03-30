#!/usr/bin/env bash
# Verifier for nextjs-layout-segment-optimization
#
# Bug: Server-side imports in app-page.ts lack turbopack transition annotations,
# and the module graph API uses incorrect parameters breaking layout segment opt.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

APP_PAGE="/workspace/next.js/packages/next/src/build/templates/app-page.ts"
LOADER_TREE="/workspace/next.js/crates/next-core/src/app_page_loader_tree.rs"
APP_RS="/workspace/next.js/crates/next-api/src/app.rs"
CHUNK_GROUP="/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs"

###############################################################################
# GATE: Key files exist
###############################################################################
for f in "$APP_PAGE" "$LOADER_TREE" "$APP_RS" "$CHUNK_GROUP"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAILED: $f missing"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: app-page.ts imports have transition)    = 0.30
#   TEST 2 (fail-to-pass: SharedMultiple variant added)           = 0.25
#   TEST 3 (fail-to-pass: app_module_graphs uses Option param)    = 0.20
#   TEST 4 (structural: fillMetadataSegment transition removed)   = 0.10
#   TEST 5 (anti-stub: files have substantial content)            = 0.10
#   TEST 6 (config-derived: Do NOT add Generated with Claude Code footers)    = 0.05
#   TOTAL                                                      = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: app-page.ts server imports have transition
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] server-side imports in app-page.ts have next-server-utility transition"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$APP_PAGE', 'utf-8');

// These imports should have the turbopack-transition annotation in the fix
const mustHaveTransition = [
  'getRevalidateReason',
  'getTracer',
  'request-meta',
  'interopDefault',
  'strip-flight-headers',
  'base-http/node',
  'checkIsAppPPREnabled',
  'fallback-params',
  'manifests-singleton',
  'streaming-metadata',
  'app-paths',
  'server-action-request-meta',
  'app-router-headers',
  'is-bot',
  'response-cache',
  'fallback',
  'render-result',
  'constants',
  'encoded-tags',
  'node-web-streams-helper',
  'send-payload',
  'no-fallback-error',
  'size-limit',
  'postponed-request-body',
  'parseUrl',
  'redirect-status-code',
  'invariant-error',
  'scheduler',
  'interception-routes',
  'get-segment-param',
];

const lines = src.split('\n');
let importsWithTransition = 0;
let importsWithoutTransition = 0;

for (const pattern of mustHaveTransition) {
  // Find import lines containing this pattern
  for (const line of lines) {
    if (line.includes('import') && line.includes(pattern)) {
      if (line.includes('next-server-utility')) {
        importsWithTransition++;
      } else {
        importsWithoutTransition++;
      }
      break;
    }
  }
}

// At least 15 imports should have the transition
if (importsWithTransition >= 15) {
  console.log('PASS: ' + importsWithTransition + ' imports have next-server-utility transition');
  process.exit(0);
}
console.log('FAIL: only ' + importsWithTransition + ' imports have transition (' + importsWithoutTransition + ' without)');
process.exit(1);
"
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: SharedMultiple variant exists in chunk_group_info
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] SharedMultiple variant exists in chunk_group_info.rs"
python3 << 'PYEOF'
import sys

with open("$CHUNK_GROUP") as f:
    src = f.read()

# Check for SharedMultiple in the enum definitions
if 'SharedMultiple' in src:
    # Verify it appears in the ChunkGroupEntry, ChunkGroup, and ChunkGroupKey enums
    count = src.count('SharedMultiple')
    if count >= 3:
        print(f"PASS: SharedMultiple found {count} times across enums")
        sys.exit(0)
    else:
        print(f"FAIL: SharedMultiple found only {count} times (expected >= 3)")
        sys.exit(1)

print("FAIL: SharedMultiple variant not found")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.20]: app_module_graphs uses Option parameter
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] app_module_graphs uses Option parameter instead of two params"
python3 << 'PYEOF'
import re, sys

with open("$APP_RS") as f:
    src = f.read()

# The fix combines client_shared_entries + has_layout_segments into Option<Vc<...>>
# Look for the function signature with Option
if 'Option<Vc<EvaluatableAssets>>' in src or 'client_shared_entries_when_has_layout_segments' in src:
    print("PASS: app_module_graphs uses Option parameter")
    sys.exit(0)

# Check that has_layout_segments is NOT a separate bool parameter
fn_match = re.search(r'fn\s+app_module_graphs[^{]+\{', src, re.DOTALL)
if fn_match:
    sig = fn_match.group(0)
    if 'has_layout_segments: bool' in sig:
        print("FAIL: still has separate has_layout_segments: bool parameter")
        sys.exit(1)
    if 'Option' in sig:
        print("PASS: app_module_graphs uses Option in signature")
        sys.exit(0)

print("FAIL: app_module_graphs signature not updated")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL, 0.10]: fillMetadataSegment import transition removed
###############################################################################
echo ""
echo "TEST 4: [structural] fillMetadataSegment import no longer has transition annotation"
python3 << 'PYEOF'
import sys

with open("$LOADER_TREE") as f:
    src = f.read()

# Find the fillMetadataSegment import line
lines = src.split('\n')
for line in lines:
    if 'fillMetadataSegment' in line and 'import' in line.lower():
        if 'next-server-utility' in line:
            print("FAIL: fillMetadataSegment still has next-server-utility transition")
            sys.exit(1)
        else:
            print("PASS: fillMetadataSegment import without transition annotation")
            sys.exit(0)

# If it's in a multi-line string, check the broader context
if 'fillMetadataSegment' in src:
    idx = src.index('fillMetadataSegment')
    context = src[max(0, idx-200):idx+200]
    if 'next-server-utility' not in context:
        print("PASS: fillMetadataSegment context lacks transition")
        sys.exit(0)
    else:
        print("FAIL: fillMetadataSegment context still has transition")
        sys.exit(1)

print("FAIL: fillMetadataSegment not found")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.15]: Files have substantial content
###############################################################################
echo ""
echo "TEST 5: [anti-stub] key files have substantial content"
python3 << 'PYEOF'
import sys

files = {
    "$APP_PAGE": 100,
    "$APP_RS": 500,
    "$CHUNK_GROUP": 200,
}

for path, min_lines in files.items():
    with open(path) as f:
        lines = len(f.readlines())
    if lines < min_lines:
        print(f"FAIL: {path} has {lines} lines (expected >= {min_lines})")
        sys.exit(1)

print("PASS: all files have substantial content")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.05]: Do NOT add Generated with Claude Code footers
###############################################################################
echo ""
echo "TEST 6: [config-derived] Do NOT add Generated with Claude Code footers"
# Source: CLAUDE.md line 348 @ 883d93c8935afb2b8124ab324a10fa36cbd7a88c
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
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.20 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: server imports have transition)  = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: SharedMultiple variant)          = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: Option param in module_graphs)   = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 4 (structural: fillMetadataSegment transition)    = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub)                                     = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
