#!/usr/bin/env bash
set -euo pipefail

TOTAL=0
TARGET_FILE="js/_website/functions/_shared.ts"

cd /repo

# ──────────────────────────────────────────────
# GATE: TypeScript must be valid
# [pr_diff] (0.00): File must parse as valid TypeScript
# ──────────────────────────────────────────────
echo "=== GATE: TypeScript syntax check ==="
if ! npx tsx --eval "await import('/repo/$TARGET_FILE')" 2>/dev/null; then
    echo "GATE FAILED: TypeScript file has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ──────────────────────────────────────────────
# Behavioral 1: serveDocMarkdown returns 302 redirect for LLM UA
# [pr_diff] (0.30): Doc handler must redirect instead of proxying
# ──────────────────────────────────────────────
echo ""
echo "=== Behavioral: serveDocMarkdown returns redirect ==="
cat > /tmp/test_doc_redirect.mjs << 'EOF'
const mod = await import('/repo/js/_website/functions/_shared.ts');
const req = new Request('https://example.com/docs/textbox', {
    headers: { 'user-agent': 'claudebot' }
});
let nextCalled = false;
const ctx = {
    request: req,
    params: { doc: 'textbox' },
    next: () => { nextCalled = true; return new Response('fallthrough', { status: 200 }); }
};
try {
    const res = await mod.serveDocMarkdown(ctx);
    const loc = res.headers.get('location') || '';
    if (res.status >= 300 && res.status < 400 && loc.includes('/api/markdown/textbox')) {
        process.stdout.write('PASS');
    } else {
        process.stdout.write('FAIL');
    }
} catch (e) {
    process.stdout.write('FAIL');
}
EOF

RESULT=$(timeout 15 npx tsx /tmp/test_doc_redirect.mjs 2>/dev/null || echo "FAIL")
if [[ "$RESULT" == *"PASS"* ]]; then
    echo "PASS (0.30)"
    TOTAL=$((TOTAL + 30))
else
    echo "FAIL"
fi

# ──────────────────────────────────────────────
# Behavioral 2: serveGuideMarkdown returns 302 redirect for LLM UA
# [pr_diff] (0.30): Guide handler must redirect instead of proxying
# ──────────────────────────────────────────────
echo ""
echo "=== Behavioral: serveGuideMarkdown returns redirect ==="
cat > /tmp/test_guide_redirect.mjs << 'EOF'
const mod = await import('/repo/js/_website/functions/_shared.ts');
const req = new Request('https://example.com/guides/quickstart', {
    headers: { 'user-agent': 'claudebot' }
});
let nextCalled = false;
const ctx = {
    request: req,
    params: { guide: 'quickstart' },
    next: () => { nextCalled = true; return new Response('fallthrough', { status: 200 }); }
};
try {
    const res = await mod.serveGuideMarkdown(ctx);
    const loc = res.headers.get('location') || '';
    if (res.status >= 300 && res.status < 400 && loc.includes('/api/markdown/guide/quickstart')) {
        process.stdout.write('PASS');
    } else {
        process.stdout.write('FAIL');
    }
} catch (e) {
    process.stdout.write('FAIL');
}
EOF

RESULT=$(timeout 15 npx tsx /tmp/test_guide_redirect.mjs 2>/dev/null || echo "FAIL")
if [[ "$RESULT" == *"PASS"* ]]; then
    echo "PASS (0.30)"
    TOTAL=$((TOTAL + 30))
else
    echo "FAIL"
fi

# ──────────────────────────────────────────────
# Pass-to-pass 1: Non-LLM requests fall through to next()
# [pr_diff] (0.15): Non-LLM UA must still call next()
# ──────────────────────────────────────────────
echo ""
echo "=== Pass-to-pass: Non-LLM requests fall through ==="
cat > /tmp/test_non_llm.mjs << 'EOF'
const mod = await import('/repo/js/_website/functions/_shared.ts');
const req = new Request('https://example.com/docs/textbox', {
    headers: { 'user-agent': 'Mozilla/5.0 Chrome/120' }
});
let nextCalled = false;
const ctx = {
    request: req,
    params: { doc: 'textbox' },
    next: () => { nextCalled = true; return new Response('normal page', { status: 200 }); }
};
const res = await mod.serveDocMarkdown(ctx);
if (nextCalled && res.status === 200) {
    process.stdout.write('PASS');
} else {
    process.stdout.write('FAIL');
}
EOF

