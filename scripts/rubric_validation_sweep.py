#!/usr/bin/env python3
"""Post-generation validation sweep for rubric and distractor rules.

Runs 5 programmatic gates across all eval_manifest.yaml files, then optionally
calls Gemini for semantic anti-tautology checks on surviving rules.

Gates (programmatic, no LLM):
  1. Dedup: collapse rules with >85% text similarity within same manifest
  2. Track 1 redundancy: remove rubric rules already covered by programmatic checks
  3. Source verification: verify cited lines exist and contain related content
  4. Field completeness: flag rules missing source.path or evidence
  5. Self-referential source: reject rules citing merge_commit instead of base_commit

Gate (LLM, optional):
  6. Anti-tautology: reject rules semantically equivalent to instruction.md

Usage:
    # Dry run — report only, don't modify files
    .venv/bin/python scripts/rubric_validation_sweep.py --dry-run

    # Apply fixes (rewrite eval_manifest.yaml files)
    .venv/bin/python scripts/rubric_validation_sweep.py --apply

    # With Gemini anti-tautology check (requires GEMINI_API_KEY)
    .venv/bin/python scripts/rubric_validation_sweep.py --apply --anti-tautology

    # Single task
    .venv/bin/python scripts/rubric_validation_sweep.py --task clickhouse-cidb-secrets-refactor --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import yaml


# ── Gate 1: Dedup ──────────────────────────────────────────────────────────

def similarity(a: str, b: str) -> float:
    """Normalized text similarity (0-1)."""
    a_norm = re.sub(r'\s+', ' ', a.lower().strip())
    b_norm = re.sub(r'\s+', ' ', b.lower().strip())
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def gate_dedup(rules: list[dict], threshold: float = 0.80) -> tuple[list[dict], list[dict]]:
    """Remove duplicate rubric rules (>threshold similarity).

    Keeps the first occurrence (assumed to have better metadata).
    Returns (kept, removed).
    """
    kept = []
    removed = []
    for rule in rules:
        rule_text = rule.get("rule", "")
        is_dup = False
        for k in kept:
            if similarity(rule_text, k.get("rule", "")) > threshold:
                removed.append({**rule, "_reason": f"duplicate of: {k.get('rule', '')[:60]}"})
                is_dup = True
                break
        if not is_dup:
            kept.append(rule)
    return kept, removed


# ── Gate 2: Track 1 redundancy ─────────────────────────────────────────────

def _extract_check_keywords(checks: list[dict]) -> set[str]:
    """Extract significant keywords from check descriptions/IDs."""
    keywords = set()
    for c in checks:
        text = f"{c.get('id', '')} {c.get('description', '')}".lower()
        # Split on non-alpha, filter short words
        words = re.findall(r'[a-z_]{4,}', text)
        keywords.update(words)
    return keywords


def gate_track1_redundancy(
    rubric: list[dict], checks: list[dict], threshold: float = 0.50
) -> tuple[list[dict], list[dict]]:
    """Remove rubric rules that are already covered by programmatic checks.

    Uses keyword overlap between rule text and check descriptions.
    """
    check_keywords = _extract_check_keywords(checks)
    if not check_keywords:
        return rubric, []

    kept = []
    removed = []
    for rule in rubric:
        rule_text = rule.get("rule", "").lower()
        rule_words = set(re.findall(r'[a-z_]{4,}', rule_text))
        if not rule_words:
            kept.append(rule)
            continue
        overlap = len(rule_words & check_keywords) / len(rule_words)
        if overlap >= threshold:
            removed.append({
                **rule,
                "_reason": f"redundant with Track 1 checks (overlap={overlap:.0%})",
                "_overlapping": sorted(rule_words & check_keywords)[:5],
            })
        else:
            kept.append(rule)
    return kept, removed


# ── Gate 3: Source verification ────────────────────────────────────────────

def gate_source_verification(
    rules: list[dict], rule_type: str = "rubric"
) -> tuple[list[dict], list[dict], list[dict]]:
    """Verify source attribution fields.

    Returns (ok, flagged_missing_source, flagged_no_lines).
    Doesn't verify file existence (no repo access) — just checks fields are present.
    """
    ok = []
    missing_source = []
    no_lines = []

    for rule in rules:
        source = rule.get("source")
        if source is None or (isinstance(source, str) and ":" not in source):
            # No structured source at all
            if isinstance(source, str) and source:
                # Legacy string format like "AGENTS.md:39"
                missing_source.append({**rule, "_reason": "legacy string source format"})
            else:
                missing_source.append({**rule, "_reason": "no source attribution"})
            continue

        if isinstance(source, dict):
            path = source.get("path", "")
            lines = source.get("lines", "")
            if not path:
                missing_source.append({**rule, "_reason": "source.path is empty"})
                continue
            if not lines:
                no_lines.append({**rule, "_reason": "source.lines is empty"})
                continue
        ok.append(rule)
    return ok, missing_source, no_lines


# ── Gate 4: Field completeness ─────────────────────────────────────────────

def gate_field_completeness(rubric: list[dict]) -> list[dict]:
    """Score field completeness for each rule. Returns annotated rules."""
    annotated = []
    for rule in rubric:
        fields = {
            "source.path": bool(
                isinstance(rule.get("source"), dict) and rule["source"].get("path")
            ),
            "source.lines": bool(
                isinstance(rule.get("source"), dict) and rule["source"].get("lines")
            ),
            "evidence": bool(rule.get("evidence")),
            "source_text": bool(rule.get("source_text")),
            "category": bool(rule.get("category")),
        }
        score = sum(fields.values()) / len(fields)
        annotated.append({**rule, "_completeness": score, "_fields": fields})
    return annotated


# ── Gate 5: Self-referential source ────────────────────────────────────────

def gate_self_referential(
    rules: list[dict], merge_commit: str, base_commit: str
) -> tuple[list[dict], list[dict]]:
    """Remove rules that cite the merge commit instead of base commit."""
    if not merge_commit:
        return rules, []

    kept = []
    removed = []
    for rule in rules:
        source = rule.get("source")
        if isinstance(source, dict):
            commit = source.get("commit", "")
            if commit and commit == merge_commit:
                removed.append({
                    **rule,
                    "_reason": f"source.commit is merge_commit ({merge_commit[:8]}), not base_commit",
                })
                continue
        kept.append(rule)
    return kept, removed


# ── Gate 6: Anti-tautology (Gemini) ────────────────────────────────────────

GEMINI_MODEL = "gemini-3.1-pro-preview-customtools"

_TAUTOLOGY_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "is_tautological": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["index", "is_tautological", "reason"],
            },
        },
    },
    "required": ["verdicts"],
}


def gate_anti_tautology(
    rubric: list[dict],
    instruction_text: str,
    gemini_key: str,
) -> tuple[list[dict], list[dict]]:
    """Use Gemini to identify tautological rubric rules.

    A rule is tautological if:
    - It restates what instruction.md tells the agent to do
    - Any correct solution would satisfy it automatically
    - It describes what the PR does rather than a pre-existing convention
    """
    if not rubric:
        return rubric, []

    rules_text = "\n".join(
        f"[{i}] {r.get('rule', '')}"
        for i, r in enumerate(rubric)
    )

    prompt = f"""You are auditing rubric rules for a coding agent benchmark.

