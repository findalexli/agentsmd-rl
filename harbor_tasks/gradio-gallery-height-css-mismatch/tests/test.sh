#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/gradio"
GALLERY="$REPO/js/gallery/shared/Gallery.svelte"
INDEX="$REPO/js/gallery/Index.svelte"
TYPES="$REPO/js/gallery/types.ts"

log() { echo "[TEST] $*"; }
add() { SCORE=$(python3 -c "print(round($SCORE + $1, 2))"); }

mkdir -p /logs/verifier

########################################
# GATE: Required files must exist
########################################
for f in "$GALLERY" "$INDEX" "$TYPES"; do
    if [ ! -f "$f" ]; then
        log "GATE FAIL: $f not found"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
log "GATE: All files exist"

########################################
# Helper: extract balanced-brace expression from Svelte
########################################
cat > /tmp/extract_expr.js << 'JSEOF'
// Usage: node extract_expr.js <file> <pattern>
// Finds `pattern{...}` and returns the expression inside braces
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const pat = process.argv[3];
const idx = src.indexOf(pat);
if (idx === -1) { console.log('__NOT_FOUND__'); process.exit(0); }
let i = idx + pat.length, d = 1;
while (i < src.length && d > 0) {
    if (src[i] === '{') d++;
    else if (src[i] === '}') d--;
    i++;
}
console.log(src.slice(idx + pat.length, i - 1).trim());
JSEOF

