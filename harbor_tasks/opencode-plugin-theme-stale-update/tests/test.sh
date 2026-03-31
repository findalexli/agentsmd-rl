#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
PKG="$REPO/packages/opencode"
SCORE=0
TOTAL=0

log() { echo "  $1"; }
pass() { log "PASS: $1"; SCORE=$(python3 -c "print($SCORE + $2)"); TOTAL=$(python3 -c "print($TOTAL + $2)"); }
fail() { log "FAIL: $1"; TOTAL=$(python3 -c "print($TOTAL + $2)"); }

mkdir -p /logs/verifier

# ─── GATE: Syntax check ──────────────────────────────────────────────
echo "=== GATE: Syntax check ==="
# [static] (0.00): Changed files must exist and not be empty
GATE_PASS=true
for f in \
  packages/opencode/src/util/filesystem.ts \
  packages/opencode/src/plugin/meta.ts \
  packages/opencode/src/cli/cmd/tui/context/theme.tsx \
  packages/opencode/src/cli/cmd/tui/plugin/runtime.ts; do
  if [ ! -f "$REPO/$f" ] || [ ! -s "$REPO/$f" ]; then
    log "GATE FAIL: $f missing or empty"
    GATE_PASS=false
    break
  fi
done
if [ "$GATE_PASS" = "false" ]; then
  echo "0" > /logs/verifier/reward.txt
  echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
  exit 0
fi
log "GATE PASS"

# ─── Fail-to-pass: Behavioral checks ─────────────────────────────────
echo ""
echo "=== Fail-to-pass: Behavioral checks ==="

# [pr_diff] (0.20): Filesystem.statAsync returns stat for existing files and undefined for missing
mkdir -p "$PKG/test/_verifier"
cat > "$PKG/test/_verifier/statAsync.ts" << 'BEOF'
import { Filesystem } from "@/util/filesystem"
import * as fs from "fs/promises"
import * as os from "os"
import * as path from "path"

const tmp = path.join(os.tmpdir(), `stat-test-${Date.now()}`)
await fs.writeFile(tmp, "hello world")
try {
  const stat = await Filesystem.statAsync(tmp)
  if (!stat) { console.error("returned undefined for existing file"); process.exit(1) }
  if (stat.size !== 11) { console.error(`expected size 11, got ${stat.size}`); process.exit(1) }
  const missing = await Filesystem.statAsync(`/tmp/no-such-${Date.now()}`)
  if (missing !== undefined) { console.error("should return undefined for missing"); process.exit(1) }
} finally {
  await fs.unlink(tmp).catch(() => {})
}
BEOF
cd "$PKG"
if bun run test/_verifier/statAsync.ts > /dev/null 2>&1; then
  pass "Filesystem.statAsync works correctly" 0.20
else
  fail "Filesystem.statAsync not working" 0.20
fi

# [pr_diff] (0.30): upsertTheme adds new themes AND updates existing ones
# Tests the full behavioral contract: validation, add path, and update path.
# Any correct implementation (setdefault, map replace, etc.) should pass.
cat > "$PKG/test/_verifier/upsertTheme.ts" << 'BEOF'
import { addTheme, hasTheme } from "@/cli/cmd/tui/context/theme"

const mod = await import("@/cli/cmd/tui/context/theme")
const upsertTheme = mod.upsertTheme
if (typeof upsertTheme !== "function") {
  console.error("upsertTheme not exported as a function")
  process.exit(1)
}

// --- Validation: must reject bad input ---
if (upsertTheme("", {}) !== false) {
  console.error("should return false for empty name")
  process.exit(1)
}
if (upsertTheme("test", "not-a-theme") !== false) {
  console.error("should return false for non-theme data")
  process.exit(1)
}

// --- Find a valid theme structure ---
// Try to load an existing theme file from the repo, or probe isTheme
import * as fs from "fs/promises"
import * as path from "path"

async function findValidTheme(): Promise<unknown> {
  // Check for theme files in the repo
  const dirs = [
    "/workspace/opencode/packages/opencode/themes",
    "/workspace/opencode/themes",
    "/workspace/opencode/packages/opencode/src/cli/cmd/tui/context",
  ]
  for (const dir of dirs) {
    try {
      const files = await fs.readdir(dir)
      for (const f of files) {
        if (f.endsWith(".json")) {
          const content = await fs.readFile(path.join(dir, f), "utf8")
          const parsed = JSON.parse(content)
          // Verify this passes addTheme validation
          const tmpName = `_probe_${Date.now()}_${Math.random()}`
          if (addTheme(tmpName, parsed)) return parsed
        }
      }
    } catch {}
  }
  // Probe common theme structures using addTheme (which uses same isTheme)
  const candidates = [
    { colors: { primary: "#000" }, defs: {} },
    { defs: {} },
    { dark: {}, light: {} },
    {},
  ]
  for (const c of candidates) {
    const tmpName = `_probe_${Date.now()}_${Math.random()}`
    if (addTheme(tmpName, c)) return c
  }
  return null
}

const validTheme = await findValidTheme()
if (!validTheme) {
  console.error("Could not discover a valid theme structure — cannot test upsert behavior")
  process.exit(1)
}

// --- ADD path: upsertTheme adds a new theme ---
const name = `_verifier_upsert_${Date.now()}`
const addResult = upsertTheme(name, validTheme)
if (addResult !== true) {
  console.error("upsertTheme returned false for valid theme (add path)")
  process.exit(1)
}
if (!hasTheme(name)) {
  console.error("hasTheme returns false after upsertTheme (theme not registered)")
  process.exit(1)
}

