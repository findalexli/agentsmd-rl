#!/usr/bin/env bash
# Scaffold all TODO PRs + fix existing broken tasks.
# Uses GLM first (free), falls back to OAuth when rate-limited.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .env 2>/dev/null || true

LOG="pipeline_logs/scaffold_all_$(date +%Y%m%d_%H%M).log"
mkdir -p pipeline_logs

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# ── Auth helpers ─────────────────────────────────────────────
setup_glm() {
    export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
    export ANTHROPIC_AUTH_TOKEN="$GLM_API_KEY"
    export ANTHROPIC_API_KEY="$GLM_API_KEY"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5.1"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5.1"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
    export API_TIMEOUT_MS="3000000"
    unset CLAUDE_ACCESS_TOKEN 2>/dev/null || true
}

setup_oauth() {
    local token
    token=$(.venv/bin/python -c "import json; print(json.load(open('$HOME/.claude/.credentials_backup.json'))['claudeAiOauth']['accessToken'])")
    export CLAUDE_ACCESS_TOKEN="$token"
    unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
          ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS 2>/dev/null || true
}

test_auth() {
    local result
    result=$(echo "hi" | timeout 30 claude -p --model opus --max-budget-usd 0.10 2>&1) || true
    [ -n "$result" ] && ! echo "$result" | grep -q "429\|rate.*limit\|Usage limit"
}

