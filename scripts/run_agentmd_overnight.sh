#!/usr/bin/env bash
# Overnight pipeline for harbor_tasks_agentmd_edits collection.
#
# Auth fallback chain:
#   1. GLM-5.1 via Z.AI (ANTHROPIC_BASE_URL → api.z.ai, cheapest)
#   2. Claude via OAuth backup token (~/.claude/.credentials_backup.json)
#   3. Claude via ANTHROPIC_API_KEY from .env (direct Anthropic, most expensive)
#
# Skips Phase 1-2 (scout/filter) if scouted_agentmd_prs_deep_filtered.jsonl exists.
#
# Phases:
#   1. Scout PRs that touch both code + agent config files
#   2. Quality filter: remove low-signal PRs programmatically
#   3. Batch scaffold tasks (4 workers)
#   4. Docker validate all tasks (nop=0, gold=1)
#   5. Retry failed scaffolds with increased budget
#   6. Final validation + summary
#
# Usage:
#   ./scripts/run_agentmd_overnight.sh              # full pipeline
#   ./scripts/run_agentmd_overnight.sh --phase 3    # start from phase 3
#   N_WORKERS=2 ./scripts/run_agentmd_overnight.sh  # fewer workers

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source .env 2>/dev/null || true

LOG_FILE="pipeline_logs/agentmd_overnight_$(date +%Y%m%d_%H%M%S).log"
mkdir -p pipeline_logs

log() {
    echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"
}

# ── Auth fallback chain ───────────────────────────────────────
AUTH_METHOD=""

try_glm() {
    log "Trying auth method 1: GLM-5.1 via Z.AI..."
    if [ -z "${GLM_API_KEY:-}" ]; then
        log "  GLM_API_KEY not set, skipping"
        return 1
    fi
    local code
    code=$(curl -s -w "%{http_code}" -o /dev/null -X POST "https://api.z.ai/api/anthropic/v1/messages" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $GLM_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d '{"model":"glm-5.1","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}')
    if [ "$code" = "200" ]; then
        export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
        export ANTHROPIC_AUTH_TOKEN="$GLM_API_KEY"
        export ANTHROPIC_API_KEY="$GLM_API_KEY"
        export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5.1"
        export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5.1"
        export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
        export API_TIMEOUT_MS="3000000"
        AUTH_METHOD="glm-5.1"
        log "  GLM-5.1: OK (HTTP 200)"
        return 0
    else
        log "  GLM-5.1: FAILED (HTTP $code)"
        return 1
    fi
}

try_oauth_backup() {
    log "Trying auth method 2: Claude OAuth backup token..."
    local creds_file="$HOME/.claude/.credentials_backup.json"
    if [ ! -f "$creds_file" ]; then
        log "  No backup credentials at $creds_file, skipping"
        return 1
    fi
    local token
    token=$(.venv/bin/python -c "import json; print(json.load(open('$creds_file'))['claudeAiOauth']['accessToken'])")
    if [ -z "$token" ]; then
        log "  Could not extract accessToken, skipping"
        return 1
    fi
    # Test it
    local result
    result=$(echo "hi" | timeout 30 bash -c "export CLAUDE_ACCESS_TOKEN='$token'; claude -p --model sonnet --max-budget-usd 0.05" 2>&1) || true
    if [ -n "$result" ]; then
        export CLAUDE_ACCESS_TOKEN="$token"
        # Unset any Z.AI overrides
        unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
              ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS 2>/dev/null || true
        AUTH_METHOD="oauth-backup"
        log "  OAuth backup: OK"
        return 0
    else
        log "  OAuth backup: FAILED"
        return 1
    fi
}

try_api_key() {
    log "Trying auth method 3: Anthropic API key from .env..."
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        log "  ANTHROPIC_API_KEY not set, skipping"
        return 1
    fi
    local result
    result=$(echo "hi" | timeout 30 bash -c "export ANTHROPIC_API_KEY='${ANTHROPIC_API_KEY}'; claude -p --model sonnet --max-budget-usd 0.05" 2>&1) || true
    if [ -n "$result" ]; then
        export ANTHROPIC_API_KEY
        # Unset any Z.AI overrides
        unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
              ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS CLAUDE_ACCESS_TOKEN 2>/dev/null || true
        AUTH_METHOD="anthropic-api-key"
        log "  Anthropic API key: OK"
        return 0
    else
        log "  Anthropic API key: FAILED"
        return 1
    fi
}

try_glm || try_oauth_backup || try_api_key || {
    log "ERROR: All 3 auth methods failed. Cannot proceed."
    exit 1
}

log ""
log "━━━ Auth: $AUTH_METHOD ━━━"

