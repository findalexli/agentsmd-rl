#!/usr/bin/env bash
set +e

REWARD=0
STYLE_FILE="js/_website/src/lib/assets/style.css"

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); echo "PASS ($1): $2"; }
skip() { echo "FAIL ($1): $2"; }

# === GATE: CSS file exists and is non-empty ===
# [pr_diff] (0.00): File must exist
if [ ! -s "$STYLE_FILE" ]; then
    echo "GATE FAIL: $STYLE_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ────────────────────────────────────────────────────────────
#  BEHAVIORAL: Parse CSS and verify table-related rules exist
#  with correct properties. Uses Node.js built-in CSS parsing
#  via a flexible approach that accepts ANY valid selector
#  targeting table elements.
# ────────────────────────────────────────────────────────────

# Write a reusable CSS analysis script
cat > /tmp/css_check.js << 'JSEOF'
const fs = require('fs');
const css = fs.readFileSync(process.argv[2], 'utf8');
const checkName = process.argv[3];

// Minimal CSS rule extractor: splits on top-level { } blocks
// Returns array of {selector, body} where body is the raw text inside braces
function extractRules(src) {
  const rules = [];
  let depth = 0, start = -1, selStart = 0;
  for (let i = 0; i < src.length; i++) {
    if (src[i] === '/' && src[i+1] === '*') {
      const end = src.indexOf('*/', i + 2);
      if (end !== -1) { i = end + 1; continue; }
    }
    if (src[i] === '{') {
      if (depth === 0) { start = i; }
      depth++;
    } else if (src[i] === '}') {
      depth--;
      if (depth === 0 && start !== -1) {
        const selector = src.slice(selStart, start).trim();
        const body = src.slice(start + 1, i).trim();
        rules.push({ selector, body });
        selStart = i + 1;
      }
    }
  }
  return rules;
}

// Parse properties from a CSS body block (handles nested blocks for dark mode etc)
function getProperties(body) {
  const props = {};
  // Match property: value pairs (simple, non-nested)
  const re = /([\w-]+)\s*:\s*([^;{}]+);/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    props[m[1].toLowerCase()] = m[2].trim();
  }
  return props;
}

// Check if selector targets a table element (flexible matching)
function selectorTargets(sel, element) {
  // Accepts: table, table th, table thead th, table > thead > th, .x table th, etc.
  const parts = sel.replace(/>/g, ' ').replace(/\s+/g, ' ').trim().split(' ');
  return parts.some(p => p === element || p.endsWith(element));
}

function selectorIsForDarkMode(sel) {
  return /\.dark\b/.test(sel) || /\[data-theme.*dark\]/.test(sel) ||
         /prefers-color-scheme:\s*dark/.test(sel);
}

function selectorTargetsTable(sel) {
  return selectorTargets(sel, 'table');
}

function selectorTargetsTableHeader(sel) {
  return selectorTargets(sel, 'th') ||
         (selectorTargets(sel, 'thead') && sel.includes('{'));
}

function selectorTargetsTableCell(sel) {
  return selectorTargets(sel, 'td');
}

const rules = extractRules(css);

// For nested rules (like inside @media), also extract inner rules
const allRules = [];
for (const r of rules) {
  allRules.push(r);
  // If this looks like an at-rule or .dark wrapper with nested blocks
  if (r.body.includes('{')) {
    const inner = extractRules(r.body);
    for (const ir of inner) {
      // Prefix with parent selector context
      allRules.push({
        selector: r.selector + ' ' + ir.selector,
        body: ir.body
      });
    }
  }
}

