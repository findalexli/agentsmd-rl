#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
HOME_TSX="$REPO/packages/opencode/src/cli/cmd/tui/routes/home.tsx"
INTERNAL_TS="$REPO/packages/opencode/src/cli/cmd/tui/plugin/internal.ts"
FOOTER_TSX="$REPO/packages/opencode/src/cli/cmd/tui/feature-plugins/home/footer.tsx"
SLOT_MAP="$REPO/packages/plugin/src/tui.ts"

SCORE=0
TOTAL=100

log()   { echo "  $1"; }
award() { echo "  PASS ($2): $1"; SCORE=$((SCORE + $2)); }
deny()  { echo "  FAIL ($2): $1"; }

mkdir -p /logs/verifier

echo "=== GATE: File existence ==="
# [pr_diff] (gate): Core modified files must exist
GATE_PASS=true
for f in "$HOME_TSX" "$INTERNAL_TS" "$SLOT_MAP"; do
    if [ ! -f "$f" ]; then
        log "GATE FAIL: $f does not exist"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
    exit 0
fi

echo ""
echo "=== Fail-to-pass: Behavioral checks ==="

# [pr_diff] (0.20): home.tsx must shrink significantly — refactor extracts ~45 lines of inline footer
# This is a behavioral proxy: the pre-fix file is bloated with footer logic, post-fix it's lean
BASELINE_LINES=$(cd "$REPO" && git show HEAD:packages/opencode/src/cli/cmd/tui/routes/home.tsx 2>/dev/null | wc -l)
CURRENT_LINES=$(wc -l < "$HOME_TSX" 2>/dev/null || echo "0")
REMOVED=$((BASELINE_LINES - CURRENT_LINES))
if [ "$REMOVED" -ge 20 ]; then
    award "home.tsx shrank by $REMOVED lines (footer extracted)" 20
else
    deny "home.tsx only shrank by $REMOVED lines (expected >=20 removed)" 20
fi

# [pr_diff] (0.15): home.tsx must NOT contain inline MCP counting/display logic
# The pre-fix file has connectedMcpCount memo, mcpError, .filter(connected) — all must move out
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HOME_TSX', 'utf8');
const mcpPatterns = [/connectedMcpCount/, /mcpError/, /\.filter\([^)]*connected/];
const found = mcpPatterns.filter(p => p.test(src));
if (found.length > 0) { console.log('Found: ' + found.map(p=>p.source)); process.exit(1); }
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "home.tsx no longer has inline MCP counting logic" 15
else
    deny "home.tsx still has inline MCP counting logic" 15
fi

# [pr_diff] (0.10): home.tsx must render footer via plugin/slot system
# Accept: <Slot name="home_footer">, <TuiPluginRuntime.Slot ...home_footer...>, or direct component import
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HOME_TSX', 'utf8');
// Must reference home_footer AND use Slot or import from footer plugin
const usesSlot = /home_footer/.test(src) && /[Ss]lot/.test(src);
const importsFooter = /footer/i.test(src) && /feature-plugins|plugin/i.test(src);
if (usesSlot || importsFooter) process.exit(0);
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "home.tsx renders footer via plugin/slot system" 10
else
    deny "home.tsx does not use plugin/slot system for footer" 10
fi

# [pr_diff] (0.15): Footer plugin file must exist with actual rendering logic
# Must contain JSX, references to directory/MCP/version content, and non-trivial code
if [ -f "$FOOTER_TSX" ]; then
    node -e "
    const fs = require('fs');
    const src = fs.readFileSync('$FOOTER_TSX', 'utf8');
    const lines = src.split('\n');
    // Count actual code lines (not comments, blanks, or single-char lines)
    const codeLines = lines.filter(l => {
        const t = l.trim();
        return t.length > 1 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
    });
    if (codeLines.length < 20) { console.log('Only ' + codeLines.length + ' code lines (need 20+)'); process.exit(1); }
    // Must contain JSX (angle brackets in non-import context)
    const jsxPattern = /<[A-Z][A-Za-z]*[\s/>]/;
    if (!jsxPattern.test(src)) { console.log('No JSX component rendering found'); process.exit(1); }
    // Must reference at least 2 of: directory/cwd, mcp, version (the moved content)
    const hasDir = /directory|cwd|useDirectory/i.test(src);
    const hasMcp = /mcp/i.test(src);
    const hasVersion = /version/i.test(src);
    const contentCount = [hasDir, hasMcp, hasVersion].filter(Boolean).length;
    if (contentCount < 2) { console.log('Only ' + contentCount + '/3 footer concerns found (need 2+)'); process.exit(1); }
    " 2>/dev/null
    if [ $? -eq 0 ]; then
        award "Footer plugin has substantial rendering content" 15
    else
        deny "Footer plugin lacks rendering content" 15
    fi
else
    deny "Footer plugin file does not exist" 15
fi

