#!/usr/bin/env bash
# Validate all harbor tasks end-to-end:
# 1. Wait for any running audit to finish
# 2. Re-lint to verify audit fixes
# 3. Run Docker oracle validation in batches (manage disk)
# 4. Update status.json per task
# 5. Generate summary
#
# Usage: nohup ./scripts/validate_and_fix.sh 2>&1 | tee pipeline_logs/validate_e2e_$(date +%Y%m%d_%H%M%S).log &
set -uo pipefail
cd "$(dirname "$0")/.."

BATCH_SIZE=30  # validate N tasks, then cleanup Docker
echo "============================================================"
echo "  E2E Validation Pipeline — $(date)"
echo "  Batch size: $BATCH_SIZE (Docker cleanup between batches)"
echo "============================================================"

# ──────────────────────────────────────────────────────────────
# Step 1: Wait for running audit to finish
# ──────────────────────────────────────────────────────────────
AUDIT_PID=$(pgrep -f "run_pipeline.py audit" || true)
if [ -n "$AUDIT_PID" ]; then
    echo ""
    echo "=== Step 1: Waiting for audit (PID $AUDIT_PID) to finish ==="
    while kill -0 "$AUDIT_PID" 2>/dev/null; do
        DONE=$(grep -c ' OK ' pipeline_logs/audit_lint_failures_*.log 2>/dev/null || echo "?")
        echo "  $(date +%H:%M) — audit in progress ($DONE completed)"
        sleep 120
    done
    echo "  Audit finished at $(date)"
else
    echo ""
    echo "=== Step 1: No audit running, skipping wait ==="
fi

# ──────────────────────────────────────────────────────────────
# Step 2: Re-lint after audit
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Step 2: Re-lint all tasks ==="
python scripts/lint_tasks.py --severity critical 2>&1 | tail -8

# ──────────────────────────────────────────────────────────────
# Step 3: Docker oracle validation in batches
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Step 3: Docker oracle validation ==="

