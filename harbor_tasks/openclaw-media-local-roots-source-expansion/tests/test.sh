#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=100
REPO="/workspace/openclaw"

echo "=== openclaw-media-local-roots-source-expansion grading ==="

# Helper: write a temp .mts file and run with tsx (handles ESM + TS natively)
run_tsx() {
  local script_file="/tmp/test_$1.mts"
  cat > "$script_file"
  cd "$REPO" && npx --yes tsx "$script_file" 2>/dev/null
}

# ─────────────────────────────────────────────────────────
# GATE (0.00): TypeScript syntax check — abort on failure
# ─────────────────────────────────────────────────────────
echo "[GATE] TypeScript syntax check on modified files..."
GATE_PASS=true
for f in src/media/local-roots.ts src/agents/tools/media-tool-shared.ts; do
  if [[ -f "$REPO/$f" ]]; then
    node -e "
      const fs = require('fs');
      const code = fs.readFileSync('$REPO/$f', 'utf8');
      try {
        require('esbuild').transformSync(code, { loader: 'ts' });
        process.exit(0);
      } catch(e) {
        console.error(e.message);
        process.exit(1);
      }
    " 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "  FAIL: $f has syntax errors"
      GATE_PASS=false
    fi
  fi
done

if [[ "$GATE_PASS" == "false" ]]; then
  echo "GATE FAILED — aborting"
  echo "0.0" > "/logs/verifier/reward.txt" 2>/dev/null || echo "0.0" > /logs/verifier/reward.txt
  echo "0.0"
  exit 0
fi
echo "  GATE: PASS"

# ─────────────────────────────────────────────────────────
# F2P + ANTI-STUB BEHAVIORAL (0.60 total)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.25): appendLocalMediaParentRoots must not widen roots from media sources
#                    AND must still return the input base roots (anti-stub)
echo "[F2P] appendLocalMediaParentRoots: no widening + preserves input roots..."
CHECK1_SCORE=0
CHECK1=$(run_tsx check1 <<'TSEOF'
import { appendLocalMediaParentRoots } from "/workspace/openclaw/src/media/local-roots.ts";
import path from "node:path";
try {
  const roots = appendLocalMediaParentRoots(["/tmp/base", "/home/user/docs"], [
    "/Users/peter/Pictures/photo.png",
    "file:///Users/peter/Movies/clip.mp4",
    "/top-level-file.png",
  ]);
  const normalized = roots.map(r => path.resolve(r));
  console.log(JSON.stringify({
    hasBase: normalized.some(r => r === path.resolve("/tmp/base")),
    hasDocs: normalized.some(r => r === path.resolve("/home/user/docs")),
    hasPictures: normalized.some(r => r.includes("Pictures")),
    hasMovies: normalized.some(r => r.includes("Movies")),
    hasRootSlash: normalized.includes("/"),
    count: normalized.length,
  }));
} catch(e: any) { console.log(JSON.stringify({ error: e.message })); }
TSEOF
)

# Must preserve base roots (anti-stub) AND not widen from media sources (F2P)
HAS_BASE=$(echo "$CHECK1" | grep -c '"hasBase":true' || true)
HAS_DOCS=$(echo "$CHECK1" | grep -c '"hasDocs":true' || true)
NO_PICS=$(echo "$CHECK1" | grep -c '"hasPictures":false' || true)
NO_MOVS=$(echo "$CHECK1" | grep -c '"hasMovies":false' || true)

if [[ "$HAS_BASE" -gt 0 && "$HAS_DOCS" -gt 0 && "$NO_PICS" -gt 0 && "$NO_MOVS" -gt 0 ]]; then
  echo "  PASS: preserves input roots, does not widen from media sources"
  CHECK1_SCORE=25
else
  echo "  FAIL: $CHECK1"
fi
SCORE=$((SCORE + CHECK1_SCORE))

# [pr_diff] (0.20): resolveMediaToolLocalRoots must not widen AND must return workspace root
echo "[F2P] resolveMediaToolLocalRoots: no widening + returns workspace root..."
CHECK2_SCORE=0
CHECK2=$(run_tsx check2 <<'TSEOF'
import { resolveMediaToolLocalRoots } from "/workspace/openclaw/src/agents/tools/media-tool-shared.ts";
import path from "node:path";
try {
  const roots = resolveMediaToolLocalRoots("/tmp/workspace", undefined, [
    "/Users/peter/Pictures/photo.png",
    "file:///Users/peter/Movies/clip.mp4",
  ]);
  const normalized = roots.map(r => path.resolve(r));
  console.log(JSON.stringify({
    count: normalized.length,
    hasWorkspace: normalized.some(r => r.includes("workspace")),
    hasPictures: normalized.some(r => r.includes("Pictures")),
    hasMovies: normalized.some(r => r.includes("Movies")),
  }));
} catch(e: any) { console.log(JSON.stringify({ error: e.message })); }
TSEOF
)

