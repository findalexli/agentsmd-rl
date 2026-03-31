#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
FILE="$REPO/packages/opencode/src/skill/index.ts"
REWARD=0

mkdir -p /logs/verifier

log() { echo "  $1"; }
add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

# Helper: strip comments from source to prevent comment-injection gaming.
# Writes stripped code to a temp file for downstream checks.
STRIPPED_FILE=$(mktemp)
strip_comments() {
    node -e "
const fs = require('fs');
let code = fs.readFileSync(process.argv[1], 'utf8');
// Remove single-line comments
code = code.replace(/\/\/.*$/gm, '');
// Remove multi-line comments
code = code.replace(/\/\*[\s\S]*?\*\//g, '');
process.stdout.write(code);
" "$FILE" > "$STRIPPED_FILE" 2>/dev/null
}

echo "=== GATE: File exists and is plausible ==="
# [pr_diff] (0.00): Target file must exist and have substantial content
if [ ! -f "$FILE" ]; then
    log "GATE FAIL: $FILE does not exist"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
    exit 0
fi

LINES=$(wc -l < "$FILE")
if [ "$LINES" -lt 80 ]; then
    log "GATE FAIL: file too short ($LINES lines), likely stubbed"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
    exit 0
fi

strip_comments
if [ ! -s "$STRIPPED_FILE" ]; then
    log "GATE FAIL: could not strip comments from file"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE PASS: file exists with $LINES lines"

echo ""
echo "=== Fail-to-pass: Bug-absence checks (comment-stripped) ==="

# [pr_diff] (0.20): Static Config async facades must be removed
# Bug: code calls Config.get() and Config.directories() as static async facades
# Fix: yield Config.Service, then use the yielded service variable (any name)
# Any correct fix removes the uppercase Config.get()/Config.directories() calls
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
// Buggy pattern: static Config.get() or Config.directories() (uppercase C = facade)
// A fix uses a local variable like config.get() (lowercase c from yield* Config.Service)
const hasStaticGet = /\bConfig\.get\s*\(/.test(stripped);
const hasStaticDirs = /\bConfig\.directories\s*\(/.test(stripped);
if (!hasStaticGet && !hasStaticDirs) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.20): Static Config.get()/Config.directories() facades removed"
    add 0.20
else
    log "FAIL (0.20): Static Config async facades still present"
fi

# [pr_diff] (0.15): Effect.runPromise bridge must be removed
# Bug: discovery.pull() wrapped in Effect.runPromise()
# Any correct fix removes Effect.runPromise and uses native yield* instead
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
const hasRunPromise = /Effect\.runPromise\s*\(/.test(stripped);
if (!hasRunPromise) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.15): Effect.runPromise bridge removed"
    add 0.15
else
    log "FAIL (0.15): Effect.runPromise bridge still present"
fi

# [pr_diff] (0.15): Monolithic Effect.promise wrapper around loadSkills must be removed
# Bug: InstanceState.make closure wraps loadSkills in Effect.promise(() => loadSkills(...))
# Fix: calls loadSkills as a native Effect generator via yield*
# Small Effect.promise calls for individual async ops (Filesystem.isDir, import) are fine
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
// Buggy pattern: Effect.promise(() => loadSkills(...)) — monolithic async bridge
const hasMonolithic = /Effect\.promise\s*\(\s*\(\s*\)\s*=>\s*loadSkills\b/.test(stripped);
if (!hasMonolithic) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.15): Monolithic Effect.promise(() => loadSkills) wrapper removed"
    add 0.15
else
    log "FAIL (0.15): Monolithic Effect.promise(() => loadSkills) wrapper still present"
fi

# [pr_diff] (0.05): defaultLayer must provide Config and Bus layers
# Accept various layer names: defaultLayer, layer, live, etc.
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
const hasConfigLayer = /Config\.\w*(layer|Layer|live|default)\w*/i.test(stripped);
const hasBusLayer = /Bus\.\w*(layer|Layer|live|default)\w*/i.test(stripped);
if (hasConfigLayer && hasBusLayer) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.05): defaultLayer provides Config and Bus layers"
    add 0.05
else
    log "FAIL (0.05): defaultLayer missing Config or Bus layer provision"
fi

# [pr_diff] (0.10): Layer must declare Config.Service and Bus.Service as dependencies
# Bug: layer type only has Discovery.Service
# Any correct fix adds Config.Service and Bus.Service to the layer dependency type
# We accept any ordering and formatting (multiline, single line, etc.)
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
// Both must appear somewhere in type context — don't require specific ordering
const hasConfig = /Config\.Service/.test(stripped);
const hasBus = /Bus\.Service/.test(stripped);
if (hasConfig && hasBus) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.10): Config.Service and Bus.Service declared as dependencies"
    add 0.10