# ── Config ─────────────────────────────────────────────────────
TASK_DIR="harbor_tasks_agentmd_edits"
SCOUT_OUTPUT="scouted_agentmd_prs.jsonl"
FILTERED_OUTPUT="scouted_agentmd_prs_filtered.jsonl"
WORKERS=${N_WORKERS:-4}
SCAFFOLD_BUDGET=${SCAFFOLD_BUDGET:-6.0}
SCAFFOLD_TIMEOUT=${SCAFFOLD_TIMEOUT:-1800}

mkdir -p "$TASK_DIR"

# Parse args
START_PHASE=${1:-1}
if [[ "$START_PHASE" == "--phase" ]]; then
    START_PHASE=${2:-1}
fi

# If we have the deep-filtered file, use it as default input
if [ -f "scouted_agentmd_prs_deep_filtered.jsonl" ]; then
    FILTERED_OUTPUT="scouted_agentmd_prs_deep_filtered.jsonl"
    if [ "$START_PHASE" -le 2 ]; then
        log "Found scouted_agentmd_prs_deep_filtered.jsonl ($(wc -l < scouted_agentmd_prs_deep_filtered.jsonl) PRs)"
        log "Skipping Phase 1-2 (scout/filter) — using existing data"
        START_PHASE=3
    fi
fi

log "=== AgentMD Overnight Pipeline ==="
log "Auth: $AUTH_METHOD"
log "Start phase: $START_PHASE"
log "Task dir: $TASK_DIR"
log "Workers: $WORKERS | Budget: \$$SCAFFOLD_BUDGET/task | Timeout: ${SCAFFOLD_TIMEOUT}s"
log "Log: $LOG_FILE"

# ─────────────────────────────────────────────────────────────────
# Phase 1: Scout PRs
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 1 ]; then
    log ""
    log "━━━ PHASE 1: Scout PRs ━━━"
    log "Target: PRs that touch both code + agent config files"

    .venv/bin/python -m taskforge.scout scout --agentmd \
        --repos-file scouted_repos.jsonl \
        --limit 15 \
        --months 4 \
        --output "$SCOUT_OUTPUT" \
        2>&1 | tee -a "$LOG_FILE"

    SCOUTED_COUNT=$(wc -l < "$SCOUT_OUTPUT")
    log "Scouted: $SCOUTED_COUNT PRs"

    if [ "$SCOUTED_COUNT" -lt 200 ]; then
        log "Low count, retrying with --limit 25..."
        .venv/bin/python -m taskforge.scout scout --agentmd \
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

    .venv/bin/python -m taskforge.scout filter --agentmd \
        --input "$SCOUT_OUTPUT" \
        --output "$FILTERED_OUTPUT" \
        2>&1 | tee -a "$LOG_FILE"

    FILTERED_COUNT=$(wc -l < "$FILTERED_OUTPUT")
    log "After filter: $FILTERED_COUNT PRs (from $(wc -l < "$SCOUT_OUTPUT") scouted)"
fi

# ─────────────────────────────────────────────────────────────────
# Phase 3: Batch scaffold
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 3 ]; then
    log ""
    log "━━━ PHASE 3: Batch scaffold ($AUTH_METHOD) ━━━"

    INPUT_FILE="$FILTERED_OUTPUT"
    if [ ! -f "$INPUT_FILE" ]; then
        INPUT_FILE="$SCOUT_OUTPUT"
        log "No filtered file, using raw scouted PRs"
    fi
    if [ ! -f "$INPUT_FILE" ]; then
        log "ERROR: No input file found. Run from phase 1 or provide scouted PRs."
        exit 1
    fi

    TASK_COUNT=$(wc -l < "$INPUT_FILE")
    log "Scaffolding $TASK_COUNT tasks ($AUTH_METHOD, \$$SCAFFOLD_BUDGET/task, $WORKERS workers, ${SCAFFOLD_TIMEOUT}s timeout)"

    .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
        --input "$INPUT_FILE" \
        --agentmd \
        --workers "$WORKERS" \
        --model opus \
        --budget "$SCAFFOLD_BUDGET" \
        --timeout "$SCAFFOLD_TIMEOUT" \
        2>&1 | tee -a "$LOG_FILE"

    SCAFFOLDED=$(find "$TASK_DIR" -name "test_outputs.py" | wc -l)
    log "Scaffolded: $SCAFFOLDED tasks with test_outputs.py"

    # Fix known issue: models may invent invalid origin values (e.g. "config_edit")
    # Safe default: pr_diff (the config update is part of the PR change)
    .venv/bin/python -c "
