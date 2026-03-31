#!/usr/bin/env bash
set +e

SCORE=0
HEADER="js/_website/src/lib/components/Header.svelte"

echo "=== Gradio Mobile Menu UX Tests ==="

# ─── GATE: Svelte file compiles ───
# [pr_diff] (0.00): File must be valid Svelte
echo "[GATE] Checking Svelte syntax..."
if ! node -e "
  const svelte = require('svelte/compiler');
  const fs = require('fs');
  const src = fs.readFileSync('$HEADER', 'utf8');
  try { svelte.compile(src, { generate: 'dom', dev: false }); }
  catch(e) { console.error(e.message); process.exit(1); }
" 2>/dev/null; then
    echo "GATE FAILED: Svelte file does not compile"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "  GATE passed"

# ─── AST-based checks via Node.js ───
# All behavioral and structural checks use Svelte's parsed AST, not grep.
# This accepts any valid implementation rather than exact CSS class strings.
AST_RESULTS=$(node -e "
const svelte = require('svelte/compiler');
const fs = require('fs');
const src = fs.readFileSync('$HEADER', 'utf8');
const ast = svelte.parse(src);

const results = {};

// ── Helpers ──
function walk(node, fn) {
  if (!node || typeof node !== 'object') return;
  fn(node);
  if (node.children) node.children.forEach(c => walk(c, fn));
  if (node.else) walk(node.else, fn);
  if (node.body) walk(node.body, fn);
  if (node.pending) walk(node.pending, fn);
  if (node.then) walk(node.then, fn);
  if (node.catch) walk(node.catch, fn);
}

// Get static text portions of an attribute value
function attrStaticText(attr) {
  if (!attr || !attr.value || attr.value === true) return '';
  return attr.value.filter(v => v.type === 'Text').map(v => v.data || '').join(' ');
}

// Get raw source of an attribute (captures dynamic expressions too)
function attrRawSrc(attr) {
  if (!attr) return '';
  return src.substring(attr.start, attr.end);
}

function getAttr(node, name) {
  return (node.attributes || []).find(a => a.name === name);
}

// ── Check 1: Conditional block contains a fixed/absolute full-screen overlay ──
// The buggy code has NO conditional overlay at all — this is a true fail-to-pass check.
// Accepts: fixed inset-0, absolute inset-0, fixed + top/left/w/h combos, etc.
let overlayIfNode = null;
walk(ast.html, (node) => {
  if (node.type === 'IfBlock' && !overlayIfNode) {
    walk({type: 'Fragment', children: node.children || []}, (child) => {
      if (child.type === 'Element') {
        const cls = attrStaticText(getAttr(child, 'class'));
        const style = attrStaticText(getAttr(child, 'style'));
        const combined = cls + ' ' + style;
        const isFixed = /\\bfixed\\b/.test(combined) || /\\babsolute\\b/.test(combined) || /position:\\s*(fixed|absolute)/.test(combined);
        const isFullScreen = /\\binset-0\\b/.test(combined) ||
          (/\\btop-0\\b/.test(combined) && /\\bleft-0\\b/.test(combined)) ||
          (/\\bw-full\\b/.test(combined) && /\\bh-full\\b/.test(combined)) ||
          (/\\bw-screen\\b/.test(combined) && /\\bh-screen\\b/.test(combined)) ||
          /inset:\\s*0/.test(combined) ||
          (/\\btop:\\s*0/.test(combined) && /\\bleft:\\s*0/.test(combined) && /\\bwidth:\\s*100/.test(combined));
        if (isFixed && isFullScreen) {
          overlayIfNode = node;
        }
      }
    });
  }
});
results.hasOverlay = !!overlayIfNode;

// ── Check 2: Close button with aria-label inside overlay ──
// Buggy code has no aria-label on close affordance. Accepts any label containing
// 'close' or 'dismiss' (case-insensitive) — not locked to 'Close menu'.
let hasCloseButton = false;
if (overlayIfNode) {
  walk({type: 'Fragment', children: overlayIfNode.children || []}, (node) => {
    if (node.type === 'Element' && (node.name === 'button' || node.name === 'a')) {
      const ariaLabel = getAttr(node, 'aria-label');
      if (ariaLabel) {
        const raw = attrRawSrc(ariaLabel).toLowerCase();
        if (raw.includes('close') || raw.includes('dismiss')) {
          hasCloseButton = true;
        }
      }
    }
  });
}
results.hasCloseButton = hasCloseButton;

// ── Check 3: Search and ThemeToggle in both desktop and mobile sections ──
// Buggy code only renders these once (desktop). Accepts any component name
// containing 'Search' and 'ThemeToggle' appearing 2+ times.
let searchCount = 0, themeCount = 0;
walk(ast.html, (node) => {
  if (node.type === 'InlineComponent') {
    if (node.name === 'Search') searchCount++;
    if (node.name === 'ThemeToggle') themeCount++;
  }
});
results.searchDual = searchCount >= 2;
results.themeDual = themeCount >= 2;

// ── Check 4: Mobile overlay has navigation links ──
// Verifies the overlay isn't just an empty div — it must contain <a> elements.
let overlayLinkCount = 0;
if (overlayIfNode) {
  walk({type: 'Fragment', children: overlayIfNode.children || []}, (node) => {
    if (node.type === 'Element' && node.name === 'a') {
      const href = attrStaticText(getAttr(node, 'href'));
      if (href && href.startsWith('/')) overlayLinkCount++;
    }
  });
}
results.overlayHasLinks = overlayLinkCount >= 2;

// ── Check 5: State decoupling (no show_nav = click_nav || store) ──
// Buggy code has \$: show_nav = click_nav || \$store?.lg coupling desktop/mobile.
let hasShowNavCoupling = false;
if (ast.instance && ast.instance.content) {
  const scriptSrc = src.substring(ast.instance.content.start, ast.instance.content.end);
  // Match reactive assignment coupling both click state and store/responsive state
  hasShowNavCoupling = /\\$:\\s*\\w+\\s*=.*click.*\\$.*store|\\$:\\s*\\w+\\s*=.*\\$.*store.*click/.test(scriptSrc);
}
results.decoupled = !hasShowNavCoupling;

// ── Check 6: Desktop elements preserved ──
let hasLogo = false, hasNavLink = false, hasCommunity = false;
walk(ast.html, (node) => {
  if (node.type === 'Element' && node.name === 'img') {
    const alt = attrStaticText(getAttr(node, 'alt'));
    if (/logo/i.test(alt)) hasLogo = true;
  }
  if (node.type === 'Element' && node.name === 'a') {
    const href = attrStaticText(getAttr(node, 'href'));
    if (href === '/docs' || href === '/guides') hasNavLink = true;
  }
  if (node.type === 'Text' && node.data && /Community/i.test(node.data)) {
    hasCommunity = true;
  }
});
results.desktopElements = hasLogo && hasNavLink && hasCommunity;

// ── Check 7: Anti-stub ──
results.lineCount = src.split('\\n').length;
// Count meaningful elements (not just blank lines)
let elementCount = 0;
walk(ast.html, (node) => {
  if (node.type === 'Element' || node.type === 'InlineComponent') elementCount++;
});
results.elementCount = elementCount;

console.log(JSON.stringify(results));
" 2>/dev/null)

if [ -z "$AST_RESULTS" ]; then
    echo "AST analysis failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo "AST results: $AST_RESULTS"

# ─── BEHAVIORAL F2P: Full-screen conditional overlay ───
# [pr_diff] (0.25): Mobile menu must render as full-screen overlay in a conditional block
# Buggy code has NO conditional overlay — fails this check. Any positioning approach accepted.
echo "[F2P] Checking conditional overlay..."
HAS_OVERLAY=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hasOverlay', False))")
if [ "$HAS_OVERLAY" = "True" ]; then
    echo "  PASS: Conditional block with full-screen overlay found"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "  FAIL: No conditional full-screen overlay found"
fi

# [pr_diff] (0.15): Accessible close button within overlay
# Buggy code has no aria-label on close. Any label with 'close' or 'dismiss' accepted.
echo "[F2P] Checking accessible close button in overlay..."
HAS_CLOSE=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hasCloseButton', False))")
if [ "$HAS_CLOSE" = "True" ]; then
    echo "  PASS: Close button with aria-label found in overlay"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL: No accessible close button in overlay"
fi

# [pr_diff] (0.15): Search and ThemeToggle in both desktop and mobile
# Buggy code only renders these once. Checks component count >= 2.
echo "[F2P] Checking Search/ThemeToggle dual placement..."
SEARCH_DUAL=$(echo "$AST_RESULTS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('searchDual',False) and d.get('themeDual',False))")
if [ "$SEARCH_DUAL" = "True" ]; then
    echo "  PASS: Search and ThemeToggle in both desktop and mobile"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL: Search/ThemeToggle not duplicated for mobile"
fi

# [pr_diff] (0.10): Overlay contains actual navigation links
# Prevents empty-overlay stubs. Must have >=2 internal links.
echo "[F2P] Checking overlay has navigation links..."
HAS_LINKS=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('overlayHasLinks', False))")
if [ "$HAS_LINKS" = "True" ]; then
    echo "  PASS: Overlay contains navigation links"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL: Overlay has no navigation links"
