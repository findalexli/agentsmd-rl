#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/opencode"

echo "=== Changelog Deterministic Commit Range Tests ==="
echo ""

###############################################################################
# GATE: TypeScript syntax check
###############################################################################
echo "--- GATE: TypeScript syntax check ---"
GATE_PASS=true
for f in script/changelog.ts script/version.ts; do
    if [ ! -f "$REPO/$f" ]; then
        echo "FAIL: $f does not exist"
        GATE_PASS=false
        continue
    fi
    if ! bun build --no-bundle "$REPO/$f" --outdir /tmp/gate_check 2>/dev/null; then
        echo "FAIL: $f has syntax errors"
        GATE_PASS=false
    else
        echo "PASS: $f syntax OK"
    fi
done

if [ "$GATE_PASS" = false ]; then
    echo ""
    echo "GATE FAILED — aborting"
    echo "0.00" > /logs/verifier/reward.txt
    exit 0
fi
echo ""

###############################################################################
# [pr_diff] (0.30): F2P — changelog.ts runs without LLM SDK dependencies
# The buggy code imports @opencode-ai/sdk and @opencode-ai/script at the
# top level. Removing those packages and trying to run the script will
# CRASH on buggy code (unresolved import) but SUCCEED on any correct fix.
###############################################################################
echo "--- [pr_diff] (0.30): F2P — changelog.ts independent of LLM SDK ---"

# Back up SDK packages, then remove them
SDK_BAK="/tmp/sdk_backup_$$"
mkdir -p "$SDK_BAK"
for pkg in sdk script; do
    PKG_DIR="$REPO/node_modules/@opencode-ai/$pkg"
    if [ -d "$PKG_DIR" ]; then
        cp -a "$PKG_DIR" "$SDK_BAK/$pkg" 2>/dev/null
        rm -rf "$PKG_DIR"
    fi
done

# Try running --help: exercises import + CLI parse without hitting gh/git APIs
# Buggy code: crashes at import (can't resolve @opencode-ai/sdk)
# Fixed code: prints usage and exits cleanly
F2P_HELP=$(cd "$REPO" && bun script/changelog.ts --help 2>&1)
F2P_EXIT=$?

if [ $F2P_EXIT -eq 0 ] && echo "$F2P_HELP" | grep -qi "usage\|from\|help\|options" 2>/dev/null; then
    echo "PASS: changelog.ts --help works without LLM SDK"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "FAIL: changelog.ts cannot run without @opencode-ai/sdk (exit=$F2P_EXIT)"
fi

# Restore SDK packages for remaining checks
for pkg in sdk script; do
    BAK_DIR="$SDK_BAK/$pkg"
    PKG_DIR="$REPO/node_modules/@opencode-ai/$pkg"
    if [ -d "$BAK_DIR" ]; then
        mkdir -p "$(dirname "$PKG_DIR")"
        mv "$BAK_DIR" "$PKG_DIR" 2>/dev/null
    fi
done
rm -rf "$SDK_BAK"
echo ""

###############################################################################
# [pr_diff] (0.20): F2P — version.ts pins commit range upper bound
# Buggy code: `opencode run --command changelog` (no upper bound)
# Fixed code: passes --to (or equivalent) to pin the commit range
###############################################################################
echo "--- [pr_diff] (0.20): F2P — version.ts pins upper bound ---"
# Parse version.ts to find the changelog invocation and check it passes
# an upper-bound argument. Accept --to, --end, --until, --head, or GITHUB_SHA.
bun -e "
const src = await Bun.file('$REPO/script/version.ts').text()
const lines = src.split('\n')

// Find lines that invoke the changelog command
const cmdLines = lines.filter(l =>
  l.includes('changelog') && (l.includes('run') || l.includes('exec') || l.includes('\$\`') || l.includes('spawn'))
)

if (cmdLines.length === 0) {
  console.log('No changelog invocation found in version.ts')
  process.exit(1)
}

// Check that at least one invocation pins an upper bound
const pinsUpper = cmdLines.some(l =>
  l.includes('--to') || l.includes('--end') || l.includes('--until') ||
  l.includes('--head') || l.includes('GITHUB_SHA')
)

if (!pinsUpper) {
  console.log('Changelog invocation does not pin upper bound')
  process.exit(1)
}

process.exit(0)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "PASS: version.ts pins commit range upper bound"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL: version.ts does not pin upper bound"
fi
echo ""

###############################################################################
# [pr_diff] (0.15): Command prompt consumes structured data, not LLM-fetched
# The buggy prompt instructs the LLM to fetch releases and find PRs.
# The fixed prompt has the LLM consume pre-computed structured data.
###############################################################################
echo "--- [pr_diff] (0.15): Command prompt uses structured input ---"
CMD_FILE="$REPO/.opencode/command/changelog.md"
FAIL_CMD=false

if [ ! -f "$CMD_FILE" ]; then
    echo "FAIL: $CMD_FILE does not exist"
    FAIL_CMD=true
else
    # Should NOT instruct LLM to fetch releases
    if grep -qi 'fetch the latest.*release' "$CMD_FILE" 2>/dev/null; then
        echo "FAIL: Command still tells LLM to fetch releases"
        FAIL_CMD=true
    fi

    # Should NOT instruct LLM to find PRs
    if grep -qi 'find each PR' "$CMD_FILE" 2>/dev/null; then
        echo "FAIL: Command still tells LLM to find PRs"
        FAIL_CMD=true
    fi

    # Should reference the changelog script for structured input (accept various forms)
    if grep -qE 'script/changelog|changelog\.ts' "$CMD_FILE" 2>/dev/null; then
        echo "PASS: Command references changelog script"
    else
        echo "FAIL: Command does not reference changelog script for structured input"
        FAIL_CMD=true
    fi
