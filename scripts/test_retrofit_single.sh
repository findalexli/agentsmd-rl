#!/usr/bin/env bash
# End-to-end test of the new qgate + quality_judge + instruction_reconcile pipeline
# against a single existing task. Uses MiniMax as cheap executor, Opus 4.6 as judge.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

TASK="${1:-airflow-pr-64897}"
echo "Testing retrofit pipeline on: $TASK"
echo "Expected: judge flags instruction issues, reconcile rewrites instruction.md, revalidate keeps nop=0/gold=1"

# Enable MiniMax as executor (cheap), Fireworks as fallback
export FIREWORKS_ENABLED=1
export MINIMAX_ENABLED=1
export GLM_ENABLED=1
export ANTHROPIC_ENABLED=0
# JUDGE_API_KEY falls back to ANTHROPIC_API_KEY — no need to set explicitly

# Retrofit a single task: start_at=validate so we skip scaffold/rubric/enrich/improve
.venv/bin/python -m taskforge.e2b_worker \
  --mode pipeline \
  --start-at judge \
  --tasks "$TASK" \
  --task-dir harbor_tasks \
  --concurrency 1 \
  --pool \
  --no-cleanup \
  2>&1 | tee /tmp/retrofit_single_${TASK}.log