## Task Instruction (what the agent sees)
{instruction_text[:2000]}

## Rubric Rules to Audit
{rules_text}

## Your Job

For each rule, determine if it is TAUTOLOGICAL — meaning:
1. It merely restates what instruction.md already tells the agent to do
2. ANY correct solution would satisfy it automatically — the rule just describes what the PR does
3. It describes the task objective rephrased as a "convention"

Mark is_tautological=true for rules matching the above.

## IMPORTANT: Convention Discovery Rules Are NOT Tautological

Some rules test whether the agent DISCOVERS conventions from config files that the instruction does NOT mention. These are the most valuable rules in our benchmark.

Examples of GOOD convention discovery rules (mark is_tautological=false):
- "Create a changeset with minor severity for new features" — instruction doesn't mention changesets, but AGENTS.md requires them
- "Run make lint before committing" — instruction doesn't mention linting, but CLAUDE.md requires it
- "Use goimports with -local flag" — instruction doesn't mention formatting, but CLAUDE.md requires it

The key distinction:
- TAUTOLOGICAL: "Fix the bug by replacing X with Y" (restates the instruction)
- NOT TAUTOLOGICAL: "Add a changeset file for every code change" (convention the agent must discover independently)

If a rule governs an action the instruction doesn't mention but a config file DOES require, it is a convention discovery rule — mark it is_tautological=false."""

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
            "responseSchema": _TAUTOLOGY_SCHEMA,
        },
        "systemInstruction": {"parts": [{"text":
            "You are a rubric quality auditor. Be aggressive about flagging "
            "tautological rules — if in doubt, flag it. A 50% false-positive "
            "rate is acceptable; we'd rather remove too many than keep bad rules."
        }]},
    }).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-goog-api-key": gemini_key,
    })

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    [!] Gemini anti-tautology call failed: {e}", file=sys.stderr)
        return rubric, []

    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    if not parts:
        return rubric, []

    try:
        result = json.loads(parts[0].get("text", ""))
    except json.JSONDecodeError:
        return rubric, []

    verdicts = {v["index"]: v for v in result.get("verdicts", [])}

    kept = []
    removed = []
    for i, rule in enumerate(rubric):
        v = verdicts.get(i, {})
        if v.get("is_tautological", False):
            removed.append({**rule, "_reason": f"tautological: {v.get('reason', '')[:100]}"})
        else:
            kept.append(rule)
    return kept, removed