fi

if [ "$FAIL_CMD" = false ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
fi
echo ""

###############################################################################
# [pr_diff] (0.10): changelog.ts paginates the GitHub compare API
# Accept any pagination approach: per_page param with loop, cursor pagination,
# Link header parsing, etc. NOT a narrow check for exact per_page=100.
###############################################################################
echo "--- [pr_diff] (0.10): changelog.ts paginates GitHub compare API ---"
bun -e "
const src = await Bun.file('$REPO/script/changelog.ts').text()

// Check for pagination patterns (any of these):
// 1. per_page/perPage + loop (for/while)
// 2. cursor/next_page + loop
// 3. Link header parsing
const hasPerPage = /per_page|perPage/.test(src)
const hasLoop = /\bfor\s*\(|while\s*\(/.test(src)
const hasCursor = /cursor|next_page|nextPage|Link.*header/.test(src)
const hasPageVar = /\bpage\b/.test(src)

const paginated = (hasPerPage && hasLoop) || (hasCursor && hasLoop) || (hasPageVar && hasLoop && hasPerPage)

if (!paginated) {
  console.log('No pagination pattern found')
  process.exit(1)
}
process.exit(0)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "PASS: Compare API has pagination logic"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: No pagination in compare API call"
fi
echo ""

###############################################################################
# [pr_diff] (0.10): Anti-stub — changelog.ts is a complete implementation
# Must have substantial deterministic logic: multiple functions, git/API calls,
# commit processing, area classification, and formatted output.
###############################################################################
echo "--- [pr_diff] (0.10): Anti-stub — changelog.ts is non-trivial ---"
bun -e "
const src = await Bun.file('$REPO/script/changelog.ts').text()
const lines = src.split('\n').filter(l => l.trim() && !l.trim().startsWith('//') && !l.trim().startsWith('*'))

const checks = {
  // At least 4 named functions (commit gathering, area classification, revert filter, formatting)
  functions: (src.match(/(?:function|const\s+\w+\s*=\s*(?:async\s+)?\()/g) || []).length >= 4,
  // References git commands for deterministic commit gathering
  gitCalls: /git\s+(log|diff-tree|show|rev-parse)/.test(src),
  // References GitHub API for commit data
  ghApi: /gh\s+api|api\.github\.com|octokit/.test(src),
  // Has commit area/section classification logic
  areaClassification: /packages\/opencode|packages\/sdk|packages\/desktop/.test(src),
  // Has revert filtering logic
  revertFilter: /[Rr]evert/.test(src),
  // Substantial size (not a stub)
  size: lines.length > 80,
}

const passed = Object.values(checks).filter(Boolean).length
const total = Object.keys(checks).length

if (passed < 5) {
  console.log('Anti-stub: only ' + passed + '/' + total + ' checks passed')
  for (const [k,v] of Object.entries(checks)) {
    if (!v) console.log('  missing: ' + k)
  }
  process.exit(1)
}
process.exit(0)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "PASS: changelog.ts has substantial deterministic implementation"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: changelog.ts appears to be a stub or incomplete"
fi
echo ""

###############################################################################
# [pr_diff] (0.05): .gitignore includes UPCOMING_CHANGELOG.md
###############################################################################
echo "--- [pr_diff] (0.05): UPCOMING_CHANGELOG.md in .gitignore ---"
if grep -q 'UPCOMING_CHANGELOG' "$REPO/.gitignore" 2>/dev/null; then
    echo "PASS: UPCOMING_CHANGELOG.md is gitignored"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: UPCOMING_CHANGELOG.md not in .gitignore"
fi
echo ""

###############################################################################
# [agent_config] (0.05): No 'any' type in changed files — AGENTS.md:49
###############################################################################
echo '--- [agent_config] (0.05): No "any" type — AGENTS.md:49 ---'
ANY_COUNT=0
for f in script/changelog.ts script/version.ts; do
    if [ -f "$REPO/$f" ]; then
        FOUND=$(grep -cE ':\s*any\b|as\s+any\b' "$REPO/$f" 2>/dev/null || echo "0")
        ANY_COUNT=$((ANY_COUNT + FOUND))
    fi
done
if [ "$ANY_COUNT" -eq 0 ]; then
    echo "PASS: No 'any' type usage"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: Found $ANY_COUNT uses of 'any' type"
fi
echo ""

###############################################################################
# [agent_config] (0.05): No try/catch in changed files — AGENTS.md:42
###############################################################################
echo '--- [agent_config] (0.05): No try/catch — AGENTS.md:42 ---'
TRYCATCH=0
for f in script/changelog.ts script/version.ts; do
    if [ -f "$REPO/$f" ]; then
        FOUND=$(grep -cE '^\s*try\s*\{' "$REPO/$f" 2>/dev/null || echo "0")
        TRYCATCH=$((TRYCATCH + FOUND))
    fi
done
if [ "$TRYCATCH" -eq 0 ]; then
    echo "PASS: No try/catch blocks"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: Found $TRYCATCH try/catch blocks"
fi
echo ""

###############################################################################
# Summary
###############################################################################
echo ""
echo "=== Results ==="
echo "Score: $SCORE / 1.00"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed breakdown
python3 -c "
import json, os
score = $SCORE
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.80), 4),
    'regression': 0.10,
    'config': 0.10,
}, open('/logs/verifier/reward.json', 'w'))
" 2>/dev/null || true

echo "Final reward: $SCORE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
