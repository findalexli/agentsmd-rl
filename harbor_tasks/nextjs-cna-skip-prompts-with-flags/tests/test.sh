#!/usr/bin/env bash
set +e
set -uo pipefail

PASS=0
TOTAL=0

cd /workspace/next.js

##############################################################################
# GATE: TypeScript compilation via ncc
##############################################################################
# [pr_diff] (gate): Modified file must compile without errors
cd packages/create-next-app
if ! npx ncc build ./index.ts -o /tmp/cna-build --no-cache --no-source-map-register 2>/tmp/ncc-build.log; then
    echo "GATE FAIL: packages/create-next-app/index.ts has compilation errors"
    cat /tmp/ncc-build.log 2>/dev/null | tail -20
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
cd /workspace/next.js
echo "GATE: compilation check passed"

##############################################################################
# Fail-to-pass: Behavioral tests (0.70 total)
##############################################################################

# [pr_diff] (0.30): CLI with partial flags completes without hanging on prompts
# WHY calling code: on buggy code, unspecified options trigger interactive
# prompts which hang because stdin is /dev/null. Fixed code uses defaults.
OUTPUT1=$(mktemp)
timeout 45 node /tmp/cna-build/index.js /tmp/test-partial-1 \
    --ts --tailwind --app --skip-install </dev/null >"$OUTPUT1" 2>&1
EXIT1=$?
if [ "$EXIT1" -eq 124 ]; then
    echo "FAIL [0.30]: CLI hung on interactive prompts (timed out)"
else
    PASS=$((PASS + 30))
    echo "PASS [0.30]: CLI with --ts --tailwind --app completed (exit=$EXIT1)"
fi
TOTAL=$((TOTAL + 30))

# [pr_diff] (0.15): Output mentions defaulted options by name
# When --ts, --tailwind, --app are explicit, the remaining options (eslint,
# react-compiler, src-dir, agents-md, import-alias) got defaults.
# A correct fix should tell the user which options were auto-filled.
if [ "$EXIT1" -ne 124 ]; then
    python3 -c "
import sys
output = open('${OUTPUT1}').read().lower()
# Options NOT passed on CLI — any correct summary should mention some of these
unspecified = ['eslint', 'biome', 'compiler', 'src', 'import', 'alias', 'agents']
matches = sum(1 for u in unspecified if u in output)
if matches >= 2:
    sys.exit(0)
else:
    print(f'Only {matches}/7 defaulted options mentioned in output')
    sys.exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 15))
        echo "PASS [0.15]: Output mentions defaulted options"
    else
        echo "FAIL [0.15]: Output doesn't mention defaulted options"
        echo "  stdout was:"
        head -40 "$OUTPUT1" 2>/dev/null
    fi
else
    echo "FAIL [0.15]: CLI didn't complete, can't check output"
fi
TOTAL=$((TOTAL + 15))

# [pr_diff] (0.10): Output includes override flags so caller knows how to change defaults
# Instruction: "print a summary... so the caller knows what flags to pass to override them"
if [ "$EXIT1" -ne 124 ]; then
    python3 -c "
import re, sys
output = open('${OUTPUT1}').read()
# Find --flag patterns in output
all_flags = set(re.findall(r'--[a-z][\w-]+', output))
# Remove flags that were INPUT (not override suggestions)
input_flags = {'--ts', '--tailwind', '--app', '--skip-install'}
override_flags = all_flags - input_flags
if len(override_flags) >= 3:
    sys.exit(0)
else:
    print(f'Only {len(override_flags)} override flags in output: {override_flags}')
    sys.exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 10))
        echo "PASS [0.10]: Output includes override flags"
    else
        echo "FAIL [0.10]: Output missing override flags"
    fi
else
    echo "FAIL [0.10]: CLI didn't complete, can't check flags"
fi
TOTAL=$((TOTAL + 10))

# [pr_diff] (0.15): Different flag combo also works — fix must be general, not hardcoded
# With --eslint --src-dir, the defaulted options are different (typescript,
# tailwind, app, react-compiler, agents-md). Tests generality.
OUTPUT2=$(mktemp)
timeout 45 node /tmp/cna-build/index.js /tmp/test-partial-2 \
    --eslint --src-dir --skip-install </dev/null >"$OUTPUT2" 2>&1
EXIT2=$?
if [ "$EXIT2" -eq 124 ]; then
    echo "FAIL [0.15]: CLI hung with --eslint --src-dir flags"
else
    # Verify output mentions at least one option that WAS defaulted in this combo
    python3 -c "
import sys
output = open('${OUTPUT2}').read().lower()
# Options NOT passed: typescript/javascript, tailwind, app/pages, react-compiler, agents
defaulted = ['typescript', 'javascript', 'tailwind', 'app', 'pages', 'compiler', 'agents']
matches = sum(1 for d in defaulted if d in output)
if matches >= 1:
    sys.exit(0)
