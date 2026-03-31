#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

BUILD_COMPLETE="packages/next/src/build/adapter/build-complete.ts"
BUILD_INDEX="packages/next/src/build/index.ts"

add_score() {
  local weight="$1"
  local pass="$2"
  local desc="$3"
  TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
  if [ "$pass" = "1" ]; then
    SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
    echo "PASS ($weight): $desc"
  else
    echo "FAIL ($weight): $desc"
  fi
}

# ── GATE: TypeScript syntax check ────────────────────────────────────
# [pr_diff] (gate): Modified files must parse without syntax errors
GATE_OK=0
node -e "
  const fs = require('fs');
  const ts = require(require.resolve('typescript', {paths: ['/repo']}));
  for (const f of ['$BUILD_COMPLETE', '$BUILD_INDEX']) {
    const src = fs.readFileSync(f, 'utf8');
    ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
  }
  console.log('syntax ok');
" 2>/dev/null && GATE_OK=1

if [ "$GATE_OK" != "1" ]; then
  echo "GATE FAIL: TypeScript syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: TypeScript syntax valid"

# ── GATE: Anti-stub — files must retain substantial content ──────────
# [pr_diff] (gate): build-complete.ts is ~2200 lines; a stub is not a valid fix
BC_LINES=$(wc -l < "$BUILD_COMPLETE" 2>/dev/null || echo 0)
BI_LINES=$(wc -l < "$BUILD_INDEX" 2>/dev/null || echo 0)
if [ "$BC_LINES" -lt 1500 ] || [ "$BI_LINES" -lt 300 ]; then
  echo "GATE FAIL: Files too short (stub detected). build-complete=${BC_LINES}L, index=${BI_LINES}L"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: File lengths plausible (build-complete=${BC_LINES}L, index=${BI_LINES}L)"

# ══════════════════════════════════════════════════════════════════════
# DEAD CODE REMOVAL CHECKS (0.55 total)
# These verify the dead code paths were removed. Since both branches of
# the original ternary are identical, removing the dead conditional is
# the only meaningful change. We test the ABSENCE of dead code tokens.
# ══════════════════════════════════════════════════════════════════════

# [pr_diff] (0.15): hasFallbackRootParams destructuring removed from build-complete.ts
# The route destructuring should no longer include this field.
if ! grep -q 'hasFallbackRootParams' "$BUILD_COMPLETE"; then
  add_score 0.15 1 "hasFallbackRootParams not referenced in build-complete.ts"
else
  add_score 0.15 0 "hasFallbackRootParams still referenced in build-complete.ts"
fi

# [pr_diff] (0.15): shouldSkipSuffixes variable removed from build-complete.ts
if ! grep -q 'shouldSkipSuffixes' "$BUILD_COMPLETE"; then
  add_score 0.15 1 "shouldSkipSuffixes not referenced in build-complete.ts"
else
  add_score 0.15 0 "shouldSkipSuffixes still referenced in build-complete.ts"
fi

# [pr_diff] (0.10): Ternary with identical branches replaced — no ternary around rscSuffix regex
# We verify no ternary operator appears on the same line as the rscSuffix regex pattern,
# which would indicate the dead conditional is still present.
if python3 -c "
import re
src = open('$BUILD_COMPLETE').read()
# Check: rscSuffix regex still exists (the pattern itself is not dead code)
assert 'rscSuffix' in src, 'rscSuffix regex missing'
# Check: no ternary around the rscSuffix regex (the dead conditional)
# Look for '? ..rscSuffix..' or 'shouldSkipSuffixes' near a ternary
lines = src.splitlines()
for line in lines:
    if 'rscSuffix' in line and '?' in line and ':' in line:
        # Ternary still wraps the regex
        exit(1)
" 2>/dev/null; then
  add_score 0.10 1 "RSC suffix regex used directly without dead ternary"
else
  add_score 0.10 0 "RSC suffix regex still has ternary or is missing"
fi

# [pr_diff] (0.15): hasFallbackRootParams removed from ManifestRoute type in build/index.ts
if ! grep -q 'hasFallbackRootParams' "$BUILD_INDEX"; then
  add_score 0.15 1 "hasFallbackRootParams removed from ManifestRoute type"
else
  add_score 0.15 0 "hasFallbackRootParams still in ManifestRoute type"
fi

# ══════════════════════════════════════════════════════════════════════
# PASS-TO-PASS: Code integrity checks (0.45 total)
# Since this is dead code removal with NO behavioral change, we invest
# heavily in verifying the surrounding code is intact and functional.
# ══════════════════════════════════════════════════════════════════════

# [pr_diff] (0.05): handleBuildComplete export preserved
if grep -q 'export async function handleBuildComplete' "$BUILD_COMPLETE"; then
  add_score 0.05 1 "handleBuildComplete export preserved"
else
  add_score 0.05 0 "handleBuildComplete export missing"
