#!/usr/bin/env python3
"""Phase-2 orchestrator: scaffold the supplement scout output and re-push.

Runs after overnight_md_orchestrator.py finishes its main commit+push+GHCR cycle.
Adds the supplement scout's 2,579 PRs into the corpus, then a second commit +
re-trigger of the GHCR workflow (which skips existing images automatically).
"""
from __future__ import annotations
import argparse
import json
import subprocess
import time
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
MD_DIR = ROOT / "harbor_tasks_md_authoring"
WORKFLOW = ".github/workflows/push-images.yml"


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def pid_alive(pid: int) -> bool:
    return Path(f"/proc/{pid}").exists()


def wait_for_pid(pid: int, name: str, max_hours: float = 6.0) -> None:
    t0 = time.time()
    while pid_alive(pid):
        if time.time() - t0 > max_hours * 3600:
            log(f"[{name}] timeout — proceeding anyway")
            return
        time.sleep(120)
    log(f"[{name}] PID {pid} exited (waited {(time.time()-t0)/60:.1f}m)")


def count_corpus() -> int:
    return sum(1 for d in MD_DIR.iterdir() if d.is_dir())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase1-pid", type=int, required=True)
    ap.add_argument("--scout-output", type=Path,
                    default=ROOT / "scouted_supplement50.jsonl")
    args = ap.parse_args()

    log(f"Phase-2 orchestrator start. Corpus: {count_corpus()}")
    log(f"Waiting for phase-1 orchestrator PID {args.phase1_pid} to finish")
    wait_for_pid(args.phase1_pid, "phase1_orchestrator", max_hours=6)
    log(f"After phase-1 orchestrator: corpus = {count_corpus()}")

    # Transform supplement scout to queue format
    queue = Path("/tmp/scaffold_queue_supplement50.jsonl")
    n = 0
    with open(args.scout_output) as fin, open(queue, "w") as fout:
        for line in fin:
            d = json.loads(line)
            fout.write(json.dumps({"repo": d["repo"], "pr": d["pr_number"]}) + "\n")
            n += 1
    log(f"Transformed {n} supplement scout rows → {queue}")

    # Run scaffolder
    log("launching scaffold_markdown_only on supplement queue")
    log_path = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / "md_only_supplement50.log"
    cmd = [".venv/bin/python", "scripts/scaffold_markdown_only.py",
           "--queue", str(queue), "--out-dir", "harbor_tasks_md_authoring",
           "--concurrency", "16"]
    with open(log_path, "w") as logf:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT)
        rc = proc.wait()
    log(f"supplement scaffolder rc={rc}")

    final_n = count_corpus()
    log(f"Final corpus: {final_n}")

    # Stage + commit + push
    log("staging new tasks for second commit")
    subprocess.run(["git", "add", "harbor_tasks_md_authoring/"], cwd=ROOT, check=False)
    msg = (f"Add {final_n - 447} more markdown_authoring tasks (supplement scout)\n\n"
           f"Total md_authoring corpus: {final_n}.\n\n"
           f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"git commit (likely nothing to commit): {r.stdout[-200:]} {r.stderr[-200:]}")
    else:
        log(f"committed: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")
        r = subprocess.run(["git", "push", "origin", "master"],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            log(f"git push failed: {r.stderr[-300:]}")
        else:
            log("pushed")

    # Re-trigger GHCR — the workflow has --skip-existing default, so already-pushed
    # images are no-ops; only the new supplement images get built+pushed.
    log("re-triggering gh workflow push-images.yml")
    cmd = ["gh", "workflow", "run", "push-images.yml",
           "-f", "task_dir=harbor_tasks_md_authoring",
           "-f", "tier_a_only=false", "-f", "update_toml=false"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"workflow trigger failed: {r.stderr[-300:]}")
    else:
        log(f"workflow triggered: {r.stdout.strip()}")
    log("Phase-2 done.")


if __name__ == "__main__":
    main()
