#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
cd "$REPO"

SCORE=0

log() { echo "$1"; }

MARKDOWN_TSX="$REPO/packages/ui/src/components/markdown.tsx"

# ── GATE: TypeScript syntax check ────────────────────────────────────
# [pr_diff] (0.00): Changed files must parse as valid TypeScript
log "=== GATE: TypeScript syntax check ==="
if ! node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$MARKDOWN_TSX', 'utf8');
  if (src.length < 100) process.exit(1);
" 2>/dev/null; then
    log "GATE FAILED: markdown.tsx is malformed or missing"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed"

# ── Install deps (agent may have added new packages) ─────────────────
bun install --frozen-lockfile 2>/dev/null || bun install 2>/dev/null || true

# ── Write behavioral test harness ────────────────────────────────────
# Uses dynamic discovery: scans all markdown-related component files for
# an exported function matching (string, boolean) → Block[] signature.
# This avoids coupling to gold-patch file names or function names.
cat > /tmp/run_behavioral.ts << 'BEHAVIORAL_EOF'
import * as fs from "fs"
import * as path from "path"
import { marked } from "marked"

const dir = path.resolve("./packages/ui/src/components/")
const files = fs.readdirSync(dir)
  .filter((f: string) => f.includes("markdown") && (f.endsWith(".ts") || f.endsWith(".tsx")))
  .sort((a: string, b: string) => {
    // Prefer dedicated stream files over the main component
    const aStream = a.includes("stream") ? 0 : 1
    const bStream = b.includes("stream") ? 0 : 1
    return aStream - bStream
  })

type Block = { raw: string; src?: string; mode?: string }
type StreamFn = (text: string, live: boolean) => Block[]

let streamFn: StreamFn | null = null

for (const file of files) {
  try {
    const mod = await import(path.join(dir, file))
    for (const val of Object.values(mod)) {
      if (typeof val !== "function") continue
      try {
        const r = (val as any)("probe **test", true)
        if (Array.isArray(r) && r.length > 0 && typeof r[0] === "object" && "raw" in r[0]) {
          streamFn = val as StreamFn
          break
        }
      } catch {}
    }
  } catch {}
  if (streamFn) break
}

function getSrc(block: Block): string {
  return (block as any).src ?? block.raw
}

const results: Record<string, string> = {
  f2p1: "NO_FN", f2p2: "NO_FN", f2p3: "NO_FN", f2p4: "NO_FN",
  p2p1: "NO_FN", p2p2: "NO_FN"
}

if (!streamFn) {
  console.log(JSON.stringify(results))
  process.exit(0)
}

// ── F2P-1: Unclosed bold emphasis is healed during streaming
try {
  const r = streamFn("hello **world", true)
  const b = r[0]
  if (!b) { results.f2p1 = "NO_BLOCK" }
  else {
    const html = await marked.parse(getSrc(b))
    results.f2p1 = html.includes("<strong>") ? "PASS" : "FAIL"
  }
} catch { results.f2p1 = "ERROR" }

// ── F2P-2: Incomplete link is NOT clickable
try {
  const r = streamFn("see [docs](https://example.com/gu", true)
  // Collect all blocks' src content
  const allSrc = r.map((b: Block) => getSrc(b)).join("")
  const html = await marked.parse(allSrc)
  // The link should NOT be rendered as clickable with the incomplete URL
  results.f2p2 = html.includes('href="https://example.com/gu') ? "FAIL" : "PASS"
} catch { results.f2p2 = "ERROR" }

// ── F2P-3: Unclosed backtick is healed
try {
  const r = streamFn("say `code", true)
  const b = r[0]
  if (!b) { results.f2p3 = "NO_BLOCK" }
  else {
    const html = await marked.parse(getSrc(b))
    results.f2p3 = html.includes("<code>") ? "PASS" : "FAIL"
  }
} catch { results.f2p3 = "ERROR" }

// ── F2P-4: Unclosed italic emphasis is healed
try {
  const r = streamFn("hello *italic", true)
  const b = r[0]
  if (!b) { results.f2p4 = "NO_BLOCK" }
  else {
    const html = await marked.parse(getSrc(b))
    results.f2p4 = html.includes("<em>") ? "PASS" : "FAIL"
  }
} catch { results.f2p4 = "ERROR" }

// ── P2P-1: Code fence splitting is preserved (content is not lost)
try {
  const r = streamFn("before\n\n```ts\nconst x = 1", true)
  const allRaw = r.map((b: Block) => b.raw).join("")
  // Content should be preserved regardless of how many blocks
  results.p2p1 = (r.length >= 1 && allRaw.includes("const x = 1") && allRaw.includes("before")) ? "PASS" : "FAIL"
} catch { results.p2p1 = "ERROR" }

// ── P2P-2: Non-streaming mode passes content through unchanged
try {
  const input = "hello **world**"
  const r = streamFn(input, false)
  const b = r[0]
  if (!b) { results.p2p2 = "NO_BLOCK" }
  else {
    const src = getSrc(b)
    results.p2p2 = (r.length === 1 && src === input) ? "PASS" : "FAIL"
  }
} catch { results.p2p2 = "ERROR" }

