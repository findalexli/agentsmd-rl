#!/usr/bin/env bash
# Opus 4.6 eval smoke test — same 10 tasks as kimi_eval_smoke.sh for head-to-head.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env
set +a

TASKS=(
  airflow-openlineage-dagrun-partition-fields
  airflow-chart-celery-volumeclaim
  airflow-pr-64853
  airflow-pr-64736
  airflow-pr-64916
  airflow-pr-64730
  airflow-pr-64725
  airflow-pr-64772
)

STAMP=$(date +%s)
TRIALS_DIR=./trial_runs
mkdir -p /tmp/opus_eval

for t in "${TASKS[@]}"; do
  TOML="./harbor_tasks/$t/task.toml"
  if ! grep -q '^name = "shichaopei/' "$TOML" 2>/dev/null; then
    sed -i 's|^name = "\([^"/]*\)"|name = "shichaopei/\1"|' "$TOML" 2>/dev/null || true
  fi

  nohup harbor trial start \
    --path "./harbor_tasks/$t" \
    --agent claude-code \
    --model "claude-opus-4-6" \
    --environment-type e2b \
    --trial-name "opus-smoke-$t-$STAMP" \
    --trials-dir "$TRIALS_DIR" \
    --agent-timeout 1800 \
    --ae ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    > "/tmp/opus_eval/$t.log" 2>&1 &
  echo "Launched $t (PID $!)"
done
echo "All ${#TASKS[@]} launched. Logs: /tmp/opus_eval/"
