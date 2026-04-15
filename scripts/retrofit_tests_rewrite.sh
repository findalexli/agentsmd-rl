#!/usr/bin/env bash
# Round 2 retrofit: rewrite test_outputs.py for tasks whose judge flagged
# test-design rubrics (tests_verify_behavior_not_text, solution_uniqueness_guard,
# test_not_tautological). Reuses the same 72-worker infra + Opus judge; new
# executor prompt is taskforge/prompts/tests_rewrite.md.
#
# Pre-filters to only tasks with relevant Tier-A fails in their existing
# quality.json — saves judge $ for tasks that don't need rewrite.

set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

# Revised pool (see backends.py — minimax 20→50, fireworks 100→50)
export FIREWORKS_ENABLED=1
export GLM_ENABLED=1
export MINIMAX_ENABLED=1
export ANTHROPIC_ENABLED=0

CONCURRENCY=${CONCURRENCY:-100}  # E2B limit is 100; using full capacity.
TASK_DIR=${TASK_DIR:-harbor_tasks}
LOG_DIR=pipeline_logs/tests_rewrite_$(date +%Y%m%d_%H%M)
mkdir -p "$LOG_DIR"

# Pre-filter: identify tasks where judge flagged test-design rubrics
echo "Pre-filtering tasks that need test rewrite..."
.venv/bin/python - <<'PY' > "$LOG_DIR/candidates.txt"
import json
from pathlib import Path

TEST_RUBRICS = {
    "tests_verify_behavior_not_text",
    "solution_uniqueness_guard",
    "test_not_tautological",
}

candidates = []
total_scanned = 0
for p in sorted(Path("harbor_tasks").glob("*/quality.json")):
    total_scanned += 1
    try:
        d = json.loads(p.read_text())
    except Exception:
        continue
    if d.get("error"):
        continue
    # Look at judge_summary_post (latest) if it exists on disk, else tier_a_fails
    fails = set(d.get("tier_a_fails", []) or [])
    if fails & TEST_RUBRICS:
        candidates.append(p.parent.name)

import sys
print("\n".join(candidates), end="")
print(f"Scanned {total_scanned} quality.json, {len(candidates)} need test rewrite",
      file=sys.stderr)
PY
n=$(wc -l < "$LOG_DIR/candidates.txt")

echo "================================================================================="
echo "  TESTS REWRITE RUN — round 2 retrofit (behavioral test rewrites)"
echo "================================================================================="
echo "  Candidates:  $n"
echo "  Concurrency: $CONCURRENCY"
echo "  Log dir:     $LOG_DIR"
echo "  Pool:        GLM (30) + MiniMax (50) + Kimi (50) + OAuth Sonnet 4.6 (15) = 145 capacity"
echo "  Target rubrics: tests_verify_behavior_not_text, solution_uniqueness_guard,"
echo "                  test_not_tautological"
echo "================================================================================="
echo

# Feed candidates as comma-separated --tasks
candidates_csv=$(paste -sd, "$LOG_DIR/candidates.txt")
# Also keep a deduped copy so resume can use it
sort -u "$LOG_DIR/candidates.txt" > "$LOG_DIR/candidates_sorted.txt"

# Launch with start-at=judge: the new node_tests_rewrite fires after judge if
# latest quality.json flags test-design rubrics.
.venv/bin/python -m taskforge.e2b_worker \
  --mode pipeline \
  --start-at judge \
  --tasks "$candidates_csv" \
  --task-dir "$TASK_DIR" \
  --concurrency "$CONCURRENCY" \
  --pool \
  --no-cleanup \
  --failed-log "$LOG_DIR/failed_tests_rewrite.jsonl" \
  2>&1 | tee "$LOG_DIR/run.log"

echo
echo "Done. See: $LOG_DIR"
