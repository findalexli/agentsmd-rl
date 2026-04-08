#!/usr/bin/env bash
# Overnight GLM pipeline: improve weak tests, scout new PRs, scaffold new tasks.
# All work via GLM-5.1 (free). Opus audit pass deferred to morning.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .env 2>/dev/null || true

LOG="pipeline_logs/overnight_glm_$(date +%Y%m%d_%H%M).log"
mkdir -p pipeline_logs

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# ── GLM auth ────────────────────────────────────────────────
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

setup_glm

# ── Phase 1: Finish improving harbor_tasks WEAK tests ───────
phase1_improve_remaining() {
    log "═══ Phase 1: Improve remaining WEAK harbor_tasks tests ═══"

    # Find tasks still WEAK
    .venv/bin/python -c "
import ast, os, re

STDLIB = {'ast', 're', 'os', 'sys', 'json', 'pathlib', 'textwrap', 'subprocess',
          'importlib', 'tempfile', 'shutil', 'glob', 'unittest', 'collections',
          'io', 'functools', 'itertools', 'typing', 'contextlib', 'copy',
          'difflib', 'hashlib', 'math', 'string', 'time', 'datetime',
          'py_compile', 'xml', 'yaml', 'toml', 'tomllib', 'configparser'}

weak = []
for t in sorted(os.listdir('harbor_tasks')):
    tp = f'harbor_tasks/{t}/tests/test_outputs.py'
    if not os.path.isdir(f'harbor_tasks/{t}'): continue
    if not os.path.exists(tp): continue
    content = open(tp).read()
    try: ast.parse(content)
    except: continue
    if 'NotImplementedError' in content or '{{' in content: continue
    has_sub = bool(re.search(r'subprocess\.run|subprocess\.check_|_run_ts|_run\(', content))
    has_beh = bool(re.search(r'assert.*returncode|assert.*stdout|assert.*stderr|\.returncode\s*==|result\.stdout', content))
    has_real = False
    for line in content.splitlines():
        m = re.match(r'from\s+(\w+)', line.strip())
        if m and m.group(1) not in STDLIB: has_real = True; break
    if not (has_sub and has_beh) and not (has_sub or has_real or 'json.loads' in content):
        weak.append(t)

with open('/tmp/phase1_weak.txt', 'w') as f:
    f.write('\n'.join(weak))
print(len(weak))
" 2>&1
    local count
    count=$(wc -l < /tmp/phase1_weak.txt)

    if [ "$count" -gt 0 ]; then
        log "  Found $count WEAK tasks to improve"
        TASKS=$(paste -sd, /tmp/phase1_weak.txt)
        .venv/bin/python -m taskforge.pipeline improve-tests \
            --task-dir harbor_tasks \
            --tasks "$TASKS" --workers 6 --budget 10.0 --timeout 1800 \
            2>&1 | tee -a "$LOG" || true
    else
        log "  No WEAK tasks remaining — skipping"
    fi
}

