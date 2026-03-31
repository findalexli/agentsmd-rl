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

GATE_PASSED=0

###############################################################################
# GATE 1: Key files exist and are genuine (not stubs)
###############################################################################
echo "=== GATE 1: Key files exist and have genuine content ==="
for f in "$APP_PAGE" "$LOADER_TREE" "$APP_RS" "$CHUNK_GROUP"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAILED: $f missing"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done

# Anti-stub: Check files have substantial real code (not just comments/strings)
python3 << 'PYEOF'
import sys

files = {
    "$APP_PAGE": (80, ["export", "import", "function", "const", "class"]),
    "$APP_RS": (400, ["fn ", "impl ", "struct ", "enum ", "use "]),
    "$CHUNK_GROUP": (150, ["fn ", "impl ", "struct ", "enum ", "use "]),
    "$LOADER_TREE": (100, ["fn ", "impl ", "struct ", "use "]),
}

for path, (min_lines, keywords) in files.items():
    expanded_path = path.replace('$APP_PAGE', '/workspace/next.js/packages/next/src/build/templates/app-page.ts').replace('$APP_RS', '/workspace/next.js/crates/next-api/src/app.rs').replace('$CHUNK_GROUP', '/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs').replace('$LOADER_TREE', '/workspace/next.js/crates/next-core/src/app_page_loader_tree.rs')
    with open(expanded_path) as f:
        content = f.read()
        lines = content.split('\n')

    # Count lines that contain actual code (not just comments/strings with keywords)
    code_lines = 0
    for line in lines:
        stripped = line.strip()
        # Skip empty lines and pure comment lines
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue
        # Count lines that have Rust/TS code keywords
        for kw in keywords:
            if kw in line:
                code_lines += 1
                break

    if code_lines < min_lines // 4:  # At least 25% of min_lines should be code
        print(f"FAIL: {expanded_path} has insufficient code ({code_lines} code keywords)")
        sys.exit(1)

print("PASS: all files have genuine code content")
sys.exit(0)
PYEOF

if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
GATE_PASSED=1
echo "GATE 1 PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (structural: app-page.ts imports have transition)      = 0.25
#   TEST 2 (structural: SharedMultiple variant integrated)        = 0.25
#   TEST 3 (structural: app_module_graphs uses Option param)      = 0.20
#   TEST 4 (structural: fillMetadataSegment transition removed)   = 0.15
#   TEST 5 (semantic: SharedMultiple properly integrated)         = 0.10
#   TEST 6 (config-derived: No Claude footers in commits)         = 0.05
#   TOTAL                                                         = 1.00
###############################################################################

TOTAL_SCORE=0

###############################################################################
# TEST 1 [STRUCTURAL, 0.25]: app-page.ts server imports have transition
# [pr_diff] Add 'turbopack-transition': 'next-server-utility' to server imports
###############################################################################
echo ""
echo "=== TEST 1: [structural] server-side imports in app-page.ts have next-server-utility transition ==="

T1_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$APP_PAGE', 'utf-8');

