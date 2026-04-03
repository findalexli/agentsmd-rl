#!/usr/bin/env python3
"""Re-validate 42 tasks that timed out at 300s, using 600s timeout."""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

BASE = Path("/home/alex/agentsmd-rl")
TIMEOUT = 600
WORKERS = 3

print_lock = Lock()
progress_lock = Lock()
completed_count = 0
results_summary = []


def log(msg):
    with print_lock:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def run_cmd(cmd, timeout=TIMEOUT):
    """Run a command, return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


def read_reward(path):
    """Read reward.txt, return the string value or None."""
    try:
        return Path(path).read_text().strip()
    except Exception:
        return None


def update_status(task, entry):
    """Append a validation entry to status.json."""
    status_path = BASE / "harbor_tasks" / task / "status.json"
    if status_path.exists():
        data = json.loads(status_path.read_text())
    else:
        data = {"validations": []}
    if "validations" not in data:
        data["validations"] = []
    data["validations"].append(entry)
    status_path.write_text(json.dumps(data, indent=2) + "\n")


def cleanup_docker(task):
    """Remove docker image to save disk."""
    img = f"harbor-{task}:latest"
    subprocess.run(f"docker rmi -f {img}", shell=True, capture_output=True, timeout=60)


def validate_task(task):
    global completed_count
    task_dir = BASE / "harbor_tasks" / task
    if not task_dir.exists():
        log(f"SKIP {task} — directory not found")
        return task, "skip", "dir_not_found"

    img = f"harbor-{task}:latest"
    env_dir = task_dir / "environment"
    tests_dir = task_dir / "tests"
    solution_dir = task_dir / "solution"

    nop_dir = f"/tmp/nop_{task}"
    gold_dir = f"/tmp/gold_{task}"

    # Clean up any leftover tmp dirs
    for d in [nop_dir, gold_dir]:
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # Phase 1: Build
    log(f"BUILD {task}")
    rc, out, err = run_cmd(f"docker build -q -t {img} {env_dir}/", timeout=TIMEOUT)
    if rc != 0:
        verdict = "fail_build"
        log(f"FAIL_BUILD {task}: {err[:200]}")
        update_status(task, {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "local_docker_retry",
            "runner": "local_600s",
            "verdict": verdict,
            "nop": None,
            "gold": None,
            "notes": f"build failed: {err[:300]}"
        })
        cleanup_docker(task)
        with progress_lock:
            completed_count += 1
            results_summary.append((task, verdict))
            if completed_count % 5 == 0:
                log(f"=== PROGRESS: {completed_count}/42 completed ===")
        return task, verdict, err[:200]

    # Phase 2: Nop test
    log(f"NOP   {task}")
    nop_cmd = (
        f"docker run --rm "
        f"-v {tests_dir}:/tests "
        f"-v {nop_dir}:/logs/verifier "
        f"{img} bash -c "
        f"'mkdir -p /logs/verifier && chmod +x /tests/test.sh && /tests/test.sh'"
    )
    rc_nop, _, err_nop = run_cmd(nop_cmd, timeout=TIMEOUT)
    nop_reward = read_reward(f"{nop_dir}/reward.txt")
    if rc_nop == -1:
        log(f"NOP_TIMEOUT {task}")

    # Phase 3: Gold test
    log(f"GOLD  {task}")
    gold_cmd = (
        f"docker run --rm "
        f"-v {tests_dir}:/tests "
        f"-v {solution_dir}:/solution "
        f"-v {gold_dir}:/logs/verifier "
        f"{img} bash -c "
        f"'mkdir -p /logs/verifier && chmod +x /tests/test.sh /solution/solve.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh'"
    )
    rc_gold, _, err_gold = run_cmd(gold_cmd, timeout=TIMEOUT)
    gold_reward = read_reward(f"{gold_dir}/reward.txt")
    if rc_gold == -1:
        log(f"GOLD_TIMEOUT {task}")

    # Determine verdict
    nop_ok = nop_reward == "0"
    gold_ok = gold_reward == "1"

    if nop_ok and gold_ok:
        verdict = "pass"
    elif rc_nop == -1 or rc_gold == -1:
        verdict = "timeout_600s"
    elif not gold_ok:
        verdict = "fail_gold"
    else:
        verdict = "fail_nop"

    notes_parts = []
    if rc_nop == -1:
        notes_parts.append("nop_timeout")
    if rc_gold == -1:
        notes_parts.append("gold_timeout")

    log(f"{'PASS' if verdict == 'pass' else 'FAIL'} {task} nop={nop_reward} gold={gold_reward} verdict={verdict}")

    update_status(task, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": "local_docker_retry",
        "runner": "local_600s",
        "verdict": verdict,
        "nop": nop_reward,
        "gold": gold_reward,
        "notes": "; ".join(notes_parts) if notes_parts else ""
    })

    # Cleanup
    cleanup_docker(task)
    shutil.rmtree(nop_dir, ignore_errors=True)
    shutil.rmtree(gold_dir, ignore_errors=True)

    with progress_lock:
        completed_count += 1
        results_summary.append((task, verdict))
        if completed_count % 5 == 0:
            log(f"=== PROGRESS: {completed_count}/42 completed ===")

    return task, verdict, f"nop={nop_reward} gold={gold_reward}"


def main():
    task_file = Path("/tmp/local_timeout_tasks.txt")
    tasks = [l.strip() for l in task_file.read_text().splitlines() if l.strip()]
    log(f"Loaded {len(tasks)} tasks for retry with {TIMEOUT}s timeout, {WORKERS} workers")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(validate_task, t): t for t in tasks}
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                task = futures[f]
                log(f"EXCEPTION {task}: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    verdicts = {}
    for task, verdict in results_summary:
        verdicts.setdefault(verdict, []).append(task)
    for v, tasks_list in sorted(verdicts.items()):
        print(f"\n{v} ({len(tasks_list)}):")
        for t in sorted(tasks_list):
            print(f"  {t}")
    print(f"\nTotal: {len(results_summary)}/42")


if __name__ == "__main__":
    main()
