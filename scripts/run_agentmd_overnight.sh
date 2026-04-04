#!/usr/bin/env bash
# Overnight pipeline for harbor_tasks_agentmd_edits collection.
#
# Phases:
#   1. Scout PRs that touch both code + agent config files (~400 target)
#   2. Quality filter: remove low-signal PRs programmatically
#   3. Batch scaffold tasks via Claude (opus, $6/task, 4 workers)
#   4. E2B validate all tasks (nop=0, gold=1)
#   5. Retry failed scaffolds with increased budget
#   6. Final E2B validation + summary
#
# Usage:
#   ./scripts/run_agentmd_overnight.sh          # full pipeline
#   ./scripts/run_agentmd_overnight.sh --phase 3  # start from phase 3
#
# Estimated cost: ~$2500 (400 tasks × $6 scaffold) + ~$50 E2B
# Estimated time: 6-8 hours

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TASK_DIR="harbor_tasks_agentmd_edits"
SCOUT_OUTPUT="scouted_agentmd_prs.jsonl"
FILTERED_OUTPUT="scouted_agentmd_prs_filtered.jsonl"
LOG_FILE="pipeline_logs/agentmd_overnight_$(date +%Y%m%d_%H%M%S).log"

mkdir -p pipeline_logs "$TASK_DIR"

# Parse args
START_PHASE=${1:-1}
if [[ "$START_PHASE" == "--phase" ]]; then
    START_PHASE=${2:-1}
fi

log() {
    echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"
}

log "=== AgentMD Overnight Pipeline ==="
log "Start phase: $START_PHASE"
log "Task dir: $TASK_DIR"
log "Log: $LOG_FILE"

# ─────────────────────────────────────────────────────────────────
# Phase 1: Scout PRs
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 1 ]; then
    log ""
    log "━━━ PHASE 1: Scout PRs ━━━"
    log "Target: ~400 PRs that touch both code + agent config files"

    python -m taskforge.scout scout --agentmd \
        --repos-file scouted_repos.jsonl \
        --limit 15 \
        --months 4 \
        --output "$SCOUT_OUTPUT" \
        2>&1 | tee -a "$LOG_FILE"

    SCOUTED_COUNT=$(wc -l < "$SCOUT_OUTPUT")
    log "Scouted: $SCOUTED_COUNT PRs"

    # If we got less than 200, try with higher limit
    if [ "$SCOUTED_COUNT" -lt 200 ]; then
        log "Low count, retrying with --limit 25..."
        python -m taskforge.scout scout --agentmd \
            --repos-file scouted_repos.jsonl \
            --limit 25 \
            --months 4 \
            --output "$SCOUT_OUTPUT" \
            2>&1 | tee -a "$LOG_FILE"
        SCOUTED_COUNT=$(wc -l < "$SCOUT_OUTPUT")
        log "Scouted (retry): $SCOUTED_COUNT PRs"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Phase 2: Quality filter
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 2 ]; then
    log ""
    log "━━━ PHASE 2: Quality filter ━━━"

    python -m taskforge.scout filter --agentmd \
        --input "$SCOUT_OUTPUT" \
        --output "$FILTERED_OUTPUT" \
        2>&1 | tee -a "$LOG_FILE"

    FILTERED_COUNT=$(wc -l < "$FILTERED_OUTPUT")
    log "After filter: $FILTERED_COUNT PRs (from $(wc -l < "$SCOUT_OUTPUT") scouted)"
fi

# ─────────────────────────────────────────────────────────────────
# Phase 3: Batch scaffold (main cost — ~$2500)
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 3 ]; then
    log ""
    log "━━━ PHASE 3: Batch scaffold ━━━"

    INPUT_FILE="$FILTERED_OUTPUT"
    if [ ! -f "$INPUT_FILE" ]; then
        INPUT_FILE="$SCOUT_OUTPUT"
        log "No filtered file, using raw scouted PRs"
    fi

    TASK_COUNT=$(wc -l < "$INPUT_FILE")
    log "Scaffolding $TASK_COUNT tasks (opus, \$6/task, 4 workers, 900s timeout)"
    log "Estimated cost: \$$(echo "$TASK_COUNT * 6" | bc)"
    log "Estimated time: ~$(echo "$TASK_COUNT * 900 / 4 / 3600" | bc) hours"

    python -m taskforge.pipeline scaffold-from-prs \
        --input "$INPUT_FILE" \
        --agentmd \
        --workers 4 \
        --model opus \
        --budget 6.0 \
        --timeout 900 \
        2>&1 | tee -a "$LOG_FILE"

    # Count results
    SCAFFOLDED=$(find "$TASK_DIR" -name "test_outputs.py" | wc -l)
    log "Scaffolded: $SCAFFOLDED tasks with test_outputs.py"
