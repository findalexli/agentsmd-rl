#!/usr/bin/env bash
# Parallel model evaluation: run N tasks per model via Harbor + LiteLLM proxy.
#
# Starts one LiteLLM proxy per model (different ports), then launches
# Harbor runs in parallel using E2B sandboxes.
#
# Usage:
#   ./scripts/eval_models_parallel.sh                    # defaults
#   ./scripts/eval_models_parallel.sh --tasks 10 --env docker  # docker instead of e2b
#
# Requires: OPENROUTER_API_KEY in .env, E2B_API_KEY in .env (for e2b mode)

set -euo pipefail
cd "$(dirname "$0")/.."
source .env 2>/dev/null || true

# ── Config ──────────────────────────────────────────────────────
N_TASKS=${TASKS:-10}
ENV_TYPE=${ENV:-docker}  # "docker" (e2b can't reach local proxy)
JOB_PREFIX="model-eval-$(date +%Y%m%d-%H%M)"
LOG_DIR="pipeline_logs/${JOB_PREFIX}"
mkdir -p "$LOG_DIR"

# Models to evaluate (OpenRouter IDs)
declare -A MODELS=(
  ["kimi-k2.5"]="moonshotai/kimi-k2.5"
  ["minimax-m2.7"]="minimax/minimax-m2.7"
  ["qwen3-coder-next"]="qwen/qwen3-coder-next"
)

# Port allocation: one proxy per model
BASE_PORT=4200

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_DIR/eval.log"; }

# ── Select tasks ────────────────────────────────────────────────
log "Selecting $N_TASKS validated tasks..."
TASK_LIST=$(.venv/bin/python -c "
import json, os, random
random.seed(42)
tasks = []
for t in sorted(os.listdir('harbor_tasks')):
    sf = f'harbor_tasks/{t}/status.json'
    if not os.path.exists(sf): continue
    data = json.load(open(sf))
    if any(v.get('verdict') == 'pass' for v in data.get('validations', [])):
        if os.path.exists(f'harbor_tasks/{t}/instruction.md'):
            tasks.append(t)
sample = random.sample(tasks, min($N_TASKS, len(tasks)))
print('\n'.join(sample))
")
log "Selected tasks:"
echo "$TASK_LIST" | while read t; do log "  $t"; done

# ── Write proxy configs ────────────────────────────────────────
write_proxy_config() {
    local model_id=$1 port=$2 outfile=$3
    local clean_model=${model_id#openrouter/}
    cat > "$outfile" <<YAML
model_list:
  - model_name: "claude-opus-4-6"
    litellm_params:
      model: "openai/${clean_model}"
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"
  - model_name: "claude-sonnet-4-6"
    litellm_params:
      model: "openai/${clean_model}"
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"

litellm_settings:
  drop_params: true
  use_chat_completions_url_for_anthropic_messages: true
YAML
}

# ── Start proxies ──────────────────────────────────────────────
PROXY_PIDS=()
PORT_MAP=()
IDX=0

for model_name in "${!MODELS[@]}"; do
    model_id="${MODELS[$model_name]}"
    port=$((BASE_PORT + IDX))
    config_file="$LOG_DIR/proxy_${model_name}.yaml"

    write_proxy_config "$model_id" "$port" "$config_file"

    log "Starting proxy for $model_name ($model_id) on port $port..."
    .venv/bin/litellm --config "$config_file" --port "$port" \
        > "$LOG_DIR/proxy_${model_name}.log" 2>&1 &
    PROXY_PIDS+=($!)
    PORT_MAP+=("$model_name:$port")
    IDX=$((IDX + 1))
done

# Wait for proxies to be ready
log "Waiting for proxies to start..."
sleep 15
for entry in "${PORT_MAP[@]}"; do
    name="${entry%%:*}"
    port="${entry##*:}"
    if curl -s "http://localhost:${port}/health" > /dev/null 2>&1; then
        log "  $name (port $port): healthy"
    else
        log "  $name (port $port): FAILED — check $LOG_DIR/proxy_${name}.log"
    fi
done

# ── Cleanup function ───────────────────────────────────────────
cleanup() {
    log "Cleaning up proxies..."
    for pid in "${PROXY_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
}
trap cleanup EXIT

# ── Run evaluations ────────────────────────────────────────────
HARBOR_PIDS=()

for entry in "${PORT_MAP[@]}"; do
    model_name="${entry%%:*}"
    port="${entry##*:}"

    log "Launching Harbor eval for $model_name ($N_TASKS tasks, env=$ENV_TYPE)..."

    (
        PASS=0; FAIL=0; ERROR=0
        echo "$TASK_LIST" | while IFS= read -r task; do
            [ -z "$task" ] && continue

            log "  [$model_name] Starting: $task"

            # Determine host URL based on env type
            if [ "$ENV_TYPE" = "docker" ]; then
                HOST_URL="http://host.docker.internal:${port}"
            else
                # E2B needs external-facing URL — use ngrok or direct IP
                # For now, E2B sandboxes can't reach localhost, so we need a tunnel
                HOST_URL="http://host.docker.internal:${port}"
            fi

            OUTPUT=$(harbor run \
                -p "harbor_tasks/${task}" \
                -a claude-code \
                -m claude-opus-4-6 \
                -k 1 \
                -e "$ENV_TYPE" \
                --ae "ANTHROPIC_BASE_URL=${HOST_URL}" \
                --ae "ANTHROPIC_API_KEY=sk-litellm-local" \
                --job-name "${JOB_PREFIX}-${model_name}-${task}" \
                -y \
                2>&1) || true

            MEAN=$(echo "$OUTPUT" | grep -oP 'Mean\s+│\s+\K[\d.]+' || echo "ERROR")
            log "  [$model_name] $task: reward=$MEAN"

            # Append to results
            echo "$task,$MEAN" >> "$LOG_DIR/results_${model_name}.csv"
        done

        log "[$model_name] All tasks complete"
    ) > "$LOG_DIR/harbor_${model_name}.log" 2>&1 &
    HARBOR_PIDS+=($!)
done

log "All ${#MODELS[@]} model evals launched in parallel"
log "Logs: $LOG_DIR/"
log "Monitor: tail -f $LOG_DIR/harbor_*.log"

# ── Wait for all to finish ─────────────────────────────────────
log "Waiting for all evaluations to complete..."
for pid in "${HARBOR_PIDS[@]}"; do
    wait "$pid" || true
done

# ── Summary ────────────────────────────────────────────────────
log ""
log "━━━ RESULTS SUMMARY ━━━"
for model_name in "${!MODELS[@]}"; do
    results_file="$LOG_DIR/results_${model_name}.csv"
    if [ -f "$results_file" ]; then
        TOTAL=$(wc -l < "$results_file")
        PASS=$(grep -c ',1\.0\|,1$' "$results_file" || echo 0)
        log "  $model_name: $PASS/$TOTAL passed ($(echo "scale=0; $PASS * 100 / $TOTAL" | bc)%)"
    else
        log "  $model_name: no results"
    fi
done
log ""
log "Full logs: $LOG_DIR/"
