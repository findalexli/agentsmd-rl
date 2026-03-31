#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
TUI_DIR="$REPO/packages/opencode/src/cli/cmd/tui"
APP_FILE="$TUI_DIR/app.tsx"
VARIANT_FILE="$TUI_DIR/component/dialog-variant.tsx"

REWARD=0
add() {
  local w=$1 p=$2
  if [ "$p" = "1" ]; then
    REWARD=$(python3 -c "print(round($REWARD + $w, 4))")
  fi
}

# ============================================================
# GATE: TypeScript build check (behavioral)
# ============================================================
# [pr_diff] (gate): Modified file must compile
echo "=== GATE: Build check ==="
if ! bun build --no-bundle --target=browser "$APP_FILE" >/dev/null 2>&1; then
  echo "GATE FAILED: app.tsx has build errors"
  echo "0.0" > /logs/verifier/reward.txt
  python3 -c "import json; json.dump({'reward':0.0,'behavioral':0.0,'regression':0.0,'config':0.0,'style_rubric':0.0}, open('/logs/verifier/reward.json','w'))"
  exit 0
fi
echo "PASS: app.tsx builds"

# ============================================================
# Analysis script: strips comments, checks patterns via bun
# Justification for source-level checks: SolidJS TSX components
# use reactive primitives (createMemo, createSignal, useDialog)
# that require the full TUI runtime to execute. Cannot call in
# isolation without the entire SolidJS reactivity system.
# ============================================================
ANALYSIS_FILE=$(mktemp /tmp/analysis.XXXXXX.json)

cat > /tmp/analyze.mjs << 'ANALYZE_SCRIPT'
import { readFileSync, writeFileSync } from "fs";

const appFile = process.argv[2];
const outFile = process.argv[3];
const raw = readFileSync(appFile, "utf8");

// Strip single-line and multi-line comments to prevent injection
const stripped = raw
  .replace(/\/\/.*$/gm, "")
  .replace(/\/\*[\s\S]*?\*\//g, "");

const results = {};

// --- Fail-to-pass checks ---

// 1. DialogVariant imported (any valid import syntax)
results.hasImport = /import\s*\{[^}]*\bDialogVariant\b[^}]*\}\s*from/.test(stripped)
  || /import\s+DialogVariant\s+from/.test(stripped);