// Parse import statements properly (not just grep)
const importRegex = /import\\s+(?:(?:\\{[^}]*\\}\\s*from\\s+)?|(?:\\*\\s+as\\s+\\w+\\s+from\\s+)?|(?:\\w+\\s+from\\s+))?['\"]([^'\"]+)['\"](?:\\s+with\\s*\\{([^}]+)\\})?/g;

// Server-side import patterns that SHOULD have the transition
const serverPatterns = [
  /server\\//,
  /shared\\/lib\\//,
  /lib\\/(?:fallback|constants|url|scheduler)/,
  /client\\/components/,
];

let totalServerImports = 0;
let importsWithTransition = 0;
let match;

while ((match = importRegex.exec(src)) !== null) {
  const importPath = match[1];
  const withClause = match[2] || '';

  // Check if this is a server-side import (from server/, shared/lib/, etc.)
  const isServerImport = serverPatterns.some(p => p.test(importPath));

  if (isServerImport) {
    totalServerImports++;
    if (withClause.includes('next-server-utility')) {
      importsWithTransition++;
    }
  }
}

// Must have at least 15 server imports with the transition annotation
if (totalServerImports >= 10 && importsWithTransition >= 10) {
  const ratio = importsWithTransition / totalServerImports;
  if (ratio >= 0.8) {
    console.log('PASS: ' + importsWithTransition + '/' + totalServerImports + ' server imports have transition');
    process.exit(0);  // Full points
  } else {
    console.log('PARTIAL: ' + importsWithTransition + '/' + totalServerImports + ' server imports have transition');
    process.exit(1);  // Partial - will be handled
  }
}

console.log('FAIL: insufficient server imports with transition (' + importsWithTransition + '/' + totalServerImports + ')');
process.exit(2);
"
T1_EXIT=$?
echo "  -> exit code: $T1_EXIT"

if [ $T1_EXIT -eq 0 ]; then
    T1_SCORE=25
elif [ $T1_EXIT -eq 1 ]; then
    T1_SCORE=12  # Half credit for partial
fi
TOTAL_SCORE=$((TOTAL_SCORE + T1_SCORE))
echo "  -> score: 0.$T1_SCORE / 0.25"

###############################################################################
# TEST 2 [STRUCTURAL, 0.25]: SharedMultiple variant exists and is integrated
# [pr_diff] Add SharedMultiple variant to ChunkGroupEntry, ChunkGroup, ChunkGroupKey
###############################################################################
echo ""
echo "=== TEST 2: [structural] SharedMultiple variant exists in all enums ==="

T2_SCORE=0
python3 << 'PYEOF'
import sys
import re

with open("$CHUNK_GROUP".replace('$CHUNK_GROUP', '/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs')) as f:
    src = f.read()

# Check for SharedMultiple in specific enum definitions (not just anywhere)
required_locations = [
    # ChunkGroupEntry enum variant
    (r'pub enum ChunkGroupEntry\s*\{[^}]*SharedMultiple\s*\(', True),
    # ChunkGroup enum variant
    (r'pub enum ChunkGroup\s*\{[^}]*SharedMultiple\s*\(', True),
    # ChunkGroupKey enum variant
    (r'pub enum ChunkGroupKey\s*\{[^}]*SharedMultiple\s*\(', True),
]

found_count = 0
for pattern, required in required_locations:
    if re.search(pattern, src, re.DOTALL):
        found_count += 1

if found_count >= 3:
    # Bonus: verify it's used in pattern matching (entries(), entries_count(), etc.)
    pattern_matches = src.count('| Self::SharedMultiple')
    pattern_matches += src.count('| ChunkGroup::SharedMultiple')
    pattern_matches += src.count('| ChunkGroupKey::SharedMultiple')

    if pattern_matches >= 3:
        print(f"PASS: SharedMultiple in all 3 enums with {pattern_matches} pattern matches")
        sys.exit(0)
    else:
        print(f"PARTIAL: SharedMultiple in enums but only {pattern_matches} pattern matches")
        sys.exit(1)
else:
    print(f"FAIL: SharedMultiple in only {found_count}/3 required locations")
    sys.exit(2)
PYEOF
T2_EXIT=$?
echo "  -> exit code: $T2_EXIT"

if [ $T2_EXIT -eq 0 ]; then
    T2_SCORE=25
elif [ $T2_EXIT -eq 1 ]; then
    T2_SCORE=15
fi
TOTAL_SCORE=$((TOTAL_SCORE + T2_SCORE))
echo "  -> score: 0.$T2_SCORE / 0.25"

###############################################################################
# TEST 3 [STRUCTURAL, 0.20]: app_module_graphs uses Option parameter
# [pr_diff] Refactor to use Option<Vc<EvaluatableAssets>> instead of separate params
###############################################################################
echo ""
echo "=== TEST 3: [structural] app_module_graphs uses Option parameter ==="

T3_SCORE=0
python3 << 'PYEOF'
import re
import sys

with open("$APP_RS".replace('$APP_RS', '/workspace/next.js/crates/next-api/src/app.rs')) as f:
    src = f.read()

# Find the app_module_graphs function definition
fn_match = re.search(r'fn\s+app_module_graphs\s*\((.*?)\)', src, re.DOTALL)
if not fn_match:
    print("FAIL: app_module_graphs function not found")
    sys.exit(1)

sig = fn_match.group(1)

# Check for the Option parameter pattern
has_option_param = 'Option<Vc<EvaluatableAssets>>' in sig
has_combined_name = 'client_shared_entries_when_has_layout_segments' in sig

# Check that old pattern is gone
has_old_pattern = 'has_layout_segments: bool' in sig and 'client_shared_entries:' in sig

if has_old_pattern:
    print("FAIL: still has old separate parameters")
    sys.exit(2)

if has_option_param or has_combined_name:
    # Additional check: verify Option is used in the function body
    body_match = re.search(r'fn\s+app_module_graphs\s*\(.*?\)\s*->.*?\{', src, re.DOTALL)
    if body_match:
        start = body_match.end()
        # Find corresponding closing brace (simplified)
        depth = 1
        end = start
        for i, c in enumerate(src[start:]):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = start + i
                    break
        body = src[start:end]

        # Check for Option usage patterns
        option_used = (
            '.then(||' in body or
            'if let Some(' in body or
            'match' in body and 'Some(' in body or
            'unwrap_or' in body or
            'is_none()' in body or
            'is_some()' in body
        )

        if option_used:
            print("PASS: app_module_graphs uses Option parameter with proper pattern matching")
            sys.exit(0)
        else:
            print("PARTIAL: Option parameter present but not properly used in function body")
            sys.exit(1)

print("FAIL: Option parameter pattern not found")
sys.exit(3)
PYEOF
T3_EXIT=$?
echo "  -> exit code: $T3_EXIT"

if [ $T3_EXIT -eq 0 ]; then
    T3_SCORE=20
elif [ $T3_EXIT -eq 1 ]; then
    T3_SCORE=10
fi
TOTAL_SCORE=$((TOTAL_SCORE + T3_SCORE))
echo "  -> score: 0.$T3_SCORE / 0.20"

###############################################################################
# TEST 4 [STRUCTURAL, 0.15]: fillMetadataSegment transition removed
# [pr_diff] Remove 'turbopack-transition' from fillMetadataSegment import string
###############################################################################
echo ""
echo "=== TEST 4: [structural] fillMetadataSegment import without transition ==="

T4_SCORE=0
python3 << 'PYEOF'
import sys

with open("$LOADER_TREE".replace('$LOADER_TREE', '/workspace/next.js/crates/next-core/src/app_page_loader_tree.rs')) as f:
    src = f.read()

# Find fillMetadataSegment in the file
if 'fillMetadataSegment' not in src:
    print("FAIL: fillMetadataSegment not found")
    sys.exit(1)

# Find context around fillMetadataSegment (±300 chars)
idx = src.index('fillMetadataSegment')
context = src[max(0, idx-300):idx+300]

# The import string should NOT have next-server-utility transition
if 'next-server-utility' in context:
    # Check if it's in a comment or actual code
    lines = context.split('\n')
    for line in lines:
        if 'next-server-utility' in line and not line.strip().startswith('//'):
            # It's in actual code - check if same line/region as fillMetadataSegment
            if 'fillMetadataSegment' in context[context.index('next-server-utility')-100:context.index('next-server-utility')+100]:
                print("FAIL: fillMetadataSegment context still has next-server-utility transition")
                sys.exit(2)

# Verify the import string exists and looks correct
if 'import' in context and 'fillMetadataSegment' in context:
    print("PASS: fillMetadataSegment import without next-server-utility transition")
    sys.exit(0)
else:
    print("FAIL: Could not verify fillMetadataSegment import")
    sys.exit(3)
PYEOF
T4_EXIT=$?
echo "  -> exit code: $T4_EXIT"

if [ $T4_EXIT -eq 0 ]; then
    T4_SCORE=15
fi
TOTAL_SCORE=$((TOTAL_SCORE + T4_SCORE))
echo "  -> score: 0.$T4_SCORE / 0.15"

###############################################################################
# TEST 5 [SEMANTIC, 0.10]: Route handlers don't pass client runtime entries
# [pr_diff] Use is_app_page.then(|| ...) pattern
###############################################################################
echo ""
echo "=== TEST 5: [semantic] Route handlers pass None, pages pass Some ==="

T5_SCORE=0
python3 << 'PYEOF'
import re
import sys

with open("$APP_RS".replace('$APP_RS', '/workspace/next.js/crates/next-api/src/app.rs')) as f:
    src = f.read()

# Look for the pattern where client_runtime_entries is conditional on is_app_page
# This validates the fix: route handlers don't get entries, pages do

patterns_found = 0

# Pattern 1: then closure pattern
if re.search(r'is_app_page\.then\(\|\|.*?client_runtime_entries', src, re.DOTALL):
    patterns_found += 1

# Pattern 2: if/then pattern for route handlers
if 'EvaluatableAssets::empty()' in src or 'None' in src:
    patterns_found += 1

# Pattern 3: Check for comment about route handlers not needing entries
if 'route' in src.lower() and ('handler' in src.lower() or 'not for' in src.lower()):
    patterns_found += 1

if patterns_found >= 2:
    print("PASS: Proper conditional handling of client runtime entries")
    sys.exit(0)
elif patterns_found >= 1:
    print("PARTIAL: Some conditional handling present")
    sys.exit(1)
else:
    print("FAIL: No conditional handling of client runtime entries found")
    sys.exit(2)
PYEOF
T5_EXIT=$?
echo "  -> exit code: $T5_EXIT"

if [ $T5_EXIT -eq 0 ]; then
    T5_SCORE=10
elif [ $T5_EXIT -eq 1 ]; then
    T5_SCORE=5
fi
TOTAL_SCORE=$((TOTAL_SCORE + T5_SCORE))
echo "  -> score: 0.$T5_SCORE / 0.10"

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.05]: Do NOT add Generated with Claude Code footers
# [agent_config] Per CLAUDE.md line ~348 @ 883d93c8935afb2b8124ab324a10fa36cbd7a88c
###############################################################################
echo ""
echo "=== TEST 6: [config-derived] No Claude attribution in commits ==="

