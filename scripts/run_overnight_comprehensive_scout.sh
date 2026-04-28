#!/bin/bash
# Overnight comprehensive scout: maximize PR recall over the last 8 months.
#
# Plan:
#   1. Wait for any in-flight code-search scout to finish (idempotent if cache exists)
#   2. Re-run code-search scout with EXPANDED query list (cached Phase 1
#      repos are reused; only new queries fire)
#   3. Run date-windowed title scout (all 27 queries, ~280 search calls)
#   4. Merge code-search + title outputs into scout_data/, dedupe by (repo, pr)
#   5. Classify unique repos (GraphQL bundle, ~200 GraphQL calls)
#   6. Hand off to run_wider_after_classify.sh for scaffold + judge + commit
#
# All raw outputs land under scout_data/ (gitignored, persistent across runs)
# so we can re-judge or re-classify without re-fetching.

set -euo pipefail
cd /home/alex/agentsmd-rl

LABEL="${1:-overnight_$(date +%Y%m%d_%H%M)}"
SCOUT_DIR=scout_data
LOG_DIR=pipeline_logs/scaffold_v4_2026_04_26
SINCE="${2:-2025-09-01}"

mkdir -p "$SCOUT_DIR"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

# 1. Wait for any in-flight scout
log "Phase 0: wait for in-flight code-search scout (if any)"
while pgrep -f "discover_via_code_search.py" > /dev/null 2>&1; do
    sleep 30
done
log "  no scout running, proceed"

# 2. Re-run code-search scout with expanded queries (uses cache)
log "Phase 1: code-search scout (expanded queries, cache-resumable)"
.venv/bin/python scripts/discover_via_code_search.py \
    --since "$SINCE" \
    --output "$SCOUT_DIR/code_search_${LABEL}.jsonl" \
    --max-pages 10 \
    --max-prs 100 \
    --concurrency 8 \
    --repos-cache "$SCOUT_DIR/code_search_repos_${LABEL}.txt" \
  > "$LOG_DIR/codesearch_${LABEL}.log" 2>&1 || log "  (code-search exited non-zero, check log)"

CS_COUNT=$(wc -l < "$SCOUT_DIR/code_search_${LABEL}.jsonl" 2>/dev/null || echo 0)
log "  code-search yielded $CS_COUNT PRs"

# 3. Date-windowed title scout
log "Phase 2: date-windowed title scout (28 queries)"
.venv/bin/python scripts/discover_recent_skill_prs.py \
    --since "$SINCE" \
    --min-stars 100 \
    --output "$SCOUT_DIR/title_${LABEL}.jsonl" \
    --max-pages 10 \
  > "$LOG_DIR/title_${LABEL}.log" 2>&1 || log "  (title scout exited non-zero, check log)"

T_COUNT=$(wc -l < "$SCOUT_DIR/title_${LABEL}.jsonl" 2>/dev/null || echo 0)
log "  title scout yielded $T_COUNT PRs"

# 4. Merge + dedupe
log "Phase 3: merge + dedupe"
.venv/bin/python - <<PY
import json
from pathlib import Path
SD = Path("$SCOUT_DIR")
out_path = SD / "merged_${LABEL}.jsonl"
seen = {}
sources = ["code_search_${LABEL}.jsonl", "title_${LABEL}.jsonl"]
for src in sources:
    p = SD / src
    if not p.exists(): continue
    for line in p.open():
        try:
            d = json.loads(line)
        except Exception: continue
        key = (d.get("repo",""), d.get("pr_number") or d.get("pr"))
        if key[0] and key[1] and key not in seen:
            d["_source"] = src.split("_")[0]
            seen[key] = d
        elif key in seen:
            # PR found by both — annotate
            seen[key]["_source"] = "both"
with out_path.open("w") as f:
    for d in seen.values():
        f.write(json.dumps(d) + "\n")
print(f"merged {len(seen)} unique PRs -> {out_path}")
PY

M_COUNT=$(wc -l < "$SCOUT_DIR/merged_${LABEL}.jsonl" 2>/dev/null || echo 0)
log "  merged unique: $M_COUNT PRs"

# 5. Classify unique repos
log "Phase 4: classify unique repos"
jq -r '.repo' "$SCOUT_DIR/merged_${LABEL}.jsonl" | sort -u > "$SCOUT_DIR/repos_${LABEL}.txt"
R_COUNT=$(wc -l < "$SCOUT_DIR/repos_${LABEL}.txt")
log "  classifying $R_COUNT unique repos"
.venv/bin/python scripts/classify_repos_llm.py \
    --repos-file "$SCOUT_DIR/repos_${LABEL}.txt" \
    --output "$SCOUT_DIR/repo_class_${LABEL}.jsonl" \
    --concurrency 16 \
  > "$LOG_DIR/classify_${LABEL}.log" 2>&1

USEFUL=$(jq -r 'select(.is_useful_for_benchmark==true) | .repo' "$SCOUT_DIR/repo_class_${LABEL}.jsonl" | wc -l)
log "  useful_for_benchmark: $USEFUL of $R_COUNT"

# 6. Stage inputs for the scaffold/judge continuation script
log "Phase 5: stage inputs and hand off to scaffold pipeline"
cp "$SCOUT_DIR/merged_${LABEL}.jsonl"   /tmp/recent_skill_prs_wide.jsonl
cp "$SCOUT_DIR/repo_class_${LABEL}.jsonl" /tmp/cross_repo_wide_repo_class.jsonl
log "  staged. running scaffold + post-judge..."
PRE_ACTIVE=$(ls -d harbor_tasks_md_authoring/*/ 2>/dev/null | wc -l)
bash scripts/run_wider_after_classify.sh "${LABEL}_scaffold" \
  > "$LOG_DIR/scaffold_${LABEL}.log" 2>&1
POST_ACTIVE=$(ls -d harbor_tasks_md_authoring/*/ 2>/dev/null | wc -l)
log "  active corpus: $PRE_ACTIVE -> $POST_ACTIVE (delta $((POST_ACTIVE-PRE_ACTIVE)))"