# [pr_diff] (0.05): Footer plugin must have a default export (any valid pattern)
if [ -f "$FOOTER_TSX" ]; then
    node -e "
    const fs = require('fs');
    const src = fs.readFileSync('$FOOTER_TSX', 'utf8');
    if (/export\s+default\b/.test(src)) process.exit(0);
    if (/export\s*\{[^}]*as\s+default/.test(src)) process.exit(0);
    if (/module\.exports\s*=/.test(src)) process.exit(0);
    process.exit(1);
    " 2>/dev/null
    if [ $? -eq 0 ]; then
        award "Footer plugin has default export" 5
    else
        deny "Footer plugin missing default export" 5
    fi
else
    deny "Footer plugin file does not exist (export)" 5
fi

# [pr_diff] (0.05): Footer plugin must register the home_footer slot
# Accept: string "home_footer" used in a registration context
if [ -f "$FOOTER_TSX" ]; then
    node -e "
    const fs = require('fs');
    const src = fs.readFileSync('$FOOTER_TSX', 'utf8');
    // Must contain the slot name as a string or identifier
    if (!/home_footer/.test(src)) process.exit(1);
    // Must have some form of registration (register call, slots API, or callback pattern)
    if (/register|slots|init\s*[:(]/.test(src)) process.exit(0);
    // Also accept: home_footer used as a key or string argument
    if (/['\"]home_footer['\"]/.test(src)) process.exit(0);
    process.exit(1);
    " 2>/dev/null
    if [ $? -eq 0 ]; then
        award "Footer plugin registers home_footer slot" 5
    else
        deny "Footer plugin does not register home_footer slot" 5
    fi
else
    deny "Footer plugin file does not exist (slot)" 5
fi

echo ""
echo "=== Fail-to-pass: Slot map and registry ==="

# [pr_diff] (0.05): home_footer slot must be declared in TuiSlotMap
node -e "
const fs = require('fs');
const src = fs.readFileSync('$SLOT_MAP', 'utf8');
if (/home_footer/.test(src)) process.exit(0);
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "home_footer slot declared in TuiSlotMap" 5
else
    deny "home_footer slot not declared in TuiSlotMap" 5
fi

# [pr_diff] (0.05): Footer plugin must be imported/registered in internal.ts
node -e "
const fs = require('fs');
const src = fs.readFileSync('$INTERNAL_TS', 'utf8');
// Accept any reference to the home footer plugin: path import, name reference, etc.
if (/home\/footer|home-footer|HomeFooter|homeFooter/i.test(src)) process.exit(0);
if (/feature-plugins.*footer/.test(src)) process.exit(0);
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "Footer plugin registered in internal.ts" 5
else
    deny "Footer plugin not registered in internal.ts" 5
fi

echo ""
echo "=== Pass-to-pass: Regression checks ==="

# [pr_diff] (0.05): home.tsx must still render Logo and Prompt components
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HOME_TSX', 'utf8');
// Check for JSX usage, not just string presence — must have <Logo or <Prompt
if (/<Logo[\s/>]/.test(src) && /<Prompt[\s/>]/.test(src)) process.exit(0);
// Also accept non-JSX references (Logo() call, etc.)
if (/Logo/.test(src) && /Prompt/.test(src)) process.exit(0);
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "home.tsx still renders Logo and Prompt" 5
else
    deny "home.tsx missing Logo or Prompt" 5
fi

# [pr_diff] (0.05): Existing internal plugins must still be registered
node -e "
const fs = require('fs');
const src = fs.readFileSync('$INTERNAL_TS', 'utf8');
if (/[Tt]ips/.test(src) && /[Ss]idebar.*[Ff]ooter|[Ff]ooter.*[Ss]idebar/.test(src)) process.exit(0);
if (/HomeTips/i.test(src) && /SidebarFooter/i.test(src)) process.exit(0);
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "Existing internal plugins still registered" 5
else
    deny "Existing internal plugins lost from registry" 5
fi

# [pr_diff] (0.05): Existing TuiSlotMap slots must still exist
node -e "
const fs = require('fs');
const src = fs.readFileSync('$SLOT_MAP', 'utf8');
const required = ['home_logo', 'home_prompt', 'home_bottom'];
const missing = required.filter(s => !new RegExp(s).test(src));
if (missing.length === 0) process.exit(0);
console.log('Missing slots: ' + missing.join(', '));
process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    award "Existing slots preserved in TuiSlotMap" 5
else
    deny "Existing slots missing from TuiSlotMap" 5
fi

echo ""
echo "=== Summary ==="
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4))")
echo "Score: $SCORE / $TOTAL"
echo "Reward: $REWARD"

# Compute component scores
BEHAVIORAL=$(python3 -c "print(round($SCORE * 0.85 / $TOTAL, 4))")
REGRESSION=$(python3 -c "print(round($SCORE * 0.15 / $TOTAL, 4))")

echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\":$REWARD,\"behavioral\":$BEHAVIORAL,\"regression\":$REGRESSION,\"config\":0,\"style_rubric\":0}" > /logs/verifier/reward.json

# LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