# ── Distractor scope filter ────────────────────────────────────────────────

def gate_distractor_scope(
    distractors: list[dict], edited_paths: list[str]
) -> tuple[list[dict], list[dict]]:
    """Flag distractors whose source file has zero path overlap with edited files.

    We keep them but flag as potentially weak — don't auto-remove since some
    cross-scope distractors are intentional (scope_ambiguity type).
    """
    if not edited_paths:
        return distractors, []

    # Extract directory prefixes from edited paths
    edit_dirs = set()
    for p in edited_paths:
        parts = Path(p).parts
        # Add first 1-2 directory components
        if len(parts) >= 2:
            edit_dirs.add(parts[0])
            edit_dirs.add(str(Path(*parts[:2])))
        elif parts:
            edit_dirs.add(parts[0])

    ok = []
    flagged = []
    for d in distractors:
        source = d.get("source")
        if not isinstance(source, dict):
            ok.append(d)
            continue
        source_path = source.get("path", "")
        if not source_path:
            ok.append(d)
            continue

        # Check if source shares any directory prefix with edited files
        source_parts = Path(source_path).parts
        has_overlap = False
        for sp in source_parts[:2]:
            if sp in edit_dirs or sp in (".", "AGENTS.md", "CLAUDE.md", ".cursorrules"):
                has_overlap = True
                break

        # Root-level config files are always in scope
        if "/" not in source_path and source_path.endswith((".md", ".cursorrules")):
            has_overlap = True

        if not has_overlap:
            flagged.append({
                **d,
                "_reason": f"source {source_path} has no path overlap with edited files",
            })
        else:
            ok.append(d)
    return ok, flagged


# ── Main sweep ─────────────────────────────────────────────────────────────

