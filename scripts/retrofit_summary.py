#!/usr/bin/env python3
"""Produce the final retrofit summary by scanning quality.json + reconcile_status.json
across harbor_tasks/. Reads the log dir for auxiliary counts.
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main(task_root: str = "harbor_tasks") -> None:
    root = Path(task_root)
    assert root.is_dir(), f"missing {root}"

    # Scan every task
    total = 0
    has_quality = 0
    has_reconcile = 0
    has_tests_rewrite = 0
    reconciled_ok = 0
    reconciled_broke_oracle = 0
    reconciled_abandoned = 0
    tests_rewritten_ok = 0
    tests_rewrite_broke_oracle = 0
    tests_rewrite_abandoned = 0
    judge_error = 0

    # Rubric counts across whole corpus
    tier_a_tasks: dict[str, int] = Counter()
    tier_b_tasks: dict[str, int] = Counter()
    tier_c_tasks: dict[str, int] = Counter()

    # Per-task Tier-A fail counts (how many rubrics failed per task)
    tier_a_fail_hist: list[int] = []
    clean_tasks = 0

    # Unsalvageable: reconcile was tried but failed, OR no quality.json at all
    unsalvageable: list[str] = []
    partially_fixed: list[str] = []

    for task_dir in sorted(root.iterdir()):
        if not task_dir.is_dir():
            continue
        if not (task_dir / "environment").is_dir():
            continue
        total += 1

        qjson = task_dir / "quality.json"
        rjson = task_dir / "reconcile_status.json"
        has_q = qjson.exists()
        has_r = rjson.exists()

        if has_q:
            has_quality += 1
            try:
                q = json.loads(qjson.read_text())
                if q.get("error"):
                    judge_error += 1
                    unsalvageable.append(f"{task_dir.name}  [judge error: {q['error'][:80]}]")
                    continue
                ta = q.get("tier_a_fails", []) or []
                tb = q.get("tier_b_fails", []) or []
                tc = q.get("tier_c_fails", []) or []
                for r in ta: tier_a_tasks[r] += 1
                for r in tb: tier_b_tasks[r] += 1
                for r in tc: tier_c_tasks[r] += 1
                tier_a_fail_hist.append(len(ta))
                if not ta and not tb and not tc:
                    clean_tasks += 1
            except Exception as e:
                unsalvageable.append(f"{task_dir.name}  [quality.json parse error: {e}]")
                continue

        if has_r:
            has_reconcile += 1
            try:
                r = json.loads(rjson.read_text())
                if r.get("reconciled"):
                    if r.get("nop_reward") == 0 and r.get("gold_reward") == 1:
                        reconciled_ok += 1
                    else:
                        reconciled_broke_oracle += 1
                        partially_fixed.append(f"{task_dir.name}  [reconciled but nop={r.get('nop_reward')} gold={r.get('gold_reward')}]")
                elif r.get("abandoned"):
                    reconciled_abandoned += 1
                    unsalvageable.append(f"{task_dir.name}  [reconcile abandoned: {r.get('reason', '')[:100]}]")
            except Exception:
                pass

        # tests_rewrite_status.json — round-2 test rewrite pass
        tjson = task_dir / "tests_rewrite_status.json"
        if tjson.exists():
            has_tests_rewrite += 1
            try:
                tr = json.loads(tjson.read_text())
                if tr.get("rewritten"):
                    if tr.get("nop_reward") == 0 and tr.get("gold_reward") == 1:
                        tests_rewritten_ok += 1
                    else:
                        tests_rewrite_broke_oracle += 1
                        partially_fixed.append(f"{task_dir.name}  [tests_rewritten but nop={tr.get('nop_reward')} gold={tr.get('gold_reward')}]")
                elif tr.get("abandoned"):
                    tests_rewrite_abandoned += 1
                    unsalvageable.append(f"{task_dir.name}  [tests_rewrite abandoned: {tr.get('reason', '')[:100]}]")
            except Exception:
                pass

    print("═" * 75)
    print("  RETROFIT SUMMARY — 20-rubric quality pipeline")
    print("═" * 75)
    print(f"  Corpus:                    {total} tasks in {task_root}/")
    print(f"  With quality.json:         {has_quality} ({100*has_quality/max(1,total):.0f}%)")
    print(f"  With reconcile_status.json:{has_reconcile} ({100*has_reconcile/max(1,total):.0f}%)")
    print(f"  Judge errors:              {judge_error}")
    print()

    print("  ── Judge verdicts across corpus ──")
    print(f"  Clean tasks (no fails): {clean_tasks} ({100*clean_tasks/max(1,has_quality):.0f}% of judged)")
    if tier_a_fail_hist:
        import statistics
        avg_a = statistics.mean(tier_a_fail_hist)
        max_a = max(tier_a_fail_hist)
        print(f"  Tier-A fails/task:      avg {avg_a:.1f}, max {max_a}")
    print()

    print("  ── Reconcile outcomes (instruction.md rewrites) ──")
    print(f"  Reconciled (oracle held):    {reconciled_ok}")
    print(f"  Reconciled but oracle broke: {reconciled_broke_oracle}")
    print(f"  Reconcile abandoned:         {reconciled_abandoned}")
    print()

    if has_tests_rewrite:
        print("  ── Tests rewrite outcomes (test_outputs.py rewrites) ──")
        print(f"  With tests_rewrite_status.json: {has_tests_rewrite}")
        print(f"  Rewritten (oracle held):        {tests_rewritten_ok}")
        print(f"  Rewritten but oracle broke:     {tests_rewrite_broke_oracle}")
        print(f"  Rewrite abandoned:              {tests_rewrite_abandoned}")
        print()

    print("  ── Top rubric failures (Tier A) ──")
    for name, n in tier_a_tasks.most_common():
        pct = 100 * n / max(1, has_quality)
        print(f"  🔴 {name:<38} {n:>4} tasks ({pct:.0f}%)")
    print()

    print("  ── Top rubric failures (Tier B) ──")
    for name, n in tier_b_tasks.most_common():
        pct = 100 * n / max(1, has_quality)
        print(f"  🟡 {name:<38} {n:>4} tasks ({pct:.0f}%)")
    print()

    print("  ── Top rubric failures (Tier C) ──")
    for name, n in tier_c_tasks.most_common():
        pct = 100 * n / max(1, has_quality)
        print(f"  ⚪ {name:<38} {n:>4} tasks ({pct:.0f}%)")
    print()

    if unsalvageable:
        print(f"  ── Unsalvageable tasks ({len(unsalvageable)}) ──")
        for t in unsalvageable[:30]:
            print(f"    {t}")
        if len(unsalvageable) > 30:
            print(f"    ... +{len(unsalvageable)-30} more")
        print()

    if partially_fixed:
        print(f"  ── Reconcile broke oracle ({len(partially_fixed)}) ──")
        for t in partially_fixed[:10]:
            print(f"    {t}")
        print()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "harbor_tasks")
