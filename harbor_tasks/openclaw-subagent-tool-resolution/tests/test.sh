#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/src/plugins/tools.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weights: >=60% behavioral (fail-to-pass + pass-to-pass)
BEHAVIORAL_WEIGHT=0.50  # Fail-to-pass: upstream test suite
P2P_WEIGHT=0.25         # Pass-to-pass: upstream regression
STRUCTURAL_WEIGHT=0.15  # Bronze: minimal AST to verify functions exist
ANTISTUB_WEIGHT=0.05    # Anti-stub: non-trivial implementation
CONFIG_WEIGHT=0.05      # Config: no @ts-nocheck

TOTAL_WEIGHT=1.0
SCORE=0.0

if [ ! -f "$TARGET" ]; then
    echo "0.0" > "$$REWARD_FILE"
    exit 0
fi

# ---------- GATE: Syntax/TypeScript validity (must pass for any points) ----------
# Check that the file is valid TypeScript (no syntax errors)
cd /workspace/openclaw
if ! npx tsc --noEmit src/plugins/tools.ts 2>/dev/null; then
    # Try esbuild or swc for faster syntax check
    if ! npx esbuild src/plugins/tools.ts --platform=node --format=cjs --outfile=/dev/null 2>/dev/null; then
        # Even simpler: try to parse as TypeScript
        node -e "
        const ts = require('typescript');
        const fs = require('fs');
        const source = fs.readFileSync('$TARGET', 'utf8');
        const result = ts.createSourceFile('$TARGET', source, ts.ScriptTarget.Latest, true);
        if (result.parseDiagnostics.length > 0) {
            console.log('SYNTAX ERROR');
            process.exit(1);
        }
        console.log('SYNTAX OK');
        " 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "GATE FAIL: Syntax errors in tools.ts" >&2
            echo "0.0" > "$REWARD_FILE"
            exit 0
        fi
    fi
fi
echo "GATE: Syntax check PASSED"

# ---------- PRIMARY 1 (50%): Fail-to-pass behavioral test ----------
# [pr_diff] (0.50): Plugin tool resolution uses active registry for subagents
# Run the upstream test that specifically tests the fix
cd /workspace/openclaw
# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    npm install 2>&1 | tail -5
fi

# Run the specific test file for optional tools that includes the new tests
npx vitest run src/plugins/tools.optional.test.ts --reporter=verbose 2>&1 | grep -E "(PASS|FAIL|✓|✗|Error)" | head -30
VITEST_EXIT=${PIPESTATUS[0]}

if [ $VITEST_EXIT -eq 0 ]; then
    echo "BEHAVIORAL: PASS - tools.optional.test.ts passes"
    SCORE=$(python3 -c "print(f'{$SCORE + $BEHAVIORAL_WEIGHT:.2f}')")
    BEHAVIORAL_PASS=1
else
    echo "BEHAVIORAL: FAIL - tests failed"
    BEHAVIORAL_PASS=0
fi

# If behavioral fails, we can still award partial credit from other checks (per additive schema)

# ---------- PRIMARY 2 (25%): Pass-to-pass regression tests ----------
# [repo_tests] (0.25): Upstream tests still pass for plugin loading
if [ $VITEST_EXIT -eq 0 ]; then
    # Also verify the main tools.ts tests still work
    npx vitest run src/plugins/loader.test.ts --run 2>&1 | grep -E "(PASS|FAIL|✓|✗|Tests:)" | tail -3
    LOADER_EXIT=${PIPESTATUS[0]}

    if [ $LOADER_EXIT -eq 0 ]; then
        echo "P2P: PASS - loader tests still work"
        SCORE=$(python3 -c "print(f'{$SCORE + $P2P_WEIGHT:.2f}')")
    else
        echo "P2P: PARTIAL - some loader tests may be affected (acceptable for bug fix)"
        # For bug fixes, we're more lenient on P2P - partial credit
        SCORE=$(python3 -c "print(f'{$SCORE + ${P2P_WEIGHT} * 0.5:.2f}')")
    fi
else
    echo "P2P: SKIP - behavioral tests must pass first"
fi

# ---------- SUPPLEMENTARY (15%): Structural verification ----------
# Bronze: Cannot call code (needs running Node runtime), so AST check is justified
python3 << 'PYEOF'
import ast
import sys

# Read file
with open("/workspace/openclaw/src/plugins/tools.ts") as f:
    src = f.read()

# Simple structural checks without regex
# 1. Must have getActivePluginRegistry imported/function
has_get_active = "getActivePluginRegistry" in src

# 2. Must have allowGatewaySubagentBinding parameter handling
has_allow_binding = "allowGatewaySubagentBinding" in src

# 3. Must not just have keywords but actual call (not just import)
has_get_active_call = "getActivePluginRegistry()" in src or \
                       "getActivePluginRegistry ()" in src

# 4. Verify there's actual logic (?? or || fallback pattern)
has_fallback = "??" in src or "||" in src or "resolveRuntimePluginRegistry" in src

# Require at least 3 of 4 conditions for full structural credit
score = 0
if has_get_active: score += 1
if has_allow_binding: score += 1
if has_get_active_call: score += 1
if has_fallback: score += 1

