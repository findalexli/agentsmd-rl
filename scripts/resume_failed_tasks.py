#!/usr/bin/env python3
"""
Read one-or-more failed_tasks.jsonl files and write a retry-candidate JSONL.

Policy for which failures to retry:
  - rate_limit_exhausted → YES (transient, will likely succeed later)
  - docker_build_error   → NO  (deterministic, will fail again)
  - test_contract_failed → NO  (nop=1 or gold=0; PR is genuinely bad)
  - scaffold_abandoned   → NO  (scaffold agent decided PR is unsuitable)
  - scaffold_error       → YES (often rate-limit-induced)
  - validate_unreachable → YES (scaffold succeeded but later node died)
  - other_error          → YES (default — worth one more try)
  - unknown              → YES

Usage:
  .venv/bin/python scripts/resume_failed_tasks.py \\
      --input pipeline_logs/failed_tasks_*.jsonl \\
      --output retry_candidates.jsonl \\
      [--include scaffold_abandoned]   # override to retry these too
      [--exclude test_contract_failed]
"""
from __future__ import annotations
import argparse
import glob
import json
from collections import Counter
from pathlib import Path

# Default policy: what's worth retrying
_RETRYABLE = {
    "rate_limit_exhausted",
    "scaffold_error",
    "validate_unreachable",
    "other_error",
    "unknown",
}

_NEVER_RETRY = {
    "docker_build_error",      # deterministic
    "test_contract_failed",    # PR genuinely bad (nop=1 or gold=0)
    "scaffold_abandoned",      # scaffold agent said no
    "qgate_rejected",          # quality gate rejected (agentmd only)
}


def load_entries(paths: list[Path]) -> list[dict]:
    all_entries = []
    for p in paths:
        if not p.exists():
            continue
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    all_entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return all_entries


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", nargs="+", required=True,
                   help="Glob(s) of failed_tasks.jsonl files")
    p.add_argument("--output", default="retry_candidates.jsonl")
    p.add_argument("--include", action="append", default=[],
                   help="Extra failure_types to include (overrides default policy)")
    p.add_argument("--exclude", action="append", default=[],
                   help="Failure_types to exclude")
    p.add_argument("--dedup", action="store_true", default=True,
                   help="Deduplicate by pr_ref (keep most recent)")
    p.add_argument("--latest-only", action="store_true",
                   help="For duplicated pr_refs, take only the most recent attempt")
    args = p.parse_args()

    paths: list[Path] = []
    for glob_pat in args.input:
        paths.extend(Path(p) for p in glob.glob(glob_pat))
    paths = sorted(set(paths))
    print(f"Found {len(paths)} failed_tasks file(s)")

    entries = load_entries(paths)
    print(f"Total failure entries: {len(entries)}")

    retryable_types = (_RETRYABLE | set(args.include)) - set(args.exclude)
    print(f"Retryable failure_types: {sorted(retryable_types)}")

    # Filter to retryable
    retry = [e for e in entries if e.get("failure_type") in retryable_types]

    # Dedupe by pr_ref — keep most recent by timestamp
    if args.dedup:
        by_ref: dict[str, dict] = {}
        for e in retry:
            ref = e.get("pr_ref")
            if not ref:
                continue
            existing = by_ref.get(ref)
            if existing is None or e.get("timestamp", "") > existing.get("timestamp", ""):
                by_ref[ref] = e
        retry = list(by_ref.values())

    # Stats
    by_type = Counter(e.get("failure_type", "?") for e in retry)
    by_phase = Counter(e.get("failure_phase", "?") for e in retry)

    # Write output in e2b_worker input format
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        for e in retry:
            f.write(json.dumps({"pr_ref": e["pr_ref"]}) + "\n")

    # Report
    all_types = Counter(e.get("failure_type", "?") for e in entries)
    print("\n" + "=" * 60)
    print("All failures by type:")
    for t, n in sorted(all_types.items(), key=lambda x: -x[1]):
        marker = "✓" if t in retryable_types else " "
        print(f"  {marker} {t}: {n}")
    print(f"\nRetry candidates by type (deduped):")
    for t, n in by_type.most_common():
        print(f"  {t}: {n}")
    print(f"\nRetry candidates by phase:")
    for ph, n in by_phase.most_common():
        print(f"  {ph}: {n}")
    print(f"\nWrote {len(retry)} retry candidates to {out_path}")
    print(f"Launch with: .venv/bin/python -m taskforge.e2b_worker --mode pipeline "
          f"--input {out_path} --concurrency 40 --pool")


if __name__ == "__main__":
    main()
