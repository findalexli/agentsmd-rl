#!/usr/bin/env python3
"""Release pipeline claim files owned by a specific PID (or any dead PID).

Use when a worker was SIGKILLed (kill -9) or otherwise died without running
its in-process cleanup, leaving sticky `.claim` files that block retries.

Each `.claim` file has the format:
    pid=NNNN ts=UNIX pr_ref=owner/repo#NNN

Usage:
    # Release claims belonging to PID 12345 (whether alive or dead).
    .venv/bin/python scripts/release_claims.py --pid 12345

    # Release claims whose owning PID is no longer running (most common
    # use after a crash/SIGKILL).
    .venv/bin/python scripts/release_claims.py --dead-only

    # Dry-run — show what would be released, change nothing.
    .venv/bin/python scripts/release_claims.py --dead-only --dry-run

    # Custom claim dir (defaults to ./pipeline_claims).
    .venv/bin/python scripts/release_claims.py --claim-dir other/claims --dead-only

WARNING: do NOT run with --pid against a still-running healthy worker — that
worker will lose track of its claims and another worker may double-process
the same PR. Use --dead-only or specify a known-dead PID.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Owned by another user — treat as alive
        return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--claim-dir", default="pipeline_claims")
    p.add_argument("--pid", type=int, default=None,
                   help="Release claims owned by this PID (alive or dead)")
    p.add_argument("--dead-only", action="store_true",
                   help="Release claims whose owning PID is no longer running")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--backup-dir", default="",
                   help="Move released claims here instead of deleting (recommended)")
    p.add_argument("--keep-if-task-in", action="append", default=[],
                   help="Directory to scan for tasks (eval_manifest.yaml). Claims whose "
                        "pr_ref matches a landed task are kept regardless of PID. "
                        "Repeat for multiple roots (e.g. harbor_tasks, harbor_tasks_agentmd_edits).")
    args = p.parse_args()

    if not args.pid and not args.dead_only:
        p.error("specify --pid PID or --dead-only")

    claim_dir = Path(args.claim_dir)
    if not claim_dir.is_dir():
        print(f"error: {claim_dir} is not a directory", file=sys.stderr)
        return 1

    backup = Path(args.backup_dir) if args.backup_dir else None
    if backup and not args.dry_run:
        backup.mkdir(parents=True, exist_ok=True)

    pid_re = re.compile(r"pid=(\d+)")
    pr_re = re.compile(r"pr_ref=(\S+)")

    # Build set of landed pr_refs (PRs with an existing task dir) so we
    # never release a claim for a completed task — that would falsely
    # advertise the task as available for re-scaffold.
    landed: set[str] = set()
    repo_re = re.compile(r"repo:\s*(\S+)")
    pr_field_re = re.compile(r"pr:\s*(\d+)")
    for root in args.keep_if_task_in:
        root_p = Path(root)
        if not root_p.is_dir():
            print(f"warn: --keep-if-task-in {root} is not a dir, skipping", file=sys.stderr)
            continue
        for em in root_p.glob("*/eval_manifest.yaml"):
            try:
                t = em.read_text()
            except Exception:
                continue
            rm = repo_re.search(t)
            pm = pr_field_re.search(t)
            if rm and pm:
                landed.add(f"{rm.group(1).strip()}#{pm.group(1)}")

    if args.keep_if_task_in:
        print(f"Loaded {len(landed)} landed pr_refs from {len(args.keep_if_task_in)} root(s)")

    n_scanned = n_release = n_kept = n_skip = 0
    for cf in claim_dir.glob("*.claim"):
        n_scanned += 1
        try:
            txt = cf.read_text()
        except Exception:
            n_skip += 1
            continue
        m = pid_re.search(txt)
        if not m:
            n_skip += 1
            continue
        owner_pid = int(m.group(1))

        should_release = False
        if args.pid is not None and owner_pid == args.pid:
            should_release = True
        elif args.dead_only and not pid_alive(owner_pid):
            should_release = True

        if not should_release:
            n_kept += 1
            continue

        # Skip if a real task dir exists for this pr_ref — never release
        # a claim for a completed task.
        if landed:
            pm = pr_re.search(txt)
            if pm and pm.group(1) in landed:
                n_kept += 1
                continue

        if args.dry_run:
            print(f"would release {cf.name} (pid={owner_pid})")
            n_release += 1
            continue

        try:
            if backup:
                shutil.move(str(cf), str(backup / cf.name))
            else:
                cf.unlink()
            n_release += 1
        except Exception as e:
            print(f"failed to release {cf.name}: {e}", file=sys.stderr)
            n_skip += 1

    verb = "would release" if args.dry_run else ("moved" if backup else "deleted")
    print(f"Scanned:  {n_scanned}")
    print(f"{verb}:  {n_release}")
    print(f"Kept:     {n_kept}")
    print(f"Skipped:  {n_skip}")
    if backup and not args.dry_run:
        print(f"Backup:   {backup}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