fi

# ─────────────────────────────────────────────────────────────────
# Phase 4: First E2B validation
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 4 ]; then
    log ""
    log "━━━ PHASE 4: E2B validation ━━━"

    python -m taskforge.e2b \
        --task-dir "$TASK_DIR" \
        --concurrency 10 \
        --build-concurrency 5 \
        2>&1 | tee -a "$LOG_FILE"

    RESULTS_FILE="pipeline_logs/e2b_validate_${TASK_DIR}_results.json"
    if [ -f "$RESULTS_FILE" ]; then
        VALID=$(python3 -c "import json; d=json.load(open('$RESULTS_FILE')); print(d.get('valid_count', 0))")
        TOTAL=$(python3 -c "import json; d=json.load(open('$RESULTS_FILE')); print(d.get('total_tasks', 0))")
        log "E2B results: $VALID/$TOTAL valid"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Phase 5: Retry timeouts + failures with higher budget
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 5 ]; then
    log ""
    log "━━━ PHASE 5: Retry failed scaffolds ━━━"

    # Find latest scaffold log dir
    LATEST_LOG=$(ls -td pipeline_logs/scaffold_agentmd_* 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        # Extract timeout/error task names
        RETRY_TASKS=""
        for f in "$LATEST_LOG"/*.json; do
            STATUS=$(python3 -c "import json; print(json.load(open('$f')).get('status',''))" 2>/dev/null || true)
            if [ "$STATUS" = "timeout" ] || [ "$STATUS" = "error" ] || [ "$STATUS" = "budget_exceeded" ]; then
                TASK=$(python3 -c "import json; print(json.load(open('$f')).get('task',''))" 2>/dev/null || true)
                if [ -n "$TASK" ]; then
                    RETRY_TASKS="${RETRY_TASKS:+$RETRY_TASKS,}$TASK"
                fi
            fi
        done

        if [ -n "$RETRY_TASKS" ]; then
            RETRY_COUNT=$(echo "$RETRY_TASKS" | tr ',' '\n' | wc -l)
            log "Retrying $RETRY_COUNT failed tasks with opus, \$8 budget, 1200s timeout"

            python -m taskforge.pipeline scaffold-agentmd \
                --task-dir "$TASK_DIR" \
                --tasks "$RETRY_TASKS" \
                --model opus \
                --budget 8.0 \
                --timeout 1200 \
                --workers 3 \
                2>&1 | tee -a "$LOG_FILE"
        else
            log "No failed tasks to retry"
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Phase 6: Final E2B validation + summary
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 6 ]; then
    log ""
    log "━━━ PHASE 6: Final E2B validation ━━━"

    python -m taskforge.e2b \
        --task-dir "$TASK_DIR" \
        --concurrency 10 \
        --build-concurrency 5 \
        2>&1 | tee -a "$LOG_FILE"

    RESULTS_FILE="pipeline_logs/e2b_validate_${TASK_DIR}_results.json"
    if [ -f "$RESULTS_FILE" ]; then
        VALID=$(python3 -c "import json; d=json.load(open('$RESULTS_FILE')); print(d.get('valid_count', 0))")
        TOTAL=$(python3 -c "import json; d=json.load(open('$RESULTS_FILE')); print(d.get('total_tasks', 0))")
        log ""
        log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        log "  FINAL RESULTS"
        log "  Valid: $VALID / $TOTAL ($(echo "scale=1; $VALID * 100 / $TOTAL" | bc)%)"
        log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
fi

log ""
log "=== Pipeline complete ==="
