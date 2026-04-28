#!/usr/bin/env python3
"""Diff before/after verdicts from the re-judge pass and move flips.

After running quality_judge.py with the new prompts on both
`harbor_tasks_md_authoring/` and `harbor_tasks_md_authoring_quarantine_quality/`:

  - Tasks in active that flipped to LOW/DELETE were already moved to
    quarantine by --quarantine.
  - Tasks in quarantine that flipped to HIGH/MEDIUM are NOT moved
    automatically — this script rescues them back to active.

Reads /tmp/verdicts_before_rejudge.json (snapshot taken before re-judge)
and reads current md_quality.json from each task to determine the diff.
"""
from __future__ import annotations
import json
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
ACTIVE = ROOT / "harbor_tasks_md_authoring"
QUARANTINE = ROOT / "harbor_tasks_md_authoring_quarantine_quality"
SNAP = Path("/tmp/verdicts_before_rejudge.json")


def current_verdict(tdir: Path) -> str | None:
    mj = tdir / "md_quality.json"
    if not mj.exists():
        return None
    try:
        return json.loads(mj.read_text()).get("verdict")
    except Exception:
        return None


def main():
    if not SNAP.exists():
        raise SystemExit(f"missing snapshot {SNAP}")
    before = json.loads(SNAP.read_text())

    rows = []
    # Walk both dirs by current name (a task may have moved).
    for d in (ACTIVE, QUARANTINE):
        for tdir in d.iterdir():
            if not tdir.is_dir():
                continue
            name = tdir.name
            now_v = current_verdict(tdir)
            old = before.get(name)
            old_v = old.get("verdict") if old else None
            old_where = old.get("where") if old else None
            rows.append({
                "task": name,
                "old_where": old_where,
                "old_verdict": old_v,
                "now_where": d.name,
                "now_verdict": now_v,
            })

    flips_demote = []   # active HIGH/MED → LOW/DELETE  (auto-quarantined already)
    flips_rescue = []   # quarantine LOW/DELETE → HIGH/MEDIUM (need to move)
    rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "DELETE": 0}

    for r in rows:
        oldv, newv = r["old_verdict"], r["now_verdict"]
        if oldv is None or newv is None:
            continue
        if oldv == newv:
            continue
        old_rank = rank.get(oldv, -1)
        new_rank = rank.get(newv, -1)
        if r["old_where"] == "harbor_tasks_md_authoring" and new_rank < 2:
            flips_demote.append(r)
        if r["old_where"] == "harbor_tasks_md_authoring_quarantine_quality" and new_rank >= 2:
            flips_rescue.append(r)

    print(f"Total tasks scanned: {len(rows)}")
    print()
    print(f"DEMOTIONS (active → quarantine): {len(flips_demote)}")
    for r in flips_demote[:25]:
        print(f"  {r['task']:50.50}  {r['old_verdict']} → {r['now_verdict']}")
    if len(flips_demote) > 25:
        print(f"  ... +{len(flips_demote)-25} more")
    print()
    print(f"RESCUES (quarantine → active): {len(flips_rescue)}")
    for r in flips_rescue[:25]:
        print(f"  {r['task']:50.50}  {r['old_verdict']} → {r['now_verdict']}")
    if len(flips_rescue) > 25:
        print(f"  ... +{len(flips_rescue)-25} more")
    print()

    # Summary table
    transitions = Counter()
    for r in rows:
        if r["old_verdict"] and r["now_verdict"]:
            transitions[(r["old_verdict"], r["now_verdict"])] += 1
    print("Transition matrix (old → new):")
    for (o, n), c in sorted(transitions.items(), key=lambda x: -x[1])[:30]:
        flag = "" if o == n else "  *"
        print(f"  {o:8} → {n:8}  {c:5}{flag}")

    # Apply rescues
    if flips_rescue:
        print()
        print("Applying rescues...")
        moved = 0
        for r in flips_rescue:
            src = QUARANTINE / r["task"]
            dst = ACTIVE / r["task"]
            if dst.exists():
                print(f"  SKIP (active dst exists): {r['task']}")
                continue
            if not src.exists():
                continue
            try:
                shutil.move(str(src), str(dst))
                moved += 1
            except Exception as e:
                print(f"  ERROR {r['task']}: {e}")
        print(f"Rescued {moved} tasks back to active corpus.")


if __name__ == "__main__":
    main()
