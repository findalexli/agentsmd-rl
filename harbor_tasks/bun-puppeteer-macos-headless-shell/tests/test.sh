#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun

TS_FILE="test/integration/next-pages/test/dev-server-puppeteer.ts"

##############################################################################
# GATE: File exists and is valid
##############################################################################
# [pr_diff] (gate): Target file must exist
if [ ! -s "$TS_FILE" ]; then
    echo "GATE FAILED: $TS_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass via Node.js evaluation (0.65 total)
#
# We strip minimal TS syntax and evaluate the actual JS logic with mocked
# process.platform to test real conditional behavior.
##############################################################################

# Helper: strip TS type annotations so Node can evaluate the file's logic
# We extract the launchOptions block and evaluate it with controlled inputs.
mkdir -p /tmp/test_harness

# [pr_diff] (0.25): macOS must use headless "shell" mode (not true)
# The bug: headless: true uses the full Chrome .app bundle which triggers Gatekeeper.
# The fix: use "shell" mode on macOS. We evaluate the actual expression.
add_total 0.25
HEADLESS_RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');

// Extract the headless property value expression
const headlessMatch = src.match(/headless\s*:\s*(.+?)(?:,|\n)/);
if (!headlessMatch) { console.log('NO_HEADLESS'); process.exit(0); }

const expr = headlessMatch[1].trim();

