#!/usr/bin/env python3
"""Overnight orchestrator: scaffold harbor_tasks_md_authoring to ≥500 + push to GHCR.

Plan:
  1. Wait for main scaffolder (PID arg) to exit
  2. Wait for scout-extra-100 (PID arg) to produce its JSONL output
  3. Run scaffold_markdown_only.py on that JSONL
  4. Verify corpus, commit + push
  5. Trigger gh workflow run push-images.yml on harbor_tasks_md_authoring

Designed to run unattended via:
    nohup setsid .venv/bin/python scripts/overnight_md_orchestrator.py \\
        --main-pid 27565 --scout-pid 37660 \\
        > pipeline_logs/scaffold_v4_2026_04_26/orchestrator.log 2>&1 &
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
MD_DIR = ROOT / "harbor_tasks_md_authoring"
WORKFLOW = ".github/workflows/push-images.yml"
TARGET = 500


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def pid_alive(pid: int) -> bool:
    return Path(f"/proc/{pid}").exists()


def wait_for_pid(pid: int, name: str, max_hours: float = 12.0) -> bool:
    t0 = time.time()
    while pid_alive(pid):
        elapsed = time.time() - t0
        if elapsed > max_hours * 3600:
            log(f"[{name}] timeout after {max_hours}h — proceeding anyway")
            return False
        time.sleep(120)  # poll every 2 min
    log(f"[{name}] PID {pid} exited (waited {(time.time()-t0)/60:.1f} min)")
    return True


def count_corpus() -> int:
    return sum(1 for d in MD_DIR.iterdir() if d.is_dir())


def transform_scout_to_queue(scout_path: Path, queue_path: Path) -> int:
    """Convert scout JSONL ({repo, pr_number}) → scaffold queue ({repo, pr})."""
    n = 0
    with open(scout_path) as fin, open(queue_path, "w") as fout:
        for line in fin:
            d = json.loads(line)
            fout.write(json.dumps({"repo": d["repo"], "pr": d["pr_number"]}) + "\n")
            n += 1
    return n


def run_scaffolder(queue_path: Path, log_path: Path) -> bool:
    """Run scaffold_markdown_only.py blocking; return True on exit 0."""
    log(f"launching scaffold_markdown_only on {queue_path.name}")
    cmd = [
        ".venv/bin/python", "scripts/scaffold_markdown_only.py",
        "--queue", str(queue_path),
        "--out-dir", "harbor_tasks_md_authoring",
        "--concurrency", "16",
    ]
    with open(log_path, "w") as logf:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT)
        rc = proc.wait()
    log(f"scaffolder exit code: {rc}")
    return rc == 0


def git_commit_and_push() -> bool:
    log("staging md_authoring + workflow change")
    subprocess.run(["git", "add", "harbor_tasks_md_authoring/", WORKFLOW,
                    "scripts/overnight_md_orchestrator.py",
                    "scripts/scaffold_markdown_only.py",
                    "scripts/dockerfile_shallow_migrate.py"],
                   cwd=ROOT, check=False)
    n = count_corpus()
    msg = (f"Add {n} markdown_authoring tasks + GHCR workflow option\n\n"
           f"Deterministic scaffolder (no LLM) for pure-tier1-md PRs.\n"
           f"Includes harbor_tasks_md_authoring as workflow choice for ghcr push.\n\n"
           f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"git commit failed: {r.stderr[-300:]}")
        return False
    log(f"committed: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")
    log("pushing to origin")
    r = subprocess.run(["git", "push", "origin", "master"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        log(f"git push failed: {r.stderr[-300:]}")
        return False
    log("pushed successfully")
    return True


def trigger_ghcr_workflow() -> bool:
    log("triggering gh workflow push-images.yml on harbor_tasks_md_authoring")
    cmd = ["gh", "workflow", "run", "push-images.yml",
           "-f", "task_dir=harbor_tasks_md_authoring",
           "-f", "tier_a_only=false",
           "-f", "update_toml=false"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"workflow trigger failed: {r.stderr[-300:]}")
        return False
    log(f"workflow triggered: {r.stdout.strip()}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main-pid", type=int, required=True,
                    help="PID of the running main scaffolder (new-188 batch)")
    ap.add_argument("--scout-pid", type=int, required=True,
                    help="PID of the scout-extra-100 process")
    ap.add_argument("--scout-output", type=Path,
                    default=ROOT / "scouted_extra100_2026_04_26.jsonl")
    ap.add_argument("--skip-extra-scaffold", action="store_true",
                    help="Skip the extra100 scaffold step")
    ap.add_argument("--skip-push", action="store_true",
                    help="Skip git commit + push + workflow trigger")
    args = ap.parse_args()

    log(f"Orchestrator start. Initial corpus: {count_corpus()}")
    log(f"Target: ≥{TARGET}")

    # Phase 1: wait for both running jobs
    log(f"Phase 1: waiting for main scaffolder PID {args.main_pid}")
    wait_for_pid(args.main_pid, "main_scaffolder", max_hours=10)
    log(f"After main scaffolder: corpus = {count_corpus()}")

    log(f"Phase 2: waiting for scout-extra-100 PID {args.scout_pid}")
    wait_for_pid(args.scout_pid, "scout_extra100", max_hours=2)

    # Phase 3: scaffold extra-100 output
    if not args.skip_extra_scaffold and args.scout_output.exists():
        queue_extra = Path("/tmp/scaffold_queue_extra100.jsonl")
        n = transform_scout_to_queue(args.scout_output, queue_extra)
        log(f"Transformed {n} scout rows → {queue_extra}")
        run_scaffolder(queue_extra, ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / "md_only_extra100.log")
        log(f"After extra100 scaffolder: corpus = {count_corpus()}")
    elif not args.scout_output.exists():
        log(f"WARN: scout output {args.scout_output} missing — skipping extra scaffold")

    # Phase 4: report + push
    final_n = count_corpus()
    log(f"Final corpus: {final_n} (target {TARGET}, met={'YES' if final_n >= TARGET else 'NO'})")

    if args.skip_push:
        log("--skip-push set, exiting before commit/push/workflow")
        return

    # Phase 5: commit + push + GHCR
    if git_commit_and_push():
        trigger_ghcr_workflow()
    else:
        log("skipping workflow trigger because git push failed")

    log("Orchestrator done.")


if __name__ == "__main__":
    main()
