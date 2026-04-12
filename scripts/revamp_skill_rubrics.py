#!/usr/bin/env python3
"""Batch revamp eval_manifest.yaml with skill-sourced rubric rules.

For each task from a skill-rich repo:
1. Clone repo at the task's base commit
2. Run hierarchy_context to discover skills
3. Call Gemini to extract skill-sourced rubric + distractor rules
4. Merge new rules into existing eval_manifest.yaml
   (preserves existing non-skill rules, adds skill-sourced ones)

Only modifies rubric + distractors sections. Never touches tests or solve.sh.

Usage:
    set -a && source .env && set +a
    .venv/bin/python scripts/revamp_skill_rubrics.py --limit 5 --dry-run
    .venv/bin/python scripts/revamp_skill_rubrics.py --concurrency 5
    .venv/bin/python scripts/revamp_skill_rubrics.py --repo biomejs/biome
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from taskforge.gemini_rubric_constructor import construct_and_classify
from taskforge.hierarchy_context import find_relevant_skills

ROOT = Path(__file__).resolve().parent.parent


def load_tasks(filter_repo: str | None = None) -> list[dict]:
    """Load tasks needing skill revamp from pre-computed list or scan."""
    cache = Path("/tmp/tasks_to_revamp.json")
    if cache.exists():
        tasks = json.loads(cache.read_text())
    else:
        # Scan — same logic as the analysis above
        tasks = _scan_tasks()

    if filter_repo:
        tasks = [t for t in tasks if t["repo"] == filter_repo]

    return tasks


def _scan_tasks() -> list[dict]:
    """Scan all tasks and find those from skill-rich repos with 0 skill refs."""
    tasks = []
    for base in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        base_dir = ROOT / base
        if not base_dir.exists():
            continue
        for task in sorted(base_dir.iterdir()):
            if not task.is_dir():
                continue
            df = task / "environment" / "Dockerfile"
            manifest = task / "eval_manifest.yaml"
            if not df.exists() or not manifest.exists():
                continue
            df_text = df.read_text()
            # Extract repo URL
            repo_match = re.search(r"github\.com/([^/]+/[^\s.]+?)(?:\.git|[\s]|$)", df_text)
            if not repo_match:
                continue
            repo = repo_match.group(1)

            try:
                m = yaml.safe_load(manifest.read_text())
            except Exception:
                continue
            if not m:
                continue
            rubric = m.get("rubric", []) or []
            skill_refs = sum(
                1 for r in rubric
                if "skill" in (r.get("source", {}) or {}).get("path", "").lower()
            )
            if skill_refs > 0:
                continue  # Already has skill refs

            tasks.append({
                "task": task.name,
                "dir": base,
                "repo": repo,
                "rubric_count": len(rubric),
                "skill_refs": 0,
            })
    return tasks


def clone_repo_at_commit(repo: str, commit: str, dest: Path) -> bool:
    """Clone repo at specific commit. Returns True on success."""
    if dest.exists():
        # Check if already at right commit
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=dest, timeout=5,
            )
            if result.stdout.strip().startswith(commit[:7]):
                return True
        except Exception:
            pass
        shutil.rmtree(dest, ignore_errors=True)

    try:
        subprocess.run(
            ["git", "clone", "--filter=blob:none", f"https://github.com/{repo}.git", str(dest)],
            capture_output=True, text=True, timeout=300,
        )
        subprocess.run(
            ["git", "checkout", commit],
            capture_output=True, text=True, cwd=dest, timeout=30,
        )
        return True
    except Exception as e:
        print(f"  Clone failed: {e}")
        return False


def get_commit_from_dockerfile(task_dir: Path) -> str:
    """Extract base commit from Dockerfile."""
    df = task_dir / "environment" / "Dockerfile"
    if not df.exists():
        return ""
    df_text = df.read_text()
    # Try various patterns
    for pattern in [
        r"git checkout\s+([a-f0-9]{7,40})",
        r"git fetch.*origin\s+([a-f0-9]{7,40})",
        r"ARG\s+BASE_COMMIT=([a-f0-9]{7,40})",
        r"FETCH_HEAD\b.*git fetch.*origin\s+([a-f0-9]{7,40})",
    ]:
        m = re.search(pattern, df_text)
        if m:
            return m.group(1)
    # For fetch+checkout pattern
    fetch_match = re.search(r"git fetch.*origin\s+([a-f0-9]{7,40})", df_text)
    if fetch_match:
        return fetch_match.group(1)
    return ""


def merge_skill_rubrics(
    manifest_path: Path,
    gemini_result: dict,
    repo_dir: Path,
    edited_paths: list[str],
) -> tuple[int, int]:
    """Merge skill-sourced rubrics into existing manifest.

    Only adds rules sourced from SKILL.md files. Preserves all existing rules.
    Returns (added_rubrics, added_distractors).
    """
    m = yaml.safe_load(manifest_path.read_text())
    if not m:
        return 0, 0

    existing_rubric = m.get("rubric", []) or []
    existing_distractors = m.get("distractors", []) or []

    # Extract skill-sourced rules from Gemini result
    new_rubrics = []
    for r in gemini_result.get("positive_rubrics", []):
        source_file = r.get("source_file", "")
        if "skill" not in source_file.lower():
            continue
        # Check for duplicates (same source file + similar rule text)
        rule_text = r.get("rule", "")
        is_dup = any(
            rule_text[:50].lower() in (er.get("rule", "")[:50].lower())
            for er in existing_rubric
        )
        if is_dup:
            continue
        new_rubrics.append({
            "rule": rule_text,
            "source": {
                "path": source_file,
                "lines": r.get("source_lines", ""),
            },
            "evidence": r.get("evidence_in_gold", ""),
            "category": r.get("category", ""),
            "verification": "llm_judge",
        })

    new_distractors = []
    for d in gemini_result.get("negative_rubrics", []):
        source_file = d.get("source_file", "")
        if "skill" not in source_file.lower():
            continue
        rule_text = d.get("rule", "")
        is_dup = any(
            rule_text[:50].lower() in (ed.get("rule", "")[:50].lower())
            for ed in existing_distractors
        )
        if is_dup:
            continue
        new_distractors.append({
            "rule": rule_text,
            "source": {
                "path": source_file,
                "lines": d.get("source_lines", ""),
            },
            "collision_type": d.get("collision_type", "scope_ambiguity"),
            "why_distracting": d.get("why_distracting", ""),
            "severity": d.get("severity", "medium"),
        })

    if not new_rubrics and not new_distractors:
        return 0, 0

    # Merge
    m["rubric"] = existing_rubric + new_rubrics
    m["distractors"] = existing_distractors + new_distractors

    # Write back
    manifest_path.write_text(yaml.dump(m, default_flow_style=False, sort_keys=False, allow_unicode=True))

    return len(new_rubrics), len(new_distractors)


def process_task(task_info: dict, gemini_key: str, repo_cache: dict[str, Path]) -> dict:
    """Process a single task: clone, extract, merge.

    repo_cache maps repo → cloned Path (reuse across tasks from same repo).
    """
    task_name = task_info["task"]
    task_dir_name = task_info["dir"]
    repo = task_info["repo"]
    task_path = ROOT / task_dir_name / task_name

    result = {
        "task": task_name,
        "repo": repo,
        "status": "error",
        "added_rubrics": 0,
        "added_distractors": 0,
        "relevant_skills": 0,
        "irrelevant_skills": 0,
        "error": "",
    }

    # Get or clone repo
    commit = get_commit_from_dockerfile(task_path)
    if not commit:
        result["error"] = "no commit in Dockerfile"
        return result

    repo_dir = repo_cache.get(repo)
    if not repo_dir or not repo_dir.exists():
        repo_dir = Path(f"/tmp/repo_cache/{repo.replace('/', '_')}")
        if not clone_repo_at_commit(repo, commit, repo_dir):
            result["error"] = "clone failed"
            return result
        repo_cache[repo] = repo_dir
    else:
        # Checkout the right commit
        try:
            subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
        except Exception:
            # Re-clone at this commit
            shutil.rmtree(repo_dir, ignore_errors=True)
            if not clone_repo_at_commit(repo, commit, repo_dir):
                result["error"] = "re-clone failed"
                return result

    # Check if repo even has skills at this commit
    from taskforge.hierarchy_context import extract_edited_paths
    edited_paths = extract_edited_paths(task_path)
    skills = find_relevant_skills(repo_dir, edited_paths)

    relevant = [s for s in skills if s["is_relevant"]]
    irrelevant = [s for s in skills if not s["is_relevant"] and not s.get("is_workflow_only")]
    result["relevant_skills"] = len(relevant)
    result["irrelevant_skills"] = len(irrelevant)

    if not relevant and not irrelevant:
        result["status"] = "no_skills"
        result["error"] = "no applicable skills found at this commit"
        return result

    # Call Gemini for rubric extraction
    try:
        gemini_result = construct_and_classify(task_path, repo_dir, gemini_key)
    except Exception as e:
        result["error"] = f"gemini error: {str(e)[:200]}"
        return result

    if "error" in gemini_result:
        result["error"] = f"gemini: {gemini_result['error'][:200]}"
        return result

    # Merge skill-sourced rules into manifest
    manifest_path = task_path / "eval_manifest.yaml"
    added_r, added_d = merge_skill_rubrics(
        manifest_path, gemini_result, repo_dir, edited_paths)

    result["status"] = "ok" if (added_r + added_d) > 0 else "no_new_rules"
    result["added_rubrics"] = added_r
    result["added_distractors"] = added_d

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch revamp skill-sourced rubrics")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--repo", type=str, default=None, help="Filter to specific repo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1, help="Parallel Gemini calls (be careful with rate limits)")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key and not args.dry_run:
        print("GEMINI_API_KEY not set")
        sys.exit(1)

    tasks = load_tasks(filter_repo=args.repo)
    tasks = tasks[args.offset:]
    if args.limit:
        tasks = tasks[:args.limit]

    print(f"Tasks to revamp: {len(tasks)}")
    if args.dry_run:
        for t in tasks[:20]:
            print(f"  {t['dir']}/{t['task']} (repo={t['repo']}, rubric={t['rubric_count']})")
        if len(tasks) > 20:
            print(f"  ... and {len(tasks) - 20} more")
        return

    # Process
    repo_cache: dict[str, Path] = {}
    results = []
    t_start = time.monotonic()

    for i, task_info in enumerate(tasks):
        print(f"\n[{i+1}/{len(tasks)}] {task_info['task']} ({task_info['repo']})")
        result = process_task(task_info, gemini_key, repo_cache)
        results.append(result)

        status = result["status"]
        if status == "ok":
            print(f"  OK: +{result['added_rubrics']} rubrics, +{result['added_distractors']} distractors")
        elif status == "no_skills":
            print(f"  SKIP: {result['error']}")
        elif status == "no_new_rules":
            print(f"  SKIP: Gemini found no new skill-sourced rules")
        else:
            print(f"  ERROR: {result['error'][:100]}")

        # Rate limit
        time.sleep(1.0)

    elapsed = time.monotonic() - t_start

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    no_skills = sum(1 for r in results if r["status"] == "no_skills")
    no_new = sum(1 for r in results if r["status"] == "no_new_rules")
    errors = sum(1 for r in results if r["status"] == "error")
    total_rubrics = sum(r["added_rubrics"] for r in results)
    total_distractors = sum(r["added_distractors"] for r in results)

    print()
    print("=" * 70)
    print(f"  SKILL RUBRIC REVAMP COMPLETE")
    print(f"  Tasks processed: {len(results)}")
    print(f"  Updated:         {ok}")
    print(f"  No skills:       {no_skills}")
    print(f"  No new rules:    {no_new}")
    print(f"  Errors:          {errors}")
    print(f"  Total added:     +{total_rubrics} rubrics, +{total_distractors} distractors")
    print(f"  Time:            {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print("=" * 70)

    # Save results
    results_file = ROOT / "pipeline_logs" / f"skill_revamp_{time.strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
