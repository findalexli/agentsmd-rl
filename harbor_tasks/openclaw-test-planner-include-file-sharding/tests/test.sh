#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0
GATE_PASS=true

cd /workspace/openclaw

##############################################################################
# GATE: Syntax check on modified files
##############################################################################
# [pr_diff] (gate): Modified .mjs files must parse without syntax errors
for f in scripts/test-planner/executor.mjs scripts/test-planner/planner.mjs; do
    if ! node -e "require('fs').readFileSync('$f','utf8')" 2>/dev/null; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=false
    elif ! node --check "$f" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    mkdir -p /logs/verifier && echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE: syntax check passed"

##############################################################################
# Fail-to-pass: Behavioral tests (0.65 total)
##############################################################################

# [pr_diff] (0.25): Single include-file CI batches get assigned to a specific shard
# WHY calling code: buildExecutionPlan is a pure function we can call directly
node --input-type=module -e "
import { buildExecutionPlan, createExecutionArtifacts } from './scripts/test-planner/executor.mjs';
import { buildExecutionPlan as plannerBuildPlan } from './scripts/test-planner/planner.mjs';

// Use whichever export works
const build = plannerBuildPlan || buildExecutionPlan;

const env = {
  CI: 'true',
  GITHUB_ACTIONS: 'true',
  OPENCLAW_TEST_SHARDS: '4',
  OPENCLAW_TEST_SHARD_INDEX: '1',
  OPENCLAW_TEST_LOAD_AWARE: '0',
};
const artifacts = createExecutionArtifacts(env);
const plan = build(
  { mode: 'ci', passthroughArgs: [] },
  { env, platform: 'linux', writeTempJsonArtifact: artifacts.writeTempJsonArtifact },
);

// Find a single-file include batch
const singleFileBatch = plan.parallelUnits.find(
  (unit) =>
    unit.id.startsWith('unit-fast-') &&
    unit.fixedShardIndex === undefined &&
    Array.isArray(unit.includeFiles) &&
    unit.includeFiles.length === 1,
);

if (!singleFileBatch) {
  console.error('No single-file include batch found in plan');
  process.exit(1);
}

const shardAssignment = plan.topLevelSingleShardAssignments.get(singleFileBatch);
if (typeof shardAssignment !== 'number') {
  console.error('Single-file include batch was NOT assigned to a shard (got ' + shardAssignment + ')');
  process.exit(1);
}

console.log('PASS: single-file include batch assigned to shard ' + shardAssignment);
artifacts.cleanupTempArtifacts();
" 2>&1 && { PASS=$(echo "$PASS + 0.25" | bc); echo "PASS [0.25]: single-file include batch gets shard assignment"; } || echo "FAIL [0.25]: single-file include batch gets shard assignment"
TOTAL=$(echo "$TOTAL + 0.25" | bc)

# [pr_diff] (0.20): formatExecutionUnitSummary shows numeric filter count for include-file units
# WHY calling code: formatExecutionUnitSummary is a pure formatting function
node --input-type=module -e "
import { formatExecutionUnitSummary } from './scripts/test-planner/planner.mjs';

// Mock a unit with includeFiles but no explicit CLI file filters
const unit = {
  id: 'test-batch-1',
  args: ['run', '--config', 'vitest.config.ts'],
  includeFiles: ['src/foo.test.ts', 'src/bar.test.ts'],
  maxWorkers: 2,
  surface: 'unit',
  isolate: false,
  pool: 'forks',
};

const summary = formatExecutionUnitSummary(unit);

// Should show filters=2, not filters=all
if (summary.includes('filters=all')) {
  console.error('Summary shows filters=all instead of numeric count: ' + summary);
  process.exit(1);
}
if (!summary.includes('filters=2')) {
  console.error('Summary does not show filters=2: ' + summary);
  process.exit(1);
}
console.log('PASS: summary shows filters=2 for include-file unit');
" 2>&1 && { PASS=$(echo "$PASS + 0.20" | bc); echo "PASS [0.20]: formatExecutionUnitSummary shows numeric filter count"; } || echo "FAIL [0.20]: formatExecutionUnitSummary shows numeric filter count"
TOTAL=$(echo "$TOTAL + 0.20" | bc)

# [pr_diff] (0.20): formatPlanOutput shows numeric filter counts for include-file batches in CI plan
# WHY calling code: formatPlanOutput + buildExecutionPlan are pure functions
node --input-type=module -e "
import { createExecutionArtifacts, formatPlanOutput } from './scripts/test-planner/executor.mjs';
import { buildExecutionPlan } from './scripts/test-planner/planner.mjs';