# ── Phase 2: Scout new PRs focused on skills + meaningful changes ────
phase2_scout() {
    log "═══ Phase 2: Scout new PRs (skills + meaningful code changes) ═══"

    # Scout repos known to have rich skill/config files
    .venv/bin/python -c "
import json, subprocess, sys, re
sys.path.insert(0, '.')
from taskforge.config import gh_json, is_agent_instruction_file, is_code_file

# Repos with known .claude/skills/ or .claude/rules/ or .agents/skills/
SKILL_REPOS = [
    ('facebook/react', 40),
    ('microsoft/playwright', 30),
    ('sgl-project/sglang', 30),
    ('oven-sh/bun', 40),
    ('pytorch/pytorch', 25),
    ('huggingface/transformers', 30),
    ('supabase/supabase', 30),
    ('PostHog/posthog', 25),
    ('THUDM/slime', 20),
    ('inclusionAI/AReaL', 25),
    ('apache/beam', 20),
    ('vercel/next.js', 30),
    ('astral-sh/ruff', 25),
    ('astral-sh/uv', 25),
    ('gradio-app/gradio', 30),
    ('anomalyco/opencode', 30),
    ('PrimeIntellect-ai/prime-rl', 20),
    ('vllm-project/vllm', 30),
    # New repos to explore for skill files
    ('anthropics/claude-code', 20),
    ('lobehub/lobe-chat', 20),
    ('microsoft/TypeScript', 15),
    ('denoland/deno', 20),
    ('cloudflare/workers-sdk', 20),
    ('sveltejs/svelte', 20),
    ('remix-run/remix', 25),
    ('electric-sql/electric', 15),
    ('payloadcms/payload', 15),
    ('triggerdotdev/trigger.dev', 15),
]

# Load existing PRs to dedup
from taskforge.scout import get_existing_prs
from pathlib import Path
existing = get_existing_prs(Path('harbor_tasks'), Path('harbor_tasks_agentmd_edits'))
print(f'Existing PRs to dedup: {len(existing)}')

all_candidates = []
for repo, fetch_limit in SKILL_REPOS:
    print(f'\\nScouting {repo} (limit {fetch_limit})...')
    try:
        prs = gh_json([
            'pr', 'list', '--repo', repo, '--state', 'merged',
            '--limit', str(fetch_limit),
            '--json', 'number,title,files,changedFiles,additions,deletions,mergedAt,labels,mergeCommit',
        ], retries=2)
    except Exception as e:
        print(f'  Error: {e}')
        continue

    if not prs:
        print(f'  No PRs found')
        continue

    found = 0
    for pr in prs:
        pr_num = pr.get('number', 0)
        if (repo, pr_num) in existing: continue

        changed_files = pr.get('changedFiles', 0)
        additions = pr.get('additions', 0)
        deletions = pr.get('deletions', 0)
        total = additions + deletions

        # Size filters
        if changed_files < 2 or changed_files > 15: continue
        if total < 10 or total > 800: continue

        # Skip bot/dep labels
        labels = {l.get('name','').lower() for l in pr.get('labels', [])}
        skip_labels = {'dependencies','documentation','docs','release','ci','chore','bot','automated','renovate','dependabot'}
        if labels & skip_labels: continue

        files = pr.get('files', [])
        file_paths = [f.get('path', '') for f in files] if files else []

        # Must have at least one agent instruction file (Tier 1)
        instruction_files = [f for f in file_paths if is_agent_instruction_file(f)]
        code_files = [f for f in file_paths if is_code_file(f)]

        if not instruction_files or not code_files: continue

        # Prioritize PRs touching skills
        has_skill = any('skill' in f.lower() or 'SKILL.md' in f for f in instruction_files)
        has_rules = any('rules/' in f for f in instruction_files)

        merge_commit = pr.get('mergeCommit', {})
        merge_sha = merge_commit.get('oid', '') if isinstance(merge_commit, dict) else ''

        all_candidates.append({
            'repo': repo,
            'pr_number': pr_num,
            'title': pr.get('title', ''),
            'changed_files': changed_files,
            'additions': additions,
            'deletions': deletions,
            'merged_at': pr.get('mergedAt', ''),
            'merge_sha': merge_sha,
            'file_paths': file_paths[:15],
            'config_files': instruction_files,
            'has_skill': has_skill,
            'has_rules': has_rules,
            'has_tier1': True,
            'priority': 2 if has_skill else (1 if has_rules else 0),
        })
        found += 1

    print(f'  Found {found} candidates with Tier 1 config + code')

# Sort: skill PRs first, then rules, then other Tier 1
all_candidates.sort(key=lambda c: (-c['priority'], c['repo'], c['pr_number']))

# Write output
output = 'scouted_overnight_20260408.jsonl'
with open(output, 'w') as f:
    for c in all_candidates:
        f.write(json.dumps(c) + '\\n')

print(f'\\nTotal candidates: {len(all_candidates)}')
print(f'  With skills: {sum(1 for c in all_candidates if c[\"has_skill\"])}')
print(f'  With rules: {sum(1 for c in all_candidates if c[\"has_rules\"])}')
print(f'  Other Tier 1: {sum(1 for c in all_candidates if not c[\"has_skill\"] and not c[\"has_rules\"])}')
print(f'Written to {output}')
" 2>&1 | tee -a "$LOG"
}