// Evaluate with process.platform = 'darwin' (macOS)
try {
  const darwinVal = new Function('process', 'isMacOS', 'return ' + expr)(
    { platform: 'darwin' }, true
  );
  // Evaluate with process.platform = 'linux'
  const linuxVal = new Function('process', 'isMacOS', 'return ' + expr)(
    { platform: 'linux' }, false
  );

  // On macOS: must be 'shell' (or 'new' — both use chrome-headless-shell)
  // On linux: must be true (boolean)
  const macOK = (darwinVal === 'shell' || darwinVal === 'new');
  const linuxOK = (linuxVal === true);
  console.log(macOK && linuxOK ? 'PASS' : (macOK ? 'PARTIAL' : 'FAIL'));
} catch(e) {
  // Expression may reference variables we don't have — try simpler eval
  // Check if the expression itself contains platform-conditional logic with 'shell'
  if (/darwin|mac/i.test(expr) && /['\"]shell['\"]/.test(expr)) {
    console.log('PASS');
  } else {
    console.log('FAIL');
  }
}
" 2>/dev/null || echo "FAIL")
if [ "$HEADLESS_RESULT" = "PASS" ]; then
    add_score 0.25
    echo "PASS [0.25]: headless='shell' on macOS, true on Linux (behavioral eval)"
elif [ "$HEADLESS_RESULT" = "PARTIAL" ]; then
    add_score 0.15
    echo "PARTIAL [0.15]: headless='shell' on macOS but Linux mode unclear"
else
    echo "FAIL [0.25]: headless mode not platform-conditional"
fi

# [pr_diff] (0.20): executablePath must be excluded on macOS
# The bug: system browser path points to full Chrome, not chrome-headless-shell.
# We evaluate the spread expression with mocked values.
add_total 0.20
EXEC_RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');

// Look for the spread that sets executablePath
// Common patterns:
//   ...(!isMacOS && browserPath ? { executablePath: browserPath } : {})
//   ...(process.platform !== 'darwin' && browserPath ? { executablePath: ... } : {})
// Or imperative: if (!isMacOS) launchOptions.executablePath = browserPath;

// Strategy: check if executablePath can appear when platform is darwin
// Build a minimal evaluation context

// Find all lines mentioning executablePath
const lines = src.split('\n');
const epLines = lines.filter(l => /executablePath/.test(l));

if (epLines.length === 0) {
  // executablePath removed entirely — acceptable fix
  console.log('PASS');
  process.exit(0);
}

// Try to evaluate the spread expression
const spreadMatch = src.match(/\.\.\.(\(.+?executablePath.+?\))/s);
if (spreadMatch) {
  const expr = spreadMatch[1];
  try {
    // Eval with macOS + browserPath set
    const macResult = new Function('process', 'isMacOS', 'browserPath',
      'return ' + expr
    )({ platform: 'darwin' }, true, '/usr/bin/chrome');

    const linuxResult = new Function('process', 'isMacOS', 'browserPath',
      'return ' + expr
    )({ platform: 'linux' }, false, '/usr/bin/chrome');

    const macHasExec = macResult && macResult.executablePath;
    const linuxHasExec = linuxResult && linuxResult.executablePath;

    // macOS must NOT have executablePath, Linux SHOULD have it
    console.log(!macHasExec && linuxHasExec ? 'PASS' : (!macHasExec ? 'PARTIAL' : 'FAIL'));
  } catch(e) {
    // Fallback: check if the expression has a platform guard
    if (/(!isMacOS|!.*darwin|platform\s*!==?\s*['\"]darwin)/.test(expr)) {
      console.log('PASS');
    } else {
      console.log('FAIL');
    }
  }
} else {
  // Imperative style — check for platform guard around executablePath assignment
  const epContext = epLines.join('\n');
  if (/(!isMacOS|!.*darwin|platform\s*!==?\s*['\"]darwin)/.test(epContext)) {
    console.log('PASS');
  } else if (/if\s*\(/.test(epContext) && /(darwin|mac)/i.test(src.substring(
    Math.max(0, src.indexOf(epContext) - 200), src.indexOf(epContext) + epContext.length
  ))) {
    console.log('PASS');
  } else {
    console.log('FAIL');
  }
}
" 2>/dev/null || echo "FAIL")
if [ "$EXEC_RESULT" = "PASS" ]; then
    add_score 0.20
    echo "PASS [0.20]: executablePath excluded on macOS (behavioral eval)"
elif [ "$EXEC_RESULT" = "PARTIAL" ]; then
    add_score 0.10
    echo "PARTIAL [0.10]: executablePath excluded on macOS but not passed on Linux"
else
    echo "FAIL [0.20]: executablePath not guarded for macOS"
fi

# [pr_diff] (0.10): timeout and protocolTimeout must be finite (>0)
# The bug: timeout: 0 causes tests to hang indefinitely on launch failure.
add_total 0.10
TIMEOUT_RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');

// Extract timeout values - try to evaluate them as JS expressions
const timeoutMatch = src.match(/timeout\s*:\s*([^,\n}]+)/);
const protoMatch = src.match(/protocolTimeout\s*:\s*([^,\n}]+)/);

let ok = true;

if (timeoutMatch) {
  try {
    const val = eval(timeoutMatch[1].trim());
    if (typeof val === 'number' && val <= 0) ok = false;
  } catch(e) {
    // Expression we can't eval — check it's not literal 0
    if (/^\s*0\s*$/.test(timeoutMatch[1])) ok = false;
  }
}

if (protoMatch) {
  try {
    const val = eval(protoMatch[1].trim());
    if (typeof val === 'number' && val <= 0) ok = false;
  } catch(e) {
    if (/^\s*0\s*$/.test(protoMatch[1])) ok = false;
  }
}

// If neither exists, Puppeteer defaults are finite — acceptable
console.log(ok ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$TIMEOUT_RESULT" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: launch timeouts are finite"
else
    echo "FAIL [0.10]: timeout and/or protocolTimeout still 0 (infinite)"
fi

# [pr_diff] (0.10): retry delay must be > 1000ms
# The bug: 1s delay insufficient for transient macOS launch issues.
add_total 0.10
RETRY_RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');

// Find setTimeout or sleep delay in the catch/retry block
// Look for the retry section (after 'catch')
const catchIdx = src.lastIndexOf('catch');
if (catchIdx === -1) { console.log('PASS'); process.exit(0); } // restructured

const retrySrc = src.substring(catchIdx);

// Find delay values — setTimeout(r, DELAY) or sleep(DELAY) or similar
const delayPatterns = [
  /setTimeout\s*\(\s*\w+\s*,\s*([^)]+)\)/,
  /sleep\s*\(\s*([^)]+)\)/,
  /delay\s*\(\s*([^)]+)\)/,
  /new Promise.+?(\d[\d_]*)\s*\)/,
];

for (const pat of delayPatterns) {
  const m = retrySrc.match(pat);
  if (m) {
    try {
      const val = eval(m[1].trim());
      console.log(val > 1000 ? 'PASS' : 'FAIL');
      process.exit(0);
    } catch(e) {}
  }
}

// If we can't find a delay pattern, check if retry logic was restructured
// Accept any non-trivial delay mechanism
console.log('NEUTRAL');
" 2>/dev/null || echo "FAIL")
if [ "$RETRY_RESULT" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: retry delay increased beyond 1 second"
elif [ "$RETRY_RESULT" = "NEUTRAL" ]; then
    add_score 0.05
    echo "PARTIAL [0.05]: retry logic restructured, delay not verifiable"
else
    echo "FAIL [0.10]: retry delay still 1 second or less"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.05): File must still have browser retry loop
add_total 0.05
RETRY_LOOP=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
// Must have a loop with multiple attempts and catch/retry pattern
const hasLoop = /for\s*\(.*attempt/.test(src) || /while\s*\(.*attempt/.test(src) ||
                /retry|attempts?\s*[<>=]/i.test(src);
const hasCatch = /catch\s*\(/.test(src);
const hasLaunch = /launch\s*\(/.test(src);
console.log(hasLoop && hasCatch && hasLaunch ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$RETRY_LOOP" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: browser retry loop preserved"
else
    echo "FAIL [0.05]: browser retry loop missing"
fi

# [pr_diff] (0.05): Core Puppeteer launch args preserved
add_total 0.05
CORE_ARGS=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
const required = ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'];
const ok = required.every(arg => src.includes(arg));
console.log(ok ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$CORE_ARGS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: core Puppeteer launch args preserved"
else
    echo "FAIL [0.05]: core Puppeteer launch args missing"
fi

# [pr_diff] (0.05): Puppeteer import and page navigation preserved
add_total 0.05
STRUCTURE=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
const hasImport = /require\s*\(\s*['\"]puppeteer['\"]/.test(src) || /from\s+['\"]puppeteer['\"]/.test(src);
const hasGoto = /goto\s*\(/.test(src) || /navigate/.test(src);
const hasBrowser = /browser\s*[:=]/.test(src);
console.log(hasImport && hasBrowser ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$STRUCTURE" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Puppeteer import and browser usage preserved"
else
    echo "FAIL [0.05]: Puppeteer import or browser usage missing"
fi

##############################################################################
# CONFIG-DERIVED (0.10)
##############################################################################

# [agent_config] (0.05): chmod for downloaded browser binaries
# macOS cache binaries may lack execute perms — must chmod them.
# Source: bun CLAUDE.md context on macOS CI binary permissions
add_total 0.05
CHMOD_CHECK=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
// Must actually execute chmod (not just mention it in a comment)
// Look for chmod in a string passed to exec, or fs.chmod call
const inExec = /exec(?:Sync)?\s*\(\s*[\`'\"].*chmod/.test(src);
const inFs = /chmod(?:Sync)?\s*\(/.test(src);
// Exclude pure comments — require chmod inside a string or function call
const lines = src.split('\n');
const codeLines = lines.filter(l => !/^\s*\/\//.test(l) && !/^\s*\*/.test(l));
const codeSrc = codeLines.join('\n');
const inCode = /chmod/.test(codeSrc);
console.log(inCode ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$CHMOD_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: chmod for cached browser binaries"
else
    echo "FAIL [0.05]: no chmod for cached browser binaries"
fi

# [agent_config] (0.05): xattr quarantine removal present
# Source: bun CLAUDE.md — macOS quarantines downloaded binaries
add_total 0.05
XATTR_CHECK=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
// Must have xattr removal in actual code (not comments)
const lines = src.split('\n');
const codeLines = lines.filter(l => !/^\s*\/\//.test(l) && !/^\s*\*/.test(l));
const codeSrc = codeLines.join('\n');
const hasXattr = /xattr/.test(codeSrc) && /quarantine/.test(codeSrc);
console.log(hasXattr ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$XATTR_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: xattr quarantine removal preserved"
else
    echo "FAIL [0.05]: xattr quarantine removal missing"
fi

##############################################################################
# ANTI-STUB (0.10)
##############################################################################

# [pr_diff] (0.05): File must be substantive (not a stub)
add_total 0.05
ANTI_STUB=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
const lines = src.split('\n');
// Count non-empty, non-comment lines
const codeLines = lines.filter(l => l.trim() && !/^\s*\/\//.test(l) && !/^\s*\*/.test(l) && !/^\s*\/\*/.test(l));
console.log(codeLines.length > 40 ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$ANTI_STUB" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: file is substantive (not a stub)"
else
    echo "FAIL [0.05]: file appears to be a stub"
fi

# [pr_diff] (0.05): Must have actual Puppeteer launch call with options
add_total 0.05
LAUNCH_CALL=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
// Must have launch() call with launchOptions or inline config
const hasLaunch = /launch\s*\(\s*(?:launchOptions|\{)/.test(src);
// Must define browser or headless in options (not just as a string)
const hasConfig = /headless\s*:/.test(src) && /args\s*:\s*\[/.test(src);
console.log(hasLaunch && hasConfig ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "FAIL")
if [ "$LAUNCH_CALL" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Puppeteer launch call with proper options"
else
    echo "FAIL [0.05]: missing proper Puppeteer launch call"
fi

##############################################################################
# FINAL SCORING
##############################################################################

REWARD=$(python3 -c "print(round($SCORE, 4))")

echo ""
echo "Total: $SCORE / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

# Build reward.json with proper breakdown
python3 -c "
import json
score = $SCORE
# Behavioral checks: headless(0.25) + execPath(0.20) + timeout(0.10) + retry(0.10) = 0.65
# Regression: retry_loop(0.05) + core_args(0.05) + structure(0.05) = 0.15
# Config: chmod(0.05) + xattr(0.05) = 0.10
# Anti-stub: substance(0.05) + launch_call(0.05) = 0.10
behavioral = min(score, 0.65)
regression = min(max(score - 0.65, 0), 0.15)
config = min(max(score - 0.80, 0), 0.10)
style = 0.0
json.dump({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': round(style, 4)
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
