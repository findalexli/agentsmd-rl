#!/usr/bin/env python3
"""Scale-up orchestrator: optimized scout → optimized scaffold → judge → push.

Chain:
1. Wait for scout PID to finish
2. Transform scout JSONL → scaffolder queue (carrying file_paths)
3. Run scaffold_markdown_only.py — fast-path skips REST for codebearing PRs
4. Run quality_judge.py on the freshly scaffolded tasks (Flex tier)
5. Quarantine reject verdicts to harbor_tasks_md_authoring_quarantine_quality/
6. Commit + push + trigger GHCR workflow
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
MD_DIR = ROOT / "harbor_tasks_md_authoring"


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def pid_alive(pid: int) -> bool:
    return Path(f"/proc/{pid}").exists()


def wait_for_pid(pid: int, name: str, max_hours: float = 8.0) -> None:
    t0 = time.time()
    while pid_alive(pid):
        if time.time() - t0 > max_hours * 3600:
            log(f"[{name}] timeout — proceeding")
            return
        time.sleep(120)
    log(f"[{name}] PID {pid} done (waited {(time.time()-t0)/60:.1f}m)")


def count_corpus() -> int:
    return sum(1 for d in MD_DIR.iterdir() if d.is_dir())


def transform_scout_to_queue(scout_jsonl: Path, queue: Path) -> int:
    """Carry file_paths from scout into queue rows so scaffolder fast-path
    can skip REST `/files` calls for codebearing PRs."""
    n = 0
    with open(scout_jsonl) as fin, open(queue, "w") as fout:
        for line in fin:
            d = json.loads(line)
            row = {"repo": d["repo"], "pr": d["pr_number"]}
            if d.get("file_paths"):
                row["file_paths"] = d["file_paths"]
            fout.write(json.dumps(row) + "\n")
            n += 1
    return n


def run(cmd, log_path):
    log(f"running: {' '.join(cmd)} > {log_path.name}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"  rc={rc}")
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scout-pid", type=int, required=True)
    ap.add_argument("--scout-output", type=Path,
                    default=ROOT / "scouted_scaleup_2026_04_27.jsonl")
    ap.add_argument("--label", default="scaleup")
    args = ap.parse_args()

    log(f"Scaleup orchestrator start. Initial corpus: {count_corpus()}")

    log(f"Phase 1: waiting for scout PID {args.scout_pid}")
    wait_for_pid(args.scout_pid, "scaleup_scout", max_hours=6)

    if not args.scout_output.exists():
        log(f"ERROR: scout output {args.scout_output} missing — exiting")
        return

    # Phase 1.5: Gemini pre-judge filter on scout output (title + file_paths
    # only — no body/patch yet). Drops obvious slop before scaffolder runs.
    # Lighter signal than the post-scaffold judge, so post-judge stays as final QC.
    prejudge_in = args.scout_output
    prejudge_out = ROOT / f"scouted_{args.label}_prejudged.jsonl"
    prejudge_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"prejudge_{args.label}.log"
    log(f"Phase 1.5: Gemini pre-judge on scout output (Standard tier — Flex flakey)")
    rc = run([".venv/bin/python", "scripts/quality_judge.py",
              "--mode", "markdown_authoring",
              "--scout-jsonl", str(prejudge_in),
              "--filtered-output", str(prejudge_out),
              "--service-tier", "standard",
              "--concurrency", "16"],
             prejudge_log)
    # Use filtered output if pre-judge succeeded; fall back to original on error.
    scout_for_scaffold = prejudge_out if (rc == 0 and prejudge_out.exists()) else prejudge_in
    log(f"Pre-judge result rc={rc}, using {scout_for_scaffold.name} for scaffold")

    queue = Path(f"/tmp/scaffold_queue_{args.label}.jsonl")
    n = transform_scout_to_queue(scout_for_scaffold, queue)
    log(f"Transformed {n} scout rows → {queue}")

    log("Phase 2: scaffold (fast-path with file_paths from scout)")
    scaffold_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_only_{args.label}.log"
    pre = count_corpus()
    run([".venv/bin/python", "scripts/scaffold_markdown_only.py",
         "--queue", str(queue),
         "--out-dir", "harbor_tasks_md_authoring",
         "--concurrency", "32"],
        scaffold_log)
    post_scaffold = count_corpus()
    log(f"Scaffolded {post_scaffold - pre} new tasks ({pre} → {post_scaffold})")

    log("Phase 3: Gemini quality judge on full corpus (Flex)")
    judge_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_quality_{args.label}.log"
    judge_out = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_quality_{args.label}.json"
    run([".venv/bin/python", "scripts/quality_judge.py",
         "--mode", "markdown_authoring",
         "--task-dir", "harbor_tasks_md_authoring",
         "--concurrency", "16",
         "--service-tier", "flex",
         "--quarantine",
         "--output", str(judge_out)],
        judge_log)
    post_judge = count_corpus()
    log(f"After quarantine: {post_judge} kept (was {post_scaffold})")

    log("Phase 4: git commit + push + GHCR workflow")
    subprocess.run(["git", "add",
                    "harbor_tasks_md_authoring/",
                    "harbor_tasks_md_authoring_quarantine_quality/",
                    "scripts/scaffold_markdown_only.py",
                    "scripts/quality_judge.py",
                    "taskforge/scout.py",
                    "taskforge/gemini_rubric_constructor.py",
                    "scripts/overnight_scaleup_orchestrator.py"],
                   cwd=ROOT, check=False)
    msg = (f"Add {post_judge - pre} more markdown_authoring tasks "
           f"(scaleup) + Gemini quality gate\n\n"
           f"Total corpus: {post_judge}. Scout-time `files` field optimization "
           f"+ scaffolder fast-path skip REST `/files` for codebearing PRs.\n"
           f"Quality gate via taskforge.gemini_rubric_constructor.call_gemini "
           f"(Flex tier, 50% off Standard) extending scripts/quality_judge.py "
           f"with --mode markdown_authoring.\n\n"
           f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(f"git commit: {r.stderr[-300:]}")
        return
    log(f"committed: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")
    r = subprocess.run(["git", "push", "origin", "master"], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        log(f"push failed: {r.stderr[-300:]}")
        return
    log("pushed")

    r = subprocess.run(["gh", "workflow", "run", "push-images.yml",
                        "-f", "task_dir=harbor_tasks_md_authoring",
                        "-f", "tier_a_only=false",
                        "-f", "update_toml=false"],
                       cwd=ROOT, capture_output=True, text=True)
    log(f"workflow trigger: {r.stdout.strip() or r.stderr[-200:]}")
    log("Scaleup orchestrator done.")


if __name__ == "__main__":
    main()
