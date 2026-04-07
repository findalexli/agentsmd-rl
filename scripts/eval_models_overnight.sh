#!/usr/bin/env bash
# Baseline model evaluation: 50 harbor_tasks + 50 harbor_tasks_agentmd_edits
# across 3 models in parallel (Kimi K2.5, MiniMax M2.7, Qwen3 Coder Next).
#
# Each model runs via a local LiteLLM proxy that maps Anthropic model names
# to the real model on OpenRouter.
#
# agentmd_edits tasks get a second-pass LLM judge score (config edit quality).
#
# Usage:
#   nohup ./scripts/eval_models_overnight.sh 2>&1 | tee pipeline_logs/eval_overnight_$(date +%Y%m%d).log &
#
# Estimated: ~8 hours for 100 tasks × 3 models (3 concurrent)
# Estimated cost: ~$30-60 via OpenRouter

set -euo pipefail
cd "$(dirname "$0")/.."
source .env 2>/dev/null || true

# ── Config ──────────────────────────────────────────────────────
N_CODE=${N_CODE:-50}       # tasks from harbor_tasks/
N_AGENTMD=${N_AGENTMD:-50} # tasks from harbor_tasks_agentmd_edits/
SEED=${SEED:-42}
JOB_PREFIX="eval-baseline-$(date +%Y%m%d-%H%M)"
LOG_DIR="pipeline_logs/${JOB_PREFIX}"
mkdir -p "$LOG_DIR"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_DIR/main.log"; }

# ── Model configs: name -> (openrouter_id, port) ───────────────
declare -A MODEL_IDS=(
  ["kimi-k2.5"]="moonshotai/kimi-k2.5"
  ["minimax-m2.7"]="minimax/minimax-m2.7"
  ["qwen3-coder"]="qwen/qwen3-coder-next"
)
declare -A MODEL_PORTS=(
  ["kimi-k2.5"]=4210
  ["minimax-m2.7"]=4211
  ["qwen3-coder"]=4212
)

# ── Select tasks from both dirs ─────────────────────────────────
select_tasks() {
    local task_dir=$1 n=$2 outfile=$3
    .venv/bin/python -c "
import json, os, random
random.seed($SEED)
tasks = []
for t in sorted(os.listdir('$task_dir')):
    sf = f'$task_dir/{t}/status.json'
    if not os.path.exists(sf): continue
    data = json.load(open(sf))
    if any(v.get('verdict') == 'pass' for v in data.get('validations', [])):
        if os.path.exists(f'$task_dir/{t}/instruction.md'):
            tasks.append(t)
sample = random.sample(tasks, min($n, len(tasks)))
for t in sorted(sample):
    print(t)
" > "$outfile"
}

CODE_TASKS="$LOG_DIR/tasks_code.txt"
AGENTMD_TASKS="$LOG_DIR/tasks_agentmd.txt"

select_tasks harbor_tasks "$N_CODE" "$CODE_TASKS"
select_tasks harbor_tasks_agentmd_edits "$N_AGENTMD" "$AGENTMD_TASKS"

N_CODE_ACTUAL=$(wc -l < "$CODE_TASKS")
N_AGENTMD_ACTUAL=$(wc -l < "$AGENTMD_TASKS")
TOTAL_TASKS=$((N_CODE_ACTUAL + N_AGENTMD_ACTUAL))

log "Selected $N_CODE_ACTUAL code tasks + $N_AGENTMD_ACTUAL agentmd tasks = $TOTAL_TASKS total"

# ── Pre-build Docker images ────────────────────────────────────
log "Pre-building Docker images..."
BUILT=0; CACHED=0; FAILED=0

prebuild_dir() {
    local task_dir=$1 task_file=$2
    while IFS= read -r task; do
        [ -z "$task" ] && continue
        local image="harbor-${task}:latest"
        if docker image inspect "$image" >/dev/null 2>&1; then
            CACHED=$((CACHED + 1))
        else
            if docker build -q -t "$image" "${task_dir}/${task}/environment/" > /dev/null 2>&1; then
                BUILT=$((BUILT + 1))
            else
                FAILED=$((FAILED + 1))
                log "  BUILD FAILED: $task"
                sed -i "/$task/d" "$task_file"
            fi
        fi
        local done=$((BUILT + CACHED + FAILED))
        if [ $((done % 20)) -eq 0 ]; then
            log "  Images: $BUILT built, $CACHED cached, $FAILED failed ($done)"
        fi
    done < "$task_file"
}