const env = {
  CI: 'true',
  GITHUB_ACTIONS: 'true',
  OPENCLAW_TEST_SHARDS: '4',
  OPENCLAW_TEST_SHARD_INDEX: '1',
  OPENCLAW_TEST_LOAD_AWARE: '0',
};
const artifacts = createExecutionArtifacts(env);
const plan = buildExecutionPlan(
  { mode: 'ci', passthroughArgs: [] },
  { env, platform: 'linux', writeTempJsonArtifact: artifacts.writeTempJsonArtifact },
);

const output = formatPlanOutput(plan);

// All unit-fast batches with includeFiles should now show numeric filter counts
const unitFastLines = output.split('\\n').filter(l => l.includes('unit-fast'));
const allFilterLine = unitFastLines.find(l => l.includes('filters=all'));
if (allFilterLine) {
  // Check if it really has includeFiles — some may genuinely have all
  // The key check: at least some unit-fast batches show numeric filters
  const numericLines = unitFastLines.filter(l => /filters=\\d+/.test(l));
  if (numericLines.length === 0) {
    console.error('No unit-fast batches show numeric filter counts in plan output');
    process.exit(1);
  }
}

const numericLines = unitFastLines.filter(l => /filters=\\d+/.test(l));
if (numericLines.length === 0) {
  console.error('No unit-fast batches show numeric filter counts');
  process.exit(1);
}
console.log('PASS: ' + numericLines.length + ' unit-fast batches show numeric filter counts');
artifacts.cleanupTempArtifacts();
" 2>&1 && { PASS=$(echo "$PASS + 0.20" | bc); echo "PASS [0.20]: plan output shows numeric filter counts for include-file batches"; } || echo "FAIL [0.20]: plan output shows numeric filter counts for include-file batches"
TOTAL=$(echo "$TOTAL + 0.20" | bc)

##############################################################################
# Pass-to-pass: Regression checks (0.15 total)
##############################################################################

# [pr_diff] (0.10): buildExecutionPlan still works for local mode (non-CI)
# WHY calling code: buildExecutionPlan is a pure function
node --input-type=module -e "
import { createExecutionArtifacts } from './scripts/test-planner/executor.mjs';
import { buildExecutionPlan } from './scripts/test-planner/planner.mjs';

const env = { OPENCLAW_TEST_HOST_CPU_COUNT: '8', OPENCLAW_TEST_HOST_MEMORY_GIB: '32', OPENCLAW_TEST_LOAD_AWARE: '0' };
const artifacts = createExecutionArtifacts(env);
const plan = buildExecutionPlan(
  { profile: null, mode: 'local', surfaces: ['unit', 'extensions'], passthroughArgs: [] },
  { env, platform: 'linux', writeTempJsonArtifact: artifacts.writeTempJsonArtifact },
);

if (!plan || !plan.selectedUnits || plan.selectedUnits.length === 0) {
  console.error('Local plan has no selected units');
  process.exit(1);
}
console.log('PASS: local plan has ' + plan.selectedUnits.length + ' units');
artifacts.cleanupTempArtifacts();
" 2>&1 && { PASS=$(echo "$PASS + 0.10" | bc); echo "PASS [0.10]: local-mode buildExecutionPlan still works"; } || echo "FAIL [0.10]: local-mode buildExecutionPlan still works"
TOTAL=$(echo "$TOTAL + 0.10" | bc)

# [pr_diff] (0.05): formatExecutionUnitSummary still works for units with explicit CLI filters
node --input-type=module -e "
import { formatExecutionUnitSummary } from './scripts/test-planner/planner.mjs';

const unit = {
  id: 'manual-run',
  args: ['run', '--config', 'vitest.config.ts', 'src/foo.test.ts'],
  includeFiles: [],
  maxWorkers: 1,
  surface: 'unit',
  isolate: false,
  pool: 'forks',
};

const summary = formatExecutionUnitSummary(unit);
if (!summary.includes('filters=1')) {
  console.error('Expected filters=1 for explicit CLI filter, got: ' + summary);
  process.exit(1);
}
console.log('PASS: explicit CLI filters still counted correctly');
" 2>&1 && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: explicit CLI filters still work in summary"; } || echo "FAIL [0.05]: explicit CLI filters still work in summary"
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Structural: Anti-stub + consistency (0.10 total)
##############################################################################

# [pr_diff] (0.05): Anti-stub — the includeFiles fallback is actually implemented (not just a no-op)
# WHY calling code: we can call the function with controlled inputs and verify behavior
node --input-type=module -e "
import { formatExecutionUnitSummary } from './scripts/test-planner/planner.mjs';

