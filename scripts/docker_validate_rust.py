#!/usr/bin/env python3
"""Docker validation for rust/cargo tasks with 900s build timeout and 3 workers."""

import json
import subprocess
import os
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

BASE = Path("/home/alex/agentsmd-rl")
HARBOR = BASE / "harbor_tasks"
BUILD_TIMEOUT = 900
RUN_TIMEOUT = 600
PHASE = "local_docker_rust"
RUNNER = "local_900s"

file_locks: dict[str, Lock] = {}
global_lock = Lock()


def get_file_lock(path: str) -> Lock:
    with global_lock:
        if path not in file_locks:
            file_locks[path] = Lock()
        return file_locks[path]


def update_status(task: str, entry: dict):
    status_path = HARBOR / task / "status.json"
    lock = get_file_lock(str(status_path))
    with lock:
        if status_path.exists():
            data = json.loads(status_path.read_text())
        else:
            data = {"validations": []}
        if "validations" not in data:
            data["validations"] = []
        data["validations"].append(entry)
        status_path.write_text(json.dumps(data, indent=2) + "\n")


def run_cmd(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    except Exception as e:
        return -2, str(e)


def read_reward(tmp_dir: str) -> str | None:
    reward_file = os.path.join(tmp_dir, "reward.txt")
    if os.path.exists(reward_file):
        return open(reward_file).read().strip()
    return None


def validate_task(task: str) -> dict:
    task_dir = HARBOR / task
    env_dir = task_dir / "environment"
    image_tag = f"harbor-rust-{task}:latest"
    abs_task = str(task_dir)

    print(f"[BUILD] {task}")

    # Build
    rc, out = run_cmd(["docker", "build", "-q", "-t", image_tag, str(env_dir)], timeout=BUILD_TIMEOUT)
    if rc != 0:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": PHASE,
            "runner": RUNNER,
            "format": "pytest_binary",
            "verdict": "fail_build",
            "nop": None,
            "gold": None,
            "notes": out[-300:]
        }
        update_status(task, entry)
        print(f"[FAIL_BUILD] {task}: {out[-200:]}")
        return {"task": task, "verdict": "fail_build"}

    # Nop test
    nop_tmp = f"/tmp/nop_{task}"
    os.makedirs(nop_tmp, exist_ok=True)
    print(f"[NOP] {task}")

    rc, out = run_cmd([
        "docker", "run", "--rm",
        "-v", f"{abs_task}/tests:/tests",
        "-v", f"{nop_tmp}:/logs/verifier",
        image_tag,
        "bash", "-c",
        "mkdir -p /logs/verifier && chmod +x /tests/test.sh && /tests/test.sh"
    ], timeout=RUN_TIMEOUT)

    nop_reward = read_reward(nop_tmp)
    shutil.rmtree(nop_tmp, ignore_errors=True)

    if nop_reward != "0":
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": PHASE,
            "runner": RUNNER,
            "format": "pytest_binary",
            "verdict": "fail",
            "nop": nop_reward,
            "gold": None,
            "notes": f"nop expected 0 got {nop_reward}; {out[-200:]}"
        }
        update_status(task, entry)
        subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)
        print(f"[FAIL_NOP] {task}: nop={nop_reward}")
        return {"task": task, "verdict": "fail", "nop": nop_reward}

    # Gold test
    gold_tmp = f"/tmp/gold_{task}"
    os.makedirs(gold_tmp, exist_ok=True)
    print(f"[GOLD] {task}")

    rc, out = run_cmd([
        "docker", "run", "--rm",
        "-v", f"{abs_task}/tests:/tests",
        "-v", f"{abs_task}/solution:/solution",
        "-v", f"{gold_tmp}:/logs/verifier",
        image_tag,
        "bash", "-c",
        "mkdir -p /logs/verifier && chmod +x /tests/test.sh /solution/solve.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh"
    ], timeout=RUN_TIMEOUT)

    gold_reward = read_reward(gold_tmp)
    shutil.rmtree(gold_tmp, ignore_errors=True)

    if nop_reward == "0" and gold_reward == "1":
        verdict = "pass"
    else:
        verdict = "fail"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": PHASE,
        "runner": RUNNER,
        "format": "pytest_binary",
        "verdict": verdict,
        "nop": nop_reward,
        "gold": gold_reward,
        "notes": "" if verdict == "pass" else out[-300:]
    }
    update_status(task, entry)

    # Cleanup
    subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)
    print(f"[{verdict.upper()}] {task}: nop={nop_reward} gold={gold_reward}")
    return {"task": task, "verdict": verdict, "nop": nop_reward, "gold": gold_reward}


def main():
    task_file = "/tmp/rust_tasks.txt"
    tasks = [l.strip() for l in open(task_file) if l.strip()]
    print(f"Validating {len(tasks)} rust tasks with {BUILD_TIMEOUT}s build timeout, 3 workers\n")

    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(validate_task, t): t for t in tasks}
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                task = futures[f]
                print(f"[ERROR] {task}: {e}")
                results.append({"task": task, "verdict": "error"})

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    counts = {}
    for r in results:
        v = r["verdict"]
        counts[v] = counts.get(v, 0) + 1
    for v, c in sorted(counts.items()):
        print(f"  {v}: {c}")
    print(f"  total: {len(results)}")

    # Details
    for r in sorted(results, key=lambda x: x["verdict"]):
        print(f"  {r['verdict']:12s} {r['task']}")


if __name__ == "__main__":
    main()
