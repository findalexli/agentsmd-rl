#!/usr/bin/env python3
"""Run execution-based fail-to-pass mining across many harbor tasks.

For each task:
  - Pick the upstream test command from CI mining cache
  - Boot an E2B sandbox with docker available
  - Run the dual-pass: base test → apply solve.sh → gold test
  - Parse both logs (per-framework via taskforge.exec_log_parsers)
  - Compute f2p / p2p delta
  - Generate one pytest function per discovered f2p test
  - Append a `# === Execution-mined f2p ===` section to test_outputs.py
  - Add manifest checks (origin: exec_diff)

This is the SWE-rebench V2 / SWE-bench approach to f2p extraction:
execution-based, not patch-parse-based — captures every test that flips
fail→pass, including pre-existing tests in modified suites.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import logging
import os
import re
import shutil
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from taskforge.exec_f2p_miner import (
    pick_test_command, pick_setup_and_test_commands, run_dual_pass, ExecResult,
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("exec_f2p")

CACHE_DIR = ROOT / "pipeline_logs" / "exec_f2p_cache"
SECTION_MARKER = "# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ==="


import hashlib

REGISTRY = "ghcr.io"
OWNER = os.environ.get("GH_OWNER", "findalexli")
REPO_NAME = "agentsmd-rl"


def _sanitize_image_name(name: str) -> str:
    """Match scripts/push_images.py:sanitize_name."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9._-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name


def task_image_tag(task_dir: Path) -> str | None:
    """Read task.toml's docker_image field, or compute the canonical tag from
    the Dockerfile's sha256 hash (matches scripts/push_images.py convention)."""
    tt = task_dir / "task.toml"
    if tt.exists():
        m = re.search(r'docker_image\s*=\s*"([^"]+)"', tt.read_text())
        if m: return m.group(1)
    # Fallback: derive from Dockerfile hash
    df = task_dir / "environment" / "Dockerfile"
    if not df.exists(): return None
    sha12 = hashlib.sha256(df.read_bytes()).hexdigest()[:12]
    return f"{REGISTRY}/{OWNER}/{REPO_NAME}/{_sanitize_image_name(task_dir.name)}:{sha12}"


def read_solve_sh(task_dir: Path) -> str | None:
    p = task_dir / "solution" / "solve.sh"
    if not p.exists(): return None
    return p.read_text()


def read_ci_spec(task_name: str) -> dict | None:
    """Find the cached CI spec JSON for this task."""
    matches = sorted(Path(ROOT / "pipeline_logs" / "ci_miner_cache").glob(f"{task_name}__*.json"))
    if not matches: return None
    try:
        return json.loads(matches[0].read_text())
    except Exception:
        return None


def safe_id(name: str) -> str:
    """Convert a test name (potentially path-style) into a valid Python identifier."""
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_").lower()
    if not s or not s[0].isalpha():
        s = "x_" + s if s else "x"
    return s[:80]  # cap length


def _emit_test_fns(prefix: str, names: list[str], description: str) -> tuple[str, set[str]]:
    """Return (block_text, set_of_function_ids_used)."""
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        sid = safe_id(name)
        orig = sid; n = 1
        while sid in seen:
            n += 1; sid = f"{orig}_{n}"
        seen.add(sid)
        out.extend([
            f"def test_exec_{prefix}_{sid}(_run_cmd=None):",
            f"    # {description}: {name!r}",
            f"    pass  # placeholder — recorded in manifest under origin: exec_diff",
            "",
        ])
    return ("\n".join(out) + "\n" if out else "", seen)


def generate_test_block(task_name: str, test_cmd: str,
                        f2p_names: list[str], p2p_names: list[str]) -> str:
    """Generate pytest functions for both f2p and p2p discovered tests."""
    if not f2p_names and not p2p_names: return ""
    lines = [
        SECTION_MARKER,
        f"# Source: dual-pass exec at base vs gold inside the task's docker image",
        f"# Test command: {test_cmd[:120]}",
        f"# {len(f2p_names)} fail→pass + {len(p2p_names)} pass→pass test name(s) discovered.",
        "",
    ]
    f2p_block, _ = _emit_test_fns("f2p", f2p_names, "Discovered f2p (failed at base, passed at gold)")
    p2p_block, _ = _emit_test_fns("p2p", p2p_names, "Discovered p2p (passed at both base and gold)")
    if f2p_block: lines.append(f2p_block)
    if p2p_block: lines.append(p2p_block)
    return "\n".join(lines)