# ── Phase 3: Scaffold new agentmd tasks from scouted PRs ────
phase3_scaffold() {
    log "═══ Phase 3: Scaffold new agentmd_edits tasks from scouted PRs ═══"

    local input_file
    input_file=$(ls -t scouted_overnight_*.jsonl 2>/dev/null | head -1)

    if [ -z "$input_file" ] || [ ! -f "$input_file" ]; then
        log "  No scouted PRs file found — skipping scaffold"
        return
    fi

    local count
    count=$(wc -l < "$input_file")
    log "  Input: $input_file ($count PRs)"

    if [ "$count" -eq 0 ]; then
        log "  No PRs to scaffold"
        return
    fi

    .venv/bin/python -m taskforge.pipeline scaffold-from-prs \
        --input "$input_file" --agentmd \
        --workers 6 --budget 8.0 --timeout 1800 \
        2>&1 | tee -a "$LOG" || true
}

# ── Phase 4: Fix origins in newly scaffolded tasks ──────────
phase4_fix_origins() {
    log "═══ Phase 4: Fix invalid origins in new tasks ═══"
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

# ── Phase 5: Final audit ────────────────────────────────────
phase5_audit() {
    log "═══ Phase 5: Final audit ═══"
    .venv/bin/python -c "
import ast, os, re

STDLIB = {'ast', 're', 'os', 'sys', 'json', 'pathlib', 'textwrap', 'subprocess',
          'importlib', 'tempfile', 'shutil', 'glob', 'unittest', 'collections',
          'io', 'functools', 'itertools', 'typing', 'contextlib', 'copy',
          'difflib', 'hashlib', 'math', 'string', 'time', 'datetime',
          'py_compile', 'xml', 'yaml', 'toml', 'tomllib', 'configparser'}

for td in ['harbor_tasks', 'harbor_tasks_agentmd_edits']:
    good = ok = weak = broken = 0
    for t in sorted(os.listdir(td)):
        tp = os.path.join(td, t, 'tests', 'test_outputs.py')
        if not os.path.isdir(os.path.join(td, t)): continue
        if not os.path.exists(tp): broken += 1; continue
        content = open(tp).read()
        try: ast.parse(content)
        except: broken += 1; continue
        if 'NotImplementedError' in content or '{{' in content: broken += 1; continue
        has_sub = bool(re.search(r'subprocess\.run|subprocess\.check_|_run_ts|_run\(', content))
        has_beh = bool(re.search(r'assert.*returncode|assert.*stdout|assert.*stderr|\.returncode\s*==|result\.stdout', content))
        has_real = False
        for line in content.splitlines():
            m = re.match(r'from\s+(\w+)', line.strip())
            if m and m.group(1) not in STDLIB: has_real = True; break
        if has_sub and has_beh: good += 1
        elif has_sub or has_real or 'json.loads' in content: ok += 1
        else: weak += 1
    total = good + ok + weak + broken
    print(f'{td}: {total} total | GOOD={good} ({100*good//total}%) OK={ok} WEAK={weak} BROKEN={broken}')
" 2>&1 | tee -a "$LOG"
}

# ═══════════════════════════════════════════════════════════════
# MAIN — run all phases sequentially
# ═══════════════════════════════════════════════════════════════

log "╔══════════════════════════════════════════╗"
log "║  Overnight GLM Pipeline — $(date +%Y-%m-%d)  ║"
log "╚══════════════════════════════════════════╝"
log "Using GLM-5.1 via Z.AI (free tier)"
log ""

phase1_improve_remaining
phase2_scout
phase3_scaffold
phase4_fix_origins
phase5_audit

log ""
log "╔══════════════════════════════════════════╗"
log "║  Pipeline complete — $(date)  ║"
log "╚══════════════════════════════════════════╝"
log "Next: use Opus to audit GLM's work"