// 2. dialog method call associated with DialogVariant
//    Find each dialog.replace/open/show/push call, check if DialogVariant
//    appears within 400 chars (covers arrow functions, JSX, etc.)
const dialogMatches = [...stripped.matchAll(/dialog\s*\.\s*(replace|open|show|push)\s*\(/g)];
results.dialogRendersVariant = dialogMatches.some(m => {
  const start = Math.max(0, m.index - 30);
  const end = Math.min(stripped.length, m.index + 400);
  return /DialogVariant/.test(stripped.slice(start, end));
});

// 3. No .variant.cycle() call (the buggy pattern)
results.noCycleCall = !/\.variant\s*\.\s*cycle\s*\(/.test(stripped);

// 4. Title is not "Variant cycle" (the buggy title)
results.titleNotCycle = !/["'`]Variant cycle["'`]/.test(stripped);

// 5. <DialogVariant /> or <DialogVariant ...> JSX element used
results.hasDialogVariantJSX = /<DialogVariant[\s/>]/.test(stripped);

// --- Pass-to-pass checks ---

// 6. variant_cycle or variant.cycle key still registered
results.hasVariantKey = /["'`]variant[._]cycle["'`]/.test(stripped);

// 7. Other dialogs/commands preserved (anti-stub)
results.hasModelDialog = /DialogModel/.test(stripped);
results.hasAppExport = /export\s+(default\s+)?function\s+App/.test(stripped)
  || /export\s+default\s+App/.test(stripped);

// 8. File substance: non-empty lines after comment stripping
const meaningfulLines = stripped.split("\n").filter(l => l.trim().length > 0);
results.lineCount = meaningfulLines.length;
results.hasSubstance = meaningfulLines.length > 150;

// --- Config checks ---

// 9. No 'any' type usage
results.noAnyType = !/:\s*any\b|<any>|as\s+any\b/.test(stripped);

// 10. No else in variant-related area
const variantArea = stripped.match(/variant[._]cycle[\s\S]{0,500}/);
results.noElseInVariant = !variantArea || !/\belse\b/.test(variantArea[0]);

writeFileSync(outFile, JSON.stringify(results));
ANALYZE_SCRIPT

bun run /tmp/analyze.mjs "$APP_FILE" "$ANALYSIS_FILE" 2>/dev/null

# Verify analysis ran
if [ ! -s "$ANALYSIS_FILE" ]; then
  echo '{}' > "$ANALYSIS_FILE"
fi

get() {
  python3 -c "
import json, sys
try:
    d = json.load(open('$ANALYSIS_FILE'))
    print('1' if d.get('$1', False) else '0')
except:
    print('0')
"
}

# ============================================================
# BEHAVIORAL: Fail-to-pass checks (0.60 total)
# These checks FAIL on the buggy base commit and PASS on a
# correct fix. Source-level analysis justified: SolidJS TSX
# requires full runtime to execute.
# ============================================================
echo ""
echo "=== BEHAVIORAL (fail-to-pass) ==="

# [pr_diff] (0.25): dialog.replace/open renders DialogVariant
# Buggy: calls .variant.cycle(), no dialog with DialogVariant
# Fix: dialog.replace(() => <DialogVariant />) or equivalent
echo -n "B1: Dialog call renders DialogVariant... "
B1=$(get dialogRendersVariant)
[ "$B1" = "1" ] && echo "PASS" || echo "FAIL"
add 0.25 $B1

# [pr_diff] (0.15): DialogVariant is imported
# Buggy: no import of DialogVariant
# Fix: import { DialogVariant } from "./component/dialog-variant"
echo -n "B2: DialogVariant imported... "
B2=$(get hasImport)
[ "$B2" = "1" ] && echo "PASS" || echo "FAIL"
add 0.15 $B2

# [pr_diff] (0.10): .variant.cycle() no longer called
# Buggy: local.model.variant.cycle() is called
# Fix: removed in favor of dialog
echo -n "B3: No .variant.cycle() call... "
B3=$(get noCycleCall)
[ "$B3" = "1" ] && echo "PASS" || echo "FAIL"
add 0.10 $B3

# [pr_diff] (0.10): Title updated from "Variant cycle"
# Buggy: title is "Variant cycle"
# Fix: title reflects selection (e.g. "Switch variant")
echo -n "B4: Title not 'Variant cycle'... "
B4=$(get titleNotCycle)
[ "$B4" = "1" ] && echo "PASS" || echo "FAIL"
add 0.10 $B4

# ============================================================
# REGRESSION: Pass-to-pass checks (0.20 total)
# ============================================================
echo ""
echo "=== REGRESSION (pass-to-pass) ==="

# [pr_diff] (0.10): Both files build together (import resolution)
echo -n "R1: Both app.tsx and dialog-variant.tsx build... "
R1=0
if bun build --no-bundle --target=browser "$APP_FILE" "$VARIANT_FILE" >/dev/null 2>&1; then
  R1=1; echo "PASS"
else
  echo "FAIL"
fi
add 0.10 $R1

# [pr_diff] (0.05): variant_cycle keybind still registered
echo -n "R2: variant_cycle keybind preserved... "
R2=$(get hasVariantKey)
[ "$R2" = "1" ] && echo "PASS" || echo "FAIL"
add 0.05 $R2

# [pr_diff] (0.05): Other commands/dialogs preserved (anti-stub)
# Original app.tsx has DialogModel and App export — verify not gutted
echo -n "R3: Other dialogs + App export preserved... "
R3_MODEL=$(get hasModelDialog)
R3_APP=$(get hasAppExport)
R3=0; [ "$R3_MODEL" = "1" ] && [ "$R3_APP" = "1" ] && R3=1
[ "$R3" = "1" ] && echo "PASS" || echo "FAIL"
add 0.05 $R3

# ============================================================
# CONFIG-DERIVED: Agent config checks (0.10 total)
# ============================================================
echo ""
echo "=== CONFIG ==="

# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ 8ac2fbbd12
echo -n "C1: No 'any' type in app.tsx... "
C1=$(get noAnyType)
[ "$C1" = "1" ] && echo "PASS" || echo "FAIL"
add 0.05 $C1

# [agent_config] (0.05): "Avoid `else` statements." — AGENTS.md:84 @ 8ac2fbbd12
echo -n "C2: No else in variant area... "
C2=$(get noElseInVariant)
[ "$C2" = "1" ] && echo "PASS" || echo "FAIL"
add 0.05 $C2

# ============================================================
# STRUCTURAL: Anti-stub checks (0.10 total)
# ============================================================
echo ""
echo "=== STRUCTURAL ==="

# [pr_diff] (0.05): File not gutted
echo -n "S1: app.tsx has >150 meaningful lines... "
S1=$(get hasSubstance)
[ "$S1" = "1" ] && echo "PASS" || echo "FAIL"
add 0.05 $S1

# [pr_diff] (0.05): dialog-variant.tsx component intact
echo -n "S2: dialog-variant.tsx exists and exports DialogVariant... "
S2=0
if [ -f "$VARIANT_FILE" ] && grep -q 'DialogVariant' "$VARIANT_FILE" 2>/dev/null; then
  S2=1; echo "PASS"
else
  echo "FAIL"
fi
add 0.05 $S2

# ============================================================
# RESULTS
# ============================================================
echo ""
echo "=== RESULTS ==="
REWARD=$(python3 -c "print(round($REWARD, 2))")
echo "Reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

B_SCORE=$(python3 -c "print(round($B1*0.25 + $B2*0.15 + $B3*0.10 + $B4*0.10, 2))")
R_SCORE=$(python3 -c "print(round($R1*0.10 + $R2*0.05 + $R3*0.05, 2))")
C_SCORE=$(python3 -c "print(round($C1*0.05 + $C2*0.05, 2))")
S_SCORE=$(python3 -c "print(round($S1*0.05 + $S2*0.05, 2))")

python3 -c "
import json
json.dump({
    'reward': $REWARD,
    'behavioral': $B_SCORE,
    'regression': $R_SCORE,
    'config': $C_SCORE,
    'style_rubric': 0.0,
    'structural': $S_SCORE
}, open('/logs/verifier/reward.json', 'w'))
"

# Cleanup
rm -f "$ANALYSIS_FILE" /tmp/analyze.mjs

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
