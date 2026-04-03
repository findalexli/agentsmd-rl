#!/usr/bin/env bash
# Docker-validate all remade tasks: build, nop=0, gold=1
# Usage: ./scripts/docker_validate_all.sh [WORKERS]
set -uo pipefail

WORKERS=${1:-8}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HARBOR="$ROOT/harbor_tasks"
LOG_FILE="$ROOT/pipeline_logs/docker_validate_$(date +%Y%m%d_%H%M%S).log"
RESULTS_FILE="$ROOT/pipeline_logs/docker_validate_$(date +%Y%m%d_%H%M%S).jsonl"

mkdir -p "$ROOT/pipeline_logs"

echo "Docker validation: $(ls -d $HARBOR/*/tests/test_outputs.py 2>/dev/null | wc -l) tasks with test_outputs.py"
echo "Workers: $WORKERS"
echo "Log: $LOG_FILE"
echo ""

validate_one() {
    local task="$1"
    local task_dir="$HARBOR/$task"
    local result=""

    # Skip tasks without test_outputs.py (not yet remade)
    if [ ! -f "$task_dir/tests/test_outputs.py" ]; then
        echo "{\"task\":\"$task\",\"verdict\":\"skipped\",\"reason\":\"no test_outputs.py\"}" >> "$RESULTS_FILE"
        return
    fi

    # Build
    if ! docker build -q -t "harbor-$task:latest" "$task_dir/environment/" > /dev/null 2>&1; then
        echo "[$(date +%H:%M:%S)] FAIL_BUILD $task" | tee -a "$LOG_FILE"
        echo "{\"task\":\"$task\",\"verdict\":\"fail_build\"}" >> "$RESULTS_FILE"
        return
    fi

    # Nop test (base commit, no fix)
    local nop_dir="/tmp/nop_$$_$task"
    mkdir -p "$nop_dir"
    docker run --rm \
        -v "$task_dir/tests:/tests" \
        -v "$nop_dir:/logs/verifier" \
        "harbor-$task:latest" \
        bash -c "mkdir -p /logs/verifier && chmod +x /tests/test.sh && /tests/test.sh" > "$nop_dir/stdout.txt" 2>&1
    local nop=$(cat "$nop_dir/reward.txt" 2>/dev/null || echo "missing")
    rm -rf "$nop_dir" 2>/dev/null || true

    # Gold test (solve.sh applied)
    local gold_dir="/tmp/gold_$$_$task"
    mkdir -p "$gold_dir"
    docker run --rm \
        -v "$task_dir/tests:/tests" \
        -v "$task_dir/solution:/solution" \
        -v "$gold_dir:/logs/verifier" \
        "harbor-$task:latest" \
        bash -c "mkdir -p /logs/verifier && chmod +x /tests/test.sh /solution/solve.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh" > "$gold_dir/stdout.txt" 2>&1
    local gold=$(cat "$gold_dir/reward.txt" 2>/dev/null || echo "missing")
    rm -rf "$gold_dir" 2>/dev/null || true

    # Verdict
    if [ "$nop" = "0" ] && [ "$gold" = "1" ]; then
        echo "[$(date +%H:%M:%S)] PASS $task" | tee -a "$LOG_FILE"
        echo "{\"task\":\"$task\",\"verdict\":\"pass\",\"nop\":$nop,\"gold\":$gold}" >> "$RESULTS_FILE"
    else
        echo "[$(date +%H:%M:%S)] FAIL $task (nop=$nop, gold=$gold)" | tee -a "$LOG_FILE"
        echo "{\"task\":\"$task\",\"verdict\":\"fail\",\"nop\":\"$nop\",\"gold\":\"$gold\"}" >> "$RESULTS_FILE"
    fi

    # Cleanup image to save disk
    docker rmi "harbor-$task:latest" > /dev/null 2>&1 || true
}

export -f validate_one
export HARBOR RESULTS_FILE LOG_FILE

# Run in parallel
ls -d "$HARBOR"/*/ | xargs -I{} basename {} | \
    xargs -P "$WORKERS" -I{} bash -c 'validate_one "{}"'

# Summary
echo ""
echo "=== Summary ==="
PASS=$(grep -c '"pass"' "$RESULTS_FILE" 2>/dev/null || echo 0)
FAIL=$(grep -c '"fail"' "$RESULTS_FILE" 2>/dev/null || echo 0)
BUILD=$(grep -c '"fail_build"' "$RESULTS_FILE" 2>/dev/null || echo 0)
SKIP=$(grep -c '"skipped"' "$RESULTS_FILE" 2>/dev/null || echo 0)
echo "Pass: $PASS"
echo "Fail: $FAIL"
echo "Build fail: $BUILD"
echo "Skipped: $SKIP"
echo "Results: $RESULTS_FILE"
