#!/usr/bin/env bash
# Overnight pipeline: scout new repos, scaffold tasks with Kimi, audit everything.
# Optimizes for quality: scout wide (80/repo), filter hard, scaffold best candidates.
#
# Usage: ./scripts/overnight_pipeline.sh 2>&1 | tee pipeline_logs/overnight_$(date +%Y%m%d_%H%M%S).log
set -uo pipefail
cd "$(dirname "$0")/.."
set -a && source .env && set +a

WORKERS=4
SCAFFOLD_TIMEOUT=900
AUDIT_TIMEOUT=900
MODEL="moonshotai/kimi-k2.5"
SCOUT_PER_REPO=80   # Scout wide, filter hard

echo "============================================================"
echo "  Overnight Pipeline — $(date)"
echo "  Model: $MODEL | Workers: $WORKERS"
echo "  Strategy: scout $SCOUT_PER_REPO/repo → filter → scaffold → audit"
echo "============================================================"

# ──────────────────────────────────────────────────────────────
# Phase 0: Audit the existing unaudited tasks FIRST
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 0: Audit existing unaudited tasks via Kimi ==="

UNAUDITED=$(python3 -c "
import json, os
tasks = sorted(d for d in os.listdir('harbor_tasks') if os.path.isdir(f'harbor_tasks/{d}'))
unaudited = []
for t in tasks:
    sf = f'harbor_tasks/{t}/status.json'
    has_audit = False
    if os.path.exists(sf):
        data = json.load(open(sf))
        for v in data.get('validations', []):
            if 'audit' in v.get('phase', '') or 'audit' in v.get('runner', ''):
                has_audit = True
                break
    if not has_audit and os.path.exists(f'harbor_tasks/{t}/tests/test.sh'):
        unaudited.append(t)
print(','.join(unaudited))
")

if [ -n "$UNAUDITED" ]; then
    UNAUDITED_COUNT=$(echo "$UNAUDITED" | tr ',' '\n' | wc -l)
    echo "Unaudited tasks: $UNAUDITED_COUNT"

    python -m taskforge.proxy --model "$MODEL" -- \
        python -m taskforge.pipeline audit-tests \
        --tasks "$UNAUDITED" \
        --workers "$WORKERS" \
        --timeout "$AUDIT_TIMEOUT" || echo "  (some audit failures, continuing)"
else
    echo "All existing tasks already audited."
fi

# ──────────────────────────────────────────────────────────────
# Phase 1: Scout PRs (wide net)
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 1: Scout PRs ($SCOUT_PER_REPO per repo) ==="
python -m taskforge.scout scout \
    --repos-file scouted_repos.jsonl \
    --output scouted_prs_new.jsonl \
    --limit "$SCOUT_PER_REPO"

SCOUTED=$(wc -l < scouted_prs_new.jsonl)
echo "Scouted: $SCOUTED PRs"

# ──────────────────────────────────────────────────────────────
# Phase 2: Pre-filter (free, Python only)
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 2: Pre-filter ==="
python -m taskforge.scout filter \
    --input scouted_prs_new.jsonl \
    --output filtered_prs_new.jsonl

FILTERED=$(wc -l < filtered_prs_new.jsonl)
echo "After filter: $FILTERED PRs"

# ──────────────────────────────────────────────────────────────
# Phase 3: Scaffold via Kimi (the expensive step)
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 3: Scaffold new tasks via Kimi ==="
echo "  Input: $FILTERED candidates"

python -m taskforge.proxy --model "$MODEL" -- \
    python -m taskforge.pipeline scaffold-from-prs \
    --input filtered_prs_new.jsonl \
    --workers "$WORKERS" \
    --timeout "$SCAFFOLD_TIMEOUT" \
    --model opus \
    --budget 100.0 || echo "  (some scaffold failures, continuing)"

TOTAL_TASKS=$(ls -d harbor_tasks/*/ 2>/dev/null | wc -l)
echo "Total tasks on disk: $TOTAL_TASKS"

# ──────────────────────────────────────────────────────────────
# Phase 4: Lint all new tasks (free)
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 4: Lint ==="
python -m taskforge.lint --severity critical

# ──────────────────────────────────────────────────────────────
# Phase 5: Audit newly scaffolded tasks via Kimi
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 5: Audit new tasks via Kimi ==="

NEW_UNAUDITED=$(python3 -c "
import json, os
tasks = sorted(d for d in os.listdir('harbor_tasks') if os.path.isdir(f'harbor_tasks/{d}'))
unaudited = []
for t in tasks:
    sf = f'harbor_tasks/{t}/status.json'
    has_audit = False
    if os.path.exists(sf):
        data = json.load(open(sf))
        for v in data.get('validations', []):
            if 'audit' in v.get('phase', '') or 'audit' in v.get('runner', ''):
                has_audit = True
                break
    if not has_audit and os.path.exists(f'harbor_tasks/{t}/tests/test.sh'):
        unaudited.append(t)
print(','.join(unaudited))
")

if [ -n "$NEW_UNAUDITED" ]; then
    NEW_COUNT=$(echo "$NEW_UNAUDITED" | tr ',' '\n' | wc -l)
    echo "New unaudited tasks: $NEW_COUNT"

    python -m taskforge.proxy --model "$MODEL" -- \
        python -m taskforge.pipeline audit-tests \
        --tasks "$NEW_UNAUDITED" \
        --workers "$WORKERS" \
        --timeout "$AUDIT_TIMEOUT" || echo "  (some audit failures, continuing)"
else
    echo "No new tasks need audit."
fi

# ──────────────────────────────────────────────────────────────
# Phase 6: Final status
# ──────────────────────────────────────────────────────────────
echo ""
echo "=== Phase 6: Write status ==="
python -m taskforge.validate --summary-only

echo ""
echo "============================================================"
echo "  Pipeline complete — $(date)"
echo "  Total tasks: $(ls -d harbor_tasks/*/ 2>/dev/null | wc -l)"
cat VALIDATION_STATUS.md | head -12
echo "============================================================"
