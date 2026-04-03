#!/usr/bin/env python3
"""Pre-filter scouted PRs using taskforge heuristics.

Reads scouted_prs.jsonl, applies size/content/patch filters,
writes filtered_prs.jsonl. No LLM, no API calls beyond `gh pr diff`.

Usage:
    python scripts/prefilter_prs.py
    python scripts/prefilter_prs.py --input scouted_prs.jsonl --output filtered_prs.jsonl
    python scripts/prefilter_prs.py --fetch-diffs   # also fetch+check diffs (slower)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from taskforge.scout import is_good_candidate  # noqa: E402
from taskforge.models import PRCandidate

ROOT = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Pre-filter scouted PRs")
    parser.add_argument("--input", default="scouted_prs.jsonl")
    parser.add_argument("--output", default="filtered_prs.jsonl")
    parser.add_argument("--fetch-diffs", action="store_true",
                        help="Fetch PR diffs to check for test-only PRs (slower)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    with open(input_path) as f:
        prs = [json.loads(line) for line in f if line.strip()]

    print(f"Input: {len(prs)} PRs from {input_path.name}")

    passed = []
    rejected = {}

    for raw in prs:
        pr = PRCandidate(**raw)

        # Optionally fetch diff for deeper filtering
        diff = ""
        if args.fetch_diffs:
            try:
                result = subprocess.run(
                    ["gh", "pr", "diff", str(pr.pr_number), "--repo", pr.repo],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0:
                    diff = result.stdout
            except Exception:
                pass

        ok, reason = is_good_candidate(pr, diff=diff)
        if ok:
            passed.append(raw)
        else:
            rejected[reason] = rejected.get(reason, 0) + 1

    print(f"Passed: {len(passed)}")
    print(f"Rejected: {len(prs) - len(passed)}")
    for reason, count in sorted(rejected.items(), key=lambda x: -x[1]):
        print(f"  {reason}: {count}")

    if not args.dry_run:
        with open(output_path, "w") as f:
            for p in passed:
                f.write(json.dumps(p) + "\n")
        print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