T6_SCORE=0
cd /workspace/next.js 2>/dev/null
if [ $? -eq 0 ]; then
    # Check recent commits for Claude attribution
    CLAUDE_IN_COMMIT=$(git log --format=%B -n10 2>/dev/null | grep -c "Generated with Claude\|Co-Authored-By: Claude" || echo "0")
    if [ "$CLAUDE_IN_COMMIT" -gt 0 ]; then
        echo "FAIL: Commit message contains Claude footer"
    else
        echo "PASS: No Claude attribution in commits"
        T6_SCORE=5
    fi
else
    # Can't check, assume pass
    echo "SKIP: Cannot check git log"
    T6_SCORE=5
fi
TOTAL_SCORE=$((TOTAL_SCORE + T6_SCORE))
echo "  -> score: 0.0$T6_SCORE / 0.05"

###############################################################################
# Final score calculation
###############################################################################
echo ""
echo "========================================"
echo "RESULTS:"
echo "  TEST 1 (app-page.ts transitions)    : 0.$T1_SCORE / 0.25"
echo "  TEST 2 (SharedMultiple variants)    : 0.$T2_SCORE / 0.25"
echo "  TEST 3 (Option parameter)           : 0.$T3_SCORE / 0.20"
echo "  TEST 4 (fillMetadataSegment fix)    : 0.$T4_SCORE / 0.15"
echo "  TEST 5 (Route handler fix)          : 0.$T5_SCORE / 0.10"
echo "  TEST 6 (No Claude attribution)      : 0.0$T6_SCORE / 0.05"
echo "========================================"

# Convert to decimal (0-100 scale to 0.00-1.00)
FINAL_SCORE=$(echo "scale=2; $TOTAL_SCORE / 100" | bc)
echo "TOTAL SCORE: $FINAL_SCORE"

# Write reward
echo "$FINAL_SCORE" > "$REWARD_FILE"

# Also write detailed breakdown
cat > "/logs/verifier/reward.json" << EOF
{
  "reward": $FINAL_SCORE,
  "breakdown": {
    "app_page_transitions": 0.$T1_SCORE,
    "shared_multiple_variant": 0.$T2_SCORE,
    "option_parameter": 0.$T3_SCORE,
    "fillmetadata_fix": 0.$T4_SCORE,
    "route_handler_fix": 0.$T5_SCORE,
    "no_claude_footer": 0.0$T6_SCORE
  }
}
EOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
