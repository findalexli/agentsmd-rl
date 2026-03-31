#!/usr/bin/env bash
set +e

EARNED=0
FILE="packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx"

add() {
  local weight=$1 pass=$2
  if [ "$pass" = "1" ]; then
    EARNED=$(python3 -c "print($EARNED + $weight)")
  fi
}

########################################
# GATE: File must exist and be structurally valid
########################################
# [pr_diff] (gate): File must have balanced braces/parens AND balanced JSX tags
if ! [ -f "$FILE" ]; then
  echo "GATE FAIL: file does not exist"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0, "config": 0.0}' > /logs/verifier/reward.json
  exit 0
fi

node -e "
  const fs = require('fs');
  const src = fs.readFileSync(process.argv[1], 'utf8');
  // Check braces and parens balance
  let b = 0, p = 0;
  for (const c of src) {
    if (c === '{') b++; if (c === '}') b--;
    if (c === '(') p++; if (c === ')') p--;
  }
  if (b !== 0 || p !== 0) {
    console.error('Unbalanced braces (' + b + ') or parens (' + p + ')');
    process.exit(1);
  }
  // Check JSX Show tags balance (prevents partial line deletion exploit)
  const showOpens = (src.match(/<Show[\s>]/g) || []).length;
  const showCloses = (src.match(/<\/Show>/g) || []).length;
  if (showOpens !== showCloses) {
    console.error('Unbalanced <Show> tags: ' + showOpens + ' opens, ' + showCloses + ' closes');
    process.exit(1);
  }
" "$FILE" 2>&1
if [ $? -ne 0 ]; then
  echo "GATE FAIL: file has structural issues"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0, "config": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: syntax and JSX tag balance OK"

########################################
# BEHAVIORAL: Fail-to-pass checks (0.65)
########################################

# [pr_diff] (0.30): variant_cycle keybind reference removed from footer
if ! grep -q 'variant_cycle' "$FILE"; then
  echo "PASS: variant_cycle reference removed"
  add 0.30 1
else
  echo "FAIL: variant_cycle reference still present"
  add 0.30 0
fi

# [pr_diff] (0.20): The variant.list() conditional is removed
if ! grep -q 'variant\.list()' "$FILE"; then
  echo "PASS: variant.list() conditional removed"
  add 0.20 1
else
  echo "FAIL: variant.list() conditional still present"
  add 0.20 0
fi

# [pr_diff] (0.15): No <Show> block wrapping variant content exists anywhere in the file
# This catches partial deletions that remove key strings but leave the Show wrapper
VARIANT_SHOW=$(node -e "
  const fs = require('fs');
  const lines = fs.readFileSync(process.argv[1], 'utf8').split('\n');
  for (let i = 0; i < lines.length; i++) {
    // Look for any Show tag near variant-related content
    if (lines[i].includes('<Show') || lines[i].includes('</Show>')) {
      const window = lines.slice(Math.max(0, i-3), i+4).join(' ');
      if (window.includes('variant')) {
        process.exit(1);
      }
    }
  }
  process.exit(0);
" "$FILE" 2>/dev/null && echo "clean" || echo "dirty")
if [ "$VARIANT_SHOW" = "clean" ]; then
  echo "PASS: no Show block associated with variant content"
  add 0.15 1
else
  echo "FAIL: Show block with variant content still present"
  add 0.15 0
fi

########################################
# REGRESSION: Pass-to-pass checks (0.20)
########################################

# [pr_diff] (0.08): agent_cycle keybind still displayed in footer
if grep -q 'agent_cycle' "$FILE"; then
  echo "PASS: agent_cycle keybind still present"
  add 0.08 1
else
  echo "FAIL: agent_cycle keybind was removed (regression)"
  add 0.08 0
fi

# [pr_diff] (0.04): command_list keybind still displayed
if grep -q 'command_list' "$FILE"; then
  echo "PASS: command_list keybind still present"
  add 0.04 1
else
  echo "FAIL: command_list keybind was removed (regression)"
  add 0.04 0
fi

# [pr_diff] (0.04): Prompt export still exists
if grep -q 'export function Prompt' "$FILE"; then
  echo "PASS: Prompt component export intact"
  add 0.04 1
else
  echo "FAIL: Prompt component export missing"
  add 0.04 0
fi

# [pr_diff] (0.04): Switch/Match JSX control flow still used
if grep -q '<Switch>' "$FILE" && grep -q '<Match' "$FILE"; then
  echo "PASS: JSX control flow primitives intact"
  add 0.04 1
else
  echo "FAIL: JSX control flow primitives missing"
  add 0.04 0
fi

########################################
# STRUCTURAL: Anti-stub + integrity (0.10)
########################################

# [pr_diff] (0.05): File not stubbed out (must still have substantial content)
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 500 ]; then
  echo "PASS: file not stubbed ($LINE_COUNT lines)"
  add 0.05 1
else
  echo "FAIL: file appears stubbed ($LINE_COUNT lines)"
  add 0.05 0
fi

# [pr_diff] (0.05): JSX text/span tags balanced (catches orphaned inner tags from partial deletion)
TAG_BAL=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync(process.argv[1], 'utf8');
  // Check that common JSX tags are balanced
  for (const tag of ['text', 'span', 'Switch', 'Match', 'Show', 'For']) {
    const openRe = new RegExp('<' + tag + '[\\\\s>]', 'g');
    const closeRe = new RegExp('</' + tag + '>', 'g');
    const selfRe = new RegExp('<' + tag + '\\\\s[^>]*/>', 'g');
    const opens = (src.match(openRe) || []).length;
    const closes = (src.match(closeRe) || []).length;
    const selfs = (src.match(selfRe) || []).length;
    if ((opens - selfs) !== closes) {
      console.error(tag + ': ' + (opens - selfs) + ' opens vs ' + closes + ' closes');
      process.exit(1);
    }
  }
  process.exit(0);
" "$FILE" 2>/dev/null && echo "ok" || echo "fail")
if [ "$TAG_BAL" = "ok" ]; then
  echo "PASS: JSX tags balanced"
  add 0.05 1
else
  echo "FAIL: JSX tags unbalanced (orphaned tags from partial deletion?)"
  add 0.05 0
fi

########################################
# CONFIG-DERIVED: Agent config checks (0.05)
########################################

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13 @ 8446719b
ANY_COUNT=$(grep -c ': any\b' "$FILE" 2>/dev/null || echo "0")
if [ "$ANY_COUNT" -le 5 ]; then
  echo "PASS: no excessive bare 'any' type annotations ($ANY_COUNT found)"
  add 0.05 1
else
  echo "FAIL: excessive bare 'any' type annotations ($ANY_COUNT found)"
  add 0.05 0
fi

########################################
# Compute reward (weights sum to 1.0)
# behavioral=0.65, regression=0.20, structural=0.10, config=0.05
########################################
REWARD=$(python3 -c "print(round($EARNED, 4))")

echo ""
echo "REWARD: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD, \"behavioral\": $(python3 -c "print(round(min($EARNED, 0.65), 4))"), \"regression\": 0.20, \"structural\": 0.10, \"config\": 0.05}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
