#!/usr/bin/env python3
"""Emergency E2B sandbox cleanup — kill ALL running sandboxes.

Use when:
- You force-killed a Python process (`kill -9`) leaving orphans
- You hit the 100-sandbox quota
- Before starting a fresh batch

Usage:
    .venv/bin/python scripts/e2b_cleanup.py           # kill all
    .venv/bin/python scripts/e2b_cleanup.py --list    # just list, don't kill
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from e2b import Sandbox


def main():
    parser = argparse.ArgumentParser(description="Clean up orphaned E2B sandboxes")
    parser.add_argument("--list", action="store_true", help="List only, don't kill")
    args = parser.parse_args()

    api_key = os.environ.get("E2B_API_KEY", "")
    if not api_key:
        print("ERROR: E2B_API_KEY not set")
        sys.exit(1)

    p = Sandbox.list(api_key=api_key)
    count = 0
    killed = 0
    failed = 0

    while True:
        items = p.next_items()
        if not items:
            break
        for s in items:
            count += 1
            if args.list:
                print(f"  {s.sandbox_id}  template={getattr(s, 'template_id', '?')}  started={getattr(s, 'started_at', '?')}")
            else:
                try:
                    Sandbox.kill(s.sandbox_id, api_key=api_key)
                    killed += 1
                    if killed <= 5 or killed % 20 == 0:
                        print(f"  killed {s.sandbox_id} (#{killed})")
                except Exception as e:
                    failed += 1
                    print(f"  FAILED {s.sandbox_id}: {e}")
        if not p.has_next:
            break

    if args.list:
        print(f"\nTotal running sandboxes: {count}")
    else:
        print(f"\nTotal found: {count}, killed: {killed}, failed: {failed}")


if __name__ == "__main__":
    main()
