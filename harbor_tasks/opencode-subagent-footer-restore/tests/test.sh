#!/usr/bin/env bash
set +e

REPO=/workspace/opencode
REWARD=0
TOTAL=0

pass() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }
add()  { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

FOOTER="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx"
SESSION="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
DIALOG_MODEL="$REPO/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx"
DIALOG_VARIANT="$REPO/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx"

# ============================================================
# GATE: All modified TSX files must have balanced braces
# ============================================================
echo "=== GATE: Syntax check ==="
GATE_PASS=true
for f in "$FOOTER" "$SESSION" "$DIALOG_MODEL" "$DIALOG_VARIANT"; do
  if [ -f "$f" ]; then
    node -e "
      const src = require('fs').readFileSync('$f', 'utf8');
      let depth = 0;
      for (const ch of src) {
        if (ch === '{') depth++;
        if (ch === '}') depth--;
        if (depth < 0) process.exit(1);
      }
      if (depth !== 0) process.exit(1);
    " 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "GATE FAIL: $f has unbalanced braces"
      GATE_PASS=false
    fi
  fi
done

if [ "$GATE_PASS" != "true" ]; then
  echo "GATE FAILED — aborting"
  echo "0.0" > /logs/verifier/reward.txt
  python3 -c "import json; json.dump({'reward': 0.0}, open('/logs/verifier/reward.json', 'w'))"
  exit 0
fi
echo "GATE passed"

# ============================================================
# Helper: strip comments from TSX source for robust matching
# ============================================================
# We use node to strip single-line and multi-line comments, then
# test the cleaned source. This prevents comment-injection gaming.
strip_comments() {
  node -e "
    const src = require('fs').readFileSync('$1', 'utf8');
    // Remove single-line comments
    let cleaned = src.replace(/\/\/.*$/gm, '');
    // Remove multi-line comments
    cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, '');
    process.stdout.write(cleaned);
  " 2>/dev/null
}

# ============================================================
# Fail-to-pass behavioral tests (0.65 total)
# ============================================================
echo ""
echo "=== Fail-to-pass behavioral tests ==="

