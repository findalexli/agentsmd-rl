#!/usr/bin/env python3
"""Remove a rubric from all quality.json files across a task corpus.

Safe: does not touch any other fields. Recomputes pass_count/fail_count from
remaining rubric_verdicts. Idempotent — re-running is a no-op.

Usage:
    .venv/bin/python scripts/purge_rubric.py --rubric anti_cheating_measures
    .venv/bin/python scripts/purge_rubric.py --rubric anti_cheating_measures --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def purge_one(path: Path, rubric: str) -> tuple[bool, str]:
    """Return (modified, reason). reason = 'noop' | 'purged' | error."""
    try:
        d = json.loads(path.read_text())
    except Exception as e:
        return False, f"parse_error: {e}"

    # Already-error'd quality.json files have no rubric data — skip.
    if d.get("error"):
        return False, "error_record"

    verdicts = d.get("rubric_verdicts") or {}
    if rubric not in verdicts:
        # Also check if it's still referenced in tier lists (could happen if
        # verdicts was cleared but lists not).
        still_listed = (
            rubric in (d.get("tier_a_fails") or [])
            or rubric in (d.get("tier_b_fails") or [])
            or rubric in (d.get("tier_c_fails") or [])
        )
        if not still_listed:
            return False, "noop"

    # Drop from verdicts
    verdicts.pop(rubric, None)
    d["rubric_verdicts"] = verdicts

    # Drop from tier lists
    for tier_key in ("tier_a_fails", "tier_b_fails", "tier_c_fails"):
        if rubric in (d.get(tier_key) or []):
            d[tier_key] = [r for r in d[tier_key] if r != rubric]

    # Recompute counts
    d["pass_count"] = sum(1 for v in verdicts.values() if v.get("outcome") == "pass")
    d["fail_count"] = sum(1 for v in verdicts.values() if v.get("outcome") == "fail")

    path.write_text(json.dumps(d, indent=2))
    return True, "purged"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rubric", required=True, help="Name of rubric to remove")
    p.add_argument("--task-dir", default="harbor_tasks")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    root = Path(args.task_dir)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    n_scanned = n_purged = n_noop = n_err = 0
    for qf in sorted(root.glob("*/quality.json")):
        n_scanned += 1
        if args.dry_run:
            # Peek without writing
            try:
                d = json.loads(qf.read_text())
                if args.rubric in (d.get("rubric_verdicts") or {}):
                    n_purged += 1
                else:
                    n_noop += 1
            except Exception:
                n_err += 1
            continue
        modified, reason = purge_one(qf, args.rubric)
        if modified:
            n_purged += 1
        elif reason == "noop":
            n_noop += 1
        else:
            n_err += 1

    verb = "would purge" if args.dry_run else "purged"
    print(f"Scanned:   {n_scanned}")
    print(f"{verb}:   {n_purged}")
    print(f"Noop:      {n_noop}")
    print(f"Errors:    {n_err}")


if __name__ == "__main__":
    main()
