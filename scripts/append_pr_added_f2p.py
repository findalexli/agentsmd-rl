#!/usr/bin/env python3
"""Apply test_patch f2p signals to harbor_tasks/<task>/tests/test_outputs.py.

For each task with mined test_patch:
  - Append generated f2p test functions
  - Add manifest check entries (type=fail_to_pass, origin=pr_diff)
  - Validate manifest schema before write
  - Backup original

Idempotent: re-runs replace the `# === PR-added f2p tests ===` section.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from taskforge.test_patch_miner import mine_test_patch
from taskforge.test_patch_generator import (
    generate_test_file_block, generate_manifest_checks,
)
from taskforge.models import EvalManifest


SECTION_MARKER = "# === PR-added f2p tests (taskforge.test_patch_miner) ==="


def append_one(task_dir: Path, repair_dir: Path, dry_run: bool) -> dict:
    rec = {"task": task_dir.name, "n_added": 0, "wrote": False, "errors": []}
    spec = mine_test_patch(task_dir)
    if spec.get("errors"): rec["errors"].extend(spec["errors"])
    n = spec.get("n_added_tests", 0)
    rec["n_added"] = n
    if n == 0: return rec

    body = generate_test_file_block(spec)
    if not body.strip(): return rec

    em = task_dir / "eval_manifest.yaml"
    tests_py = task_dir / "tests" / "test_outputs.py"
    if not em.exists() or not tests_py.exists():
        rec["errors"].append("missing eval_manifest.yaml or tests/test_outputs.py")
        return rec

    existing_text = tests_py.read_text()
    # Strip prior PR-added section if present
    if SECTION_MARKER in existing_text:
        existing_text = re.split(rf"\n+{re.escape(SECTION_MARKER)}.*", existing_text, maxsplit=1)[0].rstrip() + "\n"

    new_full = existing_text.rstrip() + "\n\n" + SECTION_MARKER + "\n" + body

    # Manifest update
    try:
        manifest = yaml.safe_load(em.read_text())
    except Exception as e:
        rec["errors"].append(f"manifest yaml error: {e}")
        return rec
    new_entries = generate_manifest_checks(spec)
    existing_ids = {c.get("id") for c in (manifest.get("checks") or [])}
    deduped = [c for c in new_entries if c["id"] not in existing_ids]
    # If the test section was previously stripped (e.g. by revamp_with_ci_mining)
    # but manifest still has the IDs, we still need to re-add the tests.
    section_present = SECTION_MARKER in (tests_py.read_text() if tests_py.exists() else "")
    needs_test_rewrite = not section_present and len(new_entries) > 0

    if not deduped and not needs_test_rewrite:
        rec["errors"].append("all generated check ids already present and tests already in file")
        return rec

    if dry_run:
        rec["would_write"] = len(deduped) or len(new_entries)
        return rec

    backup = repair_dir / "backups" / task_dir.name
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tests_py, backup / "test_outputs.py")
    shutil.copy2(em, backup / "eval_manifest.yaml")

    if deduped:
        manifest.setdefault("checks", [])
        manifest["checks"].extend(deduped)
        try:
            EvalManifest.model_validate(manifest)
        except Exception as e:
            rec["errors"].append(f"manifest validate failed: {str(e)[:200]}")
            return rec

    tests_py.write_text(new_full)
    if deduped:
        em.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False,
                                 allow_unicode=True, width=10000))
    rec["wrote"] = True
    rec["n_new_manifest_entries"] = len(deduped)
    rec["test_section_restored"] = needs_test_rewrite and not deduped
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    repair_dir = Path(f"pipeline_logs/pr_added_f2p_{ts}")
    if args.apply: repair_dir.mkdir(parents=True, exist_ok=True)

    candidates = sorted(t for t in (ROOT / args.task_dir).iterdir() if t.is_dir())
    print(f"Targets: {len(candidates)}  apply={args.apply}", file=sys.stderr)
    summary = []
    for t in candidates:
        rec = append_one(t, repair_dir, dry_run=not args.apply)
        summary.append(rec)
        if rec["n_added"] >= 1:
            flag = "WROTE" if rec["wrote"] else ("WOULD-WRITE" if args.apply == False else "skip")
            print(f"  {flag:11s} {t.name[:55]:55s} n_tests={rec['n_added']:2d}  err={'; '.join(rec['errors'])[:60]}",
                  file=sys.stderr)
    n_wrote = sum(1 for r in summary if r["wrote"])
    n_with = sum(1 for r in summary if r["n_added"] >= 1)
    n_total = sum(r["n_added"] for r in summary if r["wrote"])
    print(f"\n{n_with} tasks have PR-added tests; {n_wrote} written; +{n_total} f2p tests added",
          file=sys.stderr)

    if args.apply:
        (repair_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"Summary: {repair_dir/'summary.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
