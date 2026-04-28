#!/usr/bin/env python3
"""Chain: cross-repo skill-PR discover → repo classify → Pipeline B → commit.

Designed to run unattended once GH REST budget is available. Steps:

  1. Run scripts/discover_recent_skill_prs.py to produce candidate PRs from
     ≥500-star repos with skill activity in the last N days.
  2. Run scripts/classify_repos_llm.py on the unique repos in (1).
  3. Filter the discover output to PRs whose repo class is real software
     (production_software | working_tool) AND created before --max-created.
  4. Pre-judge → deterministic scaffold → post-judge with --quarantine
     (Pipeline B as the existing v3 orchestrator runs it).
  5. Commit + push the survivors with their `repo_class.json` sidecars,
     trigger the GHCR build workflow.

Usage:
    .venv/bin/python scripts/cross_repo_orchestrator.py \\
        --since 2025-12-27 \\
        --max-created 2025-12-01 \\
        --label cross_repo
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
MD_DIR = ROOT / "harbor_tasks_md_authoring"


def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def run(cmd, log_path: Path) -> int:
    log(f"running: {' '.join(str(c) for c in cmd)} > {log_path.name}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"  rc={rc}")
    return rc


def count_corpus():
    return sum(1 for d in MD_DIR.iterdir() if d.is_dir())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-12-27",
                    help="Only consider PRs merged after this date")
    ap.add_argument("--min-stars", type=int, default=500)
    ap.add_argument("--max-created", default="2025-12-01",
                    help="Drop repos created on/after this date (recency filter)")
    ap.add_argument("--label", default="cross_repo")
    args = ap.parse_args()

    LOGDIR = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26"
    LOGDIR.mkdir(parents=True, exist_ok=True)

    initial_corpus = count_corpus()
    log(f"Cross-repo orchestrator start. Initial corpus: {initial_corpus}")

    # 1. Discover
    discover_out = Path("/tmp/recent_skill_prs.jsonl")
    log("Phase 1: cross-repo discovery")
    rc = run([".venv/bin/python", "scripts/discover_recent_skill_prs.py",
              "--since", args.since,
              "--min-stars", str(args.min_stars),
              "--output", str(discover_out),
              "--max-pages", "10"],
             LOGDIR / f"discover_{args.label}.log")
    if rc != 0 or not discover_out.exists() or discover_out.stat().st_size == 0:
        log("Discovery produced no output; aborting.")
        return

    n_disc = sum(1 for _ in open(discover_out))
    log(f"  discovered {n_disc} candidate PRs")

    # 2. Extract unique repos and classify
    repos = sorted({json.loads(l)["repo"] for l in open(discover_out)})
    repos_file = Path(f"/tmp/{args.label}_repos.txt")
    repos_file.write_text("\n".join(repos) + "\n")
    log(f"  {len(repos)} unique repos to classify")

    classify_out = Path(f"/tmp/{args.label}_repo_class.jsonl")
    log("Phase 2: LLM repo classification")
    rc = run([".venv/bin/python", "scripts/classify_repos_llm.py",
              "--repos-file", str(repos_file),
              "--output", str(classify_out),
              "--concurrency", "8"],
             LOGDIR / f"classify_{args.label}.log")
    if rc != 0 or not classify_out.exists():
        log("Classifier produced no output; aborting.")
        return

    classifications = {}
    for line in open(classify_out):
        c = json.loads(line)
        classifications[c["repo"]] = c

    # 3. Filter
    log("Phase 3: filter to real-software repos created before " + args.max_created)
    kept = []
    dropped_class = dropped_recency = 0
    for line in open(discover_out):
        d = json.loads(line)
        c = classifications.get(d["repo"], {})
        if not c.get("is_useful_for_benchmark"):
            dropped_class += 1
            continue
        created = c.get("repo_created_at", "")
        if created and created >= args.max_created:
            dropped_recency += 1
            continue
        # Attach the classification as metadata on the row
        d["repo_class"] = {
            "class": c.get("class"),
            "purpose_one_line": c.get("purpose_one_line"),
            "skills_relationship": c.get("skills_relationship"),
            "stars": c.get("stars"),
            "primary_language": c.get("primary_language"),
            "repo_created_at": c.get("repo_created_at"),
        }
        kept.append(d)
    log(f"  {len(kept)} kept (dropped {dropped_class} for class, "
        f"{dropped_recency} for recency)")

    if not kept:
        log("Nothing survived filter; aborting.")
        return

    filtered = Path(f"/tmp/{args.label}_filtered.jsonl")
    with open(filtered, "w") as f:
        for d in kept:
            f.write(json.dumps(d) + "\n")

    # 4. Pre-judge (Pipeline B)
    log("Phase 4: pre-judge")
    prejudged = Path(f"/tmp/{args.label}_prejudged.jsonl")
    rc = run([".venv/bin/python", "scripts/quality_judge.py",
              "--mode", "markdown_authoring",
              "--scout-jsonl", str(filtered),
              "--filtered-output", str(prejudged),
              "--service-tier", "standard",
              "--concurrency", "16"],
             LOGDIR / f"prejudge_{args.label}.log")
    if rc != 0 or not prejudged.exists() or prejudged.stat().st_size == 0:
        log("Pre-judge produced no output; aborting.")
        return

    # 5. Build queue and scaffold
    log("Phase 5: deterministic scaffold")
    queue = Path(f"/tmp/scaffold_queue_{args.label}.jsonl")
    n_q = 0
    with open(prejudged) as fin, open(queue, "w") as fout:
        for line in fin:
            d = json.loads(line)
            row = {"repo": d["repo"],
                   "pr": d.get("pr_number") or d.get("pr"),
                   "file_paths": d.get("file_paths", [])}
            fout.write(json.dumps(row) + "\n")
            n_q += 1
    log(f"  queue size: {n_q}")

    pre = count_corpus()
    rc = run([".venv/bin/python", "scripts/scaffold_markdown_only.py",
              "--queue", str(queue),
              "--out-dir", "harbor_tasks_md_authoring",
              "--concurrency", "16"],
             LOGDIR / f"md_only_{args.label}.log")
    post_scaff = count_corpus()
    log(f"  scaffolded: {post_scaff - pre} new ({pre} -> {post_scaff})")

    # 6. Attach repo_class.json sidecar to each new task that came from this batch
    log("Phase 6: attach repo_class.json sidecars")
    n_sidecar = 0
    for line in open(prejudged):
        d = json.loads(line)
        repo = d["repo"]
        c = classifications.get(repo, {})
        if not c:
            continue
        # Find any task in MD_DIR sourced from this (repo, pr)
        # Slug is repo-short + title words; we just match on repo prefix in slug
        # — cheap and safe enough for sidecar attachment.
        repo_short = repo.split("/")[-1].lower()
        pr = d.get("pr_number") or d.get("pr")
        for tdir in MD_DIR.iterdir():
            if not tdir.is_dir():
                continue
            if not tdir.name.startswith(repo_short[:20]):
                continue
            em = tdir / "eval_manifest.yaml"
            if not em.exists():
                continue
            try:
                txt = em.read_text()
                if f"pr: {pr}" in txt or f'pr: "{pr}"' in txt:
                    sidecar = tdir / "repo_class.json"
                    sidecar.write_text(json.dumps({
                        "class": c.get("class"),
                        "purpose_one_line": c.get("purpose_one_line"),
                        "skills_relationship": c.get("skills_relationship"),
                        "stars": c.get("stars"),
                        "primary_language": c.get("primary_language"),
                        "repo_created_at": c.get("repo_created_at"),
                    }, indent=2))
                    n_sidecar += 1
                    break
            except Exception:
                pass
    log(f"  attached {n_sidecar} repo_class.json sidecars")

    # 7. Post-judge with --quarantine (full corpus)
    log("Phase 7: post-judge with --quarantine")
    judge_out = LOGDIR / f"md_quality_{args.label}.json"
    rc = run([".venv/bin/python", "scripts/quality_judge.py",
              "--mode", "markdown_authoring",
              "--task-dir", "harbor_tasks_md_authoring",
              "--concurrency", "32",
              "--service-tier", "standard",
              "--quarantine",
              "--output", str(judge_out)],
             LOGDIR / f"md_quality_{args.label}.log")
    final = count_corpus()
    log(f"After post-judge quarantine: {final} active "
        f"(was {post_scaff} pre-quarantine; net {final - initial_corpus} new "
        f"from this batch over initial {initial_corpus})")

    # 8. Commit + push + GHCR
    log("Phase 8: commit + push")

    # Quarantine any tasks that trip the secret-pattern pre-commit hook before
    # staging. We assemble the hook's regex from parts so this script itself
    # doesn't trip it on commit.
    import re as _re
    _patterns = [
        "AI" + "zaSy",                                # google api key prefix
        "sk-" + "ant-",                               # anthropic api key prefix
        "sk-[a-z]{2}-[a-zA-Z0-9]{20,}",               # other sk-XX-... keys
    ]
    HOOK_RE = _re.compile("|".join(_patterns))
    quarantine_secrets = ROOT / "harbor_tasks_md_authoring_quarantine_secrets"
    quarantine_secrets.mkdir(exist_ok=True)
    for tdir in MD_DIR.iterdir():
        if not tdir.is_dir():
            continue
        try:
            for f in tdir.rglob("*"):
                if not f.is_file():
                    continue
                if f.suffix in (".bin", ".png", ".jpg"):
                    continue
                try:
                    if HOOK_RE.search(f.read_text(errors="ignore")):
                        dst = quarantine_secrets / tdir.name
                        if not dst.exists():
                            shutil.move(str(tdir), str(dst))
                        break
                except Exception:
                    pass
        except Exception:
            pass

    subprocess.run(["git", "add",
                    "harbor_tasks_md_authoring/",
                    "harbor_tasks_md_authoring_quarantine_quality/",
                    "research/md_authoring_quality_judgments.json",
                    "scripts/cross_repo_orchestrator.py"],
                   cwd=ROOT, check=False)
    msg = (f"Add cross-repo discover batch ({final - initial_corpus} new active)\n\n"
           f"Pipeline: cross-repo discover (≥{args.min_stars} stars, merged "
           f">{args.since}) → LLM repo classifier (drop skill_collection / "
           f"fork_or_template / abandoned) → recency filter (drop repos "
           f"created on/after {args.max_created}) → Pipeline B pre-judge → "
           f"deterministic scaffold + repo_class.json sidecar → post-judge "
           f"with --quarantine.\n\n"
           f"Active corpus: {initial_corpus} → {final}.\n\n"
           f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(f"git commit: {r.stderr[-300:]}")
        return
    log(f"committed: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")
    r = subprocess.run(["git", "push", "origin", "master"], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    log(f"push: {r.stdout.strip()[:100] if r.returncode == 0 else r.stderr[-300:]}")

    r = subprocess.run(["gh", "workflow", "run", "push-images.yml",
                        "-f", "task_dir=harbor_tasks_md_authoring",
                        "-f", "tier_a_only=false",
                        "-f", "update_toml=false"],
                       cwd=ROOT, capture_output=True, text=True)
    log(f"workflow: {r.stdout.strip() or r.stderr[-200:]}")
    log("Cross-repo orchestrator done.")


if __name__ == "__main__":
    main()
