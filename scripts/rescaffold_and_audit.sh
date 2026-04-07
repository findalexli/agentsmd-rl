#!/usr/bin/env bash
# Re-scaffold critical tasks + auto-fix moderate issues.
# Higher budgets ($15/task), longer timeouts (45 min).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .env 2>/dev/null || true

LOG="pipeline_logs/rescaffold_$(date +%Y%m%d_%H%M).log"
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

# ── Phase 1: Delete broken template dirs, re-scaffold ───────
phase1_rescaffold() {
    local input="$1" workers="${2:-4}" budget="${3:-15.0}" timeout="${4:-2700}"
    local count
    count=$(wc -l < "$input")
    log "Phase 1: Re-scaffold $count critical tasks (budget=\$$budget, timeout=${timeout}s)"

    # Delete existing broken dirs so pipeline re-creates them
    .venv/bin/python3 -c "
import json, shutil, os
with open('$input') as f:
    for line in f:
        item = json.loads(line)
        task_dir = f'harbor_tasks_agentmd_edits/{item[\"task_dir\"]}'
        if os.path.exists(task_dir):
            shutil.rmtree(task_dir)
            print(f'  Removed: {task_dir}')
" 2>&1 | tee -a "$LOG"

    # Try GLM first, then OAuth
    setup_glm
    if test_auth; then
        log "Using GLM-5.1"
        .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
            --input "$input" --agentmd --workers "$workers" \
            --model opus --budget "$budget" --timeout "$timeout" \
            2>&1 | tee -a "$LOG" || true
    else
        log "GLM unavailable, trying OAuth"
        setup_oauth
        if test_auth; then
            log "Using Claude OAuth"
            .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                --input "$input" --agentmd --workers "$workers" \
                --model opus --budget "$budget" --timeout "$timeout" \
                2>&1 | tee -a "$LOG" || true
        else
            log "OAuth unavailable, trying API key"
            unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_DEFAULT_OPUS_MODEL \
                  ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL API_TIMEOUT_MS \
                  CLAUDE_ACCESS_TOKEN 2>/dev/null || true
            source .env 2>/dev/null || true
            export ANTHROPIC_API_KEY
            .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
                --input "$input" --agentmd --workers "$workers" \
                --model opus --budget "$budget" --timeout "$timeout" \
                2>&1 | tee -a "$LOG" || true
        fi
    fi
}

# ── Phase 2: Auto-fix moderate issues ───────────────────────
phase2_autofix() {
    log "Phase 2: Auto-fix moderate issues"

    .venv/bin/python3 << 'PYEOF'
import os, re, yaml, json
from pathlib import Path

td = 'harbor_tasks_agentmd_edits'
fixed_origins = 0
fixed_manifests = 0

for d in sorted(os.listdir(td)):
    dp = Path(td) / d
    if not dp.is_dir(): continue

    # Fix 1: Invalid origins in eval_manifest.yaml
    mf = dp / 'eval_manifest.yaml'
    if mf.exists():
        text = mf.read_text()
        new_text = text
        for invalid in ['config_edit', 'code_change', 'documentation']:
            new_text = new_text.replace(f'origin: {invalid}', 'origin: pr_diff')
        if new_text != text:
            mf.write_text(new_text)
            fixed_origins += 1

    # Fix 2: Manifest-test sync (add missing check IDs from test funcs)
    tp = dp / 'tests' / 'test_outputs.py'
    if tp.exists() and mf.exists():
        test_content = tp.read_text()
        manifest_content = mf.read_text()

        test_funcs = re.findall(r'^def (test_\w+)', test_content, re.MULTILINE)
        check_ids = re.findall(r'^\s+- id:\s*(\S+)', manifest_content, re.MULTILINE)

        # Only fix if we have test funcs but fewer check IDs
        if len(test_funcs) > len(check_ids) and len(check_ids) > 0:
            missing = [f for f in test_funcs if f not in check_ids]
            if missing and len(missing) <= 3:
                # Append missing checks
                for func_name in missing:
                    entry = f"\n  - id: {func_name}\n    type: fail_to_pass\n    origin: pr_diff\n    description: Auto-added from test function"
                    manifest_content = manifest_content.rstrip() + entry + "\n"
                mf.write_text(manifest_content)
                fixed_manifests += 1

print(f'Fixed invalid origins: {fixed_origins}')
print(f'Fixed manifest sync: {fixed_manifests}')
PYEOF
}

# ── Phase 3: Summary ────────────────────────────────────────
phase3_summary() {
    log "Phase 3: Final audit"

    .venv/bin/python3 << 'PYEOF'
import os, re, ast, json
from pathlib import Path
from collections import Counter

td = 'harbor_tasks_agentmd_edits'
total = clean = stub = template = syntax = orphan = no_sub = 0

for d in sorted(os.listdir(td)):
    dp = Path(td) / d
    if not dp.is_dir(): continue
    total += 1

    tp = dp / 'tests' / 'test_outputs.py'
    if not tp.exists(): continue

    content = tp.read_text()
    has_issue = False

    if 'NotImplementedError' in content:
        stub += 1; has_issue = True
    if '{{' in content:
        template += 1; has_issue = True
    try:
        ast.parse(content)
    except SyntaxError:
        syntax += 1; has_issue = True
    if 'subprocess.run' not in content and 'subprocess.check' not in content:
        no_sub += 1

    # Orphaned asserts
    for i, line in enumerate(content.splitlines()):
        if line.strip().startswith('assert ') and i > 5:
            leading = len(line) - len(line.lstrip())
            if leading == 0:
                orphan += 1; has_issue = True
                break

    if not has_issue:
        clean += 1

print()
print('━' * 50)
print('  QUALITY AUDIT RESULTS')
print('━' * 50)
print(f'  Total tasks:     {total}')
print(f'  Clean:           {clean}')
print(f'  Stubs:           {stub}')
print(f'  Templates:       {template}')
print(f'  Syntax errors:   {syntax}')
print(f'  Orphaned asserts:{orphan}')
print(f'  No subprocess:   {no_sub} (may be OK for Python repos)')
print('━' * 50)
PYEOF
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

log "=== Re-scaffold & Audit Pipeline ==="

# Phase 1: Re-scaffold critical tasks
if [ -f "rescaffold_critical.jsonl" ]; then
    phase1_rescaffold "rescaffold_critical.jsonl" 4 15.0 2700
fi

# Phase 2: Auto-fix moderate issues
phase2_autofix

# Phase 3: Summary
phase3_summary

log "=== Pipeline complete ==="