########################################
# F2P (0.25): CSS selectors match template class names
########################################
# [pr_diff] (0.25): Container CSS selectors must correspond to classes used in HTML template
log "CHECK F2P: CSS-template class consistency"
R=$(node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
const styleIdx = src.search(/<style[^>]*>/);
if (styleIdx === -1) { console.log('NO_STYLE'); process.exit(0); }
const template = src.slice(0, styleIdx);
const css = src.slice(styleIdx);

// Collect class names from template HTML
const tmplClasses = new Set();
for (const m of template.matchAll(/class=[\"']([^\"']+)[\"']/g))
    m[1].split(/\s+/).forEach(c => tmplClasses.add(c));

// Collect CSS class selectors from style block
const cssSelectors = new Set();
for (const m of css.matchAll(/\\.([a-zA-Z_][\w-]*)\s*[\{,:]/g))
    cssSelectors.add(m[1]);

// For each container-related class in template, it must have a CSS rule
let pass = true;
for (const c of tmplClasses) {
    if (c.length < 4) continue;
    if (c.includes('container') || c.includes('gallery')) {
        if (!cssSelectors.has(c)) { pass = false; break; }
    }
}
console.log(pass ? 'PASS' : 'FAIL');
" "$GALLERY" 2>/dev/null)

if [ "$R" = "PASS" ]; then
    log "PASS: CSS selectors match template classes"
    add 0.25
else
    log "FAIL: CSS class mismatch — styles don't apply to rendered element ($R)"
fi

########################################
# F2P (0.20): style:height expression preserves string CSS values
########################################
# [pr_diff] (0.20): height="300px" must not be corrupted to "300pxpx"
log "CHECK F2P: String height preservation (eval)"
EXPR=$(node /tmp/extract_expr.js "$GALLERY" "style:height={" 2>/dev/null)
if [ "$EXPR" = "__NOT_FOUND__" ] || [ -z "$EXPR" ]; then
    log "FAIL: No style:height binding found"
    R="NO_EXPR"
else
    R=$(node -e "
    const expr = process.argv[1];
    try {
        const fn = new Function('height', 'return ' + expr);
        const result = fn('300px');
        if (result === '300px') console.log('PASS');
        else if (typeof result === 'string' && result.includes('pxpx')) console.log('CORRUPTED');
        else console.log('WRONG:' + result);
    } catch(e) {
        // Expression may reference Svelte-specific vars; fall back to logic check
        if (/typeof\s+height|Number\.isFinite|isNaN/.test(expr) ||
            !/height\s*\+\s*['\"\`]px/.test(expr))
            console.log('GUARDED');
        else
            console.log('UNGUARDED');
    }
    " "$EXPR" 2>/dev/null)
fi

case "$R" in
    PASS)      log "PASS: '300px' preserved as '300px'"; add 0.20 ;;
    GUARDED)   log "PASS: expression has type guard (couldn't eval directly)"; add 0.15 ;;
    *)         log "FAIL: string height corrupted or unguarded ($R)" ;;
esac

########################################
# F2P (0.15): Index.svelte forwards string heights to Gallery
########################################
# [pr_diff] (0.15): String heights like "300px" must not be dropped when forwarding
log "CHECK F2P: Height forwarding accepts strings"
R=$(node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
// Find all height={...} expressions that reference gradio
const re = /height\s*=\s*\{/g;
let m;
while ((m = re.exec(src)) !== null) {
    let i = m.index + m[0].length, d = 1;
    while (i < src.length && d > 0) {
        if (src[i] === '{') d++;
        else if (src[i] === '}') d--;
        i++;
    }
    const expr = src.slice(m.index + m[0].length, i - 1).trim();
    if (!expr.includes('gradio')) continue;

    // Evaluate: does it pass through string heights?
    try {
        const fn = new Function('gradio', 'return ' + expr);
        const r = fn({ props: { height: '300px' } });
        if (r === '300px') { console.log('PASS'); process.exit(0); }
        else if (r === undefined || r === null) { console.log('DROPPED'); process.exit(0); }
        else { console.log('RESULT:' + r); process.exit(0); }
    } catch(e) {
        // Fallback: check for the known-bad pattern
        if (/typeof.*===\s*['\"]number['\"]/.test(expr)) {
            console.log('BLOCKS_STRINGS');
        } else {
            console.log('EVAL_ERR');
        }
        process.exit(0);
    }
}
console.log('NO_GRADIO_EXPR');
" "$INDEX" 2>/dev/null)

case "$R" in
    PASS)           log "PASS: '300px' forwarded to Gallery"; add 0.15 ;;
    NO_GRADIO_EXPR) log "PASS: no gradio-based height filter (direct forwarding)"; add 0.15 ;;
    EVAL_ERR)       log "PASS: expression changed (eval err, no blocking pattern)"; add 0.10 ;;
    *)              log "FAIL: string height dropped by forwarding logic ($R)" ;;
esac

########################################
# F2P (0.10): Height type accepts string values
########################################
# [pr_diff] (0.10): GalleryProps.height must accept CSS string values
log "CHECK F2P: Height type definition accepts strings"
R=$(node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
// Find all type annotations for height
const m = src.match(/height\s*[?:]?\s*:\s*([^;}\n]+)/);
if (!m) { console.log('NO_DEF'); process.exit(0); }
const typedef = m[1].trim();
// Accept any type that includes string (covers: number|string, string|number, string, etc.)
// Reject types limited to number|'auto' or just number
if (/\bstring\b/.test(typedef)) console.log('PASS');
else console.log('FAIL:' + typedef);
" "$TYPES" 2>/dev/null)

if [ "$R" = "PASS" ]; then
    log "PASS: types.ts height accepts string"
    add 0.10
else
    log "FAIL: height type too restrictive ($R)"
fi

########################################
# P2P (0.05): Numeric heights still work
########################################
# [pr_diff] (0.05): height=300 must still produce valid CSS like "300px"
log "CHECK P2P: Numeric height"
if [ "$EXPR" != "__NOT_FOUND__" ] && [ -n "$EXPR" ]; then
    R=$(node -e "
    const expr = process.argv[1];
    try {
        const fn = new Function('height', 'return ' + expr);
        const r = fn(300);
        // '300px' or 300 are both acceptable (browser treats bare numbers as px)
        console.log((r === '300px' || r === 300) ? 'PASS' : 'FAIL:' + r);
    } catch(e) { console.log('EVAL_ERR'); }
    " "$EXPR" 2>/dev/null)
else
    R="NO_EXPR"
fi

if [ "$R" = "PASS" ]; then log "PASS: numeric height works"; add 0.05
else log "FAIL: numeric height broken ($R)"; fi

########################################
# P2P (0.05): "auto" height still works
########################################
# [pr_diff] (0.05): height="auto" must still produce "auto"
log "CHECK P2P: auto height"
if [ "$EXPR" != "__NOT_FOUND__" ] && [ -n "$EXPR" ]; then
    R=$(node -e "
    const expr = process.argv[1];
    try {
        const fn = new Function('height', 'return ' + expr);
        const r = fn('auto');
        console.log(r === 'auto' ? 'PASS' : 'FAIL:' + r);
    } catch(e) { console.log('EVAL_ERR'); }
    " "$EXPR" 2>/dev/null)
else
    R="NO_EXPR"
fi

if [ "$R" = "PASS" ]; then log "PASS: auto height works"; add 0.05
else log "FAIL: auto height broken ($R)"; fi

########################################
# F2P (0.05): Upload wrapper has height styling
########################################
# [pr_diff] (0.05): Upload area must not collapse — needs height from a CSS rule
log "CHECK: Upload wrapper height"
R=$(node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
const styleIdx = src.search(/<style[^>]*>/);
if (styleIdx === -1) { console.log('NO_STYLE'); process.exit(0); }
const css = src.slice(styleIdx);
// Check for any rule that gives the upload/wrapper area height
// Accept: height:100%, min-height, flex:1, etc.
const hasRule = /upload[-_]?wrapper[^}]*height/i.test(css) ||
    /wrapper[^}]*\{[^}]*height\s*:/i.test(css);
console.log(hasRule ? 'PASS' : 'FAIL');
" "$INDEX" 2>/dev/null)

if [ "$R" = "PASS" ]; then log "PASS: upload wrapper has height"; add 0.05
else log "FAIL: no upload wrapper height styling"; fi

########################################
# P2P (0.05): hidden-upload-input class preserved
########################################
# [pr_diff] (0.05): hidden-upload-input class must still exist for webcam mode
log "CHECK P2P: hidden-upload-input preserved"
if grep -q 'hidden-upload-input' "$INDEX" 2>/dev/null; then
    log "PASS"; add 0.05
else
    log "FAIL: hidden-upload-input removed"
fi

########################################
# Regression (0.05): Anti-stub — real component structure
########################################
# [repo_tests] (0.05): Gallery.svelte must be a real Svelte component, not a stub
log "CHECK: Anti-stub"
R=$(node -e "
const src = require('fs').readFileSync(process.argv[1], 'utf8');
const hasScript = /<script/.test(src);
const hasStyle = /<style/.test(src);
const hasTemplate = /<div/.test(src) && /class=/.test(src);
const lines = src.split('\n').length;
const ok = hasScript && hasStyle && hasTemplate && lines > 100;
console.log(ok ? 'PASS' : 'FAIL:' + lines + 'lines,script=' + hasScript + ',style=' + hasStyle);
" "$GALLERY" 2>/dev/null)

if [ "$R" = "PASS" ]; then log "PASS: real component"; add 0.05
else log "FAIL: likely stub ($R)"; fi

########################################
# Config (0.05): Tab indentation
########################################
# [agent_config] (0.05): "Be consistent with the style of the surrounding code." — AGENTS.md:29
log "CHECK: Tab indentation (repo convention)"
TABS=$(grep -cP '^\t' "$GALLERY" 2>/dev/null || echo 0)
SPACES=$(grep -cP '^  [^ ]' "$GALLERY" 2>/dev/null || echo 0)
if [ "$TABS" -gt "$SPACES" ]; then
    log "PASS: consistent tabs"
    add 0.05
else
    log "FAIL: inconsistent indentation (tabs=$TABS, spaces=$SPACES)"
fi

########################################
# Summary
########################################
log "Final score: $SCORE / 1.00"

echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
s = $SCORE
d = {'reward': s, 'behavioral': min(s, 0.80), 'regression': min(max(s - 0.80, 0), 0.10), 'config': min(max(s - 0.90, 0), 0.10)}
print(json.dumps(d))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
