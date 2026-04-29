#!/usr/bin/env python3
"""Drop manifest check entries that don't have a matching `def test_<id>` in
test_outputs.py.

When mining/regenerating tests we sometimes leave manifest entries pointing to
test functions that no longer exist (e.g. the CI re-mine replaced an entire
section). Harbor would mark those checks failed because pytest can't find them.

Strategy: for each task, build the set of `def test_<name>` in test_outputs.py.
For each manifest check whose canonical id (`test_<id>` if not already
prefixed) isn't in that set, drop it. Cap removals at 90% of declared checks
so we never wipe a manifest entirely (would be a sign of catastrophic mismatch
worth investigating manually).
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def reconcile_one(task_dir: Path, dry_run: bool, repair_dir: Path) -> dict:
    rec = {"task": task_dir.name, "dropped_f2p": 0, "dropped_p2p": 0, "kept_f2p": 0, "kept_p2p": 0, "wrote": False, "errors": []}
    em = task_dir / "eval_manifest.yaml"
    tf = task_dir / "tests" / "test_outputs.py"
    if not (em.exists() and tf.exists()):
        rec["errors"].append("missing manifest or test_outputs.py")
        return rec
    try:
        manifest = yaml.safe_load(em.read_text()) or {}
    except Exception as e:
        rec["errors"].append(f"yaml load: {e}"); return rec
    test_fn_names = set(re.findall(r"^def\s+(test_\w+)", tf.read_text(), re.M))
    checks = manifest.get("checks") or []

    kept = []; dropped_ids = []
    for c in checks:
        cid = c.get("id", "")
        cand = cid if cid.startswith("test_") else f"test_{cid}"
        if cand in test_fn_names:
            kept.append(c)
            if c.get("type") == "fail_to_pass": rec["kept_f2p"] += 1
            elif c.get("type") == "pass_to_pass": rec["kept_p2p"] += 1
        else:
            dropped_ids.append(cid)
            if c.get("type") == "fail_to_pass": rec["dropped_f2p"] += 1
            elif c.get("type") == "pass_to_pass": rec["dropped_p2p"] += 1

    if not dropped_ids:
        return rec  # nothing to do

    # Safety: don't wipe everything
    if len(kept) == 0:
        rec["errors"].append(f"would wipe all {len(checks)} checks — keeping as-is for manual review")
        return rec
    if len(dropped_ids) / max(len(checks), 1) > 0.9:
        rec["errors"].append(f"would drop >90% of checks ({len(dropped_ids)}/{len(checks)}) — keeping as-is")
        return rec

    if dry_run:
        rec["would_drop"] = dropped_ids
        return rec

    # Backup before write
    backup = repair_dir / "backups" / task_dir.name
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(em, backup / "eval_manifest.yaml")

    manifest["checks"] = kept
    em.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False,
                             allow_unicode=True, width=10000))
    rec["wrote"] = True
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    import datetime as dt
    repair_dir = ROOT / "pipeline_logs" / f"manifest_reconcile_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if args.apply: repair_dir.mkdir(parents=True, exist_ok=True)

    targets = sorted(p for p in Path(args.task_dir).iterdir() if p.is_dir())
    summary = []
    n_wrote = n_dropped_f2p = n_dropped_p2p = 0
    for t in targets:
        rec = reconcile_one(t, dry_run=not args.apply, repair_dir=repair_dir)
        summary.append(rec)
        if rec.get("dropped_f2p") or rec.get("dropped_p2p"):
            flag = "wrote" if rec.get("wrote") else ("would" if not args.apply else "skip ")
            print(f"  {flag:5s} {t.name[:55]:55s}  -f2p:{rec['dropped_f2p']:3d}  -p2p:{rec['dropped_p2p']:3d}  err={'; '.join(rec['errors'])[:50]}")
        if rec.get("wrote"):
            n_wrote += 1
            n_dropped_f2p += rec["dropped_f2p"]
            n_dropped_p2p += rec["dropped_p2p"]

    print(f"\n{'wrote' if args.apply else 'WOULD write to'} {n_wrote} tasks")
    print(f"  dropped {n_dropped_f2p} f2p check entries")
    print(f"  dropped {n_dropped_p2p} p2p check entries")
    if args.apply:
        (repair_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"  summary: {repair_dir/'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
