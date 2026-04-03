#!/usr/bin/env python3
"""Lint all harbor task test.sh files using taskforge.lint.

Catches ~35% of issues that the $0.68/task audit-tests phase would find,
for $0. Run this BEFORE `run_pipeline.py audit-tests` to save LLM spend.

Usage:
    python scripts/lint_tasks.py                    # lint all tasks
    python scripts/lint_tasks.py --tasks sglang-*   # glob pattern
    python scripts/lint_tasks.py --severity critical # only critical issues
    python scripts/lint_tasks.py --json             # machine-readable output
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from taskforge.lint import Severity, lint_test_sh

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"


def get_tasks(pattern: str | None = None) -> list[Path]:
    tasks = sorted(HARBOR_TASKS.iterdir())
    tasks = [t for t in tasks if t.is_dir() and (t / "tests" / "test.sh").exists()]
    if pattern:
        tasks = [t for t in tasks if fnmatch.fnmatch(t.name, pattern)]
    return tasks


def main():
    parser = argparse.ArgumentParser(description="Lint harbor task test.sh files")
    parser.add_argument("--tasks", help="Glob pattern for task names (e.g., 'sglang-*')")
    parser.add_argument("--severity", choices=["critical", "warning", "info"], default="warning")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    min_severity = {"critical": 0, "warning": 1, "info": 2}[args.severity]
    severity_order = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.INFO: 2}

    tasks = get_tasks(args.tasks)
    print(f"Linting {len(tasks)} tasks...\n")

    total_issues = 0
    total_critical = 0
    total_passed = 0
    all_results = []

    for task_dir in tasks:
        test_sh = (task_dir / "tests" / "test.sh").read_text()
        result = lint_test_sh(test_sh)

        filtered = [i for i in result.issues if severity_order[i.severity] <= min_severity]

        if args.json_output:
            all_results.append({
                "task": task_dir.name,
                "passed": result.passed,
                "weight_sum": result.weight_sum,
                "has_gate": result.has_gate,
                "issues": [
                    {"severity": i.severity.value, "rule": i.rule,
                     "line": i.line, "message": i.message, "antipattern": i.antipattern}
                    for i in filtered
                ],
            })
        elif filtered:
            print(f"{'FAIL' if result.critical_count else 'WARN'} {task_dir.name}")
            for issue in filtered:
                prefix = "  !!" if issue.severity == Severity.CRITICAL else "  ."
                loc = f":{issue.line}" if issue.line else ""
                print(f"{prefix} [{issue.rule}]{loc} {issue.message}")
            print()

        total_issues += len(filtered)
        total_critical += result.critical_count
        if result.passed:
            total_passed += 1

    if args.json_output:
        json.dump(all_results, sys.stdout, indent=2)
        print()
    else:
        print(f"{'='*60}")
        print(f"  {len(tasks)} tasks linted")
        print(f"  {total_passed} passed ({total_passed * 100 // len(tasks)}%)")
        print(f"  {total_critical} critical issues")
        print(f"  {total_issues} total issues (at {args.severity}+ severity)")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
