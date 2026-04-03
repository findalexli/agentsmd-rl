#!/usr/bin/env bash
# Scaffold new tasks from PR refs in parallel using claude -p
# Usage: ./scripts/scaffold_new.sh <file_with_pr_refs> [workers]
set -uo pipefail

INPUT_FILE="${1:-/tmp/scaffold_pilot.txt}"
WORKERS="${2:-4}"
LOG_DIR="pipeline_logs/scaffold_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

echo "Scaffolding $(wc -l < "$INPUT_FILE") new tasks from $INPUT_FILE"
echo "Workers: $WORKERS"
echo "Log dir: $LOG_DIR"
echo ""

PROMPT_FILE="taskforge/prompts/scaffold.md"

scaffold_one() {
    local pr_ref="$1"
    local slug=$(echo "$pr_ref" | tr '/#' '-' | tr '[:upper:]' '[:lower:]')
    local log_file="$LOG_DIR/${slug}.json"

    echo "[$(date +%H:%M:%S)] START $pr_ref"

    # Substitute $ARGUMENTS in the prompt
    local prompt=$(sed "s|\$ARGUMENTS|$pr_ref|g" "$PROMPT_FILE")

    local result
    result=$(echo "$prompt" | claude -p \
        --dangerously-skip-permissions \
        --model opus \
        --max-budget-usd 10.0 \
        --output-format json \
        2>/dev/null)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "[$(date +%H:%M:%S)] OK $pr_ref"
        echo "{\"pr_ref\": \"$pr_ref\", \"status\": \"success\", \"exit_code\": $exit_code}" > "$log_file"
    else
        echo "[$(date +%H:%M:%S)] FAIL $pr_ref (exit $exit_code)"
        echo "{\"pr_ref\": \"$pr_ref\", \"status\": \"error\", \"exit_code\": $exit_code}" > "$log_file"
    fi
}

export -f scaffold_one
export LOG_DIR PROMPT_FILE

cat "$INPUT_FILE" | xargs -P "$WORKERS" -I{} bash -c 'scaffold_one "{}"'

# Summary
echo ""
echo "=== Summary ==="
OK=$(grep -l '"success"' "$LOG_DIR"/*.json 2>/dev/null | wc -l)
FAIL=$(grep -l '"error"' "$LOG_DIR"/*.json 2>/dev/null | wc -l)
echo "  Success: $OK"
echo "  Failed: $FAIL"
echo "  Log dir: $LOG_DIR"