else:
    print(f'No defaulted options mentioned for --eslint --src-dir combo')
    sys.exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 15))
        echo "PASS [0.15]: Different flag combo works and shows defaults"
    else
        # Still give credit if it at least didn't hang (partial credit)
        echo "FAIL [0.15]: Different flag combo completed but no defaults shown"
    fi
fi
TOTAL=$((TOTAL + 15))

##############################################################################
# Pass-to-pass: Regression checks (0.15 total)
##############################################################################

# [pr_diff] (0.10): --yes --skip-install still works without hanging
YES_OUTPUT=$(mktemp)
timeout 45 node /tmp/cna-build/index.js /tmp/test-yes \
    --yes --skip-install </dev/null >"$YES_OUTPUT" 2>&1
YES_EXIT=$?
if [ "$YES_EXIT" -eq 124 ]; then
    echo "FAIL [0.10]: --yes flag caused hang (regression)"
else
    PASS=$((PASS + 10))
    echo "PASS [0.10]: --yes --skip-install still works (exit=$YES_EXIT)"
fi
TOTAL=$((TOTAL + 10))

# [pr_diff] (0.05): --yes flag does NOT produce a verbose defaults summary
# --yes means "accept all defaults silently" — it should NOT show per-option info
if [ "$YES_EXIT" -ne 124 ]; then
    python3 -c "
import sys
output = open('${YES_OUTPUT}').read().lower()
# With --yes, there shouldn't be a detailed defaults summary
indicators = ['eslint', 'biome', 'compiler', 'src-dir', 'import-alias', 'agents']
matches = sum(1 for i in indicators if i in output)
# 0-1 incidental matches is OK; >=3 means a summary was printed
if matches <= 1:
    sys.exit(0)
else:
    print(f'--yes output mentions {matches} options (should be <=1)')
    sys.exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 5))
        echo "PASS [0.05]: --yes doesn't show defaults summary"
    else
        echo "FAIL [0.05]: --yes incorrectly shows defaults summary"
    fi
else
    echo "FAIL [0.05]: --yes hung, can't check output"
fi
TOTAL=$((TOTAL + 5))

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): No deprecated check() usage — AGENTS.md:194 @ e6bf5f6
node -e "
const fs = require('fs');
const src = fs.readFileSync('packages/create-next-app/index.ts', 'utf8');
if (/\bcheck\s*\(\s*\(\s*\)\s*=>/.test(src)) {
    console.log('FAIL: deprecated check() pattern found');
    process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: No deprecated check() pattern"
else
    echo "FAIL [0.05]: Deprecated check() pattern found"
fi
TOTAL=$((TOTAL + 5))

# [agent_config] (0.05): No secret values logged — AGENTS.md:306 @ e6bf5f6
node -e "
const fs = require('fs');
const src = fs.readFileSync('packages/create-next-app/index.ts', 'utf8');
const secrets = /(?:api[_-]?key|secret|token|password|credential)\s*[:=]/i;
if (secrets.test(src)) {
    console.log('FAIL: potential secret value in source');
    process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: No secret values in source"
else
    echo "FAIL [0.05]: Potential secret value in source"
fi
TOTAL=$((TOTAL + 5))

##############################################################################
# Anti-stub: structural depth (0.05)
##############################################################################

# [pr_diff] (0.05): displayConfig entries enriched with flag info for summary
# Rejects empty stubs — requires substantive additions to displayConfig
node -e "
const fs = require('fs');
const src = fs.readFileSync('packages/create-next-app/index.ts', 'utf8');
// Count lines that define flag-to-value mappings (any format: flags:{}, flagMap, etc.)
// Must have at least 3 option→flag mappings for the summary to work
const flagPatterns = src.match(/--[a-z][\w-]+['\"]?\s*[:,]/g) || [];
// Filter to only flag patterns inside displayConfig-like structures (not CLI parsing)
// Rough heuristic: at least 6 distinct --flag references in the file beyond the CLI arg parsing
const distinctFlags = new Set(flagPatterns.map(p => p.match(/--[a-z][\w-]+/)[0]));
if (distinctFlags.size >= 6) {
    process.exit(0);
} else {
    console.log('Only ' + distinctFlags.size + ' flag patterns found (need >=6)');
    process.exit(1);
}
" 2>/dev/null
if [ $? -eq 0 ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: Sufficient flag-to-option mappings for summary"
else
    echo "FAIL [0.05]: Insufficient flag-to-option mappings"
fi
TOTAL=$((TOTAL + 5))

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS / 100" | bc)
echo ""
echo "Total: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt

echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
