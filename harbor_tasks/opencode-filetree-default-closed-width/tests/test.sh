#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/opencode"
LAYOUT="$REPO/packages/app/src/context/layout.tsx"
SESSION="$REPO/packages/app/src/pages/session.tsx"

log() { echo "$1"; }
add() { SCORE=$(python3 -c "print($SCORE + $1)"); }

mkdir -p /logs/verifier

# ── GATE: Files exist and are not stubs ─────────────────────────────
# [static] (0.00): Core files must exist with real content
log "=== GATE: File integrity ==="
if [ ! -f "$LAYOUT" ]; then
    log "GATE FAILED: layout.tsx missing"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if [ "$(wc -l < "$LAYOUT")" -lt 100 ]; then
    log "GATE FAILED: layout.tsx is a stub"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! node -e "
  const src = require('fs').readFileSync('$LAYOUT','utf8');
  if (!src.includes('createStore')) process.exit(1);
  if (!src.includes('fileTree')) process.exit(1);
  if (!src.includes('sidebar')) process.exit(1);
" 2>/dev/null; then
    log "GATE FAILED: layout.tsx missing core store structure"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed"

# ── Helper: extract initial store state with robust parsing ─────────
# Uses balanced-brace matching and constant resolution instead of fragile regex.
# Accepts any valid JS formatting, nested objects, spread operators, etc.
STORE_DATA=$(node -e "
  const src = require('fs').readFileSync('$LAYOUT','utf8');

  // 1. Collect all top-level numeric constant definitions
  const constants = {};
  const re = /(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(\d+)/g;
  let m;
  while ((m = re.exec(src)) !== null) constants[m[1]] = parseInt(m[2]);

  // 2. Find createStore( and extract argument via balanced braces
  const csIdx = src.indexOf('createStore(');
  if (csIdx === -1) { console.log(JSON.stringify({error:'no_createStore'})); process.exit(0); }
  let start = src.indexOf('{', csIdx);
  let depth = 0, end = start;
  for (let i = start; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
  }
  const storeBlock = src.substring(start, end + 1);

  // 3. Extract a named panel's config block (balanced braces)
  function extractPanel(block, name) {
    const re = new RegExp(name + '\\\\s*:\\\\s*\\\\{');
    const pm = re.exec(block);
    if (!pm) return null;
    let d = 0, s = pm.index + pm[0].length - 1, e = s;
    for (let i = s; i < block.length; i++) {
      if (block[i] === '{') d++;
      if (block[i] === '}') { d--; if (d === 0) { e = i; break; } }
    }
    return block.substring(s + 1, e);
  }

  // 4. Resolve a property value to a JS primitive
  function resolve(block, prop) {
    if (!block) return undefined;
    const m = block.match(new RegExp(prop + '\\\\s*:\\\\s*([\\\\w.!]+)'));
    if (!m) return undefined;
    const raw = m[1];
    if (raw === 'true' || raw === '!0') return true;
    if (raw === 'false' || raw === '!1') return false;
    const n = parseInt(raw);
    if (!isNaN(n)) return n;
    if (constants[raw] !== undefined) return constants[raw];
    return '__unresolved__' + raw;
  }

  // 5. Get the raw identifier used for width (for structural check)
  function widthRef(block) {
    if (!block) return null;
    const m = block.match(/width\s*:\s*([\w]+)/);
    return m ? m[1] : null;
  }

  const ft = extractPanel(storeBlock, 'fileTree');
  const sb = extractPanel(storeBlock, 'sidebar');

  console.log(JSON.stringify({
    fileTree: { opened: resolve(ft,'opened'), width: resolve(ft,'width'), widthRef: widthRef(ft) },
    sidebar:  { width: resolve(sb,'width'), widthRef: widthRef(sb) }
  }));
" 2>/dev/null || echo '{"error":"node_crash"}')

log "Store data: $STORE_DATA"

# ── F2P-1 (0.35): fileTree defaults to closed ──────────────────────
# [pr_diff] (0.35): File tree must default to closed on fresh sessions
log ""
log "=== F2P-1: fileTree defaults to closed ==="
FT_OPENED=$(node -e "
  const d = JSON.parse(process.argv[1]);
  if (d.error) { console.log('error'); process.exit(0); }
  console.log(String(d.fileTree.opened));
" "$STORE_DATA" 2>/dev/null || echo "error")

if [ "$FT_OPENED" = "false" ]; then
    log "PASS: fileTree.opened defaults to false"
    add 0.35
else
    log "FAIL: fileTree.opened is '$FT_OPENED' (expected false)"
fi

# ── F2P-2 (0.30): fileTree width < sidebar width (resolved values) ─
# [pr_diff] (0.30): File tree should use a narrower default width than sidebar
log ""
log "=== F2P-2: fileTree default width < sidebar width ==="
WIDTH_RESULT=$(node -e "
  const d = JSON.parse(process.argv[1]);
  if (d.error) { console.log('FAIL:parse_error'); process.exit(0); }
  const ftW = d.fileTree.width;
  const sbW = d.sidebar.width;
  if (typeof ftW !== 'number' || typeof sbW !== 'number') {
    console.log('FAIL:unresolved:ft=' + ftW + ',sb=' + sbW);
    process.exit(0);
  }
  if (ftW > 0 && sbW > 0 && ftW < sbW) {
    console.log('PASS:ft=' + ftW + ',sb=' + sbW);
  } else {
    console.log('FAIL:ft=' + ftW + ',sb=' + sbW);
  }
" "$STORE_DATA" 2>/dev/null || echo "FAIL:error")

if [[ "$WIDTH_RESULT" == PASS:* ]]; then
    log "PASS: $WIDTH_RESULT"
    add 0.30
else
    log "FAIL: $WIDTH_RESULT"
fi

# ── P2P-1 (0.10): sidebar width unchanged at 344 ──────────────────
# [pr_diff] (0.10): Sidebar width must remain at its original value
log ""
log "=== P2P-1: sidebar width unchanged ==="
SB_WIDTH=$(node -e "
  const d = JSON.parse(process.argv[1]);
  if (d.error) { console.log('error'); process.exit(0); }
  console.log(d.sidebar.width);
" "$STORE_DATA" 2>/dev/null || echo "error")

if [ "$SB_WIDTH" = "344" ]; then
    log "PASS: sidebar width is 344"
    add 0.10
else
    log "FAIL: sidebar width is '$SB_WIDTH' (expected 344)"
fi

# ── P2P-2 (0.05): session.tsx preserves keyboard handling ──────────
# [pr_diff] (0.05): Existing keyboard event handling must not be broken
log ""
log "=== P2P-2: session.tsx onMount keydown preserved ==="
if [ -f "$SESSION" ] && node -e "
  const src = require('fs').readFileSync('$SESSION','utf8');
  if (!src.includes('onMount')) process.exit(1);
  if (!src.includes('handleKeyDown') && !src.includes('keydown') && !src.includes('KeyDown')) process.exit(1);
" 2>/dev/null; then
    log "PASS: onMount + keyboard handling present"
    add 0.05
else
    log "FAIL: session.tsx missing onMount or keyboard handling"
fi

# ── STRUCTURAL (0.10): fileTree and sidebar use different widths ────
# [pr_diff] (0.10): File tree operations must not share sidebar's width constant
log ""
log "=== STRUCTURAL: separate width defaults ==="
SEP_CHECK=$(node -e "
  const d = JSON.parse(process.argv[1]);
  if (d.error) { console.log('FAIL:error'); process.exit(0); }
  const ftRef = d.fileTree.widthRef;
  const sbRef = d.sidebar.widthRef;
  const ftW = d.fileTree.width;
  const sbW = d.sidebar.width;

  // Accept ANY approach where the values differ:
  // - Different named constants
  // - Different numeric literals
  // - One named, one literal
  if (typeof ftW === 'number' && typeof sbW === 'number' && ftW !== sbW) {
    console.log('PASS:values_differ');
  } else if (ftRef && sbRef && ftRef !== sbRef) {
    console.log('PASS:refs_differ');
  } else {
    console.log('FAIL:shared:' + ftRef + '=' + sbRef);
  }
" "$STORE_DATA" 2>/dev/null || echo "FAIL:error")

if [[ "$SEP_CHECK" == PASS:* ]]; then
    log "PASS: $SEP_CHECK"
    add 0.10
else
    log "FAIL: $SEP_CHECK"
fi

# ── CONFIG (0.05): no `any` type in changed code ───────────────────
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ d36b38e4
log ""
log "=== CONFIG: no any type ==="
DIFF=$(cd "$REPO" && git diff HEAD -- packages/app/src/context/layout.tsx packages/app/src/pages/session.tsx 2>/dev/null || echo "")
if [ -z "$DIFF" ]; then
    # No changes detected — try HEAD~1
    DIFF=$(cd "$REPO" && git diff HEAD~1 -- packages/app/src/context/layout.tsx packages/app/src/pages/session.tsx 2>/dev/null || echo "")
fi
if echo "$DIFF" | grep -q '^\+.*:\s*any\b'; then
    log "FAIL: Added any type annotation"
else
    log "PASS: No any types in changed lines"
    add 0.05
fi

# ── CONFIG (0.05): prefer const, no unnecessary else ────────────────
# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:70 @ d36b38e4
# [agent_config] (0.05): "Avoid else statements" — AGENTS.md:84 @ d36b38e4
log ""
log "=== CONFIG: const > let, no else ==="
STYLE_FAIL=0
if echo "$DIFF" | grep -q '^\+.*\blet\b'; then
    log "NOTE: let declaration found in changes"
    STYLE_FAIL=1
fi
if echo "$DIFF" | grep -q '^\+.*\belse\b'; then
    log "NOTE: else statement found in changes"
    STYLE_FAIL=1
fi
if [ "$STYLE_FAIL" -eq 0 ]; then
    log "PASS: Style checks passed"
    add 0.05
else
    log "FAIL: Style violations in changed code"
fi

# ── Final score ─────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
log "Score: $SCORE / 1.0"

echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