# Must include workspace (anti-stub) AND not widen (F2P)
HAS_WS=$(echo "$CHECK2" | grep -c '"hasWorkspace":true' || true)
NO_PICS2=$(echo "$CHECK2" | grep -c '"hasPictures":false' || true)
NO_MOVS2=$(echo "$CHECK2" | grep -c '"hasMovies":false' || true)

if [[ "$HAS_WS" -gt 0 && "$NO_PICS2" -gt 0 && "$NO_MOVS2" -gt 0 ]]; then
  echo "  PASS: includes workspace, no widening from media sources"
  CHECK2_SCORE=20
else
  echo "  FAIL: $CHECK2"
fi
SCORE=$((SCORE + CHECK2_SCORE))

# [pr_diff] (0.15): getAgentScopedMediaLocalRootsForSources must not widen roots
echo "[F2P] getAgentScopedMediaLocalRootsForSources: no widening..."
CHECK3_SCORE=0
CHECK3=$(run_tsx check3 <<'TSEOF'
import { getAgentScopedMediaLocalRootsForSources } from "/workspace/openclaw/src/media/local-roots.ts";
import path from "node:path";
try {
  const roots = getAgentScopedMediaLocalRootsForSources({
    cfg: {} as any,
    agentId: "ops",
    mediaSources: [
      "/Users/peter/Pictures/photo.png",
      "file:///Users/peter/Movies/clip.mp4",
      "/top-level-file.png",
    ],
  });
  const normalized = [...roots].map(r => path.resolve(r));
  console.log(JSON.stringify({
    hasPictures: normalized.some(r => r.includes("Pictures")),
    hasMovies: normalized.some(r => r.includes("Movies")),
    hasRootSlash: normalized.includes("/"),
    count: normalized.length,
  }));
} catch(e: any) { console.log(JSON.stringify({ error: e.message })); }
TSEOF
)

NO_PICS3=$(echo "$CHECK3" | grep -c '"hasPictures":false' || true)
NO_MOVS3=$(echo "$CHECK3" | grep -c '"hasMovies":false' || true)

if [[ "$NO_PICS3" -gt 0 && "$NO_MOVS3" -gt 0 ]]; then
  echo "  PASS: no widening from media sources"
  CHECK3_SCORE=15
else
  echo "  FAIL: $CHECK3"
fi
SCORE=$((SCORE + CHECK3_SCORE))

# ─────────────────────────────────────────────────────────
# PASS-TO-PASS REGRESSION (0.20)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.15): resolveMediaToolLocalRoots still handles default, workspace, workspaceOnly
echo "[P2P] resolveMediaToolLocalRoots: default roots, workspace, workspaceOnly..."
CHECK4_SCORE=0
CHECK4=$(run_tsx check4 <<'TSEOF'
import { resolveMediaToolLocalRoots } from "/workspace/openclaw/src/agents/tools/media-tool-shared.ts";
import path from "node:path";
try {
  // Default roots (no workspace)
  const defaultRoots = resolveMediaToolLocalRoots(undefined);
  const defaultNorm = defaultRoots.map(r => path.resolve(r));

  // With workspace
  const wsRoots = resolveMediaToolLocalRoots("/tmp/my-workspace");
  const wsNorm = wsRoots.map(r => path.resolve(r));

  // workspaceOnly
  const onlyRoots = resolveMediaToolLocalRoots("/tmp/my-workspace", { workspaceOnly: true });
  const onlyNorm = onlyRoots.map(r => path.resolve(r));

  console.log(JSON.stringify({
    defaultCount: defaultNorm.length,
    wsCount: wsNorm.length,
    hasMyWorkspace: wsNorm.some(r => r.includes("my-workspace")),
    onlyCount: onlyNorm.length,
    onlyHasWorkspace: onlyNorm.some(r => r.includes("my-workspace")),
  }));
} catch(e: any) { console.log(JSON.stringify({ error: e.message })); }
TSEOF
)

