#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
REPO="/workspace/opencode"
PKG="$REPO/packages/opencode"
FILE_SRC="$PKG/src/file/index.ts"
FS_SRC="$PKG/src/filesystem/index.ts"

log() { echo "  $1"; }
award() {
  local w=$1; local desc=$2
  TOTAL=$(python3 -c "print($TOTAL + $w)")
  SCORE=$(python3 -c "print($SCORE + $w)")
  log "PASS ($w): $desc"
}
fail() {
  local w=$1; local desc=$2
  TOTAL=$(python3 -c "print($TOTAL + $w)")
  log "FAIL ($w): $desc"
}

mkdir -p /logs/verifier

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): TypeScript files must parse without errors
if ! node -e "
  const ts = require('typescript');
  for (const f of ['$FILE_SRC', '$FS_SRC']) {
    const src = require('fs').readFileSync(f, 'utf8');
    ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
  }
" 2>/dev/null; then
  log "GATE FAIL: TypeScript syntax error — aborting"
  echo "0" > /logs/verifier/reward.txt
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > /logs/verifier/reward.json
  exit 0
fi
log "GATE PASS: TypeScript files parse"

cd "$PKG"

echo ""
echo "=== F2P: AppFileSystem.existsSafe works ==="
# [pr_diff] (0.20): existsSafe must exist on AppFileSystem and return correct booleans
cat > src/_harbor_test_exists.ts << 'TSEOF'
import { AppFileSystem } from "@/filesystem"
import { Effect } from "effect"
import * as fs from "fs"

fs.writeFileSync("/tmp/_harbor_exists_target", "hello")

const program = Effect.gen(function*() {
  const appFs = yield* AppFileSystem.Service
  if (typeof appFs.existsSafe !== "function")
    throw new Error("existsSafe is not a function on AppFileSystem.Service")

  const yes = yield* appFs.existsSafe("/tmp/_harbor_exists_target")
  if (yes !== true) throw new Error("existsSafe(/tmp/_harbor_exists_target) should be true, got: " + yes)

  const no = yield* appFs.existsSafe("/nonexistent_harbor_" + Date.now())
  if (no !== false) throw new Error("existsSafe(missing) should be false, got: " + no)
})

await Effect.runPromise(program.pipe(Effect.provide(AppFileSystem.defaultLayer)))
console.log("existsSafe OK")
TSEOF

if timeout 30 bun run src/_harbor_test_exists.ts 2>&1; then
  award 0.20 "AppFileSystem.existsSafe works correctly"
else
  fail 0.20 "AppFileSystem.existsSafe missing or broken"
fi
rm -f src/_harbor_test_exists.ts

echo ""
echo "=== F2P: AppFileSystem.readDirectoryEntries works ==="
# [pr_diff] (0.20): readDirectoryEntries must return DirEntry[] with name and type
cat > src/_harbor_test_readdir.ts << 'TSEOF'
import { AppFileSystem } from "@/filesystem"
import { Effect } from "effect"
import * as fs from "fs"

fs.mkdirSync("/tmp/_harbor_readdir_test", { recursive: true })
fs.writeFileSync("/tmp/_harbor_readdir_test/alpha.txt", "a")
fs.mkdirSync("/tmp/_harbor_readdir_test/beta_dir", { recursive: true })

const program = Effect.gen(function*() {
  const appFs = yield* AppFileSystem.Service
  if (typeof appFs.readDirectoryEntries !== "function")
    throw new Error("readDirectoryEntries is not a function on AppFileSystem.Service")

  const entries = yield* appFs.readDirectoryEntries("/tmp/_harbor_readdir_test")
  if (!Array.isArray(entries)) throw new Error("must return array, got: " + typeof entries)
  if (entries.length < 2) throw new Error("expected >=2 entries, got: " + entries.length)

  const names = entries.map((e: any) => e.name).sort()
  if (!names.includes("alpha.txt")) throw new Error("missing alpha.txt, got: " + JSON.stringify(names))
  if (!names.includes("beta_dir")) throw new Error("missing beta_dir, got: " + JSON.stringify(names))

  const fileEntry = entries.find((e: any) => e.name === "alpha.txt")!
  if ((fileEntry as any).type !== "file")
    throw new Error("alpha.txt type should be 'file', got: " + (fileEntry as any).type)

  const dirEntry = entries.find((e: any) => e.name === "beta_dir")!
  if ((dirEntry as any).type !== "directory")
    throw new Error("beta_dir type should be 'directory', got: " + (dirEntry as any).type)
})

await Effect.runPromise(program.pipe(Effect.provide(AppFileSystem.defaultLayer)))
console.log("readDirectoryEntries OK")
TSEOF

if timeout 30 bun run src/_harbor_test_readdir.ts 2>&1; then
  award 0.20 "AppFileSystem.readDirectoryEntries works correctly"
else
  fail 0.20 "AppFileSystem.readDirectoryEntries missing or broken"
fi
rm -f src/_harbor_test_readdir.ts

echo ""
echo "=== F2P: File.defaultLayer is exported and is a Layer ==="
# [pr_diff] (0.15): File namespace must export defaultLayer that composes AppFileSystem
cat > src/_harbor_test_deflayer.ts << 'TSEOF'
import { File } from "@/file"

