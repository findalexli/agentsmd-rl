#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
SCORE=0

APP="$REPO/packages/opencode/src/cli/cmd/tui/app.tsx"
SESSION="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
FOOTER="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx"

mkdir -p /logs/verifier

award() {
  local w=$1 name=$2
  SCORE=$(python3 -c "print(round($SCORE + $w, 4))")
  echo "PASS ($w): $name"
}

fail() {
  local w=$1 name=$2
  echo "FAIL ($w): $name"
}

# ── GATE: Files exist and aren't truncated ─────────────────────────
echo "=== GATE: File validity ==="
GATE_OK=1
for f in "$APP" "$SESSION" "$FOOTER"; do
  if [ ! -f "$f" ]; then
    echo "GATE FAIL: $f does not exist"
    GATE_OK=0
  elif [ "$(wc -c < "$f")" -lt 200 ]; then
    echo "GATE FAIL: $f is truncated (< 200 bytes)"
    GATE_OK=0
  fi
done

if [ "$GATE_OK" = "0" ]; then
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE: passed"

# ── F2P Behavioral: Cycling direction (0.30) ──────────────────────
# [pr_diff] (0.30): cycleSession must move opposite to direction sign
# Extract the cycling logic from source, build a test function, verify behavior
echo ""
echo "=== F2P Behavioral: Cycling direction ==="
CYCLE_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$SESSION', 'utf8');

  // Find the cycleSession or equivalent function containing the cycling logic
  // Look for the block that computes 'next' from findIndex and direction, with wrapping
  // We extract the raw cycling arithmetic and wrapping, then test it

  // Strategy: find lines with findIndex + direction + wrapping, extract them,
  // build a cycling function, test with multiple inputs

  // Extract the cycling block: lines from findIndex to the wrapping bounds
  const lines = src.split('\\n');
  let cycleLines = [];
  let inBlock = false;
  let foundFindIndex = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/findIndex.*direction|direction.*findIndex/.test(line) && /sessions|children/.test(lines[Math.max(0,i-3)] + lines[Math.max(0,i-2)] + lines[Math.max(0,i-1)] + line)) {
      foundFindIndex = true;
      inBlock = true;
    }
    if (inBlock) {
      cycleLines.push(line);
      // Stop after we've collected the wrapping logic (look for navigation/route/session change)
      if (cycleLines.length >= 8) break;
    }
  }

  if (!foundFindIndex) {
    console.log('0');
    process.exit(0);
  }

  // Now test the cycling behavior by building a function
  // We simulate: given currentIndex and direction, what's the next index?
  // The correct behavior after the fix: next = currentIndex - direction (with wrapping)
  // This means direction=1 -> move to LOWER index (wrap around to end)

  // Build the cycling function from extracted code
  // Replace variable references with our test harness
  const cycleBlock = cycleLines.join('\\n');

  // Test by creating a cycling function that uses the SAME arithmetic
  // Parse: is the operation findIndex_result + direction or findIndex_result - direction?
  // Then verify the wrapping

  // Extract the operator and build a test
  let testFn;
  try {
    // Build a self-contained cycling function using the source's arithmetic
    // We look for patterns like: findIndex(...) OP direction, then wrapping
    const opMatch = cycleBlock.match(/findIndex[^;]*?\\)\\s*([+\\-])\\s*direction/);
    const modMatch = cycleBlock.match(/\\(.*findIndex.*direction.*\\)\\s*%/);

    if (opMatch) {
      const op = opMatch[1];
      // Build function using extracted operator
      testFn = new Function('currentIndex', 'total', 'direction', \`
        let next = currentIndex \${op} direction;
        if (next >= total) next = 0;
        if (next < 0) next = total - 1;
        return next;
      \`);
    } else if (modMatch) {
      // Alternative: modular arithmetic approach
      // Extract and test: ((idx OP direction) % total + total) % total
      testFn = new Function('currentIndex', 'total', 'direction', \`
        \${cycleBlock.replace(/sessions\\.findIndex\\([^)]*\\)/g, 'currentIndex')
                      .replace(/sessions\\.length/g, 'total')
                      .replace(/let |const |var /g, 'let ')
                      .replace(/navigate.*$/gm, 'return next;')}
        return next;
      \`);
    }

    if (!testFn) {
      console.log('0');
      process.exit(0);
    }

    // KEY BEHAVIORAL TESTS:
    // After the fix, direction=1 should DECREASE the index (go 'up' in the list)
    // This means: from index 2, direction=1, total=5 -> index 1
    //             from index 0, direction=1, total=5 -> index 4 (wrap)
    //             from index 4, direction=-1, total=5 -> index 0 (wrap)

    const tests = [
      // [currentIndex, total, direction, expectedNext]
      [2, 5, 1, 1],    // direction=1: should go to index 1 (decreasing)
      [0, 5, 1, 4],    // direction=1 from 0: should wrap to 4
      [4, 5, -1, 0],   // direction=-1 from 4: should wrap to 0
      [3, 5, 1, 2],    // direction=1: 3->2
      [1, 5, -1, 2],   // direction=-1: 1->2
      [0, 3, 1, 2],    // smaller array: 0->2
      [2, 3, -1, 0],   // smaller array: 2->0 (wrap)
    ];

    let passed = 0;
    for (const [ci, total, dir, expected] of tests) {
      const result = testFn(ci, total, dir);
      if (result === expected) passed++;
    }

    // Must pass all test cases
    console.log(passed === tests.length ? '1' : '0');
  } catch(e) {
    console.log('0');
  }
" 2>/dev/null || echo "0")

if [ "$CYCLE_OK" = "1" ]; then
  award 0.30 "Cycling direction is correct (behavioral: 7 test cases)"
else
  fail 0.30 "Cycling direction is wrong or cycling logic not found"
fi

# ── F2P Behavioral: Subagent type extraction (0.20) ───────────────
# [pr_diff] (0.20): Footer must extract agent type from session title and compute index
# Extract the regex + sibling logic, test with mock data
echo ""
echo "=== F2P Behavioral: Subagent type extraction ==="
SUBAGENT_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FOOTER', 'utf8');

  // The footer must:
  // 1. Extract agent type from title via regex (e.g. '@coder subagent' -> 'coder')
  // 2. Compute sibling index and total from sessions with same parentID

  // Extract the regex pattern used for agent type matching
  const regexMatch = src.match(/\\.match\\(\\s*(\\/[^/]+\\/[gimsuy]*)\\s*\\)/);
  if (!regexMatch) {
    console.log('0');
    process.exit(0);
  }

  try {
    // Reconstruct the regex from source
    const regexStr = regexMatch[1];
    const re = eval(regexStr);

    // BEHAVIORAL TEST: does the regex extract agent types correctly?
    const testCases = [
      ['@coder subagent session #3', 'coder'],
      ['@explorer subagent', 'explorer'],
      ['@Researcher subagent task', null],  // uppercase might not match \\w+ but let's be lenient
      ['plain session title', null],
      ['@writer subagent', 'writer'],
    ];

    let passed = 0;
    for (const [title, expectedType] of testCases) {
      const m = title.match(re);
      if (expectedType === null) {
        // Either no match, or match is fine (not strict about non-matching)
        passed++;
      } else {
        if (m && m[1] && m[1].toLowerCase() === expectedType.toLowerCase()) {
          passed++;
        }
      }
    }

    // Must extract type from at least the clear cases
    if (passed < 4) {
      console.log('0');
      process.exit(0);
    }

    // Also verify sibling computation logic exists
    // Must filter by parentID and compute an index
    const hasParentFilter = /parentID/.test(src) && (/filter|reduce|forEach/.test(src));
    const hasIndexComputation = /findIndex|indexOf|entries/.test(src);

    // The label must NOT be the static 'Subagent session' anymore
    const noStatic = !src.includes('<b>Subagent session</b>');

    console.log(hasParentFilter && hasIndexComputation && noStatic ? '1' : '0');
  } catch(e) {
    console.log('0');
  }
" 2>/dev/null || echo "0")

if [ "$SUBAGENT_OK" = "1" ]; then
  award 0.20 "Subagent type extraction works (behavioral regex test + sibling logic)"
else
  fail 0.20 "Subagent type extraction missing or broken"
fi

# ── F2P Behavioral: Task content includes type (0.10) ─────────────
# [pr_diff] (0.10): Task component content must format with subagent_type
echo ""
echo "=== F2P Behavioral: Task content with type ==="
TASK_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$SESSION', 'utf8');

  // Find the Task component and its content memo
  // Must reference subagent_type field (the input property for the agent type)
  // Must format it into the displayed string

  // Find Task function body
  const taskMatch = src.match(/function Task[^{]*\\{([\\s\\S]*?)\\n\\}\\n/);
  if (!taskMatch) {
    console.log('0');
    process.exit(0);
  }
  const taskBody = taskMatch[1];

  // BEHAVIORAL: subagent_type must appear in the content construction
  // (it's the field name from the tool schema, so any valid fix must use it)
  const usesSubagentType = /subagent_type/.test(taskBody);

  // Must NOT be just plain 'Task' prefix anymore — type should come before description
  // Check that the content template includes more than just 'Task' + description
  const hasTypeInContent = /subagent_type.*description|type.*Task.*description|type.*description/.test(taskBody);

  // Anti-stub: Task body must have meaningful logic (content memo, navigation, etc.)
  const lines = taskBody.split('\\n').filter(l => l.trim() && !l.trim().startsWith('//'));
  const hasSubstance = lines.length > 15;

  console.log(usesSubagentType && hasSubstance ? '1' : '0');
" 2>/dev/null || echo "0")

if [ "$TASK_OK" = "1" ]; then
  award 0.10 "Task content references subagent_type"
else
  fail 0.10 "Task content missing subagent_type"
fi

# ── F2P Structural: Variant dialog wiring (0.15) ─────────────────
# [pr_diff] (0.15): variant.cycle command must open dialog, not call cycle()
echo ""
echo "=== F2P Structural: Variant dialog ==="
VARIANT_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$APP', 'utf8');

  // Must import DialogVariant (or a variant dialog component)
  const hasDialogImport = /import[^;]*DialogVariant/.test(src) ||
                          /import[^;]*[Vv]ariant[Dd]ialog/.test(src);

  // Find the variant.cycle command block
  const variantSection = src.match(/['\"]variant\\.cycle['\"][\\s\\S]{0,500}?onSelect/);
  if (!variantSection) {
    console.log('0');
    process.exit(0);
  }

  // After the onSelect, find the handler body (next ~200 chars)
  const afterOnSelect = src.substring(src.indexOf(variantSection[0]) + variantSection[0].length, src.indexOf(variantSection[0]) + variantSection[0].length + 300);

  // Must use dialog (any dialog method: replace, open, show, push, set)
  const usesDialog = /dialog\\.\\w+|setDialog|openDialog|showDialog/.test(afterOnSelect);

  // Must NOT directly call cycle()
  const callsCycle = /\\.cycle\\(\\)/.test(afterOnSelect);

  // Anti-stub: App function must be substantial
  const appMatch = src.match(/function App[^{]*\\{/);
  const hasSubstance = appMatch && src.length > 5000;

  console.log(hasDialogImport && usesDialog && !callsCycle && hasSubstance ? '1' : '0');
" 2>/dev/null || echo "0")

if [ "$VARIANT_OK" = "1" ]; then
  award 0.15 "Variant command opens dialog instead of cycling"
else
  fail 0.15 "Variant command doesn't open dialog or still calls cycle()"
fi

# ── P2P: Core exports intact (0.10) ───────────────────────────────
# [pr_diff] (0.10): Key exports and components must still exist
echo ""
echo "=== P2P: Core structure ==="
P2P_PASS=0
P2P_TOTAL=4

# Session export
grep -q "export function Session" "$SESSION" 2>/dev/null && P2P_PASS=$((P2P_PASS + 1)) || echo "  FAIL: Session export missing"

# SubagentFooter export
grep -q "export function SubagentFooter" "$FOOTER" 2>/dev/null && P2P_PASS=$((P2P_PASS + 1)) || echo "  FAIL: SubagentFooter export missing"

# App function
grep -q "function App(" "$APP" 2>/dev/null && P2P_PASS=$((P2P_PASS + 1)) || echo "  FAIL: App function missing"

# InlineTool (adjacent to removed ToolTitle, must survive)
grep -q "function InlineTool(" "$SESSION" 2>/dev/null && P2P_PASS=$((P2P_PASS + 1)) || echo "  FAIL: InlineTool missing"

if [ "$P2P_PASS" = "$P2P_TOTAL" ]; then
  award 0.10 "Core exports intact"
else
  # Partial credit
  PARTIAL=$(python3 -c "print(round(0.10 * $P2P_PASS / $P2P_TOTAL, 4))")
  award "$PARTIAL" "Core exports partially intact ($P2P_PASS/$P2P_TOTAL)"
fi

# ── Structural: Dead code cleanup (0.05) ──────────────────────────
# [pr_diff] (0.05): Unused ToolTitle function should be removed
echo ""
echo "=== Structural: Dead code ==="
if ! grep -q "function ToolTitle(" "$SESSION" 2>/dev/null; then
  award 0.05 "Unused ToolTitle removed"
else
  fail 0.05 "Unused ToolTitle still present"
fi

# ── Config: Functional array methods (0.10) ───────────────────────
# [agent_config] (0.10): "Prefer functional array methods" — AGENTS.md:23
echo ""
echo "=== Config: Functional style ==="
CONFIG_OK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FOOTER', 'utf8');

  // New code in footer must use functional methods for sibling computation
  // Accept: filter, reduce, flatMap, map + findIndex, indexOf, entries
  const hasFunctional = (/\\.filter\\(/.test(src) || /\\.reduce\\(/.test(src) || /\\.flatMap\\(/.test(src));
  const hasIndex = (/\\.findIndex\\(/.test(src) || /\\.indexOf\\(/.test(src) || /\\.entries\\(/.test(src));

  // Must NOT use C-style for loops for the sibling computation
  // (allow for loops elsewhere, just not in new sibling logic)
  // Check: no 'for (let/var i' near 'sibling' or 'parentID'
  const hasImperativeLoop = /for\\s*\\(\\s*(let|var)\\s+\\w+[\\s\\S]{0,100}parentID/.test(src);

  console.log(hasFunctional && hasIndex && !hasImperativeLoop ? '1' : '0');
" 2>/dev/null || echo "0")

if [ "$CONFIG_OK" = "1" ]; then
  award 0.10 "Uses functional array methods per AGENTS.md:23"
else
  fail 0.10 "Does not use functional array methods"
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "=== TOTAL ==="
echo "Score: $SCORE / 1.00"
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('$SCORE')
# Behavioral: direction(0.30) + subagent(0.20) + task(0.10) = 0.60
# Structural: variant(0.15) + p2p(0.10) + dead_code(0.05) + config(0.10) = 0.40
behavioral = min(score, 0.60)
structural = max(score - 0.60, 0)
data = {
  'reward': score,
  'behavioral': round(behavioral, 4),
  'regression': round(min(structural, 0.15), 4),
  'config': round(min(max(structural - 0.15, 0), 0.10), 4),
  'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
  json.dump(data, f)
"

# Also write to /workspace for compatibility
cp /logs/verifier/reward.txt /logs/verifier/reward.txt 2>/dev/null || true
cp /logs/verifier/reward.json /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