import os
task_dir = '$TASK_DIR'
VALID = {'pr_diff', 'repo_tests', 'agent_config', 'static'}
fixed = 0
for t in os.listdir(task_dir):
    manifest = f'{task_dir}/{t}/eval_manifest.yaml'
    if not os.path.exists(manifest): continue
    text = open(manifest).read()
    new_text = text
    for invalid in ['config_edit', 'code_change', 'documentation']:
        new_text = new_text.replace(f'origin: {invalid}', 'origin: pr_diff')
    if new_text != text:
        open(manifest, 'w').write(new_text)
        fixed += 1
if fixed:
    print(f'Fixed invalid origin values -> pr_diff in {fixed} eval_manifest.yaml files')
" 2>&1 | tee -a "$LOG_FILE"

    # Stamp scaffold_model into task.toml for all newly scaffolded tasks
    .venv/bin/python -c "
import os, tomllib
task_dir = '$TASK_DIR'
model = '$AUTH_METHOD'
for t in os.listdir(task_dir):
    toml_path = f'{task_dir}/{t}/task.toml'
    if not os.path.exists(toml_path): continue
    text = open(toml_path).read()
    if 'scaffold_model' in text: continue
    # Append to [metadata] section or end of file
    if '[metadata]' in text:
        text = text.replace('[metadata]', '[metadata]\nscaffold_model = \"$AUTH_METHOD\"', 1)
    else:
        text += '\n[metadata]\nscaffold_model = \"$AUTH_METHOD\"\n'
    open(toml_path, 'w').write(text)