switch (checkName) {
  case 'table_base': {
    // Find any rule targeting table element with border-collapse and width
    const found = allRules.some(r => {
      if (!selectorTargetsTable(r.selector)) return false;
      // Also check it's not a dark-mode-only rule
      const props = getProperties(r.body);
      return props['border-collapse'] && props['width'];
    });
    process.exit(found ? 0 : 1);
  }
  case 'table_header': {
    // Any rule targeting th (or thead th) with background/padding
    const found = allRules.some(r => {
      if (!selectorTargetsTableHeader(r.selector)) return false;
      if (selectorIsForDarkMode(r.selector)) return false;
      const props = getProperties(r.body);
      return (props['background-color'] || props['background']) && props['padding'];
    });
    process.exit(found ? 0 : 1);
  }
  case 'table_cell': {
    // Any rule targeting td (or tbody td) with padding and border
    const found = allRules.some(r => {
      if (!selectorTargetsTableCell(r.selector)) return false;
      if (selectorIsForDarkMode(r.selector)) return false;
      const props = getProperties(r.body);
      const hasBorder = props['border'] || props['border-bottom'] ||
                        props['border-top'] || props['border-left'];
      return props['padding'] && hasBorder;
    });
    process.exit(found ? 0 : 1);
  }
  case 'dark_header': {
    // Dark mode rule targeting th with any styling
    const found = allRules.some(r => {
      if (!selectorTargetsTableHeader(r.selector)) return false;
      if (!selectorIsForDarkMode(r.selector)) return false;
      const props = getProperties(r.body);
      return Object.keys(props).length > 0;
    });
    process.exit(found ? 0 : 1);
  }
  case 'dark_cell': {
    // Dark mode rule targeting td with any styling
    const found = allRules.some(r => {
      if (!selectorTargetsTableCell(r.selector)) return false;
      if (!selectorIsForDarkMode(r.selector)) return false;
      const props = getProperties(r.body);
      return Object.keys(props).length > 0;
    });
    process.exit(found ? 0 : 1);
  }
  case 'css_valid': {
    // Basic validity: balanced braces, no obviously broken syntax
    let depth = 0;
    let inComment = false;
    for (let i = 0; i < css.length; i++) {
      if (!inComment && css[i] === '/' && css[i+1] === '*') { inComment = true; i++; continue; }
      if (inComment && css[i] === '*' && css[i+1] === '/') { inComment = false; i++; continue; }
      if (inComment) continue;
      if (css[i] === '{') depth++;
      if (css[i] === '}') depth--;
      if (depth < 0) process.exit(1);
    }
    process.exit(depth === 0 ? 0 : 1);
  }
  case 'prop_values_valid': {
    // Check that table-related rules have non-trivial property values
    // Reject: padding: x, border: x, background-color: x (single-char nonsense)
    let allValid = true;
    for (const r of allRules) {
      const isTableRule = selectorTargetsTable(r.selector) ||
                          selectorTargetsTableHeader(r.selector) ||
                          selectorTargetsTableCell(r.selector);
      if (!isTableRule) continue;
      const props = getProperties(r.body);
      for (const [key, val] of Object.entries(props)) {
        // Value must be >1 char and not pure gibberish
        if (val.length <= 1) { allValid = false; break; }
      }
      if (!allValid) break;
    }
    process.exit(allValid ? 0 : 1);
  }
  default:
    console.error('Unknown check:', checkName);
    process.exit(2);
}
JSEOF

# ── Behavioral (0.60 total) ──

# [pr_diff] (0.15): Tables have base styling (border-collapse, width)
node /tmp/css_check.js "$STYLE_FILE" table_base
if [ $? -eq 0 ]; then add 0.15 "Table base styles (border-collapse, width)"; else skip 0.15 "Missing table base styles"; fi

# [pr_diff] (0.15): Table headers have visual distinction (background + padding)
node /tmp/css_check.js "$STYLE_FILE" table_header
if [ $? -eq 0 ]; then add 0.15 "Table header styling (background, padding)"; else skip 0.15 "Missing table header styling"; fi

# [pr_diff] (0.10): Table cells have padding and borders
node /tmp/css_check.js "$STYLE_FILE" table_cell
if [ $? -eq 0 ]; then add 0.10 "Table cell styling (padding, border)"; else skip 0.10 "Missing table cell styling"; fi