# Sub-check A (0.05): default roots are non-empty (anti-stub)
if echo "$CHECK4" | python3 -c "
import sys, json; d = json.loads(sys.stdin.read().strip())
sys.exit(0 if d.get('defaultCount', 0) >= 1 else 1)
" 2>/dev/null; then
  echo "  PASS: default roots non-empty (count=$(echo "$CHECK4" | python3 -c "import sys,json;print(json.loads(sys.stdin.read().strip()).get('defaultCount',0))" 2>/dev/null))"
  CHECK4_SCORE=$((CHECK4_SCORE + 5))
else
  echo "  FAIL: default roots empty or missing"
fi

# Sub-check B (0.05): workspace root included when provided
if echo "$CHECK4" | grep -q '"hasMyWorkspace":true'; then
  echo "  PASS: workspace root included"
  CHECK4_SCORE=$((CHECK4_SCORE + 5))
else
  echo "  FAIL: workspace root missing"
fi

# Sub-check C (0.05): workspaceOnly restricts output
if echo "$CHECK4" | python3 -c "
import sys, json; d = json.loads(sys.stdin.read().strip())
sys.exit(0 if d.get('onlyHasWorkspace') and d.get('onlyCount', 99) <= 2 else 1)
" 2>/dev/null; then
  echo "  PASS: workspaceOnly mode correct"
  CHECK4_SCORE=$((CHECK4_SCORE + 5))
else
  echo "  FAIL: workspaceOnly mode broken"
fi
SCORE=$((SCORE + CHECK4_SCORE))

# [pr_diff] (0.05): appendLocalMediaParentRoots still deduplicates and preserves roots
echo "[P2P] appendLocalMediaParentRoots: dedup + preserves input roots..."
CHECK5_SCORE=0
CHECK5=$(run_tsx check5 <<'TSEOF'
import path from "node:path";
try {
  const mod = await import("/workspace/openclaw/src/media/local-roots.ts");
  const append = mod.appendLocalMediaParentRoots;
  if (!append) {
    console.log(JSON.stringify({ removed: true }));
  } else {
    const roots = append(["/tmp/a", "/tmp/b", "/tmp/a"]);
    const normalized = roots.map((r: string) => path.resolve(r));
    const unique = new Set(normalized);
    console.log(JSON.stringify({
      deduped: unique.size === normalized.length,
      hasA: normalized.some((r: string) => r === path.resolve("/tmp/a")),
      hasB: normalized.some((r: string) => r === path.resolve("/tmp/b")),
      count: normalized.length,
    }));
  }
} catch(e: any) { console.log(JSON.stringify({ error: e.message })); }
TSEOF
)

if echo "$CHECK5" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read().strip())
ok = (d.get('deduped') and d.get('hasA') and d.get('hasB')) or d.get('removed')
sys.exit(0 if ok else 1)
" 2>/dev/null; then
  echo "  PASS: deduplication works and input roots preserved"
  CHECK5_SCORE=5
else
  echo "  FAIL: $CHECK5"
fi
SCORE=$((SCORE + CHECK5_SCORE))

# ─────────────────────────────────────────────────────────
# STRUCTURAL (0.10)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.05): local-roots.ts no longer uses source-expansion helpers
echo "[STRUCT] Checking source-expansion utilities removed from local-roots.ts..."
CHECK6_SCORE=0
LOCAL_ROOTS="$REPO/src/media/local-roots.ts"
if [[ -f "$LOCAL_ROOTS" ]]; then
  HAS_SAFE_URL=$(grep -c 'safeFileURLToPath' "$LOCAL_ROOTS" 2>/dev/null); HAS_SAFE_URL=${HAS_SAFE_URL:-0}
  HAS_RESOLVE_USER=$(grep -c 'resolveUserPath' "$LOCAL_ROOTS" 2>/dev/null); HAS_RESOLVE_USER=${HAS_RESOLVE_USER:-0}
  HAS_HTTP_RE=$(grep -c 'HTTP_URL_RE' "$LOCAL_ROOTS" 2>/dev/null); HAS_HTTP_RE=${HAS_HTTP_RE:-0}
  HAS_DATA_RE=$(grep -c 'DATA_URL_RE' "$LOCAL_ROOTS" 2>/dev/null); HAS_DATA_RE=${HAS_DATA_RE:-0}

  REMOVED_COUNT=0
  [[ "$HAS_SAFE_URL" == "0" ]] && REMOVED_COUNT=$((REMOVED_COUNT + 1))
  [[ "$HAS_RESOLVE_USER" == "0" ]] && REMOVED_COUNT=$((REMOVED_COUNT + 1))
  [[ "$HAS_HTTP_RE" == "0" ]] && REMOVED_COUNT=$((REMOVED_COUNT + 1))
  [[ "$HAS_DATA_RE" == "0" ]] && REMOVED_COUNT=$((REMOVED_COUNT + 1))

  if [[ "$REMOVED_COUNT" -ge 3 ]]; then
    echo "  PASS: source-expansion utilities removed ($REMOVED_COUNT/4)"
    CHECK6_SCORE=5
  else
    echo "  FAIL: source-expansion utilities still present ($REMOVED_COUNT/4 removed)"
  fi
