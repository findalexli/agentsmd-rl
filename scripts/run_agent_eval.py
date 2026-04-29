#!/usr/bin/env python3
"""Clean agent eval runner: harbor + claude-code + 3-track scoring.

Runs N harbor tasks in parallel through claude-code (E2B or docker),
pointed at DeepSeek's Anthropic-compatible endpoint.
After each trial:
  - Track 1 (programmatic): reward.txt from test.sh
  - Track 3 (rubric):        judge.py against eval_manifest.yaml + agent.diff
  - Track 4 (distractors):   distractor_judge.py against eval_manifest.yaml + agent.diff

Shadow-copies each task to a scratch dir and prepends a diff-capture hook
to tests/test.sh so the agent's diff is written to /logs/verifier/agent.diff.

Usage:
    .venv/bin/python scripts/run_agent_eval.py \\
        --tasks pipeline_logs/eval/tasks.txt \\
        --out   pipeline_logs/eval/results.jsonl \\
        --concurrency 4 \\
        --backend deepseek \\
        --env e2b

Backend: deepseek
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"
SCRATCH_DIR = Path(os.environ.get("EVAL_SCRATCH_DIR", "/tmp/agent_eval_tasks"))

DIFF_CAPTURE_SNIPPET = r"""
# --- agent_eval: capture diff BEFORE tests may mutate repo ---
mkdir -p /logs/verifier
: > /logs/verifier/agent.diff
_agent_eval_found=""
for candidate in /workspace/*/ /repo /app /src; do
    if [ -d "${candidate}/.git" ]; then
        _agent_eval_found="$candidate"
        break
    fi
done
if [ -z "$_agent_eval_found" ]; then
    _agent_eval_found=$(find /workspace /repo /app /src -maxdepth 3 -type d -name .git 2>/dev/null | head -1 | xargs -r dirname)
fi
if [ -n "$_agent_eval_found" ] && [ -d "$_agent_eval_found/.git" ]; then
    (cd "$_agent_eval_found" \
     && git add -A 2>/dev/null \
     && git diff --cached > /logs/verifier/agent.diff 2>/dev/null) || true
fi
# --- end agent_eval ---

"""


def load_env() -> dict[str, str]:
    env = {}
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


BACKEND_CFG = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/anthropic",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-v4-pro[1m]",
    },
}


@dataclass
class TrialResult:
    task: str
    ok: bool
    track1_reward: float = 0.0       # programmatic tests
    track3_rubric: float = 0.0       # rubric ICR
    track4_distractors: float = 0.0  # distractor ignore rate
    track3_passed: int = 0
    track3_total: int = 0
    track4_passed: int = 0
    track4_total: int = 0
    agent_wrote_diff: bool = False
    error: str = ""
    elapsed_s: float = 0.0
    job_dir: str = ""


def shadow_copy_task(task: str, scratch_root: Path | None = None,
                     backend_label: str = "") -> Path:
    root = scratch_root or SCRATCH_DIR
    src = HARBOR_TASKS / task
    dst = root / task
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    test_sh = dst / "tests" / "test.sh"
    original = test_sh.read_text()
    lines = original.splitlines(keepends=True)
    if lines and lines[0].startswith("#!"):
        out = [lines[0], DIFF_CAPTURE_SNIPPET] + lines[1:]
    else:
        out = ["#!/usr/bin/env bash\n", DIFF_CAPTURE_SNIPPET] + lines
    test_sh.write_text("".join(out))
    # When multiple eval backends run in parallel on the same task, they
    # would collide on the E2B template hash (Dockerfile identical → same
    # hash → E2B cancels all but first builder). Append a LABEL that varies
    # per backend so each gets its own template.
    if backend_label:
        df = dst / "environment" / "Dockerfile"
        if df.exists():
            df.write_text(df.read_text().rstrip() + f"\nLABEL eval_backend=\"{backend_label}\"\n")
    return dst


def _find_job_result(job_dir: Path) -> tuple[float, Path]:
    """Return (reward, trial_dir)."""
    if not job_dir.exists():
        return 0.0, job_dir
    # Trial dirs look like <task>__XXX
    trial_dirs = [d for d in job_dir.iterdir() if d.is_dir() and "__" in d.name]
    if not trial_dirs:
        return 0.0, job_dir
    trial = trial_dirs[0]
    reward_file = trial / "verifier" / "reward.txt"
    if reward_file.exists():
        try:
            return float(reward_file.read_text().strip()), trial
        except ValueError:
            return 0.0, trial
    return 0.0, trial


async def run_harbor(
    task_path: Path,
    job_name: str,
    job_dir: Path,
    env_type: str,
    backend_cfg: dict,
    api_key: str,
    timeout_s: int = 1800,
) -> tuple[int, str]:
    """Run `harbor run` for one task. Returns (exit_code, stderr_tail)."""
    agent_env = [
        ("ANTHROPIC_API_KEY", api_key),
        ("ANTHROPIC_AUTH_TOKEN", api_key),
        ("ANTHROPIC_MODEL", backend_cfg["model"]),
        ("ANTHROPIC_SMALL_FAST_MODEL", backend_cfg["model"]),
        ("ANTHROPIC_DEFAULT_OPUS_MODEL", backend_cfg["model"]),
        ("ANTHROPIC_DEFAULT_SONNET_MODEL", backend_cfg["model"]),
        ("ANTHROPIC_DEFAULT_HAIKU_MODEL", backend_cfg["model"]),
    ]
    # Judges run against the same DeepSeek endpoint as the agent.
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "") or api_key
    if deepseek_key:
        agent_env.append(("DEEPSEEK_API_KEY", deepseek_key))
    if backend_cfg["base_url"]:
        agent_env.insert(0, ("ANTHROPIC_BASE_URL", backend_cfg["base_url"]))

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "-a", "claude-code",
        "-m", backend_cfg["model"],
        "-k", "1",
        "-e", env_type,
        "--job-name", job_name,
        "-o", str(job_dir.parent),
        "--verifier-timeout-multiplier", "5",
        "--timeout-multiplier", "2",
        "--force-build",
        "-y",
    ]
    for k, v in agent_env:
        cmd.extend(["--ae", f"{k}={v}"])

    log_file = job_dir.parent / f"{job_name}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w") as lf:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT),
            stdout=lf,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ},
        )
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout_s)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return 124, "TIMEOUT"
    tail = ""
    if log_file.exists():
        text = log_file.read_text()[-2000:]
        tail = text
    return proc.returncode or 0, tail


async def score_trial(task: str, trial_dir: Path, env: dict[str, str]) -> tuple[dict, dict]:
    """Run Track 3 (rubric) + Track 4 (distractors) judges on the trial dir.

    Returns (rubric_info, distractor_info):
      rubric_info = {score, passed, total}
      distractor_info = {score, passed, total}
    """
    diff_path = trial_dir / "verifier" / "agent.diff"
    manifest_path = HARBOR_TASKS / task / "eval_manifest.yaml"

    default = (
        {"score": 0.0, "passed": 0, "total": 0},
        {"score": 0.0, "passed": 0, "total": 0},
    )
    if not diff_path.exists() or diff_path.stat().st_size == 0:
        return default
    if not manifest_path.exists():
        return default

    # Load judges inline
    sys.path.insert(0, str(ROOT))
    try:
        from taskforge.judge import load_manifest_rubric, call_judge
        from taskforge.distractor_judge import load_manifest_distractors, judge_distractors
    except Exception as e:
        print(f"  [score_trial] import failed: {e}", file=sys.stderr)
        return default

    diff = diff_path.read_text()
    deepseek_key = env.get("DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
    os.environ["DEEPSEEK_API_KEY"] = deepseek_key  # judges read from env

    # Track 3
    rubric_info = {"score": 0.0, "passed": 0, "total": 0}
    rules = load_manifest_rubric(str(manifest_path))
    if rules:
        try:
            results = await asyncio.to_thread(call_judge, rules, diff, deepseek_key)
            if results:
                p = sum(1 for r in results if r.get("pass", False))
                rubric_info = {
                    "score": p / len(results),
                    "passed": p,
                    "total": len(results),
                }
        except Exception as e:
            print(f"  [score_trial] rubric judge error for {task}: {e}", file=sys.stderr)

    # Track 4
    distractor_info = {"score": 0.0, "passed": 0, "total": 0}
    distractors = load_manifest_distractors(str(manifest_path))
    if distractors:
        try:
            score, results = await asyncio.to_thread(
                judge_distractors, distractors, diff, deepseek_key
            )
            p = sum(1 for r in results if not r.get("applied", False))
            distractor_info = {
                "score": score,
                "passed": p,
                "total": len(distractors),
            }
        except Exception as e:
            print(f"  [score_trial] distractor judge error for {task}: {e}", file=sys.stderr)

    return rubric_info, distractor_info


async def run_one(
    task: str,
    run_id: str,
    env_type: str,
    backend: str,
    backend_cfg: dict,
    api_key: str,
    env: dict[str, str],
    timeout_s: int,
    sem: asyncio.Semaphore,
    out_file,
    log_prefix: Path,
) -> TrialResult:
    t0 = time.time()
    async with sem:
        print(f"[{time.strftime('%H:%M:%S')}] START {task} ({backend})")
        result = TrialResult(task=task, ok=False)
        try:
            task_path = shadow_copy_task(
                task,
                scratch_root=SCRATCH_DIR,
                backend_label=backend,
            )
            job_name = f"{run_id}-{task}"
            job_dir = log_prefix / job_name
            rc, tail = await run_harbor(
                task_path=task_path,
                job_name=job_name,
                job_dir=job_dir,
                env_type=env_type,
                backend_cfg=backend_cfg,
                api_key=api_key,
                timeout_s=timeout_s,
            )
            reward, trial_dir = _find_job_result(job_dir)
            result.track1_reward = reward
            result.job_dir = str(job_dir)
            diff_path = trial_dir / "verifier" / "agent.diff"
            result.agent_wrote_diff = diff_path.exists() and diff_path.stat().st_size > 0

            rubric_info, distractor_info = await score_trial(task, trial_dir, env)
            result.track3_rubric = rubric_info["score"]
            result.track3_passed = rubric_info["passed"]
            result.track3_total = rubric_info["total"]
            result.track4_distractors = distractor_info["score"]
            result.track4_passed = distractor_info["passed"]
            result.track4_total = distractor_info["total"]

            result.ok = rc == 0
            if rc != 0:
                result.error = f"harbor rc={rc} tail={tail[-300:]}"
        except Exception as e:
            result.error = f"{type(e).__name__}: {e}"
        result.elapsed_s = round(time.time() - t0, 1)
        print(
            f"[{time.strftime('%H:%M:%S')}] DONE  {task}: "
            f"T1={result.track1_reward:.0f} "
            f"T3={result.track3_passed}/{result.track3_total} "
            f"T4={result.track4_passed}/{result.track4_total} "
            f"({result.elapsed_s}s) err={result.error[:80]}"
        )
        out_file.write(json.dumps(asdict(result)) + "\n")
        out_file.flush()
        return result


def summarize(results: list[TrialResult]) -> dict:
    n = len(results)
    t1_pass = sum(1 for r in results if r.track1_reward >= 1.0)
    t3_rules = sum(r.track3_total for r in results)
    t3_pass = sum(r.track3_passed for r in results)
    t4_rules = sum(r.track4_total for r in results)
    t4_pass = sum(r.track4_passed for r in results)
    diff_written = sum(1 for r in results if r.agent_wrote_diff)

    return {
        "n_tasks": n,
        "track1_programmatic_pass": t1_pass,
        "track1_rate": (t1_pass / n if n else 0.0),
        "track3_rubric_passed": t3_pass,
        "track3_rubric_total": t3_rules,
        "track3_rate": (t3_pass / t3_rules if t3_rules else 0.0),
        "track4_distractor_ignored": t4_pass,
        "track4_distractor_total": t4_rules,
        "track4_rate": (t4_pass / t4_rules if t4_rules else 0.0),
        "diff_written": diff_written,
    }


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tasks", required=True, help="Path to tasks.txt (one task per line)")
    p.add_argument("--out", required=True, help="Output JSONL path")
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--backend", choices=["deepseek"], default="deepseek")
    p.add_argument("--env", choices=["e2b", "docker"], default="e2b")
    p.add_argument("--timeout", type=int, default=1800, help="Per-task timeout in seconds")
    p.add_argument("--run-id", default=None)
    p.add_argument("--pin-claude-version", default="2.1.119",
                   help="Assert claude-code CLI is exactly this version. Pass '' to skip.")
    args = p.parse_args()

    # Pin claude-code version so reruns are reproducible and multi-backend
    # comparisons share an agent framework. Skippable via --pin-claude-version=''.
    if args.pin_claude_version:
        try:
            cc_out = subprocess.run(
                ["claude", "--version"], capture_output=True, text=True, timeout=10
            ).stdout.strip()
        except Exception as e:
            sys.exit(f"Could not run `claude --version`: {e}")
        if args.pin_claude_version not in cc_out:
            sys.exit(
                f"claude-code version mismatch: expected {args.pin_claude_version}, "
                f"got {cc_out!r}. Run `claude update` or pass --pin-claude-version=''."
            )
        print(f"  claude_code_version={cc_out}")

    env = load_env()
    cfg = BACKEND_CFG[args.backend]
    api_key = env.get(cfg["api_key_env"], "") or os.environ.get(cfg["api_key_env"], "")
    if not api_key:
        sys.exit(f"Missing {cfg['api_key_env']}")

    tasks = [t.strip() for t in Path(args.tasks).read_text().splitlines() if t.strip()]
    if not tasks:
        sys.exit("No tasks loaded")

    run_id = args.run_id or f"ae-{args.backend}-{time.strftime('%Y%m%d-%H%M%S')}"
    log_prefix = Path("pipeline_logs") / run_id
    log_prefix.mkdir(parents=True, exist_ok=True)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    # Also propagate E2B_API_KEY to subprocess env
    for k in ("E2B_API_KEY", "DEEPSEEK_API_KEY"):
        if k in env and not os.environ.get(k):
            os.environ[k] = env[k]

    # NOTE: not calling cleanup_orphan_sandboxes — it would kill sandboxes
    # owned by other running pipelines (e.g. overnight scaffold workers).

    print(f"run_id={run_id} backend={args.backend} env={args.env} n_tasks={len(tasks)} conc={args.concurrency}")
    print(f"  model={cfg['model']} base_url={cfg['base_url']}")
    print(f"  logs: {log_prefix}/")

    sem = asyncio.Semaphore(args.concurrency)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as out_file:
        coros = [
            run_one(
                task=t,
                run_id=run_id,
                env_type=args.env,
                backend=args.backend,
                backend_cfg=cfg,
                api_key=api_key,
                env=env,
                timeout_s=args.timeout,
                sem=sem,
                out_file=out_file,
                log_prefix=log_prefix,
            )
            for t in tasks
        ]
        results = await asyncio.gather(*coros, return_exceptions=False)

    summary = summarize(results)
    summary["backend"] = args.backend
    summary["model"] = cfg["model"]
    summary["base_url"] = cfg["base_url"]
    if args.pin_claude_version:
        summary["claude_code_version"] = args.pin_claude_version
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2))
    print("\n━━━ SUMMARY ━━━")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"\nResults: {out_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
