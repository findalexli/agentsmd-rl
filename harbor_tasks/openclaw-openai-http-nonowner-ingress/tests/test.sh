#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
TARGET="${REPO}/src/gateway/openai-http.ts"
SCORE=0

pass() { SCORE=$(python3 -c "print(${SCORE} + ${1})"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE: File exists and is parseable ─────────────────────────────
if [ ! -f "$TARGET" ]; then
  echo "GATE FAIL: $TARGET does not exist"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

if ! node -e "
  const fs = require('fs');
  const code = fs.readFileSync('${TARGET}', 'utf8');
  try { new Function(code); } catch(e) {
    if (e instanceof SyntaxError && !e.message.includes('import') && !e.message.includes('export'))
      process.exit(1);
  }
" 2>/dev/null; then
  echo "GATE FAIL: ${TARGET} has syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: TypeScript syntax OK"

# ═══════════════════════════════════════════════════════════════════
# Helper: Node.js script that strips comments, extracts function body,
# and evaluates the senderIsOwner property value in the return object.
# This is comment-resistant and works with any valid TypeScript syntax.
# ═══════════════════════════════════════════════════════════════════

# ── F2P Behavioral (0.40): senderIsOwner evaluates to false ───────
# [pr_diff] (0.40): senderIsOwner must be false in buildAgentCommandInput return object
F2P_MAIN=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');

  // Strip comments (single-line and multi-line) to prevent comment injection
  code = code.replace(/\/\/.*$/gm, '');
  code = code.replace(/\/\*[\s\S]*?\*\//g, '');

  // Find buildAgentCommandInput function body via brace matching
  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }

  // Skip past the parameter list parentheses to avoid capturing type annotations
  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }

  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        // Find senderIsOwner: <value> in the function body
        // Accept literal false, or a variable/expression that is not literal true
        const literalMatch = body.match(/senderIsOwner\s*:\s*(true|false)\b/);
        if (literalMatch) { console.log(literalMatch[1]); process.exit(0); }
        // Check for variable assignment: senderIsOwner: <identifier>
        const varMatch = body.match(/senderIsOwner\s*:\s*([a-zA-Z_]\w*)/);
        if (varMatch) {
          // Try to find the variable's value in the function or file scope
          const varName = varMatch[1];
          const varDecl = code.match(new RegExp('(?:const|let|var)\\\\s+' + varName + '\\\\s*[:=]\\\\s*(true|false)\\\\b'));
          if (varDecl) { console.log(varDecl[1]); } else { console.log('INDIRECT'); }
        } else {
          console.log('NOT_FOUND');
        }
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$F2P_MAIN" = "false" ] || [ "$F2P_MAIN" = "INDIRECT" ]; then
  pass 0.40 "senderIsOwner is false in buildAgentCommandInput (comment-stripped AST)"
else
  fail 0.40 "senderIsOwner is not false in buildAgentCommandInput (got: $F2P_MAIN)"
fi

# ── F2P Behavioral (0.20): senderIsOwner must NOT be true ─────────
# [pr_diff] (0.20): No residual senderIsOwner: true in the function body
F2P_NEG=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');
  code = code.replace(/\/\/.*$/gm, '');
  code = code.replace(/\/\*[\s\S]*?\*\//g, '');

  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }

  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }

  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        // Check all occurrences of senderIsOwner — none should be true
        const matches = [...body.matchAll(/senderIsOwner\s*:\s*(true|false)\b/g)];
        const hasTrue = matches.some(m => m[1] === 'true');
        console.log(hasTrue ? 'HAS_TRUE' : 'CLEAN');
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$F2P_NEG" = "CLEAN" ]; then
  pass 0.20 "No senderIsOwner: true in buildAgentCommandInput (comment-stripped)"
else
  fail 0.20 "senderIsOwner: true still present in buildAgentCommandInput"
fi

# ── P2P Regression (0.05): buildAgentCommandInput function exists ──
# [pr_diff] (0.05): Function must not be deleted or renamed
if node -e "
  const code = require('fs').readFileSync('${TARGET}', 'utf8');
  const stripped = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  if (stripped.includes('function buildAgentCommandInput')) process.exit(0);
  process.exit(1);
" 2>/dev/null; then
  pass 0.05 "buildAgentCommandInput function exists"
else
  fail 0.05 "buildAgentCommandInput function missing"
fi

# ── P2P Regression (0.05): handleOpenAiHttpRequest export exists ───
# [pr_diff] (0.05): Export must not be removed
if node -e "
  const code = require('fs').readFileSync('${TARGET}', 'utf8');
  const stripped = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  if (/export\b.*handleOpenAiHttpRequest/.test(stripped)) process.exit(0);
  process.exit(1);
" 2>/dev/null; then
  pass 0.05 "handleOpenAiHttpRequest export exists"
else
  fail 0.05 "handleOpenAiHttpRequest export missing"
fi

