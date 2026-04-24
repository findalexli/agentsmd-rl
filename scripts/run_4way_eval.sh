#!/usr/bin/env bash
# Orchestrate 4-way model eval: Opus / Kimi (ARK) / MiniMax (direct) / GLM-5.1.
# Runs all 4 backends IN PARALLEL, each with its own scratch dir and a unique
# Dockerfile LABEL so their E2B template hashes don't collide.
# c=3 per backend (independent API accounts — no cross-backend rate-limit contention).
#
# Usage: scripts/run_4way_eval.sh
set -eu
cd "$(dirname "$0")/.."
source .env

TASKS=pipeline_logs/4way_eval/tasks.txt
TS=$(date +%Y%m%d-%H%M%S)
ORCH_LOG=pipeline_logs/4way_eval/orchestrator.log
: > "$ORCH_LOG"

launch () {
    local backend=$1
    local conc=$2
    local dir=pipeline_logs/4way_eval/$backend
    local scratch=/tmp/agent_eval_${backend}
    mkdir -p "$dir"
    rm -rf "$scratch"
    echo "$(date '+%H:%M:%S') launching $backend conc=$conc scratch=$scratch" >> "$ORCH_LOG"
    EVAL_SCRATCH_DIR="$scratch" nohup .venv/bin/python scripts/run_agent_eval.py \
        --tasks  "$TASKS" \
        --out    "$dir/results.jsonl" \
        --backend "$backend" \
        --concurrency "$conc" \
        --env e2b \
        --timeout 2400 \
        --run-id "4way-${backend}-${TS}" \
        > "$dir/run.log" 2>&1 &
    local pid=$!
    echo "$backend pid=$pid" >> "$ORCH_LOG"
    echo "$pid" > "$dir/pid"
}

launch minimax   3
launch glm5      3
launch kimi      3
launch anthropic 3

echo "$(date '+%H:%M:%S') all 4 launched, waiting" >> "$ORCH_LOG"
wait
echo "$(date '+%H:%M:%S') all 4 finished" >> "$ORCH_LOG"
