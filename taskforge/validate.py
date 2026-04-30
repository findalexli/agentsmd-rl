#!/usr/bin/env python3
"""Write status.json per task from validation_results.csv or E2B test output.

Reads validation data and writes/updates markdown_following/<task>/status.json.
Also generates VALIDATION_STATUS.md summary.

Usage:
    python -m taskforge.validate                                   # from validation_results.csv
    python -m taskforge.validate --from-e2b scripts/e2b_scale_results.json
    python -m taskforge.validate --summary-only                    # just regenerate the markdown
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "markdown_following"


def read_or_create(status_path: Path) -> dict:
    if status_path.exists():
        return json.loads(status_path.read_text())
    return {"validations": []}


def verdict(gold: float | None, nop: float | None, build_ok: bool) -> str:
    if not build_ok:
        return "fail_build"
    if gold is None:
        return "error"
    if nop is not None and nop >= 0.99:
        return "fail_nop_high"
    if gold < 0.95:
        return "fail_gold"
    return "pass"


def import_csv(csv_path: Path, runner: str = "validate_all.sh"):
    """Import validation_results.csv into per-task status.json."""
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            task = row["TASK"]
            task_dir = HARBOR_TASKS / task
            if not task_dir.exists():
                continue

            try:
                gold = float(row["ORACLE"]) if row["ORACLE"] and row["ORACLE"] != "ERROR" else None
            except ValueError:
                gold = None
            try:
                nop = float(row["NOP"]) if row["NOP"] and row["NOP"] != "ERROR" else None
            except ValueError:
                nop = None

            build_ok = row.get("STATUS") != "SKIP"

            status_path = task_dir / "status.json"
            data = read_or_create(status_path)

            entry = {
                "timestamp": datetime.now().isoformat(),
                "runner": runner,
                "docker_build": build_ok,
                "gold_score": gold,
                "nop_score": nop,
                "verdict": verdict(gold, nop, build_ok),
                "notes": "",
            }

            data["validations"].append(entry)
            try:
                status_path.write_text(json.dumps(data, indent=2) + "\n")
                count += 1
            except PermissionError:
                pass

    print(f"Updated {count} tasks from {csv_path.name}")


def import_e2b(json_path: Path, runner: str = "test_e2b_scale.py"):
    """Import E2B test results into per-task status.json."""
    results = json.loads(Path(json_path).read_text())
    count = 0
    for run in results.get("runs", [results]):
        for task_result in run.get("results", []):
            task = task_result.get("task", "")
            task_dir = HARBOR_TASKS / task
            if not task_dir.exists():
                continue

            gold = task_result.get("gold_score")
            nop = task_result.get("base_score")
            build_ok = task_result.get("status") != "build_failed"

            status_path = task_dir / "status.json"
            data = read_or_create(status_path)

            entry = {
                "timestamp": datetime.now().isoformat(),
                "runner": runner,
                "docker_build": build_ok,
                "gold_score": gold,
                "nop_score": nop,
                "verdict": verdict(gold, nop, build_ok),
                "notes": task_result.get("error", ""),
            }

            data["validations"].append(entry)
            status_path.write_text(json.dumps(data, indent=2) + "\n")
            count += 1

    print(f"Updated {count} tasks from {json_path.name}")


def generate_summary():
    """Generate VALIDATION_STATUS.md from per-task status.json files."""
    tasks = sorted(d.name for d in HARBOR_TASKS.iterdir() if d.is_dir())

    passing, failing, errors, no_validation = [], [], [], []

    for task in tasks:
        status_path = HARBOR_TASKS / task / "status.json"
        if not status_path.exists():
            no_validation.append(task)
            continue

        data = json.loads(status_path.read_text())

        # Support both v1 (validations array) and v2 (flat schema) status.json
        if data.get("schema_version") == 2 or data.get("verdict"):
            # v2 schema from e2b_worker.write_status_json()
            v = data.get("verdict", "")
            gold = data.get("gold_reward")
            nop = data.get("nop_reward")
            runner = data.get("backend", data.get("pipeline", "?"))
        elif data.get("validations"):
            # v1 schema (legacy CSV/E2B import)
            latest = None
            for entry in reversed(data["validations"]):
                if "verdict" in entry:
                    latest = entry
                    break
            if latest is None:
                no_validation.append(task)
                continue
            v = latest["verdict"]
            gold = latest.get("gold_score")
            nop = latest.get("nop_score")
            runner = latest.get("runner", "?")
        else:
            no_validation.append(task)
            continue

        if not v:
            no_validation.append(task)
            continue

        row = {"task": task, "gold": gold, "nop": nop, "runner": runner, "verdict": v}

        if v == "pass":
            passing.append(row)
        elif v.startswith("error") or v == "fail_build":
            errors.append(row)
        else:
            failing.append(row)

    lines = [
        f"# Validation Status",
        f"",
        f"Generated: {datetime.now().isoformat()}",
        f"",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Pass | {len(passing)} |",
        f"| Fail | {len(failing)} |",
        f"| Error/build fail | {len(errors)} |",
        f"| No validation | {len(no_validation)} |",
        f"| **Total** | **{len(tasks)}** |",
        f"",
        f"## Passing ({len(passing)})",
        f"",
        f"| Task | Gold | Nop | Runner |",
        f"|------|------|-----|--------|",
    ]
    for r in passing:
        lines.append(f"| {r['task']} | {r['gold']} | {r['nop']} | {r['runner']} |")

    lines += [
        f"",
        f"## Failing ({len(failing)})",
        f"",
        f"| Task | Verdict | Gold | Nop |",
        f"|------|---------|------|-----|",
    ]
    for r in failing:
        lines.append(f"| {r['task']} | {r['verdict']} | {r['gold']} | {r['nop']} |")

    if errors:
        lines += [
            f"",
            f"## Errors ({len(errors)})",
            f"",
        ]
        for r in errors:
            lines.append(f"- {r['task']}: {r['verdict']}")

    (ROOT / "VALIDATION_STATUS.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote VALIDATION_STATUS.md: {len(passing)} pass, {len(failing)} fail, "
          f"{len(errors)} error, {len(no_validation)} unvalidated")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-csv", default="validation_results.csv")
    parser.add_argument("--from-e2b", help="Import from E2B JSON results")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    if not args.summary_only:
        if args.from_e2b:
            import_e2b(Path(args.from_e2b))
        else:
            csv_path = ROOT / args.from_csv
            if csv_path.exists():
                import_csv(csv_path)
            else:
                print(f"No {csv_path.name} found, generating summary only")

    generate_summary()


if __name__ == "__main__":
    main()
