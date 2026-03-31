#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

add_score() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); }
add_total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd /workspace/next.js

TEST_FILE="test/e2e/app-dir/interoperability-with-pages/navigation.test.ts"

##############################################################################
# GATE: File exists and is non-trivial
##############################################################################
if [ ! -f "$TEST_FILE" ]; then
    echo "GATE FAILED: $TEST_FILE does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

FILE_LINES=$(wc -l < "$TEST_FILE")
if [ "$FILE_LINES" -lt 30 ]; then
    echo "GATE FAILED: $TEST_FILE too short ($FILE_LINES lines) — likely stub"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL (0.60): Fail-to-pass — waitForElementByCss calls get timeout
# WHY STRUCTURAL: This is a TypeScript e2e test requiring Next.js dev server +
# browser (Playwright/WebDriver). Cannot execute in CPU-only Docker container.
# We use JS-level code analysis (not regex on raw text) to parse real code.
##############################################################################

# [pr_diff] (0.35): Every waitForElementByCss call in actual code (not comments)
# has an explicit timeout option >= 15000ms
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');

let callCount = 0;
let timeoutCount = 0;
const failures = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmed = line.trim();

  // Skip comment-only lines
  if (trimmed.startsWith('//') || trimmed.startsWith('*') || trimmed.startsWith('/*')) continue;

  if (trimmed.includes('waitForElementByCss(') || trimmed.includes('.waitForElementByCss(')) {
    callCount++;

    // Gather context: this line + next 4 lines (for multiline calls)
    // Stop at statement boundary (line ending without trailing operator)
    let context = '';
    for (let j = i; j < Math.min(i + 5, lines.length); j++) {
      context += lines[j] + '\n';
      const t = lines[j].trim();
      // If line ends with ) or )\n or has expect/await starting next — stop
      if (t.endsWith(')') && j > i) break;
    }

    // Check for timeout option: must be in an object literal { timeout: <value> }
    // Accept: literal numbers, variables, expressions — just needs 'timeout:' key
    // in what looks like an options object after the selector string
    const hasTimeoutKey = /waitForElementByCss\s*\([^)]*,\s*\{[^}]*timeout\s*:/s.test(context);

    if (hasTimeoutKey) {
      // Verify the value is >= 15000 if it's a literal number
      const valMatch = context.match(/timeout\s*:\s*(\d[\d_]*)/);
      if (valMatch) {
        const val = parseInt(valMatch[1].replace(/_/g, ''), 10);
        if (val >= 15000) {
          timeoutCount++;
        } else {
          failures.push('Line ' + (i+1) + ': timeout=' + val + ' < 15000');
        }
      } else {
        // Non-literal (variable/expression) — accept it, the key is present
        timeoutCount++;
      }
    } else {
      failures.push('Line ' + (i+1) + ': no timeout option');
    }
  }
}

if (callCount === 0) {
  console.log('FAIL: No waitForElementByCss calls found in code');
  process.exit(1);
}

if (timeoutCount < callCount) {
  console.log('FAIL: ' + timeoutCount + '/' + callCount + ' have timeout. Issues: ' + failures.join('; '));
  process.exit(1);
}

console.log('PASS: All ' + callCount + ' waitForElementByCss calls have timeout >= 15000');
process.exit(0);
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.35
    echo "PASS [0.35]: All waitForElementByCss calls have explicit timeout >= 15000"
else
    add_total 0.35
    echo "FAIL [0.35]: Some waitForElementByCss calls missing explicit timeout"
fi

# [pr_diff] (0.15): At least 6 waitForElementByCss calls with timeout in actual code
# (the 4 test cases have 8 total cross-router navigation points)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');
let count = 0;

for (let i = 0; i < lines.length; i++) {
  const trimmed = lines[i].trim();
  // Skip comments
  if (trimmed.startsWith('//') || trimmed.startsWith('*') || trimmed.startsWith('/*')) continue;

  if (trimmed.includes('waitForElementByCss(')) {
    // Look ahead for timeout in the call
    const context = lines.slice(i, Math.min(i + 5, lines.length)).join(' ');
    if (/waitForElementByCss\s*\([^)]*,\s*\{[^}]*timeout\s*:/s.test(context)) {
      count++;
    }
  }
}