prebuild_dir harbor_tasks "$CODE_TASKS"
prebuild_dir harbor_tasks_agentmd_edits "$AGENTMD_TASKS"
log "Images ready: $BUILT built, $CACHED cached, $FAILED failed"

docker builder prune -f --filter "until=30m" > /dev/null 2>&1

# ── Write proxy configs & start proxies ─────────────────────────
PROXY_PIDS=()
for model_name in "${!MODEL_IDS[@]}"; do
    model_id="${MODEL_IDS[$model_name]}"
    port="${MODEL_PORTS[$model_name]}"
    config="$LOG_DIR/proxy_${model_name}.yaml"
    clean_model="${model_id}"

    cat > "$config" <<YAML
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
  - model_name: "claude-haiku-4-5-20251001"
    litellm_params:
      model: "openai/${clean_model}"
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"

litellm_settings:
  drop_params: true
  use_chat_completions_url_for_anthropic_messages: true
YAML

    .venv/bin/litellm --config "$config" --port "$port" \
        > "$LOG_DIR/proxy_${model_name}.log" 2>&1 &
    PROXY_PIDS+=($!)
    log "Started proxy for $model_name on port $port (PID $!)"
done

sleep 15
for model_name in "${!MODEL_PORTS[@]}"; do
    port="${MODEL_PORTS[$model_name]}"
    if curl -s "http://localhost:${port}/health" > /dev/null 2>&1; then
        log "  $model_name (port $port): healthy"
    else
        log "  $model_name (port $port): FAILED"
    fi
done

# ── Cleanup handler ─────────────────────────────────────────────
cleanup() {
    log "Shutting down proxies..."
    for pid in "${PROXY_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
}
trap cleanup EXIT

# ── Run evals in parallel ───────────────────────────────────────
run_task() {
    local model_name=$1 port=$2 task_dir=$3 task=$4 results_file=$5 model_log=$6 idx=$7 total=$8

    local start_time=$(date +%s)
    echo "[$model_name $idx/$total] $task ($task_dir) ($(date +%H:%M))" >> "$model_log"

    OUTPUT=$(timeout 1200 harbor run \
        -p "${task_dir}/${task}" \
        -a claude-code \
        -m claude-opus-4-6 \
        -k 1 \
        --ae "ANTHROPIC_BASE_URL=http://host.docker.internal:${port}" \
        --ae "ANTHROPIC_API_KEY=sk-litellm-local" \
        --job-name "${JOB_PREFIX}-${model_name}-${task}" \
        -y \
        2>&1) || true

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    MEAN=$(echo "$OUTPUT" | grep -oP 'Mean\s+│\s+\K[\d.]+' || echo "ERROR")
    echo "  -> reward=$MEAN (${duration}s)" >> "$model_log"
    echo "$model_name,$task_dir,$task,$MEAN,$duration,$(date -Iseconds)" >> "$results_file"
    echo "$MEAN"
}

eval_model() {
    local model_name=$1 port=$2
    local results_file="$LOG_DIR/results_${model_name}.csv"
    local model_log="$LOG_DIR/${model_name}.log"
    local pass=0 fail=0 error=0 idx=0

    echo "model,task_dir,task,reward,duration_sec,timestamp" > "$results_file"

    # Run code-only tasks
    echo "=== harbor_tasks (code-only) ===" >> "$model_log"
    while IFS= read -r task; do
        [ -z "$task" ] && continue
        idx=$((idx + 1))
        MEAN=$(run_task "$model_name" "$port" harbor_tasks "$task" "$results_file" "$model_log" "$idx" "$TOTAL_TASKS")
        [[ "$MEAN" == "1.000" || "$MEAN" == "1.0" ]] && pass=$((pass + 1)) || { [[ "$MEAN" == "ERROR" ]] && error=$((error + 1)) || fail=$((fail + 1)); }
        [ $((idx % 10)) -eq 0 ] && { docker container prune -f > /dev/null 2>&1; log "[$model_name] $pass pass, $fail fail, $error err ($idx/$TOTAL_TASKS)"; }
    done < "$CODE_TASKS"

    local code_pass=$pass code_total=$idx

    # Run agentmd_edits tasks
    echo "" >> "$model_log"
    echo "=== harbor_tasks_agentmd_edits (code + config) ===" >> "$model_log"
    while IFS= read -r task; do
        [ -z "$task" ] && continue
        idx=$((idx + 1))
        MEAN=$(run_task "$model_name" "$port" harbor_tasks_agentmd_edits "$task" "$results_file" "$model_log" "$idx" "$TOTAL_TASKS")
        [[ "$MEAN" == "1.000" || "$MEAN" == "1.0" ]] && pass=$((pass + 1)) || { [[ "$MEAN" == "ERROR" ]] && error=$((error + 1)) || fail=$((fail + 1)); }
        [ $((idx % 10)) -eq 0 ] && { docker container prune -f > /dev/null 2>&1; log "[$model_name] $pass pass, $fail fail, $error err ($idx/$TOTAL_TASKS)"; }
    done < "$AGENTMD_TASKS"

    local agentmd_pass=$((pass - code_pass))
    local agentmd_total=$((idx - code_total))

    echo "" >> "$model_log"
    echo "=== $model_name FINAL ===" >> "$model_log"
    echo "  Code:    $code_pass/$code_total" >> "$model_log"
    echo "  AgentMD: $agentmd_pass/$agentmd_total" >> "$model_log"
    echo "  Total:   $pass/$idx ($fail fail, $error error)" >> "$model_log"
    log "[$model_name] DONE: code=$code_pass/$code_total agentmd=$agentmd_pass/$agentmd_total total=$pass/$idx"
}