if (!("defaultLayer" in File)) throw new Error("File.defaultLayer not found in File namespace")
if (!File.defaultLayer) throw new Error("File.defaultLayer is falsy")
if (typeof (File.defaultLayer as any).pipe !== "function")
  throw new Error("File.defaultLayer does not look like an Effect Layer (no pipe method)")
console.log("File.defaultLayer OK")
TSEOF

if timeout 30 bun run src/_harbor_test_deflayer.ts 2>&1; then
  award 0.15 "File.defaultLayer exported and is a Layer"
else
  fail 0.15 "File.defaultLayer missing or invalid"
fi
rm -f src/_harbor_test_deflayer.ts

echo ""
echo "=== F2P: read method uses generator pattern ==="
# [pr_diff] (0.10): read should be Effect.fn(...)(function* ...) not wrapping entire body in Effect.promise
# This checks the actual function shape — the PR moves from Effect.promise wrapper to yield* generators
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE_SRC', 'utf8');
// Find read = Effect.fn and check the function type on the same or next line
const readIdx = src.indexOf('const read = Effect.fn');
if (readIdx === -1) { console.error('read function not found'); process.exit(1); }
const afterRead = src.slice(readIdx, readIdx + 300);
// Should contain function* (generator) not async function
const genMatch = afterRead.match(/\(\s*(function\*|async\s+function|async\s*\(|\([^)]*\)\s*=>)/);
if (!genMatch) { console.error('Could not determine read function type'); process.exit(1); }
if (!genMatch[1].startsWith('function*')) {
  console.error('read should be a generator (function*), found: ' + genMatch[1]);
  process.exit(1);
}
// Verify Effect.promise is not the first statement (it should only be used for git calls)
const readBody = src.slice(readIdx);
const readEnd = readBody.indexOf('const list = Effect.fn');
const readSection = readEnd > 0 ? readBody.slice(0, readEnd) : readBody.slice(0, 2000);
// Count Effect.promise — in correct fix there's at most 1 (for git subprocess)
const promiseMatches = readSection.match(/yield\*\s+Effect\.promise/g) || [];
if (promiseMatches.length > 1) {
  console.error('read has ' + promiseMatches.length + ' yield* Effect.promise calls; expected <=1 (git only)');
  process.exit(1);
}
console.log('read is a generator with ' + promiseMatches.length + ' Effect.promise (git only)');
" 2>&1
if [ $? -eq 0 ]; then
  award 0.10 "read method uses generator pattern (not Effect.promise wrapper)"
else
  fail 0.10 "read method still fully wrapped in Effect.promise"
fi

echo ""
echo "=== P2P: bun typecheck ==="
# [repo_tests] (0.15): Full TypeScript type checking must pass after changes
cd "$PKG"
if timeout 90 bun run typecheck 2>&1 | tail -5; then
  award 0.15 "bun typecheck passes"
else
  fail 0.15 "bun typecheck fails"
fi

echo ""
echo "=== Config-derived checks ==="
cd "$REPO"

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:19 @ 608607256716
CHANGED_LINES=$(git diff HEAD -- "$FILE_SRC" "$FS_SRC" 2>/dev/null | grep '^+' | grep -v '^+++' || true)
if ! echo "$CHANGED_LINES" | grep -qE ':\s*any\b|as\s+any\b' 2>/dev/null; then
  award 0.05 "No 'any' type in changed code"
else
  fail 0.05 "Changed code uses 'any' type"
fi

# [agent_config] (0.05): "Use Effect.fn for named/traced effects" — packages/opencode/AGENTS.md:12 @ 608607256716
# New methods in filesystem/index.ts should use Effect.fn for tracing
if grep -qE 'Effect\.fn\("[A-Za-z]+\.(existsSafe|readDirectoryEntries|safeExists|listEntries)' "$FS_SRC" 2>/dev/null; then
  award 0.05 "New filesystem methods use Effect.fn for tracing"
else
  fail 0.05 "New filesystem methods missing Effect.fn tracing"
fi

echo ""
echo "=== Regression: list method migrated from raw fs.promises ==="
# [pr_diff] (0.05): list must not use raw fs.promises.readdir anymore
cd "$PKG"
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE_SRC', 'utf8');
const listStart = src.indexOf('const list = Effect.fn');
if (listStart === -1) { console.error('list function not found'); process.exit(1); }
const afterList = src.slice(listStart, listStart + 2000);
if (afterList.includes('fs.promises.readdir')) {
  console.error('list still uses raw fs.promises.readdir');
  process.exit(1);
}
console.log('list does not use raw fs.promises.readdir');
" 2>&1
if [ $? -eq 0 ]; then
  award 0.05 "list method migrated from raw fs.promises.readdir"
else
  fail 0.05 "list method still uses raw fs.promises.readdir"
fi

echo ""
echo "=== Results ==="
FINAL=$(python3 -c "print(round(min(1.0, $SCORE), 4))")
log "Score: $SCORE / $TOTAL"
echo "Final reward: $FINAL"

echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
s = $SCORE
# behavioral = existsSafe(0.20) + readDir(0.20) + defaultLayer(0.15) + readGen(0.10) + listMigrated(0.05)
behavioral = min(0.70, $SCORE)
regression = min(0.15, max(0, $SCORE - 0.70))
config = min(0.10, max(0, $SCORE - 0.85))
json.dump({
    'reward': round(min(1.0, s), 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4)
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
