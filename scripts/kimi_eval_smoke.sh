#!/usr/bin/env bash
# Kimi eval smoke test — run 10 harbor trials in parallel, Fireworks Kimi turbo router.
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
  ClickHouse-pr-102080
  airflow-pr-64730
  airflow-pr-64897
  airflow-pr-64725
  airflow-pr-64772
)
STAMP=$(date +%s)
TRIALS_DIR=./trial_runs
mkdir -p /tmp/kimi_eval

for t in "${TASKS[@]}"; do
  # Ensure task.toml has shichaopei/ prefix
  TOML="./harbor_tasks/$t/task.toml"
  if ! grep -q '^name = "shichaopei/' "$TOML" 2>/dev/null; then
    sed -i 's|^name = "\([^"/]*\)"|name = "shichaopei/\1"|' "$TOML" 2>/dev/null || true
  fi

  nohup harbor trial start \
    --path "./harbor_tasks/$t" \
    --agent claude-code \
    --model accounts/fireworks/routers/kimi-k2p5-turbo \
    --environment-type e2b \
    --trial-name "kimi-smoke-$t-$STAMP" \
    --trials-dir "$TRIALS_DIR" \
    --agent-timeout 1800 \
    --ae ANTHROPIC_API_KEY="$FIREWORKS_API_KEY" \
    --ae ANTHROPIC_AUTH_TOKEN="$FIREWORKS_API_KEY" \
    --ae ANTHROPIC_BASE_URL="https://api.fireworks.ai/inference" \
    --ae ANTHROPIC_MODEL="accounts/fireworks/routers/kimi-k2p5-turbo" \
    --ae ANTHROPIC_SMALL_FAST_MODEL="accounts/fireworks/routers/kimi-k2p5-turbo" \
    --ae ANTHROPIC_DEFAULT_OPUS_MODEL="accounts/fireworks/routers/kimi-k2p5-turbo" \
    --ae ANTHROPIC_DEFAULT_SONNET_MODEL="accounts/fireworks/routers/kimi-k2p5-turbo" \
    --ae ANTHROPIC_DEFAULT_HAIKU_MODEL="accounts/fireworks/routers/kimi-k2p5-turbo" \
    > "/tmp/kimi_eval/$t.log" 2>&1 &
  echo "Launched $t (PID $!)"
done
echo "All 10 launched. Logs: /tmp/kimi_eval/"