for model_name in "${!MODEL_PORTS[@]}"; do
    port="${MODEL_PORTS[$model_name]}"
    eval_model "$model_name" "$port" &
done

log "All 3 model evals launched ($TOTAL_TASKS tasks each)"
log "Monitor: tail -f $LOG_DIR/*.log"

wait

# ── LLM Judge for agentmd_edits ─────────────────────────────────
log ""
log "━━━ Running LLM judge on agentmd_edits results ━━━"
# The judge evaluates config edit quality using gold references
for model_name in "${!MODEL_IDS[@]}"; do
    results_file="$LOG_DIR/results_${model_name}.csv"
    if [ -f "$results_file" ]; then
        # Extract agentmd tasks that passed code tests (reward=1)
        agentmd_passed=$(grep "harbor_tasks_agentmd_edits.*,1\.0\|harbor_tasks_agentmd_edits.*,1\.000," "$results_file" | cut -d, -f3 || true)
        if [ -n "$agentmd_passed" ]; then
            log "  [$model_name] Running judge on $(echo "$agentmd_passed" | wc -l) passed agentmd tasks..."
            # TODO: integrate taskforge.judge for config edit scoring
            # For now, code test pass = baseline score
        fi
    fi
done

# ── Summary ─────────────────────────────────────────────────────
log ""
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "  BASELINE MODEL EVALUATION RESULTS"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for model_name in "${!MODEL_IDS[@]}"; do
    results_file="$LOG_DIR/results_${model_name}.csv"
    if [ -f "$results_file" ]; then
        TOTAL=$(tail -n +2 "$results_file" | wc -l)
        PASS=$(tail -n +2 "$results_file" | grep -cE ',1\.0+,' || echo 0)

        CODE_TOTAL=$(tail -n +2 "$results_file" | grep -c "harbor_tasks," || echo 0)
        CODE_PASS=$(tail -n +2 "$results_file" | grep "harbor_tasks," | grep -cE ',1\.0+,' || echo 0)

        AGENTMD_TOTAL=$(tail -n +2 "$results_file" | grep -c "harbor_tasks_agentmd_edits" || echo 0)
        AGENTMD_PASS=$(tail -n +2 "$results_file" | grep "harbor_tasks_agentmd_edits" | grep -cE ',1\.0+,' || echo 0)

        AVG_TIME=$(tail -n +2 "$results_file" | awk -F, '{sum+=$5; n++} END {printf "%.0f", sum/n}')

        log ""
        log "  $model_name (${MODEL_IDS[$model_name]}):"
        log "    Code tasks:    $CODE_PASS/$CODE_TOTAL ($([ $CODE_TOTAL -gt 0 ] && echo "scale=1; $CODE_PASS * 100 / $CODE_TOTAL" | bc || echo 0)%)"
        log "    AgentMD tasks: $AGENTMD_PASS/$AGENTMD_TOTAL ($([ $AGENTMD_TOTAL -gt 0 ] && echo "scale=1; $AGENTMD_PASS * 100 / $AGENTMD_TOTAL" | bc || echo 0)%)"
        log "    Total:         $PASS/$TOTAL avg=${AVG_TIME}s/task"
    fi
done

log ""
log "Results CSVs: $LOG_DIR/results_*.csv"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