def generate_manifest_entries(task_name: str, f2p_names: list[str],
                                p2p_names: list[str], test_cmd: str) -> list[dict]:
    out: list[dict] = []
    seen_ids: set[str] = set()

    def _add(prefix: str, names: list[str], type_: str):
        local_seen: set[str] = set()
        for name in names:
            sid = safe_id(name)
            orig = sid; n = 1
            while sid in local_seen:
                n += 1; sid = f"{orig}_{n}"
            local_seen.add(sid)
            cid = f"exec_{prefix}_{sid}"
            if cid in seen_ids: continue
            seen_ids.add(cid)
            out.append({
                "id": cid,
                "type": type_,
                "origin": "exec_diff",
                "description": (f"Test {name!r} ({prefix}) — captured by dual-pass exec mining"
                                f" (cmd: {test_cmd[:60]})"),
            })

    _add("f2p", f2p_names, "fail_to_pass")
    _add("p2p", p2p_names, "pass_to_pass")
    return out


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

async def mine_one(sandbox_factory, task_dir: Path, dry_run: bool, test_timeout: int) -> dict:
    task = task_dir.name
    rec: dict = {"task": task, "f2p_count": 0, "p2p_count": 0, "skipped": False, "wrote": False}

    image = task_image_tag(task_dir)
    if not image:
        rec["skipped"] = True; rec["error"] = "no docker_image in task.toml"
        return rec
    solve = read_solve_sh(task_dir)
    if not solve:
        rec["skipped"] = True; rec["error"] = "no solve.sh"
        return rec
    spec = read_ci_spec(task)
    if not spec:
        rec["skipped"] = True; rec["error"] = "no CI miner cache"
        return rec
    pick = pick_setup_and_test_commands(spec)
    if not pick:
        rec["skipped"] = True; rec["error"] = "no parsable test command"
        return rec
    setup_cmds, test_cmd, _head = pick
    rec["test_cmd"] = test_cmd[:120]
    rec["n_setup_cmds"] = len(setup_cmds)

    if dry_run:
        rec["dry_run_would_mine"] = True
        return rec

    sandbox = await sandbox_factory()
    try:
        result = await run_dual_pass(
            sandbox, task, image, test_cmd, solve,
            setup_cmds=setup_cmds,
            test_timeout=test_timeout,
            gh_token=os.environ.get("GH_TOKEN", ""),
        )
        rec["base_count"] = result.base_count
        rec["gold_count"] = result.gold_count
        rec["f2p_count"] = result.f2p_count
        rec["p2p_count"] = result.p2p_count
        rec["parser"] = result.parser_used
        rec["elapsed_s"] = result.elapsed_s
        if result.error:
            rec["error"] = result.error
        # Cache the per-task result
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{task}.json").write_text(json.dumps({
            "task": task, "image": image, "test_cmd": test_cmd,
            "n_setup_cmds": len(setup_cmds),
            "f2p": result.f2p, "p2p": result.p2p,
            "base_count": result.base_count, "gold_count": result.gold_count,
            "parser": result.parser_used,
            "elapsed_s": result.elapsed_s,
            "error": result.error,
            "base_log_tail": (getattr(result, 'base_log_tail', '') or '')[:3000],
            "gold_log_tail": (getattr(result, 'gold_log_tail', '') or '')[:3000],
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }, indent=2))
        # Write into test_outputs.py + manifest. Always write if we discovered
        # ANY test names (f2p or p2p) — p2p sections are valuable regression
        # signal even when the PR doesn't add new tests.
        # Cap p2p to top-N to keep manifests sane (some suites have 1500+ tests).
        P2P_CAP = 50
        capped_p2p = result.p2p[:P2P_CAP]
        if result.f2p_count > 0 or capped_p2p:
            _apply_to_task(task_dir, test_cmd, result.f2p, capped_p2p)
            rec["wrote"] = True
            rec["p2p_written"] = len(capped_p2p)
    finally:
        try: await sandbox.kill()
        except Exception: pass
    return rec