fi

# [pr_diff] (0.10): Desktop/mobile state decoupled
# Buggy code has $: show_nav = click_nav || $store?.lg — any removal of this coupling passes.
echo "[F2P] Checking state decoupling..."
DECOUPLED=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('decoupled', False))")
if [ "$DECOUPLED" = "True" ]; then
    echo "  PASS: Desktop/mobile state decoupled"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL: show_nav still couples desktop and mobile state"
fi

# ─── REGRESSION: Desktop elements preserved ───
# [pr_diff] (0.10): Logo, nav links, Community section must still exist
echo "[P2P] Checking desktop elements preserved..."
DESKTOP_OK=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('desktopElements', False))")
if [ "$DESKTOP_OK" = "True" ]; then
    echo "  PASS: Desktop elements preserved"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL: Desktop elements missing"
fi

# ─── STRUCTURAL: Anti-stub ───
# [pr_diff] (0.05): File must be substantial — >100 lines AND >15 real elements
echo "[ANTI-STUB] Checking file substance..."
LINES=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('lineCount', 0))")
ELEMS=$(echo "$AST_RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('elementCount', 0))")
if [ "$LINES" -gt 100 ] 2>/dev/null && [ "$ELEMS" -gt 15 ] 2>/dev/null; then
    echo "  PASS: File has $LINES lines, $ELEMS elements"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "  FAIL: File too small ($LINES lines, $ELEMS elements)"