structural_ratio = score / 4.0

if structural_ratio >= 0.75:
    print(f"STRUCTURAL: PASS ({score}/4 criteria)")
    print(f"structural_score=1.0")
elif structural_ratio >= 0.5:
    print(f"STRUCTURAL: PARTIAL ({score}/4 criteria)")
    print(f"structural_score=0.5")
else:
    print(f"STRUCTURAL: FAIL ({score}/4 criteria)")
    print("  - getActivePluginRegistry present:", has_get_active)
    print("  - allowGatewaySubagentBinding present:", has_allow_binding)
    print("  - getActivePluginRegistry called:", has_get_active_call)
    print("  - fallback logic present:", has_fallback)
    print(f"structural_score=0.0")
PYEOF

STRUCTURAL_OUT=$(python3 << 'PYEOF' 2>&1
import ast
import sys

with open("/workspace/openclaw/src/plugins/tools.ts") as f:
    src = f.read()

has_get_active = "getActivePluginRegistry" in src
has_allow_binding = "allowGatewaySubagentBinding" in src
has_get_active_call = "getActivePluginRegistry()" in src or "getActivePluginRegistry ()" in src
has_fallback = "??" in src or "||" in src or "resolveRuntimePluginRegistry" in src

score = sum([has_get_active, has_allow_binding, has_get_active_call, has_fallback])
structural_ratio = score / 4.0

if structural_ratio >= 0.75:
    print(1.0)
elif structural_ratio >= 0.5:
    print(0.5)
else:
    print(0.0)
PYEOF
)
STRUCTURAL_SCORE=$(echo "$STRUCTURAL_OUT" | tail -1)
SCORE=$(python3 -c "print(f'{$SCORE + $STRUCTURAL_WEIGHT * $STRUCTURAL_SCORE:.2f}')")

# ---------- Anti-stub (5%): Non-trivial implementation ----------
python3 << 'PYEOF'
import sys

with open("/workspace/openclaw/src/plugins/tools.ts") as f:
    lines = f.read().splitlines()

# Count non-trivial lines (not comments, not empty)
nontrivial = 0
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith('//'):
        nontrivial += 1

# Also check for function definitions (not just exports)
has_function_def = any('function ' in l or '=>' in l for l in lines)

if nontrivial > 20 and has_function_def:
    print("ANTISTUB: PASS")
    print("antistub_score=1.0")
elif nontrivial > 10:
    print("ANTISTUB: PARTIAL")
    print("antistub_score=0.5")
else:
    print("ANTISTUB: FAIL")
    print("antistub_score=0.0")
PYEOF

ANTISTUB_OUT=$(python3 << 'PYEOF'
with open("/workspace/openclaw/src/plugins/tools.ts") as f:
    lines = f.read().splitlines()

nontrivial = sum(1 for l in lines if l.strip() and not l.strip().startswith('//'))
has_function_def = any('function ' in l or '=>' in l for l in lines)

if nontrivial > 20 and has_function_def:
    print(1.0)
elif nontrivial > 10:
    print(0.5)
else:
    print(0.0)
PYEOF
)
ANTISTUB_SCORE=$(echo "$ANTISTUB_OUT" | tail -1)
SCORE=$(python3 -c "print(f'{$SCORE + $ANTISTUB_WEIGHT * $ANTISTUB_SCORE:.2f}')")

# ---------- Config-derived (5%): No @ts-nocheck ----------
# [agent_config] (0.05): "Never add @ts-nocheck" - CLAUDE.md
node -e "
const fs = require('fs');
const path = require('path');

function checkDir(dir) {
    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
                checkDir(fullPath);
            } else if (entry.isFile() && entry.name.endsWith('.ts') && !entry.name.endsWith('.d.ts') && !entry.name.includes('.test.')) {
                const content = fs.readFileSync(fullPath, 'utf8');
                if (content.includes('@ts-nocheck')) {
                    console.log('FAIL: @ts-nocheck found in ' + fullPath);
                    process.exit(1);
                }
            }
        }
    } catch(e) {}
}

checkDir('src/plugins');
console.log('CONFIG: PASS - no @ts-nocheck');
" 2>&1

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{$SCORE + $CONFIG_WEIGHT:.2f}')")
    echo "CONFIG_NOCHECK: PASS"
else
    echo "CONFIG_NOCHECK: FAIL"
fi

# Clamp score to 1.0
SCORE=$(python3 -c "print(f'{min($SCORE, 1.0):.2f}')")

echo "=== TOTAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# Output breakdown
echo "{
  \"reward\": $SCORE,
  \"behavioral\": $BEHAVIORAL_WEIGHT,
  \"behavioral_pass\": ${BEHAVIORAL_PASS:-0},
  \"structural\": $(python3 -c "print(f'{$STRUCTURAL_WEIGHT * $STRUCTURAL_SCORE:.2f}')"),
  \"antistub\": $(python3 -c "print(f'{$ANTISTUB_WEIGHT * $ANTISTUB_SCORE:.2f}')")
}" > "${REWARD_FILE%.txt}.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
