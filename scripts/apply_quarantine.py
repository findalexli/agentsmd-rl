#!/usr/bin/env python3
"""Apply the quarantine decisions from combine_verdicts.py to the corpus.

Reads /tmp/quarantine_*.txt and moves listed tasks from harbor_tasks/ to
harbor_tasks_quarantine/ with reason annotations in MANIFEST.json.

Dry-run by default — pass --apply to actually move.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Actually move tasks (default: dry run)")
    ap.add_argument("--corpus", type=Path, default=Path("harbor_tasks"))
    ap.add_argument("--quarantine", type=Path, default=Path("harbor_tasks_quarantine"))
    ap.add_argument("--in-dir", type=Path, default=Path("/tmp"),
                    help="Directory with quarantine_*.txt files")
    args = ap.parse_args()

    decorative = (args.in_dir / "quarantine_decorative.txt").read_text().strip().splitlines()
    trivial    = (args.in_dir / "quarantine_trivial.txt").read_text().strip().splitlines()
    decorative = [n.strip() for n in decorative if n.strip()]
    trivial    = [n.strip() for n in trivial    if n.strip()]

    print(f"Plan:")
    print(f"  decorative (markdown not load-bearing): {len(decorative)}")
    print(f"  trivial (LLM-confirmed):                 {len(trivial)}")
    print(f"  total to quarantine:                     {len(set(decorative + trivial))}")

    if not args.apply:
        print("\n(dry run — pass --apply to actually move)")
        if decorative:
            print(f"\nFirst 5 decorative:")
            for n in decorative[:5]:
                print(f"  - {n}")
        if trivial:
            print(f"\nFirst 5 trivial:")
            for n in trivial[:5]:
                print(f"  - {n}")
        return

    args.quarantine.mkdir(exist_ok=True, parents=True)
    manifest_path = args.quarantine / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    moved = 0
    for name in decorative:
        src = args.corpus / name
        dst = args.quarantine / name
        if src.exists() and not dst.exists():
            src.rename(dst)
            manifest.setdefault(name, [])
            if "decorative_markdown" not in manifest[name]:
                manifest[name].append("decorative_markdown")
            moved += 1

    for name in trivial:
        src = args.corpus / name
        dst = args.quarantine / name
        if src.exists() and not dst.exists():
            src.rename(dst)
        manifest.setdefault(name, [])
        if "trivial_pr" not in manifest[name]:
            manifest[name].append("trivial_pr")

    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=2))
    all_q = sorted([d.name for d in args.quarantine.iterdir()
                    if d.is_dir() and not d.name.startswith("_")])
    (args.quarantine / "INDEX.txt").write_text("\n".join(all_q) + "\n")
    print(f"\nMoved {moved} tasks. Quarantine total: {len(all_q)}")
    print(f"Active corpus: {sum(1 for d in args.corpus.iterdir() if d.is_dir())}")


if __name__ == "__main__":
    main()