fi

# ─── CONFIG: Prettier formatting ───
# [agent_config] (0.10): "Frontend code is formatted with prettier" — AGENTS.md:43-44
echo "[CONFIG] Checking Prettier formatting..."
if command -v npx &>/dev/null && npx prettier --version &>/dev/null 2>&1; then
    if npx prettier --check "$HEADER" 2>/dev/null; then
        echo "  PASS: File passes Prettier"
        SCORE=$(python3 -c "print($SCORE + 0.10)")
    else
        echo "  FAIL: File does not pass Prettier"
    fi
else
    echo "  SKIP: Prettier not available, awarding partial credit"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ─── Final score ───
echo ""
FINAL=$(python3 -c "print(round(float('$SCORE'), 4))")
echo "=== Final Score: $FINAL ==="
echo "$FINAL" > /logs/verifier/reward.txt

# Category breakdowns
python3 -c "
import json
s = float('$FINAL')
# F2P behavioral: overlay(0.25) + close(0.15) + search(0.15) + links(0.10) + decoupled(0.10) = 0.75
# P2P regression: desktop(0.10) = 0.10
# Structural: anti-stub(0.05) = 0.05
# Config: prettier(0.10) = 0.10
print(json.dumps({
    'reward': s,
    'behavioral': min(s, 0.75),
    'regression': 0.10 if s >= 0.85 else max(0, min(s - 0.75, 0.10)),
    'structural': 0.05 if s >= 0.90 else 0.0,
    'config': 0.10 if s >= 0.95 else max(0, min(s - 0.90, 0.10)),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
