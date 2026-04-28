#!/bin/bash
# Continue the wider scout pipeline after discover + classifier already ran.
# Inputs: /tmp/recent_skill_prs_wide.jsonl, /tmp/cross_repo_wide_repo_class.jsonl
# Output: scaffolded tasks in harbor_tasks_md_authoring/, post-judged, committed.
set -euo pipefail
cd /home/alex/agentsmd-rl

LABEL="${1:-cross_repo_wide}"
LOGDIR=pipeline_logs/scaffold_v4_2026_04_26
DISCOVER_OUT=/tmp/recent_skill_prs_wide.jsonl
CLASSIFY_OUT=/tmp/cross_repo_wide_repo_class.jsonl

echo "[$(date +%H:%M:%S)] Phase 3: attach repo_class metadata (no filter)"
.venv/bin/python - <<'PY'
import json
from pathlib import Path
DISC = Path("/tmp/recent_skill_prs_wide.jsonl")
CLAS = Path("/tmp/cross_repo_wide_repo_class.jsonl")
OUT  = Path("/tmp/cross_repo_wide_filtered.jsonl")
classes = {}
for line in CLAS.open():
    c = json.loads(line)
    classes[c["repo"]] = c
n = 0
with OUT.open("w") as f:
    for line in DISC.open():
        d = json.loads(line)
        c = classes.get(d["repo"], {})
        d["repo_class"] = {
            "class": c.get("class"),
            "purpose_one_line": c.get("purpose_one_line"),
            "skills_relationship": c.get("skills_relationship"),
            "stars": c.get("stars"),
            "primary_language": c.get("primary_language"),
            "repo_created_at": c.get("repo_created_at"),
            "is_useful_for_benchmark": c.get("is_useful_for_benchmark"),
        }
        f.write(json.dumps(d) + "\n"); n += 1
print(f"  metadata-attached {n} candidates -> {OUT}")
PY

echo "[$(date +%H:%M:%S)] Phase 4: build scaffold queue"
.venv/bin/python - <<'PY'
import json
from pathlib import Path
SRC = Path("/tmp/cross_repo_wide_filtered.jsonl")
OUT = Path("/tmp/scaffold_queue_cross_repo_wide.jsonl")
n = 0
with OUT.open("w") as f:
    for line in SRC.open():
        d = json.loads(line)
        f.write(json.dumps({
            "repo": d["repo"],
            "pr": d.get("pr_number") or d.get("pr"),
            "file_paths": d.get("file_paths", []),
        }) + "\n"); n += 1
print(f"  queue size: {n}")
PY

echo "[$(date +%H:%M:%S)] Phase 5: deterministic scaffold"
PRE=$(ls -d harbor_tasks_md_authoring/*/ | wc -l)
.venv/bin/python scripts/scaffold_markdown_only.py \
    --queue /tmp/scaffold_queue_cross_repo_wide.jsonl \
    --out-dir harbor_tasks_md_authoring \
    --concurrency 16 \
  > "$LOGDIR/md_only_${LABEL}.log" 2>&1
POST=$(ls -d harbor_tasks_md_authoring/*/ | wc -l)
echo "  scaffolded: $((POST-PRE)) new ($PRE -> $POST)"

echo "[$(date +%H:%M:%S)] Phase 6: attach repo_class.json sidecars"
.venv/bin/python - <<'PY'
import json
from pathlib import Path
SRC = Path("/tmp/cross_repo_wide_filtered.jsonl")
MD_DIR = Path("/home/alex/agentsmd-rl/harbor_tasks_md_authoring")
classes = {}
for line in SRC.open():
    d = json.loads(line)
    classes[(d["repo"], d.get("pr_number") or d.get("pr"))] = d.get("repo_class", {})
n = 0
for tdir in MD_DIR.iterdir():
    if not tdir.is_dir(): continue
    em = tdir / "eval_manifest.yaml"
    if not em.exists(): continue
    txt = em.read_text(errors="replace")
    for (repo, pr), c in classes.items():
        repo_short = repo.split("/")[-1].lower()[:20]
        if not tdir.name.startswith(repo_short): continue
        if f"pr: {pr}" in txt or f'pr: "{pr}"' in txt:
            (tdir / "repo_class.json").write_text(json.dumps(c, indent=2))
            n += 1
            break
print(f"  attached {n} sidecars")
PY

echo "[$(date +%H:%M:%S)] Phase 7: post-judge with --quarantine"
.venv/bin/python scripts/quality_judge.py \
    --mode markdown_authoring \
    --task-dir harbor_tasks_md_authoring \
    --concurrency 32 \
    --service-tier flex \
    --quarantine \
    --output "$LOGDIR/md_quality_${LABEL}.json" \
  > "$LOGDIR/md_quality_${LABEL}.log" 2>&1
FINAL=$(ls -d harbor_tasks_md_authoring/*/ | wc -l)
echo "  active after quarantine: $FINAL"

echo "[$(date +%H:%M:%S)] Phase 8: pre-commit secret-pattern quarantine"
.venv/bin/python - <<'PY'
import re, shutil
from pathlib import Path
ROOT = Path("/home/alex/agentsmd-rl")
patterns = ["AI" + "zaSy", "sk-" + "ant-", "sk-[a-z]{2}-[a-zA-Z0-9]{20,}"]
HOOK = re.compile("|".join(patterns))
src = ROOT / "harbor_tasks_md_authoring"
dst = ROOT / "harbor_tasks_md_authoring_quarantine_secrets"
dst.mkdir(exist_ok=True)
n = 0
for tdir in src.iterdir():
    if not tdir.is_dir(): continue
    try:
        for f in tdir.rglob("*"):
            if not f.is_file(): continue
            if f.suffix in (".bin", ".png", ".jpg"): continue
            if HOOK.search(f.read_text(errors="ignore")):
                target = dst / tdir.name
                if not target.exists():
                    shutil.move(str(tdir), str(target)); n += 1
                break
    except Exception: pass
print(f"  secret-quarantined: {n}")
PY

echo "[$(date +%H:%M:%S)] Done. Run git status / git add / git commit manually."