# ── P2P Regression (0.05): allowModelOverride remains true ─────────
# [pr_diff] (0.05): Adjacent field must not be changed
P2P_AMO=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');
  code = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }
  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }
  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        const m = body.match(/allowModelOverride\s*:\s*(true|false)\b/);
        console.log(m ? m[1] : 'NOT_FOUND');
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$P2P_AMO" = "true" ]; then
  pass 0.05 "allowModelOverride remains true"
else
  fail 0.05 "allowModelOverride changed or missing (got: $P2P_AMO)"
fi

# ── P2P Regression (0.10): deliver and bestEffortDeliver remain false
# [pr_diff] (0.10): Other boolean fields in the return object must not regress
P2P_FIELDS=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');
  code = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }
  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }
  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        const deliver = body.match(/\bdeliver\s*:\s*(true|false)\b/);
        const bestEffort = body.match(/bestEffortDeliver\s*:\s*(true|false)\b/);
        const ok = deliver && deliver[1] === 'false' && bestEffort && bestEffort[1] === 'false';
        console.log(ok ? 'OK' : 'CHANGED');
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$P2P_FIELDS" = "OK" ]; then
  pass 0.10 "deliver and bestEffortDeliver remain false"
else
  fail 0.10 "deliver/bestEffortDeliver changed or missing"
fi

# ── P2P Regression (0.05): messageChannel field still present ──────
# [pr_diff] (0.05): messageChannel must still be wired through
P2P_MC=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');
  code = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }
  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }
  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        console.log(/messageChannel/.test(body) ? 'OK' : 'MISSING');
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$P2P_MC" = "OK" ]; then
  pass 0.05 "messageChannel field still present in return object"
else
  fail 0.05 "messageChannel field missing from return object"
fi

# ── Anti-stub (0.05): Function body has substantial content ────────
# [pr_diff] (0.05): Function must not be gutted to a stub
ANTI_STUB=$(node -e "
  const fs = require('fs');
  let code = fs.readFileSync('${TARGET}', 'utf8');
  code = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  const fnStart = code.indexOf('function buildAgentCommandInput');
  if (fnStart === -1) { console.log('NO_FUNCTION'); process.exit(0); }
  let parenDepth = 0, pastParams = fnStart;
  for (let i = fnStart; i < code.length; i++) {
    if (code[i] === '(') parenDepth++;
    if (code[i] === ')') { parenDepth--; if (parenDepth === 0) { pastParams = i + 1; break; } }
  }
  let braceDepth = 0, bodyStart = -1;
  for (let i = pastParams; i < code.length; i++) {
    if (code[i] === '{') { if (braceDepth === 0) bodyStart = i; braceDepth++; }
    if (code[i] === '}') {
      braceDepth--;
      if (braceDepth === 0) {
        const body = code.slice(bodyStart + 1, i);
        // Count meaningful non-empty lines
        const lines = body.split('\\n').filter(l => l.trim().length > 0);
        console.log(lines.length >= 5 ? 'OK' : 'STUB');
        process.exit(0);
      }
    }
  }
  console.log('PARSE_ERROR');
" 2>/dev/null)

if [ "$ANTI_STUB" = "OK" ]; then
  pass 0.05 "Function body is substantial (not a stub)"
else
  fail 0.05 "Function body appears to be a stub"
fi

# ── Config-derived (0.05): Comment explains security reasoning ─────
# [agent_config] (0.05): "Add brief code comments for tricky or non-obvious logic." — CLAUDE.md:164
CONFIG_COMMENT=$(node -e "
  const fs = require('fs');
  const code = fs.readFileSync('${TARGET}', 'utf8');
  const lines = code.split('\\n');
  // Find lines with senderIsOwner: false (in actual code, not stripped)
  for (let i = 0; i < lines.length; i++) {
    const stripped = lines[i].replace(/\/\/.*$/, '').replace(/\/\*.*?\*\//g, '');
    if (/senderIsOwner\s*:\s*false/.test(stripped)) {
      // Check surrounding 3 lines for a comment with security-related keywords
      const context = lines.slice(Math.max(0, i - 3), i + 2).join(' ');
      const hasComment = /\/[\/\*]/.test(context);
      const hasKeyword = /owner|external|ingress|http|secur|privileg|trust|non.owner|restrict/i.test(context);
      console.log(hasComment && hasKeyword ? 'OK' : 'NO_COMMENT');
      process.exit(0);
    }
  }
  console.log('NO_MATCH');
" 2>/dev/null)

if [ "$CONFIG_COMMENT" = "OK" ]; then
  pass 0.05 "Comment near senderIsOwner explains security reasoning"
else
  fail 0.05 "No explanatory comment near senderIsOwner change"
fi

# ── Finalize ───────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${SCORE} / 1.0"
mkdir -p /tests 2>/dev/null || true
echo "${SCORE}" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('${SCORE}')
# Breakdown: F2P=0.60, P2P=0.30, anti-stub=0.05, config=0.05
behavioral = min(score, 0.60)
regression = min(max(score - 0.60, 0), 0.35)
config_score = min(max(score - 0.95, 0), 0.05)
style = 0.0
json.dump({
    'reward': round(score, 2),
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config_score, 2),
    'style_rubric': style
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(json.load(open('/logs/verifier/reward.json')), indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
