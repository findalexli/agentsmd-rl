#!/usr/bin/env bash
set +e

REWARD=0
TARGET="/repo/js/tabs/Index.svelte"

# ── GATE: file exists and is a Svelte component ─────────────────────
# [pr_diff] (gate): Index.svelte must exist with Svelte structure
if [ ! -s "$TARGET" ]; then
    echo "GATE FAILED: $TARGET missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! grep -q '<script' "$TARGET"; then
    echo "GATE FAILED: not a valid Svelte component"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE: PASS"

# ── F2P 1 (0.55): Walkthrough uses two-way binding for selected ─────
# [pr_diff] (0.55): The <Walkthrough> component must use bind:selected
# to sync selected-tab state back to parent. Without this, parent
# state diverges when stepper buttons change tabs internally, causing
# re-navigation to silently fail (no-change detected).
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// Strip HTML comments to block comment-injection gaming
const clean = src.replace(/<!--[\s\S]*?-->/g, '');
// Find <Walkthrough ...> tags and check for bind:selected attribute
const tags = [...clean.matchAll(/<Walkthrough\b([^>]*?)>/gs)];
if (tags.length === 0) {
    console.log('No <Walkthrough> tag found');
    process.exit(1);
}
const ok = tags.some(m => /\bbind:selected\b/.test(m[1]));
if (!ok) {
    console.log('Walkthrough tag(s) found but none have bind:selected');
    process.exit(1);
}
" "$TARGET"
if [ $? -eq 0 ]; then
    echo "F2P 1: PASS — Walkthrough uses bind:selected (two-way binding)"
    REWARD=$(python3 -c "print($REWARD + 0.55)")
else
    echo "F2P 1: FAIL — Walkthrough does not use bind:selected"
fi

# ── F2P 2 (0.10): Buggy one-way selected= pattern removed ───────────
# [pr_diff] (0.10): <Walkthrough> must NOT retain a bare selected= prop
# (without bind:), which is the exact root cause of the bug — parent
# never receives child state updates through one-way prop passing.
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const clean = src.replace(/<!--[\s\S]*?-->/g, '');
const tags = [...clean.matchAll(/<Walkthrough\b([^>]*?)>/gs)];
if (tags.length === 0) { process.exit(1); }
// Check that no Walkthrough tag has bare selected= (without bind:)
for (const m of tags) {
    // Replace bind:selected so it won't false-match
    const attrs = m[1].replace(/bind:selected/g, '__BOUND__');
    if (/\bselected\s*[={]/.test(attrs)) {
        console.log('Buggy one-way selected= still present on Walkthrough');
        process.exit(1);
    }
}
" "$TARGET"
if [ $? -eq 0 ]; then
    echo "F2P 2: PASS — No one-way selected= on Walkthrough"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "F2P 2: FAIL — Walkthrough still has one-way selected="
fi

# ── P2P 1 (0.10): Tabs still uses bind:selected ─────────────────────
# [pr_diff] (0.10): Regular Tabs component must retain its bind:selected
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const clean = src.replace(/<!--[\s\S]*?-->/g, '');
const tags = [...clean.matchAll(/<Tabs\b([^>]*?)>/gs)];
const ok = tags.some(m => /\bbind:selected\b/.test(m[1]));
process.exit(ok ? 0 : 1);
" "$TARGET"
if [ $? -eq 0 ]; then
    echo "P2P 1: PASS — Tabs retains bind:selected"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "P2P 1: FAIL — Tabs lost bind:selected"
fi

# ── P2P 2 (0.05): Both component branches present ───────────────────
# [pr_diff] (0.05): File must still render both Walkthrough and Tabs
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const clean = src.replace(/<!--[\s\S]*?-->/g, '');
const ok = /<Walkthrough\b/.test(clean) && /<Tabs\b/.test(clean);
process.exit(ok ? 0 : 1);
" "$TARGET"
if [ $? -eq 0 ]; then
    echo "P2P 2: PASS — Both Walkthrough and Tabs present"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "P2P 2: FAIL — Missing Walkthrough or Tabs"
fi

# ── Anti-stub 1 (0.10): Event dispatches preserved ──────────────────
# [pr_diff] (0.10): File must still dispatch change and select events
node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const clean = src.replace(/<!--[\s\S]*?-->/g, '');
const ok = /dispatch\(['\x22]change['\x22]/.test(clean)
        && /dispatch\(['\x22]select['\x22]/.test(clean);
process.exit(ok ? 0 : 1);
" "$TARGET"
if [ $? -eq 0 ]; then
    echo "ANTI-STUB 1: PASS — Event dispatches preserved"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "ANTI-STUB 1: FAIL — Event dispatches missing"
fi

# ── Anti-stub 2 (0.10): File not truncated ───────────────────────────
# [pr_diff] (0.10): Original file is ~50 lines; must not be gutted
LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -ge 30 ]; then
    echo "ANTI-STUB 2: PASS — File has $LINE_COUNT lines"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "ANTI-STUB 2: FAIL — File only has $LINE_COUNT lines"
fi

# ── Final score ───────────────────────────────────────────────────
echo ""
echo "TOTAL: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
score = $REWARD
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.65), 4),
    'regression': round(max(min(score - 0.65, 0.15), 0), 4),
    'anti_stub': round(max(min(score - 0.80, 0.20), 0), 4),
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