else
    log "FAIL (0.10): Missing Config.Service or Bus.Service in layer dependencies"
fi

echo ""
echo "=== Regression: Pass-to-pass checks (comment-stripped) ==="

# [pr_diff] (0.05): Core skill discovery patterns must be preserved
# The file must still handle SKILL.md files, manage InstanceState, and track Skill.state
RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// These are string literals and identifiers that must exist in any correct version
const hasSKILL = /SKILL\.md/.test(src);
const hasInstance = /InstanceState/.test(src);
const hasState = /Skill\.state/.test(src);
if (hasSKILL && hasInstance && hasState) process.exit(0);
process.exit(1);
" "$FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.05): Core skill discovery patterns preserved"
    add 0.05
else
    log "FAIL (0.05): Core patterns missing (SKILL.md, InstanceState, Skill.state)"
fi

# [pr_diff] (0.05): Error reporting via Session.Event.Error must be preserved
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
if (/Session\.Event\.Error/.test(stripped)) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.05): Session.Event.Error reporting preserved"
    add 0.05
else
    log "FAIL (0.05): Session.Event.Error reporting missing"
fi

echo ""
echo "=== Config-derived checks (comment-stripped) ==="

# [agent_config] (0.05): "Avoid try/catch where possible" — AGENTS.md:15
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
const tryCatchCount = (stripped.match(/\btry\s*\{/g) || []).length;
if (tryCatchCount === 0) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.05): No try/catch blocks (AGENTS.md style)"
    add 0.05
else
    log "FAIL (0.05): try/catch blocks present"
fi

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:14
RESULT=$(node -e "
const fs = require('fs');
const stripped = fs.readFileSync(process.argv[1], 'utf8');
const anyCount = (stripped.match(/\bas\s+any\b/g) || []).length;
if (anyCount <= 3) process.exit(0);
process.exit(1);
" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.05): No excessive 'as any' usage (AGENTS.md style)"
    add 0.05
else
    log "FAIL (0.05): Too many 'as any' casts"
fi

echo ""
echo "=== Anti-stub ==="

# [pr_diff] (0.10): File must retain substantial logic and use Effect generators
RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const stripped = fs.readFileSync(process.argv[2], 'utf8');
const lines = src.split('\n').length;
// Must have realistic function/const count
const funcCount = (stripped.match(/\b(function|const|let)\s+\w+/g) || []).length;
// Must use yield* somewhere (native Effect generator pattern)
const hasYieldStar = /yield\s*\*/.test(stripped);
// Must have exports
const hasExport = /export/.test(stripped);
if (lines >= 100 && funcCount >= 5 && hasYieldStar && hasExport) process.exit(0);
process.exit(1);
" "$FILE" "$STRIPPED_FILE" 2>/dev/null)
if [ $? -eq 0 ]; then
    log "PASS (0.10): File retains substantial logic with Effect generators"
    add 0.10
else
    log "FAIL (0.10): File appears stubbed or missing Effect generator patterns"
fi

# Cleanup
rm -f "$STRIPPED_FILE"

echo ""
echo "=== Score ==="
FINAL=$(python3 -c "print(round($REWARD, 4))")
echo "$FINAL" > /logs/verifier/reward.txt

# Compute category scores
BEH=$(python3 -c "print(round(min($REWARD, 0.65), 4))")
REG=$(python3 -c "r=$REWARD; print(round(min(max(r - 0.65, 0), 0.10), 4))")
CFG=$(python3 -c "r=$REWARD; print(round(min(max(r - 0.75, 0), 0.10), 4))")

echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"config\": $CFG, \"style_rubric\": 0}" > /logs/verifier/reward.json

log "Final reward: $FINAL"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