# Get tasks that need validation (no 'pass' verdict yet)
TASKS_TO_VALIDATE=$(python3 -c "
import json, os
tasks = sorted(d for d in os.listdir('harbor_tasks') if os.path.isdir(f'harbor_tasks/{d}'))
need = []
for t in tasks:
    # Must have test.sh and solve.sh
    if not os.path.exists(f'harbor_tasks/{t}/tests/test.sh'): continue
    if not os.path.exists(f'harbor_tasks/{t}/solution/solve.sh'): continue
    # Skip TODOs
    test_content = open(f'harbor_tasks/{t}/tests/test.sh').read()
    if 'TODO: Implement' in test_content or 'TODO: Agent' in test_content: continue
    solve_content = open(f'harbor_tasks/{t}/solution/solve.sh').read()
    if 'TODO: Apply' in solve_content or 'TODO: Agent' in solve_content: continue
    # Skip already validated PASS
    sf = f'harbor_tasks/{t}/status.json'
    if os.path.exists(sf):
        data = json.load(open(sf))
        if any(v.get('verdict') == 'pass' for v in data.get('validations', [])):
            continue
    need.append(t)
print('\n'.join(need))
")

TOTAL=$(echo "$TASKS_TO_VALIDATE" | grep -c . || echo 0)
echo "Tasks needing validation: $TOTAL"

if [ "$TOTAL" -eq 0 ]; then
    echo "All tasks already validated!"
else
    PASS=0; FAIL_ORACLE=0; FAIL_NOP=0; ERROR=0; BATCH_NUM=0

    echo "$TASKS_TO_VALIDATE" | while IFS= read -r task; do
        [ -z "$task" ] && continue
        BATCH_NUM=$((BATCH_NUM + 1))

        image="harbor-${task}:latest"

        # Build image
        if ! docker image inspect "$image" >/dev/null 2>&1; then
            echo "  [$BATCH_NUM/$TOTAL] Building $task..."
            if ! docker build -q -t "$image" "harbor_tasks/${task}/environment/" 2>&1 | tail -1; then
                echo "  [$BATCH_NUM/$TOTAL] BUILD FAILED: $task"
                # Write status
                python3 -c "
import json
from pathlib import Path
sf = Path('harbor_tasks/$task/status.json')
data = json.loads(sf.read_text()) if sf.exists() else {'validations': []}
data['validations'].append({
    'timestamp': '$(date -Iseconds)',
    'runner': 'validate_and_fix.sh',
    'docker_build': False,
    'gold_score': None,
    'nop_score': None,
    'verdict': 'fail_build',
    'notes': 'Docker build failed'
})
sf.write_text(json.dumps(data, indent=2))
"
                continue
            fi
        fi

        # Rubric mount (optional — some tasks don't have it)
        RUBRIC_MOUNT=""
        if [ -f "harbor_tasks/${task}/rubric.yaml" ]; then
            RUBRIC_MOUNT="-v $(pwd)/harbor_tasks/${task}/rubric.yaml:/rubric.yaml:ro"
        fi

        # Oracle test: gold patch
        # mkdir -p /logs/verifier ensures reward path exists (327/430 Dockerfiles miss this)
        oracle=$(timeout 180 docker run --rm --memory=4g --cpus=1 \
            -v "$(pwd)/harbor_tasks/${task}/solution:/solution" \
            -v "$(pwd)/harbor_tasks/${task}/tests:/tests" \
            $RUBRIC_MOUNT \
            "$image" \
            bash -c "mkdir -p /logs/verifier && chmod +x /solution/solve.sh /tests/test.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh 2>/dev/null; cat /logs/verifier/reward.txt 2>/dev/null || echo ERROR" 2>&1 | tail -1)

        # Nop test: no patch
        nop=$(timeout 180 docker run --rm --memory=4g --cpus=1 \
            -v "$(pwd)/harbor_tasks/${task}/tests:/tests" \
            $RUBRIC_MOUNT \
            "$image" \
            bash -c "mkdir -p /logs/verifier && chmod +x /tests/test.sh && /tests/test.sh 2>/dev/null; cat /logs/verifier/reward.txt 2>/dev/null || echo ERROR" 2>&1 | tail -1)

        # Determine verdict
        if [[ "$oracle" =~ ^1(\.0)?$ ]] && ! [[ "$nop" =~ ^1(\.0)?$ ]]; then
            verdict="pass"
        elif [[ "$nop" =~ ^1(\.0)?$ ]]; then
            verdict="fail_nop_high"
        elif [[ "$oracle" == "ERROR" ]]; then
            verdict="error"
        else
            verdict="fail_gold"
        fi

        echo "  [$BATCH_NUM/$TOTAL] $task: oracle=$oracle nop=$nop [$verdict]"

        # Write status.json
        python3 -c "
import json
from pathlib import Path
sf = Path('harbor_tasks/$task/status.json')
data = json.loads(sf.read_text()) if sf.exists() else {'validations': []}
data['validations'].append({
    'timestamp': '$(date -Iseconds)',
    'runner': 'validate_and_fix.sh',
    'docker_build': True,
    'gold_score': float('$oracle') if '$oracle' not in ['ERROR',''] else None,
    'nop_score': float('$nop') if '$nop' not in ['ERROR',''] else None,
    'verdict': '$verdict',
    'notes': ''
})
sf.write_text(json.dumps(data, indent=2))
" 2>/dev/null || true

        # Docker cleanup every BATCH_SIZE tasks
        if [ $((BATCH_NUM % BATCH_SIZE)) -eq 0 ]; then
            echo "  --- Docker cleanup (batch $((BATCH_NUM / BATCH_SIZE))) ---"
            docker container prune -f >/dev/null 2>&1
            docker image prune -f >/dev/null 2>&1
            docker builder prune -f --filter "until=30m" >/dev/null 2>&1
        fi
    done
fi

# ──────────────────────────────────────────────────────────────
# Step 4: Generate final summary
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Step 4: Final summary ==="
python -m taskforge.validate --summary-only

echo ""
echo "============================================================"
echo "  Validation complete — $(date)"
echo "============================================================"