def _apply_to_task(task_dir: Path, test_cmd: str,
                   f2p_names: list[str], p2p_names: list[str]) -> None:
    """Append/replace the # === Execution-mined f2p === section in test_outputs.py
    and add manifest check entries (origin: exec_diff)."""
    tf = task_dir / "tests" / "test_outputs.py"
    em = task_dir / "eval_manifest.yaml"
    if not (tf.exists() and em.exists()): return
    text = tf.read_text()
    if SECTION_MARKER in text:
        text = re.split(rf"\n+{re.escape(SECTION_MARKER)}.*", text, maxsplit=1, flags=re.S)[0].rstrip() + "\n"
    block = generate_test_block(task_dir.name, test_cmd, f2p_names, p2p_names)
    if block:
        text = text.rstrip() + "\n\n" + block
    tf.write_text(text)
    # Manifest
    manifest = yaml.safe_load(em.read_text()) or {}
    manifest.setdefault("checks", [])
    existing_ids = {c.get("id") for c in manifest["checks"]}
    new = [c for c in generate_manifest_entries(task_dir.name, f2p_names, p2p_names, test_cmd)
           if c["id"] not in existing_ids]
    if new:
        manifest["checks"].extend(new)
        em.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False,
                                 allow_unicode=True, width=10000))


async def main_async(args):
    from taskforge.e2b_worker import create_worker_sandbox, ensure_template

    # Ensure template is ready
    await ensure_template()

    # Build target list
    if args.tasks:
        names = [n.strip() for n in args.tasks.split(",") if n.strip()]
        targets = [Path(args.task_dir) / n for n in names]
    else:
        targets = sorted(p for p in Path(args.task_dir).iterdir() if p.is_dir())
    targets = [t for t in targets if (t / "task.toml").exists()]
    if args.limit:
        targets = targets[:args.limit]

    logger.info("targets: %d, dry_run=%s, concurrency=%d",
                len(targets), args.dry_run, args.concurrency)

    sem = asyncio.Semaphore(args.concurrency)

    async def factory():
        return await create_worker_sandbox(timeout=3600)

    async def bounded(t: Path):
        async with sem:
            return await mine_one(factory, t, args.dry_run, args.test_timeout)

    results = []
    for coro in asyncio.as_completed([bounded(t) for t in targets]):
        rec = await coro
        results.append(rec)
        flag = "WROTE" if rec.get("wrote") else ("skip " if rec.get("skipped") else "drop ")
        logger.info("%-5s %-55s f2p=%d p2p=%d err=%s",
                    flag, rec["task"][:55], rec.get("f2p_count", 0),
                    rec.get("p2p_count", 0), rec.get("error", "")[:60])

    # Summary
    n_wrote = sum(1 for r in results if r.get("wrote"))
    n_skipped = sum(1 for r in results if r.get("skipped"))
    n_with_f2p = sum(1 for r in results if r.get("f2p_count", 0) > 0)
    total_f2p = sum(r.get("f2p_count", 0) for r in results)
    total_p2p = sum(r.get("p2p_count", 0) for r in results)
    logger.info("")
    logger.info("=== Summary ===")
    logger.info("  Targets:        %d", len(results))
    logger.info("  Skipped:        %d (no image / no solve / no CI / no parser)", n_skipped)
    logger.info("  Tasks with f2p: %d", n_with_f2p)
    logger.info("  Tasks written:  %d", n_wrote)
    logger.info("  Total f2p test names discovered: %d", total_f2p)
    logger.info("  Total p2p test names discovered: %d", total_p2p)

    # Write summary file
    out_dir = ROOT / "pipeline_logs" / f"exec_f2p_run_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(results, indent=2))
    logger.info("Summary written: %s", out_dir / "summary.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks")
    ap.add_argument("--tasks", default="", help="Comma-sep list of task names")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--test-timeout", type=int, default=900,
                    help="Per-pass test command timeout (s)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Skip sandbox calls; just report which tasks would be mined")
    args = ap.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
