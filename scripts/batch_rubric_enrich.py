#!/usr/bin/env python3
"""Batch enrich tasks with rubric + distractors via parallel Gemini calls.

Targets three issue categories:
  1. WEAK: 0 rubric rules (repo has config files, just need extraction)
  2. NO_DISTRACTORS: has rubric but 0 distractors
  3. NO_SOURCE: rubric rules without source.path attribution

Clones repos once, reuses across tasks from same repo.
Parallel Gemini calls with rate limiting.

Usage:
    set -a && source .env && set +a
    .venv/bin/python scripts/batch_rubric_enrich.py --dry-run
    .venv/bin/python scripts/batch_rubric_enrich.py --concurrency 5
    .venv/bin/python scripts/batch_rubric_enrich.py --category weak --limit 20
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

ROOT = Path(__file__).resolve().parent.parent


def scan_tasks() -> list[dict]:
    """Scan all tasks and categorize issues."""
    tasks = []
    # Track which repos have rubric (to know if 0-rubric tasks are fixable)
    repos_with_rubric: set[str] = set()

    # First pass: find repos that DO have rubric
    for base in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        for task in (ROOT / base).iterdir():
            if not task.is_dir():
                continue
            manifest = task / "eval_manifest.yaml"
            if not manifest.exists():
                continue
            try:
                m = yaml.safe_load(manifest.read_text())
            except Exception:
                continue
            if not m or not isinstance(m, dict):
                continue
            rubric = m.get("rubric", []) or []
            if rubric:
                df = task / "environment" / "Dockerfile"
                if df.exists():
                    match = re.search(r"github\.com/([^/]+/[^\s.]+?)(?:\.git|[\s]|$)", df.read_text())
                    if match:
                        repos_with_rubric.add(match.group(1))

    # Second pass: find tasks that need fixing
    for base in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        for task in sorted((ROOT / base).iterdir()):
            if not task.is_dir():
                continue
            manifest = task / "eval_manifest.yaml"
            if not manifest.exists():
                continue
            try:
                m = yaml.safe_load(manifest.read_text())
            except Exception:
                continue
            if not m or not isinstance(m, dict):
                continue

            rubric = m.get("rubric", []) or []
            distractors = m.get("distractors", []) or []
            checks = m.get("checks", []) or []
            if not checks:
                continue  # Broken, skip

            df = task / "environment" / "Dockerfile"
            repo = ""
            commit = ""
            if df.exists():
                df_text = df.read_text()
                match = re.search(r"github\.com/([^/]+/[^\s.]+?)(?:\.git|[\s]|$)", df_text)
                if match:
                    repo = match.group(1)
                for pattern in [
                    r"git checkout\s+([a-f0-9]{7,40})",
                    r"git fetch.*origin\s+([a-f0-9]{7,40})",
                    r"ARG\s+BASE_COMMIT=([a-f0-9]{7,40})",
                ]:
                    cm = re.search(pattern, df_text)
                    if cm:
                        commit = cm.group(1)
                        break

            # Categorize
            categories = []
            no_source_count = 0

            if not rubric:
                if repo in repos_with_rubric:
                    categories.append("weak")  # Fixable: repo has config
                else:
                    continue  # Not fixable: repo has no config files
            else:
                # Check for missing sources
                for r in rubric:
                    if isinstance(r, dict):
                        src = r.get("source", {})
                        if not src or (isinstance(src, dict) and not src.get("path")):
                            no_source_count += 1
                if no_source_count > 0:
                    categories.append("no_source")

            if not distractors:
                categories.append("no_distractors")

            if not categories:
                continue  # Task is fine

            tasks.append({
                "task": task.name,
                "dir": base,
                "repo": repo,
                "commit": commit,
                "categories": categories,
                "rubric_count": len(rubric),
                "distractor_count": len(distractors),
                "no_source_count": no_source_count,
            })

    return tasks


def clone_repo(repo: str, commit: str, cache_dir: Path) -> Path | None:
    """Clone repo at commit. Returns repo path or None on failure."""
    repo_dir = cache_dir / repo.replace("/", "_")
    if repo_dir.exists():
        # Try checkout
        try:
            subprocess.run(
                ["git", "checkout", commit], capture_output=True, text=True,
                cwd=repo_dir, timeout=60,
            )
            return repo_dir
        except Exception:
            pass

    # Fresh clone
    repo_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--filter=blob:none",
             f"https://github.com/{repo}.git", str(repo_dir)],
            capture_output=True, text=True, timeout=300,
        )
        subprocess.run(
            ["git", "checkout", commit],
            capture_output=True, text=True, cwd=repo_dir, timeout=60,
        )
        return repo_dir
    except Exception as e:
        print(f"  Clone failed for {repo}: {e}")
        return None


def enrich_task(task_info: dict, gemini_key: str, repo_cache: dict[str, Path]) -> dict:
    """Enrich a single task with Gemini rubric extraction."""
    from taskforge.gemini_rubric_constructor import construct_and_classify

    task_name = task_info["task"]
    base = task_info["dir"]
    repo = task_info["repo"]
    commit = task_info["commit"]
    task_path = ROOT / base / task_name

    result = {
        "task": task_name,
        "repo": repo,
        "categories": task_info["categories"],
        "status": "error",
        "added_rubrics": 0,
        "added_distractors": 0,
        "fixed_sources": 0,
        "error": "",
    }

    if not repo or not commit:
        result["error"] = "no repo or commit"
        return result

    # Get or clone repo
    repo_dir = repo_cache.get(repo)
    if not repo_dir:
        repo_dir = clone_repo(repo, commit, Path("/tmp/repo_cache"))
        if not repo_dir:
            result["error"] = "clone failed"
            return result
        repo_cache[repo] = repo_dir
    else:
        try:
            subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=60,
            )
        except Exception:
            pass

    # Call Gemini
    try:
        gemini_result = construct_and_classify(task_path, repo_dir, gemini_key)
    except Exception as e:
        result["error"] = f"gemini: {str(e)[:200]}"
        return result

    if "error" in gemini_result:
        result["error"] = f"gemini: {gemini_result['error'][:200]}"
        return result

    # Read current manifest
    manifest_path = task_path / "eval_manifest.yaml"
    try:
        m = yaml.safe_load(manifest_path.read_text())
    except Exception:
        result["error"] = "manifest parse error"
        return result

    existing_rubric = m.get("rubric", []) or []
    existing_distractors = m.get("distractors", []) or []
    changed = False

    # --- Handle WEAK (0 rubric) ---
    if "weak" in task_info["categories"]:
        new_rubrics = []
        for r in gemini_result.get("positive_rubrics", []):
            rule = r.get("rule", "")
            if not rule or len(rule) < 15:
                continue
            new_rubrics.append({
                "rule": rule,
                "source": {
                    "path": r.get("source_file", ""),
                    "lines": r.get("source_lines", ""),
                },
                "evidence": r.get("evidence_in_gold", ""),
                "category": r.get("category", ""),
                "verification": "llm_judge",
            })
        if new_rubrics:
            m["rubric"] = new_rubrics
            result["added_rubrics"] = len(new_rubrics)
            changed = True

    # --- Handle NO_SOURCE (fix source attribution) ---
    if "no_source" in task_info["categories"] and existing_rubric:
        gemini_rubrics = {r.get("rule", "")[:40].lower(): r
                         for r in gemini_result.get("positive_rubrics", [])}
        fixed = 0
        for r in existing_rubric:
            if not isinstance(r, dict):
                continue
            src = r.get("source", {})
            if src and isinstance(src, dict) and src.get("path"):
                continue  # Already has source
            # Try to match with Gemini result
            key = r.get("rule", "")[:40].lower()
            if key in gemini_rubrics:
                gr = gemini_rubrics[key]
                r["source"] = {
                    "path": gr.get("source_file", ""),
                    "lines": gr.get("source_lines", ""),
                }
                fixed += 1
                changed = True
        result["fixed_sources"] = fixed
        if changed:
            m["rubric"] = existing_rubric

    # --- Handle NO_DISTRACTORS ---
    if "no_distractors" in task_info["categories"]:
        new_distractors = []
        existing_rules = {r.get("rule", "")[:40].lower()
                          for r in existing_rubric if isinstance(r, dict)}
        for d in gemini_result.get("negative_rubrics", []):
            rule = d.get("rule", "")
            if not rule or len(rule) < 15:
                continue
            # Don't add as distractor if it's already a positive rubric
            if rule[:40].lower() in existing_rules:
                continue
            new_distractors.append({
                "rule": rule,
                "source": {
                    "path": d.get("source_file", ""),
                    "lines": d.get("source_lines", ""),
                },
                "collision_type": d.get("collision_type", "scope_ambiguity"),
                "why_distracting": d.get("why_distracting", ""),
                "severity": d.get("severity", "medium"),
            })
        if new_distractors:
            m["distractors"] = existing_distractors + new_distractors
            result["added_distractors"] = len(new_distractors)
            changed = True

    if changed:
        manifest_path.write_text(yaml.dump(m, default_flow_style=False,
                                           sort_keys=False, allow_unicode=True))
        result["status"] = "ok"
    else:
        result["status"] = "no_changes"

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch rubric enrichment")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--category", choices=["weak", "no_distractors", "no_source", "all"],
                        default="all")
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Parallel Gemini calls (rate limit: ~10/min)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo", type=str, default=None)
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key and not args.dry_run:
        print("GEMINI_API_KEY not set")
        sys.exit(1)

    print("Scanning tasks...")
    tasks = scan_tasks()

    if args.category != "all":
        tasks = [t for t in tasks if args.category in t["categories"]]
    if args.repo:
        tasks = [t for t in tasks if t["repo"] == args.repo]

    # Sort: group by repo for clone reuse
    tasks.sort(key=lambda t: t["repo"])
    tasks = tasks[args.offset:]
    if args.limit:
        tasks = tasks[:args.limit]

    # Stats
    cat_counts = Counter()
    for t in tasks:
        for c in t["categories"]:
            cat_counts[c] += 1

    print(f"Tasks to process: {len(tasks)}")
    print(f"  weak (0 rubric):    {cat_counts.get('weak', 0)}")
    print(f"  no_distractors:     {cat_counts.get('no_distractors', 0)}")
    print(f"  no_source:          {cat_counts.get('no_source', 0)}")
    print(f"  Unique repos:       {len(set(t['repo'] for t in tasks))}")

    if args.dry_run:
        for t in tasks[:30]:
            print(f"  {t['dir']}/{t['task']} ({t['repo']}) cats={t['categories']}")
        if len(tasks) > 30:
            print(f"  ... and {len(tasks) - 30} more")
        return

    # Process with concurrency via ThreadPoolExecutor
    # (Gemini calls are I/O-bound, threading is fine)
    repo_cache: dict[str, Path] = {}
    results = []
    t_start = time.monotonic()

    # Group by repo for efficient cloning
    from itertools import groupby
    repo_groups = [(k, list(g)) for k, g in groupby(tasks, key=lambda t: t["repo"])]

    processed = 0
    for repo, group in repo_groups:
        print(f"\n--- {repo} ({len(group)} tasks) ---")
        for task_info in group:
            processed += 1
            print(f"[{processed}/{len(tasks)}] {task_info['task']} cats={task_info['categories']}")
            result = enrich_task(task_info, gemini_key, repo_cache)
            results.append(result)

            if result["status"] == "ok":
                parts = []
                if result["added_rubrics"]:
                    parts.append(f"+{result['added_rubrics']}R")
                if result["added_distractors"]:
                    parts.append(f"+{result['added_distractors']}D")
                if result["fixed_sources"]:
                    parts.append(f"fixed {result['fixed_sources']} sources")
                print(f"  OK: {', '.join(parts)}")
            elif result["status"] == "no_changes":
                print(f"  SKIP: Gemini found nothing new")
            else:
                print(f"  ERROR: {result['error'][:80]}")

            time.sleep(0.5)  # Rate limit

    elapsed = time.monotonic() - t_start

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    no_change = sum(1 for r in results if r["status"] == "no_changes")
    errors = sum(1 for r in results if r["status"] == "error")
    total_rubrics = sum(r["added_rubrics"] for r in results)
    total_distractors = sum(r["added_distractors"] for r in results)
    total_sources = sum(r["fixed_sources"] for r in results)

    print()
    print("=" * 70)
    print(f"  BATCH RUBRIC ENRICHMENT COMPLETE")
    print(f"  Processed:     {len(results)}")
    print(f"  Updated:       {ok}")
    print(f"  No changes:    {no_change}")
    print(f"  Errors:        {errors}")
    print(f"  +Rubrics:      {total_rubrics}")
    print(f"  +Distractors:  {total_distractors}")
    print(f"  Fixed sources: {total_sources}")
    print(f"  Time:          {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print("=" * 70)

    # Save results
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_file = ROOT / "pipeline_logs" / f"rubric_enrich_{ts}.json"
    results_file.parent.mkdir(exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