# 7. Smoke build a sample of new task Dockerfiles to verify they're not rotten
log "Phase 6: docker smoke-build sample of new tasks"
git -C /home/alex/agentsmd-rl status --short harbor_tasks_md_authoring/ 2>/dev/null \
    | awk '/^\?\? harbor_tasks_md_authoring\//{ gsub(/\?\? harbor_tasks_md_authoring\//,""); gsub("/$",""); print }' \
    | shuf | head -10 > /tmp/smoke_sample_${LABEL}.txt
SMOKE_PASS=0
SMOKE_FAIL=0
SMOKE_FAILURES=""
while read -r task; do
    [ -z "$task" ] && continue
    df="harbor_tasks_md_authoring/$task/environment/Dockerfile"
    if [ ! -f "$df" ]; then continue; fi
    log "  building $task ..."
    if timeout 180 docker build --quiet -t "agentsmd-smoke:$task" -f "$df" "harbor_tasks_md_authoring/$task/environment" \
        > "$LOG_DIR/smoke_${LABEL}_${task//[^a-zA-Z0-9_-]/_}.log" 2>&1; then
        SMOKE_PASS=$((SMOKE_PASS + 1))
    else
        SMOKE_FAIL=$((SMOKE_FAIL + 1))
        SMOKE_FAILURES+="$task "
    fi
done < /tmp/smoke_sample_${LABEL}.txt
log "  smoke build: $SMOKE_PASS pass, $SMOKE_FAIL fail of 10 sample"
if [ -n "$SMOKE_FAILURES" ]; then
    log "  failures: $SMOKE_FAILURES"
fi

# 8. Commit + push (only if smoke build is mostly OK)
if [ $SMOKE_FAIL -gt 5 ]; then
    log "Phase 7: smoke-build mostly failing ($SMOKE_FAIL/10) — SKIP commit"
    log "  Investigate logs in $LOG_DIR/smoke_${LABEL}_*.log before committing."
    exit 1
fi

log "Phase 7: stage + commit"
git -C /home/alex/agentsmd-rl add \
    harbor_tasks_md_authoring/ \
    harbor_tasks_md_authoring_quarantine_quality/ \
    harbor_tasks_md_authoring_quarantine_secrets/ \
    research/md_authoring_quality_judgments.json \
    scripts/discover_recent_skill_prs.py \
    scripts/discover_via_code_search.py \
    scripts/run_overnight_comprehensive_scout.sh \
    scripts/run_wider_after_classify.sh \
    scripts/rejudge_diff_and_rescue.py \
    scripts/scaffold_markdown_only.py \
    scripts/quality_judge.py \
    scripts/classify_repos_llm.py \
    taskforge/config.py \
    taskforge/gh_graphql.py \
    taskforge/scout.py \
    .gitignore 2>/dev/null || true

DELTA=$((POST_ACTIVE - PRE_ACTIVE))
git -C /home/alex/agentsmd-rl commit -m "$(cat <<EOF
Overnight comprehensive scout: $DELTA net new active markdown_authoring tasks

Pipeline (label=${LABEL}):
- Phase 1: code-search across 24 filename/path queries (~5K unique repos)
- Phase 2: 28-query date-windowed title scout (recovers cap-truncated tails)
- Phase 3: merge + dedupe -> $M_COUNT unique candidate PRs
- Phase 4: LLM repo classifier (GraphQL bundle, $USEFUL/$R_COUNT useful)
- Phase 5: deterministic scaffold + repo_class.json sidecar
- Phase 6: post-judge with --quarantine (Gemini flex tier)
- Phase 7: smoke-build $SMOKE_PASS/10 random task Dockerfiles

Active corpus: $PRE_ACTIVE -> $POST_ACTIVE.

Raw scouting outputs preserved under scout_data/ (gitignored) for re-judge:
  - code_search_${LABEL}.jsonl ($CS_COUNT PRs)
  - title_${LABEL}.jsonl ($T_COUNT PRs)
  - merged_${LABEL}.jsonl ($M_COUNT unique)
  - repo_class_${LABEL}.jsonl ($R_COUNT classified)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)" 2>"$LOG_DIR/commit_${LABEL}.err" || log "  commit failed — see $LOG_DIR/commit_${LABEL}.err"

log "Phase 8: push"
git -C /home/alex/agentsmd-rl push origin master 2>"$LOG_DIR/push_${LABEL}.err" \
    && log "  push: ok" \
    || log "  push failed — see $LOG_DIR/push_${LABEL}.err"

# 9. Trigger CI image build workflow
log "Phase 9: trigger CI image build (push-images.yml)"
gh workflow run push-images.yml \
    -f task_dir=harbor_tasks_md_authoring \
    -f tier_a_only=false \
    -f update_toml=false 2>&1 \
    | tee -a "$LOG_DIR/workflow_${LABEL}.log"

log "ALL DONE."
log "  raw discoveries: $SCOUT_DIR/{code_search,title,merged}_${LABEL}.jsonl"
log "  classifier: $SCOUT_DIR/repo_class_${LABEL}.jsonl"
log "  active corpus: $POST_ACTIVE"
log "  smoke: $SMOKE_PASS/10 build pass"