# ── Run a scaffold batch with auto-retry on rate limit ───────
run_batch() {
    local input="$1" label="$2" workers="${3:-4}" budget="${4:-8.0}" timeout="${5:-1800}"
    local count
    count=$(wc -l < "$input")
    log "━━━ $label: $count PRs (workers=$workers, budget=\$$budget) ━━━"
    
    # Try GLM first
    setup_glm
    if test_auth; then
        log "Using GLM-5.1"
        .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
            --input "$input" --agentmd --workers "$workers" \
            --model opus --budget "$budget" --timeout "$timeout" \
            2>&1 | tee -a "$LOG" || true
    else
        log "GLM unavailable, skipping to OAuth"
    fi
    
    # Check results, retry failures with OAuth
    local latest
    latest=$(ls -td pipeline_logs/scaffold_agentmd_* 2>/dev/null | head -1)
    local errors
    errors=$(.venv/bin/python -c "
import json, glob
errs = 0
for f in glob.glob('$latest/*.json'):
    if f.endswith('_summary.json'): continue
    try:
        if json.load(open(f)).get('status') in ('error', 'timeout', 'budget_exceeded'):
            errs += 1
    except: pass
print(errs)
" 2>/dev/null)
    
    if [ "${errors:-0}" -gt 5 ]; then
        log "GLM had $errors failures, retrying with OAuth..."
        sleep 60  # brief cooldown
        setup_oauth
        if test_auth; then
            log "Using Claude OAuth"
            .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                --input "$input" --agentmd --workers "$workers" \
                --model opus --budget "$budget" --timeout "$timeout" \
                2>&1 | tee -a "$LOG" || true
        else
            log "OAuth also unavailable — trying Anthropic API key (direct)"
            unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
                  ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS \
                  CLAUDE_ACCESS_TOKEN 2>/dev/null || true
            source .env 2>/dev/null || true
            export ANTHROPIC_API_KEY
            if test_auth; then
                log "Using Anthropic API key"
                .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                    --input "$input" --agentmd --workers "$workers" \
                    --model opus --budget "$budget" --timeout "$timeout" \
                    2>&1 | tee -a "$LOG" || true
            else
                log "All auth exhausted — waiting 1 hour, retrying GLM"
                sleep 3600
                setup_glm
                .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                    --input "$input" --agentmd --workers "$workers" \
                    --model opus --budget "$budget" --timeout "$timeout" \
                    2>&1 | tee -a "$LOG" || true
            fi
        fi
    fi
}

# ── Post-process: fix known GLM issues ───────────────────────
fix_origins() {
    .venv/bin/python -c "
import os
VALID = {'pr_diff', 'repo_tests', 'agent_config', 'static'}
fixed = 0
for t in os.listdir('harbor_tasks_agentmd_edits'):
    manifest = f'harbor_tasks_agentmd_edits/{t}/eval_manifest.yaml'
    if not os.path.exists(manifest): continue
    text = open(manifest).read()
    new_text = text
    for invalid in ['config_edit', 'code_change', 'documentation']:
        new_text = new_text.replace(f'origin: {invalid}', 'origin: pr_diff')
    if new_text != text:
        open(manifest, 'w').write(new_text)
        fixed += 1
if fixed: print(f'Fixed invalid origins in {fixed} manifests')
" 2>&1 | tee -a "$LOG"
}

# ── Summary ──────────────────────────────────────────────────
summary() {
    .venv/bin/python -c "
import json, os
td = 'harbor_tasks_agentmd_edits'
total = valid = fail = no_status = 0
for t in sorted(os.listdir(td)):
    if not os.path.isdir(f'{td}/{t}'): continue
    sf = f'{td}/{t}/status.json'
    if not os.path.exists(sf):
        no_status += 1; continue
    total += 1
    data = json.load(open(sf))
    if any(v.get('verdict') == 'pass' for v in data.get('validations', [])):
        valid += 1
    else:
        fail += 1
print()
print('━' * 50)
print('  SCAFFOLD RESULTS')
print('━' * 50)
print(f'  Valid:     {valid}')
print(f'  Failed:    {fail}')
print(f'  No status: {no_status}')
print(f'  Total:     {valid + fail + no_status}')
print('━' * 50)
" | tee -a "$LOG"
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

log "=== Scaffold All Pipeline ==="
log "Phase A: 131 TODO PRs"
log "Phase B: Fix existing broken tasks"

# Phase A: Scaffold new tasks from TODO
if [ -f "scouted_agentmd_prs_todo.jsonl" ]; then
    run_batch "scouted_agentmd_prs_todo.jsonl" "Phase A: New PRs" 4 8.0 1800
    fix_origins
fi

# Phase B: Identify and re-scaffold broken existing tasks
log ""
log "━━━ Phase B: Fix existing broken tasks ━━━"

# Find tasks with NotImplementedError stubs or orphaned code
.venv/bin/python -c "
import os, re

td = 'harbor_tasks_agentmd_edits'
broken = []
for t in sorted(os.listdir(td)):
    tp = f'{td}/{t}/tests/test_outputs.py'
    mf = f'{td}/{t}/eval_manifest.yaml'
    if not os.path.exists(tp): continue
    content = open(tp).read()
    
    # Check for known issues
    has_stub = 'NotImplementedError' in content
    has_template = '{{' in content
    
    # Check for orphaned code (assertions outside def test_*)
    lines = content.splitlines()
    orphaned = False
    in_function = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('def test_'):
            in_function = True
        elif stripped.startswith('def ') or (stripped and not stripped.startswith('#') and not stripped.startswith('\"\"\"') and line[0:1] not in (' ', '\t', '') and 'import' not in stripped and '=' not in stripped[:20]):
            in_function = False
        if stripped.startswith('assert ') and not in_function and i > 10:
            orphaned = True
            break
    
    if has_stub or has_template or orphaned:
        reasons = []
        if has_stub: reasons.append('stubs')
        if has_template: reasons.append('template')
        if orphaned: reasons.append('orphaned')
        broken.append(f'{t}|{\",\".join(reasons)}')

with open('/tmp/broken_tasks.txt', 'w') as f:
    for b in broken:
        f.write(b + '\n')
print(f'Found {len(broken)} broken tasks')
for b in broken[:10]:
    print(f'  {b}')
if len(broken) > 10:
    print(f'  ... and {len(broken) - 10} more')
" 2>&1 | tee -a "$LOG"

BROKEN_COUNT=$(wc -l < /tmp/broken_tasks.txt 2>/dev/null || echo 0)
if [ "$BROKEN_COUNT" -gt 0 ]; then
    log "Re-scaffolding $BROKEN_COUNT broken tasks with Claude OAuth..."
    # TODO: implement re-scaffold using /scaffold-task on each broken task's PR
    log "(Phase B re-scaffold not yet automated — needs manual review)"
fi

summary
log "=== Pipeline complete ==="
