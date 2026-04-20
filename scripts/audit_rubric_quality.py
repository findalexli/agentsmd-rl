#!/usr/bin/env python3
"""Audit all eval_manifest.yaml files in harbor_tasks/ for rubric and distractor quality."""

import glob
import sys
from collections import defaultdict
from pathlib import Path

import yaml


def check_rubric_rule(rule: dict) -> dict[str, bool]:
    """Check a rubric rule for required fields."""
    source = rule.get("source")
    has_source_path = isinstance(source, dict) and bool(source.get("path"))
    has_source_lines = isinstance(source, dict) and bool(source.get("lines"))
    return {
        "source.path": has_source_path,
        "source.lines": has_source_lines,
        "evidence": bool(rule.get("evidence")),
        "source_text": bool(rule.get("source_text")),
        "category": bool(rule.get("category")),
        "verification": bool(rule.get("verification")),
    }


def check_distractor_rule(rule: dict) -> dict[str, bool]:
    """Check a distractor rule for required fields."""
    source = rule.get("source")
    has_source_path = isinstance(source, dict) and bool(source.get("path"))
    return {
        "source.path": has_source_path,
        "collision_type": bool(rule.get("collision_type")),
        "why_distracting": bool(rule.get("why_distracting")),
        "severity": bool(rule.get("severity")),
    }