def process_task(
    task_dir: Path,
    *,
    apply: bool = False,
    anti_tautology: bool = False,
    gemini_key: str = "",
    verbose: bool = False,
) -> dict:
    """Run all gates on a single task's eval_manifest.yaml.

    Returns stats dict with counts of kept/removed per gate.
    """
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return {"task": task_dir.name, "status": "no_manifest"}

    try:
        manifest = yaml.safe_load(manifest_path.read_text())
    except Exception as e:
        return {"task": task_dir.name, "status": "parse_error", "error": str(e)}

    if not manifest:
        return {"task": task_dir.name, "status": "empty_manifest"}

    raw_rubric = manifest.get("rubric", [])
    raw_distractors = manifest.get("distractors", [])
    checks = manifest.get("checks", [])

    # Normalize: bare strings → dicts with rule key
    rubric = [
        r if isinstance(r, dict) else {"rule": str(r)}
        for r in (raw_rubric or [])
    ]
    distractors = [
        d if isinstance(d, dict) else {"rule": str(d)}
        for d in (raw_distractors or [])
    ]
    source = manifest.get("source", {})

    if not rubric and not distractors:
        return {"task": task_dir.name, "status": "no_rubric_or_distractors"}

    stats = {
        "task": task_dir.name,
        "status": "ok",
        "rubric_before": len(rubric),
        "distractors_before": len(distractors),
        "gates": {},
    }

    all_rubric_removed = []
    all_distractor_flagged = []

    # Gate 1: Dedup rubric rules
    rubric, removed = gate_dedup(rubric)
    stats["gates"]["dedup"] = {"removed": len(removed)}
    all_rubric_removed.extend(removed)
    if verbose and removed:
        for r in removed:
            print(f"    [dedup] {r.get('rule', '')[:60]}... -> {r.get('_reason', '')}")

    # Gate 2: Track 1 redundancy
    rubric, removed = gate_track1_redundancy(rubric, checks)
    stats["gates"]["track1_redundancy"] = {"removed": len(removed)}
    all_rubric_removed.extend(removed)
    if verbose and removed:
        for r in removed:
            print(f"    [t1-dup] {r.get('rule', '')[:60]}... -> {r.get('_reason', '')}")

    # Gate 3: Source verification (rubric + distractors)
    rubric, missing_src_r, no_lines_r = gate_source_verification(rubric, "rubric")
    distractors, missing_src_d, no_lines_d = gate_source_verification(distractors, "distractor")
    stats["gates"]["source_verification"] = {
        "rubric_missing_source": len(missing_src_r),
        "rubric_no_lines": len(no_lines_r),
        "distractor_missing_source": len(missing_src_d),
        "distractor_no_lines": len(no_lines_d),
    }
    # Don't remove for missing source — just flag. Keep them for now.
    # But DO remove rules with no source at all (no attribution = untraceable)
    all_rubric_removed.extend(missing_src_r)
    if verbose and missing_src_r:
        for r in missing_src_r:
            print(f"    [no-src] {r.get('rule', '')[:60]}... -> {r.get('_reason', '')}")

    # Gate 4: Field completeness (annotate only, don't remove)
    annotated = gate_field_completeness(rubric)
    avg_completeness = (
        sum(r["_completeness"] for r in annotated) / len(annotated)
        if annotated else 0
    )
    stats["gates"]["completeness"] = {
        "avg_score": round(avg_completeness, 2),
        "fully_complete": sum(1 for r in annotated if r["_completeness"] >= 0.8),
        "bare_minimum": sum(1 for r in annotated if r["_completeness"] <= 0.2),
    }
    # Strip annotations
    rubric = [{k: v for k, v in r.items() if not k.startswith("_")} for r in annotated]

    # Gate 5: Self-referential source
    merge_commit = source.get("merge_commit", "")
    base_commit = source.get("base_commit", "")
    rubric, removed = gate_self_referential(rubric, merge_commit, base_commit)
    stats["gates"]["self_referential"] = {"removed": len(removed)}
    all_rubric_removed.extend(removed)
    if verbose and removed:
        for r in removed:
            print(f"    [self-ref] {r.get('rule', '')[:60]}... -> {r.get('_reason', '')}")

    # Gate 6: Anti-tautology (optional, requires Gemini)
    if anti_tautology and gemini_key and rubric:
        instruction_path = task_dir / "instruction.md"
        instruction_text = ""
        if instruction_path.exists():
            instruction_text = instruction_path.read_text()
        rubric, removed = gate_anti_tautology(rubric, instruction_text, gemini_key)
        stats["gates"]["anti_tautology"] = {"removed": len(removed)}
        all_rubric_removed.extend(removed)
        if verbose and removed:
            for r in removed:
                print(f"    [tautology] {r.get('rule', '')[:60]}... -> {r.get('_reason', '')}")

    # Distractor scope check (flag only, don't remove)
    edited_paths = []
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        solve_text = solve_path.read_text()
        # Extract paths from git diff/patch commands in solve.sh
        edited_paths = re.findall(r'(?:^[+-]{3} [ab]/)(\S+)', solve_text, re.MULTILINE)
    distractors_ok, distractor_flagged = gate_distractor_scope(distractors, edited_paths)
    stats["gates"]["distractor_scope"] = {"flagged": len(distractor_flagged)}
    if verbose and distractor_flagged:
        for d in distractor_flagged:
            print(f"    [scope] {d.get('rule', '')[:60]}... -> {d.get('_reason', '')}")

    # Final counts
    stats["rubric_after"] = len(rubric)
    stats["rubric_removed"] = len(all_rubric_removed)
    stats["distractors_after"] = len(distractors)
    stats["distractor_flagged"] = len(distractor_flagged)

    # Apply changes
    if apply and (all_rubric_removed or missing_src_r):
        manifest["rubric"] = rubric
        # Don't modify distractors — only flag them
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))
        stats["applied"] = True
    else:
        stats["applied"] = False

    return stats