# [pr_diff] (0.10): Dark mode covers table headers
node /tmp/css_check.js "$STYLE_FILE" dark_header
if [ $? -eq 0 ]; then add 0.10 "Dark mode table header styling"; else skip 0.10 "Missing dark mode header styling"; fi

# [pr_diff] (0.10): Dark mode covers table cells
node /tmp/css_check.js "$STYLE_FILE" dark_cell
if [ $? -eq 0 ]; then add 0.10 "Dark mode table cell styling"; else skip 0.10 "Missing dark mode cell styling"; fi

# ── CSS validity (behavioral gate-like, 0.05) ──

# [pr_diff] (0.05): CSS file has valid syntax (balanced braces)
node /tmp/css_check.js "$STYLE_FILE" css_valid
if [ $? -eq 0 ]; then add 0.05 "CSS syntax valid (balanced braces)"; else skip 0.05 "CSS has broken syntax"; fi

# ── Anti-stub: property values aren't nonsense (0.05) ──

# [static] (0.05): Property values must be non-trivial
node /tmp/css_check.js "$STYLE_FILE" prop_values_valid
if [ $? -eq 0 ]; then add 0.05 "Property values are non-trivial"; else skip 0.05 "Property values look like stubs"; fi

# ── Pass-to-pass: existing styles preserved (0.10) ──

# [repo_tests] (0.05): Existing scoped .obj dark table styles must not be removed
if grep -q '\.dark .obj .max-h-96.overflow-y-scroll table tbody td' "$STYLE_FILE" && \
   grep -q '\.dark .obj .max-h-96.overflow-y-scroll table tbody th' "$STYLE_FILE"; then
    add 0.05 "Existing scoped dark table styles preserved"
else
    skip 0.05 "Existing scoped dark table styles were removed"
fi

# [repo_tests] (0.05): Other existing CSS rules must not be removed
if grep -q 'summary::after' "$STYLE_FILE"; then
    add 0.05 "Existing summary::after styles preserved"
else
    skip 0.05 "Existing summary::after styles were removed"
fi

# ── Config-derived: tab indentation (0.05) ──

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45 @ e8dadd6
# The existing file uses tabs; new rules should too
python3 -c "
import sys
css = open('$STYLE_FILE').read()
# Find new table rules by looking for lines with table-related selectors
lines = css.splitlines()
new_lines = []
in_table = False
for line in lines:
    stripped = line.strip()
    if any(kw in stripped for kw in ['table {', 'table,', 'thead', 'tbody', '.dark table']):
        in_table = True
    if in_table:
        new_lines.append(line)
    if in_table and stripped == '}':
        in_table = False

# Check indented lines use tabs
space_indent = sum(1 for l in new_lines if l.startswith('  ') and l.strip())
tab_indent = sum(1 for l in new_lines if l.startswith('\t') and l.strip())
if tab_indent > 0 and space_indent == 0:
    sys.exit(0)
else:
    sys.exit(1)
"
if [ $? -eq 0 ]; then add 0.05 "New CSS uses tab indentation"; else skip 0.05 "New CSS should use tab indentation"; fi

# ── Anti-stub: file size (0.05) ──

# [static] (0.05): File must not be trivially small
LINE_COUNT=$(wc -l < "$STYLE_FILE")
if [ "$LINE_COUNT" -gt 480 ]; then
    add 0.05 "File has substantial content ($LINE_COUNT lines)"
else
    skip 0.05 "File suspiciously small ($LINE_COUNT lines)"
fi

echo ""
echo "Score: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
score = $REWARD
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(min(max(score - 0.70, 0), 0.10), 4),
    'config': round(min(max(score - 0.80, 0), 0.05), 4),
    'anti_stub': round(min(max(score - 0.85, 0), 0.10), 4)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