fi

# [pr_diff] (0.05): ManifestRoute type still exported
if grep -q 'export type ManifestRoute' "$BUILD_INDEX"; then
  add_score 0.05 1 "ManifestRoute type export preserved"
else
  add_score 0.05 0 "ManifestRoute type export missing"
fi

# [pr_diff] (0.05): rscSuffix regex pattern still present in build-complete
if grep -q 'rscSuffix' "$BUILD_COMPLETE"; then
  add_score 0.05 1 "rscSuffix regex pattern preserved"
else
  add_score 0.05 0 "rscSuffix regex pattern missing"
fi

# [pr_diff] (0.05): sourceRegex.replace call still present (core logic intact)
if grep -q 'sourceRegex\.replace\|sourceRegex.replace' "$BUILD_COMPLETE"; then
  add_score 0.05 1 "sourceRegex.replace call preserved"
else
  add_score 0.05 0 "sourceRegex.replace call missing"
fi

# [pr_diff] (0.05): The actual RSC suffix regex string is intact
# This is the regex that both ternary branches had — it must survive the refactor
if grep -q '\\\\\.rsc|.*\\.segment\\.rsc' "$BUILD_COMPLETE"; then
  add_score 0.05 1 "RSC suffix regex string intact"
else
  add_score 0.05 0 "RSC suffix regex string altered or missing"
fi

# [pr_diff] (0.10): TypeScript type-check passes (stronger than parse-only)
# Attempt tsc --noEmit on the two changed files. This catches type errors
# that a parse-only check would miss (e.g., referencing removed types).
TSC_OK=0
if [ -f "node_modules/.bin/tsc" ] || command -v npx >/dev/null 2>&1; then
  # Try project-level tsc first
  cd /repo
  npx --yes tsc --noEmit --pretty false "$BUILD_COMPLETE" "$BUILD_INDEX" 2>/dev/null && TSC_OK=1
  # If single-file tsc fails (common with project refs), try full project check
  if [ "$TSC_OK" != "1" ]; then
    # Fall back to just verifying no new parse diagnostics via ts API
    node -e "
      const fs = require('fs');
      const ts = require(require.resolve('typescript', {paths: ['/repo']}));
      const files = ['$BUILD_COMPLETE', '$BUILD_INDEX'];
      for (const f of files) {
        const src = fs.readFileSync(f, 'utf8');
        const sf = ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
        const diags = ts.getPreEmitDiagnostics(
          ts.createProgram([f], {noEmit: true, strict: true, target: ts.ScriptTarget.Latest, module: ts.ModuleKind.ESNext}),
          sf
        );
        if (diags.length > 0) {
          console.error('Type errors in', f, ':', diags.length);
          process.exit(1);
        }
      }
    " 2>/dev/null && TSC_OK=1
  fi
fi
# If tsc is not available at all, give benefit of doubt (syntax gate already passed)
if [ "$TSC_OK" = "1" ] || ! command -v npx >/dev/null 2>&1; then
  add_score 0.10 1 "TypeScript type-check passes (or tsc unavailable)"
else
  add_score 0.10 0 "TypeScript type-check failed"
fi

# [pr_diff] (0.10): Key surrounding code patterns preserved (anti-gutting check)
# Verify multiple unrelated patterns from the file still exist, ensuring
# the agent didn't gut the file and rewrite from scratch.
PRESERVED=0
PRESERVED_TOTAL=5
grep -q 'dynamicRoutes' "$BUILD_COMPLETE" && PRESERVED=$((PRESERVED+1))
grep -q 'prerenderManifest' "$BUILD_COMPLETE" && PRESERVED=$((PRESERVED+1))
grep -q 'function handleBuildComplete' "$BUILD_COMPLETE" && PRESERVED=$((PRESERVED+1))
grep -q 'ManifestBuiltRoute' "$BUILD_INDEX" && PRESERVED=$((PRESERVED+1))
grep -q 'prefetchSegmentDataRoutes\|PrefetchSegmentDataRoute' "$BUILD_INDEX" && PRESERVED=$((PRESERVED+1))

if [ "$PRESERVED" -ge 4 ]; then
  add_score 0.10 1 "Surrounding code preserved ($PRESERVED/$PRESERVED_TOTAL patterns found)"
else
  add_score 0.10 0 "Surrounding code damaged ($PRESERVED/$PRESERVED_TOTAL patterns found)"
fi

# ── Final score ──────────────────────────────────────────────────────
echo ""
echo "Score: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

# Compute category scores for reward.json
python3 -c "
import json
reward = $SCORE
# Dead code removal checks = 0.55, P2P integrity = 0.45
behavioral = round(min(reward, 0.55), 4)
regression = round(min(max(reward - 0.55, 0), 0.45), 4)
json.dump({
  'reward': reward,
  'behavioral': behavioral,
  'regression': regression,
  'config': 0.0,
  'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
