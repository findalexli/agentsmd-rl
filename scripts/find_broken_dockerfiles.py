#!/usr/bin/env python3
"""Discover Dockerfile rot from recent push-images.yml workflow runs.

For each FAILED job in the last N runs:
  1. Pull the per-step log
  2. Identify which task it was building (matrix input)
  3. Capture the last ~50 lines as failure context
  4. Write `markdown_following/<task>/_failure.log` for the fix pipeline to upload
  5. Append `{"task_ref": "<task>"}` to the input JSONL

Output:
  pipeline_logs/dockerfile_fix_<ts>/input.jsonl
  pipeline_logs/dockerfile_fix_<ts>/discovery.json (per-failure detail)

Usage:
  python scripts/find_broken_dockerfiles.py --max-runs 5
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def gh_json(args: list[str]) -> dict | list:
    r = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def list_recent_runs(max_runs: int = 10) -> list[dict]:
    """Return recent push-images.yml runs, newest first."""
    return gh_json([
        "run", "list", "--workflow=push-images.yml",
        "--limit", str(max_runs),
        "--json", "databaseId,status,conclusion,createdAt,displayTitle",
    ])


def list_failed_jobs(run_id: int) -> list[dict]:
    """Return jobs with failure conclusion for a run."""
    data = gh_json(["run", "view", str(run_id), "--json", "jobs"])
    return [j for j in (data.get("jobs") or []) if j.get("conclusion") == "failure"]


def find_task_name_in_log(log_text: str) -> str | None:
    """Identify the task name from a job log by matching common build patterns.

    push_images.py builds with names like
        ghcr.io/findalexli/agentsmd-rl/<task>:<tag>
    so we grep for that.
    """
    m = re.search(r"agentsmd-rl/([\w._-]+):", log_text)
    if m: return m.group(1)
    # Try matrix-input pattern: 'task: <name>' in the early log
    m = re.search(r"^\s*task[:\s]+([\w._-]+)\s*$", log_text, re.M)
    if m: return m.group(1)
    return None


def fetch_job_log(run_id: int, job_id: int) -> str:
    """Download the log for a specific failed job (text, last ~5000 lines)."""
    r = subprocess.run(
        ["gh", "api", f"repos/findalexli/agentsmd-rl/actions/jobs/{job_id}/logs",
         "--method", "GET"],
        capture_output=True, text=True, timeout=60,
    )
    return r.stdout if r.returncode == 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-runs", type=int, default=5)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--task-dir", default="markdown_following")
    args = ap.parse_args()

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir or f"pipeline_logs/dockerfile_fix_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Listing recent push-images.yml runs (limit {args.max_runs})...", file=sys.stderr)
    runs = list_recent_runs(args.max_runs)
    discovery: list[dict] = []
    seen_tasks: set[str] = set()

    for run in runs:
        run_id = run["databaseId"]
        if run.get("conclusion") not in (None, "failure"):
            continue
        try:
            failed = list_failed_jobs(run_id)
        except RuntimeError as e:
            print(f"  run {run_id}: failed to list jobs ({e})", file=sys.stderr)
            continue
        if not failed: continue
        print(f"  run {run_id}: {len(failed)} failed jobs", file=sys.stderr)

        for job in failed:
            job_id = job["databaseId"]
            try:
                log = fetch_job_log(run_id, job_id)
            except Exception as e:
                print(f"    job {job_id}: log fetch error: {e}", file=sys.stderr)
                continue

            task = find_task_name_in_log(log) or job.get("name", "")
            if not task or task in seen_tasks: continue
            seen_tasks.add(task)

            task_path = ROOT / args.task_dir / task
            if not (task_path / "environment" / "Dockerfile").exists():
                print(f"    skip {task}: no local task dir or Dockerfile", file=sys.stderr)
                continue

            # Find the most useful error block, not just trailing GHA cleanup.
            # Strategy:
            #   1. Look for the first occurrence of "##[error]" / "ERROR " /
            #      "exit code [1-9]" / "Error: " / "FATAL" — that's the real failure
            #   2. Capture 60 lines BEFORE and 30 AFTER (build context + error)
            #   3. If nothing found, fall back to last 80 lines minus any trailing
            #      "Post job cleanup"/"Removing builder"/"Logout" boilerplate
            lines = log.splitlines()
            error_idx = None
            for i, line in enumerate(lines):
                if re.search(r"(##\[error\]|^ERROR\s|exit code [1-9]|^Error: |FATAL|"
                             r"Step failed|process completed with exit code [1-9]|"
                             r"Building image \S+ failed|Failed to)", line):
                    error_idx = i
                    break
            if error_idx is not None:
                start = max(0, error_idx - 60)
                end = min(len(lines), error_idx + 30)
                fail_tail = "\n".join(lines[start:end])[-6000:]
            else:
                # Strip GHA cleanup trailers
                tail_lines = []
                CLEANUP_PAT = re.compile(r"Post job cleanup|Removing builder|Logout|"
                                          r"Cleaning up|##\[group\]|##\[endgroup\]")
                for ln in lines[-200:]:
                    if not CLEANUP_PAT.search(ln):
                        tail_lines.append(ln)
                fail_tail = "\n".join(tail_lines[-100:])[-6000:]
            (task_path / "_failure.log").write_text(fail_tail)
            discovery.append({
                "task": task, "run_id": run_id, "job_id": job_id,
                "job_name": job.get("name", ""), "tail_chars": len(fail_tail),
            })

    # Write discovery + input JSONL
    (out_dir / "discovery.json").write_text(json.dumps(discovery, indent=2))
    inp = out_dir / "input.jsonl"
    with inp.open("w") as f:
        for d in discovery:
            f.write(json.dumps({"task_ref": d["task"]}) + "\n")

    print(f"\nFound {len(discovery)} broken Dockerfiles", file=sys.stderr)
    print(f"  → {inp}", file=sys.stderr)
    print(f"  → discovery.json: {out_dir/'discovery.json'}", file=sys.stderr)
    print(f"  → _failure.log written under each markdown_following/<task>/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