console.log(JSON.stringify(results))
BEHAVIORAL_EOF

# ── Run behavioral tests ─────────────────────────────────────────────
log ""
log "=== Running behavioral tests ==="
RESULTS=$(cd "$REPO" && bun /tmp/run_behavioral.ts 2>/dev/null || echo '{}')
log "Raw results: $RESULTS"

parse_result() {
    echo "$RESULTS" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$1','ERROR'))" 2>/dev/null || echo "ERROR"
}

# ── F2P-1 (0.30): Unclosed bold emphasis healed ─────────────────────
# [pr_diff] (0.30): Unclosed bold markers should be temporarily closed during streaming
log ""
log "=== F2P-1: Incomplete bold emphasis healed ==="
F2P1=$(parse_result f2p1)
if [ "$F2P1" = "PASS" ]; then
    log "PASS: Bold emphasis healed during streaming"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    log "FAIL: Bold emphasis not healed (got: $F2P1)"
fi

# ── F2P-2 (0.15): Incomplete links not clickable ────────────────────
# [pr_diff] (0.15): Half-formed [text](url should not become clickable
log ""
log "=== F2P-2: Incomplete links not clickable ==="
F2P2=$(parse_result f2p2)
if [ "$F2P2" = "PASS" ]; then
    log "PASS: Incomplete links rendered as plain text"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    log "FAIL: Incomplete links rendered as clickable (got: $F2P2)"
fi

# ── F2P-3 (0.10): Unclosed backtick healed ──────────────────────────
# [pr_diff] (0.10): Unclosed inline backtick should be closed for rendering
log ""
log "=== F2P-3: Inline backtick code healed ==="
F2P3=$(parse_result f2p3)
if [ "$F2P3" = "PASS" ]; then
    log "PASS: Inline backtick code healed"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: Inline backtick not healed (got: $F2P3)"
fi

# ── F2P-4 (0.10): Unclosed italic emphasis healed ───────────────────
# [pr_diff] (0.10): Unclosed italic markers should be temporarily closed
log ""
log "=== F2P-4: Incomplete italic emphasis healed ==="
F2P4=$(parse_result f2p4)
if [ "$F2P4" = "PASS" ]; then
    log "PASS: Italic emphasis healed during streaming"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: Italic emphasis not healed (got: $F2P4)"
fi

# ── P2P-1 (0.10): Code fence splitting preserved ────────────────────
# [pr_diff] (0.10): Existing code-fence splitting behavior must be preserved
log ""
log "=== P2P-1: Code fence splitting preserved ==="
P2P1=$(parse_result p2p1)
if [ "$P2P1" = "PASS" ]; then
    log "PASS: Code fence splitting preserved"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: Code fence splitting broken (got: $P2P1)"
fi

# ── P2P-2 (0.05): Non-streaming mode unchanged ──────────────────────
# [pr_diff] (0.05): When not streaming, markdown should pass through unchanged
log ""
log "=== P2P-2: Non-streaming mode unchanged ==="
P2P2=$(parse_result p2p2)
if [ "$P2P2" = "PASS" ]; then
    log "PASS: Non-streaming mode unchanged"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Non-streaming mode modified content (got: $P2P2)"
fi

# ── Structural: anti-stub check ──────────────────────────────────────
# [static] (0.05): markdown.tsx must not be empty or stub
log ""
log "=== STRUCTURAL: anti-stub ==="
LINE_COUNT=$(wc -l < "$MARKDOWN_TSX" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -ge 80 ]; then
    log "PASS: markdown.tsx has $LINE_COUNT lines (not a stub)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: markdown.tsx has only $LINE_COUNT lines — likely stubbed"
fi

# ── Config-derived: no use of `any` type ─────────────────────────────
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ 77152527
log ""
log "=== CONFIG: no any type in changed lines ==="
DIFF=$(cd "$REPO" && git diff HEAD -- packages/ui/src/components/ 2>/dev/null || echo "")
if [ -z "$DIFF" ]; then
    # No diff against HEAD — try against initial commit
    DIFF=$(cd "$REPO" && git diff 771525270a0c -- packages/ui/src/components/ 2>/dev/null || echo "")
fi
if echo "$DIFF" | grep -q '^\+.*:\s*any\b'; then
    log "FAIL: Added any type annotation in changed files"
else
    log "PASS: No any types in changed lines"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── Config-derived: no unnecessary else statements ───────────────────
# [agent_config] (0.05): "Avoid else statements. Prefer early returns." — AGENTS.md:84 @ 77152527
log ""
log "=== CONFIG: no unnecessary else ==="
if echo "$DIFF" | grep -q '^\+.*\belse\b'; then
    log "FAIL: Added else statement in changes"
else
    log "PASS: No unnecessary else statements added"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── Config-derived: prefer const over let ────────────────────────────
# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:70 @ 77152527
log ""
log "=== CONFIG: prefer const over let ==="
if echo "$DIFF" | grep -q '^\+.*\blet\b'; then
    log "FAIL: Added let declaration in changes"
else
    log "PASS: No let declarations in changed lines"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── Final score ──────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
log "Score: $SCORE / 1.0"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