def main():
    base = Path("/home/alex/agentsmd-rl/harbor_tasks")
    manifests = sorted(glob.glob(str(base / "*/eval_manifest.yaml")))

    print(f"Scanning {len(manifests)} eval_manifest.yaml files...\n")

    # Aggregate counters
    rubric_manifest_count = 0
    total_rubric_rules = 0
    rubric_field_counts = defaultdict(int)
    rubric_fields = ["source.path", "source.lines", "evidence", "source_text", "category", "verification"]

    distractor_manifest_count = 0
    total_distractor_rules = 0
    distractor_field_counts = defaultdict(int)
    distractor_fields = ["source.path", "collision_type", "why_distracting", "severity"]

    # Per-manifest missing counts for "worst" ranking
    manifest_scores = []  # (task_name, total_missing, rubric_missing, distractor_missing, n_rubric, n_distractor)

    parse_errors = []

    for mpath in manifests:
        task_name = Path(mpath).parent.name
        try:
            with open(mpath) as f:
                data = yaml.safe_load(f)
        except Exception as e:
            parse_errors.append((task_name, str(e)))
            continue

        if not isinstance(data, dict):
            continue

        rubric = data.get("rubric")
        distractors = data.get("distractors")

        task_rubric_missing = 0
        task_distractor_missing = 0
        n_rubric = 0
        n_distractor = 0

        if rubric and isinstance(rubric, list):
            rubric_manifest_count += 1
            for rule in rubric:
                if not isinstance(rule, dict):
                    continue
                n_rubric += 1
                total_rubric_rules += 1
                checks = check_rubric_rule(rule)
                for field, present in checks.items():
                    if present:
                        rubric_field_counts[field] += 1
                    else:
                        task_rubric_missing += 1

        if distractors and isinstance(distractors, list):
            distractor_manifest_count += 1
            for rule in distractors:
                if not isinstance(rule, dict):
                    continue
                n_distractor += 1
                total_distractor_rules += 1
                checks = check_distractor_rule(rule)
                for field, present in checks.items():
                    if present:
                        distractor_field_counts[field] += 1
                    else:
                        task_distractor_missing += 1

        total_missing = task_rubric_missing + task_distractor_missing
        if n_rubric > 0 or n_distractor > 0:
            manifest_scores.append((
                task_name,
                total_missing,
                task_rubric_missing,
                task_distractor_missing,
                n_rubric,
                n_distractor,
            ))

    # --- Report ---
    print("=" * 80)
    print("RUBRIC QUALITY AUDIT")
    print("=" * 80)

    print(f"\n--- Rubric Rules ---")
    print(f"  Manifests with rubric section:  {rubric_manifest_count}")
    print(f"  Total rubric rules:            {total_rubric_rules}")
    if total_rubric_rules > 0:
        print(f"  Field coverage:")
        for field in rubric_fields:
            count = rubric_field_counts[field]
            pct = 100.0 * count / total_rubric_rules
            print(f"    {field:20s}  {count:5d} / {total_rubric_rules:5d}  ({pct:5.1f}%)")

    print(f"\n--- Distractor Rules ---")
    print(f"  Manifests with distractor section:  {distractor_manifest_count}")
    print(f"  Total distractor rules:            {total_distractor_rules}")
    if total_distractor_rules > 0:
        print(f"  Field coverage:")
        for field in distractor_fields:
            count = distractor_field_counts[field]
            pct = 100.0 * count / total_distractor_rules
            print(f"    {field:20s}  {count:5d} / {total_distractor_rules:5d}  ({pct:5.1f}%)")

    # Worst manifests
    print(f"\n--- Top 20 Worst Manifests (most missing fields) ---")
    manifest_scores.sort(key=lambda x: -x[1])
    for i, (name, total_miss, r_miss, d_miss, nr, nd) in enumerate(manifest_scores[:20]):
        max_rubric_fields = nr * len(rubric_fields)
        max_distractor_fields = nd * len(distractor_fields)
        max_total = max_rubric_fields + max_distractor_fields
        pct_present = 100.0 * (max_total - total_miss) / max_total if max_total > 0 else 100.0
        print(f"  {i+1:2d}. {name}")
        print(f"      {total_miss} missing fields  ({pct_present:.0f}% complete)")
        print(f"      rubric: {nr} rules, {r_miss} missing  |  distractors: {nd} rules, {d_miss} missing")

    if parse_errors:
        print(f"\n--- Parse Errors ({len(parse_errors)}) ---")
        for name, err in parse_errors[:10]:
            print(f"  {name}: {err}")

    # Summary of manifests with NO rubric and NO distractors
    no_rubric_no_dist = len(manifests) - len(set(
        s[0] for s in manifest_scores
    ))
    print(f"\n--- Summary ---")
    print(f"  Total manifests scanned:          {len(manifests)}")
    print(f"  Manifests with rubric OR dist:    {len(set(s[0] for s in manifest_scores))}")
    print(f"  Manifests with neither:           {no_rubric_no_dist}")

    # Distribution of completeness
    print(f"\n--- Completeness Distribution (rubric rules) ---")
    if total_rubric_rules > 0:
        # Count rules by number of fields present (out of 6)
        # Re-scan to build distribution
        buckets = defaultdict(int)
        for mpath in manifests:
            try:
                with open(mpath) as f:
                    data = yaml.safe_load(f)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            rubric = data.get("rubric")
            if not rubric or not isinstance(rubric, list):
                continue
            for rule in rubric:
                if not isinstance(rule, dict):
                    continue
                checks = check_rubric_rule(rule)
                n_present = sum(1 for v in checks.values() if v)
                buckets[n_present] += 1
        for k in range(7):
            count = buckets.get(k, 0)
            pct = 100.0 * count / total_rubric_rules
            bar = "#" * int(pct / 2)
            print(f"    {k}/6 fields: {count:5d} ({pct:5.1f}%)  {bar}")

    print(f"\n--- Completeness Distribution (distractor rules) ---")
    if total_distractor_rules > 0:
        buckets = defaultdict(int)
        for mpath in manifests:
            try:
                with open(mpath) as f:
                    data = yaml.safe_load(f)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            distractors = data.get("distractors")
            if not distractors or not isinstance(distractors, list):
                continue
            for rule in distractors:
                if not isinstance(rule, dict):
                    continue
                checks = check_distractor_rule(rule)
                n_present = sum(1 for v in checks.values() if v)
                buckets[n_present] += 1
        for k in range(5):
            count = buckets.get(k, 0)
            pct = 100.0 * count / total_distractor_rules
            bar = "#" * int(pct / 2)
            print(f"    {k}/4 fields: {count:5d} ({pct:5.1f}%)  {bar}")


if __name__ == "__main__":
    main()
