#!/usr/bin/env python3
"""Find tier-A harbor tasks WITHOUT a ghcr image (i.e., push failed or never ran).

For each tier-A task (status=pass, no quality fails), probe whether
ghcr.io/findalexli/agentsmd-rl/<task>:latest exists. If not, treat as broken.

Output:
  pipeline_logs/dockerfile_fix_<ts>/input.jsonl     — { "task_ref": "<name>" } per line
  pipeline_logs/dockerfile_fix_<ts>/missing.txt     — bare task names

Optional: writes `harbor_tasks/<task>/_failure.log` with the docker build
output captured locally (probes the Dockerfile to surface the actual error).
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


async def _has_ghcr_image(name: str) -> bool:
    p = await asyncio.create_subprocess_exec(
        "docker", "manifest", "inspect", f"ghcr.io/findalexli/agentsmd-rl/{name}",
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
    )
    rc = await p.wait()
    return rc == 0


async def _try_local_build(name: str, timeout: int = 600) -> tuple[bool, str]:
    """Attempt a local docker build of the task's environment to capture the
    real error message. Returns (success, captured_log_tail)."""
    df = ROOT / "harbor_tasks" / name / "environment"
    if not (df / "Dockerfile").exists():
        return False, "no Dockerfile"
    p = await asyncio.create_subprocess_exec(
        "docker", "build", "-t", f"local-test-{name[:30].lower()}",
        str(df),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(p.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        p.kill(); await p.wait()
        return False, "TIMEOUT"
    text = out.decode("utf-8", errors="replace") if out else ""
    return p.returncode == 0, text[-6000:]


def is_tier_a(task_dir: Path) -> bool:
    sj = task_dir / "status.json"
    if not sj.exists(): return False
    try:
        d = json.loads(sj.read_text())
        if d.get("verdict") != "pass": return False
    except Exception: return False
    qj = task_dir / "quality.json"
    if qj.exists():
        try:
            q = json.loads(qj.read_text())
            if any(f.get("tier") in ("A", "B") for f in (q.get("fails", []) or [])):
                return False
        except Exception: pass
    return True


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks")
    ap.add_argument("--probe-build", action="store_true",
                    help="Run docker build locally for each missing task to capture real error (slow)")
    ap.add_argument("--build-timeout", type=int, default=300)
    ap.add_argument("--max-probes", type=int, default=20,
                    help="Max parallel docker build probes (--probe-build)")
    args = ap.parse_args()

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"pipeline_logs/dockerfile_fix_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1 — enumerate tier-A tasks + parallel manifest-inspect
    candidates = []
    for d in sorted((ROOT / args.task_dir).iterdir()):
        if d.is_dir() and is_tier_a(d):
            candidates.append(d.name)
    print(f"Tier-A tasks: {len(candidates)}", file=sys.stderr)

    sem = asyncio.Semaphore(20)
    async def check(n):
        async with sem:
            return n, await _has_ghcr_image(n)
    results = await asyncio.gather(*[check(n) for n in candidates])
    missing = [n for n, ok in results if not ok]
    print(f"Missing ghcr image: {len(missing)} of {len(candidates)} ({100*len(missing)/max(1,len(candidates)):.1f}%)",
          file=sys.stderr)

    # Phase 2 — optionally probe local docker build to capture real errors
    if args.probe_build and missing:
        print(f"Probing local builds (cap {args.max_probes} concurrent, {args.build_timeout}s timeout each)...",
              file=sys.stderr)
        probe_sem = asyncio.Semaphore(args.max_probes)
        async def probe(n):
            async with probe_sem:
                ok, log = await _try_local_build(n, args.build_timeout)
                return n, ok, log
        probes = await asyncio.gather(*[probe(n) for n in missing])
        for n, ok, log in probes:
            (ROOT / args.task_dir / n / "_failure.log").write_text(log)
            print(f"  {'OK' if ok else 'FAIL':4s}  {n}", file=sys.stderr)
        actually_failing = [n for n, ok, _ in probes if not ok]
        print(f"Local docker build fails on {len(actually_failing)}/{len(missing)}", file=sys.stderr)
        missing = actually_failing  # keep only ones still broken

    # Output
    (out_dir / "missing.txt").write_text("\n".join(missing) + "\n")
    with (out_dir / "input.jsonl").open("w") as f:
        for n in missing:
            f.write(json.dumps({"task_ref": n}) + "\n")
    print(f"\n→ {out_dir/'input.jsonl'}  ({len(missing)} tasks)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