fi
SCORE=$((SCORE + CHECK6_SCORE))

# [pr_diff] (0.05): media-tool-shared.ts no longer imports appendLocalMediaParentRoots
echo "[STRUCT] Checking media-tool-shared.ts doesn't import expansion helper..."
CHECK7_SCORE=0
SHARED_FILE="$REPO/src/agents/tools/media-tool-shared.ts"
if [[ -f "$SHARED_FILE" ]]; then
  HAS_APPEND_IMPORT=$(grep -c 'appendLocalMediaParentRoots' "$SHARED_FILE" 2>/dev/null); HAS_APPEND_IMPORT=${HAS_APPEND_IMPORT:-0}
  if [[ "$HAS_APPEND_IMPORT" == "0" ]]; then
    echo "  PASS: no longer imports appendLocalMediaParentRoots"
    CHECK7_SCORE=5
  else
    echo "  FAIL: still imports appendLocalMediaParentRoots"
  fi
fi
SCORE=$((SCORE + CHECK7_SCORE))

# ─────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10)
# ─────────────────────────────────────────────────────────

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144 @ aff6883
echo "[CONFIG] Checking no new 'any' types..."
CHECK8_SCORE=0
ANY_COUNT=0
for f in src/media/local-roots.ts src/agents/tools/media-tool-shared.ts; do
  if [[ -f "$REPO/$f" ]]; then
    FILE_ANY=$(grep -P ':\s*any\b|<any>' "$REPO/$f" 2>/dev/null | grep -v '^\s*//' | wc -l); FILE_ANY=${FILE_ANY:-0}
    ANY_COUNT=$((ANY_COUNT + FILE_ANY))
  fi
done
if [[ "$ANY_COUNT" == "0" ]]; then
  echo "  PASS: no explicit 'any' types"
  CHECK8_SCORE=5
else
  echo "  FAIL: $ANY_COUNT explicit 'any' annotations found"
fi
SCORE=$((SCORE + CHECK8_SCORE))

# [agent_config] (0.05): "Add brief code comments for tricky or non-obvious logic" — CLAUDE.md:163 @ aff6883
echo "[CONFIG] Checking explanatory comments on security change..."
CHECK9_SCORE=0
if [[ -f "$LOCAL_ROOTS" ]]; then
  # Accept any comment explaining the behavioral change — broad keyword match
  COMMENT_MATCH=$(grep -ciE '@deprecated|no longer (widen|expand)|configuration.derived|media.source|source.expan|root.expan|security|compat(ib)?|removed.*parent|parent.*removed|do not.*widen|stop.*widen|disabled.*expan' "$LOCAL_ROOTS" 2>/dev/null)
  COMMENT_MATCH=${COMMENT_MATCH:-0}
  if [[ "$COMMENT_MATCH" -gt 0 ]]; then
    echo "  PASS: explanatory comments present"
    CHECK9_SCORE=5
  else
    echo "  FAIL: no comments explaining the behavioral change"
  fi
fi
SCORE=$((SCORE + CHECK9_SCORE))

# ─────────────────────────────────────────────────────────
# FINAL SCORE
# ─────────────────────────────────────────────────────────

FINAL=$(python3 -c "print(f'{$SCORE / $TOTAL:.4f}')" 2>/dev/null || echo "0.0")
echo ""
echo "=== FINAL SCORE: $SCORE / $TOTAL = $FINAL ==="

echo "$FINAL" > "/logs/verifier/reward.txt" 2>/dev/null || echo "$FINAL" > /logs/verifier/reward.txt

# Detailed breakdown
python3 -c "
import json
score = $SCORE / $TOTAL
reward = {
    'reward': round(score, 4),
    'behavioral': round(($CHECK1_SCORE + $CHECK2_SCORE + $CHECK3_SCORE + $CHECK4_SCORE + $CHECK5_SCORE) / $TOTAL, 4),
    'structural': round(($CHECK6_SCORE + $CHECK7_SCORE) / $TOTAL, 4),
    'config': round(($CHECK8_SCORE + $CHECK9_SCORE) / $TOTAL, 4),
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(reward, f, indent=2)
print(json.dumps(reward, indent=2))
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