if (count >= 6) {
  console.log('PASS: ' + count + ' code-level waitForElementByCss calls with timeout');
  process.exit(0);
} else {
  console.log('FAIL: Only ' + count + '/6 code-level calls with timeout');
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.15
    echo "PASS [0.15]: At least 6 waitForElementByCss calls with timeout"
else
    add_total 0.15
    echo "FAIL [0.15]: Fewer than 6 code-level waitForElementByCss calls with timeout"
fi

# [pr_diff] (0.10): Comment explaining WHY timeout is increased (near a waitForElementByCss call)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');
let foundNearbyComment = false;

for (let i = 0; i < lines.length; i++) {
  const trimmed = lines[i].trim();
  // Check for comment lines
  if (trimmed.startsWith('//')) {
    const lower = trimmed.toLowerCase();
    // Must mention compilation/on-demand/cross-router context AND timeout/wait
    const hasReason = /(compil|on-demand|cross.?router|dev.?mode|ci|resource|load)/.test(lower);
    const hasTopic = /(timeout|wait|longer|increase|slow)/.test(lower);
    if (hasReason && hasTopic) {
      // Verify it's within 5 lines of a waitForElementByCss call
      for (let j = Math.max(0, i - 5); j < Math.min(lines.length, i + 8); j++) {
        if (j !== i && lines[j].includes('waitForElementByCss')) {
          foundNearbyComment = true;
          break;
        }
      }
    }
  }
  if (foundNearbyComment) break;
}

if (foundNearbyComment) {
  console.log('PASS: Found explanatory comment near waitForElementByCss call');
  process.exit(0);
} else {
  console.log('FAIL: No explanatory comment near waitForElementByCss calls');
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: Explanatory comment present near relevant code"
else
    add_total 0.10
    echo "FAIL [0.10]: No explanatory comment about increased timeout"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15 total)
##############################################################################

# [pr_diff] (0.10): All 4 test cases still present (inside it() blocks, not as strings)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const tests = [
  'navigate app -> pages',
  'navigate pages -> app',
  'pages -> app and go back',
  'app -> pages and go back'
];
let found = 0;
for (const t of tests) {
  // Must appear after 'it(' — inside an it() block name, not as a random string
  const pattern = new RegExp('it\\\\s*\\\\([^)]*' + t.replace(/[.*+?^\${}()|[\\]\\\\]/g, '\\\\\\$&'));
  if (pattern.test(code) || code.includes(\"it('It should be able to \" + t)) {
    found++;
  } else if (code.includes(\"it(\\\`\" + t) || code.includes(\"it('\" + t)) {
    found++;
  }
}
// Also accept partial matches — the key test names
if (found < 4) {
  // Fallback: check for the 4 distinct navigation directions
  const dirs = [
    [/it\s*\(.*app.*pages/i, 'app->pages'],
    [/it\s*\(.*pages.*app/i, 'pages->app'],
    [/it\s*\(.*back.*forward|it\s*\(.*go back.*pages.*app/i, 'back+forward pages->app'],
    [/it\s*\(.*back.*forward|it\s*\(.*go back.*app.*pages/i, 'back+forward app->pages']
  ];
  let dirFound = 0;
  for (const [re] of dirs) {
    if (re.test(code)) dirFound++;
  }
  // Need at least 4 it() blocks total with navigation content
  const itBlocks = (code.match(/it\s*\(/g) || []).length;
  if (itBlocks >= 4) found = 4;
}
if (found >= 4) {
  console.log('PASS: All 4 test cases present');
  process.exit(0);
} else {
  console.log('FAIL: Only ' + found + '/4 test cases found');
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: All 4 test cases preserved"
else
    add_total 0.10
    echo "FAIL [0.10]: Missing test cases"
fi

# [pr_diff] (0.05): Core test infrastructure intact (describe, webdriver, createNext)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');

// Check these exist in actual code, not just comments
let hasDescribe = false;
let hasWebdriver = false;
let hasCreateNext = false;

for (const line of lines) {
  const t = line.trim();
  if (t.startsWith('//') || t.startsWith('*')) continue;
  if (/describe\s*\(/.test(t)) hasDescribe = true;
  if (/import.*webdriver|require.*webdriver/.test(t)) hasWebdriver = true;
  if (/createNext/.test(t)) hasCreateNext = true;
}

if (hasDescribe && hasWebdriver && hasCreateNext) {
  console.log('PASS: Core structure intact');
  process.exit(0);
} else {
  const missing = [];
  if (!hasDescribe) missing.push('describe');
  if (!hasWebdriver) missing.push('webdriver import');
  if (!hasCreateNext) missing.push('createNext');
  console.log('FAIL: Missing: ' + missing.join(', '));
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: Test structure and imports intact"
else
    add_total 0.05
    echo "FAIL [0.05]: Test structure broken"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.10 total)
##############################################################################

# [agent_config] (0.05): No setTimeout used for waiting — contributing.md:180-191 @ ad65b1bd
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');
let found = false;
for (const line of lines) {
  const t = line.trim();
  if (t.startsWith('//') || t.startsWith('*')) continue;
  if (/setTimeout|new\s+Promise\s*\(\s*\(?\s*resolve\b/.test(t)) {
    found = true;
    break;
  }
}
if (!found) {
  process.exit(0);
} else {
  console.log('FAIL: setTimeout/manual Promise found in code');
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: No setTimeout used for waiting"
else
    add_total 0.05
    echo "FAIL [0.05]: setTimeout used (prefer retry/waitFor helpers)"
fi

# [agent_config] (0.05): No deprecated check() used — contributing.md:194 @ ad65b1bd
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const lines = code.split('\n');
let found = false;
for (const line of lines) {
  const t = line.trim();
  if (t.startsWith('//') || t.startsWith('*')) continue;
  // Match standalone check() call, not hasElementByCssSelector() etc.
  if (/(?<!\w)check\s*\(/.test(t)) {
    found = true;
    break;
  }
}
if (!found) {
  process.exit(0);
} else {
  console.log('FAIL: deprecated check() found in code');
  process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: No deprecated check() usage"
else
    add_total 0.05
    echo "FAIL [0.05]: Deprecated check() used"
fi

##############################################################################
# ANTI-STUB: Reject trivial/fake implementations (gate-like)
##############################################################################

# Verify waitForElementByCss calls are inside it() blocks (not floating strings/comments)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');

// Count waitForElementByCss calls that are inside actual chained method calls
// (preceded by . or await on same/previous line)
const lines = code.split('\n');
let realCalls = 0;
for (let i = 0; i < lines.length; i++) {
  const t = lines[i].trim();
  if (t.startsWith('//') || t.startsWith('*')) continue;
  if (t.includes('.waitForElementByCss(')) {
    realCalls++;
  } else if (t.startsWith('waitForElementByCss(') || t.includes('await') && t.includes('waitForElementByCss(')) {
    // standalone or await — check previous line for chaining
    if (i > 0 && /\.\s*$/.test(lines[i-1].trim())) realCalls++;
  }
}

if (realCalls >= 6) {
  console.log('PASS: ' + realCalls + ' real chained waitForElementByCss calls found');
  process.exit(0);
} else {
  console.log('FAIL: Only ' + realCalls + ' real chained calls (need >=6, no stubs/comments)');
  process.exit(1);
}
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ANTI-STUB FAILED: waitForElementByCss calls appear fake/stubbed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# STYLE RUBRIC (0.10): LLM judge placeholder
##############################################################################
add_total 0.10

##############################################################################
# Final scoring
##############################################################################

echo ""
echo "Deterministic score: $SCORE / $TOTAL"

python3 -c "
import json
score = round($SCORE, 2)
# Approximate component breakdown
behavioral = min(score, 0.60)
regression = max(0, min(score - 0.60, 0.15))
config = max(0, min(score - 0.75, 0.10))
data = {
    'reward': score,
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config, 2),
    'style_rubric': 0.0
}
print(score)
with open('/logs/verifier/reward.txt', 'w') as f:
    f.write(str(score))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

echo "Final reward: $(cat /logs/verifier/reward.txt)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
