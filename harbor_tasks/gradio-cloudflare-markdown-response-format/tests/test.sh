#!/usr/bin/env bash
set +e

BASE_COMMIT="64828b08d5be4fdde8a73932b3f288c073ec49bd"
DOC_SERVER="js/_website/src/routes/api/markdown/[doc]/+server.ts"
GUIDE_SERVER="js/_website/src/routes/api/markdown/guide/[guide]/+server.ts"
CLIENT="js/_website/src/lib/components/DocsCopyMarkdown.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

# ---------- GATE: All three changed files exist ----------
GATE_PASS=1
for f in "$DOC_SERVER" "$GUIDE_SERVER" "$CLIENT"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=0
    fi
done
if [ "$GATE_PASS" -eq 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Validate syntax — balanced braces in server files
node -e "
const fs = require('fs');
for (const f of ['$DOC_SERVER', '$GUIDE_SERVER']) {
    const src = fs.readFileSync(f, 'utf8');
    let depth = 0;
    for (const ch of src) { if (ch === '{') depth++; if (ch === '}') depth--; }
    if (depth !== 0) { console.error('GATE FAIL: unbalanced braces in ' + f); process.exit(1); }
}
" 2>&1
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax check failed"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Extract unforgeable originals from base commit
git show ${BASE_COMMIT}:"${DOC_SERVER}" > /tmp/doc_orig.ts 2>/dev/null
git show ${BASE_COMMIT}:"${GUIDE_SERVER}" > /tmp/guide_orig.ts 2>/dev/null
git show ${BASE_COMMIT}:"${CLIENT}" > /tmp/client_orig.svelte 2>/dev/null

# ---------- CHECK 1 (0.25): [pr_diff] F2P — Doc endpoint: json() wrapper → plain Response ----------
# Buggy original uses json({markdown:...}); fix must use new Response() without json()
C1=$(node -e "
const fs = require('fs');
const orig = fs.readFileSync('/tmp/doc_orig.ts', 'utf8');
const fixed = fs.readFileSync('$DOC_SERVER', 'utf8');
const origHasJsonReturn = /return\s+json\s*\(/.test(orig);
const fixedHasResponse = /new\s+Response\s*\(/.test(fixed);
const fixedNoJsonReturn = !/return\s+json\s*\(/.test(fixed);
if (!origHasJsonReturn) { console.log('SKIP: base commit lacks expected json() pattern'); process.exit(0); }
if (fixedHasResponse && fixedNoJsonReturn) { console.log('PASS'); }
else { console.log('FAIL: response=' + fixedHasResponse + ' no_json=' + fixedNoJsonReturn); }
" 2>&1)
echo "CHECK 1: $C1"
if echo "$C1" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi

# ---------- CHECK 2 (0.25): [pr_diff] F2P — Guide endpoint: json() wrapper → plain Response ----------
C2=$(node -e "
const fs = require('fs');
const orig = fs.readFileSync('/tmp/guide_orig.ts', 'utf8');
const fixed = fs.readFileSync('$GUIDE_SERVER', 'utf8');
const origHasJsonReturn = /return\s+json\s*\(/.test(orig);
const fixedHasResponse = /new\s+Response\s*\(/.test(fixed);
const fixedNoJsonReturn = !/return\s+json\s*\(/.test(fixed);
if (!origHasJsonReturn) { console.log('SKIP: base commit lacks expected json() pattern'); process.exit(0); }
if (fixedHasResponse && fixedNoJsonReturn) { console.log('PASS'); }
else { console.log('FAIL: response=' + fixedHasResponse + ' no_json=' + fixedNoJsonReturn); }
" 2>&1)
echo "CHECK 2: $C2"
if echo "$C2" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi

# ---------- CHECK 3 (0.15): [pr_diff] F2P — Client: .json()/.markdown → .text() ----------
# Original client uses response.json() then .markdown; fix must use .text()
C3=$(node -e "
const fs = require('fs');
const orig = fs.readFileSync('/tmp/client_orig.svelte', 'utf8');
const fixed = fs.readFileSync('$CLIENT', 'utf8');
const origUsesJsonParse = /\.json\s*\(\s*\)/.test(orig);
const fixedUsesText = /\.text\s*\(\s*\)/.test(fixed);
// Fixed must not use .json() followed by .markdown extraction
const fixedNoJsonMarkdown = !/\.json\s*\(\s*\)/.test(fixed) || !/\.markdown\b/.test(fixed);
if (!origUsesJsonParse) { console.log('SKIP: base commit lacks expected .json() pattern'); process.exit(0); }
if (fixedUsesText && fixedNoJsonMarkdown) { console.log('PASS'); }
else { console.log('FAIL: text=' + fixedUsesText + ' no_json_md=' + fixedNoJsonMarkdown); }
" 2>&1)
echo "CHECK 3: $C3"
if echo "$C3" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
fi

# ---------- CHECK 4 (0.10): [pr_diff] Content-Type text/markdown in both server endpoints ----------
C4=$(node -e "
const fs = require('fs');
function getGetBody(src) {
    const idx = src.indexOf('export async function GET');
    if (idx === -1) return '';
    let depth = 0, started = false, start = -1, end = -1;
    for (let i = idx; i < src.length; i++) {
        if (src[i] === '{') { depth++; if (!started) { started = true; start = i; } }
        if (src[i] === '}') { depth--; if (started && depth === 0) { end = i; break; } }
    }
    return end > start ? src.slice(start, end + 1) : '';
}
const doc = getGetBody(fs.readFileSync('$DOC_SERVER', 'utf8'));
const guide = getGetBody(fs.readFileSync('$GUIDE_SERVER', 'utf8'));
const docOk = doc.includes('text/markdown') && /new\s+Response/.test(doc);
const guideOk = guide.includes('text/markdown') && /new\s+Response/.test(guide);
console.log(docOk && guideOk ? 'PASS' : 'FAIL: doc=' + docOk + ' guide=' + guideOk);
" 2>&1)
echo "CHECK 4: $C4"
if echo "$C4" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

# ---------- CHECK 5 (0.05): [pr_diff] json import removed from @sveltejs/kit ----------
C5=$(node -e "
const fs = require('fs');
const doc = fs.readFileSync('$DOC_SERVER', 'utf8');
const guide = fs.readFileSync('$GUIDE_SERVER', 'utf8');
const hasJsonImport = (s) => /import\s*\{[^}]*\bjson\b[^}]*\}\s*from\s*['\"]@sveltejs\/kit['\"]/.test(s);
console.log(!hasJsonImport(doc) && !hasJsonImport(guide) ? 'PASS' : 'FAIL');
" 2>&1)
echo "CHECK 5: $C5"
if echo "$C5" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ---------- CHECK 6 (0.10): [pr_diff] Anti-stub — GET functions have meaningful handler logic ----------
# Rejects trivial stubs by requiring substantial function bodies with real logic
C6=$(node -e "
const fs = require('fs');
function getGetBody(src) {
    const idx = src.indexOf('export async function GET');
    if (idx === -1) return '';
    let depth = 0, started = false, start = -1, end = -1;
    for (let i = idx; i < src.length; i++) {
        if (src[i] === '{') { depth++; if (!started) { started = true; start = i; } }
        if (src[i] === '}') { depth--; if (started && depth === 0) { end = i; break; } }
    }
    return end > start ? src.slice(start, end + 1) : '';
}
function meaningfulLines(body) {
    return body.split('\\n').filter(l => {
        const t = l.trim();
        return t && !t.startsWith('//') && !t.startsWith('*') && t !== '{' && t !== '}';
    }).length;
}
const doc = getGetBody(fs.readFileSync('$DOC_SERVER', 'utf8'));
const guide = getGetBody(fs.readFileSync('$GUIDE_SERVER', 'utf8'));
const docLines = meaningfulLines(doc);
const guideLines = meaningfulLines(guide);
// Real handlers have substantial logic (data loading, error handling, response)
// Also check for operational patterns: try/catch or if-checks, and data access
const docHasLogic = (doc.includes('try') || doc.includes('if ')) && /new\s+Response/.test(doc);
const guideHasLogic = (guide.includes('try') || guide.includes('if ')) && /new\s+Response/.test(guide);
if (docLines >= 8 && guideLines >= 6 && docHasLogic && guideHasLogic) {
    console.log('PASS');
} else {
    console.log('FAIL: doc_lines=' + docLines + ' guide_lines=' + guideLines + ' doc_logic=' + docHasLogic + ' guide_logic=' + guideHasLogic);
}
" 2>&1)
echo "CHECK 6: $C6"
if echo "$C6" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

# ---------- CHECK 7 (0.10): [pr_diff] Regression — SvelteKit handler structure preserved ----------
# prerender, entries(), and GET export must still be present (not deleted by agent)
C7=$(node -e "
const fs = require('fs');
const doc = fs.readFileSync('$DOC_SERVER', 'utf8');
const guide = fs.readFileSync('$GUIDE_SERVER', 'utf8');
const checks = [
    /export\s+(const\s+)?prerender/.test(doc),
    /export\s+(const\s+)?prerender/.test(guide),
    /export\s+(async\s+)?function\s+entries/.test(doc),
    /export\s+(async\s+)?function\s+entries/.test(guide),
    /export\s+async\s+function\s+GET/.test(doc),
    /export\s+async\s+function\s+GET/.test(guide),
];
console.log(checks.every(Boolean) ? 'PASS' : 'FAIL: ' + checks.join(','));
" 2>&1)
echo "CHECK 7: $C7"
if echo "$C7" | grep -q '^PASS'; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

# ---------- Final score ----------
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
