#!/usr/bin/env python3
"""Drill into the 1,218 'unmatched f2p' from audit_test_coverage.py.

For each unmatched f2p check, classify the cause:

  1. **soft_match**: a `def test_*` exists whose name shares 2+ tokens with
     the check_id (probably the same test under a different name).
  2. **partial_keyword_match**: at least one substring of length ≥ 6 from
     the check_id appears in some test_* name.
  3. **manifest_only**: no plausible matching test_* found — the manifest
     declares a check that the test file doesn't implement.
  4. **subprocess_only**: test_outputs.py has no `def test_*` declarations
     at all but does invoke a real runner (the manifest entries map to
     pytest/vitest tests inside the upstream repo, not local test_*).

Output: jsonl + per-bucket sample.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path("/home/alex/agentsmd-rl")
TASK_DIR = ROOT / "harbor_tasks"


def tokenize(name: str) -> set[str]:
    parts = re.split(r"[_\W]+", name.lower())
    return {p for p in parts if len(p) >= 4 and p not in
            {"test", "the", "and", "for", "with", "from", "into", "when"}}


def classify_unmatched(task: Path) -> list[dict]:
    em = task / "eval_manifest.yaml"
    tests = task / "tests" / "test_outputs.py"
    if not em.is_file() or not tests.is_file():
        return []
    try:
        m = yaml.safe_load(em.read_text()) or {}
    except Exception:
        return []
    checks = m.get("checks") or []
    f2p = [c for c in checks if (c or {}).get("type") == "fail_to_pass"]
    if not f2p:
        return []
    src = tests.read_text(errors="replace")
    test_funcs = re.findall(r"^\s*def\s+(test_\w+)\s*\(", src, re.MULTILINE)
    test_token_sets = {fn: tokenize(fn) for fn in test_funcs}
    has_real_runner = bool(re.search(r"\bsubprocess\.(run|check_call|check_output)", src))

    out = []
    for c in f2p:
        cid = (c or {}).get("id", "")
        if not cid:
            continue
        # exact / prefix-fuzzy from main audit
        if (re.search(r"def\s+test_" + re.escape(cid) + r"\s*\(", src) or
            re.search(r"def\s+test_\w*" + re.escape(cid.split('_')[0]) + r"\w*\s*\(", src, re.IGNORECASE)):
            continue  # matched
        cid_tokens = tokenize(cid)
        # Token-overlap match: 2+ shared tokens with any test_*
        soft = next((fn for fn, tt in test_token_sets.items()
                     if len(cid_tokens & tt) >= 2), None)
        if soft:
            out.append({"task": task.name, "check_id": cid,
                        "bucket": "soft_match", "matched_to": soft})
            continue
        # Substring match on long token
        long_subs = [t for t in cid_tokens if len(t) >= 6]
        partial = next((fn for fn in test_funcs
                        if any(s in fn.lower() for s in long_subs)), None)
        if partial:
            out.append({"task": task.name, "check_id": cid,
                        "bucket": "partial_keyword_match",
                        "matched_to": partial})
            continue
        if not test_funcs and has_real_runner:
            out.append({"task": task.name, "check_id": cid,
                        "bucket": "subprocess_only",
                        "matched_to": "(no def test_* — runs upstream tests)"})
            continue
        out.append({"task": task.name, "check_id": cid,
                    "bucket": "manifest_only",
                    "matched_to": ""})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", type=Path, default=TASK_DIR)
    ap.add_argument("--output", type=Path,
                    default=ROOT / "pipeline_logs" / "f2p_unmatched_breakdown.jsonl")
    args = ap.parse_args()

    rows: list[dict] = []
    for d in sorted(args.task_dir.iterdir()):
        if d.is_dir():
            rows.extend(classify_unmatched(d))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    print("=== f2p unmatched, drilled-down breakdown ===")
    for b in ("soft_match", "partial_keyword_match",
              "subprocess_only", "manifest_only"):
        n = counts.get(b, 0)
        print(f"  {b:25} {n}  ({100*n/max(1,len(rows)):.1f}%)")
    print(f"  {'TOTAL':25} {len(rows)}")
    print(f"\nSample of `manifest_only` (genuinely missing — top 10):")
    seen_t = set()
    samples = 0
    for r in rows:
        if r["bucket"] != "manifest_only":
            continue
        if r["task"] in seen_t:
            continue
        seen_t.add(r["task"])
        print(f"  {r['task']:50} :: {r['check_id']}")
        samples += 1
        if samples >= 10:
            break


if __name__ == "__main__":
    main()
