#!/usr/bin/env bash
# Retrofit all existing harbor_tasks against the 20-rubric quality pipeline.
# Pipeline per task:
#   1. Upload task files to sandbox
#   2. node_qgate (programmatic lint — 20 rubrics, deterministic)
#   3. node_quality_judge (Opus 4.6 via JUDGE_API_KEY, scores 12 llm-judge rubrics)
#   4. node_instruction_reconcile (conditional — cheap MiniMax/GLM/Kimi rewrites
#      instruction.md when judge flags behavior_in_task_description /
#      no_solution_leakage / instruction_no_hint_leakage; re-validates oracle)
#   5. Download updated files (instruction.md + quality.json + reconcile_status.json)
#
# Budget per task: ~$0.08-0.12 (Opus judge) + minimal executor cost.
# For 1096 tasks: ~$90-130 + overnight wall time.

set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

# Enable cheap executors, disable Opus as executor (judge uses it direct via JUDGE_API_KEY)
export FIREWORKS_ENABLED=1   # Kimi (cost_tier 0)
export GLM_ENABLED=1         # GLM-5.1 (cost_tier 0)
export MINIMAX_ENABLED=1     # MiniMax-M2.7 (cost_tier 1)
export ANTHROPIC_ENABLED=0   # Don't route executor through real Claude

# JUDGE_API_KEY defaults to ANTHROPIC_API_KEY via create_worker_sandbox fallback

CONCURRENCY=${CONCURRENCY:-72}
TASK_DIR=${TASK_DIR:-harbor_tasks}
LOG_DIR=pipeline_logs/retrofit_$(date +%Y%m%d_%H%M)
mkdir -p "$LOG_DIR"

# Count candidate tasks (for reporting — e2b_worker scans internally)
task_count=$(find "$TASK_DIR" -mindepth 1 -maxdepth 1 -type d \
  -exec test -f {}/instruction.md \; \
  -exec test -d {}/tests \; \
  -exec test -d {}/environment \; \
  -print | wc -l)

echo "================================================================================="
echo "  RETROFIT LAUNCH — Quality rubric pipeline across existing tasks"
echo "================================================================================="
echo "  Tasks found: $task_count in $TASK_DIR"
echo "  Concurrency: $CONCURRENCY (E2B limit 80)"
echo "  Log dir:     $LOG_DIR"
echo "  Executors:   Kimi (Fireworks) + GLM + MiniMax"
echo "  Judge:       Opus 4.6 (direct Anthropic via JUDGE_API_KEY)"
echo "================================================================================="
echo

# Launch: single process, async concurrency, pool of 3 cheap backends + Opus judge
# e2b_worker with no --input / --tasks scans $TASK_DIR itself via collect_tasks()
.venv/bin/python -m taskforge.e2b_worker \
  --mode pipeline \
  --start-at judge \
  --task-dir "$TASK_DIR" \
  --concurrency "$CONCURRENCY" \
  --pool \
  --no-cleanup \
  --failed-log "$LOG_DIR/failed_retrofit.jsonl" \
  2>&1 | tee "$LOG_DIR/run.log"

echo
echo "Done. See: $LOG_DIR"