print(f'Stamped scaffold_model={model} into new task.toml files')
" 2>&1 | tee -a "$LOG_FILE"

    # ── Check for mass failures → fallback to next auth method ──
    LATEST_LOG=$(ls -td pipeline_logs/scaffold_agentmd_* 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        STATS=$(.venv/bin/python -c "
import json, glob
ok = err = 0
for f in glob.glob('$LATEST_LOG/*.json'):
    if f.endswith('_summary.json'): continue
    try:
        s = json.load(open(f)).get('status','')
        if s == 'success': ok += 1
        else: err += 1
    except: err += 1
print(f'{ok} {err}')
")
        OK_COUNT=$(echo "$STATS" | cut -d' ' -f1)
        ERR_COUNT=$(echo "$STATS" | cut -d' ' -f2)
        TOTAL_TRIED=$((OK_COUNT + ERR_COUNT))
        log "Phase 3 results: $OK_COUNT success, $ERR_COUNT failed (out of $TOTAL_TRIED)"

        # If >80% failed and we were on GLM, try fallback
        if [ "$TOTAL_TRIED" -gt 5 ] && [ "$ERR_COUNT" -gt $((TOTAL_TRIED * 4 / 5)) ] && [ "$AUTH_METHOD" = "glm-5.1" ]; then
            log ""
            log "⚠ GLM-5.1 had >80% failure rate. Attempting fallback..."
            if try_oauth_backup || try_api_key; then
                log "Switched to $AUTH_METHOD — re-running Phase 3"
                .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                    --input "$INPUT_FILE" \
                    --agentmd \
                    --workers "$WORKERS" \
                    --model opus \
                    --budget "$SCAFFOLD_BUDGET" \
                    --timeout "$SCAFFOLD_TIMEOUT" \
                    2>&1 | tee -a "$LOG_FILE"
                SCAFFOLDED=$(find "$TASK_DIR" -name "test_outputs.py" | wc -l)
                log "Scaffolded (after fallback): $SCAFFOLDED tasks with test_outputs.py"
            fi
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Phase 4: Docker validation (nop=0, gold=1)
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 4 ]; then
    log ""
    log "━━━ PHASE 4: Docker validation ━━━"

    # Find newly scaffolded tasks (have test_outputs.py but no status.json with 'pass')
    NEW_TASKS=$(.venv/bin/python -c "
import json, os
task_dir = '$TASK_DIR'
new = []
for t in sorted(os.listdir(task_dir)):
    td = f'{task_dir}/{t}'
    if not os.path.exists(f'{td}/tests/test.sh'): continue
    sf = f'{td}/status.json'
    already_valid = False
    if os.path.exists(sf):
        data = json.load(open(sf))
        already_valid = any(v.get('verdict') == 'pass' for v in data.get('validations', []))
    if not already_valid:
        new.append(t)
print(','.join(new))
")

    if [ -n "$NEW_TASKS" ]; then
        NEW_COUNT=$(echo "$NEW_TASKS" | tr ',' '\n' | wc -l)
        log "Validating $NEW_COUNT new/unvalidated tasks..."

        # Unset LLM env vars — validation is Docker-only
        (
            unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
                  ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS \
                  CLAUDE_ACCESS_TOKEN 2>/dev/null || true

            .venv/bin/python -m taskforge.pipeline validate \
                --task-dir "$TASK_DIR" \
                --tasks "$NEW_TASKS" \
                --workers 4 \
                --timeout 300 \
                2>&1 | tee -a "$LOG_FILE"
        ) || log "  (some validation failures, continuing)"
    else
        log "No new tasks to validate"
    fi

    # Count results
    VALID=$(.venv/bin/python -c "
import json, os
valid = total = 0
for t in os.listdir('$TASK_DIR'):
    sf = f'$TASK_DIR/{t}/status.json'
    if not os.path.exists(sf): continue
    total += 1
    data = json.load(open(sf))
    if any(v.get('verdict') == 'pass' for v in data.get('validations', [])):
        valid += 1
print(f'{valid}/{total}')
")
    log "Validation results: $VALID valid"
fi

# ─────────────────────────────────────────────────────────────────
# Phase 5: Retry failed scaffolds with higher budget
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 5 ]; then
    log ""
    log "━━━ PHASE 5: Retry failed scaffolds ━━━"

    LATEST_LOG=$(ls -td pipeline_logs/scaffold_agentmd_* 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        RETRY_TASKS=$(.venv/bin/python -c "
import json, glob
retry = []
for f in glob.glob('$LATEST_LOG/*.json'):
    if f.endswith('_summary.json'): continue
    try:
        data = json.load(open(f))
        if data.get('status') in ('timeout', 'error', 'budget_exceeded'):
            retry.append(data.get('task', ''))
    except: pass
print(','.join(t for t in retry if t))
")

        if [ -n "$RETRY_TASKS" ]; then
            RETRY_COUNT=$(echo "$RETRY_TASKS" | tr ',' '\n' | wc -l)
            log "Retrying $RETRY_COUNT failed tasks with \$8 budget, 1200s timeout"

            .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                --input "${INPUT_FILE:-$FILTERED_OUTPUT}" \
                --agentmd \
                --workers 3 \
                --model opus \
                --budget 8.0 \
                --timeout 1200 \
                2>&1 | tee -a "$LOG_FILE" || log "  (some retry failures)"
        else
            log "No failed tasks to retry"
        fi
    else
        log "No scaffold log dir found, skipping retries"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Phase 6: Final validation + summary
# ─────────────────────────────────────────────────────────────────
if [ "$START_PHASE" -le 6 ]; then
    log ""
    log "━━━ PHASE 6: Final validation + summary ━━━"

    # Re-validate anything that still lacks a pass verdict
    REVALIDATE=$(.venv/bin/python -c "
import json, os
task_dir = '$TASK_DIR'
need = []
for t in sorted(os.listdir(task_dir)):
    td = f'{task_dir}/{t}'
    if not os.path.exists(f'{td}/tests/test.sh'): continue
    sf = f'{td}/status.json'
    already = False
    if os.path.exists(sf):
        data = json.load(open(sf))
        already = any(v.get('verdict') == 'pass' for v in data.get('validations', []))
    if not already:
        need.append(t)
print(','.join(need))
")

    if [ -n "$REVALIDATE" ]; then
        REVAL_COUNT=$(echo "$REVALIDATE" | tr ',' '\n' | wc -l)
        log "Re-validating $REVAL_COUNT tasks..."
        (
            unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
                  ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS \
                  CLAUDE_ACCESS_TOKEN 2>/dev/null || true

            .venv/bin/python -m taskforge.pipeline validate \
                --task-dir "$TASK_DIR" \
                --tasks "$REVALIDATE" \
                --workers 4 \
                --timeout 300 \
                2>&1 | tee -a "$LOG_FILE"
        ) || true
    fi

    # Final summary
    .venv/bin/python -c "
import json, os
task_dir = '$TASK_DIR'
total = valid = failed_build = failed_nop = failed_gold = no_status = 0
for t in sorted(os.listdir(task_dir)):
    sf = f'{task_dir}/{t}/status.json'
    if not os.path.exists(sf):
        no_status += 1
        continue
    total += 1
    data = json.load(open(sf))
    vals = data.get('validations', [])
    if any(v.get('verdict') == 'pass' for v in vals):
        valid += 1
    elif any('build' in v.get('verdict', '') for v in vals):
        failed_build += 1
    elif any('nop' in v.get('verdict', '') for v in vals):
        failed_nop += 1
    elif any('gold' in v.get('verdict', '') for v in vals):
        failed_gold += 1

print()
print('━' * 50)
print('  AGENTMD OVERNIGHT RESULTS')
print('━' * 50)
print(f'  Auth method:  $AUTH_METHOD')
print(f'  Valid:        {valid}/{total} ({100*valid//max(total,1)}%)')
print(f'  Failed build: {failed_build}')
print(f'  Failed nop:   {failed_nop}')
print(f'  Failed gold:  {failed_gold}')
print(f'  No status:    {no_status}')
print('━' * 50)
" | tee -a "$LOG_FILE"
fi

log ""
log "=== Pipeline complete ==="
