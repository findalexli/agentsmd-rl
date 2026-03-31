#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/opencode"
BASH_TXT="$REPO/packages/opencode/src/tool/bash.txt"
BASH_TS="$REPO/packages/opencode/src/tool/bash.ts"

log() { echo "$1"; }

mkdir -p /logs/verifier

# ── GATE: Files must exist and be readable ──────────────────────────
# [pr_diff] (0.00): Core files must not be missing or empty
log "=== GATE: File existence ==="
if [ ! -s "$BASH_TXT" ] || [ ! -s "$BASH_TS" ]; then
    log "GATE FAILED: bash.txt or bash.ts missing/empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! node -e "require('fs').readFileSync('$BASH_TS','utf8')" 2>/dev/null; then
    log "GATE FAILED: bash.ts is not readable"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed"

# ── F2P-1 (0.30): bash.txt must not contain ${directory} placeholder ──
# [pr_diff] (0.30): Template should not have project-specific placeholder
log ""
log "=== F2P-1: bash.txt has no \${directory} placeholder ==="
if ! grep -q '\${directory}' "$BASH_TXT" 2>/dev/null; then
    log "PASS: No \${directory} placeholder in bash.txt"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    log "FAIL: bash.txt still contains \${directory} placeholder"
fi

# ── F2P-2 (0.20): Template is fully static after known global substitutions ──
# [pr_diff] (0.20): After replacing maxLines/maxBytes, no ${...} placeholders should remain
log ""
log "=== F2P-2: Template fully static after global substitutions ==="
STATIC_CHECK=$(node -e "
  const fs = require('fs');
  const txt = fs.readFileSync('$BASH_TXT', 'utf8');
  // Simulate the substitutions bash.ts does with global constants
  let result = txt.replaceAll('\${maxLines}', '5000').replaceAll('\${maxBytes}', '50000');
  // Check for any remaining \${...} placeholders needing runtime data
  const remaining = result.match(/\\\$\{[^}]+\}/g);
  if (remaining && remaining.length > 0) {
    console.log('has_placeholders:' + remaining.join(','));
  } else {
    console.log('static');
  }
" 2>/dev/null || echo "error")

if [ "$STATIC_CHECK" = "static" ]; then
    log "PASS: Template is fully static after global substitutions"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    log "FAIL: Template still has dynamic placeholders: $STATIC_CHECK"
fi

# ── F2P-3 (0.10): bash.ts must not substitute directory into description ──
# [pr_diff] (0.10): Description builder should not inject project-specific data
log ""
log "=== F2P-3: bash.ts does not inject directory into description ==="
DIR_IN_DESC=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$BASH_TS', 'utf8');
  const lines = src.split('\n');
  let found = false;
  for (const line of lines) {
    const trimmed = line.trim();
    // Skip comments
    if (trimmed.startsWith('//') || trimmed.startsWith('*')) continue;
    // Look for any replace/replaceAll call involving 'directory' as a string pattern
    // This is the core bug: .replaceAll('\${directory}', Instance.directory)
    // We check broadly: any line with both a replace call and 'directory' in a string context
    if ((line.includes('.replace(') || line.includes('.replaceAll(')) &&
        (line.includes('directory') || line.includes('\\$\\{directory\\}'))) {
      // Exclude workdir parameter description (which legitimately references directory)
      if (line.includes('.describe(')) continue;
      found = true;
      break;
    }
  }
  console.log(found ? 'has_directory' : 'clean');
" 2>/dev/null || echo "error")

if [ "$DIR_IN_DESC" = "clean" ]; then
    log "PASS: bash.ts does not inject directory into description"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: bash.ts still substitutes directory into description"
fi

# ── P2P-1 (0.10): bash.txt still describes default directory behavior ──
# [pr_diff] (0.10): Users must still know about the default working directory
log ""
log "=== P2P-1: bash.txt describes default directory behavior ==="
if grep -qiE 'working.?directory|current.?directory|default.?directory|commands?.+run.+in' "$BASH_TXT" 2>/dev/null; then
    log "PASS: bash.txt still mentions directory behavior"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: bash.txt no longer describes default directory behavior"
fi

# ── P2P-2 (0.10): bash.txt still has maxLines/maxBytes placeholders ──
# [pr_diff] (0.10): The other template substitutions must still be present
log ""
log "=== P2P-2: bash.txt retains maxLines and maxBytes placeholders ==="
HAS_LINES=$(grep -c '\${maxLines}' "$BASH_TXT" 2>/dev/null || echo "0")
HAS_BYTES=$(grep -c '\${maxBytes}' "$BASH_TXT" 2>/dev/null || echo "0")
if [ "$HAS_LINES" -gt 0 ] && [ "$HAS_BYTES" -gt 0 ]; then
    log "PASS: maxLines and maxBytes placeholders preserved"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: maxLines ($HAS_LINES) or maxBytes ($HAS_BYTES) placeholders missing"
fi

# ── Anti-stub (0.10): bash.txt must be a real tool description ──
# [static] (0.10): Template must not be gutted or replaced with garbage
log ""
log "=== ANTI-STUB: bash.txt has substantial content ==="
LINE_COUNT=$(wc -l < "$BASH_TXT" 2>/dev/null || echo "0")
WORD_COUNT=$(wc -w < "$BASH_TXT" 2>/dev/null || echo "0")
# Check for bash-tool-relevant concepts (at least 5 distinct concepts)
CONCEPT_COUNT=$(grep -ciE 'command|output|execute|run|shell|timeout|workdir|truncat|parameter|exit' "$BASH_TXT" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -ge 10 ] && [ "$WORD_COUNT" -ge 50 ] && [ "$CONCEPT_COUNT" -ge 5 ]; then
    log "PASS: bash.txt has $LINE_COUNT lines, $WORD_COUNT words, $CONCEPT_COUNT concept mentions"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: bash.txt too thin ($LINE_COUNT lines, $WORD_COUNT words, $CONCEPT_COUNT concepts)"
fi

# ── Config: no `any` type in bash.ts tool definition area ──
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:41 @ 48326e8d
log ""
log "=== CONFIG: no \`any\` type in bash.ts tool definition ==="
ANY_COUNT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$BASH_TS', 'utf8');
  // Check the tool definition area for ': any' annotations
  const anyMatches = src.match(/:\s*any\b/g);
  console.log(anyMatches ? anyMatches.length : 0);
" 2>/dev/null || echo "0")

if [ "$ANY_COUNT" = "0" ]; then
    log "PASS: No \`any\` types in bash.ts"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Found $ANY_COUNT \`any\` type annotations in bash.ts"
fi

# ── Config: BashTool export preserved ──
# [agent_config] (0.05): Tool must still be properly exported
log ""
log "=== CONFIG: BashTool export preserved ==="
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$BASH_TS', 'utf8');
  if (!src.includes('BashTool')) process.exit(1);
" 2>/dev/null; then
    log "PASS: BashTool export preserved"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: BashTool export missing"
fi

# ── Final score ──
log ""
log "=== RESULTS ==="
log "Score: $SCORE / 1.00"

echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