// --- UPDATE path: upsertTheme updates an already-registered theme ---
// This is the CORE behavior — addTheme would skip, but upsertTheme must succeed
const updateResult = upsertTheme(name, validTheme)
if (updateResult !== true) {
  console.error("upsertTheme returned false on second call (update path not working)")
  process.exit(1)
}
BEOF
if bun run test/_verifier/upsertTheme.ts > /dev/null 2>&1; then
  pass "upsertTheme adds and updates themes" 0.30
else
  fail "upsertTheme not working correctly" 0.30
fi

# [pr_diff] (0.10): PluginMeta.setTheme is callable and handles missing IDs gracefully
cat > "$PKG/test/_verifier/setTheme.ts" << 'BEOF'
import { PluginMeta } from "@/plugin/meta"

if (typeof PluginMeta.setTheme !== "function") {
  console.error("PluginMeta.setTheme not exported as function")
  process.exit(1)
}

// Call with a nonexistent plugin ID — should not throw (graceful no-op)
try {
  await PluginMeta.setTheme("_verifier_nonexistent_plugin", "test-theme", {
    src: "/tmp/test-theme.json",
    dest: "/tmp/dest-theme.json",
    mtime: Date.now(),
    size: 42,
  })
} catch (e: any) {
  console.error("setTheme threw when called with nonexistent plugin ID:", e?.message ?? e)
  process.exit(1)
}
BEOF
if bun run test/_verifier/setTheme.ts > /dev/null 2>&1; then
  pass "PluginMeta.setTheme exported and callable" 0.10
else
  fail "PluginMeta.setTheme not working" 0.10
fi

# ─── Pass-to-pass: Regression checks ─────────────────────────────────
echo ""
echo "=== Pass-to-pass: Regression checks ==="

# [repo_tests] (0.15): Existing plugin-loader tests still pass
cd "$PKG"
if timeout 60 bun test test/cli/tui/plugin-loader.test.ts > /dev/null 2>&1; then
  pass "Existing plugin-loader tests pass" 0.15
else
  fail "Existing plugin-loader tests broken" 0.15
fi

# ─── Structural: Anti-stub ────────────────────────────────────────────
echo ""
echo "=== Structural: Anti-stub ==="

# [static] (0.10): Changed files are not stubbed or truncated
STUB_OK=true
for f in \
  src/util/filesystem.ts \
  src/plugin/meta.ts \
  src/cli/cmd/tui/context/theme.tsx \
  src/cli/cmd/tui/plugin/runtime.ts; do
  lines=$(wc -l < "$PKG/$f" 2>/dev/null || echo "0")
  if [ "$lines" -lt 50 ]; then
    log "WARN: $f has only $lines lines — likely stubbed"
    STUB_OK=false
  fi
done
if [ "$STUB_OK" = "true" ]; then
  pass "No files appear stubbed" 0.10
else
  fail "One or more files appear stubbed" 0.10
fi

# ─── Config-derived checks ───────────────────────────────────────────
echo ""
echo "=== Config-derived checks ==="

# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13
ANY_FOUND=false
for f in \
  "$PKG/src/util/filesystem.ts" \
  "$PKG/src/plugin/meta.ts" \
  "$PKG/src/cli/cmd/tui/context/theme.tsx" \
  "$PKG/src/cli/cmd/tui/plugin/runtime.ts"; do
  if grep -Pn ':\s*any\b|<any>' "$f" 2>/dev/null | grep -v '// eslint-disable' > /dev/null; then
    ANY_FOUND=true
    break
  fi
done
if [ "$ANY_FOUND" = "false" ]; then
  pass "No explicit 'any' type annotations" 0.05
else
  fail "'any' type found in changed files" 0.05
fi

# [agent_config] (0.05): "Prefer `const` over `let`" — AGENTS.md:69
LET_COUNT=0
for f in \
  "$PKG/src/util/filesystem.ts" \
  "$PKG/src/plugin/meta.ts" \
  "$PKG/src/cli/cmd/tui/context/theme.tsx" \
  "$PKG/src/cli/cmd/tui/plugin/runtime.ts"; do
  cnt=$(grep -c '\blet\b' "$f" 2>/dev/null || echo "0")
  LET_COUNT=$((LET_COUNT + cnt))
done
if [ "$LET_COUNT" -lt 10 ]; then
  pass "Minimal let usage (const preferred)" 0.05
else
  fail "Excessive let usage ($LET_COUNT occurrences)" 0.05
fi

# [pr_diff] (0.05): Theme installer references plugin state for conditional update
# Structural — createThemeInstaller is a non-exported closure, cannot be called directly.
# Check that runtime.ts both checks plugin state AND uses upsertTheme.
RUNTIME="$PKG/src/cli/cmd/tui/plugin/runtime.ts"
HAS_STATE_REF=false
HAS_UPSERT_REF=false
if grep -qP '\.state\b|meta\s*\.\s*state|plugin.*state' "$RUNTIME" 2>/dev/null; then
  HAS_STATE_REF=true
fi
if grep -q 'upsertTheme' "$RUNTIME" 2>/dev/null; then
  HAS_UPSERT_REF=true
fi
if [ "$HAS_STATE_REF" = "true" ] && [ "$HAS_UPSERT_REF" = "true" ]; then
  pass "Theme installer uses plugin state and upsertTheme" 0.05
else
  fail "Theme installer missing state or upsertTheme integration" 0.05
fi

# ─── Final Score ──────────────────────────────────────────────────────
echo ""
echo "=== Final Score ==="
echo "Score: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

# Clean up verifier test files
rm -rf "$PKG/test/_verifier" 2>/dev/null || true

python3 -c "
import json
score = float('$SCORE')
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.75), 4),
    'regression': round(min(max(score - 0.75, 0), 0.15), 4),
    'config': round(min(max(score - 0.90, 0), 0.10), 4),
    'style_rubric': 0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