RESULT=$(timeout 15 npx tsx /tmp/test_non_llm.mjs 2>/dev/null || echo "FAIL")
if [[ "$RESULT" == *"PASS"* ]]; then
    echo "PASS (0.15)"
    TOTAL=$((TOTAL + 15))
else
    echo "FAIL"
fi

# ──────────────────────────────────────────────
# Pass-to-pass 2: Accept: text/markdown header still triggers LLM path
# [pr_diff] (0.10): Accept header detection preserved
# ──────────────────────────────────────────────
echo ""
echo "=== Pass-to-pass: Accept header triggers LLM path ==="
cat > /tmp/test_accept.mjs << 'EOF'
const mod = await import('/repo/js/_website/functions/_shared.ts');
const req = new Request('https://example.com/docs/textbox', {
    headers: { 'user-agent': 'Mozilla/5.0', 'accept': 'text/markdown' }
});
let nextCalled = false;
const ctx = {
    request: req,
    params: { doc: 'textbox' },
    next: () => { nextCalled = true; return new Response('fallthrough', { status: 200 }); }
};
try {
    const res = await mod.serveDocMarkdown(ctx);
    // Should NOT fall through — should handle as LLM request
    if (!nextCalled && res.status >= 300 && res.status < 400) {
        process.stdout.write('PASS');
    } else {
        process.stdout.write('FAIL');
    }
} catch (e) {
    process.stdout.write('FAIL');
}
EOF

RESULT=$(timeout 15 npx tsx /tmp/test_accept.mjs 2>/dev/null || echo "FAIL")
if [[ "$RESULT" == *"PASS"* ]]; then
    echo "PASS (0.10)"
    TOTAL=$((TOTAL + 10))
else
    echo "FAIL"
fi

# ──────────────────────────────────────────────
# Anti-stub: Functions are exported and callable
# [pr_diff] (0.10): Functions must still be exported async functions
# ──────────────────────────────────────────────
echo ""
echo "=== Structural: Functions exported and callable ==="
cat > /tmp/test_exports.mjs << 'EOF'
const mod = await import('/repo/js/_website/functions/_shared.ts');
if (typeof mod.serveDocMarkdown === 'function' && typeof mod.serveGuideMarkdown === 'function') {
    process.stdout.write('PASS');
} else {
    process.stdout.write('FAIL');
}
EOF

RESULT=$(timeout 15 npx tsx /tmp/test_exports.mjs 2>/dev/null || echo "FAIL")
if [[ "$RESULT" == *"PASS"* ]]; then
    echo "PASS (0.10)"
    TOTAL=$((TOTAL + 10))
else
    echo "FAIL"
fi

# ──────────────────────────────────────────────
# Config-derived: TypeScript style consistency
# [agent_config] (0.05): "Be consistent with the style of the surrounding code." — AGENTS.md:45 @ e900202
# ──────────────────────────────────────────────
echo ""
echo "=== Config: TypeScript file uses tabs (matching repo style) ==="
# The repo uses tabs for indentation in this file
if grep -P '^\t' "$TARGET_FILE" | head -1 >/dev/null 2>&1; then
    echo "PASS (0.05)"
    TOTAL=$((TOTAL + 5))
else
    echo "FAIL: File does not use tab indentation"
fi

# ──────────────────────────────────────────────
# Final score
# ──────────────────────────────────────────────
echo ""
echo "=== Final Score ==="
SCORE=$(python3 -c "print(f'{$TOTAL / 100:.2f}')")
echo "Total: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json breakdown
BEH=$(python3 -c "print(f'{min($TOTAL, 60) / 100:.2f}')")
REG=$(python3 -c "t=$TOTAL; beh=min(t,60); left=t-beh; print(f'{min(left,25)/100:.2f}')")
CFG=$(python3 -c "t=$TOTAL; print(f'{max(0, t-85)/100:.2f}')")
echo "{\"reward\":$SCORE,\"behavioral\":$BEH,\"regression\":$REG,\"config\":$CFG,\"style_rubric\":0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