# [pr_diff] (0.25): SubagentFooter exports a function that returns JSX with
# navigation elements (Parent/Prev/Next buttons as actual rendered content)
W=0.25; add $W
if [ -f "$FOOTER" ]; then
  RESULT=$(node -e "
    const src = require('fs').readFileSync('$FOOTER', 'utf8');
    // Strip comments to prevent gaming via comment injection
    let code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    // Must export a SubagentFooter function
    if (!/export\s+function\s+SubagentFooter/.test(code)) {
      console.log('NO_EXPORT'); process.exit(0);
    }

    // Must have a return statement with JSX (< character inside parens)
    if (!/return\s*\([\s\S]*?</.test(code)) {
      console.log('NO_JSX_RETURN'); process.exit(0);
    }

    // Navigation: must have all three action strings in non-comment code
    // These are the command triggers, not display text — any valid impl needs them
    const hasParentNav = /session[.\[]\s*parent|session_parent/.test(code);
    const hasPrevNav = /session[.\[].*previous|child.*cycle.*reverse|session_child_cycle_reverse/.test(code);
    const hasNextNav = /session[.\[].*next|child.*cycle[^_]|session_child_cycle[^_]/.test(code);

    if (!hasParentNav || !hasPrevNav || !hasNextNav) {
      console.log('MISSING_NAV'); process.exit(0);
    }

    console.log('OK');
  " 2>/dev/null)
  if [ "$RESULT" = "OK" ]; then
    pass $W "SubagentFooter exports function with JSX navigation controls"
  else
    fail $W "SubagentFooter missing export/JSX/navigation ($RESULT)"
  fi
else
  fail $W "SubagentFooter file does not exist"
fi

# [pr_diff] (0.15): SubagentFooter has token usage computation logic
# Must have actual arithmetic on tokens (not just the word "tokens" in a comment)
W=0.15; add $W
if [ -f "$FOOTER" ]; then
  RESULT=$(node -e "
    const src = require('fs').readFileSync('$FOOTER', 'utf8');
    let code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    // Must reference token counts with property access (actual logic, not keyword)
    const hasTokenAccess = /tokens\s*\.\s*(input|output|reasoning|cache)/.test(code)
                        || /tokens\s*\[/.test(code);

    // Must have cost computation (reduce, sum, or accumulator pattern on cost)
    const hasCostLogic = /\.cost\b/.test(code) && (/\.reduce\s*\(/.test(code) || /\+.*cost|cost.*\+/.test(code));

    // Must format the values for display (Intl, toFixed, Locale, template literal)
    const hasFormatting = /Intl\.NumberFormat|toFixed|Locale\.|format\s*\(/.test(code);

    if (hasTokenAccess && hasCostLogic && hasFormatting) {
      console.log('OK');
    } else {
      console.log('MISSING:' +
        (!hasTokenAccess ? ' token_access' : '') +
        (!hasCostLogic ? ' cost_logic' : '') +
        (!hasFormatting ? ' formatting' : ''));
    }
  " 2>/dev/null)
  if [ "$RESULT" = "OK" ]; then
    pass $W "SubagentFooter has token/cost computation logic"
  else
    fail $W "SubagentFooter missing token/cost logic ($RESULT)"
  fi
else
  fail $W "SubagentFooter file does not exist"
fi

# [pr_diff] (0.15): Session index.tsx imports SubagentFooter from the footer file
# and renders it conditionally when parentID is present
W=0.15; add $W
RESULT=$(node -e "
  const src = require('fs').readFileSync('$SESSION', 'utf8');
  let code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

  // Must import SubagentFooter (from any relative path containing 'subagent-footer')
  const hasImport = /import\s*\{[^}]*SubagentFooter[^}]*\}\s*from\s*['\"].*subagent-footer/.test(code);

  // Must render <SubagentFooter in the JSX
  const hasRender = /<SubagentFooter/.test(code);

  // Must gate on parentID (Show when={...parentID...} or conditional)
  const hasParentGate = /parentID/.test(code);

  if (hasImport && hasRender && hasParentGate) {
    console.log('OK');
  } else {
    console.log('MISSING:' +
      (!hasImport ? ' import' : '') +
      (!hasRender ? ' render' : '') +
      (!hasParentGate ? ' parentID_gate' : ''));
  }
" 2>/dev/null)
if [ "$RESULT" = "OK" ]; then
  pass $W "Session imports and renders SubagentFooter with parentID gating"
else
  fail $W "Session missing SubagentFooter integration ($RESULT)"
fi

# [pr_diff] (0.05): dialog-model.tsx uses early return instead of else block
# The buggy code has "} else {" in onSelect; any correct fix removes it
W=0.05; add $W
CLEANED=$(strip_comments "$DIALOG_MODEL")
if echo "$CLEANED" | grep -q "} else {"; then
  fail $W "dialog-model.tsx still uses else block"
else
  pass $W "dialog-model.tsx else block removed"
fi

# [pr_diff] (0.05): dialog-variant.tsx no longer imports useSync (unused)
W=0.05; add $W
CLEANED=$(strip_comments "$DIALOG_VARIANT")
if echo "$CLEANED" | grep -qE 'import\s*\{[^}]*useSync[^}]*\}\s*from'; then
  fail $W "dialog-variant.tsx still imports unused useSync"
else
  pass $W "dialog-variant.tsx useSync import removed"
fi

# ============================================================
# Pass-to-pass regression tests (0.10 total)
# ============================================================
echo ""
echo "=== Pass-to-pass regression tests ==="

# [pr_diff] (0.05): dialog-model.tsx still exports DialogModel function
W=0.05; add $W
if grep -q "export function DialogModel" "$DIALOG_MODEL"; then
  pass $W "DialogModel export preserved"
else
  fail $W "DialogModel export missing"
fi

# [pr_diff] (0.05): dialog-variant.tsx still exports DialogVariant function
W=0.05; add $W
if grep -q "export function DialogVariant" "$DIALOG_VARIANT"; then
  pass $W "DialogVariant export preserved"
else
  fail $W "DialogVariant export missing"
fi

# ============================================================
# Config-derived checks (0.15 total)
# ============================================================
echo ""
echo "=== Config-derived checks ==="

# [agent_config] (0.05): "Avoid else statements. Prefer early returns." — AGENTS.md:84 @ 41b0d03
W=0.05; add $W
ELSE_COUNT=0
for f in "$DIALOG_MODEL" "$FOOTER"; do
  if [ -f "$f" ]; then
    CLEANED=$(strip_comments "$f")
    COUNT=$(echo "$CLEANED" | grep -c "} else {" 2>/dev/null || true)
    ELSE_COUNT=$((ELSE_COUNT + COUNT))
  fi
done
if [ "$ELSE_COUNT" -eq 0 ]; then
  pass $W "No else blocks in modified files (AGENTS.md:84)"
else
  fail $W "Found $ELSE_COUNT else blocks (AGENTS.md:84)"
fi

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13 @ 41b0d03
W=0.05; add $W
ANY_COUNT=0
if [ -f "$FOOTER" ]; then
  CLEANED=$(strip_comments "$FOOTER")
  ANY_COUNT=$(echo "$CLEANED" | grep -cE "(:\s*any\b|as\s+any\b)" 2>/dev/null || true)
fi
if [ "$ANY_COUNT" -eq 0 ]; then
  pass $W "No 'any' type in SubagentFooter (AGENTS.md:13)"
else
  fail $W "Found $ANY_COUNT uses of 'any' type (AGENTS.md:13)"
fi

# [pr_diff] (0.05): Anti-stub — SubagentFooter function body has meaningful content
# Must have ≥15 non-blank non-comment lines inside the function body
W=0.05; add $W
if [ -f "$FOOTER" ]; then
  MEANINGFUL=$(node -e "
    const src = require('fs').readFileSync('$FOOTER', 'utf8');
    // Strip comments
    let code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
    // Count non-blank lines inside the exported function
    const match = code.match(/export\s+function\s+SubagentFooter[\s\S]*?\n([\s\S]*)/);
    if (!match) { console.log(0); process.exit(0); }
    const lines = match[1].split('\n').filter(l => l.trim().length > 0 && l.trim() !== '}');
    console.log(lines.length);
  " 2>/dev/null)
  if [ "${MEANINGFUL:-0}" -gt 15 ]; then
    pass $W "SubagentFooter has substantial body ($MEANINGFUL meaningful lines)"
  else
    fail $W "SubagentFooter body too small ($MEANINGFUL lines, need >15)"
  fi
else
  fail $W "SubagentFooter file does not exist"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "=== SUMMARY ==="
echo "Score: $REWARD / $TOTAL"

echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
r = $REWARD
data = {
    'reward': r,
    'behavioral': round(min(r, 0.65), 4),
    'regression': round(min(max(r - 0.65, 0), 0.10), 4),
    'config': round(min(max(r - 0.75, 0), 0.15), 4)
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