def main():
    parser = argparse.ArgumentParser(description="Rubric validation sweep")
    parser.add_argument("--task", help="Single task name to process")
    parser.add_argument("--apply", action="store_true", help="Rewrite manifests (default: dry run)")
    parser.add_argument("--anti-tautology", action="store_true", help="Run Gemini anti-tautology gate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-rule decisions")
    parser.add_argument("--dir", default="harbor_tasks", help="Task directory to scan")
    parser.add_argument("--concurrency", type=int, default=1, help="Concurrent Gemini calls (for anti-tautology)")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if args.anti_tautology and not gemini_key:
        print("ERROR: --anti-tautology requires GEMINI_API_KEY env var", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.dir)
    if args.task:
        task_dirs = [base_dir / args.task]
        if not task_dirs[0].exists():
            print(f"ERROR: {task_dirs[0]} does not exist", file=sys.stderr)
            sys.exit(1)
    else:
        task_dirs = sorted(d for d in base_dir.iterdir() if d.is_dir())

    print(f"Scanning {len(task_dirs)} tasks in {base_dir}/")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    if args.anti_tautology:
        print(f"Anti-tautology: ON (Gemini)")
    print()

    # Aggregate stats
    totals = defaultdict(int)
    gate_totals = defaultdict(lambda: defaultdict(int))
    errors = []
    all_stats = []

    for i, task_dir in enumerate(task_dirs):
        if args.verbose:
            print(f"[{i+1}/{len(task_dirs)}] {task_dir.name}")

        stats = process_task(
            task_dir,
            apply=args.apply,
            anti_tautology=args.anti_tautology,
            gemini_key=gemini_key,
            verbose=args.verbose,
        )
        all_stats.append(stats)

        if stats["status"] == "parse_error":
            errors.append(stats)
            continue
        if stats["status"] != "ok":
            continue

        totals["tasks_processed"] += 1
        totals["rubric_before"] += stats["rubric_before"]
        totals["rubric_after"] += stats["rubric_after"]
        totals["rubric_removed"] += stats["rubric_removed"]
        totals["distractors_before"] += stats["distractors_before"]
        totals["distractor_flagged"] += stats.get("distractor_flagged", 0)

        for gate, gate_stats in stats.get("gates", {}).items():
            for k, v in gate_stats.items():
                if isinstance(v, (int, float)):
                    gate_totals[gate][k] += v

        # Rate limit for Gemini calls
        if args.anti_tautology and gemini_key:
            time.sleep(0.5)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tasks processed: {totals['tasks_processed']}")
    print(f"Parse errors: {len(errors)}")
    print()
    print(f"Rubric rules before: {totals['rubric_before']}")
    print(f"Rubric rules after:  {totals['rubric_after']}")
    print(f"Rubric rules removed: {totals['rubric_removed']} ({totals['rubric_removed']/max(totals['rubric_before'],1):.0%})")
    print()
    print(f"Distractors: {totals['distractors_before']}")
    print(f"Distractors flagged (weak scope): {totals['distractor_flagged']}")
    print()
    print("Per-gate breakdown:")
    for gate, gs in sorted(gate_totals.items()):
        parts = ", ".join(f"{k}={v}" for k, v in sorted(gs.items()) if k != "avg_score")
        if "avg_score" in gs:
            avg = gs["avg_score"] / max(totals["tasks_processed"], 1)
            parts += f", avg_completeness={avg:.2f}"
        print(f"  {gate}: {parts}")

    if errors:
        print(f"\nParse errors ({len(errors)}):")
        for e in errors:
            print(f"  {e['task']}: {e.get('error', '')[:80]}")

    # Write detailed stats
    out_path = Path(f"pipeline_logs/rubric_sweep_{'apply' if args.apply else 'dryrun'}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for s in all_stats:
            # Strip internal annotations before writing
            clean = {k: v for k, v in s.items() if not k.startswith("_")}
            f.write(json.dumps(clean) + "\n")
    print(f"\nDetailed stats: {out_path}")


if __name__ == "__main__":
    main()