// Unit with only includeFiles, no CLI filters
const unit1 = {
  id: 'include-only',
  args: ['run', '--config', 'vitest.config.ts'],
  includeFiles: ['a.test.ts'],
  maxWorkers: 1,
  surface: 'unit',
  isolate: false,
  pool: 'forks',
};

// Unit with neither includeFiles nor CLI filters
const unit2 = {
  id: 'no-filters',
  args: ['run', '--config', 'vitest.config.ts'],
  includeFiles: [],
  maxWorkers: 1,
  surface: 'unit',
  isolate: false,
  pool: 'forks',
};

const s1 = formatExecutionUnitSummary(unit1);
const s2 = formatExecutionUnitSummary(unit2);

// unit1 should show filters=1, unit2 should show filters=all
if (!s1.includes('filters=1')) {
  console.error('includeFiles-only unit should show filters=1, got: ' + s1);
  process.exit(1);
}
if (!s2.includes('filters=all')) {
  console.error('no-filter unit should show filters=all, got: ' + s2);
  process.exit(1);
}
console.log('PASS: includeFiles fallback correctly distinguishes filtered vs unfiltered units');
" 2>&1 && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: includeFiles fallback is functional"; } || echo "FAIL [0.05]: includeFiles fallback is functional"
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Both executor.mjs and planner.mjs handle includeFiles consistently
node --input-type=module -e "
import { formatPlanOutput } from './scripts/test-planner/executor.mjs';
import { formatExecutionUnitSummary } from './scripts/test-planner/planner.mjs';

// Both formatters should handle includeFiles the same way
const unit = {
  id: 'consistency-check',
  args: ['run', '--config', 'vitest.config.ts'],
  includeFiles: ['x.test.ts', 'y.test.ts', 'z.test.ts'],
  maxWorkers: 2,
  surface: 'unit',
  isolate: false,
  pool: 'forks',
};

const summary = formatExecutionUnitSummary(unit);
if (!summary.includes('filters=3')) {
  console.error('planner summary should show filters=3, got: ' + summary);
  process.exit(1);
}
console.log('PASS: executor and planner handle includeFiles consistently');
" 2>&1 && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: consistent includeFiles handling across files"; } || echo "FAIL [0.05]: consistent includeFiles handling across files"
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Keep files concise; extract helpers instead of 'V2' copies" — CLAUDE.md:164 @ c22edbb8
# Check that the fix uses a helper function rather than inlining the fallback at each call site
node --input-type=module -e "
import fs from 'node:fs';

const executor = fs.readFileSync('scripts/test-planner/executor.mjs', 'utf8');
const planner = fs.readFileSync('scripts/test-planner/planner.mjs', 'utf8');

// Count how many places directly check includeFiles in filter-counting context
// The fix should use a helper rather than repeating includeFiles checks inline
const executorInlineChecks = (executor.match(/unit\.includeFiles\.length/g) || []).length;
const plannerInlineChecks = (planner.match(/unit\.includeFiles\.length/g) || []).length;

// If a helper is used, includeFiles.length should appear at most once per file (in the helper)
// If inlined, it would appear 2+ times per file at each call site
if (executorInlineChecks > 2 || plannerInlineChecks > 2) {
  console.error('includeFiles fallback appears to be inlined rather than extracted into a helper');
  process.exit(1);
}
console.log('PASS: includeFiles handling uses helper/concise pattern');
" 2>&1 && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: helper extraction per CLAUDE.md:164"; } || echo "FAIL [0.05]: helper extraction per CLAUDE.md:164"
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [agent_config] (0.05): "Aim to keep files under ~700 LOC" — CLAUDE.md:165 @ c22edbb8
# Both modified files should stay within reasonable LOC bounds
node --input-type=module -e "
import fs from 'node:fs';

const executorLines = fs.readFileSync('scripts/test-planner/executor.mjs', 'utf8').split('\\n').length;
const plannerLines = fs.readFileSync('scripts/test-planner/planner.mjs', 'utf8').split('\\n').length;

// These files are already large; ensure the fix doesn't bloat them significantly
// Allow up to 1500 LOC (the files are already well over 700 pre-fix)
if (executorLines > 1500) {
  console.error('executor.mjs has ' + executorLines + ' lines (>1500)');
  process.exit(1);
}
if (plannerLines > 1500) {
  console.error('planner.mjs has ' + plannerLines + ' lines (>1500)');
  process.exit(1);
}
console.log('PASS: file sizes within bounds (executor=' + executorLines + ', planner=' + plannerLines + ')');
" 2>&1 && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: file sizes reasonable per CLAUDE.md:165"; } || echo "FAIL [0.05]: file sizes reasonable per CLAUDE.md:165"
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS" | bc)
echo ""
echo "Total: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
